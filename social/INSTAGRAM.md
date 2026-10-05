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
