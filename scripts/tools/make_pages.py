#!/usr/bin/env python3
"""Generate the institutional pages AdSense requires, one set per language.

Sobre / Privacidade / Contato / Termos. Written from site.config.yaml so the
domain, e-mail and publisher name stay in one place. Re-run after changing any
of those; the files are plain JSON and can also be edited by hand afterwards.

Run: python scripts/tools/make_pages.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.engine.config import ROOT, load  # noqa: E402
from scripts.engine.util import isoformat, utcnow  # noqa: E402

OUT = ROOT / "content" / "pages"


def p(text):
    return {"type": "p", "text": text, "items": []}


def h2(text):
    return {"type": "h2", "text": text, "items": []}


def ul(items):
    return {"type": "list", "text": "", "items": items}


def pages_for(lang: str, cfg) -> list[dict]:
    name = cfg.get("site.name")
    domain = cfg.get("site.domain")
    email = cfg.get("legal.contact_email")
    niche = cfg.localized("niche.term", lang)
    mail = f'<a href="mailto:{email}">{email}</a>'

    if lang == "pt":
        return [
            {"slug": "sobre", "title": f"Sobre o {name}",
             "description": f"O que e o {name}, como as materias sao produzidas e checadas.",
             "body": [
                 p(f"O {name} e um site de noticias dedicado a {niche}. Cobrimos lancamentos "
                   f"de modelos, movimentos de mercado, regulacao e aplicacoes praticas de IA "
                   f"em empresas, no Brasil e no mundo."),
                 h2("Como as materias sao produzidas"),
                 p("Nossa producao editorial e assistida por inteligencia artificial e opera "
                   "sobre um processo fixo de checagem. O fluxo e o mesmo para toda materia:"),
                 ul(["Coleta de noticias recentes em fontes jornalisticas estabelecidas;",
                     "Checagem cruzada: um fato so entra no texto se aparecer confirmado em "
                     "pelo menos duas fontes independentes entre si;",
                     "Redacao original a partir dos fatos confirmados, sem copia ou parafrase "
                     "proxima do texto-fonte;",
                     "Verificacao automatica de originalidade, estrutura e citacao de fontes "
                     "antes da publicacao."]),
                 p("Pautas que nao passam por todas essas etapas nao sao publicadas: ficam "
                   "retidas para revisao humana ou sao descartadas."),
                 h2("Transparencia"),
                 p("Toda materia lista, ao final, as fontes usadas na apuracao. Quando as "
                   "fontes divergem sobre um dado, isso e dito no texto em vez de escondido."),
                 h2("Correcoes"),
                 p(f"Encontrou um erro? Escreva para {mail} com o link da materia. "
                   f"Correcoes relevantes sao sinalizadas na propria pagina."),
             ]},
            {"slug": "privacidade", "title": "Politica de Privacidade",
             "description": f"Como o {name} trata dados de navegacao, cookies e publicidade.",
             "body": [
                 p(f"Esta politica descreve como o {name} ({domain}) trata informacoes de "
                   f"quem visita o site."),
                 h2("Dados que coletamos"),
                 p("Nao pedimos cadastro para ler o site e nao coletamos nome, CPF ou "
                   "documento. Coletamos apenas dados de navegacao agregados: paginas "
                   "visitadas, tempo de permanencia, origem do acesso, tipo de dispositivo "
                   "e pais aproximado."),
                 h2("Google Analytics"),
                 p("Usamos o Google Analytics 4 para entender o desempenho do site. Ele grava "
                   "cookies no seu navegador e trata o endereco IP de forma anonimizada. "
                   "Voce pode bloquear esses cookies nas configuracoes do navegador ou pela "
                   "extensao oficial de opt-out do Google."),
                 h2("Publicidade"),
                 p("Este site exibe anuncios do Google AdSense. O Google e seus parceiros "
                   "podem usar cookies para exibir anuncios com base em visitas anteriores a "
                   "este e a outros sites. Voce pode desativar a publicidade personalizada "
                   'nas <a href="https://www.google.com/settings/ads" rel="nofollow noopener" '
                   'target="_blank">configuracoes de anuncios do Google</a>.'),
                 h2("Newsletter"),
                 p("Se voce assinar nossa newsletter, guardamos apenas o e-mail informado, "
                   "usado somente para enviar os proprios boletins. O cancelamento pode ser "
                   "feito a qualquer momento pelo link no rodape de cada envio."),
                 h2("Seus direitos (LGPD)"),
                 p(f"Voce pode solicitar acesso, correcao ou exclusao dos seus dados pelo "
                   f"e-mail {mail}. Respondemos em ate 15 dias."),
                 h2("Alteracoes"),
                 p("Mudancas nesta politica sao publicadas nesta mesma pagina, com a data de "
                   "atualizacao no topo."),
             ]},
            {"slug": "contato", "title": "Contato",
             "description": f"Fale com a redacao do {name}: pautas, correcoes e imprensa.",
             "body": [
                 p(f"O canal oficial de contato do {name} e o e-mail {mail}."),
                 h2("Para que serve cada assunto"),
                 ul(["<strong>Correcao</strong>: envie o link da materia e o ponto especifico "
                     "a corrigir. Priorizamos esse tipo de mensagem.",
                     "<strong>Sugestao de pauta</strong>: conte o fato e indique onde ele foi "
                     "publicado ou anunciado.",
                     "<strong>Imprensa e releases</strong>: aceitamos, mas releases nao viram "
                     "materia sozinhos - dependem de confirmacao independente.",
                     "<strong>Publicidade</strong>: nossa monetizacao hoje e feita por redes "
                     "de anuncio; nao vendemos conteudo patrocinado."]),
                 h2("Prazo de resposta"),
                 p("Lemos todas as mensagens. Correcoes sao respondidas em ate 2 dias uteis; "
                   "os demais assuntos, conforme a disponibilidade da redacao."),
             ]},
            {"slug": "termos", "title": "Termos de Uso",
             "description": f"Condicoes de uso do conteudo publicado no {name}.",
             "body": [
                 p(f"Ao navegar em {domain} voce concorda com os termos abaixo."),
                 h2("Uso do conteudo"),
                 p("Os textos publicados aqui sao originais e protegidos por direito autoral. "
                   "E permitido citar trechos curtos com credito e link para a materia "
                   "original. Nao e permitida a reproducao integral sem autorizacao previa."),
                 h2("Natureza da informacao"),
                 p("Publicamos jornalismo sobre tecnologia. Nada no site constitui "
                   "aconselhamento de investimento, juridico ou profissional. Decisoes "
                   "tomadas com base no conteudo sao de responsabilidade do leitor."),
                 h2("Conteudo assistido por IA"),
                 p("Nossas materias sao produzidas com apoio de inteligencia artificial sob "
                   "um processo de checagem em multiplas fontes. Ainda assim, erros podem "
                   "ocorrer - e por isso mantemos um canal de correcao aberto."),
                 h2("Links externos"),
                 p("Materias linkam para as fontes usadas na apuracao. Nao respondemos pelo "
                   "conteudo, pelas politicas nem pela disponibilidade desses sites."),
                 h2("Disponibilidade"),
                 p("O site e oferecido no estado em que se encontra, sem garantia de "
                   "funcionamento ininterrupto."),
             ]},
        ]

    if lang == "en":
        return [
            {"slug": "about", "title": f"About {name}",
             "description": f"What {name} is, and how our stories are produced and checked.",
             "body": [
                 p(f"{name} is a news site covering {niche}: model releases, market moves, "
                   f"regulation and the practical use of AI inside companies, in Brazil and "
                   f"worldwide."),
                 h2("How our stories are produced"),
                 p("Our editorial production is AI-assisted and runs on a fixed verification "
                   "process. Every story follows the same path:"),
                 ul(["Collection of recent reporting from established news sources;",
                     "Cross-checking: a fact only enters the text if at least two mutually "
                     "independent sources confirm it;",
                     "Original writing from the confirmed facts - never a copy or a close "
                     "paraphrase of the source text;",
                     "Automated checks on originality, structure and source citation before "
                     "publication."]),
                 p("Stories that fail any of these steps are not published: they are held for "
                   "human review or dropped."),
                 h2("Transparency"),
                 p("Every story lists the sources used. When sources disagree on a number or "
                   "a detail, we say so in the text instead of hiding it."),
                 h2("Corrections"),
                 p(f"Found an error? Write to {mail} with the link. Meaningful corrections are "
                   f"flagged on the page itself."),
             ]},
            {"slug": "privacy", "title": "Privacy Policy",
             "description": f"How {name} handles browsing data, cookies and advertising.",
             "body": [
                 p(f"This policy explains how {name} ({domain}) handles information about "
                   f"people who visit the site."),
                 h2("What we collect"),
                 p("Reading the site requires no account, and we do not collect names or "
                   "identity documents. We collect aggregate browsing data only: pages "
                   "viewed, time on page, referral source, device type and approximate "
                   "country."),
                 h2("Google Analytics"),
                 p("We use Google Analytics 4 to understand how the site performs. It stores "
                   "cookies in your browser and processes IP addresses in anonymised form. "
                   "You can block these cookies in your browser settings or with Google's "
                   "official opt-out extension."),
                 h2("Advertising"),
                 p("This site shows Google AdSense ads. Google and its partners may use "
                   "cookies to serve ads based on your prior visits to this and other sites. "
                   'You can turn off personalised advertising in your <a '
                   'href="https://www.google.com/settings/ads" rel="nofollow noopener" '
                   'target="_blank">Google ad settings</a>.'),
                 h2("Newsletter"),
                 p("If you subscribe, we store only the e-mail address you provide, used "
                   "solely to send the newsletter. You can unsubscribe at any time via the "
                   "link at the bottom of every issue."),
                 h2("Your rights"),
                 p(f"You may request access to, correction of, or deletion of your data at "
                   f"{mail}. We reply within 15 days."),
                 h2("Changes"),
                 p("Any change to this policy is published on this page, with the update "
                   "date at the top."),
             ]},
            {"slug": "contact", "title": "Contact",
             "description": f"Reach the {name} newsroom: tips, corrections and press.",
             "body": [
                 p(f"The official contact channel for {name} is {mail}."),
                 h2("What to send"),
                 ul(["<strong>Correction</strong>: send the story link and the specific point "
                     "to fix. These get priority.",
                     "<strong>Story tip</strong>: tell us the fact and where it was published "
                     "or announced.",
                     "<strong>Press and releases</strong>: welcome, but a release alone is "
                     "never a story - it needs independent confirmation.",
                     "<strong>Advertising</strong>: we monetise through ad networks and do "
                     "not sell sponsored content."]),
                 h2("Response time"),
                 p("We read everything. Corrections are answered within two business days; "
                   "other subjects as the newsroom's schedule allows."),
             ]},
            {"slug": "terms", "title": "Terms of Use",
             "description": f"Conditions for using content published on {name}.",
             "body": [
                 p(f"By browsing {domain} you agree to the terms below."),
                 h2("Use of content"),
                 p("The texts published here are original and protected by copyright. Short "
                   "quotations are allowed with credit and a link to the original story. Full "
                   "reproduction requires prior permission."),
                 h2("Nature of the information"),
                 p("We publish technology journalism. Nothing on this site is investment, "
                   "legal or professional advice. Decisions taken on the basis of our content "
                   "are the reader's responsibility."),
                 h2("AI-assisted content"),
                 p("Our stories are produced with the support of artificial intelligence under "
                   "a multi-source verification process. Errors can still happen - which is "
                   "why the corrections channel stays open."),
                 h2("External links"),
                 p("Stories link to the sources used. We are not responsible for the content, "
                   "policies or availability of those sites."),
                 h2("Availability"),
                 p("The site is provided as is, with no guarantee of uninterrupted service."),
             ]},
        ]

    return [
        {"slug": "acerca", "title": f"Acerca de {name}",
         "description": f"Que es {name} y como se producen y verifican nuestras notas.",
         "body": [
             p(f"{name} es un sitio de noticias dedicado a la {niche}. Cubrimos lanzamientos "
               f"de modelos, movimientos de mercado, regulacion y aplicaciones practicas de "
               f"IA en empresas, en Brasil y en el mundo."),
             h2("Como se producen las notas"),
             p("Nuestra produccion editorial es asistida por inteligencia artificial y opera "
               "sobre un proceso fijo de verificacion. El flujo es el mismo para toda nota:"),
             ul(["Recoleccion de notas recientes en fuentes periodisticas establecidas;",
                 "Verificacion cruzada: un dato solo entra en el texto si aparece confirmado "
                 "en al menos dos fuentes independientes entre si;",
                 "Redaccion original a partir de los datos confirmados, sin copia ni parafrasis "
                 "cercana del texto fuente;",
                 "Verificacion automatica de originalidad, estructura y cita de fuentes antes "
                 "de publicar."]),
             p("Las notas que no pasan por todas esas etapas no se publican: quedan retenidas "
               "para revision humana o se descartan."),
             h2("Transparencia"),
             p("Cada nota lista al final las fuentes usadas. Cuando las fuentes difieren sobre "
               "un dato, lo decimos en el texto en lugar de esconderlo."),
             h2("Correcciones"),
             p(f"Encontraste un error? Escribinos a {mail} con el enlace de la nota. Las "
               f"correcciones relevantes se senalan en la propia pagina."),
         ]},
        {"slug": "privacidad", "title": "Politica de Privacidad",
         "description": f"Como {name} trata datos de navegacion, cookies y publicidad.",
         "body": [
             p(f"Esta politica describe como {name} ({domain}) trata la informacion de quienes "
               f"visitan el sitio."),
             h2("Datos que recopilamos"),
             p("No pedimos registro para leer el sitio y no recopilamos nombre ni documentos "
               "de identidad. Solo recopilamos datos de navegacion agregados: paginas vistas, "
               "tiempo de permanencia, origen del acceso, tipo de dispositivo y pais "
               "aproximado."),
             h2("Google Analytics"),
             p("Usamos Google Analytics 4 para entender el desempeno del sitio. Guarda cookies "
               "en tu navegador y trata la direccion IP de forma anonimizada. Podes bloquear "
               "esas cookies en la configuracion del navegador o con la extension oficial de "
               "exclusion de Google."),
             h2("Publicidad"),
             p("Este sitio muestra anuncios de Google AdSense. Google y sus socios pueden usar "
               "cookies para mostrar anuncios segun tus visitas previas a este y a otros "
               'sitios. Podes desactivar la publicidad personalizada en la <a '
               'href="https://www.google.com/settings/ads" rel="nofollow noopener" '
               'target="_blank">configuracion de anuncios de Google</a>.'),
             h2("Newsletter"),
             p("Si te suscribis, guardamos solo el correo informado, usado unicamente para "
               "enviar los boletines. Podes cancelar cuando quieras con el enlace al pie de "
               "cada envio."),
             h2("Tus derechos"),
             p(f"Podes solicitar acceso, correccion o eliminacion de tus datos escribiendo a "
               f"{mail}. Respondemos en hasta 15 dias."),
             h2("Cambios"),
             p("Los cambios en esta politica se publican en esta misma pagina, con la fecha de "
               "actualizacion arriba."),
         ]},
        {"slug": "contacto", "title": "Contacto",
         "description": f"Escribi a la redaccion de {name}: temas, correcciones y prensa.",
         "body": [
             p(f"El canal oficial de contacto de {name} es {mail}."),
             h2("Para que sirve cada asunto"),
             ul(["<strong>Correccion</strong>: envia el enlace de la nota y el punto especifico "
                 "a corregir. Priorizamos ese tipo de mensaje.",
                 "<strong>Sugerencia de tema</strong>: contanos el hecho e indica donde fue "
                 "publicado o anunciado.",
                 "<strong>Prensa y comunicados</strong>: los recibimos, pero un comunicado solo "
                 "no se convierte en nota: depende de confirmacion independiente.",
                 "<strong>Publicidad</strong>: hoy monetizamos con redes de anuncios; no "
                 "vendemos contenido patrocinado."]),
             h2("Plazo de respuesta"),
             p("Leemos todos los mensajes. Las correcciones se responden en hasta 2 dias "
               "habiles; los demas asuntos, segun la disponibilidad de la redaccion."),
         ]},
        {"slug": "terminos", "title": "Terminos de Uso",
         "description": f"Condiciones de uso del contenido publicado en {name}.",
         "body": [
             p(f"Al navegar en {domain} aceptas los terminos siguientes."),
             h2("Uso del contenido"),
             p("Los textos publicados aqui son originales y estan protegidos por derecho de "
               "autor. Se permite citar fragmentos cortos con credito y enlace a la nota "
               "original. No se permite la reproduccion integral sin autorizacion previa."),
             h2("Naturaleza de la informacion"),
             p("Publicamos periodismo sobre tecnologia. Nada en el sitio constituye "
               "asesoramiento de inversion, juridico o profesional. Las decisiones tomadas a "
               "partir del contenido son responsabilidad del lector."),
             h2("Contenido asistido por IA"),
             p("Nuestras notas se producen con apoyo de inteligencia artificial bajo un "
               "proceso de verificacion en multiples fuentes. Aun asi pueden ocurrir errores: "
               "por eso mantenemos abierto el canal de correcciones."),
             h2("Enlaces externos"),
             p("Las notas enlazan a las fuentes usadas. No respondemos por el contenido, las "
               "politicas ni la disponibilidad de esos sitios."),
             h2("Disponibilidad"),
             p("El sitio se ofrece tal como esta, sin garantia de funcionamiento "
               "ininterrumpido."),
         ]},
    ]


def main() -> None:
    cfg = load()
    now = isoformat(utcnow())
    total = 0
    for lang in cfg.languages:
        folder = OUT / lang
        folder.mkdir(parents=True, exist_ok=True)
        for page in pages_for(lang, cfg):
            path = folder / f"{page['slug']}.json"
            existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
            payload = {**page, "lang": lang,
                       "updated_at": now if existing.get("body") != page["body"]
                       else existing.get("updated_at", now)}
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            total += 1
        print(f"  /{lang}/  {len(pages_for(lang, cfg))} paginas")
    print(f"{total} paginas institucionais em content/pages/")


if __name__ == "__main__":
    main()
