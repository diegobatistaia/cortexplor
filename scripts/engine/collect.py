"""Step 1 - collection.

Pulls recent items from the configured RSS feeds, keeps only what matches the
niche keywords, drops anything already processed, and clusters items that are
telling the same story. A cluster is what the next step tries to verify.
"""
from __future__ import annotations

import feedparser

from .config import Config
from .store import seen_fingerprints
from .util import (content_words, domain_of, excerpt, fingerprint, isoformat, parse_date,
                   strip_tags, title_overlap, utcnow)


def fetch_feed(source: dict, timeout: int = 20) -> list[dict]:
    parsed = feedparser.parse(source["url"], agent="CortexplorBot/1.0 (+news aggregation)")
    if parsed.bozo and not parsed.entries:
        print(f"  ! {source['name']}: {parsed.get('bozo_exception', 'feed ilegível')}")
        return []
    items = []
    for entry in parsed.entries:
        link = entry.get("link") or ""
        title = strip_tags(entry.get("title") or "").strip()
        if not link or not title:
            continue
        summary = strip_tags(entry.get("summary") or entry.get("description") or "")
        published = (parse_date(entry.get("published") or entry.get("updated"))
                     or parse_date(entry.get("published_parsed")))
        items.append({
            "title": title,
            "url": link,
            "summary": summary,
            "published_at": isoformat(published) if published else "",
            "published_dt": published,
            "source": source["name"],
            "owner": source["owner"],
            "lang": source.get("lang", "en"),
            "tier": source.get("tier", 2),
            "kind": source.get("kind", "press"),
            "domain": domain_of(link),
        })
    return items


def blocked(item: dict, cfg: Config) -> bool:
    """Promocao e cupom nao viram materia, venha de onde vier."""
    haystack = f"{item['title']} {item['summary']}".lower()
    return any(bad.lower() in haystack for bad in cfg.get("keywords.exclude", []))


def matches_keywords(item: dict, cfg: Config) -> bool:
    haystack = f"{item['title']} {item['summary']}".lower()
    if blocked(item, cfg):
        return False
    return any(good.lower() in haystack for good in cfg.get("keywords.include", []))


def is_recent(item: dict, hours: int) -> bool:
    if not item.get("published_dt"):
        return False
    age = (utcnow() - item["published_dt"]).total_seconds() / 3600
    return 0 <= age <= hours


def cluster(items: list[dict], threshold: float = 0.5) -> list[dict]:
    """Group items that describe the same event.

    Overlap of meaningful title words is a blunt instrument, but it is
    deliberate: the cluster is only a candidate. Nothing is treated as
    confirmed until verify.py checks the facts against independent owners.
    """
    clusters: list[dict] = []
    for item in sorted(items, key=lambda i: (-i["tier"], i["published_at"]), reverse=True):
        for group in clusters:
            if title_overlap(item["title"], group["items"][0]["title"], item["lang"]) >= threshold:
                group["items"].append(item)
                break
        else:
            clusters.append({"items": [item]})

    out = []
    for group in clusters:
        # A primaria lidera a pauta. O titulo e o resumo saem dela, nao do
        # veiculo que a leu - e a diferenca entre noticiar o anuncio e
        # noticiar quem falou do anuncio.
        members = sorted(group["items"],
                         key=lambda i: (i.get("kind") != "primary", i["tier"], i["published_at"]))
        lead = members[0]
        owners = sorted({m["owner"] for m in members})
        out.append({
            "id": fingerprint(lead["title"], owners[0]),
            "title": lead["title"],
            "summary": excerpt(lead["summary"], 400),
            "lang_hint": lead["lang"],
            "owners": owners,
            "owner_count": len(owners),
            "primary_owners": sorted({m["owner"] for m in members
                                      if m.get("kind") == "primary"}),
            "items": members,
            "first_seen": isoformat(utcnow()),
            "keywords": content_words(lead["title"], lead["lang"])[:12],
        })
    out.sort(key=lambda c: (-c["owner_count"], c["items"][0]["published_at"]), reverse=False)
    out.sort(key=lambda c: c["owner_count"], reverse=True)
    return out


def run(cfg: Config, *, include_seen: bool = False) -> list[dict]:
    sources = cfg.get("sources.rss", [])
    hours = cfg.get("collection.lookback_hours", 48)
    hours_primary = cfg.get("collection.lookback_hours_primary", hours)
    min_title = cfg.get("collection.min_title_chars", 25)
    seen = set() if include_seen else seen_fingerprints()

    raw: list[dict] = []
    for source in sources:
        items = fetch_feed(source)
        primaria = source.get("kind") == "primary"
        janela = hours_primary if primaria else hours
        kept = [i for i in items
                if len(i["title"]) >= min_title and is_recent(i, janela)
                # Um blog corporativo de IA nao precisa dizer "IA" para ser
                # sobre IA - ele fala em primeira pessoa. Exigir palavra-chave
                # da primaria descarta justamente o anuncio original.
                and (primaria or matches_keywords(i, cfg))
                and not blocked(i, cfg)]
        raw.extend(kept)
        print(f"  {source['name']:28} {len(kept):3}/{len(items):3} itens no filtro")

    unique, urls = [], set()
    for item in raw:
        key = fingerprint(item["url"])
        if item["url"] in urls or key in seen:
            continue
        urls.add(item["url"])
        item["fingerprint"] = key
        unique.append(item)

    clusters = cluster(unique, cfg.get("collection.cluster_threshold", 0.42))
    limit = cfg.get("collection.max_candidates", 60)
    return clusters[:limit]


if __name__ == "__main__":
    from .config import load
    cfg = load()
    print(f"Coletando de {len(cfg.get('sources.rss', []))} feeds "
          f"(últimas {cfg.get('collection.lookback_hours')}h)\n")
    clusters = run(cfg, include_seen=True)
    print(f"\n{len(clusters)} pautas candidatas\n")
    for c in clusters[:12]:
        mark = "OK " if c["owner_count"] >= cfg.get("quality_gate.min_independent_sources", 2) else "-- "
        print(f"{mark}[{c['owner_count']} fontes] {c['title'][:78]}")
        print(f"      {', '.join(c['owners'])}")
