# Scraper do Opas Garage

Extrai as postagens do site **opasgarage.com.br** (que exige login) e salva
tudo em **SQLite + JSONL**, num formato pronto para alimentar um agente de IA
(RAG).

> ⚠️ **Uso autorizado.** Rode isto apenas com autorização do dono do site e
> respeitando os Termos de Uso. O conteúdo tem direitos autorais do Opas Garage.

## Por que rodar na SUA máquina

O login é via **Google/2FA**, então o scraper usa um **navegador real** com
perfil persistente: você faz login **uma vez** na janela e ele reaproveita a
sessão. Suas credenciais nunca são digitadas pelo script nem saem da sua
máquina. (Este projeto foi criado num ambiente remoto que **não** tem acesso de
rede ao site — por isso a execução é local.)

## Instalação

Precisa de **Python 3.9+** e, de preferência, o **Google Chrome** instalado
(melhor para o login do Google).

```bash
cd opasgarage_scraper

# ambiente virtual (opcional, recomendado)
python3 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium   # baixa o navegador do Playwright

cp config.example.yaml config.yaml      # depois ajuste o config.yaml
```

## Uso — passo a passo

### 1. Login via Google (modo CDP) — recomendado

⚠️ **O Google bloqueia login em navegadores automatizados** ("este navegador
pode não ser seguro" / a tela trava). Por isso, com login Google, use o modo
**CDP**: você abre o **seu próprio Chrome** com depuração ligada, loga
normalmente (o Google aceita, é um Chrome de verdade), e o scraper se conecta
nesse Chrome. No `config.yaml`, deixe `use_cdp: true` (já vem assim).

> ⚠️ **O Google bloqueia o login quando a depuração está ligada** (o popup de
> login abre em branco). Por isso o login é feito em **2 etapas**: primeiro no
> Chrome normal, depois reabrindo o mesmo perfil com depuração.

**Windows — Passo 1: logar (Chrome normal).** Feche todas as janelas do Chrome e
dê dois cliques em **`passo1_logar.bat`**. Vai abrir o Opas Garage no Chrome
normal — **faça login com o Google** (agora funciona). Depois de logado, **feche
o Chrome por completo** (todas as janelas).

**Windows — Passo 2: reabrir com depuração.** Dê dois cliques em
**`abrir_chrome_login.bat`**. O site abre **já logado** (a sessão ficou salva).
**Deixe essa janela aberta.** Volte ao PowerShell e confirme:
```powershell
python scraper.py login
```
Se aparecer "Conexão OK!", está tudo certo — pode seguir para o passo 2.

> **Sem login Google?** Se o site tiver usuário/senha simples, coloque
> `use_cdp: false` no `config.yaml` e o `python scraper.py login` abre um
> navegador próprio; faça login nele e aperte ENTER no terminal.

### 2. Descobrir os posts
```bash
python scraper.py discover
```
Procura os endereços dos posts (via sitemap e/ou páginas de listagem) e salva em
`data/urls.txt`.

> Se vier **0 URLs**: abra um post real no navegador, veja o padrão do endereço
> e ajuste `post_url_pattern` e `listing_urls` no `config.yaml`. Ex.: se os posts
> ficam em `opasgarage.com.br/blog/nome-do-post`, o padrão `"/blog/[^/]+/?$"` já
> serve.

### 3. Extrair o conteúdo
```bash
python scraper.py scrape
```
Visita cada post, extrai **título, autor, data, categoria, texto e imagens** e
salva em `data/opas.sqlite`. Ao final gera o `data/posts.jsonl`.

- É **retomável**: se parar no meio, rode de novo que ele pula o que já foi feito.
- Se o site deslogar no meio, rode `python scraper.py login` de novo.

### Tudo de uma vez (após o login)
```bash
python scraper.py all
```

## Ajuste fino da extração

O extrator automático (trafilatura) acerta a maioria dos casos sozinho. Se
algum campo vier errado, preencha os **seletores CSS** no `config.yaml` — para
descobri-los: no site, clique com o botão direito no elemento → *Inspecionar*.

```yaml
selectors:
  title: "h1.entry-title"
  content: "div.entry-content"
  author: ".author-name"
  date: "time.published"
  category: ".post-category a"
```

## Saída

| Arquivo | Conteúdo |
|---|---|
| `data/opas.sqlite` | Banco com todos os posts (tabela `posts`) |
| `data/posts.jsonl` | Um JSON por linha, campos: `url, title, author, date, categories, content, images` |
| `data/urls.txt` | Lista de URLs descobertas |
| `data/images/` | Imagens baixadas, uma pasta por post |

O `posts.jsonl` já está no formato ideal para o próximo passo: **indexar num RAG
e montar o agente de IA**. Quando tiver esse arquivo gerado, me chame que a
gente monta o agente de perguntas-e-respostas sobre o acervo.

## Boas práticas embutidas

- Pausa entre páginas (`delay_seconds`) para não sobrecarregar o servidor.
- Teto de posts (`max_posts`) como trava de segurança.
- Nada de credenciais no código — só a sua sessão de navegador local.
- `.gitignore` já ignora sessão, config e dados (não sobem pro Git).
