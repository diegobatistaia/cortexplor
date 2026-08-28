"""The daily pipeline. One command runs the whole thing.

    python -m scripts.pipeline.run all        # collect -> verify -> write -> gate -> build
    python -m scripts.pipeline.run collect    # only look for stories, print candidates
    python -m scripts.pipeline.run build      # only rebuild HTML from existing content
    python -m scripts.pipeline.run queue      # what is waiting for human review
    python -m scripts.pipeline.run status     # ramp phase and gate pass rate

`all` is what the scheduled Routine calls. Everything it publishes has passed
the quality gate; everything else lands in data/queue/ for the daily review.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

from ..engine import build as build_site
from ..engine import collect, draft, gate, images, seo, verify
from ..engine.config import load
from ..engine.llm import available as llm_available
from ..engine.store import (enqueue, gate_pass_rate, load_posts, log_gate, mark_seen,
                            queue_items, record_published, save_post)
from ..engine.util import isoformat, utcnow


def banner(text: str) -> None:
    print(f"\n=== {text}")


def cmd_collect(cfg, args) -> list[dict]:
    banner("1. Coleta")
    stories = collect.run(cfg)
    print(f"\n{len(stories)} pautas candidatas")
    return stories


def cmd_verify(cfg, args, stories=None) -> list[dict]:
    stories = stories if stories is not None else cmd_collect(cfg, args)
    banner("2. Checagem cruzada de fatos")
    minimum = cfg.get("quality_gate.min_independent_sources", 2)
    plausible = [s for s in stories if s["owner_count"] >= minimum]
    print(f"{len(plausible)} de {len(stories)} pautas têm {minimum}+ fontes independentes\n")
    wanted = args.limit or cfg.posts_per_language(date.today())
    checked = verify.run(plausible[:wanted * 3], cfg, limit=wanted * 3)
    verified = [c for c in checked if c["verdict"] == "verified"]
    print(f"\n{len(verified)} pautas verificadas")
    return verified[:wanted]


def publish_one(post: dict, cfg, pool: list[dict]) -> tuple[bool, list[str]]:
    """Image -> SEO -> gate. Returns (published, reasons)."""
    reasons: list[str] = []
    try:
        post = images.attach(post, cfg)
    except images.ImageError as exc:
        reasons.append(f"imagem: {exc}")

    enriched = seo.enrich(post, pool, cfg)
    source_texts = [s.get("body", "") for s in post.get("sources", []) if s.get("body")]
    verdict = gate.evaluate(enriched, cfg, source_texts)
    reasons += verdict["reasons"]

    log_gate({"id": post["id"], "lang": post["lang"], "passed": not reasons,
              "reasons": reasons})

    if reasons:
        enqueue(post, reasons)
        return (False, reasons)

    post["status"] = "published"
    post["published_at"] = post.get("published_at") or isoformat(utcnow())
    save_post(post)
    record_published({**post, "url": seo.post_path(post)})
    return (True, [])


def cmd_all(cfg, args) -> int:
    if not llm_available():
        print("ANTHROPIC_API_KEY não configurada — a checagem e a redação precisam dela.")
        print("Sem a chave, só 'collect' e 'build' funcionam.")
        return 1

    stories = cmd_verify(cfg, args)
    if not stories:
        print("\nNada verificado hoje. Nada é publicado — por definição.")
        return 0

    banner("3-6. Redação localizada, SEO e imagem")
    published, queued = 0, 0
    for story in stories:
        for lang in cfg.languages:
            pool = [p for p in load_posts(lang) if p.get("status") == "published"]
            post = draft.write(story, lang, cfg)
            ok, reasons = publish_one(post, cfg, pool)
            if ok:
                published += 1
                print(f"  OK    [{lang}] {post['title'][:60]}")
            else:
                queued += 1
                print(f"  FILA  [{lang}] {post['title'][:60]}")
                for reason in reasons:
                    print(f"          - {reason}")

    mark_seen([i["fingerprint"] for s in stories for i in s.get("items", [])
               if i.get("fingerprint")])

    banner("7. Build do site")
    stats = build_site.run(cfg)
    print(f"  {stats['posts']} matérias e {stats['pages']} páginas geradas")

    banner("Resumo")
    print(f"  publicadas: {published}")
    print(f"  na fila de exceção: {queued}")
    if queued:
        print("  revise com: python -m scripts.pipeline.run queue")
    return 0


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
        posts = [p for p in load_posts(lang) if p.get("status") == "published"]
        print(f"  /{lang}/  {len(posts)} matérias publicadas")
    return 0


COMMANDS = {
    "all": cmd_all,
    "collect": lambda cfg, args: (cmd_collect(cfg, args), 0)[1],
    "verify": lambda cfg, args: (cmd_verify(cfg, args), 0)[1],
    "build": cmd_build,
    "queue": cmd_queue,
    "status": cmd_status,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Pipeline de conteúdo do site")
    parser.add_argument("command", choices=sorted(COMMANDS), nargs="?", default="all")
    parser.add_argument("--limit", type=int, default=0,
                        help="número de pautas a processar (padrão: o ritmo do dia)")
    args = parser.parse_args(argv)
    cfg = load()
    print(f"{cfg.get('site.name')} - {args.command}")
    return COMMANDS[args.command](cfg, args) or 0


if __name__ == "__main__":
    sys.exit(main())
