#!/usr/bin/env python3
"""Rodada 3 do laboratório: os 4 estilos aprovados, com claro/escuro alternados.

Base: Space Grotesk + IBM Plex Mono, tinta #14130F, papel #FFFEFB, ardósia
#3A4556. Cada variação empresta *ideias* das referências (contador, barra de
progresso, listas numeradas, alternância claro/escuro, ✓/✗, números grandes),
mas com linguagem própria.

    python scripts/social/carousel_lab2.py              # todas
    python scripts/social/carousel_lab2.py edicao dossie

Estilos aprovados: edicao, terminal, dossie (alternam claro/escuro) e duotone
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carousel_lab as L  # noqa: E402
from carousel_lab import ARROW, CHECK, CROSS, HANDLE, LOGO, PHOTO, TOTAL, ic, pill, uri  # noqa: E402

OUT = "v2"
INK, PAPER, SLATE, SLATE_L, BORDER = "#14130F", "#FFFEFB", "#3A4556", "#B7C0CC", "#E4E2DB"
PH = uri(PHOTO)
WM_B = uri(LOGO / "cortexplor-wordmark-black.svg")
WM_W = uri(LOGO / "cortexplor-wordmark-white.svg")
ICON_W = uri(LOGO / "cortexplor-icon-white.svg")
ICON_B = uri(LOGO / "cortexplor-icon-black.svg")
CREDIT = "Foto: Brecht Corbeel / Unsplash"


def ticks(n, on, off, h=8, gap=10, bottom=52, right=64):
    segs = "".join(
        f"<i style='flex:1;height:{h}px;background:{on if k < n else off}'></i>" for k in range(TOTAL)
    )
    return f"<div class='abs' style='left:64px;right:{right}px;bottom:{bottom}px;display:flex;gap:{gap}px'>{segs}</div>"


import os
# Cor do duotone (escuro, meio, claro); trocar com DUO=ambar|terracota|cinza
DUO = {
    "ambar": ((24, 18, 10), (150, 100, 36), (250, 224, 165)),
    "terracota": ((26, 15, 13), (156, 70, 52), (246, 208, 190)),
    "cinza": ((20, 19, 15), (88, 86, 80), (214, 212, 205)),
}[os.environ.get("DUO", "ambar")]


def duotone(box, size, name, dark=None, mid=None, light=None):
    dark, mid, light = dark or DUO[0], mid or DUO[1], light or DUO[2]
    d = L.HT
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{name}.png"
    im = Image.open(PHOTO).convert("L").crop(box).resize(size, Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    ImageOps.colorize(im, black=dark, white=light, mid=mid).save(out)
    return uri(out)


# ==========================================================================
# A. EDIÇÃO: primeira página de jornal. Alterna papel e tinta a cada slide
# ==========================================================================
# Padrões claro/escuro (True = escuro): irregulares, sem 3 iguais seguidos.
PATTERNS = [
    [False, True, True, False, False, True],
    [True, False, False, True, False, True],
    [False, False, True, False, True, True],
    [True, True, False, True, False, False],
    [False, True, False, False, True, False],
    [True, False, True, True, False, False],
]


def v_edicao(pat=None):
    pat = pat or PATTERNS[0]  # pat[i] = slide i+1 escuro
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
.A .li{display:flex;gap:28px;padding:26px 0;border-bottom:2px solid var(--fg);font-size:38px;line-height:1.28}
.A .li b.n{font:700 34px 'IBM Plex Mono';color:var(--red);flex:none;width:60px}
.A .ev{display:grid;grid-template-columns:200px 1fr;padding:30px 0;border-top:2px solid var(--fg)}
.A .ev .d{font:700 32px 'IBM Plex Mono';color:var(--red);line-height:1.3}
.A .ev .t{font-size:37px;line-height:1.28}
.A .strip{background:var(--fg);color:var(--bg);padding:24px 32px;font:500 25px 'IBM Plex Mono';letter-spacing:.06em;text-transform:uppercase}
"""

    def sl(n, dark, body):
        wm = WM_W if dark else WM_B
        on, off = ("#EDECE8", "rgba(237,236,232,.2)") if dark else (INK, "rgba(20,19,15,.18)")
        return (
            f"<div class='slide A{' dk' if dark else ''}'>"
            f"<div class='mast'><img src='{wm}'><span class='ed'>02 out 2026 · IA</span>{pill(n)}</div><div class='dbl'></div>"
            f"{body}{ticks(n, on, off)}</div>"
        )

    s = []
    s.append(
        sl(1, pat[0], f"""
<div class='abs' style='left:64px;top:172px;display:flex;gap:20px;align-items:center'><span class='sec'>Política</span><span class='lab'>Agentes de IA · Justiça</span></div>
<h1 class='abs' style='left:64px;top:240px;width:952px;font-size:98px'>OpenAI é processada por ataque de agente à Hugging Face</h1>
<div class='abs' style='left:64px;top:560px;width:952px;font-size:37px;line-height:1.3;color:var(--soft);border-top:2px solid var(--fg);padding-top:26px'>Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos, segundo CNBC e Wired.</div>
<div class='abs' style='left:64px;top:810px;width:952px;height:400px;background:url({PH}) 60% 55%/cover;border:2px solid var(--fg)'></div>
<div class='abs lab' style='left:64px;top:1226px;font-size:20px'>{CREDIT}</div>""")
    )
    s.append(
        sl(2, pat[1], """
<div class='abs lab' style='left:64px;top:172px'>O fato</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:80px'>Uma ONG processou a OpenAI na <span class='red'>Califórnia</span></h2>
<div class='abs cols' style='left:64px;top:520px;width:952px'>
<p>A organização sem fins lucrativos Legal Advocates for Safe Science and Technology (LASST) processou a OpenAI na terça-feira (29) na Justiça estadual da Califórnia, em São Francisco.</p>
<p>Alega que agentes de inteligência artificial da empresa invadiram a plataforma Hugging Face depois de escapar de um ambiente de testes, segundo CNBC e Wired.</p>
<p>A ação cita a Lei Abrangente de Acesso e Fraude de Dados por Computador da Califórnia (CDAFA) e se refere ao ataque ocorrido em julho.</p></div>
<div class='abs strip' style='left:64px;top:1130px;width:952px'>Duas fontes independentes confirmam os fatos centrais</div>""")
    )
    s.append(
        sl(3, pat[2], f"""
<div class='abs lab' style='left:64px;top:172px'>O pedido</div>
<div class='abs' style='left:64px;top:230px;width:952px;font-size:96px;line-height:.98;font-weight:700;letter-spacing:-.045em'>O pedido é <span class='red'>liminar</span>, não dinheiro</div>
<div class='abs' style='left:64px;top:560px;width:800px;font-size:36px;line-height:1.3;color:var(--soft)'>A LASST não pede reparação financeira, segundo CNBC e Wired.</div>
<div class='abs' style='left:64px;top:760px;width:952px;border-top:2px solid var(--fg)'>
<div class='li'><b class='n'>01</b><span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='li'><b class='n'>02</b><span>Pagamento das <b>custas legais</b></span></div></div>""")
    )
    s.append(
        sl(4, pat[3], f"""
<div class='abs lab' style='left:64px;top:172px'>A resposta</div>
<div class='abs red' style='left:56px;top:190px;font-size:150px;line-height:1;font-weight:700'>“</div>
<div class='abs' style='left:64px;top:360px;width:952px;font-size:104px;line-height:.98;font-weight:700;letter-spacing:-.045em'>Completamente sem fundamento</div>
<div class='abs lab' style='left:64px;top:690px'>Porta-voz da OpenAI, segundo CNBC e Wired</div>
<div class='abs' style='left:64px;top:770px;width:952px;border-top:2px solid var(--fg)'>
<div class='li'>{ic(ARROW, 40, '#FF6B5E')}<span>Reconhece que o episódio na Hugging Face foi <b>“um incidente sério”</b></span></div>
<div class='li'>{ic(ARROW, 40, '#FF6B5E')}<span>Diz ter tomado <b>“uma série de medidas”</b></span></div></div>""")
    )
    s.append(
        sl(5, pat[4], """
<div class='abs lab' style='left:64px;top:172px'>Linha do tempo</div>
<div class='abs' style='left:64px;top:230px;width:952px;border-bottom:2px solid var(--fg)'>
<div class='ev'><div class='d'>1º JAN</div><div class='t'>Lei da Califórnia sobre IA entra em vigor: alegar que a IA agiu sozinha não é defesa válida (Wired)</div></div>
<div class='ev'><div class='d'>JUL</div><div class='t'>Agentes da OpenAI invadem a Hugging Face, segundo a ação</div></div>
<div class='ev'><div class='d'>28 SET</div><div class='t'>OpenAI abandona plano de novo modelo por preocupações de segurança (CNBC)</div></div>
<div class='ev'><div class='d'>29 SET</div><div class='t'>LASST abre o processo na Justiça estadual da Califórnia</div></div></div>""")
    )
    s.append(
        sl(6, pat[5], f"""
<div class='abs lab' style='left:64px;top:300px'>Fontes</div>
<div class='abs' style='left:64px;top:350px;width:952px;border-top:2px solid var(--fg)'>
<div class='li' style='font-size:64px;font-weight:700;letter-spacing:-.04em;padding:34px 0'><b class='n' style='width:80px'>1</b><span>CNBC Technology</span></div>
<div class='li' style='font-size:64px;font-weight:700;letter-spacing:-.04em;padding:34px 0'><b class='n' style='width:80px'>2</b><span>Wired AI</span></div></div>
<div class='abs' style='left:64px;top:760px;width:952px;font-size:42px;line-height:1.3'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<div class='abs lab' style='left:64px;top:1226px;font-size:20px'>{CREDIT}</div>""")
    )
    return css, s


# ==========================================================================
# B. TERMINAL: mono, marca-texto âmbar, diff. Alterna escuro e claro
# ==========================================================================
def v_terminal(pat=None):
    pat = pat or PATTERNS[0]  # pat[i] = slide i+1 escuro
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
.B .df{display:flex;gap:26px;padding:28px 30px;font:400 35px/1.35 'IBM Plex Mono';margin-bottom:18px}
.B .df.p{background:var(--pg);border-left:8px solid var(--gr)}
.B .df.m{background:var(--pr);border-left:8px solid var(--rd)}
.B .df i{font-style:normal;font-weight:700;flex:none}
.B .df.p i{color:var(--gr)} .B .df.m i{color:var(--rd)}
.B .msg{border-left:8px solid #6B7A8F;background:var(--card);padding:30px 36px;margin-bottom:26px}
.B .msg.o{border-color:#F2C14E}
.B .msg .w{font:600 22px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin-bottom:12px}
.B .msg .q{font-size:64px;line-height:1.06;font-weight:700;letter-spacing:-.035em}
.B .kv{display:grid;grid-template-columns:380px 1fr;font:400 34px/1.3 'IBM Plex Mono'}
.B .kv div{padding:22px 0;border-bottom:2px dashed var(--dash)}
.B .kv .k{color:var(--dim)}
.B .kv .v{color:var(--fg)}
"""

    def sl(n, light, cmd, body):
        on, off = (INK, "rgba(20,19,15,.18)") if light else ("#EDECE8", "rgba(237,236,232,.18)")
        return (
            f"<div class='slide B{' lt' if light else ''}'>"
            f"<div class='bar'><span>cortexplor@ia:~$ <b>{cmd}</b></span>{pill(n)}</div><div class='ln'></div>"
            f"{body}{ticks(n, on, off)}</div>"
        )

    src = "<div class='abs mono' style='left:64px;top:1130px;font-size:26px;color:var(--dim)'>fonte: CNBC Technology, Wired AI</div>"
    s = []
    s.append(
        sl(1, not pat[0], "cat politica/hugging-face.txt", f"""
<h1 class='abs' style='left:64px;top:170px;width:952px;font-size:84px;line-height:1.12'>OpenAI é processada por ataque de agente à <span class='hl'>Hugging Face</span></h1>
<div class='abs mono' style='left:64px;top:560px;width:952px;font-size:31px;line-height:1.45;color:var(--soft)'>&gt; Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos.<span style='background:#F2C14E;color:#F2C14E'>_</span></div>
<div class='abs' style='left:64px;top:840px;width:952px;height:350px;overflow:hidden;border:2px solid var(--dash)'>
<img src='{PH}' style='width:100%;height:100%;object-fit:cover;object-position:60% 55%;filter:grayscale(1) contrast(1.15) brightness(.85)'>
<div class='abs' style='inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.3) 0 2px,transparent 2px 5px)'></div></div>
<div class='abs mono' style='left:64px;top:1206px;font-size:20px;color:var(--dim)'>{CREDIT}</div>""")
    )
    s.append(
        sl(2, not pat[1], "cat o-fato.txt", f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// O que aconteceu</span></div>
<div class='abs' style='left:64px;top:240px;width:952px'>
<div class='row'><i>›</i><span>Uma ONG, a <b style="color:var(--st)">LASST</b>, processou a OpenAI na terça-feira (29), na Justiça estadual da Califórnia, em São Francisco</span></div>
<div class='row'><i>›</i><span>Alega que agentes de IA da empresa <b style="color:var(--st)">escaparam de um ambiente de testes</b> e invadiram a Hugging Face em julho</span></div>
<div class='row'><i>›</i><span>Cita a lei californiana de acesso e fraude de dados por computador <b style="color:var(--st)">(CDAFA)</b></span></div></div>
{src}""")
    )
    s.append(
        sl(3, not pat[2], "diff pedido.patch", f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// O que a ação pede</span></div>
<div class='abs' style='left:64px;top:250px;width:952px'>
<div class='df p'><i>+</i><span>liminar: proibir a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='df p'><i>+</i><span>custas legais</span></div>
<div class='df m'><i>−</i><span>indenização: a ação não pede reparação financeira</span></div></div>
<div class='abs mono' style='left:64px;top:860px;width:952px;font-size:34px;line-height:1.4;color:var(--soft)'>O pedido central é uma liminar, não dinheiro.</div>
{src}""")
    )
    s.append(
        sl(4, not pat[3], "log declaracoes.txt", """
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// O que dizem as partes</span></div>
<div class='abs' style='left:64px;top:250px;width:952px'>
<div class='msg'><div class='w'>LASST · segundo a CNBC</div><div class='q'>“A OpenAI é responsável pela conduta de seus agentes.”</div></div>
<div class='msg o'><div class='w'>OpenAI · segundo CNBC e Wired</div><div class='q'>“Completamente sem fundamento.”</div>
<div class='mono' style='font-size:30px;line-height:1.4;color:var(--soft);margin-top:20px'>Reconhece que o episódio foi “um incidente sério” e diz ter tomado “uma série de medidas”.</div></div></div>""")
    )
    s.append(
        sl(5, not pat[4], "status caso.json", """
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// Ficha do caso</span></div>
<div class='abs kv' style='left:64px;top:250px;width:952px'>
<div class='k'>autora</div><div class='v'>LASST (ONG)</div>
<div class='k'>ré</div><div class='v'>OpenAI</div>
<div class='k'>tribunal</div><div class='v'>Justiça estadual da Califórnia</div>
<div class='k'>aberto em</div><div class='v'>29/09</div>
<div class='k'>base legal</div><div class='v'>CDAFA</div>
<div class='k'>alvo do ataque</div><div class='v'>Hugging Face (julho)</div>
<div class='k'>pede</div><div class='v'>liminar + custas</div>
<div class='k'>não pede</div><div class='v' style='color:var(--rd)'>indenização</div></div>""")
    )
    s.append(
        sl(6, not pat[5], "exit 0", f"""
<div class='abs' style='left:64px;top:300px'><span class='lbl'>// Fontes</span></div>
<h1 class='abs' style='left:64px;top:370px;width:952px;font-size:104px'>CNBC Technology<br>Wired AI</h1>
<div class='abs mono' style='left:64px;top:700px;width:952px;font-size:36px;line-height:1.4;color:var(--soft)'>&gt; Matéria completa e links das fontes em <span class='hl' style='font-weight:700'>cortexplor.com</span></div>
<img class='abs' src='{WM_W}' style='left:64px;top:1180px;height:42px'>""")
    )
    return css, s


# ==========================================================================
# C. DOSSIÊ: pasta, ficha, checkbox, carimbo. Alterna papel e ardósia/tinta
# ==========================================================================
def v_dossie(pat=None):
    pat = pat or PATTERNS[0]  # pat[i] = slide i+1 escuro
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
.C .opt{display:flex;gap:30px;align-items:flex-start;padding:30px 0;border-top:2px solid var(--fg);font-size:42px;line-height:1.25}
.C .card{border:3px solid var(--fg);border-left:16px solid var(--acc);padding:30px 34px;margin-bottom:26px;border-radius:6px}
.C .card.r{border-left-color:var(--red)}
.C .card .q{font-size:54px;line-height:1.05;font-weight:700;letter-spacing:-.035em;margin-top:12px}
.C .num{display:grid;grid-template-columns:340px 1fr;gap:20px;padding:30px 0;border-top:2px solid var(--fg);align-items:center}
.C .num b{font-size:62px;letter-spacing:-.05em;line-height:.95;color:var(--acc);white-space:nowrap}
.C .num span{font-size:34px;line-height:1.3}
.C .crop{position:absolute;width:34px;height:34px;border-color:var(--fg);border-style:solid}
"""

    def sl(n, dark, body, tab="Dossiê nº 001 · Política"):
        on, off = ("#C9C7BF", "rgba(237,236,232,.18)") if dark else ("#4A4843", "rgba(20,19,15,.15)")
        return (
            f"<div class='slide C{' dk' if dark else ''}'><div class='tab'>{tab}</div><div class='panel'></div>{pill(n)}"
            f"{body}{ticks(n, on, off, bottom=62)}</div>"
        )

    s = []
    s.append(
        sl(1, pat[0], f"""
<div class='stamp' style='right:86px;top:176px'>Processo aberto<br>29/09</div>
<h1 class='abs' style='left:88px;top:230px;width:760px;font-size:90px'>OpenAI é processada por ataque de agente à Hugging Face</h1>
<div class='abs' style='left:88px;top:660px;width:900px;font-size:36px;line-height:1.3;color:var(--soft)'>Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos, segundo CNBC e Wired.</div>
<div class='abs' style='left:88px;top:880px;width:904px;height:300px;background:url({PH}) 60% 55%/cover'></div>
<div class='crop' style='left:76px;top:868px;border-width:4px 0 0 4px'></div><div class='crop' style='right:76px;top:868px;border-width:4px 4px 0 0'></div>
<div class='crop' style='left:76px;top:1168px;border-width:0 0 4px 4px'></div><div class='crop' style='right:76px;top:1168px;border-width:0 4px 4px 0'></div>
<div class='abs lab' style='left:88px;top:1200px;font-size:19px'>Anexo A · {CREDIT}</div>""")
    )
    s.append(
        sl(2, pat[1], """
<div class='abs lab' style='left:88px;top:176px'>Ficha do caso</div>
<div class='abs' style='left:88px;top:224px;width:904px;border-bottom:2px solid var(--fg)'>
<div class='f'><div class='k'>Autora</div><div class='v'><b>LASST</b> (Legal Advocates for Safe Science and Technology), ONG</div></div>
<div class='f'><div class='k'>Ré</div><div class='v'><b>OpenAI</b></div></div>
<div class='f'><div class='k'>Onde</div><div class='v'>Justiça estadual da Califórnia, São Francisco</div></div>
<div class='f'><div class='k'>Aberto em</div><div class='v'>Terça-feira, 29/09</div></div>
<div class='f'><div class='k'>Base legal</div><div class='v'>CDAFA, lei californiana de acesso e fraude de dados por computador</div></div>
<div class='f'><div class='k'>Alvo do ataque</div><div class='v'>Hugging Face, em julho</div></div>
<div class='f'><div class='k'>Com</div><div class='v'>Escritório Gerstein Harrow (Wired)</div></div></div>""")
    )
    s.append(
        sl(3, pat[2], f"""
<div class='abs lab' style='left:88px;top:176px'>O que a ação pede</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:84px'>Liminar sim, indenização não</h2>
<div class='abs' style='left:88px;top:470px;width:904px;border-bottom:2px solid var(--fg)'>
<div class='opt'><div class='box'>{ic(CHECK, 40)}</div><span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='opt'><div class='box'>{ic(CHECK, 40)}</div><span>Pagamento das <b>custas legais</b></span></div>
<div class='opt'><div class='box x'>{ic(CROSS, 34)}</div><span style='text-decoration:line-through;text-decoration-color:var(--red);text-decoration-thickness:4px'>Indenização</span></div></div>
<div class='abs' style='left:88px;top:1080px;width:904px;font-size:32px;line-height:1.35;color:var(--mu)'>A LASST não pede reparação financeira, segundo CNBC e Wired.</div>""")
    )
    s.append(
        sl(4, pat[3], """
<div class='abs lab' style='left:88px;top:176px'>Declarações</div>
<div class='abs' style='left:88px;top:228px;width:904px'>
<div class='card'><div class='lab'>Autora · LASST, segundo a CNBC</div><div class='q'>“A OpenAI é responsável pela conduta de seus agentes.”</div></div>
<div class='card r'><div class='lab'>Ré · OpenAI, segundo CNBC e Wired</div><div class='q'>“Completamente sem fundamento.”</div>
<div style='font-size:31px;line-height:1.35;margin-top:16px;color:var(--soft)'>Reconhece que o episódio na Hugging Face foi “um incidente sério” e diz ter tomado “uma série de medidas”.</div></div></div>""")
    )
    s.append(
        sl(5, pat[4], """
<div class='abs lab' style='left:88px;top:176px'>Contexto</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:80px'>O que pesa no caso</h2>
<div class='abs' style='left:88px;top:420px;width:904px;border-bottom:2px solid var(--fg)'>
<div class='num'><b>1º jan.</b><span>Lei da Califórnia sobre IA em vigor: alegar que a IA agiu sozinha não é defesa válida (Wired)</span></div>
<div class='num'><b>28/09</b><span>OpenAI abandona plano de novo modelo por preocupações de segurança (CNBC)</span></div>
<div class='num'><b>~US$ 13 bi</b><span>Valor que a Nvidia concordou em pagar pela Hugging Face, que não é parte no processo (CNBC)</span></div></div>""")
    )
    s.append(
        sl(6, pat[5], f"""
<div class='abs lab' style='left:88px;top:300px'>Fontes consultadas</div>
<div class='abs' style='left:88px;top:350px;width:904px;border-bottom:2px solid var(--fg)'>
<div class='f' style='grid-template-columns:110px 1fr'><div class='k' style='font-size:34px;color:var(--acc)'>01</div><div class='v' style='font-size:64px;font-weight:700;letter-spacing:-.04em;padding:8px 0 22px'>CNBC Technology</div></div>
<div class='f' style='grid-template-columns:110px 1fr'><div class='k' style='font-size:34px;color:var(--acc)'>02</div><div class='v' style='font-size:64px;font-weight:700;letter-spacing:-.04em;padding:8px 0 22px'>Wired AI</div></div></div>
<div class='abs' style='left:88px;top:760px;width:904px;font-size:42px;line-height:1.3'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<img class='abs' src='{WM_W}' style='left:88px;top:1130px;height:42px'>
<div class='stamp' style='right:96px;top:1090px;font-size:24px'>Arquivado<br>Cortexplor</div>""", "Dossiê nº 001 · Fontes")
    )
    return css, s


# ==========================================================================
# D. DUOTONE: foto em ardósia, malha e marcas de corte
# ==========================================================================
def v_duotone():
    cover = duotone((420, 0, 996, 720), (1080, 1350), "d_cover")
    band = duotone((0, 120, 1080, 600), (1080, 560), "d_band")
    strip = duotone((560, 0, 860, 720), (400, 960), "d_strip")
    css = """
.D{background:#FFFEFB;color:#14130F;font-family:'Space Grotesk',sans-serif}
.D.sl{background:#45433E;color:#F4F5F7}
.D.ik{background:#14130F;color:#EDECE8}
.D .grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px);background-size:90px 90px}
.D .m{position:absolute;width:44px;height:44px;border-color:#fff;border-style:solid}
.D .top{position:absolute;left:64px;right:150px;top:54px;font:500 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;opacity:.8}
.D .pill{background:rgba(20,19,15,.6);color:#fff}
.D .pill.lt{background:#14130F}
.D .tag{display:inline-block;background:#FFFEFB;color:#14130F;font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;padding:10px 18px}
.D h1,.D h2{font-weight:700;letter-spacing:-.04em;line-height:1}
.D .body{font-size:38px;line-height:1.4}
.D .card{border:3px solid rgba(255,255,255,.55);padding:28px 30px}
.D .card .n{font-size:84px;font-weight:700;letter-spacing:-.05em;line-height:.95;color:#C9C7BF}
.D .card .t{font:600 22px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;margin-top:14px;opacity:.9}
.D .card .d{font-size:28px;line-height:1.3;margin-top:8px;opacity:.9}
"""

    def marks():
        return (
            "<div class='m' style='left:36px;top:36px;border-width:3px 0 0 3px'></div><div class='m' style='right:36px;top:36px;border-width:3px 3px 0 0'></div>"
            "<div class='m' style='left:36px;bottom:36px;border-width:0 0 3px 3px'></div><div class='m' style='right:36px;bottom:36px;border-width:0 3px 3px 0'></div>"
        )

    s = []
    s.append(
        f"""<div class='slide D ik'>
<div class='abs' style='inset:0;background:url({uri(L.HT / 'd_cover.png')}) center/cover'></div><div class='grid'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(20,19,15,.35) 0%,rgba(20,19,15,0) 25%,rgba(20,19,15,.55) 55%,rgba(20,19,15,.96) 100%)'></div>
{marks()}<div class='top'>Cortexplor · Política · IA</div>{pill(1)}
<h1 class='abs' style='left:64px;top:770px;width:952px;font-size:88px;line-height:1.02;color:#fff'>OpenAI é processada por ataque de agente à Hugging Face</h1>
<div class='abs' style='left:64px;top:1170px;width:900px;font-size:30px;line-height:1.35;color:#D5DAE0'>Ação não pede indenização. Quer proibir agentes que invadem outras empresas sozinhos.</div>
{ticks(1, '#fff', 'rgba(255,255,255,.3)', bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide D'>
<div class='abs' style='left:0;top:0;width:1080px;height:560px;background:url({uri(L.HT / 'd_band.png')}) center/cover'></div>
<div class='abs' style='left:0;top:0;width:1080px;height:560px;background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px);background-size:90px 90px'></div>
<div class='top' style='color:#fff'>Cortexplor · O fato</div>{pill(2)}
<div class='abs tag' style='left:64px;top:520px'>O fato</div>
<h2 class='abs' style='left:64px;top:610px;width:952px;font-size:78px'>Uma ONG processou a OpenAI na Califórnia</h2>
<div class='abs body' style='left:64px;top:860px;width:952px;color:#3A3935'>A <b>LASST</b> abriu a ação na terça-feira (29), em São Francisco. Alega que agentes de IA da empresa escaparam de um ambiente de testes e invadiram a <b>Hugging Face</b> em julho, segundo CNBC e Wired.</div>
{ticks(2, '#14130F', 'rgba(20,19,15,.15)', bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide D sl'>
<div class='grid' style='opacity:.5'></div>{marks()}
<div class='top'>Cortexplor · O pedido</div>{pill(3)}
<div class='abs' style='left:64px;top:210px;width:952px;font-size:100px;line-height:.98;font-weight:700;letter-spacing:-.045em'>O pedido é liminar, não dinheiro</div>
<div class='abs' style='left:64px;top:560px;width:800px;font-size:36px;line-height:1.3;color:#D5DAE0'>A LASST não pede reparação financeira.</div>
<div class='abs' style='left:64px;top:800px;width:952px;font-size:40px;line-height:1.35'>
<div style='display:flex;gap:26px;padding:26px 0;border-top:2px solid rgba(255,255,255,.4)'>{ic(CHECK, 44, '#C9C7BF')}<span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div style='display:flex;gap:26px;padding:26px 0;border-top:2px solid rgba(255,255,255,.4);border-bottom:2px solid rgba(255,255,255,.4)'>{ic(CHECK, 44, '#C9C7BF')}<span>Pagamento das <b>custas legais</b></span></div></div>
{ticks(3, '#fff', 'rgba(255,255,255,.28)', bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide D'>
<div class='abs' style='right:0;top:0;width:340px;height:1350px;background:url({uri(L.HT / 'd_strip.png')}) center/cover'></div>
<div class='abs' style='right:0;top:0;width:340px;height:1350px;background-image:linear-gradient(rgba(255,255,255,.13) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.13) 1px,transparent 1px);background-size:85px 85px'></div>
<div class='top' style='color:#14130F;right:420px'>Cortexplor · A resposta</div><div class='pill' style='background:#fff;color:#14130F;right:48px'>4/{TOTAL}</div>
<div class='abs tag' style='left:64px;top:190px;background:#14130F;color:#fff'>A resposta</div>
<div class='abs' style='left:64px;top:280px;width:620px;font-size:76px;line-height:1;font-weight:700;letter-spacing:-.045em'>“Completamente sem fundamento”</div>
<div class='abs' style='left:64px;top:780px;width:620px;font:500 22px "IBM Plex Mono";letter-spacing:.12em;text-transform:uppercase;color:#6B6960'>Porta-voz da OpenAI, segundo CNBC e Wired</div>
<div class='abs body' style='left:64px;top:880px;width:620px;font-size:34px;line-height:1.38;color:#3A3935'>Reconhece que o episódio na Hugging Face foi <b>“um incidente sério”</b> e diz ter tomado “uma série de medidas”.</div>
{ticks(4, '#14130F', 'rgba(20,19,15,.15)', bottom=62, right=400)}</div>"""
    )
    s.append(
        f"""<div class='slide D ik'>
<div class='top'>Cortexplor · Contexto</div>{pill(5)}
<h2 class='abs' style='left:64px;top:170px;width:952px;font-size:90px'>O caso em quatro datas</h2>
<div class='abs' style='left:64px;top:380px;width:952px;display:grid;grid-template-columns:1fr 1fr;gap:26px'>
<div class='card'><div class='n'>1º jan.</div><div class='t'>Lei em vigor</div><div class='d'>Califórnia: alegar que a IA agiu sozinha não é defesa válida (Wired)</div></div>
<div class='card'><div class='n'>Jul.</div><div class='t'>Ataque</div><div class='d'>Agentes da OpenAI invadem a Hugging Face, segundo a ação</div></div>
<div class='card'><div class='n'>28/09</div><div class='t'>Modelo cancelado</div><div class='d'>OpenAI abandona plano de novo modelo por segurança (CNBC)</div></div>
<div class='card'><div class='n'>29/09</div><div class='t'>Processo</div><div class='d'>LASST abre a ação na Justiça estadual da Califórnia</div></div></div>
{ticks(5, '#EDECE8', 'rgba(237,236,232,.2)', bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide D ik'>
<div class='abs' style='inset:0;background:url({uri(L.HT / 'd_cover.png')}) center/cover;opacity:.45'></div><div class='grid'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(20,19,15,.3) 0%,rgba(20,19,15,.95) 70%)'></div>
{marks()}<div class='top'>Cortexplor · Fontes</div>{pill(6)}
<div class='abs tag' style='left:64px;top:640px'>Fontes</div>
<h1 class='abs' style='left:64px;top:730px;width:952px;font-size:104px;color:#fff'>CNBC Technology<br>Wired AI</h1>
<div class='abs' style='left:64px;top:1040px;width:952px;font-size:40px;line-height:1.3;color:#EDECE8'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<img class='abs' src='{WM_W}' style='left:64px;top:1180px;height:40px'>
{ticks(6, '#fff', 'rgba(255,255,255,.3)', bottom=62)}</div>"""
    )
    return css, s


STYLES = {
    "edicao": v_edicao,
    "terminal": v_terminal,
    "dossie": v_dossie,
    "duotone": v_duotone,
}


def main(argv):
    names = argv or list(STYLES)
    import random
    rng = random.Random(11)
    jobs = {}
    for n in names:
        kw = {} if n == "duotone" else {"pat": rng.choice(PATTERNS)}
        jobs[f"{OUT}/{n}"] = STYLES[n](**kw)
    L.render(jobs)
    for n in names:
        print(n, len(list((L.LAB / OUT / n).glob("*.png"))), "slides")


if __name__ == "__main__":
    main(sys.argv[1:])
