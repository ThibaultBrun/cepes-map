#!/usr/bin/env python3
"""Couche "spots prime" = versant sud chaud ∩ forêt favorable (croisement strict).
Réutilise work/slope.tif + work/aspect.tif, masque par la forêt score>=2, sort des tuiles."""
import subprocess, numpy as np, os
from osgeo import gdal
gdal.UseExceptions()
WORK = "/home/debian/cepes/work"
FORET = "/srv/www/cepes/foret.geojson"

def run(*c): subprocess.run(c, check=True)

dem = gdal.Open(f"{WORK}/dem.tif"); gt = dem.GetGeoTransform(); W = dem.RasterXSize; H = dem.RasterYSize
xmin = gt[0]; ymax = gt[3]; xmax = xmin + gt[1]*W; ymin = ymax + gt[5]*H

# masque forêt favorable (score>=2) sur la même grille
run("gdal_rasterize", "-q", "-burn", "1", "-where", "score >= 2", "-init", "0",
    "-te", str(xmin), str(ymin), str(xmax), str(ymax), "-ts", str(W), str(H),
    "-ot", "Byte", FORET, f"{WORK}/forest_mask.tif")

ds_s = gdal.Open(f"{WORK}/slope.tif"); slope = ds_s.ReadAsArray().astype("float32")
ds_a = gdal.Open(f"{WORK}/aspect.tif"); asp = ds_a.ReadAsArray().astype("float32")
ds_m = gdal.Open(f"{WORK}/forest_mask.tif"); mask = ds_m.ReadAsArray().astype("float32")

south = (np.cos(np.radians(asp - 180.0)) + 1.0) / 2.0; south[asp < -1] = 0.3
sf = np.where(slope < 2, 0.15, np.where(slope <= 20, 1.0, np.where(slope <= 35, (35.0-slope)/15.0, 0.0))).astype("float32")
prime = south * sf * mask  # 0..1, uniquement sur forêt

t = np.clip((prime - 0.42) / 0.58, 0, 1)
show = t > 0
rgba = np.zeros((4, H, W), dtype="uint8")
rgba[0] = np.where(show, 255, 0)
rgba[1] = np.where(show, (215 - 55*t), 0)   # or vif -> ambre
rgba[2] = np.where(show, (110 - 70*t), 0)
rgba[3] = np.where(show, (110 + 125*t), 0)  # plus marqué que l'expo large
drv = gdal.GetDriverByName("GTiff")
out = drv.Create(f"{WORK}/prime_rgba.tif", W, H, 4, gdal.GDT_Byte)
out.SetGeoTransform(gt); out.SetProjection(dem.GetProjection())
for i in range(4): out.GetRasterBand(i+1).WriteArray(rgba[i])
out.FlushCache(); out = None
print("spots prime:", int(show.sum()), "px (versant sud ∩ forêt)")
run("gdal2tiles.py", "-q", "-z", "9-13", "-w", "none", "--xyz", "-r", "bilinear", f"{WORK}/prime_rgba.tif", "/srv/www/cepes/prime")
print("tuiles /srv/www/cepes/prime OK")
