#!/usr/bin/env python3
"""Pluie PRÉVUE sur grille (Open-Meteo), 48h à l'avance pas de 1h -> rain48.json.
Pour l'animation 'radar de pluie à venir' sur la carte cèpes."""
import json, urllib.request, datetime, pathlib
LON0,LON1,LAT0,LAT1,STEP = -1.85,-1.00,43.22,43.70,0.06
OUT = pathlib.Path("/srv/www/cepes/rain48.json")
def frange(a,b,s):
    v=a
    while v<=b+1e-9: yield round(v,3); v+=s
pts=[(lon,lat) for lat in frange(LAT0,LAT1,STEP) for lon in frange(LON0,LON1,STEP)]
lats=",".join(str(p[1]) for p in pts); lons=",".join(str(p[0]) for p in pts)
u=(f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}"
   "&hourly=precipitation&forecast_days=3&timezone=Europe%2FParis")
data=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"cepes"}),timeout=60))
if isinstance(data,dict): data=[data]
times=data[0]["hourly"]["time"]
now=datetime.datetime.now().strftime("%Y-%m-%dT%H:00")
start=0
for i,t in enumerate(times):
    if t>=now: start=i; break
idx=list(range(start,min(start+48,len(times))))
out_times=[times[i] for i in idx]
points=[]
for (lon,lat),d in zip(pts,data):
    pr=d["hourly"]["precipitation"]
    arr=[round(pr[i] or 0,2) for i in idx]
    if max(arr)>0:  # ne garde que les points qui voient de la pluie (allège)
        points.append({"lon":lon,"lat":lat,"p":arr})
OUT.write_text(json.dumps({"generated":datetime.datetime.now().isoformat(timespec="minutes"),
    "times":out_times,"step_h":1,"points":points,"grid_n":len(pts)},ensure_ascii=False))
print(f"rain48: {len(out_times)}h, {len(points)}/{len(pts)} points avec pluie")
