"""Base compartilhada dos estilos de carrossel: contexto do spec e helpers."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageOps

import carousel_lab as L
from carousel_lab import ARROW, CHECK, CROSS, LOGO, TOTAL, ic, pill, uri  # noqa: F401

ROOT = L.ROOT
INK = "#14130F"
WM_B = uri(LOGO / "cortexplor-wordmark-black.svg")
WM_W = uri(LOGO / "cortexplor-wordmark-white.svg")
ICON_B = uri(LOGO / "cortexplor-icon-black.svg")
ICON_W = uri(LOGO / "cortexplor-icon-white.svg")

UI = {
    "pt": {
        "sources": "Fontes",
        "sources_long": "Fontes consultadas",
        "full": "Matéria completa e links das fontes em",
        "confirm": "{n} fontes independentes confirmam os fatos centrais",
        "annex": "Anexo A",
        "photo": "Foto",
        "numbers": {2: "Duas", 3: "Três", 4: "Quatro", 5: "Cinco"},
        "archived": "Arquivado<br>Cortexplor",
        "dossier": "Dossiê nº",
        "read": "Leia a matéria completa",
        # Uma fonte só passa no gate quando é o anúncio oficial da própria empresa.
        "confirm_one": "Fonte: anúncio oficial da própria empresa",
    },
    "en": {
        "sources": "Sources",
        "sources_long": "Sources checked",
        "full": "Full story and source links at",
        "confirm": "{n} independent sources confirm the core facts",
        "annex": "Annex A",
        "photo": "Photo",
        "numbers": {2: "Two", 3: "Three", 4: "Four", 5: "Five"},
        "archived": "Archived<br>Cortexplor",
        "dossier": "File no.",
        "read": "Read the full story",
        "confirm_one": "Source: the company's own official announcement",
    },
}

# Padrões claro/escuro (True = escuro): irregulares, nunca 3 iguais seguidos.
PATTERNS = [
    [False, True, True, False, False, True],
    [True, False, False, True, False, True],
    [False, False, True, False, True, True],
    [True, True, False, True, False, False],
    [False, True, False, False, True, False],
    [True, False, True, True, False, False],
]


def short(name):
    return re.sub(r"\s+(Technology|AI)$", "", name)


def hl(text, sub, cls="hl"):
    if sub and sub in text:
        return text.replace(sub, f"<span class='{cls}'>{sub}</span>", 1)
    return text


def ticks(n, on, off, h=8, gap=10, bottom=52, right=64, left=64):
    segs = "".join(
        f"<i style='flex:1;height:{h}px;background:{on if k < n else off}'></i>" for k in range(TOTAL)
    )
    return f"<div class='abs' style='left:{left}px;right:{right}px;bottom:{bottom}px;display:flex;gap:{gap}px'>{segs}</div>"


def crop_box(size, aspect, fx=0.5, fy=0.5):
    """Maior recorte com a proporção `aspect` (largura/altura), centrado em (fx, fy)."""
    w, h = size
    cw, ch = (w, w / aspect) if w / h < aspect else (h * aspect, h)
    x = min(max(fx * w - cw / 2, 0), w - cw)
    y = min(max(fy * h - ch / 2, 0), h - ch)
    return int(x), int(y), int(x + cw), int(y + ch)


def photo_crop(c, aspect, size, name, fx=0.5, fy=0.5, blur=0, bright=1.0):
    """Recorte da foto na cor original (contraste automático leve)."""
    from PIL import ImageEnhance, ImageFilter

    L.HT.mkdir(parents=True, exist_ok=True)
    out = L.HT / f"{c.slug}_{name}.png"
    im = Image.open(c.photo).convert("RGB")
    im = im.crop(crop_box(im.size, aspect, fx, fy)).resize(size, Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
    im.save(out)
    return uri(out)


def paras(lst, style=""):
    return "".join(f"<p style='{style}'>{p}</p>" for p in lst)


class Ctx:
    """Tudo que os estilos precisam, derivado do spec."""

    def __init__(self, spec):
        self.d = spec
        # "ui" no spec troca textos fixos só deste carrossel (ex.: post de apresentação, sem matéria)
        self.u = {**UI[spec.get("lang", "pt")], **spec.get("ui", {})}
        img = spec["image"]
        self.photo = ROOT / img["path"]
        self.ph = uri(self.photo)
        self.pos = img.get("pos", "50% 50%")
        self.credit = f"{self.u['photo']}: {img['credit']}"
        self.src = spec["sources"]
        self.n = len(self.src)
        self.slug = spec["slug"]
        L.PHOTO = self.photo  # usado pela rotina de meia-tinta

    def fs(self, big, small):
        return big if self.n <= 2 else small

    def confirm(self):
        if self.n == 1:
            return self.u["confirm_one"]
        return self.u["confirm"].format(n=self.u["numbers"].get(self.n, str(self.n)))
