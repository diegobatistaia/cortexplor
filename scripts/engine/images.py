"""Step 6 - cover image, licensed and attributed.

Ordem de tentativa, da mais ligada ao assunto para a mais genérica:

1. Imagem oficial da empresa (og:image do anúncio em fonte `kind: primary`),
   só com `images.official: true`. É material de divulgação da própria empresa
   sobre o próprio anúncio, creditado como tal.
2. A foto do verbete da Wikipedia de `image.subject` (pessoa, lugar, produto),
   só se estiver no Wikimedia Commons com licença livre (domínio público, CC0,
   CC BY, CC BY-SA), com autor e licença no crédito.
3. Unsplash / Pexels pela `image.query`, como antes.

Nunca se pega a foto de uma matéria de imprensa: ela é licenciada ao veículo,
não a nós. O crédito vai junto com a matéria e aparece embaixo da imagem.
"""
from __future__ import annotations

import html
import io
import os
import re
from pathlib import Path

import requests
from PIL import Image

from .config import ROOT, Config
from .util import fingerprint

IMG_DIR = ROOT / "assets" / "img"
MAX_WIDTH = 1200
QUALITY = 82
TIMEOUT = 25
USER_AGENT = "CortexplorBot/1.0 (https://cortexplor.com; bot@cortexplor.com)"
MIN_WIDTH = 800


class ImageError(RuntimeError):
    pass


def _unsplash(query: str, orientation: str) -> dict:
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        raise ImageError("UNSPLASH_ACCESS_KEY não configurada")
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "orientation": orientation, "per_page": 1, "content_filter": "high"},
        headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"},
        timeout=TIMEOUT)
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        raise ImageError(f"Unsplash sem resultado para '{query}'")
    photo = results[0]
    # Unsplash requires pinging the download endpoint when an image is used.
    try:
        requests.get(photo["links"]["download_location"],
                     headers={"Authorization": f"Client-ID {key}"}, timeout=TIMEOUT)
    except requests.RequestException:
        pass
    return {
        "url": photo["urls"]["regular"],
        "provider": "Unsplash",
        "author": photo["user"]["name"],
        "author_url": photo["user"]["links"]["html"] + "?utm_source=cortexplor&utm_medium=referral",
        "source_url": photo["links"]["html"],
    }


def _pexels(query: str, orientation: str) -> dict:
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        raise ImageError("PEXELS_API_KEY não configurada")
    response = requests.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "orientation": orientation, "per_page": 1},
        headers={"Authorization": key}, timeout=TIMEOUT)
    response.raise_for_status()
    photos = response.json().get("photos") or []
    if not photos:
        raise ImageError(f"Pexels sem resultado para '{query}'")
    photo = photos[0]
    return {
        "url": photo["src"]["large"],
        "provider": "Pexels",
        "author": photo["photographer"],
        "author_url": photo["photographer_url"],
        "source_url": photo["url"],
    }


# --------------------------------------------------------------- Wikimedia Commons
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
FREE_LICENSES = ("cc0", "public domain", "pd", "cc by")


def free_license(name: str) -> bool:
    """CC0, domínio público, CC BY e CC BY-SA. Nada com NC (não comercial) ou ND."""
    low = (name or "").strip().lower()
    if not low or "nc" in low.replace("-", " ").split() or "nd" in low.replace("-", " ").split():
        return False
    return low.startswith(FREE_LICENSES)


def _plain(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value or "")).split())


def pick_commons(pages: list[dict], subject: str) -> dict | None:
    """Escolhe a melhor foto da busca: nome do assunto no título, licença livre,
    larga o bastante. Entre as boas, prefere a horizontal e depois a maior."""
    words = [w.lower() for w in subject.split() if len(w) > 1]
    good = []
    for page in pages:
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        title = page.get("title", "")
        name = f"{title} {_plain(meta.get('ObjectName', {}).get('value', ''))}".lower()
        license_name = _plain(meta.get("LicenseShortName", {}).get("value", ""))
        if info.get("mime") not in ("image/jpeg", "image/png", "image/webp"):
            continue
        if (info.get("width") or 0) < MIN_WIDTH or not free_license(license_name):
            continue
        if words and not all(w in name for w in words):
            continue
        landscape = info["width"] / max(info.get("height") or 1, 1) >= 1.2
        good.append((landscape, info["width"], page, info, meta, license_name))
    if not good:
        return None
    good.sort(key=lambda g: (g[0], g[1]), reverse=True)
    _, _, page, info, meta, license_name = good[0]
    author = _plain(meta.get("Artist", {}).get("value", "")) or "Wikimedia Commons"
    return {
        "url": info.get("thumburl") or info["url"],
        "provider": "Wikimedia Commons",
        "author": author[:80],
        "author_url": "",
        "source_url": info.get("descriptionurl") or "",
        "license": license_name,
        "license_url": _plain(meta.get("LicenseUrl", {}).get("value", "")),
    }


WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"


def _commons(subject: str) -> dict:
    """A foto principal do verbete da Wikipedia em inglês (a do quadro ao lado
    do texto), se ela estiver no Commons com licença livre.

    A busca livre no Commons foi testada e erra demais: "Hugging Face" trazia
    uma pessoa abraçando um globo; "Donald Trump", uma foto dele jovem com o
    pai. A foto do verbete é escolhida a dedo pelos editores da Wikipedia.
    """
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(WIKIPEDIA_API, params={
        "action": "query", "format": "json", "titles": subject, "redirects": 1,
        "prop": "pageimages", "piprop": "name",
    }, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    pages = list(((response.json().get("query") or {}).get("pages") or {}).values())
    name = (pages[0].get("pageimage") if pages else "") or ""
    if not name:
        raise ImageError(f"Wikipedia sem foto no verbete '{subject}'")
    # Arquivo que só existe na Wikipedia (e não no Commons) é de uso restrito:
    # logotipo, capa, foto com direitos. Só o Commons garante licença livre.
    response = requests.get(COMMONS_API, params={
        "action": "query", "format": "json", "titles": f"File:{name}",
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1600,
    }, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    pages = [p for p in ((response.json().get("query") or {}).get("pages") or {}).values()
             if p.get("imageinfo")]
    found = pick_commons(pages, "")
    if not found:
        raise ImageError(f"foto do verbete '{subject}' não tem licença livre no Commons")
    return found


# ------------------------------------------------------------- imagem oficial
OG_IMAGE = re.compile(
    r"""<meta[^>]+(?:property|name)=["'](?:og:image|twitter:image)["'][^>]*>""", re.I)
CONTENT = re.compile(r"""content=["']([^"']+)["']""", re.I)


def og_image(page_html: str) -> str:
    for tag in OG_IMAGE.findall(page_html or ""):
        match = CONTENT.search(tag)
        if match and match.group(1).startswith("http"):
            return html.unescape(match.group(1))
    return ""


def official_source(post: dict, cfg: Config) -> dict | None:
    """A primeira fonte da matéria que é canal oficial (`kind: primary`)."""
    primaries = {s["name"]: s for s in cfg.get("sources.rss", []) if s.get("kind") == "primary"}
    for source in post.get("sources") or []:
        if source.get("name") in primaries and source.get("url"):
            return source
    return None


def _official(post: dict, cfg: Config) -> dict:
    source = official_source(post, cfg)
    if not source:
        raise ImageError("sem fonte oficial")
    response = requests.get(source["url"], headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    response.raise_for_status()
    url = og_image(response.text)
    if not url:
        raise ImageError(f"{source['name']} sem og:image")
    # Muito site põe a mesma imagem padrão em todo anúncio (na Anthropic, um
    # cartão da marca). Se for igual à da página inicial ou da lista de
    # notícias, não é do anúncio.
    parts = source["url"].rstrip("/").split("/")
    padroes = set()
    for index in {"/".join(parts[:3]) + "/", "/".join(parts[:-1])}:
        try:
            padroes.add(og_image(requests.get(index, headers={"User-Agent": USER_AGENT},
                                              timeout=TIMEOUT).text))
        except requests.RequestException:
            pass
    if url in padroes:
        raise ImageError(f"{source['name']}: og:image é a padrão do site, não do anúncio")
    return {
        "url": url,
        "provider": "press",
        "author": source["name"],
        "author_url": "",
        "source_url": source["url"],
    }


PROVIDERS = {"unsplash": _unsplash, "pexels": _pexels}


def crop_16_9(image: Image.Image) -> Image.Image:
    """Corta para 16:9, a proporção da capa. Foto em pé (retrato de pessoa) é
    cortada perto do topo, para não decapitar ninguém; as outras, no centro."""
    target = round(image.width * 9 / 16)
    if image.height <= target:
        return image
    bias = 0.2 if image.height > image.width else 0.5
    top = round((image.height - target) * bias)
    return image.crop((0, top, image.width, top + target))


def download(url: str, slug: str) -> str:
    """Fetch, downscale, save as JPEG. Returns the site-absolute path."""
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    response.raise_for_status()
    image = crop_16_9(Image.open(io.BytesIO(response.content)).convert("RGB"))
    if image.width < 600:
        raise ImageError(f"imagem pequena demais ({image.width}px)")
    if image.width > MAX_WIDTH:
        height = round(image.height * MAX_WIDTH / image.width)
        image = image.resize((MAX_WIDTH, height), Image.LANCZOS)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{slug[:40]}-{fingerprint(url)[:8]}.jpg"
    image.save(IMG_DIR / name, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return f"/assets/img/{name}"


def query_ladder(post: dict, cfg: Config) -> list[str]:
    """Buscas da mais específica para a mais genérica.

    Um banco de imagens não tem foto de "server room data breach cybersecurity
    abstract technology abstract" - e foi assim que três matérias boas caíram na
    fila no primeiro dia. Vale mais uma imagem genérica e honesta do que matéria
    parada. A última tentativa é sempre um termo amplo do nicho, que existe.
    """
    base = (post.get("image", {}).get("query") or "").strip()
    suffix = (cfg.get("images.query_suffix") or "").strip()
    words = base.split()
    generic = cfg.localized("niche.term", "en") or "technology"

    tentativas = [
        f"{base} {suffix}".strip(),
        base,
        " ".join(words[:3]),
        " ".join(words[:2]),
        generic,
    ]
    vistas, ladder = set(), []
    for q in tentativas:
        q = " ".join(q.split())
        if q and q.lower() not in vistas:
            vistas.add(q.lower())
            ladder.append(q)
    return ladder


def candidates(post: dict, cfg: Config):
    """Gera (nome, função) na ordem de tentativa. A busca só roda quando chamada."""
    if cfg.get("images.official", False) and official_source(post, cfg):
        yield "oficial", lambda: _official(post, cfg)
    subject = (post.get("image", {}).get("subject") or "").strip()
    if subject and cfg.get("images.commons", True):
        yield f"commons '{subject}'", lambda: _commons(subject)
    orientation = cfg.get("images.orientation", "landscape")
    for name in [cfg.get("images.provider"), cfg.get("images.fallback_provider")]:
        if not name or name not in PROVIDERS:
            continue
        for query in query_ladder(post, cfg):
            yield f"{name} '{query}'", lambda n=name, q=query: PROVIDERS[n](q, orientation)


def attach(post: dict, cfg: Config) -> dict:
    """Find, download and attach a cover image. Raises ImageError if none can be had."""
    if cfg.get("images.provider", "none") == "none":
        return post

    errors = []
    for label, search in candidates(post, cfg):
        try:
            found = search()
            path = download(found["url"], post["slug"])
        except (ImageError, requests.RequestException, OSError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        image = {k: v for k, v in post.get("image", {}).items()
                 if k not in ("license", "license_url")}
        post["image"] = {
            **image,
            "path": path,
            "credit": f"{found['author']} / {found['provider']}",
            "author": found["author"],
            "author_url": found["author_url"],
            "provider": found["provider"],
            "source_url": found["source_url"],
            **({"license": found["license"], "license_url": found.get("license_url", "")}
               if found.get("license") else {}),
        }
        return post
    raise ImageError("; ".join(errors) or "nenhum provedor de imagem configurado")
