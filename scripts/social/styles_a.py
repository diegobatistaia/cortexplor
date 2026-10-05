"""Estilos 1-4 (aprovados): edição, terminal, dossiê, duotone. Leem o spec narrativo."""
from __future__ import annotations

import re

import carousel_lab as L
from carousel_core import (
    ARROW, CHECK, CROSS, INK, TOTAL, WM_B, WM_W, Ctx, ic, hl, paras, photo_crop, pill, short, ticks,
)


# ============================================================================
# 1. EDIÇÃO — primeira página de jornal
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
.A .cols{column-count:2;column-gap:56px;column-rule:2px solid var(--rule);font-size:33px;line-height:1.38;color:var(--soft)}
.A .cols p{margin-bottom:24px}
.A .cols.dc p:first-child::first-letter{float:left;font-size:112px;line-height:.8;padding:8px 14px 0 0;font-weight:700;color:var(--fg)}
.A .li{display:flex;gap:26px;padding:22px 0;border-bottom:2px solid var(--fg);font-size:31px;line-height:1.3;color:var(--soft)}
.A .li b.n{font:700 32px 'IBM Plex Mono';color:var(--red);flex:none;width:56px}
.A .li span b{color:var(--fg);display:block;font-size:34px;letter-spacing:-.02em;margin-bottom:4px}
.A .ev{display:grid;grid-template-columns:200px 1fr;padding:28px 0;border-top:2px solid var(--fg)}
.A .ev .d{font:700 30px 'IBM Plex Mono';color:var(--red);line-height:1.3;text-transform:uppercase}
.A .ev .t{font-size:33px;line-height:1.32;color:var(--soft)}
.A .strip{background:var(--fg);color:var(--bg);padding:22px 32px;font:500 24px 'IBM Plex Mono';letter-spacing:.06em;text-transform:uppercase}
.A .stat{display:flex;align-items:baseline;gap:28px;border-top:2px solid var(--fg);border-bottom:2px solid var(--fg);padding:22px 0}
.A .stat b{font-size:88px;line-height:1;letter-spacing:-.05em;color:var(--red);white-space:nowrap}
.A .stat span{font:500 23px 'IBM Plex Mono';letter-spacing:.1em;text-transform:uppercase;color:var(--mu);line-height:1.4}
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

    x = d["s2"]
    s.append(sl(2, pat[1], f"""
<div class='abs lab' style='left:64px;top:172px'>{x['label']}</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:72px'>{x['title']}</h2>
<div class='abs cols dc' style='left:64px;top:520px;width:952px'>{paras(x['body'])}</div>
<div class='abs strip' style='left:64px;top:1130px;width:952px'>{c.confirm()}</div>"""))

    x = d["s3"]
    items = "".join(f"<div class='li'><b class='n'>{i + 1:02d}</b><span><b>{p['h']}</b>{p['t']}</span></div>" for i, p in enumerate(x["points"]))
    s.append(sl(3, pat[2], f"""
<div class='abs lab' style='left:64px;top:172px'>{x['label']}</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:62px'>{x['title']}</h2>
<div class='abs' style='left:64px;top:410px;width:952px;font-size:31px;line-height:1.36;color:var(--soft)'>{x['body']}</div>
<div class='abs' style='left:64px;top:600px;width:952px;border-top:2px solid var(--fg)'>{items}</div>"""))

    x = d["s4"]
    st = x["stat"]
    s.append(sl(4, pat[3], f"""
<div class='abs lab' style='left:64px;top:172px'>{x['label']}</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:72px'>{x['title']}</h2>
<div class='abs stat' style='left:64px;top:470px;width:952px'><b>{st['big']}</b><span>{st['cap']}</span></div>
<div class='abs cols' style='left:64px;top:650px;width:952px'>{paras(x['body'])}</div>"""))

    x = d["s5"]
    evs = "".join(f"<div class='ev'><div class='d'>{e['h']}</div><div class='t'>{e['t']}</div></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs lab' style='left:64px;top:172px'>{x['label']}</div>
<h2 class='abs' style='left:64px;top:216px;width:952px;font-size:72px'>{x['title']}</h2>
<div class='abs' style='left:64px;top:470px;width:952px;border-bottom:2px solid var(--fg)'>{evs}</div>"""))

    fs = c.fs(64, 46)
    pad = 34 if c.n <= 2 else 20
    rows = "".join(
        f"<div class='li' style='font-size:{fs}px;font-weight:700;letter-spacing:-.04em;padding:{pad}px 0;color:var(--fg)'><b class='n' style='width:80px'>{i + 1}</b><span>{nm}</span></div>"
        for i, nm in enumerate(c.src)
    )
    s.append(sl(6, pat[5], f"""
<div class='abs lab' style='left:64px;top:300px'>{c.u['sources']}</div>
<div class='abs' style='left:64px;top:350px;width:952px;border-top:2px solid var(--fg)'>{rows}</div>
<div class='abs' style='left:64px;top:900px;width:952px;font-size:42px;line-height:1.3'>{c.u['full']} <b>cortexplor.com</b></div>
<div class='abs lab' style='left:64px;top:1226px;font-size:20px'>{c.credit}</div>"""))
    return css, s


# ============================================================================
# 2. TERMINAL — mono, marca-texto âmbar
# ============================================================================
def _slug(t):
    t = t.lower()
    for a, b in (("ç", "c"), ("ã", "a"), ("õ", "o"), ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("â", "a"), ("ê", "e"), ("ô", "o")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def v_terminal(c: Ctx, pat):
    d = c.d
    css = """
.B{--bg:#14130F;--fg:#EDECE8;--dim:#9A978D;--soft:#C9C7BF;--rule:#2E2C28;--dash:#3A3833;--card:#1C1B18;--acc:#F2C14E;--gr:#6FD08C;--rd:#FF7A70;--pg:rgba(111,208,140,.13);--pr:rgba(255,122,112,.13);--st:#fff;background:var(--bg);color:var(--fg);font-family:'Space Grotesk',sans-serif}
.B.lt{--bg:#FFFEFB;--fg:#14130F;--dim:#6B6960;--soft:#3A3935;--rule:#E4E2DB;--dash:#CFCBC0;--card:#F4F2EC;--acc:#8A6200;--gr:#2F7D4A;--rd:#C0392B;--pg:rgba(47,125,74,.1);--pr:rgba(192,57,43,.09);--st:#000}
.B .bar{position:absolute;left:64px;right:64px;top:44px;height:56px;display:flex;align-items:center;justify-content:space-between;font:500 24px 'IBM Plex Mono';color:var(--dim)}
.B .bar b{color:var(--fg);font-weight:500}
.B .bar .pill{position:static;background:var(--fg);color:var(--bg);font-size:26px;padding:8px 24px;font-family:'IBM Plex Mono'}
.B .ln{position:absolute;left:64px;right:64px;top:112px;border-top:2px solid var(--rule)}
.B .mono{font-family:'IBM Plex Mono'}
.B h1,.B h2{font-weight:700;letter-spacing:-.04em;line-height:1.05}
.B .hl{background:#F2C14E;color:#14130F;padding:0 .12em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.B .lbl{display:inline-block;background:#F2C14E;color:#14130F;font:600 24px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;padding:6px 14px}
.B .row{display:flex;gap:22px;padding:22px 0;border-bottom:2px dashed var(--dash);font:400 29px/1.45 'IBM Plex Mono';color:var(--soft)}
.B .row i{font-style:normal;color:var(--acc);flex:none}
.B .row b,.B .df b{color:var(--st)}
.B .df{display:flex;gap:22px;padding:22px 26px;font:400 27px/1.42 'IBM Plex Mono';margin-bottom:14px;color:var(--soft)}
.B .df.p{background:var(--pg);border-left:8px solid var(--gr)}
.B .df b{display:block;font-size:30px;margin-bottom:4px}
.B .df i{font-style:normal;font-weight:700;flex:none;color:var(--gr)}
.B .msg{border-left:8px solid #F2C14E;background:var(--card);padding:26px 34px;margin-top:30px}
.B .msg .w{font:600 22px 'IBM Plex Mono';letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin-bottom:8px}
.B .msg .q{font-size:76px;line-height:1.02;font-weight:700;letter-spacing:-.04em}
.B .kv{display:grid;grid-template-columns:210px 1fr;font:400 29px/1.45 'IBM Plex Mono'}
.B .kv div{padding:24px 0;border-bottom:2px dashed var(--dash)}
.B .kv .k{color:var(--acc);font-weight:600}
.B .kv .v{color:var(--soft)}
"""

    def sl(n, light, cmd, body):
        on, off = (INK, "rgba(20,19,15,.18)") if light else ("#EDECE8", "rgba(237,236,232,.18)")
        return (
            f"<div class='slide B{' lt' if light else ''}'>"
            f"<div class='bar'><span>cortexplor@ia:~$ <b>{cmd}</b></span>{pill(n)}</div><div class='ln'></div>"
            f"{body}{ticks(n, on, off)}</div>"
        )

    # Pedido do dono em 05/10/2026: nada de nome de arquivo (".txt", ".log")
    # no topo. O prompt mostra só o rótulo do slide, em palavras.
    cmd1 = d.get("kicker") or d["category"]
    s = []
    s.append(sl(1, not pat[0], cmd1, f"""
<h1 class='abs' style='left:64px;top:170px;width:952px;font-size:84px;line-height:1.12'>{hl(d['headline'], d.get('headline_hl'))}</h1>
<div class='abs mono' style='left:64px;top:540px;width:952px;font-size:30px;line-height:1.5;color:var(--soft)'>&gt; {d['dek']}<span style='background:#F2C14E;color:#F2C14E'>_</span></div>
<div class='abs' style='left:64px;top:860px;width:952px;height:330px;overflow:hidden;border:2px solid var(--dash)'>
<img src='{c.ph}' style='width:100%;height:100%;object-fit:cover;object-position:{c.pos};filter:grayscale(1) contrast(1.15) brightness(.85)'>
<div class='abs' style='inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.3) 0 2px,transparent 2px 5px)'></div></div>
<div class='abs mono' style='left:64px;top:1206px;font-size:20px;color:var(--dim)'>{c.credit}</div>"""))

    x = d["s2"]
    rows = "".join(f"<div class='row'><i>›</i><span>{p}</span></div>" for p in x["body"])
    s.append(sl(2, not pat[1], d["s2"]["label"], f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {x['label']}</span></div>
<h2 class='abs' style='left:64px;top:236px;width:952px;font-size:64px'>{x['title']}</h2>
<div class='abs' style='left:64px;top:480px;width:952px'>{rows}</div>"""))

    x = d["s3"]
    dfs = "".join(f"<div class='df p'><i>+</i><span><b>{p['h']}</b>{p['t']}</span></div>" for p in x["points"])
    s.append(sl(3, not pat[2], d["s3"]["label"], f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {x['label']}</span></div>
<h2 class='abs' style='left:64px;top:230px;width:952px;font-size:54px'>{x['title']}</h2>
<div class='abs mono' style='left:64px;top:380px;width:952px;font-size:26px;line-height:1.45;color:var(--soft)'>{x['body']}</div>
<div class='abs' style='left:64px;top:560px;width:952px'>{dfs}</div>"""))

    x = d["s4"]
    st = x["stat"]
    rows = "".join(f"<div class='row'><i>›</i><span>{p}</span></div>" for p in x["body"])
    s.append(sl(4, not pat[3], d["s4"]["label"], f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {x['label']}</span></div>
<h2 class='abs' style='left:64px;top:236px;width:952px;font-size:60px'>{x['title']}</h2>
<div class='abs' style='left:64px;top:410px;width:952px'>{rows}
<div class='msg'><div class='w'>{st['cap']}</div><div class='q'>{st['big']}</div></div></div>"""))

    x = d["s5"]
    kv = "".join(f"<div class='k'>{e['h']}</div><div class='v'>{e['t']}</div>" for e in x["items"])
    s.append(sl(5, not pat[4], d["s5"]["label"], f"""
<div class='abs' style='left:64px;top:170px'><span class='lbl'>// {x['label']}</span></div>
<h2 class='abs' style='left:64px;top:236px;width:952px;font-size:64px'>{x['title']}</h2>
<div class='abs kv' style='left:64px;top:430px;width:952px'>{kv}</div>"""))

    fs = c.fs(104, 64)
    s.append(sl(6, not pat[5], c.u["sources"], f"""
<div class='abs' style='left:64px;top:300px'><span class='lbl'>// {c.u['sources']}</span></div>
<h1 class='abs' style='left:64px;top:370px;width:952px;font-size:{fs}px'>{'<br>'.join(c.src)}</h1>
<div class='abs mono' style='left:64px;top:800px;width:952px;font-size:36px;line-height:1.4;color:var(--soft)'>&gt; {c.u['full']} <span class='hl' style='font-weight:700'>cortexplor.com</span></div>
<img class='abs' src='{WM_W}' style='left:64px;top:1180px;height:42px'>"""))
    return css, s


# ============================================================================
# 3. DOSSIÊ — pasta, ficha, checkbox, carimbo
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
.C .box{width:54px;height:54px;border:4px solid var(--fg);display:grid;place-items:center;flex:none;border-radius:8px;color:var(--fg);margin-top:4px}
.C .opt{display:flex;gap:26px;align-items:flex-start;padding:20px 0;border-top:2px solid var(--fg);font-size:28px;line-height:1.35;color:var(--soft)}
.C .opt b{display:block;color:var(--fg);font-size:33px;letter-spacing:-.02em;margin-bottom:4px}
.C .body{font-size:34px;line-height:1.4;color:var(--soft)}
.C .body p{margin-bottom:22px}
.C .card{border:3px solid var(--fg);border-left:16px solid var(--acc);padding:24px 34px;border-radius:6px}
.C .card .q{font-size:80px;line-height:1;font-weight:700;letter-spacing:-.045em;margin-top:8px}
.C .num{display:grid;grid-template-columns:230px 1fr;gap:20px;padding:28px 0;border-top:2px solid var(--fg);align-items:start}
.C .num b{font-size:46px;letter-spacing:-.04em;line-height:1;color:var(--acc);white-space:nowrap}
.C .num span{font-size:32px;line-height:1.35;color:var(--soft)}
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

    x = d["s2"]
    s.append(sl(2, pat[1], f"""
<div class='abs lab' style='left:88px;top:176px'>{x['label']}</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:72px'>{x['title']}</h2>
<div class='abs body' style='left:88px;top:500px;width:904px'>{paras(x['body'])}</div>"""))

    x = d["s3"]
    opts = "".join(f"<div class='opt'><div class='box'>{ic(CHECK, 36)}</div><span><b>{p['h']}</b>{p['t']}</span></div>" for p in x["points"])
    s.append(sl(3, pat[2], f"""
<div class='abs lab' style='left:88px;top:176px'>{x['label']}</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:58px'>{x['title']}</h2>
<div class='abs body' style='left:88px;top:400px;width:904px;font-size:29px'>{x['body']}</div>
<div class='abs' style='left:88px;top:590px;width:904px;border-bottom:2px solid var(--fg)'>{opts}</div>"""))

    x = d["s4"]
    st = x["stat"]
    s.append(sl(4, pat[3], f"""
<div class='abs lab' style='left:88px;top:176px'>{x['label']}</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:68px'>{x['title']}</h2>
<div class='abs body' style='left:88px;top:430px;width:904px;font-size:33px'>{paras(x['body'])}</div>
<div class='abs card' style='left:88px;top:1000px;width:904px'><div class='lab'>{st['cap']}</div><div class='q'>{st['big']}</div></div>"""))

    x = d["s5"]
    nums = "".join(f"<div class='num'><b>{e['h']}</b><span>{e['t']}</span></div>" for e in x["items"])
    s.append(sl(5, pat[4], f"""
<div class='abs lab' style='left:88px;top:176px'>{x['label']}</div>
<h2 class='abs' style='left:88px;top:224px;width:904px;font-size:72px'>{x['title']}</h2>
<div class='abs' style='left:88px;top:470px;width:904px;border-bottom:2px solid var(--fg)'>{nums}</div>"""))

    fs = c.fs(64, 44)
    pad = "8px 0 22px" if c.n <= 2 else "4px 0 12px"
    srows = "".join(
        f"<div class='f' style='grid-template-columns:110px 1fr'><div class='k' style='font-size:34px;color:var(--acc)'>{i + 1:02d}</div><div class='v' style='font-size:{fs}px;font-weight:700;letter-spacing:-.04em;padding:{pad}'>{nm}</div></div>"
        for i, nm in enumerate(c.src)
    )
    s.append(sl(6, pat[5], f"""
<div class='abs lab' style='left:88px;top:300px'>{c.u['sources_long']}</div>
<div class='abs' style='left:88px;top:350px;width:904px;border-bottom:2px solid var(--fg)'>{srows}</div>
<div class='abs' style='left:88px;top:860px;width:904px;font-size:42px;line-height:1.3'>{c.u['full']} <b>cortexplor.com</b></div>
<img class='abs' src='{WM_W}' style='left:88px;top:1130px;height:42px'>
<div class='stamp' style='right:96px;top:1090px;font-size:24px'>{c.u['archived']}</div>""", f"{c.u['dossier']} {no} · {c.u['sources']}"))
    return css, s


# ============================================================================
# 4. DUOTONE — foto na cor original, malha e marcas de corte
# ============================================================================
def v_duotone(c: Ctx, pat=None):
    d = c.d
    cover = photo_crop(c, 1080 / 1350, (1080, 1350), "cover")
    band = photo_crop(c, 1080 / 420, (1080, 420), "band")
    strip = photo_crop(c, 340 / 1350, (340, 1350), "strip", fx=0.72)
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
.D .body{font-size:34px;line-height:1.4;color:#3A3935}
.D .body p{margin-bottom:20px}
.D .card{border:3px solid rgba(255,255,255,.55);padding:26px 30px;display:grid;grid-template-columns:230px 1fr;gap:20px;align-items:start;margin-bottom:22px}
.D .card .n{font-size:46px;font-weight:700;letter-spacing:-.04em;line-height:1;color:#C9C7BF}
.D .card .d{font-size:31px;line-height:1.35;opacity:.95}
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
<div class='abs' style='inset:0;background:linear-gradient(180deg,rgba(20,19,15,.35) 0%,rgba(20,19,15,0) 25%,rgba(20,19,15,.6) 52%,rgba(20,19,15,.97) 100%)'></div>
{marks()}<div class='top'>Cortexplor · {d['category']} · IA</div>{pill(1)}
<h1 class='abs' style='left:64px;top:730px;width:952px;font-size:84px;line-height:1.02;color:#fff'>{d['headline']}</h1>
<div class='abs' style='left:64px;top:1090px;width:940px;font-size:31px;line-height:1.36;color:#E4E8EE'>{d['dek']}</div>
{ticks(1, '#fff', 'rgba(255,255,255,.3)', bottom=62)}</div>""")

    x = d["s2"]
    s.append(f"""<div class='slide D'>
<div class='abs' style='left:0;top:0;width:1080px;height:420px;background:url({band}) center/cover'></div>
<div class='abs' style='left:0;top:0;width:1080px;height:420px;{gridl};background-size:90px 90px'></div>
<div class='top' style='color:#fff'>Cortexplor · {x['label']}</div>{pill(2)}
<div class='abs tag' style='left:64px;top:380px'>{x['label']}</div>
<h2 class='abs' style='left:64px;top:470px;width:952px;font-size:64px'>{x['title']}</h2>
<div class='abs body' style='left:64px;top:690px;width:952px'>{paras(x['body'])}</div>
{ticks(2, '#14130F', 'rgba(20,19,15,.15)', bottom=62)}</div>""")

    x = d["s3"]
    li = ""
    for k, p in enumerate(x["points"]):
        last = "border-bottom:2px solid rgba(255,255,255,.4);" if k == len(x["points"]) - 1 else ""
        li += f"<div style='display:flex;gap:24px;padding:22px 0;border-top:2px solid rgba(255,255,255,.4);{last}'>{ic(CHECK, 40, '#C9C7BF')}<span style='font-size:29px;line-height:1.35;color:#D5DAE0'><b style='display:block;font-size:34px;color:#fff;margin-bottom:4px'>{p['h']}</b>{p['t']}</span></div>"
    s.append(f"""<div class='slide D sl'>
<div class='grid' style='opacity:.5'></div>{marks()}
<div class='top'>Cortexplor · {x['label']}</div>{pill(3)}
<div class='abs' style='left:64px;top:170px;width:952px;font-size:66px;line-height:1;font-weight:700;letter-spacing:-.045em'>{x['title']}</div>
<div class='abs' style='left:64px;top:380px;width:900px;font-size:30px;line-height:1.4;color:#E4E8EE'>{x['body']}</div>
<div class='abs' style='left:64px;top:590px;width:952px'>{li}</div>
{ticks(3, '#fff', 'rgba(255,255,255,.28)', bottom=62)}</div>""")

    x = d["s4"]
    st = x["stat"]
    s.append(f"""<div class='slide D'>
<div class='abs' style='right:0;top:0;width:300px;height:1350px;background:url({strip}) center/cover'></div>
<div class='abs' style='right:0;top:0;width:300px;height:1350px;{gridl};background-size:75px 75px'></div>
<div class='top' style='color:#14130F;right:360px'>Cortexplor · {x['label']}</div><div class='pill' style='background:#fff;color:#14130F;right:36px'>4/{TOTAL}</div>
<div class='abs tag' style='left:64px;top:190px;background:#14130F;color:#fff'>{x['label']}</div>
<div class='abs' style='left:64px;top:270px;width:660px;font-size:58px;line-height:1.02;font-weight:700;letter-spacing:-.045em'>{x['title']}</div>
<div class='abs body' style='left:64px;top:520px;width:660px;font-size:29px;line-height:1.4'>{paras(x['body'])}</div>
<div class='abs' style='left:64px;top:1090px;width:660px;border-top:3px solid #14130F;padding-top:18px'><div style='font-size:64px;font-weight:700;letter-spacing:-.045em;line-height:1'>{st['big']}</div><div style='font:500 20px "IBM Plex Mono";letter-spacing:.1em;text-transform:uppercase;color:#6B6960;margin-top:10px'>{st['cap']}</div></div>
{ticks(4, '#14130F', 'rgba(20,19,15,.15)', bottom=62, right=360)}</div>""")

    x = d["s5"]
    cards = "".join(f"<div class='card'><div class='n'>{e['h']}</div><div class='d'>{e['t']}</div></div>" for e in x["items"])
    s.append(f"""<div class='slide D ik'>
<div class='top'>Cortexplor · {x['label']}</div>{pill(5)}
<h2 class='abs' style='left:64px;top:170px;width:952px;font-size:70px'>{x['title']}</h2>
<div class='abs' style='left:64px;top:400px;width:952px'>{cards}</div>
{ticks(5, '#EDECE8', 'rgba(237,236,232,.2)', bottom=62)}</div>""")

    fs = c.fs(104, 66)
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


STYLES_A = {"edicao": v_edicao, "terminal": v_terminal, "dossie": v_dossie, "duotone": v_duotone}
