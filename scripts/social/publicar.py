#!/usr/bin/env python3
"""Publicação no Instagram (API com login do Instagram), só do que o dono aprovou.

As imagens precisam de endereço público: ficam no repositório público
diegobatistaia/cortexplor-midia. A chamada à API roda no GitHub Actions
(.github/workflows/instagram.yml), que é quem tem a chave INSTAGRAM_TOKEN.

Na sessão (Claude):
    python scripts/social/publicar.py midia <slug> --repo <clone do cortexplor-midia>
        Converte os 6 slides do estilo escolhido em JPEG, copia para o clone
        e grava na fila o endereço público. Depois: commit e push no midia.
    python scripts/social/publicar.py pedir <slug>
    python scripts/social/publicar.py pedir --teste
    python scripts/social/publicar.py proximo [--hora H]
        Horário fixo: escolhe o aprovado mais antigo da fila que já tem mídia
        pública e grava o pedido dele. Sem aprovado, não faz nada. Nos horários
        fixos (HORARIOS) sai sempre um; nos extras (EXTRAS) só sai se a fila tiver
        mais carrosséis do que os horários fixos que ainda faltam no dia, para
        que tudo saia no mesmo dia.
        Grava social/publicar/pedido.json. O push desse arquivo no branch
        instagram dispara o workflow, que publica (ou só testa a chave).

No GitHub Actions:
    python scripts/social/publicar.py executar
        Lê o pedido, confere a chave, publica o carrossel e marca "publicado".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diario  # noqa: E402

ROOT = diario.ROOT
PEDIDO = ROOT / "social" / "publicar" / "pedido.json"
RESULTADO = ROOT / "social" / "publicar" / "ultimo.json"
MIDIA_REPO = "diegobatistaia/cortexplor-midia"
RAW = f"https://raw.githubusercontent.com/{MIDIA_REPO}/main"
API = "https://graph.instagram.com/v23.0"
# Horas (BRT) em que sai um carrossel. Fixos: sempre que houver fila. Extras: só
# quando houver mais carrosséis do que horários fixos restantes no dia.
HORARIOS = [8, 11, 16]
EXTRAS = [13, 19, 21]


# ----------------------------------------------------------------------------
# Sessão: mídia e pedido
# ----------------------------------------------------------------------------
def cmd_midia(args) -> int:
    from PIL import Image

    fila = diario.load_fila()
    entry = next((e for e in fila if e["slug"] == args.slug), None)
    if not entry:
        print(f"{args.slug}: não está na fila")
        return 1
    src = ROOT / entry["slides"]
    dest = Path(args.repo) / args.slug
    dest.mkdir(parents=True, exist_ok=True)
    urls = []
    for i in range(1, 7):
        im = Image.open(src / f"{i:02d}.png").convert("RGB")  # a API só aceita JPEG
        out = dest / f"{i:02d}.jpg"
        im.save(out, "JPEG", quality=92, optimize=True)
        urls.append(f"{RAW}/{args.slug}/{i:02d}.jpg")
    entry["midia"] = urls
    diario.save_fila(fila)
    print("\n".join(urls))
    return 0


def cmd_pedir(args) -> int:
    PEDIDO.parent.mkdir(parents=True, exist_ok=True)
    if args.teste:
        pedido = {"acao": "teste"}
    else:
        entry = next((e for e in diario.load_fila() if e["slug"] == args.slug), None)
        if not entry or entry["status"] != "aprovado":
            print(f"{args.slug}: só se pede publicação de carrossel aprovado")
            return 1
        if not entry.get("midia"):
            print(f"{args.slug}: rode 'midia' antes (imagens no repositório público)")
            return 1
        pedido = {"acao": "publicar", "slug": args.slug}
    pedido["pedido_em"] = diario.now_iso()
    PEDIDO.write_text(json.dumps(pedido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"pedido gravado: {pedido}")
    return 0


def cmd_proximo(args) -> int:
    fila = diario.load_fila()
    prontos = [e for e in fila if e["status"] == "aprovado"]
    if not prontos:
        print("nada: nenhum carrossel aprovado na fila")
        return 0
    hora = args.hora
    if hora is None:
        agora = diario.datetime.now(diario.TZ)
        hora = agora.hour + (1 if agora.minute >= 30 else 0)  # a rotina dispara às :57
    if hora in EXTRAS:
        fixos_restantes = sum(1 for h in HORARIOS if h > hora)
        if len(prontos) <= fixos_restantes:
            print(f"nada: horário extra das {hora}h; os {len(prontos)} da fila cabem nos fixos que faltam")
            return 0
    entry = min(prontos, key=lambda e: (e.get("criado", ""), e.get("no") or 0))
    if not entry.get("midia"):
        print(f"{entry['slug']}: sem mídia pública; rode 'midia' e o push do cortexplor-midia antes")
        return 1
    args.slug, args.teste = entry["slug"], False
    return cmd_pedir(args)


# ----------------------------------------------------------------------------
# GitHub Actions: chamada à API
# ----------------------------------------------------------------------------
class ApiError(RuntimeError):
    pass


def call(method: str, path: str, token: str, **params) -> dict:
    params["access_token"] = token
    data = urllib.parse.urlencode(params).encode()
    url = path if path.startswith("http") else f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        # Nunca imprimir a chave: a URL de GET carrega o token, então só o corpo do erro sai.
        raise ApiError(f"HTTP {e.code} em {path}: {body[:500]}") from None


def renovar(token: str) -> None:
    """Renova a validade da chave (60 dias a partir de agora). Não imprime a chave."""
    try:
        r = call("GET", "https://graph.instagram.com/refresh_access_token", token, grant_type="ig_refresh_token")
    except ApiError as e:
        print(f"AVISO: renovação da chave falhou: {e}")
        return
    dias = int(r.get("expires_in", 0)) // 86400
    mesma = r.get("access_token") == token
    print(f"chave renovada: vale mais {dias} dias; {'mesma chave' if mesma else 'CHAVE NOVA (precisa trocar o secret)'}")


def esperar(container: str, token: str) -> None:
    for _ in range(30):
        st = call("GET", container, token, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise ApiError(f"container {container}: {st}")
        time.sleep(5)
    raise ApiError(f"container {container}: não ficou pronto")


def publicar(entry: dict, ig: str, token: str) -> dict:
    spec = json.loads((ROOT / "social" / "specs" / f"{entry['slug']}.json").read_text(encoding="utf-8"))
    text, tags = (ROOT / entry["legenda"]).read_text(encoding="utf-8").rstrip().rsplit("\n\n", 1)
    caption = f"{text}\n\n{tags}"
    alts = spec.get("alt", [])
    children = []
    for i, url in enumerate(entry["midia"]):
        params = {"image_url": url, "is_carousel_item": "true"}
        if i < len(alts):
            params["alt_text"] = alts[i]
        try:
            c = call("POST", f"{ig}/media", token, **params)
        except ApiError as e:
            if "alt_text" not in str(e):
                raise
            params.pop("alt_text")  # conta sem suporte a texto alternativo: segue sem ele
            c = call("POST", f"{ig}/media", token, **params)
        children.append(c["id"])
        print(f"slide {i + 1}: container {c['id']}")
    for c in children:
        esperar(c, token)
    car = call("POST", f"{ig}/media", token, media_type="CAROUSEL", children=",".join(children), caption=caption)
    esperar(car["id"], token)
    pub = call("POST", f"{ig}/media_publish", token, creation_id=car["id"])
    info = call("GET", pub["id"], token, fields="permalink")
    return {"media_id": pub["id"], "permalink": info.get("permalink")}


def cmd_executar(args) -> int:
    token = os.environ.get("INSTAGRAM_TOKEN", "").strip()
    if not token:
        print("ERRO: secret INSTAGRAM_TOKEN ausente")
        return 1
    pedido = json.loads(PEDIDO.read_text(encoding="utf-8"))
    me = call("GET", "me", token, fields="user_id,username")
    ig = me["user_id"]
    print(f"conta: @{me.get('username')}")
    # A renovação devolve outra chave, e o Actions não consegue regravar o secret:
    # renovar aqui não adiantaria. A chave do secret é trocada à mão antes de vencer.
    resultado = {"pedido": pedido, "conta": me.get("username"), "em": diario.now_iso()}
    if pedido.get("acao") == "teste":
        resultado["ok"] = True
        print("teste ok: a chave funciona e a conta foi encontrada")
    else:
        fila = diario.load_fila()
        entry = next((e for e in fila if e["slug"] == pedido.get("slug")), None)
        if not entry or entry["status"] != "aprovado" or not entry.get("midia"):
            print(f"ERRO: {pedido.get('slug')} não está aprovado com mídia pública; nada publicado")
            return 1
        try:
            out = publicar(entry, ig, token)
        except ApiError as e:
            resultado.update(ok=False, erro=str(e))
            RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"ERRO: {e}")
            return 1
        entry.update(status="publicado", publicado_em=diario.now_iso(), **out)
        diario.save_fila(fila)
        resultado.update(ok=True, **out)
        print(f"publicado: {out.get('permalink')}")
    RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("midia")
    p.add_argument("slug")
    p.add_argument("--repo", required=True)
    p = sub.add_parser("pedir")
    p.add_argument("slug", nargs="?")
    p.add_argument("--teste", action="store_true")
    p = sub.add_parser("proximo")
    p.add_argument("--hora", type=int, help="hora do horário (BRT); padrão: a hora cheia mais próxima")
    sub.add_parser("executar")
    args = ap.parse_args(argv)
    if args.cmd == "pedir" and not (args.slug or args.teste):
        ap.error("pedir precisa de um slug ou --teste")
    return {"midia": cmd_midia, "pedir": cmd_pedir, "proximo": cmd_proximo, "executar": cmd_executar}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
