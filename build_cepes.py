#!/usr/bin/env python3
"""Carte de potentiel cèpes autour de Bayonne : BD Forêt V2 (IGN) scorée par essence.
Écrit /srv/www/cepes/foret.geojson (polygones + score 0-3)."""
import json, urllib.request, pathlib

WFS = "https://data.geopf.fr/wfs/ows"
LAYER = "LANDCOVER.FORESTINVENTORY.V2:formation_vegetale"
# zone de prospection autour de Bayonne (lon_min, lat_min, lon_max, lat_max)
BBOX = (-2.10, 43.04, -0.86, 43.94)
OUT = pathlib.Path("/srv/www/cepes/foret.geojson")

# score cèpe par essence (3=top, 2=favorable, 1=possible, 0=nul)
SCORE = {
    "Chênes décidus": 3, "Chênes sempervirents": 3, "Châtaignier": 3, "Hêtre": 3,
    "Feuillus": 2, "Pin maritime": 2, "Mixte": 2,
    "Conifères": 1, "Pin laricio, pin noir": 1, "Pins mélangés": 1, "Pin autre": 1,
    "Douglas": 1, "Mélèze": 1, "Sapin, épicéa": 1,
    "Robinier": 0, "Peuplier": 0, "NC": 0, "NR": 0,
}


def fetch():
    feats = []
    start = 0
    page = 1000
    while True:
        url = (f"{WFS}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES={LAYER}"
               f"&SRSNAME=CRS:84&BBOX={BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]},CRS:84"
               f"&OUTPUTFORMAT=application/json&COUNT={page}&STARTINDEX={start}")
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "cepes"}), timeout=90))
        f = d.get("features", [])
        feats += f
        if len(f) < page:
            break
        start += page
        if start > 60000:
            break
    return feats


def main():
    feats = fetch()
    out_feats = []
    for ft in feats:
        p = ft.get("properties", {})
        ess = p.get("essence")
        sc = SCORE.get(ess, 0)
        if sc == 0:
            continue  # on n'affiche que le favorable (allège la carte)
        out_feats.append({
            "type": "Feature",
            "geometry": ft["geometry"],
            "properties": {"score": sc, "essence": ess, "tfv": p.get("tfv")},
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": out_feats}))
    from collections import Counter
    print("total parcelles:", len(feats), "| retenues:", len(out_feats))
    print("par score:", dict(Counter(f["properties"]["score"] for f in out_feats)))
    print("taille:", OUT.stat().st_size // 1024, "Ko")


if __name__ == "__main__":
    main()
