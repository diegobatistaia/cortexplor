# Cortexplor

Site de noticias sobre inteligencia artificial em tres idiomas (`/pt/`, `/en/`, `/es/`),
gerado como HTML estatico e publicado automaticamente na Hostinger.

Nao ha CMS, banco de dados nem painel. O site e um repositorio: o pipeline escreve
arquivos, o GitHub Actions sincroniza com o servidor.

## Como funciona

```
RSS/APIs  ->  checagem cruzada  ->  redacao por idioma  ->  gate  ->  HTML  ->  rsync
             (2+ fontes indep.)     (Skill de voz)         (7 criterios)
```

Uma pauta so vira materia se **dois donos de fonte diferentes** confirmarem os fatos
centrais. Veiculos do mesmo grupo contam como uma fonte so - republicacao nao e
confirmacao. O que nao passa no gate vai para `data/queue/` e espera revisao humana;
nada e publicado com ressalva.

## Estrutura

```
site.config.yaml          toda a configuracao especifica DESTE site
scripts/
  engine/                 o motor, generico - nada de nicho hardcoded
    config.py             carrega e valida o site.config.yaml
    collect.py            1. coleta RSS + filtro de palavras-chave + clusterizacao
    verify.py             2. checagem cruzada de fatos (regra das 2 fontes)
    draft.py              3-4. angulo por idioma + redacao com a Skill de voz
    seo.py                5. URLs, hreflang, JSON-LD, links internos
    images.py             6. imagem licenciada (Unsplash/Pexels) + atribuicao
    gate.py               7. o gate de qualidade
    build.py              8. gera todo o site estatico
    llm.py                unico ponto de chamada da API do Claude
    i18n.py               textos de interface (pt/en/es)
  pipeline/run.py         orquestrador: all | collect | build | queue | status
  tools/                  utilitarios de uma vez so (logo, fontes, paginas, demo)
templates/                HTML e CSS (Jinja2)
content/<lang>/*.json     as materias (fonte da verdade)
content/pages/<lang>/     paginas institucionais
data/                     indice de publicados, fila de excecao, log do gate
assets/                   logo, fontes, CSS e imagens
<lang>/                   HTML gerado - e isto que vai para o ar
```

## Comandos

```bash
python -m scripts.pipeline.run status     # fase do ramp, taxa do gate, fila
python -m scripts.pipeline.run collect    # so olhar o que tem de pauta hoje
python -m scripts.pipeline.run all        # o dia inteiro: coleta -> publicacao
python -m scripts.pipeline.run queue      # o que esta esperando revisao
python -m scripts.pipeline.run build      # so regerar o HTML
```

Para ver o site localmente:

```bash
python -m http.server 4173
```

E abrir <http://localhost:4173/pt/>.

## Ferramentas de uma vez so

```bash
python scripts/tools/build_logo.py        # regera os SVG/PNG/ICO do logo
python scripts/tools/extract_fonts.py     # regera as webfonts auto-hospedadas
python scripts/tools/make_pages.py        # regera as paginas institucionais
python scripts/tools/demo_content.py      # enche o site de posts falsos (layout)
python scripts/tools/demo_content.py --clean
```

## Replicar para outro nicho

O motor nao sabe que este site e de IA. Para lancar outro:

1. Copie o repositorio.
2. Troque o `site.config.yaml` (nicho, dominio, idiomas, fontes RSS, palavras-chave,
   categorias, cores, GA4, alvo de deploy).
3. Escreva uma nova Skill de voz em `.claude/skills/<nome>/SKILL.md` e aponte
   `voice.skill_path` para ela.
4. Troque o logo em `assets/logo/` e rode `build_logo.py` com o novo export.
5. Novos secrets no GitHub, novo dominio na hospedagem.

Nenhum arquivo em `scripts/engine/` deveria precisar de mudanca. Se precisar, aquilo
provavelmente era configuracao disfarcada de codigo.

## O que falta configurar

Ver [SETUP.md](SETUP.md).
