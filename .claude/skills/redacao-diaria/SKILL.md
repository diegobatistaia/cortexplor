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

O comando acima mostra o resumo e **falha se o briefing não for de hoje** (no
fuso do site) — sinal de que a coleta de hoje não rodou. Briefing de uma rodada
anterior **do mesmo dia** serve: se a coleta desta rodada falhou, escreva em cima
dele. O comando já tira as pautas que viraram matéria e recalcula o teto desta
rodada. (A coleta e esta sessão rodam três vezes por dia.) Se ele falhar, pare aqui:
escreva no resumo que o briefing está velho ou vazio e encerre sem commitar.
Escrever em cima de notícia de ontem é pior do que não publicar.

A única exceção é a rede de segurança da última rodada do dia (18h30): se
nenhuma das tentativas de coleta de hoje chegou e o dia ainda não tem nenhuma
matéria automática, o comando aceita o briefing das últimas 24 horas e avisa
isso na saída. O dono prefere isso a um dia sem matéria. Escreva só o que ainda
é notícia e date cada fato pelo que as fontes dizem ("na segunda-feira (5)").

Depois de passar, leia `data/briefing.json` inteiro. Cada pauta traz `sources[]`,
e cada fonte tem `owner` (o grupo dono do veículo) e `text` (a matéria inteira,
quando foi possível baixar).

## 1.1 Hierarquia das fontes

Cada fonte no briefing traz um campo `kind`:

- **`primary`** — quem fez a notícia. O anúncio da OpenAI no site da OpenAI, o
  resultado trimestral da Nvidia, o relatório de incidente da própria empresa,
  o modelo publicado no Hugging Face.
- **`press`** — quem noticiou. TechCrunch, The Verge, Guardian, Olhar Digital.

**Quando existe primária, ela é a fonte da matéria.** A imprensa vira
corroboração e contexto, não origem. Citar o TechCrunch pelo que a OpenAI
anunciou é citar o intermediário — e é o erro que este site não comete.

Na prática:

- A primária **entra sempre** em `sources`. O `check` reprova se ela existia no
  briefing e ficou de fora.
- No texto, atribua ao autor do fato: "segundo o comunicado da OpenAI",
  "de acordo com o relatório da empresa". A imprensa entra quando acrescenta
  algo que a primária não tem — reação de mercado, contexto, contraponto.
- Com duas fontes independentes, a matéria segue a regra das duas fontes
  (seção 2), e a primária conta como uma delas.
- **Anúncio oficial sozinho** (decisão do dono em 05/10/2026; vale enquanto
  o briefing trouxer `official_announcement_alone: true`): quando a pauta é o
  anúncio que a **própria empresa** publicou no canal oficial dela e ainda não
  há segundo dono, ela pode virar matéria com essa fonte só. Condições, todas
  obrigatórias:
  - o fato é o que a empresa anunciou **sobre ela mesma** (produto, modelo,
    preço, parceria, pesquisa, política). Afirmação sobre outra empresa, sobre
    pessoas ou sobre o mercado continua exigindo duas fontes;
  - a fonte tem `kind: primary` e texto (`text`) no briefing; título sozinho
    não basta;
  - o texto atribui à empresa tudo o que ela afirma: "segundo a Anthropic",
    "a OpenAI afirma". Desempenho, números e promessas vão sempre como fala da
    empresa, nunca como fato;
  - a matéria leva o campo `"fonte_unica": "anuncio_oficial"` (o `check` e o
    gate conferem que a fonte é um canal oficial, e o site mostra um aviso
    próprio no rodapé).
  Se a imprensa também cobriu, use as duas fontes e não marque `fonte_unica`.
- Cuidado com o dono: DeepMind, blog.google e research.google são todos
  Alphabet. Três feeds, uma fonte.

**Cuidado com o release.** Fonte primária é autoritativa sobre o que a empresa
disse, não sobre se aquilo é verdade. "A empresa afirma que o modelo é 40% mais
rápido" é fato; "o modelo é 40% mais rápido" é publicidade repetida. Número de
desempenho que vem só do fabricante vai sempre atribuído.

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

Descarte a pauta quando: menos de dois owners confirmam os fatos centrais (salvo
o anúncio oficial sozinho, nas condições da seção 1.1); as
fontes só repetem um comunicado; o assunto é lançamento comercial disfarçado de
notícia; ou você não entendeu o fato bem o suficiente para explicá-lo.

**O que interessa ao leitor deste site.** Ele acompanha IA por curiosidade e por
uso: quer saber que modelo saiu, o que ele faz de diferente, quanto custa, se dá
para usar hoje e como. Entre duas pautas igualmente bem apuradas, prefira a que
muda alguma coisa na vida de quem usa IA — um lançamento, uma mudança de preço,
uma ferramenta nova, um recurso liberado — em vez de mais uma de bastidor
corporativo. Movimento de mercado importa, mas não pode ser o site inteiro.

Publique no máximo `posts_per_language_today` pautas (está no briefing). Esse
número é o teto **desta rodada**, não do dia: o briefing também traz
`daily_cap_per_language` e `already_written_today`, e o código já dividiu o que
sobra do dia entre as rodadas que faltam. Se sobrarem boas, deixe para a
próxima rodada — elas continuam no feed.

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
- `sources` só com os owners que **confirmaram** os fatos, e sempre incluindo a
  primária quando o briefing tiver uma.
- `fonte_unica` só existe na matéria de anúncio oficial sozinho (seção 1.1), com o
  valor `"anuncio_oficial"`. Nas demais, não ponha o campo.
- `status` sempre `"draft"`. Quem promove para publicado é o gate.
- Corpo entre `word_count.min` e `word_count.max` palavras (está no briefing).

## 4.1 Matéria pedida pelo dono: extra

Quando o Diego pede uma matéria específica (algo que viu e quer no ar, ou um
teste), ela entra **por fora do teto**: ponha `"extra": true` no arquivo dos
três idiomas. O `used_today` não conta matéria extra, então as automáticas do
dia (4 por idioma, 5 a partir de 01/11) continuam inteiras.

- A checagem é a mesma: duas fontes independentes ou o anúncio oficial da
  seção 1.1. Pedido do dono não dispensa apuração; se não resistir, diga a ele
  por quê.
- Só quem pediu marca `extra`. A Routine nunca marca uma matéria própria como
  extra para escrever acima do teto.

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

## 7. Antes de encerrar, verifique o AdSense

```bash
python -m scripts.pipeline.run status
```

Se a saída trouxer a linha **"ADSENSE: O SITE JÁ TEM LASTRO PARA PEDIR A ANÁLISE"**,
mande uma notificação push avisando — o dono do site pediu para ser avisado nesse
momento exato, e ele não fica olhando o painel todo dia.

A mensagem deve dizer quantas matérias existem por idioma, há quantos dias o site
está no ar, e que o próximo passo é pedir a análise em adsense.google.com. Mande
uma vez só: se a linha aparecer de novo nos dias seguintes, ele já foi avisado.

Se a linha não aparecer, não mande nada. Um push por dia dizendo "ainda não" é
ruído.

## O que nunca fazer

- Publicar fato com uma fonte só, por melhor que seja a fonte.
- Copiar ou parafrasear de perto uma frase da matéria-fonte.
- Inventar aspas, números, datas ou contexto.
- Traduzir literalmente de um idioma para os outros.
- Editar arquivos em `pt/`, `en/`, `es/` (esses são gerados) ou mexer no gate
  para fazer uma matéria passar.
- Publicar acima do teto da rodada.

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
