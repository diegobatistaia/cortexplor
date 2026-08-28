# BRIEFING DO PROJETO — Cortexplor (Blog de Notícias de IA Automatizado)

> Este documento contém todo o contexto do projeto. Leia por completo antes de agir. Não é necessário pedir mais explicações sobre o objetivo geral — qualquer dúvida técnica pontual pode ser perguntada, mas o escopo e as decisões abaixo já estão definidas.

## 0. Identidade do projeto

- **Nome do site/marca:** Cortexplor
- **Domínio:** cortexplor.com
- **Tagline (reforça o nicho, já que o nome não diz "IA" sozinho):** "AI News & Trends" — versões localizadas: "Notícias e Tendências de IA" (PT), "Noticias y Tendencias de IA" (ES)
- **Uso da tagline:** deve aparecer fixa no header/logo do site, nas redes sociais e em qualquer material institucional
- **Reforço de nicho via SEO:** todo title tag e meta description deve mencionar explicitamente "Inteligência Artificial" / "AI" / "Inteligencia Artificial", já que o nome da marca por si só não comunica o nicho
- **Visão de longo prazo:** o nome foi escolhido pensando em futura expansão para além do blog (ex: Cortexplor Academy para cursos/escola de IA, Cortexplor como empresa/marca-mãe) — evitar decisões de identidade visual/copy que "prendam" a marca só ao formato blog

## 0.1 Identidade visual (logo) — TAREFA PARA O CLAUDE CODE EXECUTAR

O logo já foi finalizado em design (fora deste ambiente, via Claude Design). O que falta é puramente técnico/estrutural — o Claude Code deve executar isso automaticamente, sem pedir confirmação, como parte da configuração inicial do projeto:

**1. Criar a estrutura de pastas automaticamente:**
```
/assets/logo/
  ├── cortexplor-logo-color.svg
  ├── cortexplor-logo-black.svg
  ├── cortexplor-logo-white.svg
  ├── favicon.ico
  ├── icon-192.png
  └── icon-512.png
```

**2. Processar o arquivo de origem:** o logo foi exportado do Claude Design como **HTML standalone** (não como SVG/PNG puro). Esse arquivo HTML contém o código do logo embutido (provavelmente SVG inline dentro do HTML). O Claude Code deve:
   - **Localizar o arquivo primeiro:** o arquivo pode já estar em `/assets/logo/source/cortexplor-logo-export.html`, OU pode estar solto na raiz do projeto com outro nome (ex: `Cortexplor Mark - Standalone.html`). Se não encontrar no caminho esperado, procurar na raiz do projeto por qualquer arquivo `.html` com "cortexplor" ou "mark" no nome antes de perguntar ao usuário.
   - Mover/renomear esse arquivo para `/assets/logo/source/cortexplor-logo-export.html` (criando as pastas se não existirem)
   - Abrir o HTML e extrair o código SVG de cada uma das 3 variantes (cor, preto puro, branco puro)
   - Salvar cada variante como arquivo `.svg` independente na pasta `/assets/logo/`
   - Gerar as versões `.png` (192x192 e 512x512) e o `.ico` (favicon) a partir do SVG, usando ferramenta de conversão (ex: script com biblioteca de conversão SVG→PNG/ICO)
   - Confirmar que os arquivos finais estão legíveis/corretos antes de integrar ao template HTML do site

**3. Especificações da marca para referência:**
   - **Ícone:** símbolo "C+X" (letras C e X estilizadas, unidas por um único conector na parte inferior), estilo geométrico com nós/pontos nos vértices — conceito de "córtex/rede neural conectada"
   - **Wordmark:** "Cortexplor" — "Cort" em peso regular/médio, "explor" (e-x-p-l-o-r, todas as 6 letras) em peso bold, todas as letras do mesmo tamanho
   - **Paleta de cor principal (versão colorida):** gradiente de `#3A4556` (slate azulado escuro) a `#6B7A8F` (slate azulado claro) — tom neutro/profissional, aplicado no ícone e na porção bold ("explor") do wordmark; a porção "Cort" fica em tom neutro escuro (quase preto/slate escuro), fora do gradiente
   - **Versão preto puro:** todo o logo (ícone + wordmark) em preto sólido — uso em fundos claros
   - **Versão branco puro:** todo o logo (ícone + wordmark) em branco sólido — uso em fundos escuros/dark mode

**4. Uso no site:** o ícone "C+X" isolado deve ser usado como favicon e app icon; o wordmark completo ("Cortexplor") no header; a tagline ("AI News & Trends" / localizada) deve acompanhar o wordmark no header e em materiais institucionais.

## 0.2 Referências visuais de sites de notícia — análise já realizada

**Referências fornecidas pelo usuário:** CNN Brasil (cnnbrasil.com.br), G1 (g1.globo.com), Exame (exame.com).

**Padrões identificados nesses sites que devem ser aplicados ao Cortexplor:**
- Selo/etiqueta de categoria colorida acima de cada título de matéria (ex: "IA", "Mercado") — melhora escaneabilidade e reforça categorização/SEO
- Estrutura "hero + lista secundária": uma matéria em destaque com imagem grande, ao lado de 2-3 manchetes menores sem imagem
- Bloco "Mais lidas" (ranking numerado) — bom para engajamento e linkagem interna (SEO)
- Módulos por tópico/tema fixo (ex: bloco dedicado só a "Inteligência Artificial" agregando as últimas matérias daquele assunto) — aplicável diretamente ao Cortexplor com blocos como "Modelos & Lançamentos", "Mercado de IA", "IA no Brasil"
- Bloco de captura de newsletter embutido na home

**Padrões que NÃO devem ser replicados:**
- Densidade visual de "portal generalista" (dezenas de editorias/blocos simultâneos) — esses sites cobrem múltiplos assuntos com grande equipe editorial; o Cortexplor é um site de nicho único com volume de publicação bem menor, então replicar essa densidade deixaria o site parecendo "vazio" no início e não combina com a proposta enxuta/automatizada

**Direção de design definida:** meio-termo entre portal denso (CNN/Exame/G1) e blog editorial mais respirado (referência de estilo: TechCrunch, The Verge) — aproveitar os padrões de comportamento (selo de categoria, hero+lista, mais lidas, módulo por tópico) mas com mais espaço em branco, tipografia maior, menos blocos simultâneos disputando atenção.

**Status:** esta seção está CONCLUÍDA — o Claude Code já pode prosseguir com o design de layout/template usando as diretrizes acima, sem precisar aguardar novas referências (a menos que o usuário informe o contrário).

## 0.3 Posicionamento de anúncios (AdSense) — especificação para o template

Baseado em análise de sites de notícia de referência (CNN Brasil, Exame) — eles usam anúncios intercalados entre blocos de conteúdo e dentro do corpo dos artigos ("in-content ads"), além de banners de topo/rodapé. Para o Cortexplor, adaptar com **densidade reduzida**, já que o layout é mais enxuto/editorial (não um portal denso) e o volume de posts é menor — excesso de anúncios em site com pouco conteúdo é sinal negativo para aprovação/manutenção do AdSense.

**Slots de anúncio que o template HTML deve prever (como placeholders vazios, prontos para receber o código do AdSense após aprovação):**

1. **Banner de topo (leaderboard):** logo abaixo do header/menu, antes do conteúdo — em todas as páginas
2. **In-content (dentro do artigo):** 1 único slot inserido após o 2º-3º parágrafo do texto — não usar mais que isso por artigo no início
3. **Entre blocos da home:** 1 slot intercalado entre seções da home (ex: entre o bloco de destaques e o bloco "Mais lidas"), similar ao padrão observado ("Continua após a publicidade")
4. **Rodapé:** 1 banner antes do footer institucional

**Não incluir por enquanto:** sidebar de anúncios (a proposta de layout não usa sidebar fixa), múltiplos in-content ads por artigo, pop-ups/interstitials — tudo isso aumenta risco de penalização por "ad-heavy content" em site novo.

**Nota para o futuro:** os sites de referência também usam conteúdo patrocinado/nativo ("Branded Content", com "Apresentado por [marca]") como modelo de monetização adicional, separado do AdSense — não é prioridade na fase inicial do Cortexplor (que é 100% automatizado, sem venda direta de publicidade), mas pode valer revisitar isso futuramente, se o projeto evoluir para ter operação comercial própria.

## 1. O que é o projeto

Um site de notícias sobre **Inteligência Artificial** (novidades, tendências, métricas/números do setor, aplicações práticas em empresas), cobrindo fatos do **Brasil e do mundo**, publicado em **três idiomas — Português, Inglês e Espanhol** — como o mesmo site, em subpastas (`/pt/`, `/en/`, `/es/`), nunca como um seletor de idioma. Cada idioma tem SEO próprio (title, meta description, keywords, hreflang interligando as 3 versões da mesma notícia).

O objetivo final é operar com **automação total no dia a dia**: o dono do projeto reserva no máximo ~10 minutos por dia para supervisão (ler relatório, revisar itens que caíram em fila de exceção). Não há edição manual de matérias no fluxo normal.

Monetização inicial: **Google AdSense**. Sem foco em geração de leads para outros negócios nesta fase.

## 2. Stack técnica (decisões já tomadas)

- **Site estático em HTML puro** — sem WordPress, sem CMS, sem banco de dados.
- **Hospedagem:** Hostinger, plano com SSH habilitado (Premium/Business ou superior).
- **Deploy:** repositório Git → GitHub Actions dispara a cada `push` → conecta via SSH/rsync → sincroniza os arquivos estáticos com a pasta pública da Hostinger. 100% automático, roda na nuvem, sem depender de computador ligado.
- **Orquestração do pipeline:** Claude Code, via Routine agendada na nuvem (não é uma sessão interativa manual).
- **Analytics:** Google Analytics (GA4), script embutido no template HTML — cobre qualquer idioma automaticamente via URL/subpasta.
- **Indexação/SEO técnico:** Google Search Console, um sitemap.xml por idioma.
- **Banco de imagens:** Unsplash API e/ou Pexels API (licenciadas, com atribuição automática — nunca scraping de imagens).
- **Fontes de notícias:** RSS/APIs de fontes confiáveis internacionais (ex: Reuters, AP, TechCrunch, MIT Tech Review, VentureBeat, The Verge, Wired) e brasileiras (ex: Olhar Digital, Tecmundo, Folha/Tec) — lista final a ser validada/expandida durante o desenvolvimento.

## 3. Arquitetura — motor genérico + configuração por site

Este projeto deve ser construído desde o início como **motor reutilizável**, pensando em futura replicação para outros nichos (não apenas IA). Regra de design:

- **Código do motor (genérico, sem nada hardcoded de nicho):** scripts de coleta, checagem cruzada de fatos, geração de pauta, redação, SEO, gate de qualidade, geração de HTML, workflow de deploy.
- **Configuração específica do site** isolada em um único arquivo (ex: `site.config.yaml`): nicho, domínio, idiomas, fontes RSS, palavras-chave, referência à Skill de voz, ID do GA4, volume de publicação, cores de marca, etc.
- **Skill de voz do blog:** uma Skill própria para este site (voz/estilo de escrita), distinta de qualquer outra Skill do usuário (ex: não usar a Skill de marketing para restaurantes). Deve ser construída a partir de exemplos de texto que o usuário fornecer.
- Cada futuro site de outro nicho = novo repositório criado a partir do motor + novo `site.config.yaml` + nova Skill de voz + novo domínio/hospedagem. Isolamento total entre sites.

## 4. Pipeline de conteúdo (regras obrigatórias)

1. **Coleta:** puxar notícias recentes (24-48h) via RSS/API, filtradas por palavras-chave de IA, com deduplicação contra o que já foi publicado.
   - **Fonte adicional recomendada — Tavily (plugin de busca/extração web):** usado como reforço na coleta e principalmente na checagem cruzada de fatos (item 2 abaixo), por retornar dados de busca já estruturados para uso por IA. Requer configuração única e manual (conta no Tavily + API key conectada ao Claude Code como MCP server) — depois de configurado, entra 100% automático no fluxo da Routine, sem nenhuma ação manual recorrente do usuário.
2. **Checagem cruzada de fatos (regra rígida, não negociável):** um fato só pode ser usado no texto se aparecer confirmado em **2 ou mais fontes independentes**. Se não houver confirmação, a pauta é descartada — nunca publicar com base em uma fonte só ou em suposição/achismo.
3. **Geração de pauta localizada por idioma:** não é tradução literal — cada idioma (PT/EN/ES) recebe abordagem/ângulo relevante ao público daquele mercado, a partir do mesmo fato-base verificado.
4. **Redação:** usando a Skill de voz do blog (ver seção 3), sempre com base nos fatos verificados, nunca inventando ou "enfeitando" com informação não checada.
5. **SEO on-page automático, por idioma:** palavra-chave principal, meta description (150-160 caracteres), estrutura de headings (H1/H2/H3), slug curto, alt-text em imagens, schema markup `NewsArticle`, links internos para posts relacionados do próprio blog, tags hreflang conectando as 3 versões.
6. **Imagem:** buscar via Unsplash/Pexels API, licenciada, com atribuição.
7. **Gate de qualidade automático (sem revisão humana no fluxo padrão):** um post só é publicado se passar em TODOS os critérios abaixo; caso contrário, vai para uma fila de exceção que o usuário revisa nos seus ~10 min diários.
   - Mínimo de 2 fontes independentes confirmando os fatos centrais
   - Score de originalidade mínimo (não pode ser cópia/paráfrase próxima do texto-fonte)
   - Meta description, alt-text e schema markup presentes
   - Contagem de palavras dentro de um intervalo definido (ex: 600-1000 palavras — ajustável)
   - Fontes citadas no texto
8. **Publicação:** geração do HTML final (usando o template do motor) → commit → push → deploy automático via GitHub Actions.

## 5. Cronograma de volume de publicação (ramp progressivo)

Não começar em volume alto — sites novos publicando muito desde o dia 1 tendem a demorar mais para ganhar confiança do Google.

| Período | Posts/dia por idioma | Total/dia (3 idiomas) |
|---|---|---|
| Semanas 1-4 (lançamento/validação) | 1-2 | 3-6 |
| Mês 2 | 2-3 | 6-9 |
| Mês 3 | 3 | 9 |
| Mês 4-5 | 3-4 | 9-12 |
| Mês 6+ (se estável) | até 5 | até 15 |

Só aumentar o volume quando a taxa de aprovação no gate de qualidade estiver estável (ex: acima de 80% dos posts gerados passando sem cair na fila de exceção) por pelo menos 2 semanas seguidas.

## 6. Estrutura de repositório esperada

```
/pt/                  → posts em português
/en/                  → posts em inglês
/es/                  → posts em espanhol
/assets/              → CSS, imagens, ícones
/scripts/             → pipeline (coleta, checagem, geração, SEO, gate)
site.config.yaml      → configuração específica deste site
sitemap-pt.xml / sitemap-en.xml / sitemap-es.xml
rss-pt.xml / rss-en.xml / rss-es.xml
.github/workflows/    → GitHub Actions (deploy via SSH/rsync)
```

Páginas institucionais obrigatórias (requisito do AdSense): Sobre, Política de Privacidade, Contato, Termos de Uso — uma versão por idioma.

## 7. O que NÃO fazer

- Não publicar fato baseado em uma única fonte ou sem confirmação.
- Não copiar/reproduzir parágrafos de matérias-fonte — sempre reescrever com originalidade real.
- Não usar imagens sem licença/atribuição correta.
- Não misturar a Skill de voz de outros projetos do usuário (ex: marketing para restaurantes) neste blog.
- Não pular o gate de qualidade — nenhum post vai direto ao ar sem passar pelos critérios da seção 4.7.
- Não subir volume de publicação além do previsto no cronograma da seção 5 sem estabilidade comprovada.

## 8. Status atual / próximos passos imediatos

O projeto está na fase de **desenvolvimento do motor** (ainda sem domínio/hospedagem configurados pelo usuário). Itens pendentes do lado do usuário: domínio, hospedagem Hostinger com SSH, contas de API (NewsAPI/GNews, Unsplash/Pexels), conta GitHub, Google Search Console, Google Analytics (GA4), exemplos de texto para a Skill de voz.

Próximo passo técnico: começar a construir a estrutura do repositório, processar o logo (seção 0.1), o template HTML/CSS de layout (já pode seguir — referências visuais concluídas na seção 0.2, incluindo os slots de anúncio da seção 0.3), e os scripts do pipeline descritos na seção 4, de forma genérica conforme a seção 3 — para que este primeiro site sirva de referência replicável.
