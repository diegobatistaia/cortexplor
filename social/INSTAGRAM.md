# Carrosséis de Instagram — Cortexplor

Branch: `instagram` (isolada; `main` e a Routine não são afetadas — os workflows só disparam em `main`).

## Estilos aprovados (6 slides, 1080x1350)
1. **edicao** — editorial, mistura claro e escuro.
2. **terminal** — mono, mistura escuro e claro.
3. **dossie** — ficha de caso, mistura claro e escuro.
4. **duotone** — foto em tons de slate, como aprovado.

Protótipos: `scripts/social/carousel_lab.py` (helpers) e `carousel_lab2.py` (estilos).
`python scripts/social/carousel_lab2.py [estilo ...]` → `social/lab/v2/<estilo>/01..06.png`.

## Rodízio
`scripts/social/rotation.py::pick_styles(n, last=None)`: ordem aleatória, nunca o mesmo estilo
em sequência no dia (nem entre o último de ontem e o primeiro de hoje).

## Pendências
- Tornar os estilos orientados a dados (JSON da matéria → slides).
- Legenda e hashtags na voz do site (PT e EN, contas separadas).
- Publicação via Instagram Graph API (conta profissional + Página do Facebook + app Meta +
  token renovado a cada ~60 dias em secret do GitHub; imagens precisam de URL pública).
- Etapa de aprovação manual antes de publicar.

## Claro/escuro dinâmico
Cada carrossel usa um padrão de `PATTERNS` (carousel_lab2.py), irregular de propósito: sem alternância exata e
nunca 3 slides iguais seguidos. Na produção, sortear um padrão por matéria.

## Gerador (versão final)
- `social/specs/<slug>.json`: texto de cada carrossel (contrato entre a redação e o renderizador).
- `python scripts/social/carousel.py <slug>` ou `--all` → `social/out/<slug>/<estilo>/01..06.png` + `folha-<estilo>.png`.
- Duotone: fotos mantêm a cor original; o fundo sólido do slide 3 é cinza.
- Próximo: gerar o spec automaticamente a partir do JSON da matéria (Routine/Claude), legenda e hashtags, publicação.


## Atualização — 10 estilos e spec narrativo

- Estilos (ids em `scripts/social/rotation.py::STYLES`): edicao, terminal, dossie, duotone, jornal, poster, cobalto, meiatinta, cartao, vidro.
- Código: `carousel_core.py` (Ctx/UI/helpers), `styles_a.py` (4 originais), `styles_b.py` (6 novos), CLI `carousel.py`.
- Princípio de conteúdo: o carrossel é um resumo que faz sentido sozinho, com texto corrido. Slides: 1 capa; 2 "O que aconteceu"; 3 "Como funciona" (3 pontos); 4 "Por que importa" (+ número âncora); 5 "O que vem agora" (3 itens); 6 fontes + CTA.
- Spec: `social/specs/<slug>.json` (ver exemplos). Render: `python scripts/social/carousel.py --all [estilos]`.
- Pendente: spec automático a partir do artigo, UI EN/ES, legendas/hashtags, publicação via Graph API com aprovação manual.
