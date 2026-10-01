"""Point-in-polygon assignment: Board subdistrict, community area, ward. Pure Python.

Polygons are stored as lists of rings; membership uses the even-odd rule across all
rings of a feature, so holes and multipart shapes are handled without orientation tests.
"""
import io
import json
import zipfile

import shapefile  # pyshp

from .common import RAW


class Layer:
    def __init__(self, features):
        # features: [(label, [ring, ...])], ring = [(x, y), ...]
        self.features = []
        for label, rings in features:
            xs = [p[0] for r in rings for p in r]
            ys = [p[1] for r in rings for p in r]
            self.features.append((label, rings, (min(xs), min(ys), max(xs), max(ys))))

    @staticmethod
    def _inside(x, y, ring):
        inside = False
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        return inside

    def lookup(self, lon, lat):
        """-> list of labels containing the point (normally exactly one)."""
        hits = []
        for label, rings, (x0, y0, x1, y1) in self.features:
            if not (x0 <= lon <= x1 and y0 <= lat <= y1):
                continue
            n = sum(self._inside(lon, lat, r) for r in rings)
            if n % 2 == 1:
                hits.append(label)
        return hits


def _geojson_layer(path, label_field, number=False):
    gj = json.load(open(path))
    feats = []
    for f in gj["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = [[tuple(p[:2]) for p in ring] for poly in polys for ring in poly]
        label = f["properties"][label_field]
        feats.append((label, rings))
    return Layer(feats)


def load_subdistricts():
    z = zipfile.ZipFile(RAW / "subdistricts.zip")
    parts = {n.rsplit(".", 1)[1]: io.BytesIO(z.read(n)) for n in z.namelist()}
    r = shapefile.Reader(shp=parts["shp"], shx=parts["shx"], dbf=parts["dbf"])
    names = [f[0] for f in r.fields[1:]]
    feats = []
    for sr in r.shapeRecords():
        rec = dict(zip(names, sr.record))
        pts = sr.shape.points
        idx = list(sr.shape.parts) + [len(pts)]
        rings = [pts[idx[i]:idx[i + 1]] for i in range(len(idx) - 1)]
        label = str(rec["LONGNAME"]).replace("District ", "").strip()
        feats.append((label, rings))
    return Layer(feats)


def load_community_areas():
    return _geojson_layer(RAW / "chi_community_areas.geojson", "community")


def load_wards():
    return _geojson_layer(RAW / "chi_wards.geojson", "ward")
