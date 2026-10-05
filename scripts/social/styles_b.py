"""Estilos 5-10: jornal, poster, cobalto, meia-tinta, cartão, vidro."""
from __future__ import annotations

import carousel_lab as L
from carousel_core import (
    CHECK, ICON_B, ICON_W, INK, TOTAL, WM_B, WM_W, Ctx, crop_box, hl, ic, paras, photo_crop, pill, ticks,
)


def _tick(n, dark, **kw):
    on, off = ("#fff", "rgba(255,255,255,.25)") if dark else (INK, "rgba(20,19,15,.16)")
    return ticks(n, on, off, **kw)


# ============================================================================
# 5. JORNAL — revista, serifa (Instrument Serif) + Inter
# ============================================================================
def v_jornal(c: Ctx, pat):
    d = c.d
    css = """
.J{--bg:#F2ECDF;--fg:#1A1A17;--soft:#3C3A34;--mu:#7A7468;--rule:#CFC7B4;--ac:#8C2F26;background:var(--bg);color:var(--fg);font-family:'Inter',sans-serif}
.J.dk{--bg:#1B1A17;--fg:#F2ECDF;--soft:#D4CCBA;--mu:#A39B8A;--rule:#3A372F;--ac:#E3A94B}
.J .mast{position:absolute;left:64px;right:64px;top:42px;height:60px;display:flex;align-items:center;justify-content:space-between}
.J .mast .dt{font:500 20px 'Inter';letter-spacing:.18em;text-transform:uppercase;color:var(--mu);width:260px}
.J .mast .nm{font:italic 400 44px 'Instrument Serif';letter-spacing:.01em}
.J .mast .pill{position:static;background:transparent;color:var(--fg);border:2px solid var(--fg);font:500 24px 'Inter';padding:6px 20px;width:auto}
.J .rule{position:absolute;left:64px;right:64px;top:116px;border-top:3px solid var(--fg);height:6px;border-bottom:1px solid var(--fg)}
.J .lab{font:600 22px 'Inter';letter-spacing:.2em;text-transform:uppercase;color:var(--ac)}
.J .t{font:400 84px/.98 'Instrument Serif';letter-spacing:-.01em}
.J .t i{color:var(--ac)}
.J .b{font-size:33px;line-height:1.5;color:var(--soft)}
.J .b p{margin-bottom:22px}
.J .dcap p:first-child::first-letter{float:left;font:400 128px/.78 'Instrument Serif';padding:8px 14px 0 0;color:var(--ac)}
.J .pt{display:grid;grid-template-columns:96px 1fr;gap:18px;padding:24px 0;border-top:1px solid var(--rule)}
.J .pt .n{font:italic 400 92px/.8 'Instrument Serif';color:var(--ac)}
.J .pt h4{font:400 42px/1 'Instrument Serif';margin-bottom:8px;color:var(--fg)}
.J .pt p{font-size:28px;line-height:1.42;color:var(--soft)}
.J .stat{border-top:3px solid var(--fg);border-bottom:1px solid var(--rule);padding:24px 0;display:flex;align-items:baseline;gap:28px}
.J .stat b{font:italic 400 130px/.9 'Instrument Serif';color:var(--ac);white-space:nowrap}
.J .stat span{font:600 20px 'Inter';letter-spacing:.16em;text-transform:uppercase;color:var(--mu);line-height:1.5}
.J .tl{position:relative;padding-left:70px}
.J .tl:before{content:'';position:absolute;left:21px;top:14px;bottom:30px;border-left:2px solid var(--rule)}
.J .tl .e{position:relative;margin-bottom:46px}
.J .tl .e:before{content:'';position:absolute;left:-58px;top:10px;width:22px;height:22px;border-radius:50%;background:var(--ac);box-shadow:0 0 0 8px var(--bg)}
.J .tl .w{font:italic 400 48px/1 'Instrument Serif';color:var(--ac);margin-bottom:8px}
.J .tl p{font-size:31px;line-height:1.45;color:var(--soft)}
"""

    def sl(n, dark, body):
        return (
            f"<div class='slide J{' dk' if dark else ''}'>"
            f"<div class='mast'><span class='dt'>{d['date']}</span><span class='nm'>Cortexplor</span><span style='width:260px;text-align:right'>{pill(n)}</span></div><div class='rule'></div>"
            f"{body}{_tick(n, dark)}</div>"
        )

    s = []
    nlen = len(d["headline"])
    hs = 108 if nlen <= 50 else (92 if nlen <= 62 else 82)
    s.append(sl(1, pat[0], f"""
<div class='abs' style='left:64px;top:164px;width:952px;height:1090px;display:flex;flex-direction:column'>
<div class='lab'>{d['category']} · {d['kicker'].split('·')[-1].strip()}</div>
<div class='t' style='font-size:{hs}px;margin-top:22px'>{d['headline']}</div>
<div style='font:italic 400 40px/1.2 "Instrument Serif";color:var(--soft);margin-top:28px;padding-top:24px;border-top:1px solid var(--rule)'>{d['dek']}</div>
<div style='margin-top:30px;flex:1;min-height:0;background:url({c.ph}) {c.pos}/cover'></div>
<div style='margin-top:12px;font:500 19px Inter;letter-spacing:.14em;text-transform:uppercase;color:var(--mu)'>{c.credit}</div></div>"""))

    x = d["s2"]
    s.append(sl(2, pat[1], f"""
<div class='abs lab' style='left:64px;top:170px'>{x['label']}</div>
<div class='abs t' style='left:64px;top:216px;width:952px;font-size:76px'>{x['title']}</div>
<div class='abs b dcap' style='left:64px;top:520px;width:952px;font-size:35px'>{paras(x['body'])}</div>"""))

    x = d["s3"]
    pts = "".join(f"<div class='pt'><div class='n'>{i + 1}</div><div><h4>{p['h']}</h4><p>{p['t']}</p></div></div>" for i, p in enumerate(x["points"]))
    s.append(sl(3, pat[2], f"""
<div class='abs lab' style='left:64px;top:170px'>{x['label']}</div>
<div class='abs t' style='left:64px;top:214px;width:952px;font-size:64px'>{x['title']}</div>
<div class='abs b' style='left:64px;top:400px;width:952px;font-size:30px;line-height:1.45'>{x['body']}</div>
<div class='abs' style='left:64px;top:620px;width:952px'>{pts}</div>"""))

    x = d["s4"]
    st = x["stat"]
    s.append(sl(4, pat[3], f"""
<div class='abs lab' style='left:64px;top:170px'>{x['label']}</div>
<div class='abs t' style='left:64px;top:214px;width:952px;font-size:72px'>{x['title']}</div>
<div class='abs stat' style='left:64px;top:470px;width:952px'><b>{st['big']}</b><span>{st['cap']}</span></div>
<div class='abs b' style='left:64px;top:690px;width:952px;font-size:32px'>{paras(x['body'])}</div>"""))

    x = d["s5"]
    ev = "".join(f"<div class='e'><div class='w'>{e['h']}</div><p>{e['t']}</p></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs lab' style='left:64px;top:170px'>{x['label']}</div>
<div class='abs t' style='left:64px;top:214px;width:952px;font-size:72px'>{x['title']}</div>
<div class='abs tl' style='left:64px;top:470px;width:952px'>{ev}</div>"""))

    srcs = "".join(f"<div style='display:flex;gap:26px;align-items:baseline;padding:14px 0;border-top:1px solid var(--rule)'><i style='font:italic 400 44px \"Instrument Serif\";color:var(--ac);width:50px'>{i + 1}</i><span style='font:400 {c.fs(72, 56)}px/1 \"Instrument Serif\"'>{nm}</span></div>" for i, nm in enumerate(c.src))
    s.append(sl(6, pat[5], f"""
<div class='abs lab' style='left:64px;top:290px'>{c.u['sources']}</div>
<div class='abs' style='left:64px;top:340px;width:952px'>{srcs}</div>
<div class='abs' style='left:64px;top:900px;width:952px;font:italic 400 48px/1.2 "Instrument Serif";color:var(--soft)'>{c.u['full']} <span style='color:var(--ac)'>cortexplor.com</span></div>
<div class='abs' style='left:64px;top:1226px;font:500 19px Inter;letter-spacing:.14em;text-transform:uppercase;color:var(--mu)'>{c.credit}</div>"""))
    return css, s


# ============================================================================
# 6. POSTER — Anton em caixa-alta, amarelo ácido
# ============================================================================
def v_poster(c: Ctx, pat):
    d = c.d
    css = """
.P{font-family:'Archivo',sans-serif;--y:#D8D0BE;--k:#3A362F;--w:#F5F2EA;--r:#A8432A}
.P.y{background:var(--y);color:var(--k);--ac:var(--k);--soft:#3A362F;--pb:#3A362F;--pt:var(--y)}
.P.k{background:var(--k);color:#fff;--ac:var(--y);--soft:#D9D9D4;--pb:var(--y);--pt:#3A362F}
.P.w{background:var(--w);color:var(--k);--ac:var(--r);--soft:#3A362F;--pb:#3A362F;--pt:var(--w)}
.P .an{font-family:'Anton';text-transform:uppercase;font-weight:400;line-height:.96;letter-spacing:.002em}
.P .top{position:absolute;left:56px;right:56px;top:44px;display:flex;justify-content:space-between;align-items:center}
.P .top img{height:36px}
.P .top .pill{position:static;background:var(--pb);color:var(--pt);font:800 24px 'Archivo';padding:8px 22px;border-radius:0}
.P .lb{display:inline-block;background:var(--pb);color:var(--pt);font:800 26px 'Archivo';letter-spacing:.06em;text-transform:uppercase;padding:8px 18px}
.P .bd{font-size:35px;line-height:1.42;font-weight:500;color:var(--soft)}
.P .bd p{margin-bottom:22px}
.P .blk{background:var(--pb);color:var(--pt);padding:22px 28px;margin-bottom:16px}
.P .blk h4{font:400 40px/1 'Anton';text-transform:uppercase;letter-spacing:.01em;margin-bottom:8px;color:var(--pt)}
.P .blk p{font-size:28px;line-height:1.38;font-weight:500}
.P .sticker{position:absolute;background:#A8432A;color:#fff;font:800 26px/1.15 'Archivo';letter-spacing:.06em;text-transform:uppercase;padding:14px 22px;transform:rotate(-6deg);text-align:center}
.P .row{display:grid;grid-template-columns:230px 1fr;gap:20px;padding:24px 0;border-top:6px solid var(--pb);align-items:start}
.P .row b{font:400 62px/.95 'Anton';text-transform:uppercase}
.P .row p{font-size:31px;line-height:1.38;font-weight:500;color:var(--soft)}
"""
    theme = lambda n, dark: "k" if dark else ("y" if n % 2 == 1 else "w")

    def sl(n, dark, body):
        th = theme(n, dark)
        wm = WM_W if th == "k" else WM_B
        return (
            f"<div class='slide P {th}'><div class='top'><img src='{wm}'>{pill(n)}</div>"
            f"{body}{_tick(n, th == 'k', left=56, right=56, bottom=48)}</div>"
        )

    s = []
    nlen = len(d["headline"])
    hs = 128 if nlen <= 50 else (112 if nlen <= 62 else 100)
    s.append(sl(1, False, f"""
<div class='sticker' style='right:56px;top:690px'>{d['stamp']}</div>
<div class='abs lb' style='left:56px;top:140px'>{d['category']}</div>
<div class='abs an' style='left:56px;top:210px;width:900px;font-size:{hs}px'>{d['headline']}</div>
<div class='abs' style='left:56px;top:790px;width:968px;font-size:30px;line-height:1.38;font-weight:600'>{d['dek']}</div>
<div class='abs' style='left:56px;top:950px;width:968px;height:300px;background:url({c.ph}) {c.pos}/cover;border:6px solid var(--k)'></div>"""))

    x = d["s2"]
    s.append(sl(2, pat[1], f"""
<div class='abs lb' style='left:56px;top:140px'>{x['label']}</div>
<div class='abs an' style='left:56px;top:210px;width:968px;font-size:84px'>{x['title']}</div>
<div class='abs bd' style='left:56px;top:560px;width:968px'>{paras(x['body'])}</div>"""))

    x = d["s3"]
    blks = "".join(f"<div class='blk'><h4>{p['h']}</h4><p>{p['t']}</p></div>" for p in x["points"])
    s.append(sl(3, pat[2], f"""
<div class='abs lb' style='left:56px;top:140px'>{x['label']}</div>
<div class='abs an' style='left:56px;top:204px;width:968px;font-size:66px'>{x['title']}</div>
<div class='abs bd' style='left:56px;top:400px;width:968px;font-size:29px;line-height:1.4'>{x['body']}</div>
<div class='abs' style='left:56px;top:600px;width:968px'>{blks}</div>"""))

    x = d["s4"]
    st = x["stat"]
    s.append(sl(4, pat[3], f"""
<div class='abs lb' style='left:56px;top:140px'>{x['label']}</div>
<div class='abs an' style='left:56px;top:204px;width:968px;font-size:72px'>{x['title']}</div>
<div class='abs' style='left:0;top:470px;width:1080px;background:var(--pb);color:var(--pt);padding:26px 56px'>
<div class='an' style='font-size:128px;white-space:nowrap'>{st['big']}</div>
<div style='font:700 24px Archivo;letter-spacing:.08em;text-transform:uppercase;margin-top:8px'>{st['cap']}</div></div>
<div class='abs bd' style='left:56px;top:760px;width:968px;font-size:31px'>{paras(x['body'])}</div>"""))

    x = d["s5"]
    rows = "".join(f"<div class='row'><b>{e['h']}</b><p>{e['t']}</p></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs lb' style='left:56px;top:140px'>{x['label']}</div>
<div class='abs an' style='left:56px;top:204px;width:968px;font-size:78px'>{x['title']}</div>
<div class='abs' style='left:56px;top:460px;width:968px;border-bottom:6px solid var(--pb)'>{rows}</div>"""))

    fs = c.fs(110, 80)
    s.append(sl(6, pat[5], f"""
<div class='abs lb' style='left:56px;top:140px'>{c.u['sources']}</div>
<div class='abs an' style='left:56px;top:220px;width:968px;font-size:{fs}px'>{'<br>'.join(c.src)}</div>
<div class='abs bd' style='left:56px;top:900px;width:968px;font-weight:700'>{c.u['full']} <span style='background:var(--pb);color:var(--pt);padding:0 10px'>cortexplor.com</span></div>"""))
    return css, s


# ============================================================================
# 7. COBALTO — fundo cobalto / creme, Archivo pesada
# ============================================================================
def v_cobalto(c: Ctx, pat):
    d = c.d
    css = """
.K{font-family:'Archivo',sans-serif;--or:#C8693A}
.K.dk{background:#243352;color:#F1EBDD;--fg:#F1EBDD;--soft:#DCE0EA;--card:rgba(241,235,221,.12);--cardb:rgba(241,235,221,.4);--ac:#E0B08A}
.K.lt{background:#F1EBDD;color:#17233F;--fg:#17233F;--soft:#33456B;--card:#243352;--cardb:#243352;--ac:#C8693A}
.K .top{position:absolute;left:56px;right:56px;top:46px;display:flex;justify-content:space-between;align-items:center}
.K .top img{height:36px}
.K .top .pill{position:static;background:var(--fg);color:var(--ac);font:800 24px 'Archivo';padding:8px 22px;color:#243352}
.K.lt .top .pill{background:#243352;color:#F1EBDD}
.K .sf{font:italic 400 46px/1 'Instrument Serif';color:var(--ac)}
.K .h{font:800 78px/.98 'Archivo';font-stretch:112%;letter-spacing:-.035em}
.K .bd{font-size:34px;line-height:1.45;font-weight:500;color:var(--soft)}
.K .bd p{margin-bottom:22px}
.K .cd{border-radius:30px;padding:24px 30px;margin-bottom:18px;background:var(--card);border:2px solid var(--cardb)}
.K.lt .cd{color:#F1EBDD}
.K .cd h4{font:800 36px/1.05 'Archivo';letter-spacing:-.02em;margin-bottom:8px}
.K.lt .cd h4{color:#E0B08A}
.K .cd p{font-size:28px;line-height:1.4;font-weight:500}
.K .num{display:inline-grid;place-items:center;width:46px;height:46px;border-radius:50%;background:var(--or);color:#fff;font:800 24px Archivo;margin-right:14px;vertical-align:middle}
.K .big{font:900 150px/.9 'Archivo';font-stretch:112%;letter-spacing:-.05em;color:var(--or);white-space:nowrap}
.K .or{color:#C8693A}
.K .tm{display:grid;grid-template-columns:260px 1fr;gap:18px;padding:26px 0;border-top:3px solid var(--fg)}
.K .tm b{font:800 46px/1 'Archivo';letter-spacing:-.03em;color:var(--ac)}
.K .tm p{font-size:31px;line-height:1.4;font-weight:500;color:var(--soft)}
"""

    def sl(n, dark, body):
        wm = WM_W if dark else WM_B
        return (
            f"<div class='slide K {'dk' if dark else 'lt'}'><div class='top'><img src='{wm}'>{pill(n)}</div>"
            f"{body}{_tick(n, dark, left=56, right=56, bottom=48) if dark else ticks(n, '#243352', 'rgba(36,51,82,.2)', left=56, right=56, bottom=48)}</div>"
        )

    s = []
    nlen = len(d["headline"])
    hs = 92 if nlen <= 50 else (80 if nlen <= 62 else 72)
    s.append(sl(1, True, f"""
<div class='abs sf' style='left:56px;top:150px'>{d['category']} · {d['kicker'].split('·')[-1].strip()}</div>
<div class='abs h' style='left:56px;top:216px;width:968px;font-size:{hs}px'>{hl(d['headline'], d.get('headline_hl'), 'or')}</div>
<div class='abs bd' style='left:56px;top:640px;width:968px;font-size:31px;line-height:1.4'>{d['dek']}</div>
<div class='abs' style='left:56px;top:850px;width:968px;height:370px;border-radius:34px;background:url({c.ph}) {c.pos}/cover;border:8px solid #F1EBDD;transform:rotate(-1.4deg)'></div>"""))
    
    x = d["s2"]
    s.append(sl(2, pat[1], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:216px;width:968px;font-size:68px'>{x['title']}</div>
<div class='abs bd' style='left:56px;top:520px;width:968px'>{paras(x['body'])}</div>"""))

    x = d["s3"]
    cds = "".join(f"<div class='cd'><h4><span class='num'>{i + 1}</span>{p['h']}</h4><p>{p['t']}</p></div>" for i, p in enumerate(x["points"]))
    s.append(sl(3, pat[2], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:210px;width:968px;font-size:58px'>{x['title']}</div>
<div class='abs bd' style='left:56px;top:390px;width:968px;font-size:29px;line-height:1.4'>{x['body']}</div>
<div class='abs' style='left:56px;top:570px;width:968px'>{cds}</div>"""))

    x = d["s4"]
    st = x["stat"]
    s.append(sl(4, pat[3], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:210px;width:968px;font-size:64px'>{x['title']}</div>
<div class='abs' style='left:56px;top:450px;width:968px'><div class='big' style='font-size:{110 if len(st['big']) > 11 else 140}px'>{st['big']}</div>
<div class='sf' style='font-size:38px;margin-top:6px'>{st['cap']}</div></div>
<div class='abs bd' style='left:56px;top:700px;width:968px;font-size:31px'>{paras(x['body'])}</div>"""))

    x = d["s5"]
    tms = "".join(f"<div class='tm'><b>{e['h']}</b><p>{e['t']}</p></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:210px;width:968px;font-size:68px'>{x['title']}</div>
<div class='abs' style='left:56px;top:470px;width:968px;border-bottom:3px solid var(--fg)'>{tms}</div>"""))

    srcs = "".join(f"<div style='font:800 {c.fs(76, 58)}px/1.05 Archivo;letter-spacing:-.03em;padding:6px 0'><span class='num' style='width:50px;height:50px'>{i + 1}</span>{nm}</div>" for i, nm in enumerate(c.src))
    s.append(sl(6, pat[5], f"""
<div class='abs sf' style='left:56px;top:230px'>{c.u['sources']}</div>
<div class='abs' style='left:56px;top:300px;width:968px'>{srcs}</div>
<div class='abs bd' style='left:56px;top:860px;width:968px;font-weight:700'>{c.u['full']} <span style='color:var(--or)'>cortexplor.com</span></div>"""))
    return css, s


# ============================================================================
# 8. MEIA-TINTA — retícula de pontos, preto/creme/laranja
# ============================================================================
def v_meiatinta(c: Ctx, pat):
    d = c.d
    from PIL import Image

    size = Image.open(c.photo).size
    cream, black = "#ECE6D8", "#121212"
    hc = lambda aspect, sz, name, dot, bg, dd, sp, g=0.9: L.halftone(crop_box(size, aspect), sz, dot, bg, dd, f"{c.slug}_{name}", sp, g)
    cover = hc(1080 / 1350, (1080, 1350), "ht_cover", cream, black, False, 13)
    band_k = hc(1080 / 400, (1080, 400), "ht_band_k", cream, black, False, 11)
    band_l = hc(1080 / 400, (1080, 400), "ht_band_l", black, cream, True, 11, 1.0)
    css = """
.H{font-family:'Archivo',sans-serif;--or:#E8542A}
.H.dk{background:#121212;color:#ECE6D8;--fg:#ECE6D8;--soft:#CFC9BB;--rule:#3A3935;--card:#1D1D1B}
.H.lt{background:#ECE6D8;color:#121212;--fg:#121212;--soft:#333;--rule:#C9C2B1;--card:#E1DAC9}
.H .top{position:absolute;left:56px;right:56px;top:46px;display:flex;justify-content:space-between;align-items:center}
.H .top img{height:36px}
.H .top .pill{position:static;background:var(--fg);color:var(--card);font:700 24px 'Archivo';padding:8px 22px}
.H .sf{font:italic 400 46px/1 'Instrument Serif';color:var(--or)}
.H .h{font:800 74px/.98 'Archivo';font-stretch:108%;letter-spacing:-.035em}
.H .bd{font-size:33px;line-height:1.45;font-weight:500;color:var(--soft)}
.H .bd p{margin-bottom:22px}
.H .pt{display:grid;grid-template-columns:70px 1fr;gap:16px;padding:22px 0;border-top:2px solid var(--rule)}
.H .pt .n{width:56px;height:56px;border-radius:50%;background:var(--or);color:#fff;display:grid;place-items:center;font:800 26px Archivo}
.H .pt h4{font:800 36px/1.05 Archivo;letter-spacing:-.02em;margin-bottom:6px}
.H .pt p{font-size:27px;line-height:1.4;color:var(--soft);font-weight:500}
.H .big{font:900 140px/.9 'Archivo';font-stretch:108%;letter-spacing:-.05em;color:var(--or);white-space:nowrap}
.H .dots{position:absolute;right:-60px;bottom:-60px;width:520px;height:520px;background-image:radial-gradient(circle,var(--or) 0 36%,transparent 38%);background-size:26px 26px;-webkit-mask-image:radial-gradient(circle at 70% 70%,#000 0,transparent 68%);mask-image:radial-gradient(circle at 70% 70%,#000 0,transparent 68%);opacity:.9}
.H .tm{display:grid;grid-template-columns:260px 1fr;gap:18px;padding:26px 0;border-top:2px solid var(--rule)}
.H .tm b{font:800 44px/1 Archivo;letter-spacing:-.03em;color:var(--or)}
.H .tm p{font-size:30px;line-height:1.4;font-weight:500;color:var(--soft)}
"""

    def sl(n, dark, body, extra=""):
        wm = WM_W if dark else WM_B
        on, off = ("#ECE6D8", "rgba(236,230,216,.22)") if dark else ("#121212", "rgba(18,18,18,.16)")
        return (
            f"<div class='slide H {'dk' if dark else 'lt'}'>{extra}<div class='top'><img src='{wm}'>{pill(n)}</div>"
            f"{body}{ticks(n, on, off, left=56, right=56, bottom=48)}</div>"
        )

    s = []
    nlen = len(d["headline"])
    hs = 84 if nlen <= 50 else (74 if nlen <= 62 else 68)
    s.append(
        f"<div class='slide H dk'><div class='abs' style='inset:0;background:url({cover}) center/cover'></div>"
        f"<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(18,18,18,.55) 0%,rgba(18,18,18,.05) 16%,rgba(18,18,18,.3) 44%,rgba(18,18,18,.95) 76%)'></div>"
        f"<div class='top'><img src='{WM_W}'>{pill(1)}</div>"
        f"<div class='abs sf' style='left:56px;top:690px'>{d['category']} · {d['kicker'].split('·')[-1].strip()}</div>"
        f"<div class='abs h' style='left:56px;top:750px;width:968px;font-size:{hs}px;color:#ECE6D8'>{d['headline']}</div>"
        f"<div class='abs bd' style='left:56px;top:1070px;width:968px;font-size:29px;line-height:1.38;color:#CFC9BB'>{d['dek']}</div>"
        f"{ticks(1, '#ECE6D8', 'rgba(236,230,216,.22)', left=56, right=56, bottom=48)}</div>"
    )

    x = d["s2"]
    dark2 = pat[1]
    band = band_k if dark2 else band_l
    s.append(sl(2, dark2, f"""
<div class='abs' style='left:0;top:120px;width:1080px;height:400px;background:url({band}) center/cover'></div>
<div class='abs sf' style='left:56px;top:560px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:620px;width:968px;font-size:56px'>{x['title']}</div>
<div class='abs bd' style='left:56px;top:830px;width:968px;font-size:29px;line-height:1.42'>{paras(x['body'], 'margin-bottom:16px')}</div>"""))

    x = d["s3"]
    pts = "".join(
        f"<div class='pt'><div class='n'>{i}</div><div><h4>{p['h']}</h4><p>{p['t']}</p></div></div>"
        for i, p in enumerate(x["points"], 1)
    )
    s.append(sl(3, pat[2], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:210px;width:968px;font-size:58px'>{x['title']}</div>
<div class='abs bd' style='left:56px;top:390px;width:968px;font-size:29px;line-height:1.4'>{x['body']}</div>
<div class='abs' style='left:56px;top:590px;width:968px'>{pts}</div>"""))

    x = d["s4"]
    s.append(sl(4, pat[3], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:210px;width:968px;font-size:62px'>{x['title']}</div>
<div class='abs' style='left:56px;top:450px;width:968px'><div class='big' style='font-size:{140 if len(x['stat']['big']) <= 10 else 112}px'>{x['stat']['big']}</div>
<div class='sf' style='font-size:36px;margin-top:8px'>{x['stat']['cap']}</div></div>
<div class='abs bd' style='left:56px;top:700px;width:968px;font-size:30px'>{paras(x['body'])}</div>""", extra="<div class='dots'></div>" if pat[3] else ""))

    x = d["s5"]
    rows = "".join(f"<div class='tm'><b>{e['h']}</b><p>{e['t']}</p></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs sf' style='left:56px;top:150px'>{x['label']}</div>
<div class='abs h' style='left:56px;top:210px;width:968px;font-size:66px'>{x['title']}</div>
<div class='abs' style='left:56px;top:460px;width:968px;border-bottom:2px solid var(--rule)'>{rows}</div>"""))

    srcs = "<br>".join(c.src)
    s.append(
        f"<div class='slide H dk'><div class='abs' style='inset:0;background:url({cover}) center/cover;opacity:.5'></div>"
        f"<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(18,18,18,.4),rgba(18,18,18,.96) 70%)'></div>"
        f"<div class='top'><img src='{WM_W}'>{pill(6)}</div><div class='abs sf' style='left:56px;top:560px'>{c.u['sources']}</div>"
        f"<div class='abs h' style='left:56px;top:620px;width:968px;font-size:62px;color:#ECE6D8'>{srcs}</div>"
        f"<div class='abs bd' style='left:56px;top:1030px;width:968px;font-weight:700;color:#ECE6D8'>{c.u['full']} <span style='color:#E8542A'>cortexplor.com</span></div>"
        f"{ticks(6, '#ECE6D8', 'rgba(236,230,216,.22)', left=56, right=56, bottom=48)}</div>"
    )
    return css, s


# ============================================================================
# 9. CARTÃO — post de rede social, cartões arredondados verde/lima
# ============================================================================
def v_cartao(c: Ctx, pat):
    d = c.d
    css = """
.T{font-family:'DM Sans',sans-serif}
.T.lt{background:#ECEBE5;color:#1B1D20;--card:#fff;--soft:#44494F;--chip:#D9D2C2;--chipt:#1B1D20;--sub:#F3F2EC;--ac:#2F3A44}
.T.dk{background:#22252A;color:#F3F2EE;--card:rgba(255,255,255,.09);--soft:#D0D2D4;--chip:#D9D2C2;--chipt:#1B1D20;--sub:rgba(255,255,255,.08);--ac:#D9D2C2}
.T .hd{position:absolute;left:56px;right:56px;top:44px;height:72px;display:flex;align-items:center;gap:18px}
.T .av{width:64px;height:64px;border-radius:50%;background:#D9D2C2;display:grid;place-items:center}
.T .av img{height:34px}
.T .hd .nm{font:700 30px/1.1 'DM Sans'}
.T .hd .nm span{display:block;font:500 22px 'DM Sans';opacity:.65}
.T .hd .pill{position:static;margin-left:auto;background:var(--chip);color:var(--chipt);font:700 24px 'DM Sans';padding:8px 22px}
.T .card{position:absolute;left:40px;right:40px;top:140px;bottom:92px;background:var(--card);border-radius:44px;padding:44px 48px;box-shadow:0 10px 40px rgba(18,40,31,.10)}
.T.dk .card{box-shadow:none;border:2px solid rgba(255,255,255,.14)}
.T .chip{display:inline-block;background:var(--chip);color:var(--chipt);font:700 24px 'DM Sans';padding:8px 20px;border-radius:999px}
.T .h{font:700 64px/1.02 'DM Sans';letter-spacing:-.03em;margin-top:22px}
.T .bd{font-size:34px;line-height:1.45;color:var(--soft);font-weight:500}
.T .bd p{margin-bottom:22px}
.T .sub{background:var(--sub);border-radius:28px;padding:22px 28px;margin-bottom:16px}
.T .sub h4{font:700 34px/1.1 'DM Sans';margin-bottom:6px;color:inherit}
.T .sub p{font-size:27px;line-height:1.4;color:var(--soft);font-weight:500}
.T .sub .nb{display:inline-grid;place-items:center;width:42px;height:42px;border-radius:50%;background:var(--ac);color:#fff;font:700 22px 'DM Sans';margin-right:12px;vertical-align:middle}
.T.dk .sub .nb{color:#1B1D20 !important}
.T .big{font:700 120px/.95 'DM Sans';letter-spacing:-.05em;color:var(--ac);white-space:nowrap}
.T .tm{display:grid;grid-template-columns:240px 1fr;gap:16px;padding:22px 0;border-top:2px solid rgba(127,140,132,.3)}
.T .tm b{font:700 40px/1 'DM Sans';letter-spacing:-.03em;color:var(--ac)}
.T .tm p{font-size:29px;line-height:1.4;color:var(--soft);font-weight:500}
"""
    user = f"@cortexplor · {d['date']}"

    def sl(n, dark, inner):
        on, off = ("#D9D2C2", "rgba(255,255,255,.2)") if dark else ("#2F3A44", "rgba(34,37,42,.18)")
        return (
            f"<div class='slide T {'dk' if dark else 'lt'}'><div class='hd'><div class='av'><img src='{ICON_B}'></div>"
            f"<div class='nm'>Cortexplor<span>{user}</span></div>{pill(n)}</div>"
            f"<div class='card'>{inner}</div>{ticks(n, on, off, left=56, right=56, bottom=40)}</div>"
        )

    s = []
    nlen = len(d["headline"])
    hs = 62 if nlen <= 62 else 54
    s.append(sl(1, True, f"""
<div class='chip'>{d['category']}</div>
<div class='h' style='font-size:{hs}px'>{d['headline']}</div>
<div class='bd' style='font-size:29px;line-height:1.4;margin-top:20px'>{d['dek']}</div>
<div style='position:absolute;left:48px;right:48px;bottom:48px;height:420px;border-radius:30px;background:url({c.ph}) {c.pos}/cover'></div>"""))

    x = d["s2"]
    s.append(sl(2, pat[1], f"""
<div class='chip'>{x['label']}</div>
<div class='h' style='font-size:58px'>{x['title']}</div>
<div class='bd' style='margin-top:30px;font-size:33px'>{paras(x['body'])}</div>"""))

    x = d["s3"]
    subs = "".join(
        f"<div class='sub'><h4><span class='nb'>{i}</span>{p['h']}</h4><p>{p['t']}</p></div>"
        for i, p in enumerate(x["points"], 1)
    )
    s.append(sl(3, pat[2], f"""
<div class='chip'>{x['label']}</div>
<div class='h' style='font-size:50px;margin-top:16px'>{x['title']}</div>
<div class='bd' style='font-size:28px;line-height:1.4;margin-top:16px'>{x['body']}</div>
<div style='margin-top:22px'>{subs}</div>"""))

    x = d["s4"]
    s.append(sl(4, pat[3], f"""
<div class='chip'>{x['label']}</div>
<div class='h' style='font-size:52px'>{x['title']}</div>
<div class='sub' style='margin-top:26px;margin-bottom:22px'><div class='big' style='font-size:118px'>{x['stat']['big']}</div><p style='font-size:25px;margin-top:6px;color:var(--soft)'>{x['stat']['cap']}</p></div>
<div class='bd' style='font-size:29px;line-height:1.42'>{paras(x['body'])}</div>"""))

    x = d["s5"]
    rows = "".join(f"<div class='tm'><b>{e['h']}</b><p>{e['t']}</p></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='chip'>{x['label']}</div>
<div class='h' style='font-size:56px'>{x['title']}</div>
<div style='margin-top:30px'>{rows}</div>"""))

    nb = "display:inline-grid;place-items:center;width:42px;height:42px;border-radius:50%;background:var(--ac);color:#fff;font:700 22px 'DM Sans';margin-right:14px;vertical-align:middle"
    srcs = "".join(
        f"<div class='sub' style='font:700 40px/1.1 \"DM Sans\"'><span class='nb' style='{nb}'>{i}</span>{nm}</div>"
        for i, nm in enumerate(c.src, 1)
    )
    s.append(sl(6, pat[5], f"""
<div class='chip'>{c.u['sources']}</div>
<div style='margin-top:30px'>{srcs}</div>
<div class='bd' style='margin-top:30px;font-weight:700'>{c.u['full']} <span style='color:var(--ac)'>cortexplor.com</span></div>"""))
    return css, s


STYLES_B = {
    "jornal": v_jornal,
    "poster": v_poster,
    "cobalto": v_cobalto,
    "meiatinta": v_meiatinta,
    "cartao": v_cartao,
}
