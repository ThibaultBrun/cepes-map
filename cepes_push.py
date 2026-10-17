#!/usr/bin/env python3
"""Radar de poussée à cèpes autour de Bayonne : indice basé sur la pluie récente + douceur.
Écrit /srv/www/cepes/push.json et alerte Discord quand la fenêtre optimale s'ouvre."""
import json, urllib.request, datetime, pathlib, os

OUT = pathlib.Path("/srv/www/cepes/push.json")
STATE = pathlib.Path("/home/debian/cepes/push_state.json")
DISCORD_CH = "1511007406870495265"  # #dev (à changer pour un salon dédié)

# Secteurs échantillonnés sur toute la zone (la pluie est très localisée ici,
# un seul point rate les orages de versant → on sonde plusieurs coins).
POINTS = [
    ("Bayonne / St-Pierre-d'Irube", 43.47, -1.45),
    ("Anglet / côte", 43.49, -1.52),
    ("Ustaritz / Nive", 43.40, -1.45),
    ("Cambo / Itxassou", 43.36, -1.40),
    ("Espelette / sud", 43.33, -1.45),
    ("St-Jean-de-Luz / Ciboure", 43.39, -1.64),
    ("Hasparren / est", 43.38, -1.30),
    ("Sud Landes / Labenne", 43.59, -1.44),
]

def meteo_multi():
    lats = ",".join(str(p[1]) for p in POINTS)
    lons = ",".join(str(p[2]) for p in POINTS)
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}"
         "&daily=precipitation_sum,temperature_2m_mean,temperature_2m_max,temperature_2m_min"
         "&past_days=25&forecast_days=7&timezone=Europe%2FParis")
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "cepes"}), timeout=30))
    return r if isinstance(r, list) else [r]  # multi-location => liste

def score_point(d):
    """Scoring d'un secteur : détecte la dernière grosse saucée et l'âge de la poussée."""
    days = d["time"]; rain = d["precipitation_sum"]; tmean = d["temperature_2m_mean"]
    tmin = d["temperature_2m_min"]; tmax = d["temperature_2m_max"]
    today = datetime.date.today().isoformat()
    ti = days.index(today) if today in days else len(rain) - 8
    # saucée = fenêtre 3 j >= 20 mm (seuil abaissé) ou 1 j >= 15
    soak_idx = None
    for i in range(ti, -1, -1):
        r3 = sum(x or 0 for x in rain[max(0, i - 2):i + 1])
        if r3 >= 20 or (rain[i] or 0) >= 15:
            soak_idx = i; break
    verdict = ""; score = 0; lag = None; window = ""; rain_mm = 0
    if soak_idx is None:
        verdict = "Trop sec — pas de grosse pluie récente"; score = 10
    else:
        lag = ti - soak_idx
        seg = tmean[soak_idx:ti + 1] or [tmean[ti]]
        tmoy = sum(seg) / len(seg)
        gel = any((x or 99) < 1 for x in tmin[soak_idx:ti + 1])
        chaud = tmoy > 22
        rain_mm = sum(x or 0 for x in rain[max(0, soak_idx - 2):soak_idx + 1])
        if gel:
            verdict = "Gelée après la pluie — poussée bloquée"; score = 15
        elif lag < 6:
            score = 40
            verdict = f"Ça s'amorce — patiente encore {max(1,8-lag)}-{max(2,14-lag)} j"
            window = f"fenêtre vers {(datetime.date.fromisoformat(today)+datetime.timedelta(days=max(1,9-lag))).strftime('%d/%m')}"
        elif 6 <= lag <= 20 and not chaud:
            score = 90 if 8 <= lag <= 15 else 70
            verdict = "🔥 FENÊTRE OPTIMALE — vas-y maintenant !" if score >= 85 else "Bonne fenêtre — ça doit sortir"
            window = f"saucée de {rain_mm:.0f} mm il y a {lag} j · {tmoy:.0f}°C moy."
        else:
            verdict = "Fenêtre passée — attends la prochaine pluie"; score = 25
    # prochaine pluie + prévi 7 j
    fut = [(days[i], rain[i]) for i in range(ti + 1, len(rain)) if (rain[i] or 0) >= 10]
    nextrain = fut[0] if fut else None
    forecast = [{"date": days[i], "rain": round(rain[i] or 0, 1),
                 "tmax": round(tmax[i] or 0, 1), "tmin": round(tmin[i] or 0, 1)}
                for i in range(ti + 1, min(ti + 8, len(days)))]
    rain_fut7 = sum(x["rain"] for x in forecast)
    score_future = 0
    for k, fc in enumerate(forecast):
        r3 = sum(x["rain"] for x in forecast[max(0, k - 2):k + 1])
        if r3 >= 20 or fc["rain"] >= 15:
            pot_lag = k + 1
            score_future = 70 if 7 <= pot_lag <= 17 else 50
            break
    return {"score": score, "verdict": verdict, "lag": lag, "window": window,
            "rain_mm": round(rain_mm), "next_rain": nextrain,
            "rain14": round(sum(x or 0 for x in rain[max(0, ti - 13):ti + 1])),
            "forecast": forecast, "score_future": score_future, "rain_fut7": round(rain_fut7)}

def compute():
    data = meteo_multi()
    per = []
    for (name, lat, lon), d in zip(POINTS, data):
        try: per.append((name, score_point(d["daily"])))
        except Exception as e: print("skip", name, e)
    per.sort(key=lambda x: x[1]["score"], reverse=True)
    best_name, best = per[0]
    # localisation : écart entre le meilleur secteur et la moyenne
    scores = [p[1]["score"] for p in per]
    localized = (max(scores) - (sum(scores) / len(scores))) > 25
    zones = [{"name": n, "score": r["score"], "lag": r["lag"], "rain_mm": r["rain_mm"]} for n, r in per]
    verdict = best["verdict"]
    if best["score"] >= 70:
        verdict = f"{best['verdict']} · secteur {best_name}"
    out = {"ts": datetime.datetime.now().isoformat(timespec="minutes"),
           "score": best["score"], "verdict": verdict, "lag": best["lag"],
           "window": best["window"], "best_zone": best_name, "localized": localized,
           "next_rain": ({"date": best["next_rain"][0], "mm": round(best["next_rain"][1])} if best["next_rain"] else None),
           "rain14": best["rain14"], "forecast": best["forecast"],
           "score_future": best["score_future"], "rain_fut7": best["rain_fut7"],
           "zones": zones}
    return out

def discord(msg):
    try:
        tok = json.load(open(os.path.expanduser("~/.openclaw/openclaw.json")))["channels"]["discord"]["token"]
        req = urllib.request.Request(f"https://discord.com/api/v10/channels/{DISCORD_CH}/messages",
            data=json.dumps({"content": msg}).encode(),
            headers={"Authorization": f"Bot {tok}", "Content-Type": "application/json", "User-Agent": "DiscordBot (cepes,1.0)"})
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print("discord fail", e)

def main():
    r = compute()
    OUT.write_text(json.dumps(r, ensure_ascii=False))
    print(json.dumps(r, ensure_ascii=False, indent=2))
    # alerte sur transition vers fenêtre (score >= 85)
    prev = {}
    try: prev = json.loads(STATE.read_text())
    except Exception: pass
    if r["score"] >= 85 and prev.get("score", 0) < 85:
        discord(f"🍄🔔 **Fenêtre à cèpes ouverte autour de Bayonne !**\n{r['verdict']}\n{r['window']}\n→ cepes.tbrun.dev")
    STATE.write_text(json.dumps(r))

if __name__ == "__main__":
    main()
