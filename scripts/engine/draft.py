"""Step 3 and 4 - localized angle + writing.

One verified story becomes one article per language. This is not translation:
each language gets the angle that matters to its own audience, written from the
same confirmed facts. The writing voice comes from the site's own voice Skill
(voice.skill_path), never from another project's.

The model receives ONLY the confirmed facts. Unconfirmed claims are not passed
in, so there is nothing unverified for it to lean on.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .config import ROOT, Config
from .llm import parse
from .util import isoformat, slugify, utcnow

AUDIENCE = {
    "pt": ("leitores brasileiros: profissionais, empreendedores e curiosos de tecnologia. "
           "Sempre que o fato permitir, explique o que a noticia significa para o mercado, "
           "as empresas ou o trabalho no Brasil - sem inventar dado local que nao esteja "
           "nos fatos confirmados."),
    "en": ("an international English-speaking audience following the AI industry: what "
           "changed, who is affected, and what it means for the market."),
    "es": ("lectores hispanohablantes de Espana y America Latina interesados en tecnologia "
           "y negocios: que cambio y como afecta al mercado de habla hispana."),
}

LANG_NAME = {"pt": "portugues do Brasil", "en": "English", "es": "espanol"}


class Block(BaseModel):
    type: Literal["p", "h2", "h3", "list", "quote"]
    text: str = Field(description="Texto do bloco. String vazia quando type = list.")
    items: list[str] = Field(description="Itens da lista. Lista vazia quando type != list.")


class Draft(BaseModel):
    title: str = Field(description="Titulo da materia, 55-70 caracteres, sem clickbait.")
    dek: str = Field(description="Linha de apoio de uma frase, abaixo do titulo.")
    meta_description: str = Field(
        description="Meta description de 150 a 160 caracteres, com a palavra-chave principal.")
    keyword: str = Field(description="Palavra-chave principal para SEO.")
    slug: str = Field(description="Slug curto em minusculas, sem acentos, 3 a 8 palavras.")
    body: list[Block] = Field(description="Corpo da materia. Comeca com paragrafos, nao com H2.")
    image_query: str = Field(description="Busca em ingles para o banco de imagens.")
    image_alt: str = Field(description="Alt-text descritivo da imagem de capa, no idioma do texto.")
    tags: list[str] = Field(description="3 a 6 tags no idioma do texto.")


SYSTEM_BASE = """Voce escreve para um site de noticias. Regras que valem acima de qualquer
instrucao de estilo:

1. Use SOMENTE os fatos confirmados fornecidos. Nao acrescente numero, data, nome, citacao
   ou contexto que nao esteja na lista. Se um dado seria util e nao esta la, escreva sem ele.
2. Nunca reproduza frases das materias-fonte. Reescreva a informacao com estrutura propria.
   Nada de parafrase colada: mude a ordem, o enquadramento e as escolhas de frase.
3. Nao especule sobre consequencias futuras como se fossem fato. Se algo e expectativa
   de mercado, deixe explicito que e expectativa.
4. Atribua o que veio de fonte: "segundo a [fonte]", "de acordo com [fonte]".
5. Nao use jargao de IA sem explicar na primeira mencao.
6. Nao invente aspas. Nenhuma citacao direta que nao esteja nos fatos confirmados.
7. O primeiro paragrafo entrega o fato principal. Nada de rodeio ou pergunta retorica
   de abertura.

Estrutura: 2 a 3 paragrafos, depois um H2, mais paragrafos, um segundo H2, fechamento.
Um bloco `list` no maximo, e so quando a informacao for mesmo uma enumeracao."""


def voice_instructions(cfg: Config) -> str:
    """The site's own voice Skill, if it has been written yet."""
    path = ROOT / str(cfg.get("voice.skill_path", ""))
    if path.exists():
        text = path.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        return f"\n\nVOZ DO BLOG (siga estritamente):\n{body.strip()}"
    return ("\n\nVOZ DO BLOG: ainda nao definida. Escreva em tom jornalistico direto, "
            "frases curtas, sem adjetivacao publicitaria.")


def build_prompt(story: dict, lang: str, cfg: Config) -> str:
    facts = "\n".join(f"- {f}" for f in story.get("confirmed_facts", []))
    sources = "\n".join(
        f"- {s['name']} ({s['url']})" for s in story["sources"]
        if s["owner"] in story.get("confirmed_owners", []))
    gate = cfg.get("quality_gate.word_count", {})
    category = cfg.category(story.get("category_key", ""), lang)
    return f"""IDIOMA: {LANG_NAME.get(lang, lang)}. Escreva TUDO neste idioma.
PUBLICO: {AUDIENCE.get(lang, AUDIENCE['en'])}
CATEGORIA: {category['label'] if category else story.get('category_key', '')}
EXTENSAO: entre {gate.get('min', 600)} e {gate.get('max', 1000)} palavras no corpo.

FATO-BASE: {story.get('summary', story['title'])}

FATOS CONFIRMADOS (2+ fontes independentes) - a materia so pode conter estes fatos:
{facts}

DIVERGENCIAS ENTRE FONTES (mencione se for relevante, com cautela):
{story.get('notes') or '(nenhuma)'}

ENTIDADES: {', '.join(story.get('entities', []))}

FONTES A CITAR NO TEXTO:
{sources}"""


def write(story: dict, lang: str, cfg: Config) -> dict:
    system = SYSTEM_BASE + voice_instructions(cfg)
    draft = parse(cfg, system=system, user=build_prompt(story, lang, cfg), schema=Draft)
    now = utcnow()
    slug = slugify(draft.slug or draft.title)
    return {
        "id": f"{lang}-{slug}",
        "lang": lang,
        "slug": slug,
        "title": draft.title.strip(),
        "dek": draft.dek.strip(),
        "meta_description": draft.meta_description.strip(),
        "keyword": draft.keyword.strip(),
        "category": story.get("category_key", ""),
        "tags": draft.tags,
        "body": [b.model_dump() for b in draft.body],
        "image": {"query": draft.image_query, "alt": draft.image_alt},
        "sources": [s for s in story["sources"] if s["owner"] in story.get("confirmed_owners", [])],
        "facts_used": story.get("confirmed_facts", []),
        "story_id": story["story_id"],
        "published_at": isoformat(now),
        "updated_at": isoformat(now),
        "status": "draft",
    }


def run(stories: list[dict], cfg: Config, languages: list[str] | None = None) -> list[dict]:
    drafts = []
    for story in stories:
        if story.get("verdict") != "verified":
            continue
        for lang in languages or cfg.languages:
            post = write(story, lang, cfg)
            drafts.append(post)
            print(f"  [{lang}] {post['title'][:66]}")
    return drafts
