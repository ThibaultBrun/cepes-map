#!/usr/bin/env python3
"""Trouve une boucle famille (~2.5km, D+ mini) sur le réseau de sentiers OSM depuis un parking.
Usage: make_loop.py <lon> <lat> [target_km]  -> écrit /tmp/loop.geojson + affiche stats."""
import json, math, heapq, sys
def dk(a,b): return math.hypot((a[0]-b[0])*math.cos(math.radians(43.4))*111.32,(a[1]-b[1])*111.32)
PK=(float(sys.argv[1]), float(sys.argv[2]))
TARGET=float(sys.argv[3]) if len(sys.argv)>3 else 2.5
S=[f['geometry']['coordinates'] for f in json.load(open(sys.argv[4] if len(sys.argv)>4 else '/srv/www/cepes/sentiers.geojson'))['features']]
segs=[cs for cs in S if any(dk(PK,c)<TARGET*0.8 for c in cs[::2])]
def key(c): return (round(c[0],4),round(c[1],4))
adj={};nodes={}
def add(a,b):
    ka,kb=key(a),key(b)
    if ka==kb:return
    nodes[ka]=a;nodes[kb]=b;w=dk(a,b)
    adj.setdefault(ka,[]).append((kb,w));adj.setdefault(kb,[]).append((ka,w))
for cs in segs:
    for i in range(len(cs)-1):add(cs[i],cs[i+1])
nk=list(nodes)
for i in range(len(nk)):
    for j in range(i+1,len(nk)):
        d=dk(nodes[nk[i]],nodes[nk[j]])
        if 0<d<0.05:adj.setdefault(nk[i],[]).append((nk[j],d));adj.setdefault(nk[j],[]).append((nk[i],d))
start=min(nodes,key=lambda k:dk(PK,nodes[k]))
def dij(src,pen=set(),pf=4):
    dist={src:0};prev={};pq=[(0,src)]
    while pq:
        d,u=heapq.heappop(pq)
        if d>dist.get(u,1e9):continue
        for v,w in adj.get(u,[]):
            w2=w*pf if ((u,v) in pen or (v,u) in pen) else w
            nd=d+w2
            if nd<dist.get(v,1e9):dist[v]=nd;prev[v]=u;heapq.heappush(pq,(nd,v))
    return dist,prev
dist,prev=dij(start)
def path(pv,s,d):
    o=[d]
    while o[-1]!=s:o.append(pv[o[-1]])
    return o[::-1]
from shapely.geometry import shape,Point
from shapely.strtree import STRtree
_all=[(shape(f['geometry']),f['properties'].get('score',0)) for f in json.load(open('/srv/www/cepes/foret.geojson'))['features']]
Fg=[g for g,sc in _all if sc>=2 and dk(PK,(g.centroid.x,g.centroid.y))<TARGET*1.3]
_tree=STRtree(Fg) if Fg else None
def inforest(c):
    if not _tree: return False
    p=Point(c)
    for idx in _tree.query(p):
        if Fg[idx].contains(p): return True
    return False
from osgeo import gdal;gdal.UseExceptions()
ds=gdal.Open("work/dem.tif");gt=ds.GetGeoTransform();dem=ds.GetRasterBand(1).ReadAsArray()
def el(c):return float(dem[int((c[1]-gt[3])/gt[5]),int((c[0]-gt[0])/gt[1])])
best=None
for T in [k for k in dist if TARGET*0.35<dist[k]<TARGET*0.62 and inforest(nodes[k])]:
    p1=path(prev,start,T)
    pen=set((p1[i],p1[i+1]) for i in range(len(p1)-1))
    d2,pv2=dij(T,pen,pf=4)
    if start not in d2:continue
    p2=path(pv2,T,start)
    loop=[nodes[k] for k in p1+p2[1:]]
    clean=[loop[0]]
    for c in loop[1:]:
        if dk(clean[-1],c)>0.002:clean.append(c)
    L=sum(dk(clean[i],clean[i+1]) for i in range(len(clean)-1))
    if not (TARGET*0.8<L<TARGET*1.25):continue
    els=[el(c) for c in clean];gain=sum(max(0,els[i+1]-els[i]) for i in range(len(els)-1))
    infrac=sum(1 for c in clean if inforest(c))/len(clean)
    sc=abs(L-TARGET)*1000+gain*2-infrac*300
    if best is None or sc<best[0]:
        best=(sc,L,gain,clean,min(els),max(els),infrac)
if not best:
    print("AUCUNE boucle trouvée");sys.exit(1)
sc,L,gain,clean,lo,hi,infrac=best
print(f"BOUCLE: {L*1000:.0f}m | D+ ~{gain:.0f}m | alt {lo:.0f}-{hi:.0f}m | forêt {infrac*100:.0f}% | {len(clean)}pts")
print(f"parking node: [{nodes[start][1]:.5f},{nodes[start][0]:.5f}]")
json.dump({"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"LineString","coordinates":clean},"properties":{}}]},open("/tmp/loop.geojson","w"))
