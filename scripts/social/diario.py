#!/usr/bin/env python3
"""Rotina diária do Instagram: matérias novas do site → carrosséis na fila de aprovação.

    python scripts/social/diario.py novas [--data AAAA-MM-DD] [--lang pt]
        Busca no branch main as matérias publicadas na data (padrão: hoje, no fuso
        do site) que ainda não têm carrossel, traz a matéria e a foto para este
        branch e cria o spec de cada uma (redacao.py prepare).

    (a redação escreve os specs: skill instagram-carrossel)

    python scripts/social/diario.py fechar [--aprovar] <slug> [<slug> ...]
        Para cada matéria, na ordem dada: escolhe o estilo pelo rodízio, roda o
        controle completo (redacao.py check + foto), renderiza só o estilo
        escolhido, monta a legenda e põe o carrossel na fila como "pendente".
        Com --aprovar, entra já "aprovado": o dono dispensou a aprovação por
        carrossel em 05/10/2026 e o check passou a ser o controle.

    python scripts/social/diario.py fila
        Mostra a fila (pendentes primeiro).

    python scripts/social/diario.py aprovar <slug>
    python scripts/social/diario.py descartar <slug>
        Registra a decisão do dono. Nada é publicado aqui: a publicação só lê
        carrosséis "aprovado".

A fila fica em social/fila.json; é o histórico que o rodízio usa.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import redacao  # noqa: E402
from rotation import STYLES, eligible_styles, photo_report  # noqa: E402

ROOT = redacao.ROOT
FILA = ROOT / "social" / "fila.json"
TZ = redacao.TZ
# Primeiro post do perfil (apresentação, fora da fila): o rodízio parte dele.
FIRST_STYLE = {"pt": "duotone"}


# ----------------------------------------------------------------------------
# Fila
# ----------------------------------------------------------------------------
def load_fila() -> list[dict]:
    if not FILA.exists():
        return []
    return json.loads(FILA.read_text(encoding="utf-8"))


def save_fila(fila: list[dict]) -> None:
    FILA.write_text(json.dumps(fila, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def pick_style(fila: list[dict], lang: str, eligible: list[str], seed: str) -> str:
    """Estilo menos usado nas últimas 8 entradas da conta, nunca igual ao anterior."""
    hist = [FIRST_STYLE[lang]] if lang in FIRST_STYLE else []
    hist += [e["style"] for e in fila if e["lang"] == lang and e["status"] != "descartado"]
    last = hist[-1] if hist else None
    recent = hist[-(len(STYLES)):]
    options = [s for s in eligible if s != last] or eligible
    fewest = min(recent.count(s) for s in options)
    pool = [s for s in options if recent.count(s) == fewest]
    return random.Random(seed).choice(pool)


# ----------------------------------------------------------------------------
# novas
# ----------------------------------------------------------------------------
def git(*args: str, binary: bool = False):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode("utf-8")


def cmd_novas(args) -> int:
    day = date.fromisoformat(args.data) if args.data else datetime.now(TZ).date()
    lang = args.lang
    git("fetch", "-q", "origin", "main")
    ref = "FETCH_HEAD"
    files = [f for f in git("ls-tree", "--name-only", ref, f"content/{lang}/").split() if f.endswith(".json")]
    have = {p.stem for p in redacao.SPECS.glob("*.json")}
    found = []
    for f in files:
        post = json.loads(git("show", f"{ref}:{f}"))
        when = post.get("published_at")
        if post.get("status") != "published" or not when:
            continue
        if datetime.fromisoformat(when).astimezone(TZ).date() != day:
            continue
        found.append((when, post))
    found.sort(key=lambda x: x[0])
    if not found:
        print(f"nenhuma matéria publicada em {day.isoformat()} ({lang}).")
        return 0
    created = []
    for _, post in found:
        slug = post["slug"]
        if slug in have:
            print(f"já tem carrossel: {slug}")
            continue
        dest = ROOT / "content" / lang / f"{slug}.json"
        dest.write_bytes(git("show", f"{ref}:content/{lang}/{slug}.json", binary=True))
        img = (post.get("image") or {}).get("path", "").lstrip("/")
        if img:
            (ROOT / img).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / img).write_bytes(git("show", f"{ref}:{img}", binary=True))
        rc = redacao.main(["prepare", slug, "--lang", lang])
        if rc == 0:
            created.append(slug)
    if created:
        print("\nSpecs criados (escreva cada um seguindo a skill instagram-carrossel):")
        for s in created:
            print(f"  social/specs/{s}.json")
        print("Depois: python scripts/social/diario.py fechar " + " ".join(created))
    return 0


# ----------------------------------------------------------------------------
# fechar
# ----------------------------------------------------------------------------
def cmd_fechar(args) -> int:
    import carousel

    fila = load_fila()
    bad = 0
    for slug in args.slugs:
        if any(e["slug"] == slug for e in fila):
            print(f"{slug}: já está na fila")
            continue
        spec = redacao.load_spec(slug)
        err, warn = redacao.check_spec(spec)
        for w in warn:
            print(f"{slug}: AVISO: {w}")
        if err:
            for e in err:
                print(f"{slug}: ERRO: {e}")
            bad += 1
            continue
        for w in photo_report(spec)[0]:
            print(f"{slug}: AVISO: {w}")
        lang = spec.get("lang", "pt")
        style = pick_style(fila, lang, eligible_styles(spec), seed=slug)
        carousel.build(slug, [style])
        redacao.main(["caption", slug])
        fila.append({
            "slug": slug,
            "lang": lang,
            "no": spec.get("no"),
            "style": style,
            "cta_variant": spec["caption"]["cta_variant"],
            "status": "aprovado" if args.aprovar else "pendente",
            "criado": now_iso(),
            **({"aprovado_em": now_iso(), "aprovado_por": "automatico"} if args.aprovar else {}),
            "slides": f"social/out/{slug}/{style}",
            "folha": f"social/out/{slug}/folha-{style}.png",
            "legenda": f"social/out/{slug}/legenda-{lang}.txt",
        })
        save_fila(fila)
        print(f"{slug}: na fila ({fila[-1]['status']}), estilo {style}, chamada {spec['caption']['cta_variant']}")
    return 1 if bad else 0


# ----------------------------------------------------------------------------
# fila / aprovar / descartar
# ----------------------------------------------------------------------------
def cmd_fila(args) -> int:
    fila = load_fila()
    if not fila:
        print("fila vazia")
        return 0
    order = {"pendente": 0, "aprovado": 1, "publicado": 2, "descartado": 3}
    for e in sorted(fila, key=lambda e: (order.get(e["status"], 9), e["criado"])):
        print(f"{e['status']:<10} nº {e.get('no')}  {e['style']:<9}  {e['slug']}")
    return 0


def set_status(slug: str, status: str, field: str) -> int:
    fila = load_fila()
    for e in fila:
        if e["slug"] == slug:
            if e["status"] == "publicado":
                print(f"{slug}: já publicado; nada a mudar")
                return 1
            e["status"] = status
            e[field] = now_iso()
            save_fila(fila)
            print(f"{slug}: {status}")
            return 0
    print(f"{slug}: não está na fila")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("novas")
    p.add_argument("--data")
    p.add_argument("--lang", default="pt")
    p = sub.add_parser("fechar")
    p.add_argument("--aprovar", action="store_true", help="entra na fila já aprovado")
    p.add_argument("slugs", nargs="+")
    sub.add_parser("fila")
    for name in ("aprovar", "descartar"):
        p = sub.add_parser(name)
        p.add_argument("slug")
    args = ap.parse_args(argv)
    if args.cmd == "novas":
        return cmd_novas(args)
    if args.cmd == "fechar":
        return cmd_fechar(args)
    if args.cmd == "fila":
        return cmd_fila(args)
    if args.cmd == "aprovar":
        return set_status(args.slug, "aprovado", "aprovado_em")
    return set_status(args.slug, "descartado", "descartado_em")


if __name__ == "__main__":
    sys.exit(main())
