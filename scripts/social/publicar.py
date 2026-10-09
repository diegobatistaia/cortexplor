#!/usr/bin/env python3
"""Publicação no Instagram (API com login do Instagram), só do que o dono aprovou.

As imagens precisam de endereço público: ficam no repositório público
diegobatistaia/cortexplor-midia. A chamada à API roda no GitHub Actions
(.github/workflows/instagram.yml), que é quem tem as chaves: uma por conta
(CONTAS abaixo; PT em INSTAGRAM_TOKEN, EN em INSTAGRAM_TOKEN_EN).

Na sessão (Claude):
    python scripts/social/publicar.py midia <slug> --repo <clone do cortexplor-midia>
        Converte os 6 slides do estilo escolhido em JPEG, copia para o clone
        e grava na fila o endereço público. Depois: commit e push no midia.
    python scripts/social/publicar.py pedir <slug>
    python scripts/social/publicar.py pedir --teste [--lang en]
    python scripts/social/publicar.py pedir --conferir [--lang en]   (só lê os últimos posts)
    python scripts/social/publicar.py proximo [--hora H]
        Horário fixo: para cada conta ativa, escolhe o aprovado mais antigo
        daquele idioma que já tem mídia pública e grava o pedido (as duas contas
        saem no mesmo horário). Sem aprovado, não faz nada. Nos horários
        fixos (HORARIOS) sai sempre um; nos extras (EXTRAS) só sai se a fila tiver
        mais carrosséis do que os horários fixos que ainda faltam no dia, para
        que tudo saia no mesmo dia.
        Grava social/publicar/pedido.json. O push desse arquivo no branch
        instagram dispara o workflow, que publica (ou só testa a chave).

No GitHub Actions:
    python scripts/social/publicar.py executar
        Lê o pedido, confere a chave e se ela é da conta certa, publica cada
        carrossel e marca "publicado".
"""
from __future__ import annotations

import argparse
import datetime
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
HORARIOS = [9, 14, 20]
EXTRAS = [10, 15, 21]
# Uma conta por idioma. "ativa" só vira True depois que o teste da chave passa;
# conta inativa não ganha carrossel (diario.py novas) nem publicação.
CONTAS = {
    "pt": {"usuario": "cortexplor", "secret": "INSTAGRAM_TOKEN", "ativa": True},
    "en": {"usuario": "cortexplor.en", "secret": "INSTAGRAM_TOKEN_EN", "ativa": True},
}


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
    lang = entry.get("lang", "pt")
    rel = args.slug if lang == "pt" else f"{lang}/{args.slug}"  # PT ficou na raiz
    dest = Path(args.repo) / rel
    dest.mkdir(parents=True, exist_ok=True)
    urls = []
    for i in range(1, 7):
        im = Image.open(src / f"{i:02d}.png").convert("RGB")  # a API só aceita JPEG
        out = dest / f"{i:02d}.jpg"
        im.save(out, "JPEG", quality=92, optimize=True)
        urls.append(f"{RAW}/{rel}/{i:02d}.jpg")
    entry["midia"] = urls
    diario.save_fila(fila)
    print("\n".join(urls))
    return 0


def gravar_pedido(pedido: dict) -> int:
    PEDIDO.parent.mkdir(parents=True, exist_ok=True)
    pedido["pedido_em"] = diario.now_iso()
    PEDIDO.write_text(json.dumps(pedido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"pedido gravado: {pedido}")
    return 0


def cmd_pedir(args) -> int:
    if args.conferir:
        return gravar_pedido({"acao": "conferir", "lang": args.lang})
    if args.teste:
        return gravar_pedido({"acao": "teste", "lang": args.lang})
    entry = next((e for e in diario.load_fila() if e["slug"] == args.slug), None)
    if not entry or entry["status"] != "aprovado":
        print(f"{args.slug}: só se pede publicação de carrossel aprovado")
        return 1
    if not entry.get("midia"):
        print(f"{args.slug}: rode 'midia' antes (imagens no repositório público)")
        return 1
    return gravar_pedido({"acao": "publicar", "itens": [{"slug": args.slug, "lang": entry.get("lang", "pt")}]})


def cmd_proximo(args) -> int:
    fila = diario.load_fila()
    hora = args.hora
    if hora is None:
        agora = diario.datetime.now(diario.TZ)
        hora = agora.hour + (1 if agora.minute >= 30 else 0)  # a rotina dispara às :57
    itens, falta_midia = [], []
    for lang, conta in CONTAS.items():
        if not conta["ativa"]:
            continue
        prontos = [e for e in fila if e["status"] == "aprovado" and e.get("lang", "pt") == lang]
        if not prontos:
            continue
        if hora in EXTRAS:
            fixos_restantes = sum(1 for h in HORARIOS if h > hora)
            if len(prontos) <= fixos_restantes:
                print(f"{lang}: horário extra das {hora}h; os {len(prontos)} da fila cabem nos fixos que faltam")
                continue
        entry = min(prontos, key=lambda e: (e.get("criado", ""), e.get("no") or 0))
        if not entry.get("midia"):
            falta_midia.append(entry["slug"])
            continue
        itens.append({"slug": entry["slug"], "lang": lang})
    for slug in falta_midia:
        print(f"{slug}: sem mídia pública; rode 'midia' e o push do cortexplor-midia antes")
    if falta_midia:
        return 1
    if not itens:
        print("nada: nenhum carrossel aprovado na fila para este horário")
        return 0
    return gravar_pedido({"acao": "publicar", "itens": itens})


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
    inicio = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=2)
    try:
        pub = call("POST", f"{ig}/media_publish", token, creation_id=car["id"])
    except ApiError as e:
        # O Instagram às vezes devolve erro (500, ou 403 "Application request limit
        # reached") e publica mesmo assim. Antes de dar o item como falho, confere se o
        # post já está na conta; só então segue como publicado.
        achado = achar_publicado(ig, token, caption, inicio)
        if not achado:
            raise
        print(f"AVISO: a API devolveu erro, mas o post está no ar: {achado['permalink']} ({str(e)[:80]})")
        return {"media_id": achado["id"], "permalink": achado["permalink"]}
    info = call("GET", pub["id"], token, fields="permalink")
    return {"media_id": pub["id"], "permalink": info.get("permalink")}


def achar_publicado(ig: str, token: str, caption: str, desde: datetime.datetime) -> dict | None:
    """Procura nos últimos posts da conta um criado desde `desde` com a mesma primeira linha."""
    primeira = caption.split("\n", 1)[0].strip()
    for _ in range(3):
        time.sleep(10)
        try:
            media = call("GET", f"{ig}/media", token, fields="caption,permalink,timestamp", limit=5).get("data", [])
        except ApiError:
            continue
        for m in media:
            quando = datetime.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            if quando >= desde and (m.get("caption") or "").split("\n", 1)[0].strip() == primeira:
                return m
    return None


def conta_da_chave(lang: str) -> tuple[str, str]:
    """Chave e id da conta do idioma. Recusa se a chave for de outra conta."""
    conta = CONTAS[lang]
    token = os.environ.get(conta["secret"], "").strip()
    if not token:
        raise ApiError(f"secret {conta['secret']} ausente")
    me = call("GET", "me", token, fields="user_id,username")
    if me.get("username") != conta["usuario"]:
        # Nunca publicar o carrossel EN na conta PT (ou o contrário).
        raise ApiError(f"a chave {conta['secret']} é da conta @{me.get('username')}, não de @{conta['usuario']}")
    print(f"{lang}: conta @{me['username']}")
    return token, me["user_id"]


def cmd_executar(args) -> int:
    pedido = json.loads(PEDIDO.read_text(encoding="utf-8"))
    resultado = {"pedido": pedido, "em": diario.now_iso()}
    if pedido.get("acao") == "conferir":
        # Só leitura: os últimos posts da conta, para saber se um erro da API
        # publicou mesmo assim (evita post duplicado ao tentar de novo).
        lang = pedido.get("lang", "pt")
        try:
            token, ig = conta_da_chave(lang)
            media = call("GET", f"{ig}/media", token, fields="caption,permalink,timestamp", limit=8).get("data", [])
        except ApiError as e:
            resultado.update(ok=False, erro=str(e))
            print(f"ERRO: {e}")
        else:
            resultado.update(ok=True, conta=CONTAS[lang]["usuario"], ultimos=[
                {"quando": m.get("timestamp"), "link": m.get("permalink"),
                 "inicio": (m.get("caption") or "").split("\n", 1)[0][:90]} for m in media])
            print(json.dumps(resultado["ultimos"], ensure_ascii=False, indent=1))
        RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0 if resultado["ok"] else 1

    if pedido.get("acao") == "teste":
        lang = pedido.get("lang", "pt")
        try:
            conta_da_chave(lang)
        except ApiError as e:
            resultado.update(ok=False, erro=str(e))
            print(f"ERRO: {e}")
        else:
            resultado.update(ok=True, conta=CONTAS[lang]["usuario"])
            print("teste ok: a chave funciona e é da conta certa")
        RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0 if resultado["ok"] else 1

    # Pedido antigo, de um item só: {"slug": ...}
    itens = pedido.get("itens") or [{"slug": pedido.get("slug"), "lang": "pt"}]
    fila = diario.load_fila()
    saidas, falhou = [], False
    for item in itens:
        saida = {"slug": item["slug"], "lang": item["lang"], "conta": CONTAS[item["lang"]]["usuario"]}
        entry = next((e for e in fila if e["slug"] == item["slug"]), None)
        try:
            if not entry or entry["status"] != "aprovado" or not entry.get("midia"):
                raise ApiError(f"{item['slug']} não está aprovado com mídia pública; nada publicado")
            if entry.get("lang", "pt") != item["lang"]:
                raise ApiError(f"{item['slug']} é do idioma {entry.get('lang', 'pt')}, não {item['lang']}")
            # A renovação devolve outra chave, e o Actions não consegue regravar o
            # secret: a chave é trocada à mão antes de vencer.
            token, ig = conta_da_chave(item["lang"])
            out = publicar(entry, ig, token)
        except ApiError as e:
            saida.update(ok=False, erro=str(e))
            falhou = True
            print(f"ERRO ({item['slug']}): {e}")
        else:
            entry.update(status="publicado", publicado_em=diario.now_iso(), **out)
            diario.save_fila(fila)
            saida.update(ok=True, **out)
            print(f"publicado ({item['lang']}): {out.get('permalink')}")
        saidas.append(saida)
    resultado.update(ok=not falhou, itens=saidas)
    RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if falhou else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("midia")
    p.add_argument("slug")
    p.add_argument("--repo", required=True)
    p = sub.add_parser("pedir")
    p.add_argument("slug", nargs="?")
    p.add_argument("--teste", action="store_true")
    p.add_argument("--conferir", action="store_true", help="só lista os últimos posts da conta")
    p.add_argument("--lang", default="pt", choices=sorted(CONTAS), help="conta do teste ou da conferência")
    p = sub.add_parser("proximo")
    p.add_argument("--hora", type=int, help="hora do horário (BRT); padrão: a hora cheia mais próxima")
    sub.add_parser("executar")
    args = ap.parse_args(argv)
    if args.cmd == "pedir" and not (args.slug or args.teste or args.conferir):
        ap.error("pedir precisa de um slug ou --teste")
    return {"midia": cmd_midia, "pedir": cmd_pedir, "proximo": cmd_proximo, "executar": cmd_executar}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
