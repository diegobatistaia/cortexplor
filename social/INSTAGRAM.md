# Instagram do Cortexplor — plano e padrões

Branch: `instagram` (isolada; `main` e a Routine do site não são afetadas — os workflows só disparam em `main`).
Objetivo: um carrossel por matéria publicada, em contas separadas (PT e EN), para criar uma comunidade em torno do site.
Fluxo final: matéria publicada → spec do carrossel → render dos slides → legenda → aprovação manual → publicação.

---

## 1. Estado atual

| Parte | Estado |
|---|---|
| 8 estilos visuais de carrossel | Prontos e aprovados |
| Rodízio de estilos | Pronto (`scripts/social/rotation.py`) |
| Gerador de slides a partir de spec JSON | Pronto (`scripts/social/carousel.py`) |
| Padrão de legenda e hashtags | Definido neste documento (seção 4) |
| Controle de qualidade (validação, layout, fotos, referências) | Pronto (`scripts/social/check.py`, seção 7) |
| Geração do spec e da legenda a partir da matéria | Pronta: skill `instagram-carrossel` + `scripts/social/redacao.py` (prepare, check, caption) |
| Checagem de encaixe do texto nos 8 estilos | Pronta (`scripts/social/fit.py`, roda dentro do `check`) |
| Textos fixos dos slides em EN | A fazer (hoje só PT, em `carousel_core.py::UI`) |
| Rotina diária (matérias do dia → fila) | Pronta: `scripts/social/diario.py` (novas, fechar, fila) |
| Aprovação manual | Pronta: fila em `social/fila.json`, `diario.py aprovar/descartar`; o dono aprova pelo chat |
| Publicação pela Instagram Graph API | A fazer (depende de contas e app Meta) |
| Página de links da bio | Fica para depois, decisão do dono |

---

## 2. Carrosséis

### 2.1 Formato
- 6 slides, 1080x1350 PNG, gerados por HTML/CSS com Playwright (Chromium).
- Cada carrossel é um **resumo da matéria que faz sentido sozinho**: texto corrido e explicado, não só dados e números. Quem não abrir o site precisa entender o que aconteceu, como funciona, por que importa e o que vem agora.
- Roteiro fixo dos slides:
  1. **Capa** — manchete, subtítulo e foto.
  2. **O que aconteceu** — 2 parágrafos.
  3. **Como funciona** — parágrafo curto e 3 pontos.
  4. **Por que importa** — número âncora (com legenda) e 2 parágrafos.
  5. **O que vem agora** — 3 itens com marcador (data ou rótulo).
  6. **Fontes** — nomes das fontes e chamada para a matéria completa no site.
- Atribuição de fonte entre parênteses no texto. Nenhum dado inventado; só o que está nos fatos confirmados da matéria.
- Aplicação no dia a dia aparece de forma impessoal ("Para quem desenvolve com IA…"), sem "você", conforme a skill `voz-cortexplor`.
- Crédito da foto fica no slide, como na matéria.

### 2.2 Os 8 estilos aprovados
IDs usados no código (`rotation.py::STYLES`):

| # | id | Descrição |
|---|---|---|
| 1 | `edicao` | Editorial, mistura claro e escuro |
| 2 | `terminal` | Fonte mono, estética de terminal |
| 3 | `dossie` | Ficha de caso com selos; fundo externo bege |
| 4 | `duotone` | Foto em tela cheia com a cor original; fundo sólido do slide 3 em cinza |
| 5 | `jornal` | Revista, serifa com capitular e linha do tempo |
| 6 | `cobalto` | Azul-marinho e creme, laranja queimado discreto, cartões arredondados |
| 7 | `meiatinta` | Capa e faixas em halftone, preto, creme e laranja |
| 8 | `cartao` | Estilo de post, grafite e areia |

Reprovados e removidos: `poster` (amarelo, depois preto/grafite) e `vidro` (efeito glass).
Regra do dono: **fotos mantêm a cor original**; sem "O" gigante nem aspas decorativas grandes.

### 2.3 Claro/escuro dinâmico
Cada carrossel usa um padrão de `PATTERNS` (`carousel_core.py`), irregular de propósito: nunca alternância exata e nunca 3 slides iguais seguidos. O padrão é sorteado por matéria (`random.Random(f"{slug}-{seed}")`).

### 2.4 Rodízio dos estilos
`scripts/social/rotation.py::pick_styles(n, styles, last, rng)`:
- ordem aleatória por "sacola" embaralhada, equilibrando o uso dos estilos;
- **nunca o mesmo estilo em sequência**, nem entre o último do dia anterior e o primeiro do dia seguinte (`last`);
- autoteste: `python scripts/social/rotation.py`.

### 2.5 Spec da matéria
`social/specs/<slug>.json` é o contrato entre a redação (Routine/Claude) e o renderizador.

```json
{
  "slug": "…", "lang": "pt", "date": "02 out 2026", "no": 3,
  "category": "…", "kicker": "…·…", "headline": "…", "headline_hl": "trecho destacado",
  "dek": "…", "image": {"path": "assets/img/….jpg", "credit": "…", "pos": "50% 50%"},
  "stamp": "…", "sources": ["…"],
  "s2": {"label": "O que aconteceu", "title": "…", "body": ["§1", "§2"]},
  "s3": {"label": "Como funciona", "title": "…", "body": "…", "points": [{"h": "…", "t": "…"}]},
  "s4": {"label": "Por que importa", "title": "…", "body": ["§1", "§2"], "stat": {"big": "…", "cap": "…"}},
  "s5": {"label": "O que vem agora", "title": "…", "items": [{"h": "…", "t": "…"}]}
}
```

Orçamentos de texto (para não estourar o slide): `s3.points` e `s5.items` ≈ 20 palavras cada; `s2.body` e `s4.body` com 2 parágrafos; `stat.big` curto (cabe em ~10 caracteres na fonte grande).
Exemplos reais: `social/specs/google-lanca-gemini-4-argon-ciberseguranca.json` e `social/specs/openai-lanca-dots-agentes-permanentes-chatgpt.json`.

### 2.6 Como gerar
```
python scripts/social/redacao.py prepare <slug>   # cria o spec a partir da matéria
# (a redação escreve os campos; ver skill instagram-carrossel)
python scripts/social/redacao.py check <slug>     # valida e mede o encaixe
python scripts/social/redacao.py caption <slug>   # legenda-<idioma>.txt e alt-<idioma>.txt
python scripts/social/carousel.py <slug> [estilo ...]
python scripts/social/carousel.py --all [estilo ...]
```
Saída: `social/out/<slug>/<estilo>/01..06.png` e a folha de contato `folha-<estilo>.png`.
Código: `carousel_core.py` (Ctx, textos fixos, helpers), `styles_a.py` (edicao, terminal, dossie, duotone), `styles_b.py` (jornal, cobalto, meiatinta, cartao), `carousel_lab.py` (fontes, halftone, render).

---

## 3. Boas práticas do Instagram (pesquisa de 05/10/2026)

Fontes: resumo do Q&A do Mosseri ([Kontentino](https://www.kontentino.com/q-and-a/instagram-search-seo/)), [Digital Trends](https://www.digitaltrends.com/social-media/instagram-now-limits-you-to-five-hashtags-per-post/), [TechBuzz](https://www.techbuzz.ai/articles/instagram-caps-hashtags-at-five-to-combat-spam), [Digital Diplomacy](https://wearedigitaldiplomacy.substack.com/p/hashtags-still-relevant-adam-mosseri), [Dataslayer](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers), [Hootsuite](https://blog.hootsuite.com/instagram-algorithm/), [ALM Corp](https://almcorp.com/blog/instagram-restricts-reach-content-aggregators/), [Replug](https://replug.io/blog/instagram-character-limits), [Paperbell](https://paperbell.com/blog/how-to-add-a-link-to-instagram-posts/).
Nenhum post original do Instagram foi aberto; vários pontos vêm de blogs de marketing. Marcado abaixo o grau de certeza.

- **Palavras-chave** (bem apoiado): a busca lê legenda, texto alternativo, texto dentro da imagem e nome/bio da conta. Posts públicos de contas profissionais aparecem no Google desde julho de 2025.
- **Hashtags** (bem apoiado): o Mosseri diz que hashtag não aumenta alcance; ajuda a classificar o tema. Teto de **5 por post** noticiado para dezembro de 2025 (Digital Trends e TechBuzz; texto original não verificado). Usar 4 fica seguro nos dois cenários.
- **Sinais de distribuição** (fonte secundária): tempo de visualização, envios por DM (pesam mais que curtidas para chegar a não seguidores), curtidas por alcance, conversa de duas vias e originalidade. Salvamento é sinal de intenção.
- **Originalidade** (fonte secundária, regra de 30/04/2026): contas que só repostam conteúdo alheio perdem recomendação. Resumo e análise do próprio conteúdo contam como original; marca d'água ou crédito sozinhos não contam.
- **Links**: legenda de post não tem link clicável. Link na bio é o caminho; link sticker em Stories está liberado para todas as contas. Por isso **nenhum link na legenda**.
- **Limites técnicos**: legenda até 2.200 caracteres, mas só os **primeiros 125** aparecem antes do "mais"; texto alternativo ≈ 100 caracteres; bio 150 caracteres.

---

## 4. Padrão de legenda (decidido em 05/10/2026)

### 4.1 Estrutura
Tamanho do corpo: **600 a 800 caracteres**, sem contar as hashtags.

1. **Primeira linha (até 125 caracteres):** o fato principal com o nome do assunto. Serve de gancho e de palavra-chave. Exemplo: "A OpenAI lançou os Dots, agentes de IA que trabalham o tempo todo dentro do ChatGPT."
2. **Corpo (2 a 3 parágrafos curtos):** o que aconteceu e por que importa, com os termos naturais do tema (nome da empresa, produto, tecnologia). Não repete o carrossel palavra por palavra; acrescenta o contexto que não coube nos slides. Só fatos da matéria, com atribuição.
3. **Chamada final**, alternando entre duas variantes (seção 4.2).
4. **Aviso do link:** "Matéria completa no link da bio." Sem URL e sem o domínio.
5. **Hashtags (linha separada, no final), máximo 4:** 1 da marca (`#cortexplor`) e 3 do tema. Nada de hashtags genéricas ou gigantes (`#tecnologia`, `#love`).

### 4.2 Chamada final: teste A/B
Alternar entre duas variantes e registrar qual foi usada, para comparar depois (envios, salvamentos, comentários, alcance).

- **Variante A — pergunta**, para estimular comentários. Uma pergunta objetiva sobre o fato ou o uso, sem opinar.
- **Variante B — salvar e enviar.** "Salve para consultar depois e envie a quem acompanha IA." Em EN: "Save it for later and send it to someone following AI."

Regra: alternar de forma determinística por ordem de publicação (A, B, A, B…) por conta. Campo `caption.cta_variant` no spec guarda "A" ou "B".

### 4.3 Texto alternativo
Um por slide, ≈ 100 caracteres, descrevendo o conteúdo e repetindo o assunto. Ex.: "Slide 2: A OpenAI lança agentes Dots, sempre ativos, no ChatGPT". Campo `alt` (lista de 6) no spec. Depende de a API de publicação aceitar texto alternativo; verificar na etapa de publicação.

### 4.4 Voz
A legenda segue a skill `voz-cortexplor`: fato na primeira frase, frases curtas, número com fonte, jargão explicado na primeira vez, atribuição, lista negra respeitada (nada de "revolucionário", "ecossistema", "game changer", "impressionante" etc.), sem opinião, sem previsão como fato.
**Única exceção, autorizada pelo dono:** a chamada final (4.2) e o aviso do link. Fora disso, sem "você", sem clickbait, sem curiosidade plantada. A chamada deve soar impessoal quando possível ("Salve para consultar depois").
Sem excesso de emojis (no máximo 1, opcional).

### 4.5 Idiomas
- Conta PT: legenda, hashtags e texto alternativo em português, ângulo PT (mercado, empresas e trabalho no Brasil, dentro do limite da skill).
- Conta EN: tudo em inglês, ângulo internacional. Não é tradução literal; escrito a partir da matéria EN. Link: "Full story: link in bio."
- Hashtags de marca: `#cortexplor` nas duas.

### 4.6 Campos no spec
```json
"caption": {
  "hook": "primeira linha, até 125 caracteres",
  "body": ["parágrafo 1", "parágrafo 2", "parágrafo 3"],
  "cta_variant": "A",
  "cta": "texto da chamada final",
  "hashtags": ["#cortexplor", "#inteligenciaartificial", "#chatgpt", "#openai"]
},
"alt": ["slide 1…", "slide 2…", "slide 3…", "slide 4…", "slide 5…", "slide 6…"]
```
Montagem final: `hook` + `body` + `cta` + "Matéria completa no link da bio." + linha em branco + hashtags.
Validações automáticas (`python scripts/social/redacao.py check <slug>`): hook ≤ 125 caracteres; legenda montada sem as hashtags entre 600 e 800; 2 a 4 hashtags, `#cortexplor` primeiro, minúsculas, sem genéricas; nenhum link ou domínio; alt com 6 itens começando por "Slide N: ", ≤ 100 caracteres cada; variante da chamada coerente com o `no` (A ímpar, B par; B com texto fixo, A uma pergunta só).
Também confere: orçamentos dos slides, fontes iguais às da matéria, todo número presente na matéria, trecho com número sempre com fonte, lista negra e "você" fora da chamada, nada de exclamação, legenda sem repetir frase do carrossel e, por fim, se o texto cabe nos slides dos 8 estilos (medido no Chromium: texto fora da tela, sobreposto, cortado ou invadindo o rodapé).

---

## 5. Link na bio
Fica para depois. A ideia do dono: uma página de links do próprio site, **sem listar as matérias**, para depois poder incluir grupos de WhatsApp e Telegram e formar a comunidade. Nada disso muda a legenda: o aviso é sempre "link na bio".

---

## 7. Controle de qualidade (para o dono não precisar monitorar)

Os slides são desenhados por código fixo: o visual não muda de um dia para o outro. O que pode variar é o texto e a foto da matéria. Duas ferramentas, e `social/CLAUDE.md` com as regras para qualquer Claude que trabalhe aqui.

- **`scripts/social/redacao.py check <slug>`** (spec, legenda e encaixe): limites de texto, fontes iguais às da matéria, todo número presente na matéria, lista negra, legenda sem link e com hashtags corretas, e medição no navegador de estouro, sobreposição e texto cortado em todos os estilos (`fit.py`).
- **`scripts/social/check.py`** (foto e referências):
  - `photo <slug>`: foto muito escura (luminância < 45) tira o estilo `meiatinta` da matéria; foto menor que 800x500 gera aviso.
  - `build <slug>`: roda `redacao.py check`, a análise da foto e renderiza só os estilos elegíveis.
  - `golden`: renderiza uma matéria de referência congelada (`social/golden/spec-referencia.json`) em todos os estilos e compara com as imagens aprovadas em `social/golden/`; reprova se algum estilo mudou. `golden --update` só com aprovação do dono.

| Risco | Proteção |
|---|---|
| Texto grande demais | `redacao.py check`: limites + medição de encaixe em todos os estilos |
| Foto ruim | `check.py photo` (escura, pequena) |
| Texto fora do padrão | `redacao.py check` (fatos, números, voz, legenda) |
| Alguém mexer no código dos estilos | `check.py golden` |
| Publicar algo errado | Aprovação manual por carrossel antes de qualquer publicação |

Fluxo por matéria: `check.py build <slug>` (precisa terminar sem erro) → carrossel fica "pendente de aprovação" → dono aprova → publica.
Teste de 05/10/2026: os 8 estilos passam na comparação com as referências; uma troca de cor em um estilo foi detectada (diferença 8,8 contra 0,2 normal).

---

## 8. Perfis (criados em 05/10/2026)

Imagens do perfil: `social/perfil/perfil-escuro.png`, `perfil-claro.png`, `perfil-cor.png` (1080x1080, ícone C+X com margem para o corte circular).

| | Português | Inglês |
|---|---|---|
| Nome (busca, até 30 caracteres) | Cortexplor \| Notícias de IA | Cortexplor \| AI News |
| Categoria | Site de notícias | News & Media Website |
| Bio (até 150 caracteres) | Notícias de inteligência artificial em linguagem clara.<br>Cada matéria com no mínimo 2 fontes independentes.<br>Site no link ↓ (121) | AI news in plain language.<br>Every story backed by at least 2 independent sources.<br>Site in the link ↓ (99) |
| Alternativa | O que aconteceu em IA e por que importa.<br>Cada matéria com pelo menos 2 fontes independentes.<br>Site no link ↓ (107) | What happened in AI and why it matters.<br>Every story backed by at least 2 independent sources.<br>Site in the link ↓ (112) |

Usuário sugerido: `@cortexplor` (PT) e `@cortexplor.en` (EN); disponibilidade não verificada. Link da bio: o próprio site, por enquanto. As contas devem ser **profissionais** (necessário para a publicação pela API e para o Google indexar os posts).

---

## 6. O que falta (em ordem)

1. ~~Geração do spec e da legenda~~ (feito em 05/10/2026: skill `instagram-carrossel`, `redacao.py`, `fit.py`).
2. **Textos fixos em EN** (rótulos dos slides, "Sources", chamada do slide 6) em `carousel_core.py::UI`.
3. ~~Integração diária~~ (feito em 05/10/2026: `diario.py`).
   Antes: para cada matéria do dia, escolher o estilo pelo rodízio (lembrando o último usado), renderizar e salvar slides + legenda por conta.
4. ~~Aprovação manual~~ (feito em 05/10/2026: fila + aprovação pelo chat). Antes: (página de prévia ou arquivos enviados ao dono).
5. **Publicação pela Instagram Graph API**, que exige (parte do dono):
   - contas profissionais de Instagram (PT e EN);
   - uma Página do Facebook ligada a cada conta;
   - um app na Meta e token de acesso (≈ 60 dias, renovado e guardado em secret do GitHub);
   - imagens em URL pública para a API buscar.
6. **Medição do teste A/B** das chamadas finais, depois de algumas semanas de posts.
7. Página de links da bio (decisão do dono, depois).
