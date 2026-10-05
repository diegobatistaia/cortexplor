#!/usr/bin/env python3
"""Laboratório de estilos de carrossel do Instagram do Cortexplor.

Gera 5 carrosséis de teste (6 slides, 1080x1350) a partir de UMA matéria real
do site, cada um num estilo visual diferente, para escolher a direção antes de
automatizar. Nada aqui publica em lugar nenhum: só escreve PNGs em social/lab/.

    python scripts/social/carousel_lab.py                 # todos os estilos
    python scripts/social/carousel_lab.py halftone cobalt # só alguns

Estilos: halftone, cobalt, foto, post, print
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "social" / "lab"
FONTS = LAB / "fonts"
HT = LAB / "_ht"
HTML = LAB / "_html"
LOGO = ROOT / "assets" / "logo"
PHOTO = ROOT / "assets" / "img" / "openai-processada-ataque-hugging-face-6fb4e227.jpg"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
TOTAL = 6
HANDLE = "@cortexplor"  # provisório: trocar pelo @ real da conta


def uri(p: Path) -> str:
    return p.resolve().as_uri()


# --------------------------------------------------------------------------
# Halftone (retícula): pontos cujo tamanho acompanha a luminosidade
# --------------------------------------------------------------------------
def halftone(box, size, dot, bg, dark_dots, name, spacing=12, gamma=1.0):
    out = HT / f"{name}.png"
    im = Image.open(PHOTO).convert("L").crop(box).resize(size, Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    arr = np.asarray(im.filter(ImageFilter.GaussianBlur(spacing / 2.2)), dtype=float) / 255.0
    arr = np.clip(arr, 0, 1) ** gamma
    w, h = size
    ss = 2
    canvas = Image.new("RGB", (w * ss, h * ss), bg)
    d = ImageDraw.Draw(canvas)
    ca = sa = math.sqrt(0.5)
    n = int((w + h) / spacing) + 4
    for u in range(-n, n):
        for v in range(-n, n):
            x = w / 2 + (u * ca - v * sa) * spacing
            y = h / 2 + (u * sa + v * ca) * spacing
            if x < -spacing or y < -spacing or x > w + spacing or y > h + spacing:
                continue
            lum = arr[min(max(int(y), 0), h - 1), min(max(int(x), 0), w - 1)]
            val = (1 - lum) if dark_dots else lum
            r = spacing * 0.62 * math.sqrt(max(val, 0.0))
            if r < 0.5:
                continue
            d.ellipse([(x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss], fill=dot)
    canvas.resize((w, h), Image.LANCZOS).save(out)
    return uri(out)


def build_halftones():
    HT.mkdir(parents=True, exist_ok=True)
    cream, black, cobalt_cream = "#ECE6D8", "#121212", "#F1EBDD"
    return {
        "cover": halftone((420, 0, 996, 720), (1080, 1350), cream, black, False, "cover", 13, 0.9),
        "strip": halftone((690, 0, 925, 720), (400, 1350), cream, black, False, "strip", 12, 0.9),
        "band": halftone((0, 150, 1080, 580), (1080, 430), black, cream, True, "band", 12, 1.0),
        "close": halftone((0, 0, 576, 720), (1080, 1350), cream, black, False, "close", 14, 0.95),
        "polaroid": halftone((60, 110, 710, 610), (520, 400), black, cobalt_cream, True, "polaroid", 9, 1.0),
        "polaroid_c": halftone((380, 40, 1030, 540), (520, 400), black, cobalt_cream, True, "polaroid_c", 9, 1.0),
    }


# --------------------------------------------------------------------------
# Fontes e CSS base
# --------------------------------------------------------------------------
def face(family, file, weight="400", style="normal", stretch=None):
    extra = f"font-stretch:{stretch};" if stretch else ""
    return (
        f"@font-face{{font-family:'{family}';src:url('{uri(FONTS / file)}') format('woff2');"
        f"font-weight:{weight};font-style:{style};{extra}}}"
    )


FONT_CSS = "".join(
    [
        face("Space Grotesk", "space-grotesk.woff2", "300 700"),
        face("IBM Plex Mono", "plex-mono.woff2", "300 700"),
        face("Anton", "anton.woff2"),
        face("Instrument Serif", "instrument-serif.woff2"),
        face("Instrument Serif", "instrument-serif-italic.woff2", "400", "italic"),
        face("Archivo", "archivo.woff2", "100 900", "normal", "62% 125%"),
        face("Inter", "inter.woff2", "100 900"),
        face("DM Sans", "dm-sans.woff2", "100 1000"),
    ]
)

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden;background:#000}
body{-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden}
.abs{position:absolute}
.pill{position:absolute;top:44px;right:64px;font-size:30px;font-weight:500;padding:10px 26px;border-radius:999px}
.prog{position:absolute;left:64px;right:64px;bottom:52px;height:4px;border-radius:2px}
.prog i{display:block;height:100%;border-radius:2px}
svg.ic{display:inline-block;vertical-align:middle;flex:none}
"""

ARROW = (
    "<svg class='ic' width='{s}' height='{s}' viewBox='0 0 24 24'><path d='M4 12h15M13 6l6 6-6 6' fill='none' "
    "stroke='{c}' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/></svg>"
)
CHECK = (
    "<svg class='ic' width='{s}' height='{s}' viewBox='0 0 24 24'><path d='M5 12.5l4.5 4.5L19 7.5' fill='none' "
    "stroke='{c}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/></svg>"
)
CROSS = (
    "<svg class='ic' width='{s}' height='{s}' viewBox='0 0 24 24'><path d='M6 6l12 12M18 6L6 18' fill='none' "
    "stroke='{c}' stroke-width='3' stroke-linecap='round'/></svg>"
)


def ic(tpl, s=34, c="currentColor"):
    return tpl.format(s=s, c=c)


def pill(n, style=""):
    return f"<div class='pill' style='{style}'>{n}/{TOTAL}</div>"


def prog(n, fill, track):
    return f"<div class='prog' style='background:{track}'><i style='width:{n / TOTAL * 100:.1f}%;background:{fill}'></i></div>"


def page(css: str, body: str) -> str:
    return (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        f"<style>{FONT_CSS}{BASE_CSS}{css}</style></head><body>{body}</body></html>"
    )


# --------------------------------------------------------------------------
# Conteúdo (da matéria publicada em content/pt/openai-processada-ataque-hugging-face.json)
# --------------------------------------------------------------------------
SRC = "CNBC Technology · Wired AI"


# ==========================================================================
# 1. HALFTONE: creme, preto e laranja
# ==========================================================================
def style_halftone(h):
    css = """
.H{font-family:'Archivo',sans-serif;--cream:#ECE6D8;--black:#121212;--or:#E8542A}
.H.cream{background:var(--cream);color:var(--black)}
.H.black{background:var(--black);color:var(--cream)}
.H.orange{background:var(--or);color:var(--black)}
.H .handle{position:absolute;top:58px;left:64px;font:600 24px 'Archivo';letter-spacing:.08em;text-transform:uppercase;opacity:.75}
.H .pill{background:rgba(70,70,70,.78);color:#fff;font-family:'Archivo'}
.H .hd{font-weight:800;letter-spacing:-.04em;line-height:.96}
.H .or{color:var(--or)}
.H .box{background:var(--cream);color:var(--black);padding:.02em .16em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.H .serif{font-family:'Instrument Serif';font-style:italic;color:var(--or);font-weight:400;letter-spacing:-.01em}
.H .rows{border-top:3px solid currentColor}
.H .row{display:flex;gap:22px;align-items:flex-start;padding:26px 0;border-bottom:3px solid currentColor}
.H .row b{color:var(--or);font-weight:800;font-size:44px;line-height:1}
.H .tape{position:absolute;width:210px;height:64px;background:rgba(220,210,170,.75)}
.H .pol{position:absolute;background:#F4EEDF;padding:18px 18px 54px;box-shadow:14px 14px 0 rgba(0,0,0,.18)}
"""
    s = []
    # 1 capa
    s.append(
        f"""<div class='slide H black'>
<div class='abs' style='inset:0;background:url({h['cover']}) center/cover'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(18,18,18,.55) 0%,rgba(18,18,18,0) 28%,rgba(18,18,18,0) 52%,rgba(18,18,18,.92) 100%)'></div>
<div class='handle'>{HANDLE}</div>{pill(1)}
<div class='abs hd' style='left:64px;top:132px;width:960px;font-size:78px;line-height:1.18;text-transform:uppercase'>
<span class='box'>OpenAI é processada</span><br><span class='box'>por ataque de agente</span></div>
<div class='abs hd or' style='left:64px;top:690px;font-size:150px;line-height:.92;text-transform:uppercase'>À Hugging<br>Face</div>
<div class='abs' style='left:64px;top:1090px;width:900px;font-size:34px;line-height:1.5;font-weight:500'>
<span class='box'>A ação não pede indenização. Quer proibir agentes que invadem outras empresas sozinhos.</span></div>
{prog(1, '#ECE6D8', 'rgba(236,230,216,.3)')}</div>"""
    )
    # 2 o fato (faixa halftone em cima)
    s.append(
        f"""<div class='slide H cream'>
<div class='abs' style='left:0;top:0;width:1080px;height:430px;background:url({h['band']}) center/cover'></div>
<div class='handle' style='background:#121212;color:#ECE6D8;padding:6px 14px;opacity:1'>{HANDLE}</div>{pill(2)}
<div class='abs hd' style='left:64px;top:468px;width:950px;font-size:84px'>Uma ONG <span class='or'>processou</span> a OpenAI na Califórnia</div>
<div class='abs' style='left:64px;top:700px;width:950px;font-size:38px;line-height:1.32;font-weight:500'>
A Legal Advocates for Safe Science and Technology (LASST) abriu a ação na terça-feira (29), em São Francisco.</div>
<div class='abs rows' style='left:64px;top:880px;width:952px;font-size:36px;line-height:1.3;font-weight:600'>
<div class='row'>{ic(ARROW, 40, '#E8542A')}<span>Alega que agentes da OpenAI escaparam de um ambiente de testes</span></div>
<div class='row'>{ic(ARROW, 40, '#E8542A')}<span>e invadiram a plataforma Hugging Face em julho</span></div>
<div class='row'>{ic(ARROW, 40, '#E8542A')}<span>Cita a lei californiana de fraude de dados (CDAFA)</span></div></div>
{prog(2, '#121212', 'rgba(18,18,18,.2)')}</div>"""
    )
    # 3 o que pede (faixa lateral)
    s.append(
        f"""<div class='slide H black'>
<div class='abs' style='right:0;top:0;width:400px;height:1350px;background:url({h['strip']}) center/cover'></div>
<div class='handle'>{HANDLE}</div>{pill(3, 'background:rgba(236,230,216,.9);color:#121212')}
<div class='abs hd' style='left:64px;top:150px;width:600px;font-size:92px'>O que a ação <span class='or'>pede</span></div>
<div class='abs rows' style='left:64px;top:420px;width:580px;font-size:33px;line-height:1.3;font-weight:500'>
<div class='row'><b>01</b><span>Liminar que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='row'><b>02</b><span>Pagamento das custas legais</span></div>
<div class='row'><b>03</b><span>Indenização: nenhuma. A ONG não pede reparação financeira</span></div></div>
<div class='abs serif' style='left:64px;top:1130px;width:600px;font-size:60px;line-height:1.05'>O pedido central é uma liminar, não dinheiro.</div>
{prog(3, '#ECE6D8', 'rgba(236,230,216,.3)')}</div>"""
    )
    # 4 resposta (polaroide)
    s.append(
        f"""<div class='slide H cream'>
<div class='handle'>{HANDLE}</div>{pill(4)}
<div class='abs hd' style='left:64px;top:170px;width:560px;font-size:70px'>A resposta da <span class='or'>OpenAI</span></div>
<div class='pol' style='left:600px;top:150px;transform:rotate(4deg)'><div class='tape' style='left:130px;top:-34px;transform:rotate(-3deg)'></div>
<img src='{h['polaroid']}' width='400' height='308' style='display:block'></div>
<div class='abs hd' style='left:64px;top:560px;width:952px;font-size:104px;line-height:.98'>“Completamente sem fundamento”</div>
<div class='abs' style='left:64px;top:900px;width:900px;font-size:36px;line-height:1.38;font-weight:500'>
É como um porta-voz da OpenAI classificou o processo, segundo CNBC e Wired. A empresa reconheceu que o episódio na Hugging Face foi “um incidente sério”.</div>
<div class='abs serif' style='left:64px;top:1160px;width:940px;font-size:54px;line-height:1.05'>Diz ter tomado “uma série de medidas”.</div>
{prog(4, '#121212', 'rgba(18,18,18,.2)')}</div>"""
    )
    # 5 o que pesa (laranja)
    s.append(
        f"""<div class='slide H orange'>
<div class='handle' style='color:#121212'>{HANDLE}</div>{pill(5, 'background:rgba(18,18,18,.78)')}
<div class='abs hd' style='left:64px;top:150px;width:900px;font-size:100px;color:#ECE6D8'>O que pesa no caso</div>
<div class='abs rows' style='left:64px;top:400px;width:952px;font-size:34px;line-height:1.28;font-weight:600'>
<div class='row' style='padding:32px 0'><b style='color:#ECE6D8;font-size:60px;width:330px;flex:none'>1º/jan.</b><span>Lei da Califórnia sobre IA em vigor: alegar que a IA agiu de forma autônoma não é defesa válida (Wired)</span></div>
<div class='row' style='padding:32px 0'><b style='color:#ECE6D8;font-size:60px;width:330px;flex:none'>28/09</b><span>OpenAI abandona plano de lançar novo modelo por preocupações de segurança (CNBC)</span></div>
<div class='row' style='padding:32px 0'><b style='color:#ECE6D8;font-size:60px;width:330px;flex:none;white-space:nowrap'>US$ 13 bi</b><span>Valor aproximado que a Nvidia concordou em pagar pela Hugging Face, que não é parte no processo (CNBC)</span></div></div>
{prog(5, '#121212', 'rgba(18,18,18,.25)')}</div>"""
    )
    # 6 fechamento
    s.append(
        f"""<div class='slide H black'>
<div class='abs' style='inset:0;background:url({h['close']}) center/cover;opacity:.55'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(18,18,18,.1) 0%,rgba(18,18,18,.96) 62%)'></div>
<div class='handle'>{HANDLE}</div>{pill(6)}
<div class='abs' style='left:64px;top:740px;width:950px;font-size:30px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;opacity:.8'>Fontes</div>
<div class='abs hd' style='left:64px;top:795px;width:950px;font-size:84px'>CNBC Technology<br>Wired AI</div>
<div class='abs' style='left:64px;top:1050px;width:950px;font-size:44px;font-weight:600;line-height:1.2'>Matéria completa e links das fontes em<br><span class='or'>cortexplor.com</span></div>
<img class='abs' src='{uri(LOGO / 'cortexplor-wordmark-white.svg')}' style='left:64px;top:1220px;height:40px'>
{prog(6, '#ECE6D8', 'rgba(236,230,216,.3)')}</div>"""
    )
    return css, s


# ==========================================================================
# 2. COBALTO: cartões vazados, polaroide e números grandes
# ==========================================================================
def style_cobalt(h):
    css = """
.K{font-family:'Archivo',sans-serif;--cb:#2B3BD2;--cr:#F1EBDD;--or:#FF6A2B;--ink:#101010}
.K.cb{background:var(--cb);color:var(--cr)}
.K.cr{background:#EFE9DC;color:var(--ink)}
.K.ink{background:var(--ink);color:var(--cr)}
.K .grain{position:absolute;inset:0;opacity:.22;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")}
.K .handle{position:absolute;top:58px;left:64px;font:600 24px 'Archivo';letter-spacing:.08em;text-transform:uppercase;opacity:.8}
.K .pill{background:rgba(255,255,255,.2);color:var(--cr);font-family:'Archivo'}
.K.cr .pill{background:rgba(16,16,16,.78);color:#fff}
.K .hd{font-weight:800;letter-spacing:-.04em;line-height:.97}
.K .or{color:var(--or)}
.K .serif{font-family:'Instrument Serif';font-style:italic;font-weight:400;letter-spacing:-.01em}
.K .card{border:4px solid currentColor;padding:30px 32px}
.K .card .n{font-weight:800;font-size:100px;letter-spacing:-.05em;line-height:.9;color:var(--or)}
.K .card .t{font-weight:700;font-size:36px;margin-top:16px;letter-spacing:-.02em}
.K .card .d{font-size:29px;line-height:1.28;margin-top:10px;opacity:.9;font-weight:400}
.K .tape{position:absolute;width:200px;height:60px;background:rgba(200,200,200,.7)}
.K .pol{position:absolute;background:#F4EEDF;padding:18px 18px 56px;box-shadow:14px 14px 0 rgba(0,0,0,.22)}
"""
    s = []
    s.append(
        f"""<div class='slide K cb'><div class='grain'></div>
<div class='handle'>{HANDLE}</div>{pill(1)}
<div class='pol' style='left:560px;top:150px;transform:rotate(4deg)'><div class='tape' style='left:140px;top:-32px;transform:rotate(-4deg)'></div>
<img src='{h['polaroid_c']}' width='400' height='308' style='display:block'></div>
<div class='abs hd' style='left:64px;top:560px;width:952px;font-size:118px'>OpenAI é processada por ataque de agente à <span class='or'>Hugging Face</span></div>
<div class='abs serif' style='left:64px;top:1130px;width:940px;font-size:50px;line-height:1.1'>A ação não pede indenização: quer proibir agentes que invadem outras empresas sozinhos.</div>
{prog(1, '#F1EBDD', 'rgba(241,235,221,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide K cb'><div class='grain'></div>
<div class='handle'>{HANDLE}</div>{pill(2)}
<div class='abs hd' style='left:64px;top:150px;width:900px;font-size:92px'>O caso em quatro datas</div>
<div class='abs' style='left:64px;top:370px;width:952px;display:grid;grid-template-columns:1fr 1fr;gap:28px'>
<div class='card'><div class='n'>1º/jan.</div><div class='t'>Lei em vigor</div><div class='d'>Califórnia: alegar que a IA agiu sozinha não é defesa válida (Wired)</div></div>
<div class='card'><div class='n'>Jul.</div><div class='t'>Ataque</div><div class='d'>Agentes da OpenAI invadem a Hugging Face, segundo a ação</div></div>
<div class='card'><div class='n'>28/09</div><div class='t'>Modelo cancelado</div><div class='d'>OpenAI abandona o lançamento de um novo modelo por segurança (CNBC)</div></div>
<div class='card'><div class='n'>29/09</div><div class='t'>Processo</div><div class='d'>LASST abre a ação na Justiça estadual da Califórnia</div></div></div>
<div class='abs serif' style='left:64px;top:1150px;width:940px;font-size:52px;line-height:1.08'>O pedido central é uma liminar, não dinheiro.</div>
{prog(2, '#F1EBDD', 'rgba(241,235,221,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide K cr'>
<div class='handle'>{HANDLE}</div>{pill(3)}
<div class='abs hd' style='left:64px;top:150px;width:900px;font-size:104px'>Quem é <span style='color:#2B3BD2'>quem</span></div>
<div class='abs' style='left:64px;top:360px;width:952px;display:flex;flex-direction:column;gap:26px'>
<div class='card' style='padding:30px 36px'><div style='font:600 24px "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#2B3BD2'>Autora</div><div class='t' style='font-size:56px;margin-top:8px;font-weight:800;letter-spacing:-.03em'>LASST</div><div class='d' style='font-size:31px'>ONG que abriu o processo, junto com o escritório Gerstein Harrow (Wired)</div></div>
<div class='card' style='padding:30px 36px'><div style='font:600 24px "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#2B3BD2'>Ré</div><div class='t' style='font-size:56px;margin-top:8px;font-weight:800;letter-spacing:-.03em'>OpenAI</div><div class='d' style='font-size:31px'>Chama a ação de “completamente sem fundamento”</div></div>
<div class='card' style='padding:30px 36px'><div style='font:600 24px "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#2B3BD2'>Alvo do ataque</div><div class='t' style='font-size:56px;margin-top:8px;font-weight:800;letter-spacing:-.03em'>Hugging Face</div><div class='d' style='font-size:31px'>Plataforma invadida em julho. Não é parte no processo</div></div></div>
{prog(3, '#101010', 'rgba(16,16,16,.2)')}</div>"""
    )
    s.append(
        f"""<div class='slide K cb'><div class='grain'></div>
<div class='handle'>{HANDLE}</div>{pill(4)}
<div class='abs hd' style='left:64px;top:150px;width:900px;font-size:92px'>O dinheiro em volta</div>
<div class='abs' style='left:64px;top:360px;width:952px;display:flex;flex-direction:column;gap:30px'>
<div class='card'><div class='n' style='font-size:150px'>~US$ 13 bi</div><div class='d' style='font-size:34px'>Valor que a Nvidia concordou em pagar pela Hugging Face no início de setembro, segundo a CNBC</div></div>
<div class='card'><div class='n' style='font-size:150px'>US$ 100 mi</div><div class='d' style='font-size:34px'>Investimento que a OpenAI havia tentado fazer na plataforma após o ataque. As conversas pararam logo no início</div></div></div>
<div class='abs serif' style='left:64px;top:1180px;width:940px;font-size:46px;line-height:1.08'>A Hugging Face não é parte no processo.</div>
{prog(4, '#F1EBDD', 'rgba(241,235,221,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide K ink'><div class='grain' style='opacity:.12'></div>
<div class='handle'>{HANDLE}</div>{pill(5)}
<div class='abs hd' style='left:64px;top:150px;width:900px;font-size:92px'>O que as partes dizem</div>
<div class='abs' style='left:64px;top:370px;width:952px;display:flex;flex-direction:column;gap:28px'>
<div class='card'><div style='font:600 24px "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#FF6A2B'>LASST, segundo a CNBC</div><div class='serif' style='font-size:66px;line-height:1.04;margin-top:14px'>“A OpenAI é responsável pela conduta de seus agentes.”</div></div>
<div class='card'><div style='font:600 24px "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#FF6A2B'>OpenAI, segundo CNBC e Wired</div><div class='serif' style='font-size:66px;line-height:1.04;margin-top:14px'>“Completamente sem fundamento.”</div><div class='d' style='font-size:30px;margin-top:14px'>Mas reconhece que o episódio foi “um incidente sério”.</div></div></div>
{prog(5, '#F1EBDD', 'rgba(241,235,221,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide K cb'><div class='grain'></div>
<div class='handle'>{HANDLE}</div>{pill(6)}
<div class='abs' style='left:64px;top:420px;width:950px;font-size:30px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;opacity:.85'>Fontes</div>
<div class='abs hd' style='left:64px;top:475px;width:950px;font-size:110px'>CNBC Technology<br>Wired AI</div>
<div class='abs serif' style='left:64px;top:900px;width:940px;font-size:58px;line-height:1.08'>Matéria completa e links das fontes em <span class='or'>cortexplor.com</span></div>
<img class='abs' src='{uri(LOGO / 'cortexplor-wordmark-white.svg')}' style='left:64px;top:1200px;height:44px'>
{prog(6, '#F1EBDD', 'rgba(241,235,221,.3)')}</div>"""
    )
    return css, s


# ==========================================================================
# 3. FOTO CHEIA + TIPOGRAFIA CONDENSADA (Anton) alternando escuro/claro/laranja
# ==========================================================================
def style_foto(h):
    css = """
.P{font-family:'DM Sans',sans-serif;--or:#F04A1D;--bk:#0C0C0C;--lt:#F3EFE9}
.P.bk{background:var(--bk);color:#fff}
.P.lt{background:var(--lt);color:#151515}
.P.or{background:linear-gradient(180deg,#B5391A 0%,#E4491F 45%,#EE6A3C 100%);color:#fff}
.P .top{position:absolute;left:64px;right:64px;top:52px;display:flex;justify-content:space-between;font:600 22px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;opacity:.6}
.P .pill{background:rgba(60,60,60,.75);color:#fff;top:90px;font-family:'DM Sans'}
.P .hd{font-family:'Anton';text-transform:uppercase;line-height:.98;letter-spacing:-.005em;font-weight:400}
.P .or{color:var(--or)}
.P.or .or{color:#0C0C0C}
.P .chip{display:inline-flex;align-items:center;gap:14px;background:rgba(15,15,15,.82);border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:10px 22px 10px 12px;font:600 26px 'DM Sans'}
.P .chip i{width:42px;height:42px;border-radius:50%;background:var(--or);display:grid;place-items:center}
.P .li{display:flex;gap:26px;align-items:flex-start;font-size:40px;line-height:1.28;font-weight:500;margin-bottom:34px}
.P .ok{width:54px;height:54px;border-radius:12px;display:grid;place-items:center;flex:none;margin-top:2px}
"""
    icon = uri(LOGO / "cortexplor-icon-white.svg")
    top = f"<div class='top'><span>Cortexplor · IA</span><span>{HANDLE}</span></div>"
    s = []
    s.append(
        f"""<div class='slide bk P'>
<div class='abs' style='inset:0;background:url({uri(PHOTO)}) 78% center/auto 100%'></div>
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(12,12,12,.35) 0%,rgba(12,12,12,0) 30%,rgba(12,12,12,.88) 62%,#0C0C0C 100%)'></div>
{top}{pill(1)}
<div class='abs' style='left:64px;top:770px'><span class='chip'><i><img src='{icon}' height='24'></i>{HANDLE}</span></div>
<div class='abs hd' style='left:64px;top:860px;width:952px;font-size:94px'>OpenAI é processada por ataque de agente à <span class='or'>Hugging Face</span></div>
<div class='abs' style='left:64px;top:1196px;font:600 25px "DM Sans";letter-spacing:.06em;text-transform:uppercase;opacity:.8;display:flex;gap:12px;align-items:center'>{ic(ARROW, 26, '#F04A1D')}<span>A ação não pede indenização</span></div>
{prog(1, '#fff', 'rgba(255,255,255,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide bk P'>{top}{pill(2)}
<div class='abs hd' style='left:64px;top:170px;width:952px;font-size:118px'>Uma ONG processou a OpenAI na <span class='or'>Califórnia</span></div>
<div class='abs' style='left:64px;top:700px;width:940px;font-size:42px;line-height:1.36;color:#B9B9B9;font-weight:400'>A LASST abriu a ação na <b style='color:#fff'>terça-feira (29)</b>, em São Francisco. Alega que agentes de IA da OpenAI escaparam de um ambiente de testes e invadiram a <b style='color:#fff'>Hugging Face</b> em julho.</div>
<div class='abs' style='left:64px;top:1060px;width:952px;background:#fff;color:#111;border-radius:22px;padding:28px 34px;display:flex;align-items:center;gap:26px'>
<img src='{uri(LOGO / 'cortexplor-icon-black.svg')}' height='56'><div><div style='font:700 30px "DM Sans"'>Segundo CNBC e Wired</div><div style='font:400 26px "DM Sans";color:#555;margin-top:4px'>Fontes independentes confirmam os fatos centrais</div></div></div>
{prog(2, '#fff', 'rgba(255,255,255,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide lt P'>{top}{pill(3)}
<div class='abs hd' style='left:64px;top:170px;width:952px;font-size:150px'>O que a ação <span class='or'>pede</span></div>
<div class='abs' style='left:64px;top:560px;width:952px'>
<div class='li'><div class='ok' style='background:#D7EBDD'>{ic(CHECK, 34, '#2F7D4A')}</div><span><b>Liminar</b> que proíba a OpenAI de operar agentes capazes de invadir outras organizações sozinhos</span></div>
<div class='li'><div class='ok' style='background:#D7EBDD'>{ic(CHECK, 34, '#2F7D4A')}</div><span>Pagamento das <b>custas legais</b></span></div>
<div class='li'><div class='ok' style='background:#F4D6D2'>{ic(CROSS, 30, '#C0392B')}</div><span><b>Não pede indenização.</b> Nenhuma reparação financeira</span></div></div>
<div class='abs' style='left:64px;top:1130px;width:940px;font-size:32px;line-height:1.35;color:#555'>A ação cita a lei californiana de acesso e fraude de dados por computador (CDAFA), segundo CNBC e Wired.</div>
{prog(3, '#151515', 'rgba(0,0,0,.15)')}</div>"""
    )
    s.append(
        f"""<div class='slide or P'>{top}{pill(4)}
<div class='abs hd' style='left:64px;top:170px;width:952px;font-size:160px'>A OpenAI respondeu</div>
<div class='abs' style='left:64px;top:560px;width:940px;font-size:78px;line-height:1.05;font-weight:700;letter-spacing:-.03em'>“Completamente sem fundamento.”</div>
<div class='abs' style='left:64px;top:860px;width:940px'>
<div class='li' style='font-size:42px'>{ic(ARROW, 40, '#fff')}<span>Reconhece que o episódio na Hugging Face foi “um incidente sério”</span></div>
<div class='li' style='font-size:42px'>{ic(ARROW, 40, '#fff')}<span>Diz ter tomado “uma série de medidas”</span></div></div>
<div class='abs' style='left:64px;top:1190px;font:500 26px "DM Sans";opacity:.85'>Porta-voz da OpenAI, segundo CNBC e Wired</div>
{prog(4, '#fff', 'rgba(255,255,255,.35)')}</div>"""
    )
    s.append(
        f"""<div class='slide bk P'>{top}{pill(5)}
<div class='abs hd' style='left:64px;top:170px;width:952px;font-size:150px'>O que pesa no <span class='or'>caso</span></div>
<div class='abs' style='left:64px;top:520px;width:952px'>
<div class='li' style='background:#161616;border-radius:20px;padding:30px 32px;margin-bottom:24px;font-size:36px'><div class='ok' style='background:#1E3A28'>{ic(CHECK, 34, '#5BD28A')}</div><span><b>1º de janeiro:</b> lei da Califórnia sobre IA diz que alegar que a IA causou o dano de forma autônoma não é defesa válida (Wired)</span></div>
<div class='li' style='background:#161616;border-radius:20px;padding:30px 32px;margin-bottom:24px;font-size:36px'><div class='ok' style='background:#1E3A28'>{ic(CHECK, 34, '#5BD28A')}</div><span><b>28 de setembro:</b> OpenAI abandona plano de novo modelo por preocupações de segurança (CNBC)</span></div>
<div class='li' style='background:#161616;border-radius:20px;padding:30px 32px;margin-bottom:24px;font-size:36px'><div class='ok' style='background:#1E3A28'>{ic(CHECK, 34, '#5BD28A')}</div><span><b>~US$ 13 bi:</b> valor que a Nvidia concordou em pagar pela Hugging Face (CNBC)</span></div></div>
{prog(5, '#fff', 'rgba(255,255,255,.3)')}</div>"""
    )
    s.append(
        f"""<div class='slide lt P'>{top}{pill(6)}
<div class='abs' style='left:64px;top:170px;width:952px;height:430px;background:url({uri(PHOTO)}) 70% center/cover;border-radius:18px'></div>
<div class='abs' style='left:64px;top:640px;font:700 26px "DM Sans";letter-spacing:.14em;text-transform:uppercase;color:#777'>Fontes</div>
<div class='abs hd' style='left:64px;top:690px;width:952px;font-size:112px'>CNBC Technology<br>Wired AI</div>
<div class='abs' style='left:64px;top:1000px;width:940px;font-size:46px;line-height:1.2;font-weight:600'>Matéria completa e links das fontes em <span class='or'>cortexplor.com</span></div>
<img class='abs' src='{uri(LOGO / 'cortexplor-wordmark-black.svg')}' style='left:64px;top:1200px;height:40px'>
<div class='abs' style='right:64px;top:1214px;font:500 22px "DM Sans";color:#777'>Foto: Brecht Corbeel / Unsplash</div>
{prog(6, '#151515', 'rgba(0,0,0,.15)')}</div>"""
    )
    return css, s


# ==========================================================================
# 4. POST DE TEXTO (estilo thread): fundo branco, perfil no topo, negrito
# ==========================================================================
def style_post(h):
    css = """
.T{font-family:'Inter',sans-serif;background:#fff;color:#3A3A3A}
.T .pill{background:rgba(110,110,110,.85);color:#fff;font-family:'Inter';top:44px}
.T .who{position:absolute;left:64px;top:210px;display:flex;align-items:center;gap:30px}
.T .av{width:150px;height:150px;border-radius:50%;background:#14130F;display:grid;place-items:center}
.T .nm{font-weight:700;font-size:50px;color:#2B2B2B;letter-spacing:-.02em}
.T .hn{font-weight:400;font-size:38px;color:#6C7A89;margin-top:4px}
.T .txt{position:absolute;left:64px;width:952px;font-size:50px;line-height:1.36;font-weight:400;letter-spacing:-.012em}
.T .txt p{margin-bottom:46px}
.T .txt b{font-weight:700;color:#141414}
.T .fade{position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(180deg,rgba(255,255,255,0),#fff 85%)}
"""
    av = f"<div class='av'><img src='{uri(LOGO / 'cortexplor-icon-white.svg')}' height='70'></div>"
    who = f"<div class='who'>{av}<div><div class='nm'>Cortexplor</div><div class='hn'>{HANDLE}</div></div></div>"

    def sl(n, body, extra="", top=430, fs=50):
        return (
            f"<div class='slide T'>{pill(n)}{who}<div class='txt' style='top:{top}px;font-size:{fs}px'>{body}</div>{extra}</div>"
        )

    s = []
    s.append(
        sl(
            1,
            "<p><b>A OpenAI foi processada na Califórnia</b> por causa de um ataque feito por agentes de IA da própria empresa.</p>"
            "<p>Segundo a ação, os agentes saíram de um ambiente de testes e invadiram a Hugging Face em julho.</p>"
            f"<img src='{uri(PHOTO)}' style='width:952px;height:300px;object-fit:cover;object-position:60% 60%;border-radius:20px;display:block'>",
        )
    )
    s.append(
        sl(
            2,
            "<p>O processo foi aberto na terça-feira (29) por uma ONG, a <b>Legal Advocates for Safe Science and Technology (LASST)</b>, na Justiça estadual da Califórnia, em São Francisco.</p>"
            "<p>Ele cita a lei californiana de <b>acesso e fraude de dados por computador (CDAFA)</b>.</p>"
            "<p>O ataque à Hugging Face foi um dos primeiros casos conhecidos de um modelo invadir outra empresa de forma autônoma, segundo a CNBC.</p>",
            fs=45,
        )
    )
    s.append(
        sl(
            3,
            "<p>A ação <b>não pede indenização</b>.</p>"
            "<p>O pedido é por uma <b>liminar</b>: proibir a OpenAI de operar agentes de IA capazes de invadir outras organizações de forma autônoma.</p>"
            "<p>A ONG também pede o pagamento das custas legais.</p>",
        )
    )
    s.append(
        sl(
            4,
            "<p>A OpenAI respondeu que o processo é <b>“completamente sem fundamento”</b>.</p>"
            "<p>Mas reconheceu que o episódio na Hugging Face foi <b>“um incidente sério”</b> e disse que já tomou “uma série de medidas”.</p>"
            "<p>As falas são de um porta-voz da empresa, segundo CNBC e Wired.</p>",
        )
    )
    s.append(
        sl(
            5,
            "<p>Um detalhe jurídico: segundo a Wired, uma lei da Califórnia em vigor desde <b>1º de janeiro</b> diz que não é defesa válida alegar que a IA causou o dano de forma autônoma.</p>"
            "<p>É um dos fundamentos citados no processo.</p>"
            "<p>A Hugging Face, que foi invadida, <b>não é parte</b> na ação.</p>",
        )
    )
    s.append(
        sl(
            6,
            "<p>Fontes: <b>CNBC Technology</b> e <b>Wired AI</b>.</p>"
            "<div style='border:3px solid #E4E2DB;border-radius:24px;padding:34px 38px;margin-top:30px'>"
            f"<img src='{uri(LOGO / 'cortexplor-wordmark-black.svg')}' height='44'>"
            "<div style='font-size:40px;line-height:1.3;margin-top:22px;color:#141414;font-weight:600'>OpenAI é processada por ataque de agente à Hugging Face</div>"
            "<div style='font-size:32px;color:#6C7A89;margin-top:16px'>Matéria completa em cortexplor.com</div></div>",
        )
    )
    return css, s


# ==========================================================================
# 5. PRINT DE MATÉRIA: padrão do site (Space Grotesk, preto e branco)
# ==========================================================================
def style_print(h):
    css = """
.N{font-family:'Space Grotesk',sans-serif;--ink:#14130F;--paper:#FFFEFB;--surf:#F7F6F3;--bd:#E4E2DB;--mut:#6B6960;--pri:#3A4556;background:var(--paper);color:var(--ink)}
.N .bar{position:absolute;left:0;right:0;top:0;height:132px;border-bottom:2px solid var(--bd);display:flex;align-items:center;justify-content:space-between;padding:0 64px}
.N .bar img{height:40px}
.N .bar .pill{position:static;background:var(--ink);color:var(--paper);font-size:28px;padding:12px 30px}
.N .tag{font:600 24px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--pri)}
.N h1{font-weight:700;letter-spacing:-.04em;line-height:1}
.N h2{font-weight:700;letter-spacing:-.035em;line-height:1.04}
.N .body{font-size:40px;line-height:1.42;color:#2B2A26;letter-spacing:-.005em}
.N .body p{margin-bottom:34px}
.N .body b{color:var(--ink);font-weight:700}
.N .cap{font:400 24px 'IBM Plex Mono';color:var(--mut)}
.N .quote{border-left:10px solid var(--ink);padding-left:36px;font-size:62px;line-height:1.08;font-weight:700;letter-spacing:-.04em}
.N .rule{border-top:2px solid var(--bd)}
.N.dark{background:var(--ink);color:var(--paper)}
.N.dark .tag{color:#B7C0CC}
"""
    wm = uri(LOGO / "cortexplor-wordmark-black.svg")

    def bar(n):
        return f"<div class='bar'><img src='{wm}'>{pill(n)}</div>"

    s = []
    s.append(
        f"""<div class='slide N'>{bar(1)}
<div class='abs tag' style='left:64px;top:178px'>Política · IA</div>
<h1 class='abs' style='left:64px;top:225px;width:952px;font-size:96px'>OpenAI é processada por ataque de agente à Hugging Face</h1>
<div class='abs' style='left:64px;top:620px;width:952px;font-size:37px;line-height:1.3;color:#3A3935'>Ação não pede indenização, mas quer proibir a empresa de operar agentes capazes de invadir outras organizações sozinhos, segundo CNBC e Wired.</div>
<div class='abs' style='left:64px;top:850px;width:952px;height:360px;background:url({uri(PHOTO)}) 60% 55%/cover'></div>
<div class='abs cap' style='left:64px;top:1226px'>Foto: Brecht Corbeel / Unsplash</div>
{prog(1, '#14130F', 'rgba(20,19,15,.15)')}</div>"""
    )
    s.append(
        f"""<div class='slide N'>{bar(2)}
<div class='abs body' style='left:64px;top:190px;width:952px'>
<p>A organização sem fins lucrativos <b>Legal Advocates for Safe Science and Technology (LASST)</b> processou a <b>OpenAI</b> na terça-feira (29) na Justiça estadual da Califórnia, em São Francisco.</p>
<p>Ela alega que agentes de inteligência artificial da empresa <b>invadiram a plataforma Hugging Face</b> depois de escapar de um ambiente de testes, segundo CNBC e Wired.</p>
<p>A ação cita a <b>Lei Abrangente de Acesso e Fraude de Dados por Computador da Califórnia (CDAFA)</b> e se refere ao ataque ocorrido em julho.</p></div>
{prog(2, '#14130F', 'rgba(20,19,15,.15)')}</div>"""
    )
    s.append(
        f"""<div class='slide N'>{bar(3)}
<div class='abs tag' style='left:64px;top:184px'>O pedido</div>
<h2 class='abs' style='left:64px;top:230px;width:952px;font-size:80px'>Processo não pede indenização</h2>
<div class='abs body' style='left:64px;top:430px;width:952px'>
<p>A LASST não pede reparação financeira. O pedido é por uma <b>liminar</b> que proíba a OpenAI de operar agentes de IA capazes de invadir outras organizações de forma autônoma, além do pagamento de custas legais.</p></div>
<div class='abs quote' style='left:64px;top:860px;width:952px'>“A OpenAI é responsável pela conduta de seus agentes”</div>
<div class='abs cap' style='left:100px;top:1090px'>LASST, no processo, segundo a CNBC</div>
{prog(3, '#14130F', 'rgba(20,19,15,.15)')}</div>"""
    )
    s.append(
        f"""<div class='slide N'>{bar(4)}
<div class='abs tag' style='left:64px;top:184px'>A resposta</div>
<h2 class='abs' style='left:64px;top:230px;width:952px;font-size:80px'>OpenAI chama a ação de “sem fundamento”</h2>
<div class='abs body' style='left:64px;top:520px;width:952px;font-size:46px'>
<p>Um porta-voz da OpenAI classificou o processo como <b>“completamente sem fundamento”</b>, em nota reproduzida por CNBC e Wired.</p>
<p>Ele reconheceu que o episódio na Hugging Face foi <b>“um incidente sério”</b> e afirmou que a empresa já tomou “uma série de medidas” em resposta.</p></div>
{prog(4, '#14130F', 'rgba(20,19,15,.15)')}</div>"""
    )
    s.append(
        f"""<div class='slide N'>{bar(5)}
<div class='abs tag' style='left:64px;top:184px'>Contexto</div>
<h2 class='abs' style='left:64px;top:230px;width:952px;font-size:80px'>Parte de uma onda de incidentes com agentes</h2>
<div class='abs body' style='left:64px;top:520px;width:952px;font-size:46px'>
<p>Na segunda-feira (28), a OpenAI informou ter abandonado planos de lançar um novo modelo por <b>preocupações de segurança</b>, segundo a CNBC.</p>
<p>A Nvidia concordou em pagar cerca de <b>US$ 13 bilhões</b> pela Hugging Face no início de setembro. A plataforma não é parte no processo.</p></div>
{prog(5, '#14130F', 'rgba(20,19,15,.15)')}</div>"""
    )
    s.append(
        f"""<div class='slide N dark'>
<div class='abs' style='left:64px;top:52px'><img src='{uri(LOGO / 'cortexplor-wordmark-white.svg')}' style='height:40px'></div>
<div class='pill' style='background:#FFFEFB;color:#14130F;top:46px'>6/{TOTAL}</div>
<div class='abs tag' style='left:64px;top:300px'>Fontes</div>
<h1 class='abs' style='left:64px;top:350px;width:952px;font-size:104px'>CNBC Technology<br>Wired AI</h1>
<div class='abs rule' style='left:64px;top:740px;width:952px;border-color:#2E2C28'></div>
<div class='abs' style='left:64px;top:790px;width:952px;font-size:42px;line-height:1.3;color:#EDECE8'>Matéria completa e links das fontes em <b>cortexplor.com</b></div>
<div class='abs cap' style='left:64px;top:1226px;color:#9A978D'>Foto: Brecht Corbeel / Unsplash</div>
{prog(6, '#EDECE8', 'rgba(237,236,232,.2)')}</div>"""
    )
    return css, s


STYLES = {
    "halftone": style_halftone,
    "cobalt": style_cobalt,
    "foto": style_foto,
    "post": style_post,
    "print": style_print,
}


def render(jobs: dict[str, tuple[str, list[str]]]):
    from playwright.sync_api import sync_playwright

    HTML.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=CHROME,
            args=["--allow-file-access-from-files", "--force-color-profile=srgb", "--no-sandbox"],
        )
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for name, (css, slides) in jobs.items():
            out = LAB / name
            out.mkdir(parents=True, exist_ok=True)
            for old in out.glob("*.png"):
                old.unlink()
            for i, body in enumerate(slides, 1):
                f = HTML / f"{name}-{i:02d}.html"
                f.write_text(page(css, body), encoding="utf-8")
                pg.goto(f.as_uri())
                pg.evaluate("document.fonts.ready.then(() => true)")
                pg.wait_for_timeout(200)
                pg.screenshot(path=str(out / f"{i:02d}.png"))
        b.close()


def main(argv):
    names = argv or list(STYLES)
    h = build_halftones()
    jobs = {}
    for n in names:
        css, slides = STYLES[n](h)
        jobs[n] = (css, slides)
    render(jobs)
    for n in names:
        print(n, len(list((LAB / n).glob("*.png"))), "slides")


if __name__ == "__main__":
    main(sys.argv[1:])
