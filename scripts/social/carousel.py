#!/usr/bin/env python3
"""Carrosséis de Instagram a partir de um spec JSON (social/specs/<slug>.json).

Os 4 estilos aprovados (edicao, terminal, dossie, duotone) leem o mesmo spec.
Claro/escuro alterna de forma irregular (PATTERNS). O spec é o contrato entre a
redação (Routine / Claude) e o renderizador: todo o texto vem dele.

    python scripts/social/carousel.py <slug> [edicao terminal dossie duotone]
    python scripts/social/carousel.py --all
Saída: social/out/<slug>/<estilo>/01..06.png (1080x1350) e folhas de contato.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lab as L  # noqa: E402
from carousel_lab import ARROW, CHECK, CROSS, LOGO, TOTAL, ic, pill, uri  # noqa: E402

ROOT = L.ROOT
SPECS = ROOT / "social" / "specs"
OUT = ROOT / "social" / "out"
INK = "#14130F"
WM_B = uri(LOGO / "cortexplor-wordmark-black.svg")
WM_W = uri(LOGO / "cortexplor-wordmark-white.svg")

UI = {
    "pt": {
        "sources": "Fontes",
        "sources_long": "Fontes consultadas",
        "full": "Matéria completa e links das fontes em",
        "confirm": "{n} fontes independentes confirmam os fatos centrais",
        "annex": "Anexo A",
        "photo": "Foto",
        "timeline": "Linha do tempo",
        "context": "Contexto",
        "numbers": {2: "Duas", 3: "Três", 4: "Quatro", 5: "Cinco"},
        "archived": "Arquivado<br>Cortexplor",
        "dossier": "Dossiê nº",
    }
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



# --------------------------------------------------------------------- helpers
def short(name):
    return re.sub(r"\s+(Technology|AI)$", "", name)


def hl(text, sub, cls="hl"):
    if sub and sub in text:
        return text.replace(sub, f"<span class='{cls}'>{sub}</span>", 1)
    return text


def ticks(n, on, off, h=8, gap=10, bottom=52, right=64):
    segs = "".join(
        f"<i style='flex:1;height:{h}px;background:{on if k < n else off}'></i>" for k in range(TOTAL)
    )
    return f"<div class='abs' style='left:64px;right:{right}px;bottom:{bottom}px;display:flex;gap:{gap}px'>{segs}</div>"


def crop_box(size, aspect, fx=0.5, fy=0.5):
    """Maior recorte com a proporção `aspect` (largura/altura), centrado em (fx, fy)."""
    w, h = size
    cw, ch = (w, w / aspect) if w / h < aspect else (h * aspect, h)
    x = min(max(fx * w - cw / 2, 0), w - cw)
    y = min(max(fy * h - ch / 2, 0), h - ch)
    return int(x), int(y), int(x + cw), int(y + ch)


def duotone(photo, box, size, name):
    """Recorte da foto na COR ORIGINAL (só contraste automático leve)."""
    d = L.HT
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{name}.png"
    im = Image.open(photo).convert("RGB").crop(box).resize(size, Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im.save(out)
    return uri(out)


class Ctx:
    """Tudo que os estilos precisam, derivado do spec."""

    def __init__(self, spec):
        self.d = spec
        self.u = UI[spec.get("lang", "pt")]
        img = spec["image"]
        self.photo = ROOT / img["path"]
        self.ph = uri(self.photo)
        self.pos = img.get("pos", "50% 50%")
        self.credit = f"{self.u['photo']}: {img['credit']}"
        self.src = spec["sources"]
        self.n = len(self.src)
        self.slug = spec["slug"]

    def src_sizes(self, big, small):
        return big if self.n <= 2 else small


def li_arrow(text):
    return f"<div class='li'>{ic(ARROW, 40, '#FF6B5E')}<span>{text}</span></div>"


# ============================================================================
# A. EDIÇÃO
# ============================================================================
def v_edicao(c: Ctx, pat):
    d = c.d
    css = """
.A{--bg:#FFFEFB;--fg:#14130F;--soft:#3A3935;--mu:#6B6960;--rule:#E4E2DB;--red:#C8362B;background:var(--bg);color:var(--fg);font-family:'Space Grotesk',sans-serif}
.A.dk{--bg:#14130F;--fg:#EDECE8;--soft:#C9C7BF;--mu:#9A978D;--rule:#2E2C28;--red:#FF6B5E}
.A .mast{position:absolute;left:64px;right:64px;top:40px;height:64px;display:flex;align-items:center;justify-content:space-between}
.A .mast img{height:38px}
.A .ed{font:500 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:var(--mu)}
.A .mast .pill{position:static;background:var(--fg);color:var(--bg);font-size:26px;padding:10px 26px}
.A .dbl{position:absolute;left:64px;right:64px;top:122px;height:12px;border-top:6px solid var(--fg);border-bottom:2px solid var(--fg)}
.A .lab{font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:var(--mu)}
.A .sec{display:inline-block;background:#C8362B;color:#fff;padding:8px 16px;font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase}
.A h1,.A h2{font-weight:700;letter-spacing:-.04em;line-height:1.0}
.A .red{color:var(--red)}
.A .cols{column-count:2;column-gap:56px;column-rule:2px solid var(--rule);font-size:34px;line-height:1.38;color:var(--soft)}
.A .cols p{margin-bottom:26px}
.A .cols p:first-child::first-letter{float:left;font-size:112px;line-height:.8;padding:8px 14px 0 0;font-weight:700;color:var(--fg)}
.A .li{display:flex;gap:28px;padding:24px 0;border-bottom:2px solid var(--fg);font-size:37px;line-height:1.26}
.A .li b.n{font:700 34px 'IBM Plex Mono';color:var(--red);flex:none;width:60px}
.A .ev{display:grid;grid-template-columns:210px 1fr;padding:30px 0;border-top:2px solid var(--fg)}
.A .ev .d{font:700 30px 'IBM Plex Mono';color:var(--red);line-height:1.3;text-transform:uppercase}
.A .ev .t{font-size:37px;line-height:1.28}
.A .strip{background:var(--fg);color:var(--bg);padding:24px 32px;font:500 25px 'IBM Plex Mono';letter-spacing:.06em;text-transform:uppercase}
"""

    def sl(n, dark, body):
        wm = WM_W if dark else WM_B
        on, off = ("#EDECE8", "rgba(237,236,232,.2)") if dark else (INK, "rgba(20,19,15,.18)")
        return (
            f"<div class='slide A{' dk' if dark else ''}'>"
            f"<div class='mast'><img src='{wm}'><span class='ed'>{d['date']} · IA</span>{pill(n)}</div><div class='dbl'></div>"
            f"{body}{ticks(n, on, off)}</div>"
        )

    s = []
    n = len(d["headline"])
    h1 = 98 if n <= 50 else (84 if n <= 62 else 76)
    s.append(sl(1, pat[0], f"""
<div class='abs' style='left:64px;top:172px;width:952px;height:1070px;display:flex;flex-direction:column'>
<div style='display:flex;gap:20px;align-items:center;margin-bottom:34px'><span class='sec'>{d['category']}</span><span class='lab'>{d['kicker']}</span></div>
<h1 style='font-size:{h1}px'>{d['headline']}</h1>
<div style='margin-top:30px;font-size:36px;line-height:1.3;color:var(--soft);border-top:2px solid var(--fg);padding-top:26px'>{d['dek']}</div>
<div style='margin-top:32px;flex:1;min-height:0;background:url({c.ph}) {c.pos}/cover;border:2px solid var(--fg)'></div>
<div class='lab' style='margin-top:14px;font-size:20px'>{c.credit}</div></div>"""))

    f = d["fact"]
    paras = "".join(f"<p>{p}</p>" for p in f["paras"])
    strip = c.u["confirm"].format(n=c.u["numbers"].get(c.n, str(c.n)))
    s.append(sl(2, pat[1], f"""
<div class='abs lab' style='left:64px;top:172px'>{f['label']}</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:76px'>{hl(f['title'], f.get('title_hl'), 'red')}</h2>
<div class='abs cols' style='left:64px;top:520px;width:952px'>{paras}</div>
<div class='abs strip' style='left:64px;top:1130px;width:952px'>{strip}</div>"""))

    p = d["points"]
    items = "".join(
        f"<div class='li'><b class='n'>{i + 1:02d}</b><span>{it['t']}</span></div>" for i, it in enumerate(p["items"])
    )
    s.append(sl(3, pat[2], f"""
<div class='abs lab' style='left:64px;top:172px'>{p['label']}</div>
<div class='abs' style='left:64px;top:226px;width:952px;font-size:92px;line-height:.98;font-weight:700;letter-spacing:-.045em'>{hl(p['title'], p.get('title_hl'), 'red')}</div>
<div class='abs' style='left:64px;top:520px;width:880px;font-size:33px;line-height:1.3;color:var(--soft)'>{p['note']}</div>
<div class='abs' style='left:64px;top:640px;width:952px;border-top:2px solid var(--fg)'>{items}</div>"""))

    v = d["voice"]
    bl = "".join(li_arrow(b) for b in v["bullets"])
    if v.get("mark"):
        top = f"""<div class='abs red' style='left:56px;top:190px;font-size:150px;line-height:1;font-weight:700'>{v['mark']}</div>
<div class='abs' style='left:64px;top:360px;width:952px;font-size:104px;line-height:.98;font-weight:700;letter-spacing:-.045em'>{v['big']}</div>
<div class='abs lab' style='left:64px;top:690px;width:952px'>{v['by']}</div>
<div class='abs' style='left:64px;top:770px;width:952px;border-top:2px solid var(--fg)'>{bl}</div>"""
    else:
        top = f"""<div class='abs' style='left:64px;top:240px;width:952px'>
<div class='red' style='font-size:132px;line-height:.95;font-weight:700;letter-spacing:-.05em'>{v['big']}</div>
<div class='lab' style='margin-top:36px;line-height:1.45'>{v['by']}</div>
<div style='margin-top:48px;border-top:2px solid var(--fg)'>{bl}</div></div>"""
    s.append(sl(4, pat[3], f"<div class='abs lab' style='left:64px;top:172px'>{v['label']}</div>{top}"))

    t = d["timeline"]
    evs = "".join(f"<div class='ev'><div class='d'>{e['when']}</div><div class='t'>{e['text']}</div></div>" for e in t["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs lab' style='left:64px;top:172px'>{c.u['timeline']}</div>
<div class='abs' style='left:64px;top:230px;width:952px;border-bottom:2px solid var(--fg)'>{evs}</div>"""))

    fs = c.src_sizes(64, 46)
    pad = 34 if c.n <= 2 else 20
    rows = "".join(
        f"<div class='li' style='font-size:{fs}px;font-weight:700;letter-spacing:-.04em;padding:{pad}px 0'><b class='n' style='width:80px'>{i + 1}</b><span>{n}</span></div>"
        for i, n in enumerate(c.src)
    )
    s.append(sl(6, pat[5], f"""
<div class='abs lab' style='left:64px;top:300px'>{c.u['sources']}</div>
<div class='abs' style='left:64px;top:350px;width:952px;border-top:2px solid var(--fg)'>{rows}</div>
<div class='abs' style='left:64px;top:900px;width:952px;font-size:42px;line-height:1.3'>{c.u['full']} <b>cortexplor.com</b></div>
<div class='abs lab' style='left:64px;top:1226px;font-size:20px'>{c.credit}</div>"""))
    return css, s


# ============================================================================
# B. TERMINAL
# ============================================================================
def v_terminal(c: Ctx, pat):
    d = c.d
    css = """
.B{--bg:#14130F;--fg:#EDECE8;--dim:#9A978D;--soft:#B7C0CC;--rule:#2E2C28;--dash:#3A3833;--card:#1C1B18;--acc:#F2C14E;--gr:#6FD08C;--rd:#FF7A70;--pg:rgba(111,208,140,.13);--pr:rgba(255,122,112,.13);--st:#fff;background:var(--bg);color:var(--fg);font-family:'Space Grotesk',sans-serif}
.B.lt{--bg:#FFFEFB;--fg:#14130F;--dim:#6B6960;--soft:#3A3935;--rule:#E4E2DB;--dash:#CFCBC0;--card:#F4F2EC;--acc:#8A6200;--gr:#2F7D4A;--rd:#C0392B;--pg:rgba(47,125,74,.1);--pr:rgba(192,57,43,.09);--st:#000}
.B .bar{position:absolute;left:64px;right:64px;top:44px;height:56px;display:flex;align-items:center;justify-content:space-between;font:500 24px 'IBM Plex Mono';color:var(--dim)}
.B .bar b{color:var(--fg);font-weight:500}
.B .bar .pill{position:static;background:var(--fg);color:var(--bg);font-size:26px;padding:8px 24px;font-family:'IBM Plex Mono'}
.B .ln{position:absolute;left:64px;right:64px;top:112px;border-top:2px solid var(--rule)}
.B .mono{font-family:'IBM Plex Mono'}
.B h1,.B h2{font-weight:700;letter-spacing:-.04em;line-height:1.02}
.B .hl{background:#F2C14E;color:#14130F;padding:0 .12em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.B .lbl{display:inline-block;background:#F2C14E;color:#14130F;font:600 24px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;padding:6px 14px}
.B .row{display:flex;gap:26px;padding:30px 0;border-bottom:2px dashed var(--dash);font:400 36px/1.35 'IBM Plex Mono'}
.B .row i{font-style:normal;color:var(--acc);flex:none}
.B .row b,.B .df b{color:var(--st)}
.B .df{display:flex;gap:26px;padding:28px 30px;font:400 33px/1.35 'IBM Plex Mono';margin-bottom:18px}
.B .df.p{background:var(--pg);border-left:8px solid var(--gr)}
.B .df.m{background:var(--pr);border-left:8px solid var(--rd)}
.B .df i{font-style:normal;font-weight:700;flex:none}
.B .df.p i{color:var(--gr)} .B .df.m i{color:var(--rd)}
.B .msg{border-left:8px solid #6B7A8F;background:var(--card);padding:30px 36px;margin-bottom:26px}
.B .msg.o{border-color:#F2C14E}
.B .msg .w{font:600 22px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin-bottom:12px}
.B .msg .q{font-size:60px;line-height:1.06;font-weight:700;letter-spacing:-.035em}
.B .kv{display:grid;grid-template-columns:330px 1fr;font:400 32px/1.3 'IBM Plex Mono'}
.B .kv div{padding:20px 0;border-bottom:2px dashed var(--dash)}
.B .kv .k{color:var(--dim)}
.B .kv .v{color:var(--fg)}
.B .kv .v b{font-weight:600}
"""

    def sl(n, light, cmd, body):
        on, off = (INK, "rgba(20,19,15,.18)") if light else ("#EDECE8", "rgba(237,236,232,.18)")
        return (
            f"<div class='slide B{' lt' if light else ''}'>"
            f"<div class='bar'><span>cortexplor@ia:~$ <b>{cmd}</b></span>{pill(n)}</div><div class='ln'></div>"
            f"{body}{ticks(n, on, off)}</div>"
        )

    def slugify(t):
        t = t.lower()
        for a, b in (("ç", "c"), ("ã", "a"), ("õ", "o"), ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("â", "a"), ("ê", "e"), ("ô", "o")):
            t = t.replace(a, b)
        return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

    cmd1 = f"cat {slugify(d['category'])}/{slugify(d.get('headline_hl') or c.slug)}.txt"
    src = f"<div class='abs mono' style='left:64px;top:1130px;font-size:26px;color:var(--dim)'>fonte: {', '.join(short(x) for x in c.src)}</div>"

    s = []
    s.append(sl(1, not pat[0], cmd1, f"""
<h1 class='abs' style='left:64px;top:170px;width:952px;font-size:84px;line-height:1.12'>{hl(d['headline'], d.get('headline_hl'))}</h1>
<div class='abs mono' style='left:64px;top:560px;width:952px;font-size:31px;line-height:1.45;color:var(--soft)'>&gt; {d['dek_short']}<span style='background:#F2C14E;color:#F2C14E'>_</span></div>
<div class='abs' style='left:64px;top:840px;width:952px;height:350px;overflow:hidden;border:2px solid var(--dash)'>
<img src='{c.ph}' style='width:100%;height:100%;object-fit:cover;object-position:{c.pos};filter:grayscale(1) contrast(1.15) brightness(.85)'>
<div class='abs' style='inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.3) 0 2px,transparent 2px 5px)'></div></div>
<div class='abs mono' style='left:64px;top:1206px;font-size:20px;color:var(--dim)'>{c.credit}</div>"""))

    f = d["fact"]
    rows = "".join(f"<div class='row'><i>›</i><span>{b}</span></div>" for b in f["bullets"])
    s.append(sl(2, not pat[1], "cat o-fato.txt", f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {f['label']}</span></div>
<div class='abs' style='left:64px;top:240px;width:952px'>{rows}</div>{src}"""))

    p = d["points"]
    dfs = "".join(
        f"<div class='df {'p' if it['kind'] == 'ok' else 'm'}'><i>{'+' if it['kind'] == 'ok' else '−'}</i><span>{it['t']}</span></div>"
        for it in p["items"]
    )
    s.append(sl(3, not pat[2], "diff acesso.patch", f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {p['label']}</span></div>
<div class='abs' style='left:64px;top:250px;width:952px'>{dfs}</div>
<div class='abs mono' style='left:64px;top:860px;width:952px;font-size:32px;line-height:1.4;color:var(--soft)'>{p['tail']}</div>{src}"""))

    v = d["voice"]
    cards = ""
    for i, cd in enumerate(v["cards"]):
        extra = f"<div class='mono' style='font-size:30px;line-height:1.4;color:var(--soft);margin-top:20px'>{cd['extra']}</div>" if cd.get("extra") else ""
        cards += f"<div class='msg{' o' if i else ''}'><div class='w'>{cd['who']}</div><div class='q'>{cd['text']}</div>{extra}</div>"
    s.append(sl(4, not pat[3], "log numeros.txt", f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {v['label']}</span></div>
<div class='abs' style='left:64px;top:250px;width:952px'>{cards}</div>"""))

    t = d["table"]
    kv = "".join(
        f"<div class='k'>{r['k']}</div><div class='v'{' style=color:var(--rd)' if r.get('neg') else ''}>{r['v']}</div>" for r in t["rows"]
    )
    s.append(sl(5, not pat[4], "status ficha.json", f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {t['label']}</span></div>
<div class='abs kv' style='left:64px;top:250px;width:952px'>{kv}</div>"""))

    fs = c.src_sizes(104, 64)
    s.append(sl(6, not pat[5], "exit 0", f"""
<div class='abs' style='left:64px;top:300px'><span class='lbl'>// {c.u['sources']}</span></div>
<h1 class='abs' style='left:64px;top:370px;width:952px;font-size:{fs}px'>{'<br>'.join(c.src)}</h1>
<div class='abs mono' style='left:64px;top:800px;width:952px;font-size:36px;line-height:1.4;color:var(--soft)'>&gt; {c.u['full']} <span class='hl' style='font-weight:700'>cortexplor.com</span></div>
<img class='abs' src='{WM_W}' style='left:64px;top:1180px;height:42px'>"""))
    return css, s


# ============================================================================
# C. DOSSIÊ
# ============================================================================
def v_dossie(c: Ctx, pat):
    d = c.d
    css = """
.C{--out:#E4E1D8;--panel:#FFFEFB;--fg:#14130F;--mu:#6B6960;--soft:#3A3935;--acc:#4A4843;--red:#B3261E;--tabbg:#14130F;--tabfg:#FFFEFB;background:var(--out);color:var(--fg);font-family:'Space Grotesk',sans-serif}
.C.dk{--out:#E4E1D8;--panel:#14130F;--fg:#EDECE8;--mu:#9A978D;--soft:#C9C7BF;--acc:#C9C7BF;--red:#FF6B5E;--tabbg:#EDECE8;--tabfg:#14130F}
.C .panel{position:absolute;left:40px;right:40px;top:132px;bottom:40px;background:var(--panel);border:3px solid var(--fg);border-radius:0 18px 18px 18px}
.C .tab{position:absolute;left:40px;top:86px;height:46px;padding:0 26px;background:var(--tabbg);color:var(--tabfg);font:600 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;display:flex;align-items:center;border-radius:14px 14px 0 0}
.C .pill{background:#14130F;color:#fff;top:40px}
.C .lab{font:600 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:var(--mu)}
.C h1,.C h2{font-weight:700;letter-spacing:-.04em;line-height:1}
.C .stamp{position:absolute;border:6px solid var(--red);color:var(--red);font:700 28px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;padding:10px 22px;transform:rotate(-7deg);opacity:.9;border-radius:6px;text-align:center;line-height:1.25}
.C .f{display:grid;grid-template-columns:250px 1fr;border-top:2px solid var(--fg)}
.C .f .k{font:600 22px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;color:var(--mu);padding:26px 0}
.C .f .v{font-size:35px;line-height:1.28;padding:20px 0}
.C .box{width:60px;height:60px;border:4px solid var(--fg);display:grid;place-items:center;flex:none;border-radius:8px;color:var(--fg)}
.C .box.x{border-color:var(--red);color:var(--red)}
.C .opt{display:flex;gap:30px;align-items:flex-start;padding:28px 0;border-top:2px solid var(--fg);font-size:40px;line-height:1.25}
.C .card{border:3px solid var(--fg);border-left:16px solid var(--acc);padding:30px 34px;margin-bottom:26px;border-radius:6px}
.C .card.r{border-left-color:var(--red)}
.C .card .q{font-size:54px;line-height:1.05;font-weight:700;letter-spacing:-.035em;margin-top:12px}
.C .num{display:grid;grid-template-columns:340px 1fr;gap:20px;padding:30px 0;border-top:2px solid var(--fg);align-items:center}
.C .num b{font-size:62px;letter-spacing:-.05em;line-height:.95;color:var(--acc);white-space:nowrap}
.C .num span{font-size:34px;line-height:1.3}
.C .crop{position:absolute;width:34px;height:34px;border-color:var(--fg);border-style:solid}
"""
    no = f"{d.get('no', 1):03d}"

    def sl(n, dark, body, tab=None):
        tab = tab or f"{c.u['dossier']} {no} · {d['category']}"
        on, off = ("#C9C7BF", "rgba(237,236,232,.18)") if dark else ("#4A4843", "rgba(20,19,15,.15)")
        return (
            f"<div class='slide C{' dk' if dark else ''}'><div class='tab'>{tab}</div><div class='panel'></div>{pill(n)}"
            f"{body}{ticks(n, on, off, bottom=62)}</div>"
        )

    s = []
    s.append(sl(1, pat[0], f"""
<div class='stamp' style='right:86px;top:176px'>{d['stamp']}</div>
<h1 class='abs' style='left:88px;top:290px;width:880px;font-size:84px'>{d['headline']}</h1>
<div class='abs' style='left:88px;top:700px;width:900px;font-size:34px;line-height:1.3;color:var(--soft)'>{d['dek']}</div>
<div class='abs' style='left:88px;top:910px;width:904px;height:270px;background:url({c.ph}) {c.pos}/cover'></div>
<div class='crop' style='left:76px;top:898px;border-width:4px 0 0 4px'></div><div class='crop' style='right:76px;top:898px;border-width:4px 4px 0 0'></div>
<div class='crop' style='left:76px;top:1168px;border-width:0 0 4px 4px'></div><div class='crop' style='right:76px;top:1168px;border-width:0 4px 4px 0'></div>
<div class='abs lab' style='left:88px;top:1200px;font-size:19px'>{c.u['annex']} · {c.credit}</div>"""))

    t = d["table"]
    frows = "".join(f"<div class='f'><div class='k'>{r['k']}</div><div class='v'>{r['v']}</div></div>" for r in t["rows"][:7])
    s.append(sl(2, pat[1], f"""
<div class='abs lab' style='left:88px;top:176px'>{t['label']}</div>
<div class='abs' style='left:88px;top:224px;width:904px;border-bottom:2px solid var(--fg)'>{frows}</div>"""))

    p = d["points"]
    opts = ""
    for it in p["items"]:
        if it["kind"] == "ok":
            opts += f"<div class='opt'><div class='box'>{ic(CHECK, 40)}</div><span>{it['t']}</span></div>"
        else:
            st = "text-decoration:line-through;text-decoration-color:var(--red);text-decoration-thickness:4px" if it.get("strike") else ""
            opts += f"<div class='opt'><div class='box x'>{ic(CROSS, 34)}</div><span style='{st}'>{it['t']}</span></div>"
    s.append(sl(3, pat[2], f"""
<div class='abs lab' style='left:88px;top:176px'>{p['label']}</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:84px'>{p['title']}</h2>
<div class='abs' style='left:88px;top:470px;width:904px;border-bottom:2px solid var(--fg)'>{opts}</div>
<div class='abs' style='left:88px;top:1090px;width:904px;font-size:32px;line-height:1.35;color:var(--mu)'>{p['note']}</div>"""))

    v = d["voice"]
    cards = ""
    for i, cd in enumerate(v["cards"]):
        extra = f"<div style='font-size:31px;line-height:1.35;margin-top:16px;color:var(--soft)'>{cd['extra']}</div>" if cd.get("extra") else ""
        cards += f"<div class='card{' r' if i else ''}'><div class='lab'>{cd['who']}</div><div class='q'>{cd['text']}</div>{extra}</div>"
    s.append(sl(4, pat[3], f"""
<div class='abs lab' style='left:88px;top:176px'>{v['label']}</div>
<div class='abs' style='left:88px;top:228px;width:904px'>{cards}</div>"""))

    tl = d["timeline"]
    nums = "".join(f"<div class='num'><b>{e['when']}</b><span>{e['text']}</span></div>" for e in tl["items"][:3])
    s.append(sl(5, pat[4], f"""
<div class='abs lab' style='left:88px;top:176px'>{c.u['context']}</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:80px'>{tl['title3']}</h2>
<div class='abs' style='left:88px;top:420px;width:904px;border-bottom:2px solid var(--fg)'>{nums}</div>"""))

    fs = c.src_sizes(64, 44)
    pad = "8px 0 22px" if c.n <= 2 else "4px 0 12px"
    srows = "".join(
        f"<div class='f' style='grid-template-columns:110px 1fr'><div class='k' style='font-size:34px;color:var(--acc)'>{i + 1:02d}</div><div class='v' style='font-size:{fs}px;font-weight:700;letter-spacing:-.04em;padding:{pad}'>{n}</div></div>"
        for i, n in enumerate(c.src)
    )
    s.append(sl(6, pat[5], f"""
<div class='abs lab' style='left:88px;top:300px'>{c.u['sources_long']}</div>
<div class='abs' style='left:88px;top:350px;width:904px;border-bottom:2px solid var(--fg)'>{srows}</div>
<div class='abs' style='left:88px;top:860px;width:904px;font-size:42px;line-height:1.3'>{c.u['full']} <b>cortexplor.com</b></div>
<img class='abs' src='{WM_W}' style='left:88px;top:1130px;height:42px'>
<div class='stamp' style='right:96px;top:1090px;font-size:24px'>{c.u['archived']}</div>""", f"{c.u['dossier']} {no} · {c.u['sources']}"))
    return css, s


# ============================================================================
# D. DUOTONE
# ============================================================================
def v_duotone(c: Ctx, pat=None):
    d = c.d
    size = Image.open(c.photo).size
    cover = duotone(c.photo, crop_box(size, 1080 / 1350), (1080, 1350), f"{c.slug}_cover")
    band = duotone(c.photo, crop_box(size, 1080 / 560), (1080, 560), f"{c.slug}_band")
    strip = duotone(c.photo, crop_box(size, 400 / 960, 0.72), (400, 960), f"{c.slug}_strip")
    css = """
.D{background:#FFFEFB;color:#14130F;font-family:'Space Grotesk',sans-serif}
.D.sl{background:#45433E;color:#F4F5F7}
.D.ik{background:#14130F;color:#EDECE8}
.D .grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px);background-size:90px 90px}
.D .m{position:absolute;width:44px;height:44px;border-color:#fff;border-style:solid}
.D .top{position:absolute;left:64px;right:150px;top:54px;font:500 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;opacity:.8}
.D .pill{background:rgba(20,19,15,.6);color:#fff}
.D .tag{display:inline-block;background:#FFFEFB;color:#14130F;font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;padding:10px 18px}
.D h1,.D h2{font-weight:700;letter-spacing:-.04em;line-height:1}
.D .body{font-size:38px;line-height:1.4}
.D .card{border:3px solid rgba(255,255,255,.55);padding:28px 30px}
.D .card .n{font-size:72px;font-weight:700;letter-spacing:-.05em;line-height:.95;color:#C9C7BF}
.D .card .t{font:600 22px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;margin-top:14px;opacity:.9}
.D .card .d{font-size:28px;line-height:1.3;margin-top:8px;opacity:.9}
"""

    def marks():
        return (
            "<div class='m' style='left:36px;top:36px;border-width:3px 0 0 3px'></div><div class='m' style='right:36px;top:36px;border-width:3px 3px 0 0'></div>"
            "<div class='m' style='left:36px;bottom:36px;border-width:0 0 3px 3px'></div><div class='m' style='right:36px;bottom:36px;border-width:0 3px 3px 0'></div>"
        )

    gridl = "background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px)"
    s = []
    s.append(f"""<div class='slide D ik'>
<div class='abs' style='inset:0;background:url({cover}) center/cover'></div><div class='grid'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(20,19,15,.35) 0%,rgba(20,19,15,0) 25%,rgba(20,19,15,.55) 55%,rgba(20,19,15,.96) 100%)'></div>
{marks()}<div class='top'>Cortexplor · {d['category']} · IA</div>{pill(1)}
<h1 class='abs' style='left:64px;top:770px;width:952px;font-size:88px;line-height:1.02;color:#fff'>{d['headline']}</h1>
<div class='abs' style='left:64px;top:1150px;width:900px;font-size:30px;line-height:1.35;color:#D5DAE0'>{d['dek_short']}</div>
{ticks(1, '#fff', 'rgba(255,255,255,.3)', bottom=62)}</div>""")

    f = d["fact"]
    s.append(f"""<div class='slide D'>
<div class='abs' style='left:0;top:0;width:1080px;height:560px;background:url({band}) center/cover'></div>
<div class='abs' style='left:0;top:0;width:1080px;height:560px;{gridl};background-size:90px 90px'></div>
<div class='top' style='color:#fff'>Cortexplor · {f['label']}</div>{pill(2)}
<div class='abs tag' style='left:64px;top:520px'>{f['label']}</div>
<h2 class='abs' style='left:64px;top:610px;width:952px;font-size:70px'>{f['title']}</h2>
<div class='abs body' style='left:64px;top:860px;width:952px;color:#3A3935'>{f['short']}</div>
{ticks(2, '#14130F', 'rgba(20,19,15,.15)', bottom=62)}</div>""")

    p = d["points"]
    li = ""
    for k, it in enumerate(p["items"]):
        icon = ic(CHECK, 44, "#C9C7BF") if it["kind"] == "ok" else ic(CROSS, 40, "#FF8A80")
        last = "border-bottom:2px solid rgba(255,255,255,.4);" if k == len(p["items"]) - 1 else ""
        li += f"<div style='display:flex;gap:26px;padding:22px 0;border-top:2px solid rgba(255,255,255,.4);{last}'>{icon}<span>{it['t']}</span></div>"
    s.append(f"""<div class='slide D sl'>
<div class='grid' style='opacity:.5'></div>{marks()}
<div class='top'>Cortexplor · {p['label']}</div>{pill(3)}
<div class='abs' style='left:64px;top:190px;width:952px;font-size:92px;line-height:.98;font-weight:700;letter-spacing:-.045em'>{p['title']}</div>
<div class='abs' style='left:64px;top:510px;width:860px;font-size:33px;line-height:1.3;color:#D5DAE0'>{p['note']}</div>
<div class='abs' style='left:64px;top:700px;width:952px;font-size:36px;line-height:1.32'>{li}</div>
{ticks(3, '#fff', 'rgba(255,255,255,.28)', bottom=62)}</div>""")

    v = d["voice"]
    s.append(f"""<div class='slide D'>
<div class='abs' style='right:0;top:0;width:340px;height:1350px;background:url({strip}) center/cover'></div>
<div class='abs' style='right:0;top:0;width:340px;height:1350px;{gridl};background-size:85px 85px'></div>
<div class='top' style='color:#14130F;right:420px'>Cortexplor · {v['label']}</div><div class='pill' style='background:#fff;color:#14130F;right:48px'>4/{TOTAL}</div>
<div class='abs tag' style='left:64px;top:190px;background:#14130F;color:#fff'>{v['label']}</div>
<div class='abs' style='left:64px;top:280px;width:620px'>
<div style='font-size:80px;line-height:1;font-weight:700;letter-spacing:-.045em'>{v.get('mark', '')}{v['big']}{'”' if v.get('mark') else ''}</div>
<div style='margin-top:36px;font:500 22px "IBM Plex Mono";letter-spacing:.12em;text-transform:uppercase;line-height:1.5;color:#6B6960'>{v['by']}</div>
<div class='body' style='margin-top:48px;font-size:33px;line-height:1.38;color:#3A3935'>{v['detail']}</div></div>
{ticks(4, '#14130F', 'rgba(20,19,15,.15)', bottom=62, right=400)}</div>""")

    t = d["timeline"]
    cards = "".join(
        f"<div class='card'><div class='n'>{e['when']}</div><div class='t'>{e['tag']}</div><div class='d'>{e['text']}</div></div>" for e in t["items"]
    )
    s.append(f"""<div class='slide D ik'>
<div class='top'>Cortexplor · {c.u['context']}</div>{pill(5)}
<h2 class='abs' style='left:64px;top:170px;width:952px;font-size:80px'>{t['title']}</h2>
<div class='abs' style='left:64px;top:380px;width:952px;display:grid;grid-template-columns:1fr 1fr;gap:26px'>{cards}</div>
{ticks(5, '#EDECE8', 'rgba(237,236,232,.2)', bottom=62)}</div>""")

    fs = c.src_sizes(104, 66)
    s.append(f"""<div class='slide D ik'>
<div class='abs' style='inset:0;background:url({cover}) center/cover;opacity:.45'></div><div class='grid'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(20,19,15,.3) 0%,rgba(20,19,15,.95) 70%)'></div>
{marks()}<div class='top'>Cortexplor · {c.u['sources']}</div>{pill(6)}
<div class='abs tag' style='left:64px;top:600px'>{c.u['sources']}</div>
<h1 class='abs' style='left:64px;top:690px;width:952px;font-size:{fs}px;color:#fff'>{'<br>'.join(c.src)}</h1>
<div class='abs' style='left:64px;top:1040px;width:952px;font-size:40px;line-height:1.3;color:#EDECE8'>{c.u['full']} <b>cortexplor.com</b></div>
<img class='abs' src='{WM_W}' style='left:64px;top:1180px;height:40px'>
{ticks(6, '#fff', 'rgba(255,255,255,.3)', bottom=62)}</div>""")
    return css, s


STYLES = {"edicao": v_edicao, "terminal": v_terminal, "dossie": v_dossie, "duotone": v_duotone}


def sheet(folder: Path, dest: Path):
    ims = [Image.open(folder / f"{i:02d}.png").convert("RGB").resize((540, 675)) for i in range(1, TOTAL + 1)]
    w = Image.new("RGB", (540 * 3 + 40, 675 * 2 + 30), (60, 60, 60))
    for k, im in enumerate(ims):
        w.paste(im, (10 + (k % 3) * 550, 10 + (k // 3) * 685))
    w.save(dest)


def build(slug, names=None, seed=11):
    spec = json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))
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
        folder = OUT / slug / n
        dest = OUT / slug / f"folha-{n}.png"
        sheet(folder, dest)
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
