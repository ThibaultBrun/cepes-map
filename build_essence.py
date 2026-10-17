#!/usr/bin/env python3
"""Couche essences 10m -> tuiles raster colorées par espèce.
Codes essence10.tif : 2=Pinus 3=Fagus 4=Quercus 6=Feuillu-mixte (autres=transparent).
Scores cèpes : Quercus+Fagus=top, Feuillu=bon, Pinus=moyen (B.pinophilus)."""
import subprocess, numpy as np, os
from osgeo import gdal
gdal.UseExceptions()

WORK = "/home/debian/cepes/work"
OUT_DIR = "/srv/www/cepes/essence"

def run(*c): subprocess.run(c, check=True)

# --- 1. Reprojeter/rééchantillonner essence10.tif sur la grille DEM (nearest pour classes)
dem = gdal.Open(f"{WORK}/dem.tif")
gt = dem.GetGeoTransform()
W = dem.RasterXSize; H = dem.RasterYSize
xmin = gt[0]; ymax = gt[3]
xmax = xmin + gt[1] * W; ymin = ymax + gt[5] * H

ess_warp = f"{WORK}/essence_warp.tif"
run("gdalwarp", "-q", "-overwrite",
    "-te", str(xmin), str(ymin), str(xmax), str(ymax),
    "-ts", str(W), str(H),
    "-r", "mode",  # mode = valeur dominante (classes discrètes)
    "-ot", "Byte",
    f"{WORK}/essence10.tif", ess_warp)

# --- 2. Lire les données
ds = gdal.Open(ess_warp)
ess = ds.GetRasterBand(1).ReadAsArray()

# --- 3. Palette RGBA champêtre par essence
# val -> (R, G, B, A)
PALETTE = {
    4: (212, 160,  23, 200),  # Quercus/Chêne   → or chaud (top cèpes)
    3: (160,  82,  45, 190),  # Fagus/Hêtre     → rouille cuivrée (top cèpes)
    6: ( 82, 183, 136, 160),  # Feuillu mixte   → vert sauge (bon)
    2: ( 45, 106,  79, 140),  # Pinus/Pin       → vert sombre (B.pinophilus)
}

rgba = np.zeros((4, H, W), dtype="uint8")
for val, (r, g, b, a) in PALETTE.items():
    mask = ess == val
    rgba[0][mask] = r
    rgba[1][mask] = g
    rgba[2][mask] = b
    rgba[3][mask] = a

# stats
total = 0
for val, _ in PALETTE.items():
    n = int((ess == val).sum())
    names = {2:"Pinus", 3:"Fagus", 4:"Quercus", 6:"Feuillu"}
    print(f"  {names[val]:10s} ({val}): {n:>8d} px")
    total += n
print(f"  Total essences cartographiées: {total} px / {W*H} px")

# --- 4. Écrire RGBA tif
rgba_tif = f"{WORK}/essence_rgba.tif"
drv = gdal.GetDriverByName("GTiff")
out = drv.Create(rgba_tif, W, H, 4, gdal.GDT_Byte)
out.SetGeoTransform(gt)
out.SetProjection(dem.GetProjection())
for i in range(4):
    out.GetRasterBand(i + 1).WriteArray(rgba[i])
out.FlushCache(); out = None
print(f"Raster RGBA: {rgba_tif}")

# --- 5. Tuiles
os.makedirs(OUT_DIR, exist_ok=True)
run("gdal2tiles.py", "-q", "-z", "9-13", "-w", "none", "--xyz", "-r", "near",
    rgba_tif, OUT_DIR)
print(f"Tuiles: {OUT_DIR} OK")
