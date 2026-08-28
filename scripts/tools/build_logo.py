#!/usr/bin/env python3
"""Build the Cortexplor logo asset set from the Claude Design standalone export.

The export is a self-contained HTML bundle: the icon lives in it as inline SVG,
but the wordmark is plain HTML text (Space Grotesk) coloured with a CSS gradient.
So the icon is re-serialised from the bundle's own geometry, and the wordmark is
shaped with HarfBuzz and converted to outlines using the font embedded in the
same bundle - the final files depend on no font at all.

Weights: the bundle asks for font-weight 700 on "explor", but only 300/400/500/600
faces are declared, so the browser rendered it at 600. Measured against the live
render (span widths 61.719px / 89.547px at 30px), 400 + 600 reproduce the approved
artwork exactly; 700 does not. We ship what was approved.

Run: python scripts/tools/build_logo.py
"""
import base64
import io
import json
import math
import re
from pathlib import Path

import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets" / "logo" / "source" / "cortexplor-logo-export.html"
OUT = ROOT / "assets" / "logo"

SG_UUID = "11fe16c8-a598-475a-90b9-3ae93fb45368"  # Space Grotesk, latin subset (variable)
WORDMARK = [("Cort", 400), ("explor", 600)]
LETTER_SPACING_EM = -0.01

# Role -> hex, per variant. Roles come from the colour panel: the angular C is
# "primary", the chevron X is "accent".
PALETTES = {
    "color": {"primary": "#3A4556", "accent": "#6B7A8F"},
    "black": {"primary": "#14130F", "accent": "#14130F"},
    "white": {"primary": "#FFFEFB", "accent": "#FFFEFB"},
    "light": {"primary": "#8A94A6", "accent": "#B7C0CC"},  # the export's dark-tile treatment
}
WORDMARK_INK = {
    "color": {"cort": "#14130F", "explor": ("#3A4556", "#6B7A8F")},  # tuple = horizontal gradient
    "black": {"cort": "#14130F", "explor": "#14130F"},
    "white": {"cort": "#FFFEFB", "explor": "#FFFEFB"},
    "light": {"cort": "#FFFEFB", "explor": ("#8A94A6", "#B7C0CC")},
}
APP_TILE = "#1A1533"  # the app-icon tile used in the export's colour panel


# --------------------------------------------------------------------------- bundle

def load_bundle():
    text = SRC.read_text(encoding="utf-8")
    manifest = json.loads(
        re.search(r'<script type="__bundler/manifest">(.*?)</script>', text, re.S).group(1))
    template = json.loads(
        re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1))
    return manifest, template


def parse_icon(svg, role_of):
    """Turn one inline <svg> into {strokes, dots, width} carrying roles, not colours."""
    group = re.search(r"<g([^>]*)>(.*?)</g>", svg, re.S)
    gattrs, body = group.group(1), group.group(2)
    gstroke = re.search(r'stroke="([^"]+)"', gattrs)
    width = float(re.search(r'stroke-width="([\d.]+)"', gattrs).group(1))

    strokes = []
    for m in re.finditer(r'<path d="([^"]+)"([^>]*)>', body):
        pts = [tuple(map(float, p.split()))
               for p in re.findall(r"[ML]\s*([\d.-]+\s+[\d.-]+)", m.group(1))]
        colour = re.search(r'stroke="([^"]+)"', m.group(2))
        strokes.append({"points": pts, "role": role_of((colour or gstroke).group(1))})

    dots = []
    for m in re.finditer(r'<circle cx="([\d.-]+)" cy="([\d.-]+)" r="([\d.]+)" fill="([^"]+)"', svg):
        dots.append({
            "c": (float(m.group(1)), float(m.group(2))),
            "r": float(m.group(3)),
            "role": role_of(m.group(4)),
        })

    return {"strokes": strokes, "dots": dots, "width": width}


def read_geometry(template):
    """Panel 7a carries both treatments: the detailed mark and the small-size mark."""
    panel = template[template.find('<div id="7a"'):template.find('<div id="7b"')]
    svgs = re.findall(r"<svg .*?</svg>", panel, re.S)
    detail_roles = {"#3A4556": "primary", "#6B7A8F": "accent"}
    small_roles = {"#8A94A6": "primary", "#B7C0CC": "accent"}
    return {
        "detail": parse_icon(svgs[0], lambda ink: detail_roles[ink]),
        "small": parse_icon(svgs[2], lambda ink: small_roles[ink]),
    }


def ink_bounds(geom):
    half = geom["width"] / 2
    xs, ys = [], []
    for s in geom["strokes"]:
        for x, y in s["points"]:
            xs += [x - half, x + half]
            ys += [y - half, y + half]
    for d in geom["dots"]:
        xs += [d["c"][0] - d["r"], d["c"][0] + d["r"]]
        ys += [d["c"][1] - d["r"], d["c"][1] + d["r"]]
    return min(xs), min(ys), max(xs), max(ys)


# --------------------------------------------------------------------------- wordmark

def instance(raw_woff2, weight):
    font = TTFont(io.BytesIO(raw_woff2))
    font.flavor = None
    instantiateVariableFont(font, {"wght": weight}, inplace=True)
    buf = io.BytesIO()
    font.save(buf)
    return font, buf.getvalue()


def shape(ttf_bytes, text):
    face = hb.Face(ttf_bytes)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return ([(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
             for i, p in zip(buf.glyph_infos, buf.glyph_positions)], face.upem)


def wordmark_paths(raw_woff2, size, baseline, origin=0.0):
    """Outline both spans at `size` units with the baseline at y=`baseline`."""
    spans, pen_x = [], origin
    for text, weight in WORDMARK:
        font, ttf = instance(raw_woff2, weight)
        glyphs, upem = shape(ttf, text)
        order, glyphset = font.getGlyphOrder(), font.getGlyphSet()
        k = size / upem
        start, pieces = pen_x, []
        for gid, adv, dx, dy in glyphs:
            spen = SVGPathPen(glyphset, ntos=lambda v: f"{v:.2f}")
            tpen = TransformPen(spen, Transform(k, 0, 0, -k, pen_x + dx * k, baseline - dy * k))
            glyphset[order[gid]].draw(tpen)
            pieces.append(spen.getCommands())
            pen_x += adv * k + LETTER_SPACING_EM * size
        spans.append({"span": text, "d": " ".join(p for p in pieces if p), "x0": start, "x1": pen_x})
        font.close()
    return spans, pen_x - origin


def wordmark_vbounds(raw_woff2, size, baseline):
    """Vertical ink extent of the wordmark, taken from the outlines themselves."""
    lo, hi = math.inf, -math.inf
    for text, weight in WORDMARK:
        font, ttf = instance(raw_woff2, weight)
        glyphs, upem = shape(ttf, text)
        order, glyphset = font.getGlyphOrder(), font.getGlyphSet()
        k = size / upem
        for gid, *_ in glyphs:
            bp = BoundsPen(glyphset)
            glyphset[order[gid]].draw(bp)
            if bp.bounds:
                lo = min(lo, baseline - bp.bounds[3] * k)
                hi = max(hi, baseline - bp.bounds[1] * k)
        font.close()
    return lo, hi


# --------------------------------------------------------------------------- svg

def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def icon_markup(geom, palette, classes=False):
    p = PALETTES[palette]
    cls = {"primary": " class=\"p\"", "accent": " class=\"a\""} if classes else {"primary": "", "accent": ""}
    by_role = {}
    for s in geom["strokes"]:
        by_role.setdefault(s["role"], []).append(s)
    parts = []
    for role, items in by_role.items():
        paths = "".join(
            "\n      <path d=\"M{}\"/>".format(" L".join(f"{fmt(x)} {fmt(y)}" for x, y in s["points"]))
            for s in items)
        parts.append(
            f'    <g fill="none" stroke="{p[role]}"{cls[role]} stroke-width="{fmt(geom["width"])}"'
            f' stroke-linecap="round" stroke-linejoin="round">{paths}\n    </g>')
    for d in geom["dots"]:
        parts.append(f'    <circle cx="{fmt(d["c"][0])}" cy="{fmt(d["c"][1])}" r="{fmt(d["r"])}"'
                     f' fill="{p[d["role"]]}"{cls[d["role"]]}/>')
    return "\n".join(parts)


def svg_doc(view, body, title):
    x0, y0, w, h = view
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(x0)} {fmt(y0)} {fmt(w)} {fmt(h)}"'
            f' role="img" aria-label="{title}">\n  <title>{title}</title>\n{body}\n</svg>\n')


def wordmark_body(spans, variant, prefix=""):
    ink = WORDMARK_INK[variant]
    cort, explor = spans
    out, fill = [], ink["explor"]
    if isinstance(fill, tuple):
        gid = f"{prefix}wordmark-gradient"
        out.append(
            f'    <defs>\n      <linearGradient id="{gid}" x1="{fmt(explor["x0"])}" y1="0"'
            f' x2="{fmt(explor["x1"])}" y2="0" gradientUnits="userSpaceOnUse">\n'
            f'        <stop offset="0" stop-color="{fill[0]}"/>\n'
            f'        <stop offset="1" stop-color="{fill[1]}"/>\n'
            f"      </linearGradient>\n    </defs>")
        fill = f"url(#{gid})"
    out.append(f'    <path fill="{ink["cort"]}" d="{cort["d"]}"/>')
    out.append(f'    <path fill="{fill}" d="{explor["d"]}"/>')
    return "\n".join(out)


# --------------------------------------------------------------------------- raster

def rasterize(geom, palette, size, pad=0.08, background=None, supersample=6):
    """Render the mark to a square RGBA image. Round caps and joins are drawn as a
    thick polyline plus a disc at every vertex, which is what the SVG renderer does."""
    p = PALETTES[palette]
    x0, y0, x1, y1 = ink_bounds(geom)
    span = max(x1 - x0, y1 - y0)
    canvas = size * supersample
    k = canvas * (1 - 2 * pad) / span
    ox = (canvas - (x1 - x0) * k) / 2 - x0 * k
    oy = (canvas - (y1 - y0) * k) / 2 - y0 * k

    def T(x, y):
        return (x * k + ox, y * k + oy)

    img = Image.new("RGBA", (canvas, canvas), background or (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w = geom["width"] * k
    for s in geom["strokes"]:
        pts = [T(x, y) for x, y in s["points"]]
        draw.line(pts, fill=p[s["role"]], width=int(round(w)))
        for cx, cy in pts:
            draw.ellipse([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], fill=p[s["role"]])
    for d in geom["dots"]:
        cx, cy = T(*d["c"])
        r = d["r"] * k
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=p[d["role"]])
    return img.resize((size, size), Image.LANCZOS)


# --------------------------------------------------------------------------- main

def main():
    manifest, template = load_bundle()
    geo = read_geometry(template)
    raw = base64.b64decode(manifest[SG_UUID]["data"])
    OUT.mkdir(parents=True, exist_ok=True)
    made = []

    def write(name, text):
        (OUT / name).write_text(text, encoding="utf-8")
        made.append(name)

    # --- icon. Tight viewBox so the outer nodes are not clipped the way they are
    # in the export, whose own viewport cuts ~1 unit off the leftmost node.
    ix0, iy0, ix1, iy1 = ink_bounds(geo["detail"])
    pad = 2
    icon_view = (ix0 - pad, iy0 - pad, (ix1 - ix0) + 2 * pad, (iy1 - iy0) + 2 * pad)
    for variant in ("color", "black", "white"):
        write(f"cortexplor-icon-{variant}.svg",
              svg_doc(icon_view, icon_markup(geo["detail"], variant), "Cortexplor"))

    # --- wordmark on its own, drawn on the same 100-unit grid as the icon.
    spans, adv = wordmark_paths(raw, 100.0, 100.0)
    top, bottom = wordmark_vbounds(raw, 100.0, 100.0)
    wm_view = (-2, top - 4, adv + 4, (bottom - top) + 8)
    for variant in ("color", "black", "white"):
        write(f"cortexplor-wordmark-{variant}.svg",
              svg_doc(wm_view, wordmark_body(spans, variant, f"{variant}-"), "Cortexplor"))

    # --- lockup: icon ink 1.5x the wordmark cap height, centred on the cap band.
    cap = (iy1 - iy0) / 1.5
    wm_size = cap / 0.7
    wm_baseline = (iy0 + iy1) / 2 + cap / 2
    wm_x = ix1 + cap * 0.45
    lspans, ladv = wordmark_paths(raw, wm_size, wm_baseline, origin=wm_x)
    ltop, lbottom = wordmark_vbounds(raw, wm_size, wm_baseline)
    lx0, ly0 = ix0 - pad, min(iy0, ltop) - pad
    lx1, ly1 = wm_x + ladv + pad, max(iy1, lbottom) + pad
    lock_view = (lx0, ly0, lx1 - lx0, ly1 - ly0)
    for variant in ("color", "black", "white"):
        body = icon_markup(geo["detail"], variant) + "\n" + wordmark_body(lspans, variant, f"{variant}-")
        write(f"cortexplor-logo-{variant}.svg", svg_doc(lock_view, body, "Cortexplor"))

    # --- favicon.svg uses the small-size treatment and flips palette in dark UI.
    sx0, sy0, sx1, sy1 = ink_bounds(geo["small"])
    sview = (sx0 - 3, sy0 - 3, (sx1 - sx0) + 6, (sy1 - sy0) + 6)
    dark = PALETTES["light"]
    style = ("    <style>@media (prefers-color-scheme: dark){"
             f".p{{stroke:{dark['primary']};fill:{dark['primary']}}}"
             f".a{{stroke:{dark['accent']};fill:{dark['accent']}}}}}</style>")
    write("favicon.svg",
          svg_doc(sview, style + "\n" + icon_markup(geo["small"], "color", classes=True), "Cortexplor"))

    # --- rasters. The .ico uses the small-size treatment (thicker strokes, fewer
    # nodes) because the detailed mark turns to mush at 16px.
    frames = [rasterize(geo["small"], "color", s, pad=0.04) for s in (16, 32, 48)]
    frames[0].save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)],
                   append_images=frames[1:])
    made.append("favicon.ico")
    for s in (192, 512):
        rasterize(geo["detail"], "light", s, pad=0.18, background=APP_TILE).save(OUT / f"icon-{s}.png")
        made.append(f"icon-{s}.png")
    rasterize(geo["detail"], "light", 180, pad=0.18, background=APP_TILE).save(OUT / "apple-touch-icon.png")
    made.append("apple-touch-icon.png")

    for name in made:
        print(f"  {name:34} {(OUT / name).stat().st_size / 1024:7.1f} KB")
    print(f"{len(made)} files -> assets/logo/")


if __name__ == "__main__":
    main()
