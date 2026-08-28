#!/usr/bin/env python3
"""Check everything that can be checked without spending an API call.

Config validity, interface strings, template rendering, SEO output and every
branch of the quality gate. Run it after touching the engine or the config.

    python scripts/tools/selfcheck.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.engine import gate, seo  # noqa: E402
from scripts.engine.images import query_ladder  # noqa: E402
from scripts.engine.store import queue_key  # noqa: E402
from scripts.pipeline.run import draft_problems  # noqa: E402
from scripts.engine.config import ConfigError, ROOT, load  # noqa: E402
from scripts.engine.i18n import missing_keys, strings  # noqa: E402
from scripts.engine.render import base_context, environment, humanize, render  # noqa: E402
from scripts.engine.util import isoformat, longest_common_run, similarity, utcnow  # noqa: E402

FAILURES: list[str] = []
CHECKS = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FALHA {label}{(' - ' + detail) if detail else ''}")
        FAILURES.append(label)


def fixture(cfg, **overrides) -> dict:
    body = [{"type": "p", "text": " ".join(["palavra"] * 120), "items": []},
            {"type": "p", "text": " ".join(["texto"] * 120), "items": []},
            {"type": "h2", "text": "Um subtitulo", "items": []},
            {"type": "p", "text": " ".join(["conteudo"] * 200), "items": []},
            {"type": "p", "text": "Segundo a Reuters, o numero foi confirmado. "
                                  + " ".join(["fecho"] * 250), "items": []}]
    post = {
        "id": "pt-fixture", "lang": "pt", "slug": "fixture", "story_id": "s1",
        "title": "Titulo de teste do gate de qualidade", "dek": "Linha de apoio.",
        "meta_description": "M" * 155, "keyword": "inteligencia artificial",
        "category": "modelos", "tags": ["ia"], "body": body,
        "image": {"path": "/assets/img/x.jpg", "alt": "Descricao suficientemente longa da imagem",
                  "credit": "Autor / Unsplash"},
        "sources": [{"name": "Reuters", "owner": "reuters", "url": "https://r.com/", "title": "A"},
                    {"name": "Associated Press", "owner": "ap", "url": "https://ap.com/", "title": "B"}],
        "published_at": isoformat(utcnow()), "updated_at": isoformat(utcnow()),
        "status": "published",
    }
    post.update(overrides)
    return post


def main() -> int:
    print("Config")
    try:
        cfg = load()
        check("site.config.yaml carrega e valida", True)
    except ConfigError as exc:
        check("site.config.yaml carrega e valida", False, str(exc))
        return 1

    check("idiomas configurados", len(cfg.languages) >= 1)
    check("categorias cobrem todos os idiomas",
          all(len(cfg.categories(l)) == len(cfg.get("editorial.categories"))
              for l in cfg.languages))
    check("gate exige 2+ fontes independentes",
          cfg.get("quality_gate.min_independent_sources") >= 2)
    check("todas as fontes RSS têm owner",
          all(s.get("owner") for s in cfg.get("sources.rss", [])))
    owners = [s["owner"] for s in cfg.get("sources.rss", [])]
    check("há pelo menos 2 grupos independentes por idioma",
          all(len({s["owner"] for s in cfg.get("sources.rss", []) if s.get("lang") == l}) >= 2
              for l in cfg.languages))

    print("\nTextos de interface")
    gaps = missing_keys()
    check("nenhum idioma com string faltando", not gaps, str(gaps))
    for lang in cfg.languages:
        check(f"strings de {lang} carregam", bool(strings(lang).most_read))

    print("\nAssets do logo")
    for name in ("cortexplor-logo-color.svg", "cortexplor-logo-white.svg",
                 "cortexplor-icon-color.svg", "favicon.ico", "favicon.svg",
                 "icon-192.png", "icon-512.png"):
        path = ROOT / "assets" / "logo" / name
        check(f"{name} existe e não está vazio", path.exists() and path.stat().st_size > 200)
    check("webfonts auto-hospedadas",
          len(list((ROOT / "assets" / "fonts").glob("*.woff2"))) >= 2)

    print("\nSEO")
    post = seo.enrich(fixture(cfg), [], cfg)
    check("URL do post no formato /lang/slug/", post["url"] == "/pt/fixture/")
    check("canonical absoluto", post["canonical"].startswith("https://"))
    check("schema NewsArticle gerado", '"@type":"NewsArticle"' in post["schema_news_article"])
    check("JSON-LD escapa < e >", "<" not in post["schema_news_article"])
    check("title tag leva o sufixo de nicho",
          "Cortexplor" in post["title_tag"] and post["title"] in post["title_tag"])
    other = fixture(cfg, lang="en", slug="fixture-en", id="en-fixture")
    alts = seo.alternates(post, [post, other], cfg)
    check("hreflang liga as versões da mesma pauta", len(alts) == 2)

    print("\nGate de qualidade")
    verdict = gate.evaluate(post, cfg, [])
    check("post correto passa", verdict["passed"], "; ".join(verdict["reasons"]))

    cases = {
        "fonte única reprova": fixture(cfg, sources=[
            {"name": "Reuters", "owner": "reuters", "url": "https://r.com/", "title": "A"}]),
        "texto curto reprova": fixture(cfg, body=[{"type": "p", "text": "curto", "items": []}]),
        "meta description fora da faixa reprova": fixture(cfg, meta_description="curta"),
        "sem H2 reprova": fixture(cfg, body=[
            {"type": "p", "text": " ".join(["palavra"] * 700), "items": []}]),
        "alt-text ausente reprova": fixture(cfg, image={"path": "/x.jpg", "alt": "",
                                                        "credit": "A / Unsplash"}),
        "imagem sem atribuição reprova": fixture(cfg, image={
            "path": "/x.jpg", "alt": "Descricao suficientemente longa da imagem", "credit": ""}),
    }
    for label, broken in cases.items():
        enriched = seo.enrich(broken, [], cfg)
        check(label, not gate.evaluate(enriched, cfg, [])["passed"])

    # The internal-links rule must not block the site's very first posts, but
    # must apply once there is something to link to.
    neighbour = fixture(cfg, slug="vizinho", id="pt-vizinho", title="Outra materia",
                        tags=["assunto-sem-relacao"], category="politica")
    lonely = seo.enrich(fixture(cfg), [neighbour], cfg)
    check("site vazio não reprova por link interno",
          gate.evaluate(seo.enrich(fixture(cfg), [], cfg), cfg, [])["passed"])
    check("sem parente tematico, cai para as mais recentes",
          len(lonely["related"]) >= 1, "materia boa nao pode parar por falta de vizinho")

    source_text = " ".join(["conteudo"] * 200)
    copied = seo.enrich(fixture(cfg), [], cfg)
    check("cópia da fonte reprova por similaridade",
          not gate.evaluate(copied, cfg, [source_text])["passed"])
    check("similaridade detecta reciclagem",
          similarity("um dois tres quatro cinco seis", "um dois tres quatro cinco seis") == 1.0)
    check("trecho literal é medido",
          longest_common_run("a b c d e f g", "z a b c d e f g z") == 7)

    print("\nRascunhos do modo Routine")
    frase = ("Segundo a TechCrunch, o fato principal foi confirmado por duas fontes "
             "independentes antes da publicação, e este texto valida a estrutura. ")
    corpo = [{"type": "p", "text": frase * 6, "items": []} for _ in range(5)]
    corpo.insert(2, {"type": "h2", "text": "Subtítulo", "items": []})
    rascunho = {
        "lang": "pt", "slug": "s", "story_id": "x", "title": "T", "dek": "d",
        "keyword": "ia", "category": "modelos", "tags": ["ia"], "body": corpo,
        "meta_description": ("Matéria de teste usada para validar toda a estrutura do arquivo "
                             "de rascunho que é aceita pelo pipeline automatizado do site de "
                             "notícias sobre IA hoje."),
        "image": {"query": "tech", "alt": "Ilustração abstrata representando tecnologia"},
        "sources": [{"name": "TechCrunch", "owner": "techcrunch", "url": "u", "title": "t"},
                    {"name": "MIT Technology Review", "owner": "mit-tr", "url": "u", "title": "t"}],
        "status": "draft",
    }
    check("rascunho correto passa", not draft_problems(rascunho, cfg),
          "; ".join(draft_problems(rascunho, cfg)))
    quebrados = {
        "campo faltando reprova": {k: v for k, v in rascunho.items() if k != "body"},
        "categoria inexistente reprova": {**rascunho, "category": "nao-existe"},
        "fonte unica reprova": {**rascunho, "sources": rascunho["sources"][:1]},
        "comecar com H2 reprova": {**rascunho, "body": corpo[2:] + corpo[:2]},
        "alt-text curto reprova": {**rascunho, "image": {"query": "t", "alt": "curto"}},
    }
    for label, broken in quebrados.items():
        check(label, bool(draft_problems(broken, cfg)))

    # Dois bugs que só apareceram no primeiro fechamento real.
    print("\nFila e busca de imagem")
    check("fila usa chave única por idioma",
          queue_key({"lang": "pt", "slug": "x"}) != queue_key({"lang": "es", "slug": "x"}))
    check("fila não colapsa em 'item' sem id",
          queue_key({"lang": "pt", "slug": "x"}) == "pt-x")
    ladder = query_ladder({"image": {"query": "server room data breach cybersecurity abstract"}}, cfg)
    check("busca de imagem afunila até um termo genérico", len(ladder) >= 4 and len(ladder[-1].split()) <= 3,
          str(ladder))
    check("busca de imagem não repete tentativa", len(ladder) == len(set(ladder)))
    check("query vazia ainda tenta o termo do nicho",
          len(query_ladder({"image": {"query": ""}}, cfg)) >= 1)

    print("\nTemplates")
    env = environment()
    try:
        html = render(env, "article.html", base_context(
            cfg, "pt", post=humanize(post, "pt"), page_title=post["title_tag"],
            page_description=post["meta_description"], page_keywords=post["keywords"],
            canonical=post["canonical"], alternates=post["alternates"], og_type="article",
            legal_pages=[]))
        check("article.html renderiza", "<h1>" in html)
        check("ad slot in-content presente", "ad slot: in_content" in html)
        check("hreflang no head", 'rel="alternate"' in html)
        check("fontes listadas no rodapé da matéria", "sources-title" in html)
    except Exception as exc:  # noqa: BLE001 - the point is to report any failure
        check("article.html renderiza", False, f"{type(exc).__name__}: {exc}")

    print(f"\n{CHECKS - len(FAILURES)}/{CHECKS} verificações passaram")
    if FAILURES:
        print("Falhas: " + ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
