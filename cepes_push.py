#!/usr/bin/env python3
"""Radar de poussée à cèpes autour de Bayonne : indice basé sur la pluie récente + douceur.
Écrit /srv/www/cepes/push.json et alerte Discord quand la fenêtre optimale s'ouvre."""
import json, urllib.request, datetime, pathlib, os

LAT, LON = 43.40, -1.45
OUT = pathlib.Path("/srv/www/cepes/push.json")
STATE = pathlib.Path("/home/debian/cepes/push_state.json")
DISCORD_CH = "1511007406870495265"  # #dev (à changer pour un salon dédié)

def meteo():
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
         "&daily=precipitation_sum,temperature_2m_mean,temperature_2m_max,temperature_2m_min"
         "&past_days=25&forecast_days=7&timezone=Europe%2FParis")
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "cepes"}), timeout=25))["daily"]

def compute():
    d = meteo()
    days = d["time"]; rain = d["precipitation_sum"]; tmean = d["temperature_2m_mean"]
    tmin = d["temperature_2m_min"]; tmax = d["temperature_2m_max"]
    today = datetime.date.today().isoformat()
    ti = days.index(today) if today in days else len(rain) - 8  # index d'aujourd'hui
    # dernière "bonne saucée" : fenêtre glissante 3 j >= 25 mm (ou 1 j >= 18)
    soak_idx = None
    for i in range(ti, -1, -1):
        r3 = sum(x or 0 for x in rain[max(0, i - 2):i + 1])
        if r3 >= 25 or (rain[i] or 0) >= 18:
            soak_idx = i; break
    verdict = ""; score = 0; lag = None; window = ""
    if soak_idx is None:
        verdict = "Trop sec — pas de grosse pluie récente"; score = 10
    else:
        lag = ti - soak_idx  # jours depuis la saucée
        # douceur sur la fenêtre depuis la saucée
        seg = tmean[soak_idx:ti + 1] or [tmean[ti]]
        tmoy = sum(seg) / len(seg)
        gel = any((x or 99) < 1 for x in tmin[soak_idx:ti + 1])
        chaud = tmoy > 22
        rain_mm = sum(x or 0 for x in rain[max(0, soak_idx - 2):soak_idx + 1])
        if gel:
            verdict = "Gelée après la pluie — poussée bloquée"; score = 15
        elif lag < 6:
            verdict = f"Ça s'amorce — patiente encore {8-lag}-{14-lag} j"; score = 40
            window = f"fenêtre vers {(datetime.date.fromisoformat(today)+datetime.timedelta(days=max(1,9-lag))).strftime('%d/%m')}"
        elif 6 <= lag <= 18 and not chaud:
            score = 90 if 8 <= lag <= 14 else 70
            verdict = "🔥 FENÊTRE OPTIMALE — vas-y maintenant !" if score >= 85 else "Bonne fenêtre — ça doit sortir"
            window = f"saucée de {rain_mm:.0f} mm il y a {lag} j · {tmoy:.0f}°C moy."
        else:
            verdict = "Fenêtre passée — attends la prochaine pluie"; score = 25
    # prochaine pluie prévue (jours futurs)
    fut = [(days[i], rain[i]) for i in range(ti + 1, len(rain)) if (rain[i] or 0) >= 10]
    nextrain = fut[0] if fut else None
    # prévisions J+1..J+7 pour sparkline
    forecast = []
    for i in range(ti + 1, min(ti + 8, len(days))):
        r_mm = round(rain[i] or 0, 1)
        forecast.append({"date": days[i], "rain": r_mm,
                         "tmax": round(tmax[i] or 0, 1), "tmin": round(tmin[i] or 0, 1)})
    # indice futur : si grosse saucée prévue dans les 7j, calcul lag potentiel
    rain_fut7 = sum(x["rain"] for x in forecast)
    score_future = 0
    for k, fc in enumerate(forecast):
        r3 = sum(x["rain"] for x in forecast[max(0,k-2):k+1])
        if r3 >= 25 or fc["rain"] >= 18:
            pot_lag = k + 1  # jours depuis auj à la saucée + fenêtre optimale
            if 7 <= pot_lag <= 17:
                score_future = 70
            elif pot_lag < 7:
                score_future = 50
            break
    return {"ts": datetime.datetime.now().isoformat(timespec="minutes"),
            "score": score, "verdict": verdict, "lag": lag,
            "window": window,
            "next_rain": ({"date": nextrain[0], "mm": round(nextrain[1])} if nextrain else None),
            "rain14": round(sum(x or 0 for x in rain[max(0, ti - 13):ti + 1])),
            "forecast": forecast, "score_future": score_future,
            "rain_fut7": round(rain_fut7)}

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
