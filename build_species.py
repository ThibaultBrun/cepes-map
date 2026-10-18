#!/usr/bin/env python3
"""Potentiel multi-facteurs PAR ESPÈCE -> tuiles /srv/www/cepes/sp/<key>/.
Facteurs : essence (BD Forêt) × exposition (chaud SSE / frais nord selon l'espèce)
× pente × fond de vallon (humidité, dérivé du DEM) × lisière.
Les cèpes gardent leur couche 'prime' existante."""
import subprocess, json, os, numpy as np
from osgeo import gdal
from scipy import ndimage
gdal.UseExceptions()
WORK = "/home/debian/cepes/work"
FORET = "/srv/www/cepes/foret.geojson"
def run(*c): subprocess.run(c, check=True)

dem_ds = gdal.Open(f"{WORK}/dem.tif"); gt = dem_ds.GetGeoTransform(); prj = dem_ds.GetProjection()
W = dem_ds.RasterXSize; H = dem_ds.RasterYSize
dem = dem_ds.GetRasterBand(1).ReadAsArray().astype("float32")
slope = gdal.Open(f"{WORK}/slope.tif").ReadAsArray().astype("float32")
asp = gdal.Open(f"{WORK}/aspect.tif").ReadAsArray().astype("float32")

# --- essence raster (1=feuillus nobles chêne/hêtre/châtaignier, 2=autres feuillus/mixte, 3=conifères/pin, 0=hors forêt) ---
NOBLE = {"Chênes décidus","Hêtre","Châtaignier","Chênes sempervirents"}
CONIF = {"Pin maritime","Pin laricio, pin noir","Pin autre","Pins mélangés","Conifères","Douglas","Sapin, épicéa","Mélèze"}
gj = json.load(open(FORET))
for f in gj["features"]:
    e = f["properties"].get("essence","")
    f["properties"]["eg"] = 1 if e in NOBLE else (3 if e in CONIF else 2)
tmp = f"{WORK}/foret_eg.geojson"; json.dump(gj, open(tmp,"w"))
xmin=gt[0]; ymax=gt[3]; xmax=xmin+gt[1]*W; ymin=ymax+gt[5]*H
run("gdal_rasterize","-q","-a","eg","-init","0","-te",str(xmin),str(ymin),str(xmax),str(ymax),
    "-ts",str(W),str(H),"-ot","Byte",tmp,f"{WORK}/essence_grp.tif")
eg = gdal.Open(f"{WORK}/essence_grp.tif").ReadAsArray().astype("float32")

# --- facteurs relief ---
warm = (np.cos(np.radians(asp-155.0))+1)/2.0; warm[asp<-1]=0.6          # 1 plein SSE
cool = (np.cos(np.radians(asp-335.0))+1)/2.0; cool[asp<-1]=0.6          # 1 plein NNO (frais)
sf = np.where(slope<2,0.55,np.where(slope<=22,1.0,np.where(slope<=38,1.0-0.6*(slope-22)/16.0,0.4))).astype("float32")
# fond de vallon / humidité : DEM lissé - DEM (positif = creux => frais/humide)
smooth = ndimage.gaussian_filter(dem, sigma=16)          # ~500 m
valley = np.clip((smooth-dem)/14.0, 0, 1).astype("float32")
# lisière (forêt à <=2 px d'une bordure)
forest = eg>=1
lis = (forest & ndimage.binary_dilation(~forest, iterations=2)).astype("float32")

def essw(w):  # eg -> poids
    out = np.zeros_like(eg)
    for k,v in w.items(): out[eg==k]=v
    return out

# profils par espèce : base essence + modulateurs
SPEC = {
 "trompettes": lambda: essw({1:1.0,2:0.55,3:0.1}) * (0.45+0.55*cool) * (0.55+0.45*valley) * (0.7+0.3*sf) + 0.08*lis,
 "girolles":   lambda: essw({1:0.85,2:0.78,3:0.62})* (0.55+0.45*cool) * (0.6+0.4*valley) * (0.7+0.3*sf),
 "sanguins":   lambda: essw({1:0.12,2:0.15,3:1.0}) * (0.85) * (0.7+0.3*sf),
 "piedmouton": lambda: essw({1:0.8,2:0.76,3:0.82}) * (0.6+0.4*cool) * (0.72+0.28*sf),
 "coulemelles":lambda: np.clip(0.85*lis + 0.18*(eg>0) + 0.25*(valley), 0, 1.3) * (slope<18),
 "morilles":   lambda: essw({1:0.7,2:0.82,3:0.15}) * (0.35+0.65*valley) * (0.55+0.45*lis),
}

drv = gdal.GetDriverByName("GTiff")
for key, fn in SPEC.items():
    s = fn().astype("float32")
    mx = np.percentile(s[s>0], 97) if (s>0).any() else 1.0
    t = np.clip((s/max(mx,1e-3) - 0.18)/0.82, 0, 1) ** 1.4
    show = t > 0.02
    rgba = np.zeros((4,H,W),dtype="uint8")
    rgba[0]=np.where(show,255,0)
    rgba[1]=np.where(show,(230-160*t),0)
    rgba[2]=np.where(show,(150-125*t),0)
    rgba[3]=np.where(show,(26+206*t),0)
    out=drv.Create(f"{WORK}/sp_{key}.tif",W,H,4,gdal.GDT_Byte)
    out.SetGeoTransform(gt); out.SetProjection(prj)
    for i in range(4): out.GetRasterBand(i+1).WriteArray(rgba[i])
    out.FlushCache(); out=None
    outdir=f"/srv/www/cepes/sp/{key}"
    run("gdal2tiles.py","-q","-z","9-13","-w","none","--xyz","-r","bilinear",f"{WORK}/sp_{key}.tif",outdir)
    print(f"{key}: {int(show.sum())} px -> {outdir}")
print("OK species tiles")
