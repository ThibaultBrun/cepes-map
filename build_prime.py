#!/usr/bin/env python3
"""Spots prime = ESSENCE/forêt (moteur principal) × exposition douce (secondaire) + BONUS LISIÈRE.
- base = qualité d'essence (score forêt 3/2/1), c'est le vrai moteur du cèpe.
- expo = modulateur doux (0.6..1.0) : le nord garde 60 %, il n'est plus exclu.
- lisière = bonus fort : forêt à ~60 m d'une bordure/clairière (effet de lisière = top cèpes).
Sort aussi une couche lisière dédiée (toggle 🌾)."""
import subprocess, numpy as np, os
from osgeo import gdal
from scipy import ndimage
gdal.UseExceptions()
WORK = "/home/debian/cepes/work"
FORET = "/srv/www/cepes/foret.geojson"

def run(*c): subprocess.run(c, check=True)

dem = gdal.Open(f"{WORK}/dem.tif"); gt = dem.GetGeoTransform(); W = dem.RasterXSize; H = dem.RasterYSize
xmin = gt[0]; ymax = gt[3]; xmax = xmin + gt[1]*W; ymin = ymax + gt[5]*H

# rasterise la forêt par SCORE réel (0 hors forêt, sinon 1/2/3)
run("gdal_rasterize", "-q", "-a", "score", "-init", "0",
    "-te", str(xmin), str(ymin), str(xmax), str(ymax), "-ts", str(W), str(H),
    "-ot", "Byte", FORET, f"{WORK}/forest_score.tif")

ds_s = gdal.Open(f"{WORK}/slope.tif"); slope = ds_s.ReadAsArray().astype("float32")
ds_a = gdal.Open(f"{WORK}/aspect.tif"); asp = ds_a.ReadAsArray().astype("float32")
score = gdal.Open(f"{WORK}/forest_score.tif").ReadAsArray().astype("float32")

# base essence = moteur principal, mais contraste marqué (le feuillu "possible" pèse peu)
base = np.select([score >= 3, score >= 2, score >= 1], [1.0, 0.58, 0.26], default=0.0).astype("float32")
# exposition : PLEINE plage (0.45..1.0), compte vraiment — pic SSE, nord non exclu
warm = (np.cos(np.radians(asp - 155.0)) + 1.0) / 2.0
expo = 0.45 + 0.55 * warm; expo[asp < -1] = 0.70
# pente : PLEINE plage (0.4..1.0), pic 6-22°
sf = np.where(slope < 2, 0.55, np.where(slope <= 22, 1.0,
     np.where(slope <= 38, 1.0 - 0.60*(slope-22)/16.0, 0.40))).astype("float32")

# LISIÈRE : pixels de forêt à <=2 px (~60 m) d'une bordure forêt/non-forêt
forest = score >= 1
near_edge = ndimage.binary_dilation(~forest, iterations=2)
lisiere = forest & near_edge

# produit plein-range : essence × expo × pente, puis boost lisière multiplicatif
prime = base * expo * sf
prime = np.clip(prime * np.where(lisiere, 1.25, 1.0), 0, 1).astype("float32")

# affichage NUANCÉ : seuil haut + gamma → seul le vrai top est vif, le médiocre s'estompe
t = np.clip((prime - 0.30) / 0.70, 0, 1) ** 1.5
show = t > 0.015
rgba = np.zeros((4, H, W), dtype="uint8")
rgba[0] = np.where(show, 255, 0)                 # R constant
rgba[1] = np.where(show, (230 - 160*t), 0)       # G : 230 (jaune) -> 70 (rouge)
rgba[2] = np.where(show, (150 - 125*t), 0)       # B : 150 -> 25
rgba[3] = np.where(show, (26 + 206*t), 0)        # alpha : 26 (quasi invisible) -> 232
drv = gdal.GetDriverByName("GTiff")
out = drv.Create(f"{WORK}/prime_rgba.tif", W, H, 4, gdal.GDT_Byte)
out.SetGeoTransform(gt); out.SetProjection(dem.GetProjection())
for i in range(4): out.GetRasterBand(i+1).WriteArray(rgba[i])
out.FlushCache(); out = None
print("spots prime:", int(show.sum()), "px (essence × expo douce + lisière)")
run("gdal2tiles.py", "-q", "-z", "9-13", "-w", "none", "--xyz", "-r", "bilinear", f"{WORK}/prime_rgba.tif", "/srv/www/cepes/prime")

# couche lisière dédiée (vert-mousse doré translucide)
lr = np.zeros((4, H, W), dtype="uint8")
lr[0] = np.where(lisiere, 190, 0); lr[1] = np.where(lisiere, 205, 0)
lr[2] = np.where(lisiere, 95, 0);  lr[3] = np.where(lisiere, 120, 0)
outl = drv.Create(f"{WORK}/lisiere_rgba.tif", W, H, 4, gdal.GDT_Byte)
outl.SetGeoTransform(gt); outl.SetProjection(dem.GetProjection())
for i in range(4): outl.GetRasterBand(i+1).WriteArray(lr[i])
outl.FlushCache(); outl = None
print("lisière:", int(lisiere.sum()), "px")
run("gdal2tiles.py", "-q", "-z", "9-13", "-w", "none", "--xyz", "-r", "bilinear", f"{WORK}/lisiere_rgba.tif", "/srv/www/cepes/lisiere")
print("tuiles prime + lisiere OK")
