#!/usr/bin/env python3
"""Couche "versants favorables" = exposition douce × pente, depuis le DEM Copernicus.
Modèle rééquilibré (climat atlantique) : la chaleur n'est plus le seul critère.
Le pic est au sud-sud-est (soleil du matin + sol frais) et le NORD n'est PAS tué
(plancher 0.45) car au Pays Basque le facteur limitant du cèpe est l'humidité, pas le froid."""
import subprocess, numpy as np, os
from osgeo import gdal
gdal.UseExceptions()

RAW = "/home/debian/dem/raw"
WORK = "/home/debian/cepes/work"
os.makedirs(WORK, exist_ok=True)
BBOX = (-2.10, 43.04, -0.86, 43.94)  # lon_min lat_min lon_max lat_max

def run(*c): subprocess.run(c, check=True)

# 1. mosaïque + clip (seulement si absent)
if not os.path.exists(f"{WORK}/dem.tif"):
    run("gdalbuildvrt", f"{WORK}/dem.vrt", *[f"{RAW}/{f}" for f in os.listdir(RAW) if f.endswith(".tif")])
    run("gdalwarp", "-q", "-overwrite", "-te", str(BBOX[0]), str(BBOX[1]), str(BBOX[2]), str(BBOX[3]),
        "-tr", "0.00028", "0.00028", "-r", "bilinear", f"{WORK}/dem.vrt", f"{WORK}/dem.tif")
if not os.path.exists(f"{WORK}/slope.tif"):
    run("gdaldem", "slope", f"{WORK}/dem.tif", f"{WORK}/slope.tif", "-q", "-s", "111120")
if not os.path.exists(f"{WORK}/aspect.tif"):
    run("gdaldem", "aspect", f"{WORK}/dem.tif", f"{WORK}/aspect.tif", "-q")

ds_s = gdal.Open(f"{WORK}/slope.tif"); slope = ds_s.GetRasterBand(1).ReadAsArray().astype("float32")
ds_a = gdal.Open(f"{WORK}/aspect.tif"); asp = ds_a.GetRasterBand(1).ReadAsArray().astype("float32")

# exposition rééquilibrée : pic au sud-sud-est (~155°), plancher 0.45 (le nord/est reste favorable)
warm = (np.cos(np.radians(asp - 155.0)) + 1.0) / 2.0   # 1 @155°, 0 @335°
expo = 0.45 + 0.55 * warm                               # 0.45 (nord) .. 1.0 (SSE)
expo[asp < -1] = 0.72                                   # plat / fond de vallon = neutre-haut (frais, humide)
# pente : pic 6-22°, pénalité DOUCE au-delà (jamais nulle sauf quasi-falaise)
sf = np.where(slope < 2, 0.6,
     np.where(slope <= 22, 1.0,
     np.where(slope <= 38, 1.0 - 0.55 * (slope - 22) / 16.0, 0.45))).astype("float32")
suit = expo * sf  # ~0.27 .. 1.0

# RGBA (or -> ambre, alpha selon suit, seuil 0.58 pour ne garder que le vraiment favorable)
h, w = suit.shape
rgba = np.zeros((4, h, w), dtype="uint8")
t = np.clip((suit - 0.58) / 0.42, 0, 1)
mask = t > 0
rgba[0] = np.where(mask, 255, 0)
rgba[1] = np.where(mask, (206 - 66 * t), 0)
rgba[2] = np.where(mask, (96 - 60 * t), 0)
rgba[3] = np.where(mask, (50 + 90 * t), 0)

drv = gdal.GetDriverByName("GTiff")
out = drv.Create(f"{WORK}/suit_rgba.tif", w, h, 4, gdal.GDT_Byte)
out.SetGeoTransform(ds_s.GetGeoTransform()); out.SetProjection(ds_s.GetProjection())
for i in range(4): out.GetRasterBand(i + 1).WriteArray(rgba[i])
out.FlushCache(); out = None
print("versants favorables — couverture:", int(mask.sum()), "px")

run("gdal2tiles.py", "-q", "-z", "9-13", "-w", "none", "--xyz", "-r", "bilinear",
    f"{WORK}/suit_rgba.tif", "/srv/www/cepes/expo")
print("tuiles /srv/www/cepes/expo OK")
