"""Interface strings, per language.

These are chrome labels, not editorial content - they belong to the engine and
are the same for any site built on it. Anything niche- or brand-specific lives
in site.config.yaml instead.
"""
from __future__ import annotations

STRINGS = {
    "pt": {
        "skip_to_content": "Ir para o conteúdo",
        "sections": "Editorias",
        "about_site": "O site",
        "rights": "Todos os direitos reservados.",
        "ai_disclosure": "Conteúdo produzido com apoio de inteligência artificial "
                         "e checagem automatizada em múltiplas fontes.",
        "most_read": "Mais lidas",
        "see_all": "Ver tudo",
        "min_read": "min de leitura",
        "photo": "Foto",
        "sources": "Fontes",
        "verification_note": "Cada fato desta matéria foi confirmado em pelo menos "
                             "duas fontes independentes antes da publicação.",
        "single_source_note": "Esta matéria foi publicada a partir de uma única fonte "
                              "primária oficial, por autorização direta da direção do "
                              "site, fora do processo padrão de checagem cruzada.",
        "related": "Leia também",
        "section": "Editoria",
        "empty_category": "Ainda não há matérias publicadas nesta editoria.",
        "updated_on": "Atualizado em",
        "newsletter_title": "Receba as novidades de IA por e-mail",
        "newsletter_text": "Um resumo do que importa em inteligência artificial, "
                           "sem ruído e sem hype.",
        "newsletter_placeholder": "seu@email.com",
        "newsletter_button": "Assinar",
        "newsletter_note": "Sem spam. Cancele quando quiser.",
        "home_title": "Notícias de Inteligência Artificial",
        "category_description": "Últimas notícias e análises sobre {label} em {niche}.",
    },
    "en": {
        "skip_to_content": "Skip to content",
        "sections": "Sections",
        "about_site": "The site",
        "rights": "All rights reserved.",
        "ai_disclosure": "Content produced with the support of artificial intelligence "
                         "and automated multi-source fact-checking.",
        "most_read": "Most read",
        "see_all": "See all",
        "min_read": "min read",
        "photo": "Photo",
        "sources": "Sources",
        "verification_note": "Every fact in this story was confirmed by at least two "
                             "independent sources before publication.",
        "single_source_note": "This story was published from a single official primary "
                              "source, by direct authorization from the site's owner, "
                              "outside the standard cross-checking process.",
        "related": "Read next",
        "section": "Section",
        "empty_category": "No stories published in this section yet.",
        "updated_on": "Updated on",
        "newsletter_title": "Get AI news by email",
        "newsletter_text": "A digest of what actually matters in artificial intelligence "
                           "- no noise, no hype.",
        "newsletter_placeholder": "you@email.com",
        "newsletter_button": "Subscribe",
        "newsletter_note": "No spam. Unsubscribe anytime.",
        "home_title": "Artificial Intelligence News",
        "category_description": "Latest news and analysis on {label} in {niche}.",
    },
    "es": {
        "skip_to_content": "Ir al contenido",
        "sections": "Secciones",
        "about_site": "El sitio",
        "rights": "Todos los derechos reservados.",
        "ai_disclosure": "Contenido producido con apoyo de inteligencia artificial "
                         "y verificación automatizada en múltiples fuentes.",
        "most_read": "Lo más leído",
        "see_all": "Ver todo",
        "min_read": "min de lectura",
        "photo": "Foto",
        "sources": "Fuentes",
        "verification_note": "Cada dato de esta nota fue confirmado por al menos dos "
                             "fuentes independientes antes de publicarse.",
        "single_source_note": "Esta nota fue publicada a partir de una única fuente "
                              "primaria oficial, por autorización directa de la "
                              "dirección del sitio, fuera del proceso estándar de "
                              "verificación cruzada.",
        "related": "Lee también",
        "section": "Sección",
        "empty_category": "Todavía no hay notas publicadas en esta sección.",
        "updated_on": "Actualizado el",
        "newsletter_title": "Recibe las novedades de IA por correo",
        "newsletter_text": "Un resumen de lo que importa en inteligencia artificial, "
                           "sin ruido y sin hype.",
        "newsletter_placeholder": "tu@email.com",
        "newsletter_button": "Suscribirme",
        "newsletter_note": "Sin spam. Cancela cuando quieras.",
        "home_title": "Noticias de Inteligencia Artificial",
        "category_description": "Últimas noticias y análisis sobre {label} en {niche}.",
    },
}


class Strings(dict):
    """Dict with attribute access, so templates can write t.most_read."""

    def __getattr__(self, name: str) -> str:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(f"string de interface ausente: {name}") from exc


def strings(lang: str) -> Strings:
    base = dict(STRINGS.get("en", {}))
    base.update(STRINGS.get(lang, {}))
    return Strings(base)


def missing_keys() -> dict[str, list[str]]:
    """Which languages are missing which keys - used by the build's self-check."""
    reference = set(STRINGS["en"])
    return {lang: sorted(reference - set(values))
            for lang, values in STRINGS.items() if reference - set(values)}
