#!/usr/bin/env python3
"""Versão em vídeo do carrossel de apresentação (estilo Duotone), só para este post.

Os slides 1, 2, 4 e 6 trocam a capa estática pela mesma rede animada da página
de links da bio (sinais correndo pelas linhas e nós pulsando) e viram MP4 de
1080x1350 em loop. Os slides 3 e 5 continuam PNG. No slide 1 o título fica
centralizado e mais afastado do logo. Nada aqui altera o modelo Duotone
(styles_a.py): os ajustes são feitos no HTML gerado.

    python scripts/social/video_apresentacao.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
import carousel_lab as L  # noqa: E402
from carousel_core import ROOT, Ctx, crop_box  # noqa: E402
from styles_a import v_duotone  # noqa: E402

SLUG = "cortexplor-apresentacao"
OUT = ROOT / "social" / "out" / SLUG / "duotone-video"
FPS, SECS = 30, 6
SRC = (1600, 1200)  # tamanho da arte da capa
# recortes usados pelo Duotone: nome -> (proporção, tamanho, fx)
CROPS = {"cover": (1080 / 1350, (1080, 1350), 0.5), "band": (1080 / 420, (1080, 420), 0.5), "strip": (340 / 1350, (340, 1350), 0.72)}
ANIM = {1, 2, 4, 6}

# Mesma rede da capa (assets/img/cortexplor-apresentacao-capa.jpg), agora animada
EDGES = [
    "M-40 860 L240 400 L560 550 L840 230 L1200 470 L1480 170 L1680 340",
    "M240 400 L380 960 L720 860 L840 230",
    "M720 860 L1020 1020 L1200 470 L1380 860 L1680 760",
    "M560 550 L720 860", "M1480 170 L1380 860", "M-40 230 L240 400",
]
FLOWS = EDGES[:3] + [EDGES[4]]
NODES = [(240, 400, 14), (560, 550, 12), (840, 230, 18), (1200, 470, 16), (1480, 170, 12),
         (380, 960, 12), (720, 860, 14), (1020, 1020, 12), (1380, 860, 14)]
ICON = (ROOT / "assets" / "logo" / "cortexplor-icon-white.svg").as_uri()


def scene() -> str:
    edges = "".join(f"<path d='{d}'/>" for d in EDGES)
    flows = "".join(f"<path class='flow' pathLength='1000' d='{d}'/>" for d in FLOWS)
    nodes = "".join(f"<circle class='pulse' cx='{x}' cy='{y}' r='{r}'/>" for x, y, r in NODES)
    return f"""<div class='net' style='position:absolute;left:0;top:0;width:1600px;height:1200px;transform-origin:0 0;background:linear-gradient(150deg,#6B7A8F 0%,#4A5568 45%,#2C3442 100%)'>
<svg viewBox='0 0 1600 1200' width='1600' height='1200' style='position:absolute;inset:0' fill='none'>
<g stroke='rgba(237,236,232,.35)' stroke-width='3'>{edges}</g>
<g stroke='#EDECE8' stroke-width='6' stroke-linecap='round' style='filter:drop-shadow(0 0 8px rgba(237,236,232,.9))'>{flows}</g>
<g fill='#EDECE8'>{nodes}</g></svg>
<div style='position:absolute;left:50%;top:36%;width:380px;height:380px;transform:translate(-50%,-50%);border-radius:50%;background:#14130F;display:grid;place-items:center;box-shadow:0 0 0 14px rgba(237,236,232,.18),0 40px 120px rgba(0,0,0,.45)'>
<img src='{ICON}' style='width:230px'></div></div>"""


def levels(c, name):
    """Reproduz o autocontraste que photo_crop aplica, como filtro linear por canal."""
    aspect, size, fx = CROPS[name]
    im = Image.open(c.photo).convert("RGB")
    im = im.crop(crop_box(im.size, aspect, fx, 0.5)).resize(size, Image.LANCZOS)
    a = np.asarray(im, float).reshape(-1, 3)
    b = np.asarray(ImageOps.autocontrast(im, cutoff=0.5), float).reshape(-1, 3)
    return [tuple(np.polyfit(a[::7, k], b[::7, k], 1)) for k in range(3)]


def filters(c) -> str:
    out = ""
    for name in CROPS:
        f = "".join(f"<feFunc{ch} type='linear' slope='{m:.4f}' intercept='{q / 255:.4f}'/>" for ch, (m, q) in zip("RGB", levels(c, name)))
        out += f"<filter id='ac-{name}' color-interpolation-filters='sRGB'><feComponentTransfer>{f}</feComponentTransfer></filter>"
    return f"<svg width='0' height='0' style='position:absolute'>{out}</svg>"


# Liga cada fundo com a capa estática à rede animada, no mesmo enquadramento do recorte
JS = """
(crops) => {
  const tpl = document.getElementById('scene');
  for (const el of document.querySelectorAll('.slide *')) {
    const bg = el.style.backgroundImage || '';
    const hit = Object.keys(crops).find(n => bg.includes('_' + n + '.png'));
    if (!hit) continue;
    const [cx, cy, cw, ch, iw, ih] = crops[hit];
    const w = el.offsetWidth, h = el.offsetHeight;
    const s = Math.max(w / iw, h / ih), k = iw / cw * s;
    const ox = (w - iw * s) / 2 - cx * k, oy = (h - ih * s) / 2 - cy * k;
    el.style.backgroundImage = 'none';
    el.style.overflow = 'hidden';
    const n = tpl.content.firstElementChild.cloneNode(true);
    n.style.transform = `translate(${ox}px,${oy}px) scale(${k})`;
    n.style.filter = `url(#ac-${hit})`;
    el.appendChild(n);
  }
  const flows = [...document.querySelectorAll('.flow')], pulses = [...document.querySelectorAll('.pulse')];
  // t em [0,1): tudo fecha o ciclo em t=1, então o vídeo repete sem emenda
  window.setT = (t) => {
    flows.forEach((p, i) => {
      p.setAttribute('stroke-dasharray', '45 455');
      p.setAttribute('stroke-dashoffset', String(-500 * t - 137 * (i % 4)));
    });
    pulses.forEach((c, i) => {
      const ph = 2 * Math.PI * (2 * t + (i % 9) / 9 * 0.999 + (i % 3) * 0.17);
      const v = (1 - Math.cos(ph)) / 2;
      c.style.transformBox = 'fill-box';
      c.style.transformOrigin = 'center';
      c.style.transform = `scale(${1 + 0.4 * v})`;
      c.style.opacity = String(0.45 + 0.55 * v);
    });
  };
  window.setT(0);
}
"""


def slides(c):
    css, s = v_duotone(c)
    # Slide 1: título centralizado e mais longe do logo (só neste carrossel)
    d = c.d
    old_h1 = f"<h1 class='abs' style='left:64px;top:730px;width:952px;font-size:84px;line-height:1.02;color:#fff'>{d['headline']}</h1>"
    old_dek = f"<div class='abs' style='left:64px;top:1090px;width:940px;font-size:31px;line-height:1.36;color:#E4E8EE'>{d['dek']}</div>"
    assert old_h1 in s[0] and old_dek in s[0], "slide 1 do Duotone mudou; revise os ajustes"
    s[0] = s[0].replace(old_h1, f"<h1 class='abs' style='left:64px;top:870px;width:952px;font-size:84px;line-height:1.02;color:#fff;text-align:center'>{d['headline']}</h1>")
    s[0] = s[0].replace(old_dek, f"<div class='abs' style='left:140px;top:990px;width:800px;font-size:31px;line-height:1.36;color:#E4E8EE;text-align:center'>{d['dek']}</div>")
    return css, s


def main():
    from playwright.sync_api import sync_playwright

    spec = json.loads((ROOT / "social" / "specs" / f"{SLUG}.json").read_text(encoding="utf-8"))
    c = Ctx(spec)
    css, s = slides(c)
    crops = {}
    for n, (aspect, size, fx) in CROPS.items():
        x0, y0, x1, y1 = crop_box(SRC, aspect, fx, 0.5)
        crops[n] = [x0, y0, x1 - x0, y1 - y0, *size]
    extra = f"{filters(c)}<template id='scene'>{scene()}</template>"

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.iterdir():
        old.unlink()
    L.HTML.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=L.CHROME, args=["--allow-file-access-from-files", "--force-color-profile=srgb", "--no-sandbox"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for i, body in enumerate(s, 1):
            f = L.HTML / f"{SLUG}-video-{i:02d}.html"
            f.write_text(L.page(css, extra + body), encoding="utf-8")
            pg.goto(f.as_uri())
            pg.evaluate("document.fonts.ready.then(() => true)")
            if i in ANIM:
                pg.evaluate(JS, crops)
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / f"{i:02d}.png"))  # quadro parado (capa do vídeo ou slide fixo)
            if i not in ANIM:
                continue
            fr = tmp / f"s{i}"
            fr.mkdir()
            for k in range(FPS * SECS):
                pg.evaluate(f"setT({k / (FPS * SECS)})")
                pg.screenshot(path=str(fr / f"{k:04d}.png"))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fr / "%04d.png"),
                            "-c:v", "libx264", "-profile:v", "high", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(OUT / f"{i:02d}.mp4")], check=True)
            print(f"slide {i}: {OUT / f'{i:02d}.mp4'}")
        b.close()
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
