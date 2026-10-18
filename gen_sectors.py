import json
from shapely.geometry import MultiPoint, box, mapping, Point
from shapely.ops import voronoi_diagram
PTS=json.load(open("sectors_points.json"))
clip=box(-1.86,43.21,-0.98,43.71)
mp=MultiPoint([(p["lon"],p["lat"]) for p in PTS])
cells=list(voronoi_diagram(mp, envelope=clip).geoms)
feats=[]
for p in PTS:
    pt=Point(p["lon"],p["lat"])
    cell=next((c for c in cells if c.contains(pt)), None)
    if cell is None: continue
    feats.append({"type":"Feature","properties":{"name":p["name"],"clon":p["lon"],"clat":p["lat"],"score":0},"geometry":mapping(cell.intersection(clip))})
json.dump({"type":"FeatureCollection","features":feats},open("/srv/www/cepes/sectors.geojson","w"),ensure_ascii=False)
print("secteurs:",len(feats))
