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
| `ANTHROPIC_API_KEY` | chave da API do Claude | console.anthropic.com |
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

## 4. Ligar a publicação automática

No `site.config.yaml`, preencha a data do lançamento — é ela que controla o ramp
de volume:

```yaml
publishing:
  launch_date: "2026-09-01"
```

O workflow **Publicar** roda todo dia às 06:00 (horário de Brasília). Para testar
antes: **Actions > Publicar > Run workflow**, com `limit = 1`.

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
    footer: "1234567893"
```

Os quatro slots já estão posicionados no HTML como comentários
(`<!-- ad slot: ... -->`). Preencher o config liga todos de uma vez, sem tocar em
template.

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
