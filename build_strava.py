#!/usr/bin/env python3
"""Aspire la heatmap Strava PÉDESTRE (sport_Hike) sur la zone cèpes → tuiles statiques.
Fréquentation = accès (sentiers battus) + concurrence (coins déjà ratissés)."""
import math, os, urllib.request, concurrent.futures as cf

BBOX = (-2.10, 43.04, -0.86, 43.94)  # lon_min, lat_min, lon_max, lat_max
ZOOMS = range(10, 14)                 # z10-13
ACT, COLOR = "sport_Hike", "hot"
OUT = "/srv/www/cepes/strava"
BASE = f"https://content-a.strava.com/identified/globalheat/{ACT}/{COLOR}"

def cookies():
    for l in open("/home/debian/repos/pista/.env"):
        if l.startswith("STRAVA_COOKIES="):
            return l.split("=", 1)[1].strip().strip('"')
    return ""
COOK = cookies()
HDR = {"cookie": COOK, "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
       "accept": "*/*", "accept-language": "fr-FR,fr;q=0.9", "origin": "https://www.strava.com", "referer": "https://www.strava.com/"}

def deg2tile(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    lat_r = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n)
    return x, y

jobs = []
for z in ZOOMS:
    x0, y0 = deg2tile(BBOX[0], BBOX[3], z)  # NW
    x1, y1 = deg2tile(BBOX[2], BBOX[1], z)  # SE
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            jobs.append((z, x, y))
print("tuiles à tester:", len(jobs))

def fetch(job):
    z, x, y = job
    d = f"{OUT}/{z}/{x}"
    p = f"{d}/{y}.png"
    if os.path.exists(p):
        return "skip"
    try:
        req = urllib.request.Request(f"{BASE}/{z}/{x}/{y}.png?v=19&missing=empty", headers=HDR)
        b = urllib.request.urlopen(req, timeout=25).read()
        if len(b) < 1024:
            return "empty"
        os.makedirs(d, exist_ok=True)
        open(p, "wb").write(b)
        return "ok"
    except urllib.error.HTTPError as e:
        return f"err{e.code}"
    except Exception:
        return "err"

from collections import Counter
c = Counter()
with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for r in ex.map(fetch, jobs):
        c[r] += 1
print("résultat:", dict(c))
