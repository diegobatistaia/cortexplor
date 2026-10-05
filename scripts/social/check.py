#!/usr/bin/env python3
"""Controle de qualidade dos carrosséis. Nada vai para aprovação sem passar aqui.

    python scripts/social/check.py spec <slug>        valida o spec (e a legenda, se existir)
    python scripts/social/check.py build <slug>       valida + renderiza os estilos elegíveis + mede layout
    python scripts/social/check.py golden             compara o render atual com as referências aprovadas
    python scripts/social/check.py golden --update    regrava as referências (só com aprovação do dono)

Saída com código != 0 quando algo reprova. Regras e limites: social/INSTAGRAM.md, seção 7.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel  # noqa: E402
from carousel_core import ROOT  # noqa: E402
from rotation import STYLES  # noqa: E402

SPECS = ROOT / "social" / "specs"
GOLDEN = ROOT / "social" / "golden"
GOLDEN_SLUG = "openai-lanca-dots-agentes-permanentes-chatgpt"

# ----------------------------------------------------------------------------
# Limites de texto (calibrados nas matérias aprovadas, com folga pequena)
# ----------------------------------------------------------------------------
W = lambda s: len(s.split())  # noqa: E731
LIMITS = {
    "headline": ("max_chars", 70), "dek": ("max_chars", 175), "kicker": ("max_chars", 32),
}
PARA_MAX_WORDS = 60      # cada parágrafo de s2 e s4
TITLE_MAX_CHARS = 70     # título de cada slide
S3_BODY_MAX_WORDS = 36
POINT_MAX_WORDS = 28
POINT_H_MAX_CHARS = 26
ITEM_MAX_WORDS = 30
ITEM_H_MAX_CHARS = 10
STAT_BIG_MAX_CHARS = 14
STAT_CAP_MAX_CHARS = 48
CAPTION_BODY = (600, 800)
CAPTION_HOOK_MAX = 125
HASHTAGS_MAX = 4
ALT_MAX = 100
PHOTO_MIN_W, PHOTO_MIN_H = 800, 500
DARK_PHOTO = 45          # luminância média (0-255) abaixo da qual a capa em meia-tinta fica ilegível


def validate_spec(spec: dict) -> list[str]:
    e: list[str] = []

    def need(cond, msg):
        if not cond:
            e.append(msg)

    for k, (_, lim) in LIMITS.items():
        need(len(spec.get(k, "")) <= lim and spec.get(k), f"{k}: vazio ou acima de {lim} caracteres")
    need(spec.get("headline_hl", "") in spec.get("headline", "") or not spec.get("headline_hl"),
         "headline_hl precisa ser um trecho exato da manchete")
    need(2 <= len(spec.get("sources", [])) <= 5, "sources: entre 2 e 5 fontes (regra das duas fontes independentes)")
    img = spec.get("image", {})
    need((ROOT / img.get("path", "x")).exists(), f"image.path não existe: {img.get('path')}")
    need(bool(img.get("credit")), "image.credit ausente (crédito da foto)")

    for k in ("s2", "s3", "s4", "s5"):
        s = spec.get(k, {})
        need(bool(s.get("label")) and bool(s.get("title")), f"{k}: label e title obrigatórios")
        need(len(s.get("title", "")) <= TITLE_MAX_CHARS, f"{k}.title acima de {TITLE_MAX_CHARS} caracteres")
    for k in ("s2", "s4"):
        body = spec.get(k, {}).get("body", [])
        need(len(body) == 2, f"{k}.body: exatamente 2 parágrafos")
        for i, p in enumerate(body, 1):
            need(W(p) <= PARA_MAX_WORDS, f"{k}.body[{i}]: {W(p)} palavras (máx. {PARA_MAX_WORDS})")
    s3 = spec.get("s3", {})
    need(W(s3.get("body", "")) <= S3_BODY_MAX_WORDS, f"s3.body acima de {S3_BODY_MAX_WORDS} palavras")
    pts = s3.get("points", [])
    need(len(pts) == 3, "s3.points: exatamente 3 pontos")
    for i, p in enumerate(pts, 1):
        need(W(p.get("t", "")) <= POINT_MAX_WORDS, f"s3.points[{i}].t acima de {POINT_MAX_WORDS} palavras")
        need(len(p.get("h", "")) <= POINT_H_MAX_CHARS, f"s3.points[{i}].h acima de {POINT_H_MAX_CHARS} caracteres")
    st = spec.get("s4", {}).get("stat", {})
    need(0 < len(st.get("big", "")) <= STAT_BIG_MAX_CHARS, f"s4.stat.big vazio ou acima de {STAT_BIG_MAX_CHARS} caracteres")
    need(0 < len(st.get("cap", "")) <= STAT_CAP_MAX_CHARS, f"s4.stat.cap vazio ou acima de {STAT_CAP_MAX_CHARS} caracteres")
    items = spec.get("s5", {}).get("items", [])
    need(len(items) == 3, "s5.items: exatamente 3 itens")
    for i, it in enumerate(items, 1):
        need(W(it.get("t", "")) <= ITEM_MAX_WORDS, f"s5.items[{i}].t acima de {ITEM_MAX_WORDS} palavras")
        need(len(it.get("h", "")) <= ITEM_H_MAX_CHARS, f"s5.items[{i}].h acima de {ITEM_H_MAX_CHARS} caracteres")

    blob = json.dumps(spec, ensure_ascii=False)
    need(not re.search(r"https?://|www\.", blob), "spec contém URL")
    if "caption" in spec:
        e += validate_caption(spec)
    return e


def validate_caption(spec: dict) -> list[str]:
    e: list[str] = []
    c = spec.get("caption", {})
    hook, body = c.get("hook", ""), c.get("body", [])
    text = " ".join(body)
    full = " ".join([hook, text, c.get("cta", ""), " ".join(c.get("hashtags", []))])
    if not hook or len(hook) > CAPTION_HOOK_MAX:
        e.append(f"caption.hook vazio ou acima de {CAPTION_HOOK_MAX} caracteres")
    n = len(hook) + len(text) + len(c.get("cta", ""))
    if not CAPTION_BODY[0] <= n <= CAPTION_BODY[1]:
        e.append(f"caption: {n} caracteres (hook+corpo+chamada deve ter {CAPTION_BODY[0]}-{CAPTION_BODY[1]})")
    tags = c.get("hashtags", [])
    if not 1 <= len(tags) <= HASHTAGS_MAX or not all(t.startswith("#") and " " not in t for t in tags):
        e.append(f"caption.hashtags: de 1 a {HASHTAGS_MAX}, cada uma começando com # e sem espaço")
    if "#cortexplor" not in [t.lower() for t in tags]:
        e.append("caption.hashtags: falta a hashtag da marca #cortexplor")
    if c.get("cta_variant") not in ("A", "B"):
        e.append("caption.cta_variant deve ser 'A' ou 'B'")
    if re.search(r"https?://|www\.|\.com|\.br\b", full, re.I):
        e.append("caption: não pode ter link nem domínio (o aviso é 'link na bio')")
    alt = spec.get("alt", [])
    if len(alt) != 6 or any(not a or len(a) > ALT_MAX for a in alt):
        e.append(f"alt: 6 textos alternativos, cada um com até {ALT_MAX} caracteres")
    return e


def photo_report(spec: dict) -> tuple[list[str], list[str]]:
    """Devolve (avisos, estilos excluídos por causa da foto)."""
    p = ROOT / spec["image"]["path"]
    im = Image.open(p)
    warns, excluded = [], []
    if im.width < PHOTO_MIN_W or im.height < PHOTO_MIN_H:
        warns.append(f"foto pequena ({im.width}x{im.height}); mínimo {PHOTO_MIN_W}x{PHOTO_MIN_H}")
    lum = ImageStat.Stat(im.convert("L")).mean[0]
    if lum < DARK_PHOTO:
        excluded.append("meiatinta")
        warns.append(f"foto muito escura (luminância {lum:.0f}); estilo meiatinta fora do rodízio desta matéria")
    return warns, excluded


def eligible_styles(spec: dict) -> list[str]:
    return [s for s in STYLES if s not in photo_report(spec)[1]]


def load(slug: str) -> dict:
    return json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))


def cmd_spec(slug: str) -> int:
    spec = load(slug)
    errs = validate_spec(spec)
    warns, excl = photo_report(spec)
    for w in warns:
        print("AVISO:", w)
    for er in errs:
        print("ERRO :", er)
    print(f"{slug}: {'REPROVADO' if errs else 'spec ok'} | estilos elegíveis: {', '.join(eligible_styles(spec))}")
    return 1 if errs else 0


def cmd_build(slug: str) -> int:
    if cmd_spec(slug):
        return 1
    styles = eligible_styles(load(slug))
    carousel.build(slug, styles)
    bad = carousel.build.issues
    for style, n, kind, what in bad:
        print(f"LAYOUT {style} slide {n}: {kind} — {what}")
    print("layout ok em", len(styles), "estilos" if not bad else f"— {len(bad)} problema(s)")
    return 1 if bad else 0


def _diff(a: Path, b: Path) -> float:
    ia = Image.open(a).convert("L").resize((415, 345))
    ib = Image.open(b).convert("L").resize((415, 345))
    return ImageStat.Stat(ImageChops.difference(ia, ib)).mean[0]


def cmd_golden(update: bool) -> int:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    sheets = carousel.build(GOLDEN_SLUG, list(STYLES))
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


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "spec":
        return cmd_spec(argv[1])
    if cmd == "build":
        return cmd_build(argv[1])
    if cmd == "golden":
        return cmd_golden("--update" in argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
