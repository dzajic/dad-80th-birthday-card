#!/usr/bin/env python3
"""Build a North Atlantic route map from Natural Earth 50m.

Data: Natural Earth admin-0 countries and lakes, 1:50m, public domain.
https://www.naturalearthdata.com/

The geographic window is the crossing that matters: Montreal on the left,
Ireland, Britain, France, and Czechia on the right. Coastlines are projected
with a Lambert conformal conic, then clipped to that window so shapes stay
accurate instead of being redrawn by hand.
"""

import json
import math
from pathlib import Path

COUNTRIES = Path("/tmp/ne/countries.json")
LAKES = Path("/tmp/ne/lakes.json")
OUT = Path(__file__).resolve().parents[1] / "images" / "journey-map.svg"

# Geographic window (degrees). Tight enough that Europe and eastern Canada
# are large, wide enough that the Atlantic crossing reads as ocean.
LON0, LON1 = -80.0, 26.0
LAT0, LAT1 = 35.5, 63.5
PHI1, PHI2, PHI0 = 38.0, 58.0, 47.0
LAM0 = -28.0

HIGHLIGHT = {"Canada", "Czechia", "France", "United Kingdom"}

CITIES = [
    # name, lon, lat, anchor, dx, dy — kept off the route line
    ("Praha", 14.4378, 50.0755, "start", 16, -18),
    ("Paris", 2.3522, 48.8566, "middle", 8, 32),
    ("London", -0.1278, 51.5074, "middle", -6, -44),
    ("Montréal", -73.5673, 45.5017, "start", 16, -28),
]


def rad(deg):
    return deg * math.pi / 180.0


def make_projector():
    p1, p2, p0, l0 = map(rad, (PHI1, PHI2, PHI0, LAM0))

    def t_of(phi):
        return math.tan(math.pi / 4 + phi / 2)

    n = math.log(math.cos(p1) / math.cos(p2)) / math.log(t_of(p2) / t_of(p1))
    f_const = math.cos(p1) * (t_of(p1) ** n) / n
    rho0 = f_const / (t_of(p0) ** n)

    def project(lon, lat):
        lat = max(min(lat, 89.0), -89.0)
        phi, lam = rad(lat), rad(lon)
        rho = f_const / (t_of(phi) ** n)
        x = rho * math.sin(n * (lam - l0))
        y = rho0 - rho * math.cos(n * (lam - l0))
        return x, y

    return project


project = make_projector()


def bounds():
    pts = []
    lat = LAT0
    while lat <= LAT1 + 1e-6:
        lon = LON0
        while lon <= LON1 + 1e-6:
            pts.append(project(lon, lat))
            lon += 2
        lat += 2
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


X0, Y0, X1, Y1 = bounds()


def _intersect(a, b, edge, value):
    ax, ay = a
    bx, by = b
    if edge in ("l", "r"):
        denom = bx - ax
        t = 0 if denom == 0 else (value - ax) / denom
        return value, ay + t * (by - ay)
    denom = by - ay
    t = 0 if denom == 0 else (value - ay) / denom
    return ax + t * (bx - ax), value


def clip(points):
    """Sutherland–Hodgman clip in projected coordinates."""
    edges = (
        ("l", X0, lambda p: p[0] >= X0 - 1e-12),
        ("r", X1, lambda p: p[0] <= X1 + 1e-12),
        ("b", Y0, lambda p: p[1] >= Y0 - 1e-12),
        ("t", Y1, lambda p: p[1] <= Y1 + 1e-12),
    )
    output = points
    for edge, value, inside in edges:
        if not output:
            return []
        nxt = []
        prev = output[-1]
        prev_in = inside(prev)
        for cur in output:
            cur_in = inside(cur)
            if cur_in:
                if not prev_in:
                    nxt.append(_intersect(prev, cur, edge, value))
                nxt.append(cur)
            elif prev_in:
                nxt.append(_intersect(prev, cur, edge, value))
            prev, prev_in = cur, cur_in
        output = nxt
    return output


def geom_bbox(coords, acc=None):
    if acc is None:
        acc = [1e9, 1e9, -1e9, -1e9]
    if isinstance(coords[0], (int, float)):
        lon, lat = coords[0], coords[1]
        acc[0] = min(acc[0], lon)
        acc[1] = min(acc[1], lat)
        acc[2] = max(acc[2], lon)
        acc[3] = max(acc[3], lat)
        return acc
    for part in coords:
        geom_bbox(part, acc)
    return acc


def overlaps(coords):
    minx, miny, maxx, maxy = geom_bbox(coords)
    return not (maxx < LON0 or minx > LON1 or maxy < LAT0 or miny > LAT1)


def iter_polygons(geom):
    kind = geom["type"]
    coords = geom["coordinates"]
    if kind == "Polygon":
        yield coords
    elif kind == "MultiPolygon":
        yield from coords
    elif kind == "GeometryCollection":
        for g in geom["geometries"]:
            yield from iter_polygons(g)


VW, VH = 1400, 980
PAD = 28
SPAN_X = X1 - X0
SPAN_Y = Y1 - Y0
SCALE = min((VW - 2 * PAD) / SPAN_X, (VH - 2 * PAD) / SPAN_Y)
USED_W = SPAN_X * SCALE
USED_H = SPAN_Y * SCALE
OX = (VW - USED_W) / 2
OY = (VH - USED_H) / 2


def to_svg(x, y):
    sx = OX + (x - X0) * SCALE
    sy = OY + (Y1 - y) * SCALE
    return sx, sy


def ring_to_path(ring):
    projected = [project(lon, lat) for lon, lat in ring]
    # Drop consecutive duplicates before clipping.
    cleaned = [projected[0]]
    for pt in projected[1:]:
        if abs(pt[0] - cleaned[-1][0]) + abs(pt[1] - cleaned[-1][1]) > 1e-9:
            cleaned.append(pt)
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
        cleaned = cleaned[:-1]
    clipped = clip(cleaned)
    if len(clipped) < 3:
        return ""
    pts = [to_svg(x, y) for x, y in clipped]
    commands = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    commands.extend(f"L{x:.1f} {y:.1f}" for x, y in pts[1:])
    commands.append("Z")
    return "".join(commands)


def feature_path(geom):
    chunks = []
    for polygon in iter_polygons(geom):
        for ring in polygon:
            if len(ring) < 4:
                continue
            path = ring_to_path(ring)
            if path:
                chunks.append(path)
    return "".join(chunks)


def great_circle(lon1, lat1, lon2, lat2, steps):
    p1, l1 = rad(lat1), rad(lon1)
    p2, l2 = rad(lat2), rad(lon2)
    d = 2 * math.asin(
        math.sqrt(
            math.sin((p2 - p1) / 2) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2
        )
    )
    if d == 0:
        return [(lon1, lat1)]
    pts = []
    for i in range(steps + 1):
        f = i / steps
        a = math.sin((1 - f) * d) / math.sin(d)
        b = math.sin(f * d) / math.sin(d)
        x = a * math.cos(p1) * math.cos(l1) + b * math.cos(p2) * math.cos(l2)
        y = a * math.cos(p1) * math.sin(l1) + b * math.cos(p2) * math.sin(l2)
        z = a * math.sin(p1) + b * math.sin(p2)
        lat = math.degrees(math.atan2(z, math.hypot(x, y)))
        lon = math.degrees(math.atan2(y, x))
        pts.append((lon, lat))
    return pts


def route_points():
    stops = [(c[1], c[2]) for c in CITIES]
    pts = []
    steps = [18, 12, 56]
    for (a, b), n in zip(zip(stops, stops[1:]), steps):
        seg = great_circle(a[0], a[1], b[0], b[1], n)
        if pts:
            seg = seg[1:]
        pts.extend(seg)
    return pts


def main():
    countries = json.loads(COUNTRIES.read_text())
    lakes = json.loads(LAKES.read_text())

    land = []
    hi = []
    for feature in countries["features"]:
        geom = feature["geometry"]
        if not overlaps(geom["coordinates"]):
            continue
        path = feature_path(geom)
        if not path:
            continue
        name = feature["properties"].get("NAME") or ""
        (hi if name in HIGHLIGHT else land).append(path)

    water = []
    for feature in lakes["features"]:
        geom = feature["geometry"]
        if not geom or not overlaps(geom["coordinates"]):
            continue
        path = feature_path(geom)
        if path:
            water.append(path)

    route = []
    for lon, lat in route_points():
        sx, sy = to_svg(*project(lon, lat))
        route.append(f"{sx:.1f},{sy:.1f}")

    graticule = []
    for lon in range(-70, 21, 10):
        line = []
        lat = LAT0
        while lat <= LAT1 + 1e-6:
            line.append(to_svg(*project(lon, lat)))
            lat += 1.5
        graticule.append(line)
    for lat in range(40, 61, 10):
        line = []
        lon = LON0
        while lon <= LON1 + 1e-6:
            line.append(to_svg(*project(lon, lat)))
            lon += 1.5
        graticule.append(line)

    def poly(points):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    city_svg = []
    for name, lon, lat, anchor, dx, dy in CITIES:
        x, y = to_svg(*project(lon, lat))
        city_svg.append(
            f'<g class="city">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="#9d4638" stroke="#f7f1e7" stroke-width="2.5"/>'
            f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" fill="#1c2c30" stroke="#f6f1e8" stroke-width="5" paint-order="stroke fill" stroke-linejoin="round">{name}</text>'
            f"</g>"
        )

    # A quiet ocean label, placed by eye in projected space near 40W, 45N.
    ax, ay = to_svg(*project(-40.0, 46.0))

    grat = "\n".join(
        f'<polyline points="{poly(line)}"/>' for line in graticule
    )
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" role="img" aria-labelledby="mapTitle mapDesc">
<title id="mapTitle">From Prague to Montreal</title>
<desc id="mapDesc">A geographically accurate map of the North Atlantic. A route runs from Prague to Paris, London, and Montreal.</desc>
<rect width="{VW}" height="{VH}" fill="#7e9894"/>
<g fill="none" stroke="#f4efe6" stroke-width="0.6" opacity="0.28">
{grat}
</g>
<g fill="#e5d6c2" stroke="#314843" stroke-width="2.4" stroke-linejoin="round" fill-rule="evenodd">
<path d="{''.join(land)}"/>
</g>
<g fill="#f3e6ce" stroke="#314843" stroke-width="2.4" stroke-linejoin="round" fill-rule="evenodd">
<path d="{''.join(hi)}"/>
</g>
<g fill="#7e9894" stroke="#7e9894" stroke-width="0.6" fill-rule="evenodd">
<path d="{''.join(water)}"/>
</g>
<polyline points="{' '.join(route)}" fill="none" stroke="#7a342c" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
<polyline points="{' '.join(route)}" fill="none" stroke="#c45c48" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>
<g fill="#1c2c30" font-family="Georgia, 'Iowan Old Style', Palatino, serif" font-size="28">
{''.join(city_svg)}
</g>
<text x="{ax:.1f}" y="{ay:.1f}" fill="#f6f1e8" opacity="0.78" font-family="Georgia, Palatino, serif" font-size="18" letter-spacing="6" text-anchor="middle">ATLANTIC</text>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"land {len(land)} highlight {len(hi)} lakes {len(water)}")

    index = Path(__file__).resolve().parents[1] / "index.html"
    if index.exists():
        html = index.read_text()
        start = html.find("<!-- MAP -->")
        end = html.find("<!-- /MAP -->")
        inline = svg.replace('<?xml version="1.0" encoding="UTF-8"?>\n', "").replace(
            "<svg ", '<svg class="map" ', 1
        )
        block = "<!-- MAP -->\n" + inline + "<!-- /MAP -->"
        if start != -1 and end != -1:
            html = html[:start] + block + html[end + len("<!-- /MAP -->") :]
            index.write_text(html)
            print("inlined map into index.html")


if __name__ == "__main__":
    main()
