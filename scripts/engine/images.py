"""Step 6 - cover image, licensed and attributed.

Only Unsplash and Pexels APIs. Never scrape an image off a source article: the
photo in a news story is licensed to that outlet, not to us. Attribution is
stored with the post and rendered under the image.
"""
from __future__ import annotations

import io
import os
from pathlib import Path

import requests
from PIL import Image

from .config import ROOT, Config
from .util import fingerprint

IMG_DIR = ROOT / "assets" / "img"
MAX_WIDTH = 1200
QUALITY = 82
TIMEOUT = 25


class ImageError(RuntimeError):
    pass


def _unsplash(query: str, orientation: str) -> dict:
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        raise ImageError("UNSPLASH_ACCESS_KEY nao configurada")
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
        raise ImageError("PEXELS_API_KEY nao configurada")
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


PROVIDERS = {"unsplash": _unsplash, "pexels": _pexels}


def download(url: str, slug: str) -> str:
    """Fetch, downscale, save as JPEG. Returns the site-absolute path."""
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    image = Image.open(io.BytesIO(response.content)).convert("RGB")
    if image.width > MAX_WIDTH:
        height = round(image.height * MAX_WIDTH / image.width)
        image = image.resize((MAX_WIDTH, height), Image.LANCZOS)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{slug[:40]}-{fingerprint(url)[:8]}.jpg"
    image.save(IMG_DIR / name, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return f"/assets/img/{name}"


def attach(post: dict, cfg: Config) -> dict:
    """Find, download and attach a cover image. Raises ImageError if none can be had."""
    provider = cfg.get("images.provider", "none")
    if provider == "none":
        return post

    query = " ".join(filter(None, [
        post.get("image", {}).get("query", ""),
        cfg.get("images.query_suffix", ""),
    ])).strip()
    orientation = cfg.get("images.orientation", "landscape")

    errors = []
    for name in [provider, cfg.get("images.fallback_provider")]:
        if not name or name not in PROVIDERS:
            continue
        try:
            found = PROVIDERS[name](query, orientation)
            post["image"] = {
                **post.get("image", {}),
                "path": download(found["url"], post["slug"]),
                "credit": f"{found['author']} / {found['provider']}",
                "author": found["author"],
                "author_url": found["author_url"],
                "provider": found["provider"],
                "source_url": found["source_url"],
            }
            return post
        except (ImageError, requests.RequestException, OSError) as exc:
            errors.append(f"{name}: {exc}")
    raise ImageError("; ".join(errors) or "nenhum provedor de imagem configurado")
