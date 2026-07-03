# Scraper do Opas Garage

Extrai as postagens do site **opasgarage.com.br** (que exige login) e salva
tudo em **SQLite + JSONL**, num formato pronto para alimentar um agente de IA
(RAG).

> ⚠️ **Uso autorizado.** Rode isto apenas com autorização do dono do site e
> respeitando os Termos de Uso. O conteúdo tem direitos autorais do Opas Garage.

## Por que rodar na SUA máquina

O login é via **Google/2FA**. Como o Google bloqueia login em navegadores
automatizados, o scraper reaproveita a sessão do **seu Chrome normal** (método
de cookies). Suas credenciais nunca são digitadas pelo script nem saem da sua
máquina.

## Instalação

Precisa de **Python 3.9+**.

```powershell
cd C:\Users\User\Downloads\Scraper

python -m pip install -r requirements.txt
python -m playwright install chromium

copy config.example.yaml config.yaml
```

## 1. Login via Google — método COOKIES (recomendado)

O Google bloqueia login em navegadores automatizados (o popup abre em branco).
A forma mais confiável é reaproveitar a sessão do **seu Chrome normal**, copiando
os cookies. Você faz isso **uma vez**:

1. No seu **Chrome do dia a dia**, entre em `https://opasgarage.com.br` e
   **faça login normalmente** (com o Google — aqui funciona, é o seu Chrome).
2. Instale a extensão gratuita **Cookie-Editor**:
   https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
3. Com o site **aberto e logado**, clique no ícone da extensão (Cookie-Editor).
4. Clique em **Export** e escolha **JSON** — isso copia os cookies.
5. Na pasta do scraper, crie um arquivo chamado **`cookies.json`** e **cole**
   (Ctrl+V) o conteúdo. Salve.
   - No Bloco de Notas: *Arquivo -> Salvar como*, nome `cookies.json`, e em
     "Tipo" escolha **Todos os arquivos** (senão vira `cookies.json.txt`).
6. No `config.yaml` já vem `use_cdp: false` e `cookies_file: "cookies.json"`.

Pronto — o scraper usa essa sessão. Não precisa dos arquivos `.bat`.

> Os cookies são o seu "crachá" de login. **Não compartilhe o `cookies.json`.**
> O `.gitignore` já impede que ele suba pro Git.

Teste rápido (deve abrir o site já logado e imprimir o título):
```powershell
python scraper.py login
```

## 2. Descobrir os posts
```powershell
python scraper.py discover
```
Procura os endereços dos posts (via sitemap e/ou páginas de listagem) e salva em
`data/urls.txt`.

> Se vier **0 URLs**: abra um post real no navegador, veja o padrão do endereço
> e ajuste `post_url_pattern` e `listing_urls` no `config.yaml`.

## 3. Extrair o conteúdo
```powershell
python scraper.py scrape
```
Visita cada post, extrai **título, autor, data, categoria, texto e imagens** e
salva em `data/opas.sqlite`. Ao final gera o `data/posts.jsonl`.

- É **retomável**: se parar no meio, rode de novo que ele pula o que já foi feito.

### Tudo de uma vez (após o login)
```powershell
python scraper.py all
```

## Ajuste fino da extração

O extrator automático (trafilatura) acerta a maioria dos casos sozinho. Se
algum campo vier errado, preencha os **seletores CSS** no `config.yaml` (clique
com o botão direito no elemento do site -> *Inspecionar* para achar o seletor):

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
| `data/posts.jsonl` | Um JSON por linha: `url, title, author, date, categories, content, images` |
| `data/urls.txt` | Lista de URLs descobertas |
| `data/images/` | Imagens baixadas, uma pasta por post |

O `posts.jsonl` já está no formato ideal para indexar num RAG e montar o agente
de IA.

## Alternativa: método CDP (avançado)

Se preferir, dá para conectar a um Chrome com depuração aberta (`use_cdp: true` +
`abrir_chrome_login.bat`). Mas o Google costuma bloquear o login nesse modo — por
isso o método de cookies acima é o recomendado.

## Boas práticas embutidas

- Pausa entre páginas (`delay_seconds`) para não sobrecarregar o servidor.
- Teto de posts (`max_posts`) como trava de segurança.
- Nada de credenciais no código — só a sua sessão (cookies) local.
- `.gitignore` ignora sessão, cookies, config e dados (não sobem pro Git).
