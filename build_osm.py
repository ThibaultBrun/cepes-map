#!/usr/bin/env python3
"""OSM parkings + sentiers (path/track) autour de Bayonne -> GeoJSON pour la carte cèpes."""
import json, urllib.request, urllib.parse

# bbox = south,west,north,east
S, W, N, E = 43.04, -2.10, 43.94, -0.86
OVERPASS = "https://overpass-api.de/api/interpreter"


def q(body):
    data = urllib.parse.urlencode({"data": body}).encode()
    req = urllib.request.Request(OVERPASS, data=data, headers={"User-Agent": "cepes-map"})
    return json.load(urllib.request.urlopen(req, timeout=300))


# --- parkings (points) ---
pk = q(f"[out:json][timeout:240];nwr[amenity=parking]({S},{W},{N},{E});out center 4000;")
pfeat = []
for el in pk.get("elements", []):
    lat = el.get("lat") or (el.get("center") or {}).get("lat")
    lon = el.get("lon") or (el.get("center") or {}).get("lon")
    if lat and lon:
        pfeat.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]},
                      "properties": {"name": (el.get("tags") or {}).get("name", "Parking")}})
json.dump({"type": "FeatureCollection", "features": pfeat}, open("/srv/www/cepes/parkings.geojson", "w"))
print("parkings:", len(pfeat))

# --- sentiers / pistes (lignes) ---
tr = q(f'[out:json][timeout:280];way[highway~"^(path|track)$"]({S},{W},{N},{E});out geom 200000;')
tfeat = []
for el in tr.get("elements", []):
    g = el.get("geometry")
    if not g:
        continue
    coords = [[p["lon"], p["lat"]] for p in g]
    if len(coords) >= 2:
        tfeat.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
                      "properties": {"h": (el.get("tags") or {}).get("highway", "")}})
json.dump({"type": "FeatureCollection", "features": tfeat}, open("/srv/www/cepes/sentiers.geojson", "w"))
print("sentiers:", len(tfeat))
