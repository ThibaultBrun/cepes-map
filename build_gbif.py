#!/usr/bin/env python3
"""Observations GBIF des champignons comestibles prisés autour de Bayonne -> gbif.geojson.
Croise avec la carte : où les gens trouvent réellement ces espèces."""
import json, urllib.request, urllib.parse, time

# bbox zone cèpes
LAT0, LAT1, LON0, LON1 = 43.04, 43.94, -2.10, -0.86

# espèces : latin -> (nom FR, groupe, couleur)
SPECIES = {
    "Boletus edulis":            ("Cèpe de Bordeaux", "Cèpes", "#f5c842"),
    "Boletus aereus":            ("Cèpe bronzé (tête de nègre)", "Cèpes", "#5c2d00"),
    "Boletus pinophilus":        ("Cèpe des pins", "Cèpes", "#c0430c"),
    "Boletus reticulatus":       ("Cèpe d'été", "Cèpes", "#d4a558"),
    "Craterellus cornucopioides":("Trompette de la mort", "Trompettes", "#26242b"),
    "Cantharellus cibarius":     ("Girolle", "Girolles", "#ffb02e"),
    "Craterellus tubaeformis":   ("Chanterelle en tube", "Girolles", "#b98a3a"),
    "Lactarius deliciosus":      ("Lactaire délicieux (sanguin)", "Sanguins", "#e8622a"),
    "Lactarius sanguifluus":     ("Sanguin", "Sanguins", "#c0352a"),
    "Hydnum repandum":           ("Pied-de-mouton", "Pied-de-mouton", "#e8d9a8"),
    "Imleria badia":             ("Bolet bai", "Cèpes", "#6e4a28"),
}

def fetch(name):
    feats = []
    for offset in range(0, 900, 300):
        q = urllib.parse.urlencode({
            "scientificName": name, "hasCoordinate": "true",
            "decimalLatitude": f"{LAT0},{LAT1}", "decimalLongitude": f"{LON0},{LON1}",
            "limit": 300, "offset": offset,
        })
        try:
            d = json.load(urllib.request.urlopen(
                urllib.request.Request("https://api.gbif.org/v1/occurrence/search?" + q,
                                       headers={"User-Agent": "cepes-map"}), timeout=30))
        except Exception as e:
            print("  err", name, e); break
        for r in d.get("results", []):
            lat, lon = r.get("decimalLatitude"), r.get("decimalLongitude")
            if lat is None or lon is None:
                continue
            fr, grp, col = SPECIES[name]
            feats.append({"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                          "properties": {"species": name, "fr": fr, "group": grp,
                                         "year": r.get("year"), "basisOfRecord": r.get("basisOfRecord")}})
        if d.get("endOfRecords"):
            break
        time.sleep(0.2)
    return feats

all_feats = []
for name in SPECIES:
    f = fetch(name)
    print(f"{name}: {len(f)}")
    all_feats += f
json.dump({"type": "FeatureCollection", "features": all_feats},
          open("/srv/www/cepes/gbif.geojson", "w"), ensure_ascii=False)
print("total:", len(all_feats))
