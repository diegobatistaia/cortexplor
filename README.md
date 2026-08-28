# Cortexplor

Site de notícias sobre inteligência artificial em três idiomas (`/pt/`, `/en/`, `/es/`),
gerado como HTML estático e publicado automaticamente na Hostinger.

Não há CMS, banco de dados nem painel. O site é um repositório: o pipeline escreve
arquivos, o GitHub Actions sincroniza com o servidor.

## Como funciona

```
RSS/APIs  ->  checagem cruzada  ->  redação por idioma  ->  gate  ->  HTML  ->  rsync
             (2+ fontes indep.)     (Skill de voz)         (7 critérios)
```

Uma pauta só vira matéria se **dois donos de fonte diferentes** confirmarem os fatos
centrais. Veículos do mesmo grupo contam como uma fonte só — republicação não é
confirmação. O que não passa no gate vai para `data/queue/` e espera revisão humana;
nada é publicado com ressalva.

## Estrutura

```
site.config.yaml          toda a configuração específica DESTE site
scripts/
  engine/                 o motor, genérico — nada de nicho hardcoded
    config.py             carrega e valida o site.config.yaml
    collect.py            1. coleta RSS + filtro de palavras-chave + clusterização
    verify.py             2. checagem cruzada de fatos (regra das 2 fontes)
    draft.py              3-4. ângulo por idioma + redação com a Skill de voz
    seo.py                5. URLs, hreflang, JSON-LD, links internos
    images.py             6. imagem licenciada (Unsplash/Pexels) + atribuição
    gate.py               7. o gate de qualidade
    build.py              8. gera todo o site estático
    llm.py                único ponto de chamada da API do Claude
    i18n.py               textos de interface (pt/en/es)
  pipeline/run.py         orquestrador: all | collect | build | queue | status
  tools/                  utilitários de uma vez só (logo, fontes, páginas, demo)
templates/                HTML e CSS (Jinja2)
content/<lang>/*.json     as matérias (fonte da verdade)
content/pages/<lang>/     páginas institucionais
data/                     índice de publicados, fila de exceção, log do gate
assets/                   logo, fontes, CSS e imagens
<lang>/                   HTML gerado — é isto que vai para o ar
```

## Comandos

```bash
python -m scripts.pipeline.run status     # fase do ramp, taxa do gate, fila
python -m scripts.pipeline.run collect    # só olhar o que tem de pauta hoje
python -m scripts.pipeline.run all        # o dia inteiro: coleta -> publicação
python -m scripts.pipeline.run queue      # o que está esperando revisão
python -m scripts.pipeline.run build      # só regerar o HTML
```

Para ver o site localmente:

```bash
python -m http.server 4173
```

E abrir <http://localhost:4173/pt/>.

## Ferramentas de uma vez só

```bash
python scripts/tools/selfcheck.py         # 40 verificações, sem gastar API
python scripts/tools/build_logo.py        # regera os SVG/PNG/ICO do logo
python scripts/tools/extract_fonts.py     # regera as webfonts auto-hospedadas
python scripts/tools/make_pages.py        # regera as páginas institucionais
python scripts/tools/demo_content.py      # enche o site de posts falsos (layout)
python scripts/tools/demo_content.py --clean
```

## Replicar para outro nicho

O motor não sabe que este site é de IA. Para lançar outro:

1. Copie o repositório.
2. Troque o `site.config.yaml` (nicho, domínio, idiomas, fontes RSS, palavras-chave,
   categorias, cores, GA4, alvo de deploy).
3. Escreva uma nova Skill de voz em `.claude/skills/<nome>/SKILL.md` e aponte
   `voice.skill_path` para ela.
4. Troque o logo em `assets/logo/` e rode `build_logo.py` com o novo export.
5. Novos secrets no GitHub, novo domínio na hospedagem.

Nenhum arquivo em `scripts/engine/` deveria precisar de mudança. Se precisar, aquilo
provavelmente era configuração disfarçada de código.

## O que falta configurar

Ver [SETUP.md](SETUP.md).
