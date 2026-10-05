#!/usr/bin/env python3
"""Redação do Instagram: da matéria publicada ao spec do carrossel + legenda.

O texto (slides, legenda, texto alternativo) é escrito pela redação (Routine /
Claude) seguindo a skill `instagram-carrossel`. Este script faz a parte
determinística em volta dela:

    python scripts/social/redacao.py prepare <slug> [--lang pt] [--force]
        Cria social/specs/<slug>.json com os campos que saem direto da matéria
        (data, número, editoria, foto, fontes, variante da chamada final) e
        deixa vazios os campos que a redação escreve.

    python scripts/social/redacao.py check <slug> [--no-render]
    python scripts/social/redacao.py check --all [--no-render]
        Valida o spec: campos, orçamentos de texto, números e fontes contra a
        matéria, voz, regras da legenda (seção 4 de social/INSTAGRAM.md) e, por
        fim, se o texto cabe nos slides dos 8 estilos. Sai com código 1 se
        houver erro.

    python scripts/social/redacao.py caption <slug>
        Monta a legenda final e o texto alternativo em social/out/<slug>/.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "social" / "specs"
OUT = ROOT / "social" / "out"
CONTENT = ROOT / "content"
TZ = ZoneInfo("America/Sao_Paulo")  # site.config.yaml: site.timezone

MONTHS = {
    "pt": "jan fev mar abr mai jun jul ago set out nov dez".split(),
    "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),
}
# Rótulo curto da editoria no slide (o rótulo do site é longo demais para o selo).
CATEGORY = {
    "pt": {"modelos": "Modelos", "mercado": "Mercado", "brasil": "IA no Brasil",
           "aplicacoes": "Aplicações", "politica": "Regulação"},
    "en": {"models": "Models", "market": "Market", "applications": "Applications",
           "policy": "Policy"},
}
LINK = {"pt": "Matéria completa no link da bio.", "en": "Full story: link in bio."}
CTA_B = {
    "pt": "Salve para consultar depois e envie a quem acompanha IA.",
    "en": "Save it for later and send it to someone following AI.",
}
BRAND_TAG = "#cortexplor"

# Orçamentos em caracteres, calibrados nos dois carrosséis aprovados com folga.
# A palavra final é da checagem de encaixe (fit.py), que mede no navegador.
LIMITS = {
    "headline": 70, "dek": 170, "kicker": 30, "title": 70, "para": 300,
    "s3_body": 200, "point_h": 26, "item_h": 10, "point_t": 160,
    "stat_big": 14, "stat_cap": 50, "stamp_line": 14,
}
HOOK_MAX = 125
CAPTION_MIN, CAPTION_MAX = 600, 800
ALT_MAX = 100

BLACKLIST = {
    "pt": [r"revolucion\w*", r"jornada", r"ecossistema", r"alavanc\w*", r"potencializ\w*",
           r"pr[óo]ximo n[íi]vel", r"transformar o neg[óo]cio", r"chave do sucesso",
           r"destrav\w*", r"desbloque\w*", r"game.?changer", r"no fim do dia",
           r"n[ãa]o [ée] apenas", r"em um mundo cada vez mais", r"vamos mergulhar",
           r"nesse cen[áa]rio", r"impressionante\w*", r"gigantesc\w*", r"incr[íi]ve\w*",
           r"surpreendente\w*", r"resta saber"],
    "en": [r"revolution\w*", r"journey", r"ecosystem", r"leverag\w*", r"next level",
           r"game.?changer", r"unlock\w*", r"at the end of the day", r"not just \w+,? (it'?s|but)",
           r"in an increasingly", r"let'?s dive", r"impressive", r"huge", r"incredible",
           r"amazing", r"surprising\w*", r"remains to be seen"],
}
# Fala direta com o leitor e chamada para ação: só a chamada final pode.
DIRECT = {
    "pt": [r"voc[êe]s?", r"a gente", r"confira", r"n[ãa]o perca", r"clique", r"comente\w*",
           r"pensa comigo"],
    "en": [r"you", r"your\w*", r"check out", r"don'?t miss", r"click", r"comment below"],
}
ATTRIB = {
    "pt": r"segundo|de acordo com|afirm|diz|disse|informou|anunci|relat|comunicado|divulg",
    "en": r"according to|said|says|told|announced|report|statement|disclosed",
}
GENERIC_TAGS = {"#tecnologia", "#tech", "#technology", "#inovacao", "#innovation", "#love",
                "#instagood", "#news", "#noticias", "#viral", "#trending", "#ia", "#ai"}
URL_RE = re.compile(r"https?://|www\.|\b[\w-]+\.(com|com\.br|br|ai|io|net|org|co)\b", re.I)
# Número que é parte de nome de produto ("GPT-6 Astra", "Gemini 4") não pede fonte.
NAME_NUM = re.compile(r"\b[A-Z][\w.]*[- ]\d+(?:\.\d+)*\b")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


# ----------------------------------------------------------------------------
# Leitura
# ----------------------------------------------------------------------------
def load_post(lang: str, slug: str) -> dict:
    path = CONTENT / lang / f"{slug}.json"
    if not path.exists():
        raise SystemExit(f"matéria não encontrada: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_spec(slug: str) -> dict:
    path = SPECS / f"{slug}.json"
    if not path.exists():
        raise SystemExit(f"spec não encontrado: {path.relative_to(ROOT)} (rode prepare)")
    return json.loads(path.read_text(encoding="utf-8"))


def specs_of(lang: str) -> list[dict]:
    out = []
    for p in sorted(SPECS.glob("*.json")):
        if p.name.startswith("_"):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("lang", "pt") == lang:
            out.append(d)
    return out


def post_text(post: dict) -> str:
    parts = [post.get("title", ""), post.get("dek", "")]
    for b in post.get("body", []):
        parts.append(b.get("text", ""))
        parts.extend(b.get("items", []))
    return "\n".join(parts)


def cta_variant(no: int) -> str:
    """A, B, A, B… pela ordem de publicação na conta (o `no` é sequencial por idioma)."""
    return "A" if no % 2 == 1 else "B"


# ----------------------------------------------------------------------------
# prepare
# ----------------------------------------------------------------------------
def cmd_prepare(args) -> int:
    lang, slug = args.lang, args.slug
    path = SPECS / f"{slug}.json"
    if path.exists() and not args.force:
        print(f"{path.relative_to(ROOT)} já existe; use --force para recriar do zero.")
        return 1
    post = load_post(lang, slug)
    img = post.get("image") or {}
    if not img.get("path"):
        print("a matéria ainda não tem foto (o workflow Finalizar põe a foto ao publicar).")
        return 1
    if post.get("status") != "published":
        print(f"aviso: a matéria está com status '{post.get('status')}', não 'published'.")

    when = datetime.fromisoformat(post.get("published_at") or post.get("updated_at")).astimezone(TZ)
    nos = [d.get("no", 0) for d in specs_of(lang) if d.get("slug") != slug]
    no = max(nos, default=0) + 1
    variant = cta_variant(no)
    category = CATEGORY.get(lang, {}).get(post.get("category"), post.get("category", ""))

    spec = {
        "slug": slug,
        "lang": lang,
        "date": f"{when.day:02d} {MONTHS[lang][when.month - 1]} {when.year}",
        "no": no,
        "category": category,
        "kicker": "",
        "headline": "",
        "headline_hl": "",
        "dek": "",
        "image": {"path": img["path"].lstrip("/"), "credit": img.get("credit", ""), "pos": "50% 50%"},
        "stamp": "",
        "sources": [s["name"] for s in post.get("sources", [])],
        "s2": {"label": "O que aconteceu" if lang == "pt" else "What happened", "title": "", "body": ["", ""]},
        "s3": {"label": "Como funciona" if lang == "pt" else "How it works", "title": "", "body": "",
               "points": [{"h": "", "t": ""} for _ in range(3)]},
        "s4": {"label": "Por que importa" if lang == "pt" else "Why it matters", "title": "",
               "body": ["", ""], "stat": {"big": "", "cap": ""}},
        "s5": {"label": "O que vem agora" if lang == "pt" else "What comes next", "title": "",
               "items": [{"h": "", "t": ""} for _ in range(3)]},
        "caption": {"hook": "", "body": ["", ""], "cta_variant": variant,
                    "cta": CTA_B[lang] if variant == "B" else "", "hashtags": [BRAND_TAG, "", "", ""]},
        "alt": [f"Slide {i}: " for i in range(1, 7)],
    }
    SPECS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"criado {path.relative_to(ROOT)} (nº {no}, chamada final {variant})")
    print(f"matéria: content/{lang}/{slug}.json")
    print("Preencha os campos vazios e rode: python scripts/social/redacao.py check " + slug)
    return 0


# ----------------------------------------------------------------------------
# check
# ----------------------------------------------------------------------------
def fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def numbers(text: str) -> set[str]:
    """Números do texto, normalizados ('1,5' e '1.5' viram '1.5'; '1.000' vira '1000')."""
    out = set()
    for tok in re.findall(r"\d+(?:[.,]\d+)*", text):
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", tok):  # milhar no padrão PT
            tok = tok.replace(".", "")
        elif re.fullmatch(r"\d{1,3}(?:,\d{3})+", tok):  # milhar no padrão EN
            tok = tok.replace(",", "")
        out.add(tok.replace(",", "."))
    return out


def strip_dates(text: str) -> tuple[str, set[str]]:
    """Tira datas dd/mm do texto e devolve só os dias (o mês costuma vir por extenso na matéria)."""
    days = set()

    def keep_day(m):
        days.add(str(int(m.group(1))))
        return " "

    return re.sub(r"\b(\d{1,2})/(\d{1,2})\b", keep_day, text), days


def slide_texts(spec: dict) -> list[tuple[str, str]]:
    """(onde, texto) de todo texto editorial dos slides."""
    t = [("headline", spec.get("headline", "")), ("dek", spec.get("dek", "")),
         ("kicker", spec.get("kicker", "")), ("stamp", spec.get("stamp", ""))]
    for k in ("s2", "s3", "s4", "s5"):
        s = spec.get(k, {})
        t.append((f"{k}.title", s.get("title", "")))
        body = s.get("body", [])
        for i, p in enumerate(body if isinstance(body, list) else [body]):
            t.append((f"{k}.body[{i}]", p))
        for key in ("points", "items"):
            for i, p in enumerate(s.get(key, [])):
                t.append((f"{k}.{key}[{i}].h", p.get("h", "")))
                t.append((f"{k}.{key}[{i}].t", p.get("t", "")))
        if "stat" in s:
            t.append((f"{k}.stat.big", s["stat"].get("big", "")))
            t.append((f"{k}.stat.cap", s["stat"].get("cap", "")))
    return t


def assemble(spec: dict) -> tuple[str, str]:
    """(texto da legenda sem hashtags, linha de hashtags)."""
    c = spec["caption"]
    lang = spec.get("lang", "pt")
    parts = [c["hook"], *c["body"], c["cta"], LINK[lang]]
    return "\n\n".join(p.strip() for p in parts if p.strip()), " ".join(c["hashtags"])


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) >= 40]


def check_spec(spec: dict, render: bool = True) -> tuple[list[str], list[str]]:
    err: list[str] = []
    warn: list[str] = []
    lang = spec.get("lang", "pt")
    slug = spec.get("slug", "")
    try:
        post = load_post(lang, slug)
    except SystemExit as e:
        return [str(e)], []
    article = post_text(post)

    # --- campos e orçamentos dos slides --------------------------------------
    def need(where, text, limit=None):
        if not isinstance(text, str) or not text.strip():
            err.append(f"{where}: vazio")
        elif limit and len(text) > limit:
            err.append(f"{where}: {len(text)} caracteres (máx. {limit})")

    need("headline", spec.get("headline"), LIMITS["headline"])
    need("dek", spec.get("dek"), LIMITS["dek"])
    need("kicker", spec.get("kicker"), LIMITS["kicker"])
    need("category", spec.get("category"))
    hl = spec.get("headline_hl", "")
    if hl and hl not in spec.get("headline", ""):
        err.append("headline_hl: o trecho destacado não está na manchete")
    stamp = spec.get("stamp", "")
    need("stamp", stamp)
    lines = stamp.split("<br>")
    if len(lines) > 2 or any(len(x) > LIMITS["stamp_line"] for x in lines):
        err.append(f"stamp: até 2 linhas separadas por <br>, {LIMITS['stamp_line']} caracteres cada")
    if not spec.get("image", {}).get("path") or not (ROOT / spec["image"]["path"]).exists():
        err.append("image.path: foto não encontrada")

    for k in ("s2", "s3", "s4", "s5"):
        s = spec.get(k) or {}
        need(f"{k}.label", s.get("label"))
        need(f"{k}.title", s.get("title"), LIMITS["title"])
    for k in ("s2", "s4"):
        body = spec.get(k, {}).get("body", [])
        if not isinstance(body, list) or len(body) != 2:
            err.append(f"{k}.body: precisa de exatamente 2 parágrafos")
        else:
            for i, p in enumerate(body):
                need(f"{k}.body[{i}]", p, LIMITS["para"])
    need("s3.body", spec.get("s3", {}).get("body"), LIMITS["s3_body"])
    for k, key, hmax in (("s3", "points", LIMITS["point_h"]), ("s5", "items", LIMITS["item_h"])):
        lst = spec.get(k, {}).get(key, [])
        if len(lst) != 3:
            err.append(f"{k}.{key}: precisa de exatamente 3")
        for i, p in enumerate(lst):
            need(f"{k}.{key}[{i}].h", p.get("h"), hmax)
            need(f"{k}.{key}[{i}].t", p.get("t"), LIMITS["point_t"])
    stat = spec.get("s4", {}).get("stat", {})
    need("s4.stat.big", stat.get("big"), LIMITS["stat_big"])
    need("s4.stat.cap", stat.get("cap"), LIMITS["stat_cap"])

    # --- fontes ---------------------------------------------------------------
    names = {s["name"] for s in post.get("sources", [])}
    spec_src = set(spec.get("sources", []))
    if spec_src - names:
        err.append(f"sources: fora da matéria: {', '.join(sorted(spec_src - names))}")
    if names - spec_src:
        err.append(f"sources: faltam fontes da matéria: {', '.join(sorted(names - spec_src))}")

    def short_names():
        out = set()
        for n in names:
            out.add(n.lower())
            base = re.sub(r"\s+(technology|ai|tech)$", "", n.lower())
            out.update({base, re.sub(r"^the\s+", "", base)})  # "The Guardian" citado como "Guardian"
        return out

    srcs = short_names()
    attrib = re.compile(ATTRIB[lang], re.I)

    # Todo trecho com número precisa dizer de onde veio.
    for where, text in slide_texts(spec):
        if not text or where in ("stamp", "kicker", "headline") or where.endswith((".h", "stat.big", "stat.cap", ".title")):
            continue
        if re.search(r"\d", NAME_NUM.sub("", text)) and not (any(s in text.lower() for s in srcs) or attrib.search(text)):
            err.append(f"{where}: tem número mas não diz a fonte (atribua entre parênteses)")

    # --- números: nenhum que não esteja na matéria ----------------------------
    art_clean, art_days = strip_dates(article)
    art_nums = numbers(art_clean) | art_days | {str(int(n)) for n in numbers(art_clean) if n.isdigit()}
    caption = spec.get("caption") or {}
    editorial = slide_texts(spec) + [("caption.hook", caption.get("hook", ""))]
    editorial += [(f"caption.body[{i}]", p) for i, p in enumerate(caption.get("body", []))]
    editorial += [(f"alt[{i}]", re.sub(r"^Slide \d+:", "", a)) for i, a in enumerate(spec.get("alt", []))]
    for where, text in editorial:
        clean, days = strip_dates(text or "")
        for n in sorted(numbers(clean)):
            if n not in art_nums and (n.lstrip("0") or "0") not in art_nums:
                err.append(f"{where}: número '{n}' não aparece na matéria")
        # Data dd/mm pode ser deduzida ("um dia depois" de 30/09): aviso, não erro.
        for d in sorted(days - art_days - art_nums):
            warn.append(f"{where}: o dia {d} não aparece escrito na matéria; confira se a data decorre do texto")

    # --- voz ------------------------------------------------------------------
    texts = editorial + [("caption.hashtags", " ".join(caption.get("hashtags", [])))]
    for where, text in texts:
        if not text:
            continue
        for pat in BLACKLIST[lang]:
            m = re.search(rf"\b{pat}\b", text, re.I)
            if m:
                err.append(f"{where}: lista negra da voz: '{m.group(0)}'")
        for pat in DIRECT[lang]:
            m = re.search(rf"\b{pat}\b", text, re.I)
            if m:
                err.append(f"{where}: fala direta com o leitor: '{m.group(0)}' (só a chamada final pode)")
        if "!" in text:
            err.append(f"{where}: ponto de exclamação")
        if URL_RE.search(text):
            err.append(f"{where}: link ou domínio (o aviso é sempre 'link na bio')")

    # --- legenda --------------------------------------------------------------
    hook = caption.get("hook", "")
    body = caption.get("body", [])
    need("caption.hook", hook, HOOK_MAX)
    if not isinstance(body, list) or not 2 <= len(body) <= 3:
        err.append("caption.body: 2 ou 3 parágrafos")
    else:
        for i, p in enumerate(body):
            need(f"caption.body[{i}]", p)
    expected = cta_variant(int(spec.get("no", 1)))
    variant = caption.get("cta_variant")
    cta = caption.get("cta", "")
    if variant != expected:
        err.append(f"caption.cta_variant: deveria ser {expected} (alterna A/B pelo nº {spec.get('no')})")
    if variant == "B" and cta != CTA_B[lang]:
        err.append(f"caption.cta: a variante B é fixa: \"{CTA_B[lang]}\"")
    if variant == "A":
        if not cta.strip().endswith("?") or cta.count("?") != 1:
            err.append("caption.cta: a variante A é uma pergunta só, terminada em '?'")
        for pat in BLACKLIST[lang]:
            if re.search(rf"\b{pat}\b", cta, re.I):
                err.append(f"caption.cta: lista negra da voz: '{pat}'")
        if URL_RE.search(cta) or "!" in cta:
            err.append("caption.cta: sem link e sem exclamação")
    if hook and body and cta:
        text, _ = assemble(spec)
        if not CAPTION_MIN <= len(text) <= CAPTION_MAX:
            err.append(f"legenda: {len(text)} caracteres sem as hashtags (faixa {CAPTION_MIN}-{CAPTION_MAX})")
        if len(EMOJI_RE.findall(text)) > 1:
            err.append("legenda: no máximo 1 emoji")
        if lang == "pt" and not re.search(r"[áàâãéêíóôõúç]", text, re.I):
            err.append("legenda: sem nenhum acento; português sem acento não passa")
        slides_all = " ".join(t for _, t in slide_texts(spec))
        for s in sentences(" ".join([hook, *body])):
            if s in slides_all:
                err.append(f"legenda: repete frase do carrossel: \"{s[:60]}…\"")
        kw = post.get("keyword", "")
        if kw and fold(kw) not in fold(hook):
            hl_term = spec.get("headline_hl", "")
            if not hl_term or fold(hl_term) not in fold(hook):
                warn.append(f"caption.hook: não cita a palavra-chave da matéria ('{kw}')")

    tags = [t for t in caption.get("hashtags", []) if t]
    if not 2 <= len(tags) <= 4:
        err.append(f"caption.hashtags: {len(tags)} (de 2 a 4: a da marca + até 3 do tema)")
    if not tags or tags[0] != BRAND_TAG:
        err.append(f"caption.hashtags: a primeira é {BRAND_TAG}")
    for t in tags:
        if not re.fullmatch(r"#[a-z0-9_]+", t):
            err.append(f"caption.hashtags: '{t}' (só minúsculas, sem acento nem espaço)")
        if t in GENERIC_TAGS:
            err.append(f"caption.hashtags: '{t}' é genérica demais")
    if len(set(tags)) != len(tags):
        err.append("caption.hashtags: repetida")

    # --- texto alternativo ----------------------------------------------------
    alt = spec.get("alt", [])
    if len(alt) != 6:
        err.append("alt: precisa de 6 textos, um por slide")
    for i, a in enumerate(alt, 1):
        if not re.match(rf"Slide {i}: \S", a or ""):
            err.append(f"alt[{i - 1}]: começa com 'Slide {i}: ' seguido da descrição")
        elif len(a) > ALT_MAX:
            err.append(f"alt[{i - 1}]: {len(a)} caracteres (máx. {ALT_MAX})")
    subject = spec.get("headline_hl", "")
    if subject and alt and not any(fold(subject) in fold(a) for a in alt):
        warn.append(f"alt: nenhum texto alternativo cita o assunto ('{subject}')")

    # --- encaixe nos slides -----------------------------------------------------
    if render and not err:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import carousel  # noqa: E402
        import fit  # noqa: E402

        err.extend(f"encaixe {p}" for p in fit.fit_problems(spec, carousel.STYLES))
    elif render:
        warn.append("encaixe nos slides não conferido: corrija os erros acima primeiro")
    try:
        from rotation import photo_report

        warn.extend(photo_report(spec)[0])
    except Exception as ex:  # foto ausente já é erro acima
        warn.append(f"foto não analisada: {ex}")
    return err, warn


def cmd_check(args) -> int:
    if args.all:
        slugs = sorted(p.stem for p in SPECS.glob("*.json") if not p.name.startswith("_"))
    else:
        slugs = [args.slug]
    bad = 0
    for slug in slugs:
        err, warn = check_spec(load_spec(slug), render=not args.no_render)
        print(f"{'OK ' if not err else 'ERRO'} {slug}")
        for e in err:
            print(f"  ✗ {e}")
        for w in warn:
            print(f"  ! {w}")
        bad += bool(err)
    return 1 if bad else 0


# ----------------------------------------------------------------------------
# caption
# ----------------------------------------------------------------------------
def cmd_caption(args) -> int:
    spec = load_spec(args.slug)
    err, _ = check_spec(spec, render=False)
    if err:
        print("o spec não passa na checagem; rode check primeiro.")
        return 1
    text, tags = assemble(spec)
    folder = OUT / args.slug
    folder.mkdir(parents=True, exist_ok=True)
    lang = spec.get("lang", "pt")
    cap = folder / f"legenda-{lang}.txt"
    cap.write_text(f"{text}\n\n{tags}\n", encoding="utf-8")
    alt = folder / f"alt-{lang}.txt"
    alt.write_text("\n".join(spec["alt"]) + "\n", encoding="utf-8")
    print(f"{text}\n\n{tags}\n")
    print(f"({len(text)} caracteres sem as hashtags; chamada {spec['caption']['cta_variant']})")
    print(cap.relative_to(ROOT))
    print(alt.relative_to(ROOT))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("slug")
    p.add_argument("--lang", default="pt", choices=sorted(LINK))
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("check")
    p.add_argument("slug", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--no-render", action="store_true")
    p = sub.add_parser("caption")
    p.add_argument("slug")
    args = ap.parse_args(argv)
    if args.cmd == "check" and not (args.slug or args.all):
        ap.error("check precisa de um slug ou --all")
    return {"prepare": cmd_prepare, "check": cmd_check, "caption": cmd_caption}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
