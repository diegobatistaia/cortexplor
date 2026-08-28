# O que falta para o site entrar no ar

Ordem sugerida. Os itens 1 a 4 são o caminho crítico: com eles o site publica
sozinho. O resto pode vir depois.

---

## 1. Repositório no GitHub

```bash
gh repo create cortexplor --private --source=. --push
```

Se preferir pela interface: crie o repositório vazio e depois

```bash
git remote add origin git@github.com:SEU_USUARIO/cortexplor.git
git push -u origin main
```

## 2. Secrets no GitHub

Em **Settings > Secrets and variables > Actions > New repository secret**:

| Secret | O que é | Onde conseguir |
|---|---|---|
| `HOSTINGER_SSH_KEY` | a **chave privada** de deploy | já existe: `~/.ssh/pontoesal_deploy` |
| `ANTHROPIC_API_KEY` | chave da API do Claude | console.anthropic.com |
| `UNSPLASH_ACCESS_KEY` | banco de imagens | unsplash.com/developers |
| `PEXELS_API_KEY` | banco de imagens (reserva) | pexels.com/api |

A chave privada você mesmo sobe — eu não movo credencial. Pela CLI do GitHub:

```bash
gh secret set HOSTINGER_SSH_KEY < ~/.ssh/pontoesal_deploy
```

> A chave `Deploy Claude` que já está na Hostinger foi testada em 28/08/2026:
> conecta em `147.79.91.241:65002` como `u433721675`, e `cortexplor.com` já existe
> na conta. É a mesma chave do Ponto e Sal — funciona, mas o ideal é gerar um par
> exclusivo para este projeto e cadastrar a pública no painel da Hostinger.

## 3. Primeiro deploy

Assim que o primeiro push chegar no `main`, o workflow **Deploy** roda sozinho e
sincroniza tudo com `public_html`. Para disparar na mão: aba **Actions > Deploy >
Run workflow**.

Depois do primeiro deploy, apague o `default.php` que a Hostinger deixou lá:

```bash
ssh -i ~/.ssh/pontoesal_deploy -p 65002 u433721675@147.79.91.241 "rm -f ~/domains/cortexplor.com/public_html/default.php"
```

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

- [ ] `default.php` removido do servidor
- [ ] `launch_date` preenchido
- [ ] GA4 e Search Console ativos
- [ ] páginas institucionais revisadas (`/pt/sobre/`, `/pt/privacidade/`,
      `/pt/contato/`, `/pt/termos/` e equivalentes em EN e ES)
- [ ] e-mail `contato@cortexplor.com` criado e funcionando
