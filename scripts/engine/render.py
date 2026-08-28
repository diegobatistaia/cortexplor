"""Step 8a - turning post records into HTML.

Jinja environment, the ad-slot helper, and the per-page context. The templates
know nothing about the niche: every label comes from site.config.yaml or i18n.
"""
from __future__ import annotations

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from .config import ROOT, Config
from .i18n import strings
from .util import format_date, parse_date, utcnow

TEMPLATES = ROOT / "templates"

# The in-content ad follows this paragraph - counting paragraphs, not blocks, so
# the slot never lands between a heading and the text it introduces. One single
# in-content slot per article, by design.
AD_AFTER_PARAGRAPH = 3


def ad_slot_factory(cfg: Config, lang: str):
    ads = cfg.get("ads", {}) or {}

    def ad_slot(name: str) -> Markup:
        slot_id = (ads.get("slots") or {}).get(name, "")
        if not ads.get("enabled") or not ads.get("client_id") or not slot_id:
            # The position stays visible in the source so the slot can be filled
            # the day AdSense is approved, without touching the templates.
            return Markup(f"<!-- ad slot: {name} -->")
        label = (ads.get("labels") or {}).get(lang, "")
        label_html = f"<span class='ad-label'>{label}</span>" if label else ""
        client_id = ads["client_id"]
        return Markup(
            f'<div class="ad ad-{name}">'
            f"{label_html}"
            f'<ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{client_id}" data-ad-slot="{slot_id}" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f"<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>")

    return ad_slot


def environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["date"] = lambda value, lang: format_date(parse_date(value) or utcnow(), lang)
    return env


def base_context(cfg: Config, lang: str, **extra) -> dict:
    context = {
        "cfg": cfg,
        "site": cfg,
        "lang": lang,
        "html_lang": cfg.get(f"site.html_lang.{lang}", lang),
        "t": strings(lang),
        "categories": cfg.categories(lang),
        "ads": cfg.get("ads", {}) or {},
        "newsletter": cfg.get("newsletter", {}) or {},
        "ad_slot": ad_slot_factory(cfg, lang),
        "ad_after_paragraph": AD_AFTER_PARAGRAPH,
        "year": utcnow().year,
        "active_category": None,
        "alternates": [],
        "og_image": None,
        "page_keywords": "",
        "legal_pages": [],
    }
    context.update(extra)
    return context


def humanize(post: dict, lang: str) -> dict:
    published = parse_date(post.get("published_at"))
    updated = parse_date(post.get("updated_at"))
    return {
        **post,
        "published_human": format_date(published, lang) if published else "",
        "updated_human": format_date(updated, lang) if updated else "",
    }


def render(env: Environment, template: str, context: dict) -> str:
    return env.get_template(template).render(**context)
