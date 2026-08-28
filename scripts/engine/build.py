"""Step 8b - build the static site from the post records.

Reads content/<lang>/*.json plus content/pages/<lang>/*.json and writes the
whole public site: article pages, homes, category pages, institutional pages,
sitemaps, RSS, robots.txt, the manifest and the generated CSS.

The build is deterministic and idempotent: running it twice produces the same
bytes, which keeps git diffs meaningful.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from . import seo
from .config import ROOT, Config
from .i18n import strings
from .render import base_context, environment, humanize, render
from .store import CONTENT, DATA, load_posts
from .util import excerpt, isoformat, parse_date, utcnow

PAGES = CONTENT / "pages"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def views() -> dict[str, int]:
    """Pageviews per URL, if a GA4 export has been dropped in data/views.json."""
    path = DATA / "views.json"
    if not path.exists():
        return {}
    try:
        return {k: int(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {}


# --------------------------------------------------------------------- pieces

def build_posts(env, cfg: Config, pool: list[dict], out: Path, nav: list[dict]) -> list[dict]:
    built = []
    for post in pool:
        enriched = humanize(post, post["lang"])
        context = base_context(
            cfg, post["lang"],
            post=enriched,
            page_title=enriched["title_tag"],
            page_description=enriched["meta_description"],
            page_keywords=enriched["keywords"],
            canonical=enriched["canonical"],
            alternates=enriched["alternates"],
            active_category=enriched.get("category"),
            og_type="article",
            og_image=cfg.url(enriched["image"]["path"]) if enriched.get("image", {}).get("path") else None,
            og_image_alt=enriched.get("image", {}).get("alt", ""),
            legal_pages=legal_links(cfg, post["lang"]),
            categories=nav,
        )
        write(out / post["lang"] / post["slug"] / "index.html",
              render(env, "article.html", context))
        built.append(enriched)
    return built


def build_home(env, cfg: Config, lang: str, posts: list[dict], out: Path, nav: list[dict]) -> None:
    counts = views()
    ranked = sorted(posts, key=lambda p: (counts.get(p["url"], 0), p["published_at"]), reverse=True)
    t = strings(lang)
    modules = []
    for category in cfg.categories(lang)[:cfg.get("editorial.topic_module_count", 4)]:
        in_category = [p for p in posts if p.get("category") == category["key"]][:3]
        if in_category:
            modules.append({**category, "posts": in_category})

    context = base_context(
        cfg, lang,
        hero=posts[0] if posts else None,
        secondary=posts[1:4],
        most_read=ranked[:cfg.get("editorial.most_read_count", 5)],
        topic_modules=modules,
        home_layout=cfg.get("editorial.home_layout", []),
        schema_website=seo.website_schema(cfg, lang),
        page_title=f"{cfg.get('site.name')} - {cfg.localized('site.tagline', lang)}",
        page_description=cfg.localized("site.description", lang),
        page_keywords=cfg.localized("niche.term", lang),
        canonical=cfg.url(seo.home_path(lang)),
        alternates=seo.home_alternates(cfg),
        og_image=cfg.url("/assets/logo/icon-512.png"),
        legal_pages=legal_links(cfg, lang),
        categories=nav,
    )
    write(out / lang / "index.html", render(env, "home.html", context))


def nav_categories(cfg: Config, lang: str, posts: list[dict]) -> list[dict]:
    """Editorias que já têm ao menos uma matéria.

    Um menu que leva a "Ainda não há matérias publicadas nesta editoria" faz o
    site parecer abandonado no dia em que ele mais precisa parecer vivo. A
    editoria volta ao menu sozinha assim que a primeira matéria dela sai.
    """
    com_materia = {p.get("category") for p in posts}
    return [c for c in cfg.categories(lang) if c["key"] in com_materia]


def prune_categories(cfg: Config, lang: str, out: Path, nav: list[dict]) -> list[str]:
    """Apaga páginas de editorias que não existem mais neste idioma.

    Sem isso, tirar uma editoria do config deixa a página antiga no ar: órfã do
    menu, mas acessível e indexável pelo Google. Aconteceu quando "IA no Brasil"
    passou a ser exclusiva da edição em português.
    """
    root = out / lang / seo.CATEGORY_PREFIX
    if not root.exists():
        return []
    validas = {c["slug"] for c in nav}
    removidas = []
    for folder in root.iterdir():
        if folder.is_dir() and folder.name not in validas:
            shutil.rmtree(folder)
            removidas.append(f"{lang}/{seo.CATEGORY_PREFIX}/{folder.name}")
    return removidas


def build_categories(env, cfg: Config, lang: str, posts: list[dict], out: Path, nav: list[dict]) -> None:
    t = strings(lang)
    for category in nav:
        in_category = [p for p in posts if p.get("category") == category["key"]]
        description = t["category_description"].format(
            label=category["label"], niche=cfg.localized("niche.term", lang))
        context = base_context(
            cfg, lang,
            category=category,
            posts=in_category,
            active_category=category["key"],
            page_title=f"{category['label']}{cfg.localized('seo.title_suffix', lang, '')}",
            page_description=description,
            page_keywords=f"{category['label']}, {cfg.localized('niche.term', lang)}",
            canonical=cfg.url(seo.category_path(lang, category["slug"])),
            alternates=[],
            legal_pages=legal_links(cfg, lang),
            categories=nav,
        )
        write(out / lang / seo.CATEGORY_PREFIX / category["slug"] / "index.html",
              render(env, "category.html", context))


def load_pages(lang: str) -> list[dict]:
    folder = PAGES / lang
    if not folder.exists():
        return []
    pages = []
    for path in sorted(folder.glob("*.json")):
        pages.append(json.loads(path.read_text(encoding="utf-8")))
    return pages


def legal_links(cfg: Config, lang: str) -> list[dict]:
    return [{"title": p["title"], "url": seo.page_path(lang, p["slug"])}
            for p in load_pages(lang)]


def build_pages(env, cfg: Config, lang: str, out: Path, nav: list[dict]) -> list[dict]:
    built = []
    for page in load_pages(lang):
        enriched = humanize(page, lang)
        context = base_context(
            cfg, lang,
            page=enriched,
            page_title=f"{page['title']}{cfg.localized('seo.title_suffix', lang, '')}",
            page_description=page.get("description", ""),
            canonical=cfg.url(seo.page_path(lang, page["slug"])),
            alternates=[],
            legal_pages=legal_links(cfg, lang),
            categories=nav,
        )
        write(out / lang / page["slug"] / "index.html", render(env, "page.html", context))
        built.append(page)
    return built


# ------------------------------------------------------------------ feeds etc

def build_sitemap(cfg: Config, lang: str, posts: list[dict], pages: list[dict], out: Path,
                  nav: list[dict]) -> None:
    urls = [(cfg.url(seo.home_path(lang)), isoformat(utcnow()), "daily", "1.0")]
    for category in nav:
        urls.append((cfg.url(seo.category_path(lang, category["slug"])),
                     isoformat(utcnow()), "daily", "0.7"))
    for post in posts:
        urls.append((post["canonical"], post.get("updated_at", post["published_at"]),
                     "monthly", "0.9"))
    for page in pages:
        urls.append((cfg.url(seo.page_path(lang, page["slug"])),
                     page.get("updated_at", isoformat(utcnow())), "yearly", "0.3"))

    body = "\n".join(
        f"  <url><loc>{escape(loc)}</loc><lastmod>{escape(mod)}</lastmod>"
        f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>"
        for loc, mod, freq, prio in urls)
    write(out / f"sitemap-{lang}.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f"{body}\n</urlset>\n")


def build_sitemap_index(cfg: Config, out: Path) -> None:
    entries = "\n".join(
        f"  <sitemap><loc>{cfg.url(f'/sitemap-{lang}.xml')}</loc>"
        f"<lastmod>{isoformat(utcnow())}</lastmod></sitemap>"
        for lang in cfg.languages)
    write(out / "sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f"{entries}\n</sitemapindex>\n")


def build_rss(cfg: Config, lang: str, posts: list[dict], out: Path) -> None:
    items = []
    for post in posts[:30]:
        published = parse_date(post["published_at"])
        items.append(
            "    <item>\n"
            f"      <title>{escape(post['title'])}</title>\n"
            f"      <link>{escape(post['canonical'])}</link>\n"
            f"      <guid isPermaLink=\"true\">{escape(post['canonical'])}</guid>\n"
            f"      <description>{escape(post.get('meta_description', ''))}</description>\n"
            f"      <category>{escape(post.get('category_label', ''))}</category>\n"
            f"      <pubDate>{published.strftime('%a, %d %b %Y %H:%M:%S +0000') if published else ''}</pubDate>\n"
            "    </item>")
    write(out / f"rss-{lang}.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
          f"    <title>{escape(str(cfg.get('site.name')))} - {escape(cfg.localized('site.tagline', lang))}</title>\n"
          f"    <link>{escape(cfg.url(seo.home_path(lang)))}</link>\n"
          f"    <description>{escape(cfg.localized('site.description', lang))}</description>\n"
          f"    <language>{cfg.get(f'site.html_lang.{lang}', lang)}</language>\n"
          f"    <lastBuildDate>{utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>\n"
          f'    <atom:link href="{escape(cfg.url(f"/rss-{lang}.xml"))}" rel="self" type="application/rss+xml"/>\n'
          + "\n".join(items) + "\n  </channel>\n</rss>\n")


def build_robots(cfg: Config, out: Path) -> None:
    lines = ["User-agent: *", "Allow: /", ""]
    for lang in cfg.languages:
        lines.append(f"Sitemap: {cfg.url(f'/sitemap-{lang}.xml')}")
    lines.append(f"Sitemap: {cfg.url('/sitemap.xml')}")
    write(out / "robots.txt", "\n".join(lines) + "\n")


def build_manifest(cfg: Config, out: Path) -> None:
    write(out / "site.webmanifest", json.dumps({
        "name": cfg.get("site.name"),
        "short_name": cfg.get("site.name"),
        "description": cfg.localized("site.description", cfg.default_language),
        "start_url": seo.home_path(cfg.default_language),
        "display": "standalone",
        "background_color": cfg.get("brand.paper"),
        "theme_color": cfg.get("brand.primary"),
        "icons": [
            {"src": "/assets/logo/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/logo/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }, ensure_ascii=False, indent=2) + "\n")


def build_root(cfg: Config, out: Path) -> None:
    """Root URL sends visitors to the default language; hreflang tells Google
    that the three versions are equals, not a redirect chain."""
    default = cfg.default_language
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{cfg.get(f"site.html_lang.{l}", l)}" '
        f'href="{cfg.url(seo.home_path(l))}">'
        for l in cfg.languages)
    write(out / "index.html",
          f"""<!DOCTYPE html>
<html lang="{cfg.get(f'site.html_lang.{default}', default)}">
<head>
<meta charset="utf-8">
<title>{cfg.get('site.name')} - {cfg.localized('site.tagline', default)}</title>
<link rel="canonical" href="{cfg.url(seo.home_path(default))}">
{alts}
<link rel="alternate" hreflang="x-default" href="{cfg.url(seo.home_path(default))}">
<meta http-equiv="refresh" content="0; url={seo.home_path(default)}">
</head>
<body>
<p><a href="{seo.home_path(default)}">{cfg.get('site.name')}</a></p>
<script>
  var supported = {json.dumps(cfg.languages)};
  var preferred = (navigator.languages || [navigator.language || ""])
    .map(function (l) {{ return String(l).slice(0, 2).toLowerCase(); }})
    .filter(function (l) {{ return supported.indexOf(l) !== -1; }})[0];
  location.replace("/" + (preferred || "{default}") + "/");
</script>
</body>
</html>
""")


def build_favicon(cfg: Config, out: Path) -> None:
    """Browsers, feed readers and link previews ask for /favicon.ico at the root
    regardless of what the <link> tags say. Keep a copy there."""
    source = out / "assets" / "logo" / "favicon.ico"
    if source.exists():
        shutil.copyfile(source, out / "favicon.ico")


def build_css(env, cfg: Config, out: Path) -> None:
    # CSS is not HTML: rendering it with autoescape on would turn the font
    # stack's quotes into entities.
    plain = env.overlay(autoescape=False)
    css = plain.get_template("site.css.j2").render(b=cfg.get("brand", {}))
    write(out / "assets" / "css" / "site.css", css)


# ----------------------------------------------------------------------- main

def run(cfg: Config, out: Path = ROOT) -> dict:
    env = environment()
    everything = [p for lang in cfg.languages for p in load_posts(lang)
                  if p.get("status") == "published"]
    enriched_all = [seo.enrich(p, everything, cfg) for p in everything]

    stats = {"posts": 0, "pages": 0, "languages": {}}
    for lang in cfg.languages:
        posts = [p for p in enriched_all if p["lang"] == lang]
        posts.sort(key=lambda p: p["published_at"], reverse=True)
        nav = nav_categories(cfg, lang, posts)
        built = build_posts(env, cfg, posts, out, nav)
        pages = build_pages(env, cfg, lang, out, nav)
        build_home(env, cfg, lang, [humanize(p, lang) for p in posts], out, nav)
        build_categories(env, cfg, lang, [humanize(p, lang) for p in posts], out, nav)
        for removida in prune_categories(cfg, lang, out, nav):
            print(f"  - editoria sem materia, pagina removida: /{removida}/")
        build_sitemap(cfg, lang, posts, pages, out, nav)
        build_rss(cfg, lang, posts, out)
        stats["languages"][lang] = {"posts": len(built), "pages": len(pages)}
        stats["posts"] += len(built)
        stats["pages"] += len(pages)

    build_sitemap_index(cfg, out)
    build_robots(cfg, out)
    build_manifest(cfg, out)
    build_root(cfg, out)
    build_favicon(cfg, out)
    build_css(env, cfg, out)
    return stats


if __name__ == "__main__":
    from .config import load
    cfg = load()
    stats = run(cfg)
    for lang, counts in stats["languages"].items():
        print(f"  /{lang}/  {counts['posts']} materias, {counts['pages']} paginas")
    print(f"total: {stats['posts']} materias, {stats['pages']} paginas institucionais")
