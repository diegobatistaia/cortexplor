---
name: redacao-diaria
description: Procedimento diário da redação do Cortexplor - checar as pautas do briefing contra a regra das duas fontes independentes e escrever as matérias nos três idiomas. Use quando rodar o pipeline diário do site, seja numa Routine agendada na nuvem ou numa sessão manual.
---

# Fechamento diário do Cortexplor

Você é a redação. Seu trabalho hoje: pegar as pautas coletadas, decidir **quais
resistem à checagem**, e escrever as que resistirem. Nada além disso.

O que decide se o site é bom não é o volume publicado — é o que você **descarta**.
Um dia sem matéria é um resultado aceitável. Uma matéria com fato não confirmado
não é.

## 1. Ler o briefing do dia

```bash
python -m scripts.pipeline.run briefing
```

**Não rode `brief`.** Esta sessão não tem saída para a web — só PyPI e as APIs da
Anthropic passam pelo proxy, e qualquer feed de notícia volta com 403. A coleta
já aconteceu no GitHub Actions meia hora antes, e o resultado veio junto no
clone, em `data/briefing.json`.

O comando acima mostra o resumo e **falha se o arquivo estiver com mais de 18
horas** — sinal de que a coleta de hoje não rodou. Se ele falhar, pare aqui:
escreva no resumo que o briefing está velho ou vazio e encerre sem commitar.
Escrever em cima de notícia de ontem é pior do que não publicar.

Depois de passar, leia `data/briefing.json` inteiro. Cada pauta traz `sources[]`,
e cada fonte tem `owner` (o grupo dono do veículo) e `text` (a matéria inteira,
quando foi possível baixar).

## 2. Checar — a parte que só você faz

Para cada pauta do briefing, leia o texto de todas as fontes e separe os **fatos
centrais**: aqueles sem os quais a matéria não existe. Normalmente são de três a
seis (o que aconteceu, quem, quando, quanto, o que muda).

Um fato só está confirmado se **dois `owner` diferentes afirmam ele no texto**.

As regras que fazem essa conta ser honesta:

- **Owner, não veículo.** Wired e Ars Technica são as duas da Condé Nast: contam
  como uma fonte. A lista de `owners` da pauta já vem no briefing.
- **Frase quase igual em duas fontes = mesmo release.** Isso é uma fonte só
  reproduzida duas vezes, não confirmação independente. Descarte a pauta ou
  registre a ressalva.
- **Número, data e nome próprio têm que bater.** Se as fontes divergem, ou você
  não usa o dado, ou diz no texto que as fontes divergem. Nunca escolha um valor
  e apresente como certo.
- **Não complete lacuna.** Se um dado seria útil e não está em nenhuma fonte, a
  matéria sai sem ele.
- **Fonte sem `text`** (não foi possível baixar) só vale pelo título. Título não
  confirma fato.

Descarte a pauta quando: menos de dois owners confirmam os fatos centrais; as
fontes só repetem um comunicado; o assunto é lançamento comercial disfarçado de
notícia; ou você não entendeu o fato bem o suficiente para explicá-lo.

Publique no máximo `posts_per_language_today` pautas (está no briefing). Se
sobrarem boas, deixe para amanhã — elas continuam no feed.

## 3. Escrever

Para **cada pauta aprovada**, escreva **uma matéria por idioma** listado em
`languages`: `pt`, `en`, `es`.

Não é tradução. É a mesma apuração com o ângulo que interessa a cada público:

- **pt** — o que o fato significa para o mercado, as empresas e o trabalho no
  Brasil. Nunca invente dado local que não esteja nos fatos confirmados.
- **en** — público internacional acompanhando a indústria: o que mudou, quem é
  afetado, o que isso diz sobre o mercado.
- **es** — Espanha e América Latina: o que muda para o mercado hispanofalante.

Isso vale também para a editoria: a mesma pauta pode ser "IA no Brasil" em
português e "Mercado de IA" em inglês, porque o recorte regional que interessa a
um público não interessa ao outro.

A voz do site está em `.claude/skills/voz-cortexplor/SKILL.md`. **Leia antes de
escrever a primeira matéria.** Em resumo: primeiro parágrafo entrega o fato,
frases curtas, número sempre com fonte, zero adjetivo de propaganda, nenhuma
aspa que não esteja nos fatos confirmados.

Cite as fontes no corpo ("segundo a TechCrunch", "de acordo com o MIT Technology
Review") — pelo menos uma, e isso é conferido automaticamente.

Escreva com a ortografia e a acentuação corretas do idioma. Um site de notícias
em português sem acento não passa.

## 4. Salvar

Um arquivo por matéria, em `content/<idioma>/<slug>.json`:

```json
{
  "lang": "pt",
  "slug": "openai-anuncia-modelo-de-baixo-custo",
  "story_id": "<copie o story_id da pauta no briefing>",
  "title": "Título de 55 a 70 caracteres, sem clickbait",
  "dek": "Uma frase de apoio, abaixo do título.",
  "meta_description": "Entre 150 e 160 caracteres, com a palavra-chave principal. Conte os caracteres.",
  "keyword": "palavra-chave principal",
  "category": "modelos",
  "tags": ["ia", "openai", "modelos"],
  "body": [
    {"type": "p",  "text": "Primeiro parágrafo, com o fato principal.", "items": []},
    {"type": "p",  "text": "Segundo parágrafo.", "items": []},
    {"type": "h2", "text": "Subtítulo", "items": []},
    {"type": "p",  "text": "Mais texto.", "items": []},
    {"type": "list", "text": "", "items": ["Item um", "Item dois"]}
  ],
  "image": {
    "query": "busca em inglês para o banco de imagens",
    "alt": "Descrição da imagem no idioma do texto, com pelo menos 15 caracteres"
  },
  "sources": [
    {"name": "TechCrunch", "owner": "techcrunch", "url": "https://...", "title": "Título original"},
    {"name": "MIT Technology Review", "owner": "mit-tr", "url": "https://...", "title": "Título original"}
  ],
  "status": "draft"
}
```

Regras do arquivo:

- `slug` em minúsculas, sem acento, 3 a 8 palavras, **diferente em cada idioma**.
- `story_id` **igual nos três idiomas** — é o que liga as versões pelo hreflang.
- `category` tem que ser válida **para aquele idioma**: o briefing traz
  `categories_by_language`, e as listas não são iguais. "IA no Brasil" só existe
  em `pt` — uma pauta brasileira escrita em inglês ou espanhol vai para outra
  editoria, normalmente `mercado` ou `politica`. Editoria regional não se
  traduz, se troca.
- Todo bloco tem exatamente três campos: `type`, `text`, `items`. Use `items`
  só em `list`, e `text` vazio nesse caso.
- `sources` só com os owners que **confirmaram** os fatos.
- `status` sempre `"draft"`. Quem promove para publicado é o gate.
- Corpo entre `word_count.min` e `word_count.max` palavras (está no briefing).

## 5. Conferir antes de commitar

```bash
python -m scripts.pipeline.run check
```

Ele aponta campo faltando, meta description fora da faixa, texto curto ou longo
demais, fonte não citada, categoria inexistente. **Corrija e rode de novo até
zerar.** Isso é de graça; o gate lá na frente não é.

## 6. Publicar

```bash
git add -A
git commit -m "content: <n> matérias de <data>"
git push
```

O push aciona o workflow **Finalizar** do GitHub Actions, que busca a imagem
licenciada, roda o gate de qualidade e publica no site. O que reprovar no gate vai para `data/queue/` em vez
de ir ao ar — e isso é o sistema funcionando, não um erro seu.

## O que nunca fazer

- Publicar fato com uma fonte só, por melhor que seja a fonte.
- Copiar ou parafrasear de perto uma frase da matéria-fonte.
- Inventar aspas, números, datas ou contexto.
- Traduzir literalmente de um idioma para os outros.
- Editar arquivos em `pt/`, `en/`, `es/` (esses são gerados) ou mexer no gate
  para fazer uma matéria passar.
- Publicar acima do teto do dia.

## Se não houver pauta

Se o briefing vier vazio, vier velho, ou nada resistir à checagem: escreva isso
no resumo e encerre sem commitar. É um resultado legítimo e vai acontecer.

## Onde cada etapa roda

| Etapa | Onde | Por quê |
|---|---|---|
| coleta dos feeds | GitHub Actions | é o único lugar com internet |
| checagem e redação | esta sessão | é o trabalho de julgamento |
| imagem, gate, build | GitHub Actions | precisa da chave do Unsplash e do gate determinístico |

Você é a etapa do meio. Não tente fazer as outras duas.
