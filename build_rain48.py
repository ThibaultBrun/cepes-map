#!/usr/bin/env python3
"""Pluie PRÉVUE sur grille (Open-Meteo, pas 15 min, modèle AROME HD sur la France),
48h à l'avance -> rain48.json. Pour l'animation 'pluie à venir' sur la carte cèpes."""
import json, urllib.request, datetime, pathlib
LON0, LON1, LAT0, LAT1, STEP = -1.85, -1.00, 43.22, 43.70, 0.06
OUT = pathlib.Path("/srv/www/cepes/rain48.json")
N_FRAMES = 192  # 48 h au pas de 15 min

def frange(a, b, s):
    v = a
    while v <= b + 1e-9:
        yield round(v, 3); v += s

pts = [(lon, lat) for lat in frange(LAT0, LAT1, STEP) for lon in frange(LON0, LON1, STEP)]
lats = ",".join(str(p[1]) for p in pts); lons = ",".join(str(p[0]) for p in pts)
u = (f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}"
     "&minutely_15=precipitation&forecast_days=3&timezone=Europe%2FParis")
data = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "cepes"}), timeout=90))
if isinstance(data, dict): data = [data]
times = data[0]["minutely_15"]["time"]
now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
start = next((i for i, t in enumerate(times) if t >= now), 0)
idx = list(range(start, min(start + N_FRAMES, len(times))))
out_times = [times[i] for i in idx]
points = []
for (lon, lat), d in zip(pts, data):
    pr = d["minutely_15"]["precipitation"]
    arr = [round(pr[i] or 0, 2) for i in idx]
    if max(arr) > 0:
        points.append({"lon": lon, "lat": lat, "p": arr})
OUT.write_text(json.dumps({"generated": datetime.datetime.now().isoformat(timespec="minutes"),
    "times": out_times, "step_min": 15, "points": points, "grid_n": len(pts)}, ensure_ascii=False))
print(f"rain48: {len(out_times)} pas de 15min ({len(out_times)/4:.0f}h), {len(points)}/{len(pts)} points avec pluie")
