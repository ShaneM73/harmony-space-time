"""Build the relief base map for the 3D frame, in the style of
github.com/ShaneM73/European_spatiotemporal_geography: a land-masked elevation grid, a flat sea,
hillshade multiplied over muted per-country tints, borders stroked in the background colour.

Inputs (paths given on the command line, see README):
  --etopo   directory with etopo20data.gz / etopo20lons.gz / etopo20lats.gz (matplotlib/basemap doc/examples)
  --europe  the European_spatiotemporal_geography repo: data/terrain.png (5 km LAEA) + data/boundaries.json (meta)
  --geo     directory with countries.geojson and land.geojson (world-atlas 50m, countries carry a palette index 'c')
Outputs: data/terrain.png (R/G = elevation + 6000 m, B = land mask), data/map_texture_{dark,light}.jpg, data/basemap_meta.json
"""
import argparse, gzip, json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("--etopo", required=True); ap.add_argument("--europe", required=True); ap.add_argument("--geo", required=True)
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
a = ap.parse_args()

LON = (-130.0, 45.0); LAT = (12.0, 70.0)
RES_ELEV = 1 / 6          # degrees per elevation cell (mesh)
RES_TEX = 1 / 16          # degrees per texture pixel
OFFSET = 6000
THEMES = {  # same palettes as European_spatiotemporal_geography
    'dark': dict(palette=['#857558', '#62775a', '#8f675f', '#5f7189', '#857d56', '#75657f', '#537c77', '#8f7853', '#727260', '#885e5d'],
                 ocean='#1b252c', unclaimed='#2b2e31', border=(16, 19, 22), hill=0.65, gamma=1.0),
    'light': dict(palette=['#d9c7a7', '#b5c9a8', '#e3bcae', '#b8c7da', '#ddd3a3', '#c9b6d2', '#a6cbc4', '#e6c7a0', '#c2c1a8', '#d7aaa9'],
                  ocean='#c9d6dc', unclaimed='#dedbd1', border=(255, 255, 255), hill=0.95, gamma=1.6),
}

# ---------------------------------------------------------------- elevation grids
def grid(res):
    cols = int(round((LON[1] - LON[0]) / res)) + 1; rows = int(round((LAT[1] - LAT[0]) / res)) + 1
    lons = LON[0] + np.arange(cols) * res; lats = LAT[1] - np.arange(rows) * res  # rows north -> south
    return lons, lats

def etopo_on(lons, lats):
    topo = np.loadtxt(gzip.open(f"{a.etopo}/etopo20data.gz")); elon = np.loadtxt(gzip.open(f"{a.etopo}/etopo20lons.gz")); elat = np.loadtxt(gzip.open(f"{a.etopo}/etopo20lats.gz"))
    elon = np.where(elon > 180, elon - 360, elon); o = np.argsort(elon); elon = elon[o]; topo = topo[:, o]
    # bilinear sample
    fx = np.interp(lons, elon, np.arange(len(elon))); fy = np.interp(lats, elat, np.arange(len(elat)))
    x0 = np.clip(np.floor(fx).astype(int), 0, len(elon) - 2); y0 = np.clip(np.floor(fy).astype(int), 0, len(elat) - 2)
    tx = (fx - x0)[None, :]; ty = (fy - y0)[:, None]
    X0, Y0 = np.meshgrid(x0, y0)
    return (topo[Y0, X0] * (1 - tx) * (1 - ty) + topo[Y0, X0 + 1] * tx * (1 - ty) + topo[Y0 + 1, X0] * (1 - tx) * ty + topo[Y0 + 1, X0 + 1] * tx * ty)

def europe_on(lons, lats):
    """Reproject the 5 km LAEA grid of the European app onto lon/lat; NaN outside its extent."""
    meta = json.load(open(f"{a.europe}/data/boundaries.json"))["meta"]
    img = np.asarray(Image.open(f"{a.europe}/data/terrain.png").convert("RGB")).astype(np.int32)
    elev = img[:, :, 0] * 256 + img[:, :, 1] - meta["elevationOffset"]; land = img[:, :, 2] > 127
    elev = np.where(land, np.maximum(elev, 0), np.nan).astype(float)
    xmin, ymin, xmax, ymax = meta["extent"]; kpp = meta["kmPerPx"]; p = meta["projection"]
    lon0, lat0, R = math.radians(p["lon0"]), math.radians(p["lat0"]), p["R"]
    LO, LA = np.meshgrid(np.radians(lons), np.radians(lats))
    k = np.sqrt(2 / (1 + math.sin(lat0) * np.sin(LA) + math.cos(lat0) * np.cos(LA) * np.cos(LO - lon0)))
    x = R * k * np.cos(LA) * np.sin(LO - lon0); y = R * k * (math.cos(lat0) * np.sin(LA) - math.sin(lat0) * np.cos(LA) * np.cos(LO - lon0))
    gx = (x - xmin) / kpp - 0.5; gy = (ymax - y) / kpp - 0.5
    H, W = elev.shape
    inside = (gx >= 0) & (gx <= W - 1) & (gy >= 0) & (gy <= H - 1)
    gxc = np.clip(gx, 0, W - 1.001); gyc = np.clip(gy, 0, H - 1.001)
    x0 = np.floor(gxc).astype(int); y0 = np.floor(gyc).astype(int); tx = gxc - x0; ty = gyc - y0
    def s(yy, xx): return elev[yy, xx]
    v = s(y0, x0) * (1 - tx) * (1 - ty) + s(y0, x0 + 1) * tx * (1 - ty) + s(y0 + 1, x0) * (1 - tx) * ty + s(y0 + 1, x0 + 1) * tx * ty
    v = np.where(inside, v, np.nan)
    # inside the extent but on sea in the 5 km data -> 0 (the land mask below decides)
    v = np.where(inside & np.isnan(v), 0.0, v)
    return v

def rasterize(geojson_path, lons, lats, by_colour=False):
    """Fill polygons into a lon/lat raster. Returns land mask (uint8) or a palette-index raster (-1 = none)."""
    gj = json.load(open(geojson_path)); W, H = len(lons), len(lats)
    sx = (W - 1) / (LON[1] - LON[0]); sy = (H - 1) / (LAT[1] - LAT[0])
    img = Image.new("I", (W, H), 0 if not by_colour else 0)
    d = ImageDraw.Draw(img)
    for f in gj["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        val = 1 if not by_colour else int(f["properties"]["c"]) + 1
        for poly in polys:
            # a ring that jumps across the antimeridian is drawn in 0..360 space, twice (shifted by -360),
            # so it never paints a false edge across the map
            def draw(ring, fill):
                xs = np.array([pt[0] for pt in ring]); ys = np.array([pt[1] for pt in ring])
                shifts = [0.0]
                dx = np.diff(xs)
                if (np.abs(dx) > 180).any():  # unwrap: a jump of ~360 degrees continues the ring instead of crossing the map
                    dx = np.where(dx > 180, dx - 360, np.where(dx < -180, dx + 360, dx))
                    xs = np.concatenate([[xs[0]], xs[0] + np.cumsum(dx)]); shifts = [0.0, -360.0, 360.0]
                for sh in shifts:
                    pts = [((x + sh - LON[0]) * sx, (LAT[1] - y) * sy) for x, y in zip(xs, ys)]
                    if len(pts) >= 3: d.polygon(pts, fill=fill)
            draw(poly[0], val)
            for hole in poly[1:]: draw(hole, 0)
    arr = np.asarray(img, dtype=np.int32)
    return arr if by_colour else (arr > 0).astype(np.uint8)

# ---- elevation for the mesh
lons_e, lats_e = grid(RES_ELEV)
base = etopo_on(lons_e, lats_e); eu = europe_on(lons_e, lats_e)
elev_e = np.where(np.isnan(eu), base, eu)
land_e = rasterize(f"{a.geo}/land.geojson", lons_e, lats_e)
elev_e = np.where(land_e > 0, np.maximum(elev_e, 0), 0)
rgb = np.zeros(elev_e.shape + (3,), np.uint8); v = np.clip(elev_e + OFFSET, 0, 65535).astype(np.int32)
rgb[:, :, 0] = v // 256; rgb[:, :, 1] = v % 256; rgb[:, :, 2] = land_e * 255
Image.fromarray(rgb, "RGB").save(f"{a.out}/terrain.png", optimize=True)
print("terrain.png", rgb.shape, os.path.getsize(f"{a.out}/terrain.png"), "bytes; max elev", int(elev_e.max()))

# ---- texture: country tints x hillshade, flat sea, borders
lons_t, lats_t = grid(RES_TEX)
base_t = etopo_on(lons_t, lats_t); eu_t = europe_on(lons_t, lats_t)
elev_t = np.where(np.isnan(eu_t), base_t, eu_t)
land_t = rasterize(f"{a.geo}/land.geojson", lons_t, lats_t)
elev_t = np.where(land_t > 0, np.maximum(elev_t, 0), 0).astype(float)
cidx = rasterize(f"{a.geo}/countries.geojson", lons_t, lats_t, by_colour=True)
# hillshade (same formula as the European app: azimuth 315, altitude 45, z = 2.2)
cell_y = RES_TEX * 110574.0; cell_x = RES_TEX * 111320.0 * np.cos(np.radians(lats_t))[:, None]
z = 3.5; az = math.radians(315); alt = math.radians(45)
dzdx = (np.roll(elev_t, -1, 1) - np.roll(elev_t, 1, 1)) * z / (2 * cell_x); dzdy = (np.roll(elev_t, 1, 0) - np.roll(elev_t, -1, 0)) * z / (2 * cell_y)
slope = np.arctan(np.hypot(dzdx, dzdy)); aspect = np.arctan2(dzdy, -dzdx)
hs = np.cos(alt) * np.cos(slope) + np.sin(alt) * np.sin(slope) * np.cos(az - aspect)
hill = np.clip(0.5 + 0.5 * hs / math.sin(alt), 0, 1)
# outside the 5 km European data the elevation comes from the 1/3-degree ETOPO grid: shade it at its own
# resolution (on the coarser mesh grid) and upsample, otherwise the interpolated slopes are too gentle to see
cy_e = RES_ELEV * 110574.0; cx_e = RES_ELEV * 111320.0 * np.cos(np.radians(lats_e))[:, None]
ex = (np.roll(elev_e, -1, 1) - np.roll(elev_e, 1, 1)) * 14.0 / (2 * cx_e); ey = (np.roll(elev_e, 1, 0) - np.roll(elev_e, -1, 0)) * 14.0 / (2 * cy_e)
sl = np.arctan(np.hypot(ex, ey)); asp = np.arctan2(ey, -ex)
hs_e = np.cos(alt) * np.cos(sl) + np.sin(alt) * np.sin(sl) * np.cos(az - asp)
hill_e = np.clip(0.5 + 0.5 * hs_e / math.sin(alt), 0, 1)
hill_up = np.asarray(Image.fromarray((hill_e * 255).astype(np.uint8)).resize((len(lons_t), len(lats_t)), Image.BICUBIC)).astype(float) / 255
hill = np.where(np.isnan(eu_t), hill_up, hill); hill = np.where(land_t > 0, hill, 1.0)
hex2rgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
edge = (cidx != np.roll(cidx, 1, 1)) | (cidx != np.roll(cidx, 1, 0))
edge &= (land_t > 0) & (np.roll(land_t, 1, 1) > 0) & (np.roll(land_t, 1, 0) > 0)
for name, T in THEMES.items():
    pal = np.array([hex2rgb(T['unclaimed'])] + [hex2rgb(c) for c in T['palette']])
    tex = pal[np.clip(cidx, 0, len(pal) - 1)]
    tex = np.where(land_t[:, :, None] > 0, tex, hex2rgb(T['ocean'])[None, None, :])
    # light theme: steeper shading curve so slopes away from the light read as shadow on pale tints
    h = np.where(land_t > 0, hill ** T['gamma'], 1.0)
    tex = tex * (1 - T['hill'] + T['hill'] * h[:, :, None])
    arr = np.clip(tex, 0, 255).astype(np.uint8).copy()
    arr[edge] = (arr[edge] * 0.3 + np.array(T['border']) * 0.7).astype(np.uint8)
    img = Image.fromarray(arr, "RGB"); img.save(f"{a.out}/map_texture_{name}.jpg", quality=82, optimize=True)
    print(f"map_texture_{name}.jpg", img.size, os.path.getsize(f"{a.out}/map_texture_{name}.jpg"), "bytes")
json.dump(dict(lon=LON, lat=LAT, elevSize=[len(lons_e), len(lats_e)], elevationOffset=OFFSET, texSize=list(img.size),
               sources=["ETOPO 20-minute grid (NOAA, via matplotlib/basemap examples)", "European_spatiotemporal_geography terrain.png (AWS Terrain Tiles, 5 km LAEA) for Europe, North Africa and the Near East", "world-atlas 50m land and countries (Natural Earth)"]),
          open(f"{a.out}/basemap_meta.json", "w"))
