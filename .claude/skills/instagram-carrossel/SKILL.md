---
name: instagram-carrossel
description: Procedimento para transformar uma matéria publicada do Cortexplor no spec do carrossel de Instagram (6 slides) e na legenda. Use ao gerar carrossel, legenda, hashtags ou texto alternativo do Instagram do Cortexplor, só no branch instagram.
---

# Carrossel e legenda do Instagram

Vale **só no branch `instagram`**. Nada daqui vai para `main`.

Antes de escrever, leia:
- `.claude/skills/voz-cortexplor/SKILL.md` (a voz vale para slide, legenda e texto alternativo);
- `social/INSTAGRAM.md`, seções 2 (carrosséis) e 4 (legenda).

Entrada: uma matéria **publicada** em `content/<idioma>/<slug>.json` (com `status: published` e foto).
Saída: `social/specs/<slug>.json` aprovado pelo `check`, os slides renderizados e a legenda montada.

## 1. Preparar

```bash
python scripts/social/redacao.py prepare <slug> [--lang pt]
```

Cria o spec com o que sai direto da matéria: data, número do carrossel (`no`,
sequencial por conta), editoria curta, foto e crédito, fontes e a variante da
chamada final (A no `no` ímpar, B no par). **Não mexa nesses campos.** O resto
vem vazio para você escrever.

## 2. Ler a matéria inteira

Abra `content/<idioma>/<slug>.json` e leia todos os blocos. Os fatos confirmados
são o que está escrito ali, com a atribuição que está ali. Nada além disso:
nem do briefing, nem de memória, nem "o que todo mundo sabe".

## 3. Escrever os slides

O carrossel é um **resumo que se entende sozinho**: quem não abrir o site precisa
sair sabendo o que aconteceu, como funciona, por que importa e o que vem agora.
Texto corrido e explicado, não lista de números.

| Campo | O que vai |
|---|---|
| `kicker` | Rótulo curto "Tema · Empresa" (ex.: "Justiça · OpenAI"). Até 30 caracteres. |
| `headline` | Manchete da capa: o fato, sem clickbait. Pode partir do título da matéria. Até 70. |
| `headline_hl` | O nome do assunto, copiado exatamente da manchete (ex.: "Dots"). |
| `dek` | Uma frase com o ângulo e as fontes. Até 170. |
| `stamp` | Selo do dossiê: "Rótulo<br>dd/mm" (ex.: "Lançado<br>30/09"). |
| `s2` O que aconteceu | Título + 2 parágrafos: quem, o quê, quando, onde, com fonte. Até 300 cada. |
| `s3` Como funciona | Título + parágrafo curto (até 200) + 3 pontos `{h, t}`: o mecanismo, não só o resultado. |
| `s4` Por que importa | Título + 2 parágrafos + `stat` (número âncora até 14 caracteres e legenda até 50). |
| `s5` O que vem agora | Título + 3 itens `{h, t}`: `h` é data ou rótulo curto (até 10: "29/09", "Julho", "Sem data"). |

Regras:
- Fonte entre parênteses no fim de cada trecho com fato: "(CNBC, Wired)". Todo trecho com número **precisa** de fonte.
- Número só se estiver na matéria. Data dd/mm só se o dia estiver na matéria ou decorrer dela sem dúvida.
- Aplicação no dia a dia aparece impessoal: "Para quem desenvolve com IA…". Nunca "você".
- Jargão explicado na primeira vez, em meia frase.
- O PT tem o ângulo PT; o EN não é tradução (escreva a partir da matéria EN).

## 4. Escrever a legenda e o texto alternativo

`caption`:
- `hook`: a primeira linha, até 125 caracteres, com o fato e o nome do assunto (é gancho e palavra-chave de busca). Sem pergunta, sem "você".
- `body`: 2 ou 3 parágrafos curtos com **contexto que não coube nos slides**. Não repita frase do carrossel. Só fatos da matéria, com atribuição.
- `cta`: na variante B já vem pronta. Na variante A, escreva **uma pergunta objetiva** sobre o fato ou o uso, sem opinar e sem induzir resposta.
- `hashtags`: `#cortexplor` primeiro + até 3 do tema, minúsculas e sem acento (empresa, produto, tecnologia). Nada genérico (`#tecnologia`, `#ia`, `#ai`).

A legenda montada (hook + corpo + chamada + "Matéria completa no link da bio.") precisa ter **600 a 800 caracteres** sem as hashtags. O aviso do link entra sozinho; não escreva URL nem domínio.

`alt`: 6 textos, um por slide, cada um começando com "Slide N: " e com até 100 caracteres. Descreva o conteúdo do slide e repita o assunto.

## 5. Conferir até zerar

```bash
python scripts/social/redacao.py check <slug>
```

O `check` reprova: campo vazio, texto acima do orçamento, número que não está na
matéria, trecho com número sem fonte, fonte que não é da matéria, lista negra da
voz, "você" fora da chamada, exclamação, link, legenda fora da faixa, hashtags
erradas, texto alternativo longo e, no fim, **texto que não cabe nos slides** em
qualquer um dos 8 estilos (mede no navegador). Corrija e rode de novo até sair
`OK`. Avisos (`!`) pedem conferência, não bloqueiam.

O `check` também avisa sobre a foto (escura demais ou pequena). Foto muito escura tira
o estilo `meiatinta` da matéria automaticamente: o renderizador e o rodízio usam só os
estilos elegíveis (`rotation.eligible_styles`).

Não afrouxe o `check` para um spec passar. Se uma regra estiver errada, avise o dono.

## 6. Renderizar e montar a legenda

```bash
python scripts/social/carousel.py <slug> [estilo]
python scripts/social/redacao.py caption <slug>
```

Sem estilo informado, renderiza só os estilos elegíveis para a foto da matéria.
O comando único que faz tudo (check, foto e render) é `python scripts/social/check.py build <slug>`.

Se alguém mexer em `styles_a.py`, `styles_b.py`, `carousel_core.py` ou `carousel_lab.py`, rode
`python scripts/social/check.py golden`: ele compara com os estilos aprovados e reprova se algum mudou.

Saída: `social/out/<slug>/<estilo>/01..06.png`, a folha `folha-<estilo>.png`,
`legenda-<idioma>.txt` e `alt-<idioma>.txt`. Olhe a folha antes de entregar.

## Rotina diária (várias matérias de uma vez)

```bash
python scripts/social/diario.py novas            # matérias publicadas hoje no main → specs vazios
# escreva cada spec (passos 2 a 5 acima)
python scripts/social/diario.py fechar --aprovar <slug> ... # rodízio + check + render + legenda → fila (aprovado)
python scripts/social/diario.py fila
```

`novas` traz do `main` só a matéria e a foto de cada carrossel novo (insumo; nada vai
para o `main`). `fechar` escolhe o estilo pelo rodízio (menos usado entre os
elegíveis, nunca igual ao anterior), renderiza só esse estilo e põe o carrossel em
`social/fila.json` como `pendente`.

Aprovação: desde 05/10/2026 o dono dispensou o "pode" por carrossel (pode corrigir
depois, nos próximos). Use sempre `fechar --aprovar`: o que passa no `check` entra
aprovado; o que não passa fica fora da fila. `diario.py descartar <slug>` tira da fila
um carrossel que o dono vetar. Nada é publicado sem `aprovado`.

## Publicar (só o que está `aprovado`)

```bash
python scripts/social/publicar.py midia <slug> --repo /home/claude/cortexplor-midia
git -C /home/claude/cortexplor-midia add -A && git -C /home/claude/cortexplor-midia commit -m "<slug>" && git -C /home/claude/cortexplor-midia push
python scripts/social/publicar.py pedir <slug>   # depois: commit e push de social/publicar/pedido.json no branch instagram
```

O push do pedido dispara `.github/workflows/instagram.yml`, que publica com o secret
`INSTAGRAM_TOKEN` e grava `publicado` na fila e o resultado em `social/publicar/ultimo.json`.
Horários fixos: 8h, 11h e 16h (BRT), um carrossel por horário, com
`publicar.py proximo` (o aprovado mais antigo da fila) no lugar de `pedir <slug>`.
`pedir --teste` só confere a chave.
Antes de publicar, confirme que o dono não postou à mão.

## O que nunca fazer

- Inventar número, data, aspas ou contexto que não estão na matéria.
- Opinar, prever como fato, ou deduzir "o que isso significa para o Brasil" sem fonte.
- Publicar no Instagram o que não está `aprovado` na fila.
- Commitar no `main`.
