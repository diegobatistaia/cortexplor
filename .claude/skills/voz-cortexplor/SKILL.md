---
name: voz-cortexplor
description: Voz editorial do Cortexplor - como as materias de IA sao escritas neste site. Use ao redigir, reescrever ou revisar qualquer texto publicado no cortexplor.com, em portugues, ingles ou espanhol. Nao usar em nenhum outro projeto.
---

# Voz do Cortexplor

> **Status: esqueleto.** As regras abaixo sao um ponto de partida seguro, derivadas
> do briefing do projeto. A voz definitiva deve ser construida a partir de exemplos
> de texto do dono do site (ver "Como completar esta Skill", no fim). Enquanto os
> exemplos nao chegarem, o pipeline escreve com estas regras.

Esta Skill vale **somente** para o Cortexplor. Nao misture com a voz de outros
projetos - em especial, nada de linguagem de marketing, chamada para acao ou
tom promocional.

## O que este site e

Um site de noticias sobre inteligencia artificial. O leitor vem para saber **o que
aconteceu** e **por que isso importa**, nao para ser convencido de nada.

## Regras de escrita

**Abertura.** O primeiro paragrafo entrega o fato principal: o que aconteceu, quem
fez, quando. Nada de pergunta retorica, nada de "voce ja parou para pensar", nada
de contexto historico antes do fato.

**Frases.** Curtas. Uma ideia por frase. Se a frase passou de duas linhas, ela
provavelmente virou duas frases.

**Numeros.** Sempre com a fonte e a data de referencia. "US$ 45 bilhoes, segundo a
Reuters" e melhor que "bilhoes de dolares". Numero sem fonte nao entra.

**Jargao.** Todo termo tecnico e explicado na primeira aparicao, em meia frase.
"modelo multimodal (que processa texto e imagem no mesmo pedido)". Da segunda
mencao em diante, use o termo direto.

**Atribuicao.** "Segundo a [fonte]", "de acordo com o comunicado da [empresa]".
O leitor precisa saber de onde veio cada informacao.

**Especulacao.** Se e expectativa, diga que e expectativa. Nunca escreva projecao
como se fosse fato consumado.

**Adjetivos.** Corte. "Revolucionario", "impressionante", "gigantesco" nao
descrevem nada. Numero descreve.

**Fechamento.** Termine no ultimo fato relevante ou no que ainda esta em aberto.
Nada de paragrafo de conclusao motivacional.

## O que nunca fazer

- Chamar o leitor para acao ("confira", "nao perca", "clique")
- Escrever titulo que esconde a informacao para gerar clique
- Usar primeira pessoa do plural editorial ("nos acreditamos que")
- Reproduzir frase da materia-fonte, mesmo reordenada
- Inventar aspas ou atribuir fala a quem nao falou

## Diferencas por idioma

Nao e traducao. Cada idioma tem seu angulo:

- **PT** - o que o fato significa para o mercado, as empresas e o trabalho no
  Brasil. Nunca inventar dado local que nao esteja nos fatos confirmados.
- **EN** - publico internacional acompanhando a industria: o que mudou, quem e
  afetado, o que isso diz sobre o mercado.
- **ES** - Espanha e America Latina: o que muda para o mercado hispanofalante.

## Como completar esta Skill

Quando os exemplos de texto estiverem disponiveis, faca o seguinte:

1. Junte de 5 a 10 textos que representem a voz desejada (podem ser textos do
   dono do site, ou materias de referencia que ele aponte como "e assim que quero").
2. Peca ao Claude Code para extrair de la: tamanho medio de frase e de paragrafo,
   como abre uma materia, como cita fonte, que palavras se repetem, que palavras
   nunca aparecem.
3. Substitua as regras genericas acima pelas regras observadas, e acrescente uma
   secao **Exemplos** com 2 ou 3 aberturas reais anotadas ("funciona porque...").
4. Rode `python -m scripts.pipeline.run all --limit 1` e compare o resultado com
   os exemplos. Ajuste e repita.

O pipeline le este arquivo em `scripts/engine/draft.py` (funcao `voice_instructions`)
e injeta o conteudo abaixo do titulo no system prompt de cada redacao.
