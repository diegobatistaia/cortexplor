"""The daily pipeline, in two modes.

MODO ROUTINE (padrão hoje, sem custo de API)
    A inteligência é a própria sessão do Claude Code que roda na nuvem. Os
    scripts fazem só o trabalho determinístico, e a Routine faz a checagem e a
    redação lendo .claude/skills/redacao-diaria/SKILL.md.

        run brief     coleta, baixa o texto das fontes e escreve data/briefing.json
        run check     valida os rascunhos que a Routine escreveu (sem API, sem imagem)
        run finish    imagem + gate + build; publica ou manda para a fila
        run build     só regera o HTML

MODO API (para quando houver orçamento)
        run all       faz tudo sozinho chamando a API do Claude

Os dois modos terminam no mesmo lugar: gate, build, commit, push, deploy.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from ..engine import build as build_site
from ..engine import collect, draft, gate, images, seo, verify
from ..engine.config import load
from ..engine.llm import available as llm_available
from ..engine.store import (DATA, enqueue, gate_pass_rate, load_posts, log_gate, mark_seen,
                            queue_items, record_published, save_post)
from ..engine.util import isoformat, utcnow, word_count

BRIEFING = DATA / "briefing.json"

# Campos que todo rascunho precisa ter. A Routine escreve o arquivo; `check`
# confere antes de qualquer coisa cara acontecer.
REQUIRED_FIELDS = ["lang", "slug", "title", "dek", "meta_description", "keyword",
                   "category", "tags", "body", "image", "sources", "story_id", "status"]


def banner(text: str) -> None:
    print(f"\n=== {text}")


# --------------------------------------------------------------- modo routine

def cmd_brief(cfg, args) -> int:
    """Monta o briefing do dia: pautas plausíveis com o texto das fontes baixado."""
    banner("1. Coleta")
    stories = collect.run(cfg)
    minimum = cfg.get("quality_gate.min_independent_sources", 2)
    plausible = [s for s in stories if s["owner_count"] >= minimum]
    print(f"\n{len(stories)} pautas coletadas, {len(plausible)} com {minimum}+ fontes independentes")

    wanted = args.limit or cfg.posts_per_language(date.today())
    selected = plausible[:wanted * 3]

    banner("2. Baixando o texto integral das fontes")
    payload = []
    for story in selected:
        verify.gather(story)
        readable = [i for i in story["items"] if i.get("body")]
        print(f"  {len(readable)}/{len(story['items'])} fontes legíveis  {story['title'][:56]}")
        payload.append({
            "story_id": story["id"],
            "title": story["title"],
            "summary": story["summary"],
            "owners": story["owners"],
            "fingerprints": [i.get("fingerprint", "") for i in story["items"]],
            "sources": [{
                "name": i["source"], "owner": i["owner"], "url": i["url"],
                "title": i["title"], "published_at": i["published_at"],
                "text": i.get("body", ""),
            } for i in story["items"]],
        })

    BRIEFING.parent.mkdir(parents=True, exist_ok=True)
    BRIEFING.write_text(json.dumps({
        "generated_at": isoformat(utcnow()),
        "posts_per_language_today": wanted,
        "min_independent_sources": minimum,
        "languages": cfg.languages,
        "categories": [{"key": c["key"], "label": c["label"]}
                       for c in cfg.categories(cfg.default_language)],
        "word_count": cfg.get("quality_gate.word_count"),
        "meta_description_range": cfg.get("quality_gate.meta_description_range"),
        "stories": payload,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\ndata/briefing.json  {len(payload)} pauta(s), teto de {wanted} por idioma hoje")
    print("Agora leia .claude/skills/redacao-diaria/SKILL.md e escreva os rascunhos.")
    return 0


def draft_problems(post: dict, cfg) -> list[str]:
    """Erros estruturais que dá para pegar sem imagem e sem API."""
    problems = []
    missing = [f for f in REQUIRED_FIELDS if f not in post]
    if missing:
        return [f"faltam os campos {missing}"]

    if post["lang"] not in cfg.languages:
        problems.append(f"idioma '{post['lang']}' não está em site.languages")
    if not cfg.category(post["category"], post["lang"]):
        keys = [c["key"] for c in cfg.categories(cfg.default_language)]
        problems.append(f"categoria '{post['category']}' não existe; use uma de {keys}")

    lo, hi = cfg.get("quality_gate.meta_description_range", [150, 160])
    meta = (post.get("meta_description") or "").strip()
    if not lo <= len(meta) <= hi:
        problems.append(f"meta description com {len(meta)} caracteres, faixa {lo}-{hi}")

    blocks = post.get("body") or []
    if not blocks:
        problems.append("corpo vazio")
    else:
        if blocks[0].get("type") != "p":
            problems.append("o texto não começa com parágrafo")
        if not any(b.get("type") == "h2" for b in blocks):
            problems.append("sem nenhum H2")
        for i, block in enumerate(blocks):
            if set(block) != {"type", "text", "items"}:
                problems.append(f"bloco {i} deve ter exatamente type, text e items")
                break

    words = word_count(" ".join(
        b.get("text", "") + " " + " ".join(b.get("items", [])) for b in blocks))
    limits = cfg.get("quality_gate.word_count", {})
    if not limits.get("min", 600) <= words <= limits.get("max", 1000):
        problems.append(f"{words} palavras, faixa {limits.get('min')}-{limits.get('max')}")

    owners = {s.get("owner") for s in post.get("sources", []) if s.get("owner")}
    minimum = cfg.get("quality_gate.min_independent_sources", 2)
    if len(owners) < minimum:
        problems.append(f"{len(owners)} fonte(s) independente(s), mínimo {minimum}")

    text = " ".join(b.get("text", "") for b in blocks).lower()
    if not any(s.get("name", "").split()[0].lower() in text for s in post.get("sources", [])):
        problems.append("nenhuma fonte citada no corpo do texto")

    if len((post.get("image", {}).get("alt") or "").strip()) < 15:
        problems.append("image.alt ausente ou curto demais")
    if not (post.get("image", {}).get("query") or "").strip():
        problems.append("image.query vazio - é a busca no banco de imagens")

    return problems


def cmd_check(cfg, args) -> int:
    """Valida os rascunhos escritos pela Routine, antes do commit."""
    banner("Conferindo os rascunhos")
    drafts = [p for lang in cfg.languages for p in load_posts(lang)
              if p.get("status") == "draft"]
    if not drafts:
        print("Nenhum rascunho em content/. Nada a conferir.")
        return 0

    total_problems = 0
    for post in drafts:
        problems = draft_problems(post, cfg)
        total_problems += len(problems)
        mark = "OK   " if not problems else "AJUSTE"
        print(f"  {mark} [{post.get('lang', '??')}] {post.get('title', '(sem título)')[:58]}")
        for problem in problems:
            print(f"          - {problem}")

    print(f"\n{len(drafts)} rascunho(s), {total_problems} problema(s)")
    if total_problems:
        print("Corrija os arquivos e rode de novo antes de commitar.")
        return 1
    print("Pode commitar. O gate final roda no GitHub Actions.")
    return 0


def cmd_finish(cfg, args) -> int:
    """Imagem, gate e build sobre os rascunhos. É o que o Actions roda."""
    drafts = [p for lang in cfg.languages for p in load_posts(lang)
              if p.get("status") == "draft"]
    if not drafts:
        print("Nenhum rascunho para finalizar.")
        return 0

    banner(f"Finalizando {len(drafts)} rascunho(s)")
    published, queued = 0, 0
    for post in drafts:
        pool = [p for p in load_posts(post["lang"]) if p.get("status") == "published"]
        ok, reasons = publish_one(post, cfg, pool)
        if ok:
            published += 1
            print(f"  OK    [{post['lang']}] {post['title'][:58]}")
        else:
            queued += 1
            print(f"  FILA  [{post['lang']}] {post['title'][:58]}")
            for reason in reasons:
                print(f"          - {reason}")

    if BRIEFING.exists():
        briefing = json.loads(BRIEFING.read_text(encoding="utf-8"))
        used = {p["story_id"] for p in drafts}
        mark_seen([f for s in briefing.get("stories", []) if s["story_id"] in used
                   for f in s.get("fingerprints", []) if f])

    banner("Build do site")
    stats = build_site.run(cfg)
    print(f"  {stats['posts']} matérias e {stats['pages']} páginas geradas")

    banner("Resumo")
    print(f"  publicadas: {published}")
    print(f"  na fila de exceção: {queued}")
    return 0


# --------------------------------------------------------------- comum

def publish_one(post: dict, cfg, pool: list[dict]) -> tuple[bool, list[str]]:
    """Imagem -> SEO -> gate. Retorna (publicou, motivos)."""
    reasons: list[str] = []
    try:
        post = images.attach(post, cfg)
    except images.ImageError as exc:
        reasons.append(f"imagem: {exc}")

    enriched = seo.enrich(post, pool, cfg)
    source_texts = [s.get("text", "") for s in post.get("sources", []) if s.get("text")]
    verdict = gate.evaluate(enriched, cfg, source_texts)
    reasons += verdict["reasons"]

    log_gate({"id": post.get("id", post["slug"]), "lang": post["lang"],
              "passed": not reasons, "reasons": reasons})

    if reasons:
        enqueue(post, reasons)
        return (False, reasons)

    post["status"] = "published"
    post["published_at"] = post.get("published_at") or isoformat(utcnow())
    post["updated_at"] = isoformat(utcnow())
    # O texto integral das fontes serve à checagem, não ao site publicado.
    post["sources"] = [{k: v for k, v in s.items() if k != "text"} for s in post["sources"]]
    save_post(post)
    record_published({**post, "id": post.get("id", f"{post['lang']}-{post['slug']}"),
                      "url": seo.post_path(post)})
    return (True, [])


# ------------------------------------------------------------------ modo api

def cmd_all(cfg, args) -> int:
    if not llm_available():
        print("ANTHROPIC_API_KEY não configurada — este é o modo que cobra por uso.")
        print("Para o modo sem custo, use: brief -> (Routine escreve) -> check -> finish")
        return 1

    banner("1-2. Coleta e checagem cruzada")
    stories = collect.run(cfg)
    minimum = cfg.get("quality_gate.min_independent_sources", 2)
    plausible = [s for s in stories if s["owner_count"] >= minimum]
    wanted = args.limit or cfg.posts_per_language(date.today())
    checked = verify.run(plausible[:wanted * 3], cfg, limit=wanted * 3)
    verified = [c for c in checked if c["verdict"] == "verified"][:wanted]
    if not verified:
        print("\nNada verificado hoje. Nada é publicado — por definição.")
        return 0

    banner("3-6. Redação localizada, SEO e imagem")
    published, queued = 0, 0
    for story in verified:
        for lang in cfg.languages:
            pool = [p for p in load_posts(lang) if p.get("status") == "published"]
            post = draft.write(story, lang, cfg)
            ok, reasons = publish_one(post, cfg, pool)
            published += ok
            queued += not ok
            print(f"  {'OK   ' if ok else 'FILA '} [{lang}] {post['title'][:58]}")
            for reason in reasons:
                print(f"          - {reason}")

    banner("7. Build do site")
    stats = build_site.run(cfg)
    print(f"  {stats['posts']} matérias e {stats['pages']} páginas geradas")
    print(f"\npublicadas: {published} | na fila: {queued}")
    return 0


# --------------------------------------------------------------- informativos

def cmd_build(cfg, args) -> int:
    banner("Build do site")
    stats = build_site.run(cfg)
    for lang, counts in stats["languages"].items():
        print(f"  /{lang}/  {counts['posts']} matérias, {counts['pages']} páginas")
    return 0


def cmd_queue(cfg, args) -> int:
    items = queue_items()
    if not items:
        print("Fila de exceção vazia.")
        return 0
    print(f"{len(items)} item(ns) aguardando revisão:\n")
    for item in items:
        print(f"  [{item.get('lang')}] {item.get('title', '')[:70]}")
        print(f"      arquivo: data/queue/{item.get('id')}.json")
        for reason in item.get("reasons", []):
            print(f"      - {reason}")
        print()
    return 0


def cmd_status(cfg, args) -> int:
    allowed = cfg.posts_per_language(date.today())
    window = cfg.get("publishing.ramp_window_days", 14)
    rate, sample = gate_pass_rate(window)
    target = cfg.get("publishing.ramp_gate_pass_rate", 0.8)
    modo = "API (cobra por uso)" if llm_available() else "Routine (sem custo de API)"
    print(f"Modo: {modo}")
    print(f"Fase de publicação: até {allowed} post(s) por idioma por dia "
          f"({allowed * len(cfg.languages)} no total)")
    if not cfg.get("publishing.launch_date"):
        print("  ! publishing.launch_date vazio — o ramp só avança depois de preenchido")
    if sample:
        verdict = "estável" if rate >= target else "abaixo da meta"
        print(f"Gate nos últimos {window} dias: {rate:.0%} de aprovação "
              f"({sample} decisões) — {verdict}, meta {target:.0%}")
    else:
        print(f"Gate nos últimos {window} dias: sem dados ainda")
    print(f"Fila de exceção: {len(queue_items())} item(ns)")
    for lang in cfg.languages:
        posts = load_posts(lang)
        pub = [p for p in posts if p.get("status") == "published"]
        rascunhos = [p for p in posts if p.get("status") == "draft"]
        extra = f", {len(rascunhos)} rascunho(s)" if rascunhos else ""
        print(f"  /{lang}/  {len(pub)} matérias publicadas{extra}")
    return 0


COMMANDS = {
    "brief": cmd_brief,
    "check": cmd_check,
    "finish": cmd_finish,
    "build": cmd_build,
    "queue": cmd_queue,
    "status": cmd_status,
    "all": cmd_all,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline de conteúdo do site")
    parser.add_argument("command", choices=sorted(COMMANDS), nargs="?", default="status")
    parser.add_argument("--limit", type=int, default=0,
                        help="número de pautas a processar (padrão: o ritmo do dia)")
    args = parser.parse_args(argv)
    cfg = load()
    print(f"{cfg.get('site.name')} - {args.command}")
    return COMMANDS[args.command](cfg, args) or 0


if __name__ == "__main__":
    sys.exit(main())
