# O que falta para o site entrar no ar

Ordem sugerida. Os itens 1 a 4 sao o caminho critico: com eles o site publica
sozinho. O resto pode vir depois.

---

## 1. Repositorio no GitHub

```bash
gh repo create cortexplor --private --source=. --push
```

Se preferir pela interface: crie o repositorio vazio e depois

```bash
git remote add origin git@github.com:SEU_USUARIO/cortexplor.git
git push -u origin main
```

## 2. Secrets no GitHub

Em **Settings > Secrets and variables > Actions > New repository secret**:

| Secret | O que e | Onde conseguir |
|---|---|---|
| `HOSTINGER_SSH_KEY` | a **chave privada** de deploy | ja existe: `~/.ssh/pontoesal_deploy` |
| `ANTHROPIC_API_KEY` | chave da API do Claude | console.anthropic.com |
| `UNSPLASH_ACCESS_KEY` | banco de imagens | unsplash.com/developers |
| `PEXELS_API_KEY` | banco de imagens (reserva) | pexels.com/api |

A chave privada voce mesmo sobe - eu nao movo credencial. Pela CLI do GitHub:

```bash
gh secret set HOSTINGER_SSH_KEY < ~/.ssh/pontoesal_deploy
```

> A chave `Deploy Claude` que ja esta na Hostinger foi testada em 28/08/2026:
> conecta em `147.79.91.241:65002` como `u433721675`, e `cortexplor.com` ja existe
> na conta. E a mesma chave do Ponto e Sal - funciona, mas o ideal e gerar um par
> exclusivo para este projeto e cadastrar a publica no painel da Hostinger.

## 3. Primeiro deploy

Assim que o primeiro push chegar no `main`, o workflow **Deploy** roda sozinho e
sincroniza tudo com `public_html`. Para disparar na mao: aba **Actions > Deploy >
Run workflow**.

Depois do primeiro deploy, apague o `default.php` que a Hostinger deixou la:

```bash
ssh -i ~/.ssh/pontoesal_deploy -p 65002 u433721675@147.79.91.241 \
  "rm -f ~/domains/cortexplor.com/public_html/default.php"
```

## 4. Ligar a publicacao automatica

No `site.config.yaml`, preencha a data do lancamento - e ela que controla o ramp
de volume:

```yaml
publishing:
  launch_date: "2026-09-01"
```

O workflow **Publicar** roda todo dia as 06:00 (horario de Brasilia). Para testar
antes: **Actions > Publicar > Run workflow**, com `limit = 1`.

---

## 5. Google Analytics 4

Crie a propriedade, pegue o ID (`G-XXXXXXXXXX`) e preencha:

```yaml
analytics:
  ga4_id: "G-XXXXXXXXXX"
```

A tag so e renderizada quando o campo tem valor - o site nao carrega Analytics
vazio.

## 6. Google Search Console

1. Adicione a propriedade `cortexplor.com`.
2. Se pedir verificacao por meta tag, cole o codigo em
   `analytics.search_console_verification`.
3. Envie os tres sitemaps:
   - `https://cortexplor.com/sitemap-pt.xml`
   - `https://cortexplor.com/sitemap-en.xml`
   - `https://cortexplor.com/sitemap-es.xml`

## 7. AdSense

So depois de ter conteudo real publicado - site novo e vazio costuma ser
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

Os quatro slots ja estao posicionados no HTML como comentarios
(`<!-- ad slot: ... -->`). Preencher o config liga todos de uma vez, sem tocar em
template.

## 8. Skill de voz

O arquivo `.claude/skills/voz-cortexplor/SKILL.md` esta com regras genericas
seguras. Para a voz de verdade, junte de 5 a 10 textos que representem como voce
quer que o site escreva e me passe - o proprio arquivo explica o processo no fim.

## 9. Fontes de agencia (opcional, mas relevante)

Reuters e AP fecharam o RSS publico - os feeds antigos retornam erro. Hoje a
checagem cruzada roda com 14 veiculos de tecnologia (MIT Tech Review, TechCrunch,
The Verge, Wired, Ars Technica, ZDNet, The Register, Olhar Digital, Tecmundo,
Canaltech, Xataka, Hipertextual, El Pais e VentureBeat).

Duas formas de recuperar peso de agencia:

- **Tavily** (mais barato e ja previsto no config): conta em tavily.com, chave na
  variavel de ambiente, e trocar `collection.tavily.enabled` para `true`.
- **API paga da Reuters/AP**: precisa de contrato comercial.

## 10. Newsletter

O bloco na home esta com `action="#"`. Quando escolher a ferramenta
(Mailchimp, Beehiiv, Buttondown), e so apontar o formulario para o endpoint dela.

---

## Checagem rapida antes de abrir ao publico

```bash
python -m scripts.pipeline.run status   # ramp, gate, fila
python -m scripts.pipeline.run build    # regera tudo
python -m http.server 4173              # conferir em localhost:4173/pt/
```

- [ ] `default.php` removido do servidor
- [ ] `launch_date` preenchido
- [ ] GA4 e Search Console ativos
- [ ] paginas institucionais revisadas (`/pt/sobre/`, `/pt/privacidade/`,
      `/pt/contato/`, `/pt/termos/` e equivalentes em EN e ES)
- [ ] e-mail `contato@cortexplor.com` criado e funcionando
