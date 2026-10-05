"""Confere se o texto do spec cabe nos slides, em todos os estilos.

Monta o HTML de cada slide como o renderizador faria e mede no Chromium:
texto fora da tela, bloco de texto em cima de outro, texto cortado por
overflow e texto invadindo a faixa do rodapé (marcadores de progresso).
Não grava PNG nenhum: só devolve a lista de problemas.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import carousel_lab as L
from carousel_core import PATTERNS, Ctx

# Topo dos marcadores de progresso (ticks: bottom 52px, 8px de altura) com folga.
FOOTER_Y = 1350 - 52 - 8 - 6

PROBE = """
(footerY) => {
  const W = 1080, H = 1350, out = [];
  const slide = document.querySelector('.slide') || document.body;
  const textRect = (el) => {
    const r = document.createRange(); r.selectNodeContents(el);
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9, n = 0;
    for (const q of r.getClientRects()) {
      if (q.width < 1 || q.height < 1) continue; n++;
      x0 = Math.min(x0, q.left); y0 = Math.min(y0, q.top);
      x1 = Math.max(x1, q.right); y1 = Math.max(y1, q.bottom);
    }
    return n ? {x0, y0, x1, y1} : null;
  };
  const name = (el) => '"' + el.innerText.trim().slice(0, 40).replace(/\\s+/g, ' ') + '…"';
  const abs = [...slide.querySelectorAll('*')].filter(
    e => getComputedStyle(e).position === 'absolute' && e.innerText && e.innerText.trim());
  const blocks = abs.map(e => ({e, r: textRect(e)})).filter(b => b.r);
  for (const b of blocks) {
    const r = b.r;
    if (r.x0 < -1 || r.y0 < -1 || r.x1 > W + 1 || r.y1 > H + 1) out.push('texto fora da tela: ' + name(b.e));
    else if (r.y1 > footerY) out.push('texto invade o rodapé: ' + name(b.e));
  }
  for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) {
    const a = blocks[i], c = blocks[j];
    if (a.e.contains(c.e) || c.e.contains(a.e)) continue;
    const w = Math.min(a.r.x1, c.r.x1) - Math.max(a.r.x0, c.r.x0);
    const h = Math.min(a.r.y1, c.r.y1) - Math.max(a.r.y0, c.r.y0);
    if (w > 4 && h > 4) out.push('texto sobreposto: ' + name(a.e) + ' x ' + name(c.e));
  }
  for (const e of slide.querySelectorAll('*')) {
    if (!e.innerText || !e.innerText.trim()) continue;
    const cs = getComputedStyle(e);
    if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && e.scrollHeight > e.clientHeight + 2)
      out.push('texto cortado: ' + name(e));
  }
  return out;
}
"""


def fit_problems(spec: dict, styles: dict) -> list[str]:
    """Problemas de encaixe do spec em cada estilo, como 'estilo/slide: problema'."""
    from playwright.sync_api import sync_playwright

    c = Ctx(spec)
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=L.CHROME, args=["--allow-file-access-from-files", "--no-sandbox"]
        )
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for name, fn in styles.items():
            # Os padrões claro/escuro não mudam a geometria; o primeiro basta.
            css, slides = fn(c, PATTERNS[0])
            for i, body in enumerate(slides, 1):
                f = Path(tmp) / f"{name}-{i}.html"
                f.write_text(L.page(css, body), encoding="utf-8")
                pg.goto(f.as_uri())
                pg.evaluate("document.fonts.ready.then(() => true)")
                for issue in pg.evaluate(PROBE, FOOTER_Y):
                    problems.append(f"{name}/{i:02d}: {issue}")
        b.close()
    return problems
