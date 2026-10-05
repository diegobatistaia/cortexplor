#!/usr/bin/env python3
"""Controles que complementam `redacao.py check` (spec, legenda e encaixe do texto).

    python scripts/social/check.py photo <slug>       foto da matéria: tamanho e escuridão; lista estilos elegíveis
    python scripts/social/check.py build <slug>       redacao.py check + foto + render dos estilos elegíveis
    python scripts/social/check.py golden             compara o render atual com as referências aprovadas
    python scripts/social/check.py golden --update    regrava as referências (só com aprovação do dono)

Saída com código != 0 quando algo reprova. Regras: social/INSTAGRAM.md, seção 7.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel  # noqa: E402
from carousel_core import ROOT  # noqa: E402
from rotation import STYLES, eligible_styles, photo_report  # noqa: E402

SPECS = ROOT / "social" / "specs"
GOLDEN = ROOT / "social" / "golden"
GOLDEN_SPEC = GOLDEN / "spec-referencia.json"  # cópia congelada: mudar o texto das matérias não afeta a comparação


def load(slug: str) -> dict:
    return json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))


def load(slug: str) -> dict:
    return json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))


def _diff(a: Path, b: Path) -> float:
    ia = Image.open(a).convert("L").resize((415, 345))
    ib = Image.open(b).convert("L").resize((415, 345))
    return ImageStat.Stat(ImageChops.difference(ia, ib)).mean[0]


def cmd_golden(update: bool) -> int:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    sheets = carousel.build("golden-ref", list(STYLES), spec=json.loads(GOLDEN_SPEC.read_text(encoding="utf-8")))
    fails = 0
    for p in sheets:
        ref = GOLDEN / (p.stem + ".jpg")
        if update:
            Image.open(p).convert("RGB").save(ref, quality=82)
            print("referência gravada:", ref.relative_to(ROOT))
            continue
        tmp = GOLDEN / "_tmp.png"
        Image.open(ref).convert("RGB").save(tmp)
        d = _diff(p, tmp)
        tmp.unlink()
        ok = d < 2.0
        fails += not ok
        print(f"{'ok   ' if ok else 'MUDOU'} {p.stem}  diferença {d:.2f}")
    return 1 if fails else 0


def cmd_photo(slug: str) -> int:
    spec = load(slug)
    warns, _ = photo_report(spec)
    for w in warns:
        print("AVISO:", w)
    print(f"{slug}: estilos elegíveis: {', '.join(eligible_styles(spec))}")
    return 0


def cmd_build(slug: str) -> int:
    import redacao  # noqa: E402

    err, warn = redacao.check_spec(redacao.load_spec(slug))
    for e in err:
        print("ERRO :", e)
    for w in warn:
        print("AVISO:", w)
    if err:
        return 1
    cmd_photo(slug)
    carousel.build(slug, eligible_styles(load(slug)))
    print("render ok:", slug)
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "photo":
        return cmd_photo(argv[1])
    if cmd == "build":
        return cmd_build(argv[1])
    if cmd == "golden":
        return cmd_golden("--update" in argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
