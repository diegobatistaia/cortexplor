#!/usr/bin/env python3
"""Carrosséis de Instagram a partir de um spec JSON (social/specs/<slug>.json).

Todos os estilos leem o mesmo spec narrativo (capa + 4 slides de texto + fontes).
O spec é o contrato entre a redação (Routine / Claude) e o renderizador.

    python scripts/social/carousel.py <slug> [estilo ...]
    python scripts/social/carousel.py --all [estilo ...]
Saída: social/out/<slug>/<estilo>/01..06.png (1080x1350) e folha-<estilo>.png.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lab as L  # noqa: E402
from carousel_core import PATTERNS, ROOT, TOTAL, Ctx  # noqa: E402
from styles_a import STYLES_A  # noqa: E402

try:
    from styles_b import STYLES_B  # noqa: E402
except ImportError:  # estilos 5-10 ainda não existem
    STYLES_B = {}

SPECS = ROOT / "social" / "specs"
OUT = ROOT / "social" / "out"
STYLES = {**STYLES_A, **STYLES_B}


def sheet(folder: Path, dest: Path):
    ims = [Image.open(folder / f"{i:02d}.png").convert("RGB").resize((540, 675)) for i in range(1, TOTAL + 1)]
    w = Image.new("RGB", (540 * 3 + 40, 675 * 2 + 30), (60, 60, 60))
    for k, im in enumerate(ims):
        w.paste(im, (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    w.save(dest)


def build(slug, names=None, seed=11, spec=None):
    spec = spec or json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))
    c = Ctx(spec)
    rng = random.Random(f"{slug}-{seed}")
    names = names or list(STYLES)
    jobs = {}
    for n in names:
        pat = rng.choice(PATTERNS)
        jobs[f"../out/{slug}/{n}"] = STYLES[n](c, pat)
    L.render(jobs)
    sheets = []
    for n in names:
        dest = OUT / slug / f"folha-{n}.png"
        sheet(OUT / slug / n, dest)
        sheets.append(dest)
    return sheets


def main(argv):
    if argv and argv[0] == "--all":
        slugs = sorted(p.stem for p in SPECS.glob("*.json"))
        names = argv[1:] or None
    else:
        slugs, names = [argv[0]], argv[1:] or None
    for slug in slugs:
        for p in build(slug, names):
            print(p.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
