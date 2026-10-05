#!/usr/bin/env python3
"""Rodada 2 do laboratório: 5 variações do estilo "print" (identidade do site).

Base: Space Grotesk + IBM Plex Mono, tinta #14130F, papel #FFFEFB, ardósia
#3A4556. Cada variação empresta *ideias* das referências (contador, barra de
progresso, listas numeradas, alternância claro/escuro, ✓/✗, números grandes),
mas com linguagem própria.

    python scripts/social/carousel_lab2.py              # todas
    python scripts/social/carousel_lab2.py edicao dossie

Variações: edicao, terminal, dossie, duotone, perguntas
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


def duotone(box, size, name, dark=(20, 19, 15), mid=(74, 86, 106), light=(205, 212, 222)):
    d = L.HT
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{name}.png"
    im = Image.open(PHOTO).convert("L").crop(box).resize(size, Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    ImageOps.colorize(im, black=dark, white=light, mid=mid).save(out)
    return uri(out)


# ==========================================================================
# A. EDIÇÃO: primeira página de jornal. Cabeçalho duplo, seção, colunas
# ==========================================================================
def v_edicao():
    css = """
.A{background:#FFFEFB;color:#14130F;font-family:'Space Grotesk',sans-serif}
.A.dk{background:#14130F;color:#EDECE8}
.A .mast{position:absolute;left:64px;right:64px;top:40px;height:64px;display:flex;align-items:center;justify-content:space-between}
.A .mast img{height:38px}
.A .ed{font:500 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;opacity:.6}
.A .mast .pill{position:static;background:#14130F;color:#FFFEFB;font-size:26px;padding:10px 26px}
.A.dk .mast .pill{background:#FFFEFB;color:#14130F}
.A .dbl{position:absolute;left:64px;right:64px;top:122px;height:12px;border-top:6px solid currentColor;border-bottom:2px solid currentColor}
.A .lab{font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase}
.A .sec{display:inline-block;background:#C8362B;color:#fff;padding:8px 16px;font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase}
.A h1,.A h2{font-weight:700;letter-spacing:-.04em;line-height:1.0}
.A .red{color:#C8362B}
.A .cols{column-count:2;column-gap:56px;column-rule:2px solid #E4E2DB;font-size:34px;line-height:1.38;color:#2B2A26}
.A .cols p{margin-bottom:26px}
.A .cols p:first-child::first-letter{float:left;font-size:112px;line-height:.8;padding:8px 14px 0 0;font-weight:700;color:#14130F}
.A .li{display:flex;gap:28px;padding:26px 0;border-bottom:2px solid #14130F;font-size:38px;line-height:1.28}
.A .li b.n{font:700 34px 'IBM Plex Mono';color:#C8362B;flex:none;width:60px}
.A .ev{display:grid;grid-template-columns:200px 1fr;padding:30px 0;border-top:2px solid #14130F}
.A .ev .d{font:700 32px 'IBM Plex Mono';color:#C8362B;line-height:1.3}
.A .ev .t{font-size:37px;line-height:1.28}
"""

    def mast(n, dark=False):
        wm = WM_W if dark else WM_B
        return (
            f"<div class='mast'><img src='{wm}'><span class='ed'>02 out 2026 · IA</span>{pill(n)}</div><div class='dbl'></div>"
        )

    on, off = INK, "rgba(20,19,15,.18)"
    s = []
    s.append(
        f"""<div class='slide A'>{mast(1)}
<div class='abs' style='left:64px;top:172px;display:flex;gap:20px;align-items:center'><span class='sec'>Política</span><span class='lab' style='opacity:.6'>Agentes de IA · Justiça</span></div>
<h1 class='abs' style='left:64px;top:240px;width:952px;font-size:98px'>OpenAI é processada por ataque de agente à Hugging Face</h1>
<div class='abs' style='left:64px;top:560px;width:952px;font-size:37px;line-height:1.3;color:#3A3935;border-top:2px solid #14130F;padding-top:26px'>Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos, segundo CNBC e Wired.</div>
<div class='abs' style='left:64px;top:810px;width:952px;height:400px;background:url({PH}) 60% 55%/cover;border:2px solid #14130F'></div>
<div class='abs lab' style='left:64px;top:1226px;font-size:20px;opacity:.55'>{CREDIT}</div>
{ticks(1, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide A'>{mast(2)}
<div class='abs lab' style='left:64px;top:172px;opacity:.6'>O fato</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:80px'>Uma ONG processou a OpenAI na <span class='red'>Califórnia</span></h2>
<div class='abs cols' style='left:64px;top:520px;width:952px'>
<p>A organização sem fins lucrativos Legal Advocates for Safe Science and Technology (LASST) processou a OpenAI na terça-feira (29) na Justiça estadual da Califórnia, em São Francisco.</p>
<p>Alega que agentes de inteligência artificial da empresa invadiram a plataforma Hugging Face depois de escapar de um ambiente de testes, segundo CNBC e Wired.</p>
<p>A ação cita a Lei Abrangente de Acesso e Fraude de Dados por Computador da Califórnia (CDAFA) e se refere ao ataque ocorrido em julho.</p></div>
<div class='abs' style='left:64px;top:1130px;width:952px;background:#14130F;color:#FFFEFB;padding:24px 32px;font:500 25px "IBM Plex Mono";letter-spacing:.06em;text-transform:uppercase'>Duas fontes independentes confirmam os fatos centrais</div>
{ticks(2, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide A'>{mast(3)}
<div class='abs lab' style='left:64px;top:172px;opacity:.6'>O pedido</div>
<div class='abs' style='left:48px;top:200px;font-size:500px;font-weight:700;letter-spacing:-.06em;line-height:.85;color:#14130F'>0</div>
<div class='abs' style='left:420px;top:330px;width:596px;font-size:58px;line-height:1.02;font-weight:700;letter-spacing:-.035em'>pedido de <span class='red'>indenização</span></div>
<div class='abs' style='left:420px;top:500px;width:596px;font-size:34px;line-height:1.3;color:#3A3935'>A LASST não pede reparação financeira, segundo CNBC e Wired.</div>
<div class='abs' style='left:64px;top:760px;width:952px;border-top:2px solid #14130F'>
<div class='li'><b class='n'>01</b><span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='li'><b class='n'>02</b><span>Pagamento das <b>custas legais</b></span></div></div>
{ticks(3, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide A'>{mast(4)}
<div class='abs lab' style='left:64px;top:172px;opacity:.6'>A resposta</div>
<div class='abs red' style='left:56px;top:190px;font-size:380px;line-height:1;font-weight:700'>“</div>
<div class='abs' style='left:64px;top:470px;width:952px;font-size:104px;line-height:.98;font-weight:700;letter-spacing:-.045em'>Completamente sem fundamento</div>
<div class='abs lab' style='left:64px;top:800px;opacity:.6'>Porta-voz da OpenAI, segundo CNBC e Wired</div>
<div class='abs' style='left:64px;top:880px;width:952px;border-top:2px solid #14130F'>
<div class='li'>{ic(ARROW, 40, '#C8362B')}<span>Reconhece que o episódio na Hugging Face foi <b>“um incidente sério”</b></span></div>
<div class='li'>{ic(ARROW, 40, '#C8362B')}<span>Diz ter tomado <b>“uma série de medidas”</b></span></div></div>
{ticks(4, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide A'>{mast(5)}
<div class='abs lab' style='left:64px;top:172px;opacity:.6'>Linha do tempo</div>
<div class='abs' style='left:64px;top:230px;width:952px;border-bottom:2px solid #14130F'>
<div class='ev'><div class='d'>1º JAN</div><div class='t'>Lei da Califórnia sobre IA entra em vigor: alegar que a IA agiu sozinha não é defesa válida (Wired)</div></div>
<div class='ev'><div class='d'>JUL</div><div class='t'>Agentes da OpenAI invadem a Hugging Face, segundo a ação</div></div>
<div class='ev'><div class='d'>28 SET</div><div class='t'>OpenAI abandona plano de novo modelo por preocupações de segurança (CNBC)</div></div>
<div class='ev'><div class='d'>29 SET</div><div class='t'>LASST abre o processo na Justiça estadual da Califórnia</div></div></div>
{ticks(5, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide A dk'>{mast(6, True)}
<div class='abs lab' style='left:64px;top:300px;opacity:.6'>Fontes</div>
<div class='abs' style='left:64px;top:350px;width:952px;border-top:2px solid #EDECE8'>
<div class='li' style='border-color:#EDECE8;font-size:64px;font-weight:700;letter-spacing:-.04em;padding:34px 0'><b class='n' style='color:#B7C0CC;width:80px'>1</b><span>CNBC Technology</span></div>
<div class='li' style='border-color:#EDECE8;font-size:64px;font-weight:700;letter-spacing:-.04em;padding:34px 0'><b class='n' style='color:#B7C0CC;width:80px'>2</b><span>Wired AI</span></div></div>
<div class='abs' style='left:64px;top:760px;width:952px;font-size:42px;line-height:1.3;color:#EDECE8'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<div class='abs lab' style='left:64px;top:1226px;font-size:20px;opacity:.5'>{CREDIT}</div>
{ticks(6, '#EDECE8', 'rgba(237,236,232,.2)')}</div>"""
    )
    return css, s


# ==========================================================================
# B. TERMINAL: tinta, mono, marca-texto âmbar, diff para "o que pede"
# ==========================================================================
def v_terminal():
    css = """
.B{background:#14130F;color:#EDECE8;font-family:'Space Grotesk',sans-serif;--am:#F2C14E;--gr:#6FD08C;--rd:#FF7A70;--dim:#9A978D}
.B .bar{position:absolute;left:64px;right:64px;top:44px;height:56px;display:flex;align-items:center;justify-content:space-between;font:500 24px 'IBM Plex Mono';color:var(--dim)}
.B .bar b{color:#EDECE8;font-weight:500}
.B .bar .pill{position:static;background:#EDECE8;color:#14130F;font-size:26px;padding:8px 24px;font-family:'IBM Plex Mono'}
.B .ln{position:absolute;left:64px;right:64px;top:112px;border-top:2px solid #2E2C28}
.B .mono{font-family:'IBM Plex Mono'}
.B h1,.B h2{font-weight:700;letter-spacing:-.04em;line-height:1.02}
.B .hl{background:var(--am);color:#14130F;padding:0 .12em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.B .lbl{font:600 24px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--am)}
.B .row{display:flex;gap:26px;padding:30px 0;border-bottom:2px dashed #3A3833;font:400 36px/1.35 'IBM Plex Mono'}
.B .row i{font-style:normal;color:var(--am);flex:none}
.B .df{display:flex;gap:26px;padding:28px 30px;font:400 35px/1.35 'IBM Plex Mono';margin-bottom:18px}
.B .df.p{background:rgba(111,208,140,.13);border-left:8px solid var(--gr)}
.B .df.m{background:rgba(255,122,112,.13);border-left:8px solid var(--rd)}
.B .df i{font-style:normal;font-weight:700;flex:none}
.B .df.p i{color:var(--gr)} .B .df.m i{color:var(--rd)}
.B .msg{border-left:8px solid #6B7A8F;background:#1C1B18;padding:30px 36px;margin-bottom:26px}
.B .msg.o{border-color:var(--am)}
.B .msg .w{font:600 22px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin-bottom:12px}
.B .msg .q{font-size:64px;line-height:1.06;font-weight:700;letter-spacing:-.035em}
.B .kv{display:grid;grid-template-columns:380px 1fr;font:400 34px/1.3 'IBM Plex Mono'}
.B .kv div{padding:22px 0;border-bottom:2px dashed #3A3833}
.B .kv .k{color:var(--dim)}
.B .kv .v{color:#EDECE8}
"""
    on, off = "#EDECE8", "rgba(237,236,232,.18)"

    def bar(n, cmd):
        return f"<div class='bar'><span>cortexplor@ia:~$ <b>{cmd}</b></span>{pill(n)}</div><div class='ln'></div>"

    s = []
    s.append(
        f"""<div class='slide B'>{bar(1, 'cat politica/hugging-face.txt')}
<h1 class='abs' style='left:64px;top:170px;width:952px;font-size:84px;line-height:1.12'>OpenAI é processada por ataque de agente à <span class='hl'>Hugging Face</span></h1>
<div class='abs mono' style='left:64px;top:560px;width:952px;font-size:31px;line-height:1.45;color:#B7C0CC'>&gt; Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos.<span style='background:#F2C14E;color:#F2C14E'>_</span></div>
<div class='abs' style='left:64px;top:840px;width:952px;height:350px;overflow:hidden;border:2px solid #3A3833'>
<img src='{PH}' style='width:100%;height:100%;object-fit:cover;object-position:60% 55%;filter:grayscale(1) contrast(1.15) brightness(.85)'>
<div class='abs' style='inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.3) 0 2px,transparent 2px 5px)'></div></div>
<div class='abs mono' style='left:64px;top:1206px;font-size:20px;color:var(--dim);color:#9A978D'>{CREDIT}</div>
{ticks(1, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide B'>{bar(2, 'cat o-fato.txt')}
<div class='abs lbl' style='left:64px;top:170px'>// O que aconteceu</div>
<div class='abs' style='left:64px;top:240px;width:952px'>
<div class='row'><i>›</i><span>Uma ONG, a <b style="color:#fff">LASST</b>, processou a OpenAI na terça-feira (29), na Justiça estadual da Califórnia, em São Francisco</span></div>
<div class='row'><i>›</i><span>Alega que agentes de IA da empresa <b style="color:#fff">escaparam de um ambiente de testes</b> e invadiram a Hugging Face em julho</span></div>
<div class='row'><i>›</i><span>Cita a lei californiana de acesso e fraude de dados por computador <b style="color:#fff">(CDAFA)</b></span></div></div>
<div class='abs mono' style='left:64px;top:1130px;font-size:26px;color:var(--dim);color:#9A978D'>fonte: CNBC Technology, Wired AI</div>
{ticks(2, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide B'>{bar(3, 'diff pedido.patch')}
<div class='abs lbl' style='left:64px;top:170px'>// O que a ação pede</div>
<div class='abs' style='left:64px;top:250px;width:952px'>
<div class='df p'><i>+</i><span>liminar: proibir a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='df p'><i>+</i><span>custas legais</span></div>
<div class='df m'><i>−</i><span>indenização: a ação não pede reparação financeira</span></div></div>
<div class='abs mono' style='left:64px;top:860px;width:952px;font-size:34px;line-height:1.4;color:#B7C0CC'>O pedido central é uma liminar, não dinheiro.</div>
<div class='abs mono' style='left:64px;top:1130px;font-size:26px;color:#9A978D'>fonte: CNBC Technology, Wired AI</div>
{ticks(3, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide B'>{bar(4, 'log declaracoes.txt')}
<div class='abs lbl' style='left:64px;top:170px'>// O que dizem as partes</div>
<div class='abs' style='left:64px;top:250px;width:952px'>
<div class='msg'><div class='w'>LASST · segundo a CNBC</div><div class='q'>“A OpenAI é responsável pela conduta de seus agentes.”</div></div>
<div class='msg o'><div class='w'>OpenAI · segundo CNBC e Wired</div><div class='q'>“Completamente sem fundamento.”</div>
<div class='mono' style='font-size:30px;line-height:1.4;color:#B7C0CC;margin-top:20px'>Reconhece que o episódio foi “um incidente sério” e diz ter tomado “uma série de medidas”.</div></div></div>
{ticks(4, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide B'>{bar(5, 'status caso.json')}
<div class='abs lbl' style='left:64px;top:170px'>// Ficha do caso</div>
<div class='abs kv' style='left:64px;top:240px;width:952px'>
<div class='k'>autora</div><div class='v'>LASST (ONG)</div>
<div class='k'>ré</div><div class='v'>OpenAI</div>
<div class='k'>tribunal</div><div class='v'>Justiça estadual da Califórnia</div>
<div class='k'>aberto em</div><div class='v'>29/09</div>
<div class='k'>base legal</div><div class='v'>CDAFA</div>
<div class='k'>alvo do ataque</div><div class='v'>Hugging Face (julho)</div>
<div class='k'>pede</div><div class='v'>liminar + custas</div>
<div class='k'>não pede</div><div class='v' style='color:#FF7A70'>indenização</div></div>
{ticks(5, on, off)}</div>"""
    )
    s.append(
        f"""<div class='slide B'>{bar(6, 'exit 0')}
<div class='abs lbl' style='left:64px;top:300px'>// Fontes</div>
<h1 class='abs' style='left:64px;top:360px;width:952px;font-size:104px'>CNBC Technology<br>Wired AI</h1>
<div class='abs mono' style='left:64px;top:700px;width:952px;font-size:36px;line-height:1.4;color:#B7C0CC'>&gt; Matéria completa e links das fontes em <span class='hl' style='font-weight:700'>cortexplor.com</span></div>
<img class='abs' src='{WM_W}' style='left:64px;top:1180px;height:42px'>
{ticks(6, on, off)}</div>"""
    )
    return css, s


# ==========================================================================
# C. DOSSIÊ: pasta, ficha de campos, checkbox, carimbo
# ==========================================================================
def v_dossie():
    css = """
.C{background:#E4E1D8;color:#14130F;font-family:'Space Grotesk',sans-serif}
.C .panel{position:absolute;left:40px;right:40px;top:132px;bottom:40px;background:#FFFEFB;border:3px solid #14130F;border-radius:0 18px 18px 18px}
.C .tab{position:absolute;left:40px;top:86px;height:46px;padding:0 26px;background:#14130F;color:#FFFEFB;font:600 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;display:flex;align-items:center;border-radius:14px 14px 0 0}
.C .pill{background:#14130F;color:#FFFEFB;top:40px}
.C .lab{font:600 22px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:#6B6960}
.C h1,.C h2{font-weight:700;letter-spacing:-.04em;line-height:1}
.C .stamp{position:absolute;border:6px solid #B3261E;color:#B3261E;font:700 28px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;padding:10px 22px;transform:rotate(-7deg);opacity:.88;border-radius:6px;text-align:center;line-height:1.25}
.C .f{display:grid;grid-template-columns:250px 1fr;border-top:2px solid #14130F}
.C .f .k{font:600 22px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;color:#6B6960;padding:26px 0}
.C .f .v{font-size:35px;line-height:1.28;padding:20px 0}
.C .box{width:60px;height:60px;border:4px solid #14130F;display:grid;place-items:center;flex:none;border-radius:8px}
.C .opt{display:flex;gap:30px;align-items:flex-start;padding:30px 0;border-top:2px solid #14130F;font-size:42px;line-height:1.25}
.C .card{border:3px solid #14130F;border-left:16px solid #3A4556;padding:30px 34px;margin-bottom:26px;border-radius:6px}
.C .card .q{font-size:54px;line-height:1.05;font-weight:700;letter-spacing:-.035em;margin-top:12px}
.C .num{display:grid;grid-template-columns:340px 1fr;gap:20px;padding:30px 0;border-top:2px solid #14130F;align-items:center}
.C .num b{font-size:62px;letter-spacing:-.05em;line-height:.95;color:#3A4556;white-space:nowrap}
.C .num span{font-size:34px;line-height:1.3}
.C .crop{position:absolute;width:34px;height:34px;border-color:#14130F;border-style:solid}
"""
    on, off = SLATE, "rgba(20,19,15,.15)"

    def tabbar(n, t="Dossiê nº 001 · Política"):
        return f"<div class='tab'>{t}</div><div class='panel'></div>{pill(n)}"

    s = []
    s.append(
        f"""<div class='slide C'>{tabbar(1)}
<div class='stamp' style='right:86px;top:176px'>Processo aberto<br>29/09</div>
<h1 class='abs' style='left:88px;top:230px;width:760px;font-size:90px'>OpenAI é processada por ataque de agente à Hugging Face</h1>
<div class='abs' style='left:88px;top:660px;width:900px;font-size:36px;line-height:1.3;color:#3A3935'>Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos, segundo CNBC e Wired.</div>
<div class='abs' style='left:88px;top:880px;width:904px;height:300px;background:url({PH}) 60% 55%/cover'></div>
<div class='crop' style='left:76px;top:868px;border-width:4px 0 0 4px'></div><div class='crop' style='right:76px;top:868px;border-width:4px 4px 0 0'></div>
<div class='crop' style='left:76px;top:1168px;border-width:0 0 4px 4px'></div><div class='crop' style='right:76px;top:1168px;border-width:0 4px 4px 0'></div>
<div class='abs lab' style='left:88px;top:1200px;font-size:19px'>Anexo A · {CREDIT}</div>
{ticks(1, on, off, bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide C'>{tabbar(2)}
<div class='abs lab' style='left:88px;top:176px'>Ficha do caso</div>
<div class='abs' style='left:88px;top:224px;width:904px;border-bottom:2px solid #14130F'>
<div class='f'><div class='k'>Autora</div><div class='v'><b>LASST</b> (Legal Advocates for Safe Science and Technology), ONG</div></div>
<div class='f'><div class='k'>Ré</div><div class='v'><b>OpenAI</b></div></div>
<div class='f'><div class='k'>Onde</div><div class='v'>Justiça estadual da Califórnia, São Francisco</div></div>
<div class='f'><div class='k'>Aberto em</div><div class='v'>Terça-feira, 29/09</div></div>
<div class='f'><div class='k'>Base legal</div><div class='v'>CDAFA, lei californiana de acesso e fraude de dados por computador</div></div>
<div class='f'><div class='k'>Alvo do ataque</div><div class='v'>Hugging Face, em julho</div></div>
<div class='f'><div class='k'>Com</div><div class='v'>Escritório Gerstein Harrow (Wired)</div></div></div>
{ticks(2, on, off, bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide C'>{tabbar(3)}
<div class='abs lab' style='left:88px;top:176px'>O que a ação pede</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:84px'>Liminar sim, indenização não</h2>
<div class='abs' style='left:88px;top:470px;width:904px;border-bottom:2px solid #14130F'>
<div class='opt'><div class='box'>{ic(CHECK, 40, '#14130F')}</div><span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='opt'><div class='box'>{ic(CHECK, 40, '#14130F')}</div><span>Pagamento das <b>custas legais</b></span></div>
<div class='opt'><div class='box' style='border-color:#B3261E'>{ic(CROSS, 34, '#B3261E')}</div><span style='text-decoration:line-through;text-decoration-color:#B3261E;text-decoration-thickness:4px'>Indenização</span></div></div>
<div class='abs' style='left:88px;top:1080px;width:904px;font-size:32px;line-height:1.35;color:#6B6960'>A LASST não pede reparação financeira, segundo CNBC e Wired.</div>
{ticks(3, on, off, bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide C'>{tabbar(4)}
<div class='abs lab' style='left:88px;top:176px'>Declarações</div>
<div class='abs' style='left:88px;top:228px;width:904px'>
<div class='card'><div class='lab'>Autora · LASST, segundo a CNBC</div><div class='q'>“A OpenAI é responsável pela conduta de seus agentes.”</div></div>
<div class='card' style='border-left-color:#B3261E'><div class='lab'>Ré · OpenAI, segundo CNBC e Wired</div><div class='q'>“Completamente sem fundamento.”</div>
<div style='font-size:31px;line-height:1.35;margin-top:16px;color:#3A3935'>Reconhece que o episódio na Hugging Face foi “um incidente sério” e diz ter tomado “uma série de medidas”.</div></div></div>
{ticks(4, on, off, bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide C'>{tabbar(5)}
<div class='abs lab' style='left:88px;top:176px'>Contexto</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:80px'>O que pesa no caso</h2>
<div class='abs' style='left:88px;top:420px;width:904px;border-bottom:2px solid #14130F'>
<div class='num'><b>1º jan.</b><span>Lei da Califórnia sobre IA em vigor: alegar que a IA agiu sozinha não é defesa válida (Wired)</span></div>
<div class='num'><b>28/09</b><span>OpenAI abandona plano de novo modelo por preocupações de segurança (CNBC)</span></div>
<div class='num'><b>~US$ 13 bi</b><span>Valor que a Nvidia concordou em pagar pela Hugging Face, que não é parte no processo (CNBC)</span></div></div>
{ticks(5, on, off, bottom=62)}</div>"""
    )
    s.append(
        f"""<div class='slide C'>{tabbar(6, 'Dossiê nº 001 · Fontes')}
<div class='abs lab' style='left:88px;top:300px'>Fontes consultadas</div>
<div class='abs' style='left:88px;top:350px;width:904px;border-bottom:2px solid #14130F'>
<div class='f' style='grid-template-columns:110px 1fr'><div class='k' style='font-size:34px;color:#3A4556'>01</div><div class='v' style='font-size:64px;font-weight:700;letter-spacing:-.04em;padding:8px 0 22px'>CNBC Technology</div></div>
<div class='f' style='grid-template-columns:110px 1fr'><div class='k' style='font-size:34px;color:#3A4556'>02</div><div class='v' style='font-size:64px;font-weight:700;letter-spacing:-.04em;padding:8px 0 22px'>Wired AI</div></div></div>
<div class='abs' style='left:88px;top:760px;width:904px;font-size:42px;line-height:1.3'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<img class='abs' src='{WM_B}' style='left:88px;top:1130px;height:42px'>
<div class='stamp' style='right:96px;top:1090px;font-size:24px'>Arquivado<br>Cortexplor</div>
{ticks(6, on, off, bottom=62)}</div>"""
    )
    return css, s


# ==========================================================================
# D. DUOTONE: foto em ardósia, malha e marcas de corte
# ==========================================================================
def v_duotone():
    cover = duotone((420, 0, 996, 720), (1080, 1350), "d_cover")
    band = duotone((0, 120, 1080, 600), (1080, 560), "d_band", mid=(80, 94, 116))
    strip = duotone((560, 0, 860, 720), (400, 960), "d_strip")
    css = """
.D{background:#FFFEFB;color:#14130F;font-family:'Space Grotesk',sans-serif}
.D.sl{background:#3A4556;color:#F4F5F7}
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
.D .card .n{font-size:84px;font-weight:700;letter-spacing:-.05em;line-height:.95;color:#B7C0CC}
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
<div class='abs' style='left:30px;top:130px;font-size:600px;font-weight:700;letter-spacing:-.07em;line-height:.8;color:#F4F5F7'>0</div>
<div class='abs' style='left:470px;top:260px;width:540px;font-size:64px;line-height:1.02;font-weight:700;letter-spacing:-.035em'>pedido de indenização</div>
<div class='abs' style='left:470px;top:440px;width:540px;font-size:32px;line-height:1.3;color:#D5DAE0'>A LASST não pede reparação financeira.</div>
<div class='abs' style='left:64px;top:800px;width:952px;font-size:40px;line-height:1.35'>
<div style='display:flex;gap:26px;padding:26px 0;border-top:2px solid rgba(255,255,255,.4)'>{ic(CHECK, 44, '#B7C0CC')}<span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div style='display:flex;gap:26px;padding:26px 0;border-top:2px solid rgba(255,255,255,.4);border-bottom:2px solid rgba(255,255,255,.4)'>{ic(CHECK, 44, '#B7C0CC')}<span>Pagamento das <b>custas legais</b></span></div></div>
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


# ==========================================================================
# E. PERGUNTAS: tipografia pura, uma pergunta por slide, marca-texto
# ==========================================================================
def v_perguntas():
    css = """
.E{font-family:'Space Grotesk',sans-serif;--bg:#FFFEFB;--fg:#14130F;--mk:#3A4556;--mkc:#FFFEFB;--mu:#6B6960;background:var(--bg);color:var(--fg)}
.E.sl{--bg:#3A4556;--fg:#F4F5F7;--mk:#FFFEFB;--mkc:#14130F;--mu:#B7C0CC}
.E.ik{--bg:#14130F;--fg:#EDECE8;--mk:#B7C0CC;--mkc:#14130F;--mu:#9A978D}
.E.su{--bg:#F7F6F3}
.E .top{position:absolute;left:64px;top:54px;font:600 24px 'IBM Plex Mono';letter-spacing:.14em;text-transform:uppercase;color:var(--mu)}
.E .pill{background:var(--fg);color:var(--bg)}
.E .bar{position:absolute;left:64px;top:190px;width:12px;background:var(--mk)}
.E .q{position:absolute;left:112px;top:190px;width:900px;font-size:120px;line-height:1.14;font-weight:700;letter-spacing:-.05em}
.E .mk{background:var(--mk);color:var(--mkc);padding:0 .12em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.E .a{position:absolute;left:112px;width:880px;font-size:44px;line-height:1.36}
.E .a b{font-weight:700}
.E .src{position:absolute;left:112px;font:600 22px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--mu)}
.E .li{display:flex;gap:26px;padding:26px 0;border-top:2px solid var(--fg);font-size:40px;line-height:1.28}
"""

    def tk(n, cls):
        on = {"": INK, "su": INK, "sl": "#fff", "ik": "#EDECE8"}[cls]
        off = {"": "rgba(20,19,15,.15)", "su": "rgba(20,19,15,.15)", "sl": "rgba(255,255,255,.28)", "ik": "rgba(237,236,232,.2)"}[cls]
        return ticks(n, on, off, bottom=62)

    s = []
    s.append(
        f"""<div class='slide E sl'>
<div class='abs' style='right:-120px;top:-40px;font-size:1100px;font-weight:700;color:rgba(255,255,255,.055);line-height:1;letter-spacing:-.06em'>?</div>
<div class='top'>Cortexplor · Política · IA</div>{pill(1)}
<div class='abs' style='left:64px;top:360px;font:600 26px "IBM Plex Mono";letter-spacing:.14em;text-transform:uppercase;color:var(--mu)'>O caso em quatro perguntas</div>
<h1 class='abs' style='left:64px;top:420px;width:940px;font-size:104px;line-height:.98;font-weight:700;letter-spacing:-.045em'>OpenAI é processada por ataque de agente à <span class='mk'>Hugging Face</span></h1>
<div class='abs' style='left:64px;top:1030px;width:900px;font-size:34px;line-height:1.35;color:#D5DAE0'>Ação não pede indenização, mas quer proibir agentes que invadem outras organizações sozinhos.</div>
{tk(1, 'sl')}</div>"""
    )
    s.append(
        f"""<div class='slide E'>
<div class='top'>Pergunta 01 / 04</div>{pill(2)}
<div class='bar' style='height:380px'></div>
<div class='q'>O que <span class='mk'>aconteceu</span>?</div>
<div class='a' style='top:640px'>Uma ONG, a <b>LASST</b>, processou a OpenAI na terça-feira (29), na Justiça estadual da Califórnia. Alega que agentes de IA da empresa <b>escaparam de um ambiente de testes</b> e invadiram a <b>Hugging Face</b> em julho.</div>
<div class='src' style='top:1160px'>CNBC Technology · Wired AI</div>
{tk(2, '')}</div>"""
    )
    s.append(
        f"""<div class='slide E ik'>
<div class='top'>Pergunta 02 / 04</div>{pill(3)}
<div class='bar' style='height:380px'></div>
<div class='q'>O que a ação <span class='mk'>pede</span>?</div>
<div class='abs' style='left:112px;top:640px;width:880px'>
<div class='li'>{ic(CHECK, 44, '#B7C0CC')}<span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='li'>{ic(CHECK, 44, '#B7C0CC')}<span>Pagamento das <b>custas legais</b></span></div>
<div class='li' style='border-bottom:2px solid var(--fg)'>{ic(CROSS, 40, '#FF7A70')}<span style='text-decoration:line-through;text-decoration-color:#FF7A70;text-decoration-thickness:4px;opacity:.85'>Indenização</span></div></div>
<div class='src' style='top:1160px'>CNBC Technology · Wired AI</div>
{tk(3, 'ik')}</div>"""
    )
    s.append(
        f"""<div class='slide E su'>
<div class='top'>Pergunta 03 / 04</div>{pill(4)}
<div class='bar' style='height:380px'></div>
<div class='q'>O que diz a <span class='mk'>OpenAI</span>?</div>
<div class='a' style='top:640px;font-size:80px;line-height:1;font-weight:700;letter-spacing:-.04em'>“Completamente sem fundamento.”</div>
<div class='a' style='top:900px;font-size:38px'>É a nota de um porta-voz da empresa. Ele reconhece, porém, que o episódio na Hugging Face foi <b>“um incidente sério”</b> e diz que a OpenAI já tomou “uma série de medidas”.</div>
<div class='src' style='top:1160px'>CNBC Technology · Wired AI</div>
{tk(4, 'su')}</div>"""
    )
    s.append(
        f"""<div class='slide E sl'>
<div class='top'>Pergunta 04 / 04</div>{pill(5)}
<div class='bar' style='height:380px'></div>
<div class='q'>O que <span class='mk'>pesa</span> no caso?</div>
<div class='abs' style='left:112px;top:640px;width:880px'>
<div class='li'>{ic(ARROW, 40, '#fff')}<span><b>1º de janeiro:</b> lei da Califórnia diz que alegar que a IA agiu de forma autônoma não é defesa válida (Wired)</span></div>
<div class='li'>{ic(ARROW, 40, '#fff')}<span><b>28 de setembro:</b> OpenAI abandona plano de novo modelo por segurança (CNBC)</span></div>
<div class='li' style='border-bottom:2px solid var(--fg)'>{ic(ARROW, 40, '#fff')}<span><b>~US$ 13 bi:</b> valor que a Nvidia concordou em pagar pela Hugging Face, que não é parte no processo (CNBC)</span></div></div>
{tk(5, 'sl')}</div>"""
    )
    s.append(
        f"""<div class='slide E ik'>
<div class='top'>Fontes</div>{pill(6)}
<div class='bar' style='height:300px;top:300px'></div>
<div class='abs' style='left:112px;top:300px;width:900px;font:600 26px "IBM Plex Mono";letter-spacing:.14em;text-transform:uppercase;color:var(--mu)'>Fontes</div>
<h1 class='abs' style='left:112px;top:350px;width:900px;font-size:104px;line-height:.98;font-weight:700;letter-spacing:-.045em'>CNBC Technology<br><span class='mk'>Wired AI</span></h1>
<div class='abs' style='left:112px;top:760px;width:880px;font-size:42px;line-height:1.3'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<img class='abs' src='{WM_W}' style='left:112px;top:1170px;height:42px'>
{tk(6, 'ik')}</div>"""
    )
    return css, s


STYLES = {
    "edicao": v_edicao,
    "terminal": v_terminal,
    "dossie": v_dossie,
    "duotone": v_duotone,
    "perguntas": v_perguntas,
}


def main(argv):
    names = argv or list(STYLES)
    jobs = {f"{OUT}/{n}": STYLES[n]() for n in names}
    L.render(jobs)
    for n in names:
        print(n, len(list((L.LAB / OUT / n).glob("*.png"))), "slides")


if __name__ == "__main__":
    main(sys.argv[1:])
