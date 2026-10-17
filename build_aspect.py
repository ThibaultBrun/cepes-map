#!/usr/bin/env python3
"""Couche favorabilité "lisière chaude" = exposition sud × pente douce, depuis le DEM Copernicus.
Sort un RGBA GeoTIFF puis des tuiles XYZ drapables sur le terrain 3D."""
import subprocess, numpy as np, os
from osgeo import gdal
gdal.UseExceptions()

RAW = "/home/debian/dem/raw"
WORK = "/home/debian/cepes/work"
os.makedirs(WORK, exist_ok=True)
BBOX = (-2.10, 43.04, -0.86, 43.94)  # lon_min lat_min lon_max lat_max

def run(*c): subprocess.run(c, check=True)

# 1. mosaïque + clip
run("gdalbuildvrt", f"{WORK}/dem.vrt", *[f"{RAW}/{f}" for f in os.listdir(RAW) if f.endswith(".tif")])
run("gdalwarp", "-q", "-overwrite", "-te", str(BBOX[0]), str(BBOX[1]), str(BBOX[2]), str(BBOX[3]),
    "-tr", "0.00028", "0.00028", "-r", "bilinear", f"{WORK}/dem.vrt", f"{WORK}/dem.tif")
# 2. pente + exposition
run("gdaldem", "slope", f"{WORK}/dem.tif", f"{WORK}/slope.tif", "-q", "-s", "111120")
run("gdaldem", "aspect", f"{WORK}/dem.tif", f"{WORK}/aspect.tif", "-q")

# 3. favorabilité
ds_s = gdal.Open(f"{WORK}/slope.tif"); slope = ds_s.GetRasterBand(1).ReadAsArray().astype("float32")
ds_a = gdal.Open(f"{WORK}/aspect.tif"); asp = ds_a.GetRasterBand(1).ReadAsArray().astype("float32")
# southness: 1 plein sud, 0 plein nord
south = (np.cos(np.radians(asp - 180.0)) + 1.0) / 2.0
south[asp < -1] = 0.3  # plat = neutre-bas
# facteur pente: top 5-20°, nul <2 et >35
sf = np.where(slope < 2, 0.15,
     np.where(slope <= 20, 1.0,
     np.where(slope <= 35, (35.0 - slope) / 15.0, 0.0))).astype("float32")
suit = south * sf  # 0..1

# 4. RGBA (ambre->rouge, alpha selon suit, seuil 0.4)
h, w = suit.shape
rgba = np.zeros((4, h, w), dtype="uint8")
t = np.clip((suit - 0.40) / 0.60, 0, 1)  # 0 au seuil, 1 au top
mask = t > 0
rgba[0] = np.where(mask, 255, 0)                      # R
rgba[1] = np.where(mask, (206 - 66 * t), 0)           # G: or 206 -> ambre 140
rgba[2] = np.where(mask, (96 - 60 * t), 0)            # B: 96 -> 36
rgba[3] = np.where(mask, (55 + 95 * t), 0)            # alpha doux 55 -> 150 (voile, pas nappe)

drv = gdal.GetDriverByName("GTiff")
out = drv.Create(f"{WORK}/suit_rgba.tif", w, h, 4, gdal.GDT_Byte)
out.SetGeoTransform(ds_s.GetGeoTransform()); out.SetProjection(ds_s.GetProjection())
for i in range(4): out.GetRasterBand(i + 1).WriteArray(rgba[i])
out.FlushCache(); out = None
print("suit_rgba.tif OK — couverture favorable:", int(mask.sum()), "px")

# 5. tuiles XYZ
run("gdal2tiles.py", "-q", "-z", "9-13", "-w", "none", "--xyz", "-r", "bilinear",
    f"{WORK}/suit_rgba.tif", "/srv/www/cepes/expo")
print("tuiles /srv/www/cepes/expo OK")
