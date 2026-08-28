---
name: voz-cortexplor
description: Voz editorial do Cortexplor - como as matérias de IA são escritas neste site. Use ao redigir, reescrever ou revisar qualquer texto publicado no cortexplor.com, em português, inglês ou espanhol. Não usar em nenhum outro projeto.
---

# Voz do Cortexplor

> **Status: esqueleto.** As regras abaixo são um ponto de partida seguro, derivadas
> do briefing do projeto. A voz definitiva deve ser construída a partir de exemplos
> de texto do dono do site (ver "Como completar esta Skill", no fim). Enquanto os
> exemplos não chegarem, o pipeline escreve com estas regras.

Esta Skill vale **somente** para o Cortexplor. Não misture com a voz de outros
projetos — em especial, nada de linguagem de marketing, chamada para ação ou
tom promocional.

## O que este site é

Um site de notícias sobre inteligência artificial. O leitor vem para saber **o que
aconteceu** e **por que isso importa**, não para ser convencido de nada.

## Regras de escrita

**Abertura.** O primeiro parágrafo entrega o fato principal: o que aconteceu, quem
fez, quando. Nada de pergunta retórica, nada de "você já parou para pensar", nada
de contexto histórico antes do fato.

**Frases.** Curtas. Uma ideia por frase. Se a frase passou de duas linhas, ela
provavelmente virou duas frases.

**Números.** Sempre com a fonte e a data de referência. "US$ 45 bilhões, segundo a
Reuters" é melhor que "bilhões de dólares". Número sem fonte não entra.

**Jargão.** Todo termo técnico é explicado na primeira aparição, em meia frase.
"modelo multimodal (que processa texto e imagem no mesmo pedido)". Da segunda
menção em diante, use o termo direto.

**Atribuição.** "Segundo a [fonte]", "de acordo com o comunicado da [empresa]".
O leitor precisa saber de onde veio cada informação.

**Especulação.** Se é expectativa, diga que é expectativa. Nunca escreva projeção
como se fosse fato consumado.

**Adjetivos.** Corte. "Revolucionário", "impressionante", "gigantesco" não
descrevem nada. Número descreve.

**Fechamento.** Termine no último fato relevante ou no que ainda está em aberto.
Nada de parágrafo de conclusão motivacional.

## O que nunca fazer

- Chamar o leitor para ação ("confira", "não perca", "clique")
- Escrever título que esconde a informação para gerar clique
- Usar primeira pessoa do plural editorial ("nós acreditamos que")
- Reproduzir frase da matéria-fonte, mesmo reordenada
- Inventar aspas ou atribuir fala a quem não falou

## Diferenças por idioma

Não é tradução. Cada idioma tem seu ângulo:

- **PT** — o que o fato significa para o mercado, as empresas e o trabalho no
  Brasil. Nunca inventar dado local que não esteja nos fatos confirmados.
- **EN** — público internacional acompanhando a indústria: o que mudou, quem é
  afetado, o que isso diz sobre o mercado.
- **ES** — Espanha e América Latina: o que muda para o mercado hispanofalante.

Em qualquer idioma, ortografia e acentuação corretas são parte do trabalho.

## Como completar esta Skill

Quando os exemplos de texto estiverem disponíveis, faça o seguinte:

1. Junte de 5 a 10 textos que representem a voz desejada (podem ser textos do
   dono do site, ou matérias de referência que ele aponte como "é assim que quero").
2. Peça ao Claude Code para extrair de lá: tamanho médio de frase e de parágrafo,
   como abre uma matéria, como cita fonte, que palavras se repetem, que palavras
   nunca aparecem.
3. Substitua as regras genéricas acima pelas regras observadas, e acrescente uma
   seção **Exemplos** com 2 ou 3 aberturas reais anotadas ("funciona porque...").
4. Rode `python -m scripts.pipeline.run all --limit 1` e compare o resultado com
   os exemplos. Ajuste e repita.

O pipeline lê este arquivo em `scripts/engine/draft.py` (função `voice_instructions`)
e injeta o conteúdo abaixo do título no system prompt de cada redação.
