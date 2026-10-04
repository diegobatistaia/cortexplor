# O que falta para o site entrar no ar

Ordem sugerida. Os itens 1 a 4 são o caminho crítico: com eles o site publica
sozinho. O resto pode vir depois.

Versão detalhada, clique a clique, com progresso salvo:
**[guia de publicação](https://claude.ai/code/artifact/711eccd1-ec45-45cc-8bf0-05e850f489f5)**.

Já resolvido: o domínio `cortexplor.com` resolve para a Hostinger e o HTTPS está
ativo — hoje serve a "Página padrão" do painel, que o primeiro deploy substitui.

---

## 1. Repositório no GitHub

Esta máquina não tem o `gh` instalado, então crie pela interface:
<https://github.com/new>, nome `cortexplor`, **Private**, e sem marcar nada em
"Initialize this repository" (um README criado pelo GitHub faz o push do passo 3
ser recusado).

Depois, conecte a pasta ao repositório:

```bash
git remote add origin https://github.com/SEU_USUARIO/cortexplor.git
```

```bash
git push -u origin main
```

O Git Credential Manager abre uma janela do navegador para autorizar na primeira
vez. Crie o secret do item 2 **antes** do push, senão o primeiro deploy falha.

## 2. Secrets no GitHub

Em **Settings > Secrets and variables > Actions > New repository secret**:

| Secret | O que é | Onde conseguir |
|---|---|---|
| `HOSTINGER_SSH_KEY` | a **chave privada** de deploy | gerada para este projeto: `~/.ssh/cortexplor_deploy` |
| `UNSPLASH_ACCESS_KEY` | banco de imagens | unsplash.com/developers |
| `PEXELS_API_KEY` | banco de imagens (reserva) | pexels.com/api |

A chave privada você mesmo sobe — eu não movo credencial. No Git Bash, copie o
conteúdo dela para a área de transferência:

```bash
cat ~/.ssh/cortexplor_deploy | clip
```

e cole no campo Secret, da linha `BEGIN` até a linha `END`.

> O par `~/.ssh/cortexplor_deploy` foi gerado só para este projeto. A chave pública
> precisa ser cadastrada uma vez no painel da Hostinger (**Avançado > Acesso SSH >
> Chaves SSH > Adicionar chave SSH**, nome sugerido `Deploy Cortexplor`).
>
> A conta de hospedagem (`u433721675` em `147.79.91.241:65002`) é a mesma que abriga
> os outros domínios — isso é do plano, não do projeto. O que fica isolado é a chave:
> revogar a do Cortexplor não derruba o deploy de nenhum outro site.

## 3. Primeiro deploy

Assim que o primeiro push chegar no `main`, o workflow **Deploy** roda sozinho e
sincroniza tudo com `public_html`. Para disparar na mão: aba **Actions > Deploy >
Run workflow**.

O `default.php` da Hostinger some sozinho: o rsync roda com `--delete` e remove do
servidor o que não pertence ao site.

## 4. Ligar a publicação automática (modo Routine, sem custo de API)

1. Instale o app do Claude no GitHub para o repositório `cortexplor`:
   <https://claude.ai/code/onboarding?magic=github-app-setup>
2. No `site.config.yaml`, preencha a data do lançamento — é ela que controla o
   ramp de volume:

   ```yaml
   publishing:
     launch_date: "2026-08-29"
   ```

3. Crie a Routine diária em <https://claude.ai/code/routines> (ou peça para eu
   criar). Ela roda `brief`, checa as pautas, escreve as matérias seguindo
   `.claude/skills/redacao-diaria/SKILL.md` e dá push.
4. O push aciona o workflow **Finalizar**, que busca a imagem, roda o gate e
   publica. O **Deploy** sobe para a Hostinger em seguida.

O workflow **Publicar (modo API)** existe mas está sem agendamento — ninguém
paga por engano. Ver "Voltar para o modo API" no README.

---

## 5. Google Analytics 4

Crie a propriedade, pegue o ID (`G-XXXXXXXXXX`) e preencha:

```yaml
analytics:
  ga4_id: "G-XXXXXXXXXX"
```

A tag só é renderizada quando o campo tem valor — o site não carrega Analytics
vazio.

## 6. Google Search Console

1. Adicione a propriedade `cortexplor.com`.
2. Se pedir verificação por meta tag, cole o código em
   `analytics.search_console_verification`.
3. Envie os três sitemaps:
   - `https://cortexplor.com/sitemap-pt.xml`
   - `https://cortexplor.com/sitemap-en.xml`
   - `https://cortexplor.com/sitemap-es.xml`

## 7. AdSense

Só depois de ter conteúdo real publicado — site novo e vazio costuma ser
reprovado. Quando aprovar:

```yaml
ads:
  enabled: true
  client_id: "ca-pub-XXXXXXXXXXXXXXXX"
  slots:
    top_leaderboard: "1234567890"
    in_content: "1234567891"
    home_between_blocks: "1234567892"
    home_sidebar: "1234567894"
    footer: "1234567893"
```

Todos os slots listados em `ads.slots` já estão posicionados no HTML como
comentários (`<!-- ad slot: ... -->`). Preencher o config liga todos de uma vez,
sem tocar em template.

## 8. Métricas automáticas (GA4 + Search Console)

Feito uma vez, não precisa mexer de novo:

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com)
   e ative a **Google Analytics Data API** e a **Search Console API**.
2. Crie uma conta de serviço nesse projeto e gere uma chave **JSON**.
3. Dê acesso de leitura pra essa conta de serviço:
   - No GA4: Administrador → Gerenciamento de acesso à propriedade → papel
     "Leitor".
   - No Search Console: Configurações → Usuários e permissões → qualquer
     nível, "Restrita" já basta pra ler relatório.
4. Cole o conteúdo inteiro do arquivo `.json` como secret do repositório,
   nome `GA_SEARCH_CONSOLE_CREDENTIALS` (Settings → Secrets and variables →
   Actions). O valor nunca fica no código.
5. Preencha em `site.config.yaml` (não são segredo, só identificadores):
   ```yaml
   analytics:
     ga4_property_id: "123456789"
     search_console_site: "https://cortexplor.com/"
   ```

O workflow **Métricas** roda toda segunda-feira, busca os números das duas
APIs e commita `data/analytics.json` — mesmo padrão do `briefing.json`: coleta
onde há internet, a Routine só lê o resultado. Pra rodar na hora, dispare o
workflow manualmente em Actions → Métricas → Run workflow.

## 8. Skill de voz

O arquivo `.claude/skills/voz-cortexplor/SKILL.md` está com regras genéricas
seguras. Para a voz de verdade, junte de 5 a 10 textos que representem como você
quer que o site escreva e me passe — o próprio arquivo explica o processo no fim.

## 9. Fontes de agência (opcional, mas relevante)

Reuters e AP fecharam o RSS público — os feeds antigos retornam erro. Hoje a
checagem cruzada roda com 14 veículos de tecnologia (MIT Tech Review, TechCrunch,
The Verge, Wired, Ars Technica, ZDNet, The Register, Olhar Digital, Tecmundo,
Canaltech, Xataka, Hipertextual, El País e VentureBeat).

Duas formas de recuperar peso de agência:

- **Tavily** (mais barato e já previsto no config): conta em tavily.com, chave na
  variável de ambiente, e trocar `collection.tavily.enabled` para `true`.
- **API paga da Reuters/AP**: precisa de contrato comercial.

## 10. Newsletter

O bloco na home está com `action="#"`. Quando escolher a ferramenta
(Mailchimp, Beehiiv, Buttondown), é só apontar o formulário para o endpoint dela.

---

## Checagem rápida antes de abrir ao público

```bash
python scripts/tools/selfcheck.py
```

```bash
python -m scripts.pipeline.run status
```

```bash
python -m http.server 4173
```

- [ ] `launch_date` preenchido
- [ ] GA4 e Search Console ativos
- [ ] páginas institucionais revisadas (`/pt/sobre/`, `/pt/privacidade/`,
      `/pt/contato/`, `/pt/termos/` e equivalentes em EN e ES)
- [ ] e-mail `contato@cortexplor.com` criado e funcionando

## 9. Capa, tema e idiomas (para replicar em outro nicho)

Tudo que muda de um nicho para outro fica no `site.config.yaml`:

- `editorial.home_layout`: a ordem dos blocos da capa. Blocos disponíveis:
  `today`, `feed`, `by_section`, `hero`, `most_read`, `topic_modules`,
  `ad_between_blocks`, `newsletter`. Um bloco de conteúdo não pode aparecer duas
  vezes (o build recusa).
- `editorial.today_label` e `editorial.highlights_label`: os nomes dos blocos
  ("Hoje em IA" vira "Hoje no Esporte", por exemplo).
- `editorial.today_count`, `timeline_count`, `highlights_count`,
  `highlights_days`, `section_posts`, `section_columns`, `most_read_min_views`.
- `brand.default_theme`: `light`, `dark` ou `system`. O leitor troca pelo botão
  do topo e a escolha fica no navegador dele.
- `newsletter.title` e `newsletter.text`: o texto da chamada de e-mail.

As páginas institucionais (`content/pages/<idioma>/*.json`) precisam do campo
`key` (`about`, `privacy`, `contact`, `terms`), igual nos três idiomas: é ele que
liga "Sobre" a "About" e "Acerca" no hreflang e no seletor de idioma.
`scripts/tools/make_pages.py` já gera o campo.

## 10. Publicação ao longo do dia

O código já suporta três rodadas por dia (coleta às 07h, 12h e 18h no fuso do
site, Routine 30 minutos depois de cada uma), mas **hoje roda uma só**
(coleta 03:30, Routine ~04:00). Para ligar as três, três pontos precisam andar
juntos (os cron já estão comentados nos workflows):

1. `publishing.run_hours` no `site.config.yaml` (ex.: `[7, 12, 18]`).
2. Os `cron` do workflow **Coletar** (em UTC; Brasília é UTC-3).
3. O horário da Routine em claude.ai/code/routines (30 min depois de cada coleta).

O teto diário (`publishing.ramp`) é dividido entre as rodadas que ainda faltam:
com teto 3, a manhã escreve 1, o meio-dia 1 e a noite 1. Uma rodada sem pauta boa
devolve a vaga e a seguinte escreve mais. O briefing de outro dia é recusado; o de
uma rodada anterior do mesmo dia serve (as pautas já escritas saem dele e o teto é
recalculado), então uma coleta que falha não custa a rodada.
