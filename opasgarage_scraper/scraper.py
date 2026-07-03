#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper do Opas Garage (opasgarage.com.br)
==========================================

Extrai as postagens de um site com login (Google/2FA) usando um navegador
real com PERFIL PERSISTENTE: você loga uma única vez na janela e o scraper
reaproveita a sessão. Nenhuma credencial é digitada pelo script.

Fluxo de uso:
    1. python scraper.py login       # abre o navegador; faça login manualmente
    2. python scraper.py discover     # descobre os endereços dos posts
    3. python scraper.py scrape       # extrai e salva (SQLite + JSONL)
    4. python scraper.py export       # (re)gera o JSONL a partir do banco

Ou tudo de uma vez, depois do login:
    python scraper.py all

Saída:
    data/opas.sqlite   -> banco com todos os posts
    data/posts.jsonl   -> um JSON por linha (pronto para RAG/agente de IA)
    data/urls.txt      -> lista de URLs descobertas
    data/images/       -> imagens baixadas (se download_images: true)

Requer autorização do dono do site. Respeite os Termos de Uso.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml

# ---------------------------------------------------------------------------
# Caminhos base
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
IMAGES = DATA / "images"
PROFILE_DIR = ROOT / ".pw-profile"          # perfil do navegador (contém a sessão)
DB_PATH = DATA / "opas.sqlite"
JSONL_PATH = DATA / "posts.jsonl"
URLS_PATH = DATA / "urls.txt"


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
def load_config() -> dict:
    cfg_path = ROOT / "config.yaml"
    if not cfg_path.exists():
        sys.exit(
            "config.yaml não encontrado.\n"
            "Rode:  cp config.example.yaml config.yaml   e ajuste os valores."
        )
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    cfg.setdefault("listing_urls", [])
    cfg.setdefault("post_url_pattern", r"/blog/[^/]+/?$")
    cfg.setdefault("next_page_selector", "a[rel='next'], a.next, .pagination a.next")
    cfg.setdefault("max_listing_pages", 100)
    cfg.setdefault("selectors", {})
    cfg.setdefault("delay_seconds", 2.0)
    cfg.setdefault("max_posts", 2000)
    cfg.setdefault("headless_scrape", False)
    cfg.setdefault("download_images", True)
    cfg.setdefault("browser_channel", "chrome")
    # Modo CDP: conectar a um Chrome REAL já aberto pelo usuário (resolve o
    # bloqueio do login do Google em navegadores automatizados).
    cfg.setdefault("use_cdp", False)
    cfg.setdefault("cdp_url", "http://localhost:9222")
    # Modo COOKIES: reaproveita a sessão exportada do seu Chrome normal
    # (jeito mais robusto quando o login é via Google). Aponte para o arquivo
    # de cookies exportado (ex. pela extensão "Cookie-Editor").
    cfg.setdefault("cookies_file", "cookies.json")
    if not cfg.get("base_url"):
        sys.exit("Defina 'base_url' no config.yaml")
    return cfg


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
def db_connect() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            url         TEXT PRIMARY KEY,
            title       TEXT,
            author      TEXT,
            date        TEXT,
            categories  TEXT,
            content_text TEXT,
            content_html TEXT,
            images      TEXT,   -- JSON array de URLs
            scraped_at  TEXT
        )
        """
    )
    conn.commit()
    return conn


def already_scraped(conn: sqlite3.Connection, url: str) -> bool:
    cur = conn.execute("SELECT 1 FROM posts WHERE url = ? AND content_text != ''", (url,))
    return cur.fetchone() is not None


def save_post(conn: sqlite3.Connection, post: dict) -> None:
    conn.execute(
        """
        INSERT INTO posts (url, title, author, date, categories,
                           content_text, content_html, images, scraped_at)
        VALUES (:url, :title, :author, :date, :categories,
                :content_text, :content_html, :images, :scraped_at)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title, author=excluded.author, date=excluded.date,
            categories=excluded.categories, content_text=excluded.content_text,
            content_html=excluded.content_html, images=excluded.images,
            scraped_at=excluded.scraped_at
        """,
        post,
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Navegador (Playwright, contexto persistente)
# ---------------------------------------------------------------------------
def load_cookies_file(path: Path) -> list:
    """Lê cookies exportados (formato Cookie-Editor / EditThisCookie) e
    converte para o formato que o Playwright entende."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "cookies" in raw:
        raw = raw["cookies"]
    samesite_map = {
        "no_restriction": "None", "none": "None",
        "lax": "Lax", "unspecified": "Lax", "": "Lax",
        "strict": "Strict",
    }
    out = []
    for c in raw:
        name, value = c.get("name"), c.get("value")
        domain = c.get("domain")
        if not name or domain is None:
            continue
        ck = {
            "name": name,
            "value": value or "",
            "domain": domain,
            "path": c.get("path", "/") or "/",
            "httpOnly": bool(c.get("httpOnly", False)),
            "secure": bool(c.get("secure", False)),
            "sameSite": samesite_map.get(str(c.get("sameSite", "")).lower(), "Lax"),
        }
        exp = c.get("expirationDate") or c.get("expires")
        if exp and not c.get("session"):
            try:
                ck["expires"] = int(float(exp))
            except (TypeError, ValueError):
                pass
        out.append(ck)
    return out


def launch_context(cfg: dict, headless: bool):
    """Abre/conecta o navegador. Devolve (pw, ctx, closer).

    Dois modos:
      - use_cdp: True  -> conecta a um Chrome REAL já aberto pelo usuário
                          (necessário quando o login é via Google, que bloqueia
                          navegadores automatizados). NÃO fecha o seu Chrome.
      - use_cdp: False -> abre um navegador próprio com perfil persistente.
    """
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()

    # ---- Modo CDP: conectar ao Chrome real já logado --------------------
    if cfg.get("use_cdp"):
        cdp_url = cfg.get("cdp_url") or "http://localhost:9222"
        try:
            browser = pw.chromium.connect_over_cdp(cdp_url)
        except Exception as exc:
            pw.stop()
            sys.exit(
                f"Não consegui conectar ao Chrome em {cdp_url} ({exc}).\n"
                "Abra o Chrome com depuração ligada ANTES (veja o README, seção "
                "'Login via Google') e deixe-o aberto e logado no site."
            )
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()

        def closer():
            pw.stop()  # apenas solta a conexão; NÃO fecha o seu Chrome

        return pw, ctx, closer

    # ---- Modo próprio: navegador com perfil persistente -----------------
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    launch_kwargs = dict(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        viewport={"width": 1366, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    channel = cfg.get("browser_channel")
    if channel:
        launch_kwargs["channel"] = channel  # ex.: "chrome"
    try:
        ctx = pw.chromium.launch_persistent_context(**launch_kwargs)
    except Exception as exc:
        if channel:
            print(f"[aviso] canal '{channel}' indisponível ({exc}); usando Chromium do Playwright.")
            launch_kwargs.pop("channel", None)
            ctx = pw.chromium.launch_persistent_context(**launch_kwargs)
        else:
            raise

    # Modo COOKIES: injeta a sessão exportada do seu Chrome normal.
    cookies_path = ROOT / str(cfg.get("cookies_file") or "")
    if cfg.get("cookies_file") and cookies_path.exists():
        try:
            cookies = load_cookies_file(cookies_path)
            ctx.add_cookies(cookies)
            print(f"[cookies] {len(cookies)} cookies carregados de {cookies_path.name}")
        except Exception as exc:
            print(f"[aviso] não consegui carregar {cookies_path.name}: {exc}")

    def closer():
        ctx.close()
        pw.stop()

    return pw, ctx, closer


# ---------------------------------------------------------------------------
# Comando: LOGIN
# ---------------------------------------------------------------------------
def cmd_login(cfg: dict) -> None:
    # No modo CDP o login é feito por você no seu próprio Chrome; aqui só
    # confirmamos que a conexão funciona e que você está logado.
    if cfg.get("use_cdp"):
        print("Modo CDP: conectando ao seu Chrome já aberto...")
        pw, ctx, closer = launch_context(cfg, headless=False)
        page = ctx.new_page()
        try:
            page.goto(cfg["base_url"], wait_until="domcontentloaded", timeout=60000)
            print("Conexão OK! Título da página:", (page.title() or "")[:80])
            print("Se você já fez login nessa janela do Chrome, pode rodar: python scraper.py all")
        except Exception as exc:
            print("[aviso] conectou, mas a página demorou:", exc)
        finally:
            page.close()
            closer()
        return

    print("Abrindo o navegador. Faça login no site (inclusive Google/2FA).")
    pw, ctx, closer = launch_context(cfg, headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try:
        page.goto(cfg["base_url"], wait_until="domcontentloaded", timeout=60000)
    except Exception as exc:
        print(f"[aviso] a página inicial demorou ({exc}); você pode navegar manualmente.")
    print("\n>>> Faça o login na janela do navegador.")
    print(">>> Quando terminar e estiver logado, volte AQUI e pressione ENTER.")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    closer()
    print("Sessão salva em", PROFILE_DIR)
    print("Pronto! Agora rode:  python scraper.py discover")


# ---------------------------------------------------------------------------
# Descoberta de URLs de posts
# ---------------------------------------------------------------------------
SITEMAP_CANDIDATES = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
    "/post-sitemap.xml",
    "/sitemap-posts.xml",
]


def fetch_text(page, url: str) -> str:
    """Carrega uma URL na sessão logada e devolve o conteúdo (texto/HTML/XML)."""
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if resp and resp.status >= 400:
            return ""
        return page.content()
    except Exception:
        return ""


def discover_from_sitemaps(page, base_url: str, pattern: re.Pattern) -> set:
    from bs4 import BeautifulSoup

    found, to_visit, seen = set(), list(SITEMAP_CANDIDATES), set()
    while to_visit:
        path = to_visit.pop(0)
        sm_url = urljoin(base_url, path)
        if sm_url in seen:
            continue
        seen.add(sm_url)
        xml = fetch_text(page, sm_url)
        if not xml or "<loc" not in xml.lower():
            continue
        soup = BeautifulSoup(xml, "xml")
        locs = [loc.get_text(strip=True) for loc in soup.find_all("loc")]
        for loc in locs:
            low = loc.lower()
            if low.endswith(".xml") or "sitemap" in low:
                to_visit.append(loc)                # sitemap-índice: descer um nível
            elif pattern.search(loc):
                found.add(loc)
        print(f"  sitemap {sm_url}: {len(locs)} URLs, {len(found)} posts até agora")
    return found


def discover_from_listings(page, cfg: dict, pattern: re.Pattern) -> set:
    from bs4 import BeautifulSoup

    found = set()
    for start in cfg["listing_urls"]:
        current, pages = start, 0
        visited = set()
        while current and pages < cfg["max_listing_pages"]:
            if current in visited:
                break
            visited.add(current)
            html = fetch_text(page, current)
            pages += 1
            if not html:
                break
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                link = urljoin(current, a["href"].split("#")[0])
                if pattern.search(link):
                    found.add(link)
            # próxima página
            nxt = None
            for sel in cfg["next_page_selector"].split(","):
                el = soup.select_one(sel.strip())
                if el and el.get("href"):
                    nxt = urljoin(current, el["href"])
                    break
            print(f"  listagem {current}: {len(found)} posts acumulados")
            current = nxt
            time.sleep(cfg["delay_seconds"])
    return found


def cmd_discover(cfg: dict) -> None:
    pattern = re.compile(cfg["post_url_pattern"])
    pw, ctx, closer = launch_context(cfg, headless=cfg["headless_scrape"])
    page = ctx.new_page()
    print("Descobrindo posts via sitemap...")
    urls = discover_from_sitemaps(page, cfg["base_url"], pattern)
    if cfg["listing_urls"]:
        print("Descobrindo posts via páginas de listagem...")
        urls |= discover_from_listings(page, cfg, pattern)
    page.close()
    closer()

    urls = sorted(urls)
    DATA.mkdir(parents=True, exist_ok=True)
    URLS_PATH.write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")
    print(f"\n{len(urls)} URLs de posts salvas em {URLS_PATH}")
    if not urls:
        print(
            "Nenhuma URL encontrada. Ajuste 'post_url_pattern' e 'listing_urls' no config.yaml\n"
            "(abra um post real no navegador e confira o padrão do endereço)."
        )


# ---------------------------------------------------------------------------
# Extração de um post
# ---------------------------------------------------------------------------
def extract_with_selectors(html: str, base_url: str, sel: dict) -> dict:
    """Extração via seletores CSS informados no config (parcial; complementa o trafilatura)."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    out = {}

    def text_of(css):
        if not css:
            return ""
        el = soup.select_one(css)
        return el.get_text(" ", strip=True) if el else ""

    out["title"] = text_of(sel.get("title", ""))
    out["author"] = text_of(sel.get("author", ""))
    out["date"] = text_of(sel.get("date", ""))
    if sel.get("category"):
        cats = [e.get_text(" ", strip=True) for e in soup.select(sel["category"])]
        out["categories"] = ", ".join([c for c in cats if c])
    else:
        out["categories"] = ""

    content_html, content_text, images = "", "", []
    if sel.get("content"):
        node = soup.select_one(sel["content"])
        if node:
            content_html = str(node)
            content_text = node.get_text("\n", strip=True)
            images = [urljoin(base_url, img.get("src", "")) for img in node.find_all("img") if img.get("src")]
    out["content_html"] = content_html
    out["content_text"] = content_text
    out["images"] = images
    return out


def extract_smart(html: str, url: str) -> dict:
    """Extração automática via trafilatura (título, texto, autor, data)."""
    import trafilatura

    out = {"title": "", "author": "", "date": "", "categories": "",
           "content_text": "", "content_html": "", "images": []}
    try:
        data = trafilatura.extract(
            html, url=url, output_format="json",
            include_images=True, include_links=False,
            with_metadata=True, favor_recall=True,
        )
        if data:
            j = json.loads(data)
            out["title"] = j.get("title") or ""
            out["author"] = j.get("author") or ""
            out["date"] = j.get("date") or ""
            out["categories"] = j.get("categories") or ""
            if isinstance(out["categories"], list):
                out["categories"] = ", ".join(out["categories"])
            out["content_text"] = j.get("text") or j.get("raw_text") or ""
    except Exception as exc:
        print(f"    [aviso] trafilatura falhou em {url}: {exc}")
    return out


def merge_extractions(smart: dict, css: dict) -> dict:
    """Prioriza o que veio dos seletores CSS; completa com a extração automática."""
    merged = dict(smart)
    for k, v in css.items():
        if v:
            merged[k] = v
    if not merged.get("content_text") and css.get("content_text"):
        merged["content_text"] = css["content_text"]
    if css.get("images"):
        merged["images"] = css["images"]
    return merged


def collect_images(html: str, base_url: str) -> list:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src:
            imgs.append(urljoin(base_url, src))
    # remove duplicatas mantendo ordem
    seen, out = set(), []
    for u in imgs:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def download_images(page, urls: list, post_url: str) -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", urlparse(post_url).path).strip("-") or "post"
    folder = IMAGES / slug
    folder.mkdir(parents=True, exist_ok=True)
    for i, u in enumerate(urls):
        name = os.path.basename(urlparse(u).path) or f"img_{i}"
        dest = folder / name
        if dest.exists():
            continue
        try:
            resp = page.request.get(u, timeout=30000)
            if resp.ok:
                dest.write_bytes(resp.body())
        except Exception as exc:
            print(f"    [aviso] imagem falhou {u}: {exc}")


def cmd_scrape(cfg: dict) -> None:
    if not URLS_PATH.exists():
        sys.exit("data/urls.txt não existe. Rode antes:  python scraper.py discover")
    urls = [u.strip() for u in URLS_PATH.read_text(encoding="utf-8").splitlines() if u.strip()]
    if not urls:
        sys.exit("Nenhuma URL em data/urls.txt")

    conn = db_connect()
    pw, ctx, closer = launch_context(cfg, headless=cfg["headless_scrape"])
    page = ctx.new_page()
    sel = cfg.get("selectors") or {}

    done = 0
    for idx, url in enumerate(urls[: cfg["max_posts"]], 1):
        if already_scraped(conn, url):
            print(f"[{idx}/{len(urls)}] (pulando, já extraído) {url}")
            continue
        print(f"[{idx}/{len(urls)}] {url}")
        html = fetch_text(page, url)
        if not html:
            print("    [aviso] não carregou; pode ter deslogado. Rode 'login' de novo se persistir.")
            continue

        smart = extract_smart(html, url)
        css = extract_with_selectors(html, cfg["base_url"], sel)
        post = merge_extractions(smart, css)
        if not post.get("images"):
            post["images"] = collect_images(html, cfg["base_url"])

        if cfg["download_images"] and post["images"]:
            download_images(page, post["images"], url)

        record = {
            "url": url,
            "title": post.get("title", ""),
            "author": post.get("author", ""),
            "date": post.get("date", ""),
            "categories": post.get("categories", ""),
            "content_text": post.get("content_text", ""),
            "content_html": post.get("content_html", ""),
            "images": json.dumps(post.get("images", []), ensure_ascii=False),
            "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        save_post(conn, record)
        done += 1
        chars = len(record["content_text"])
        print(f"    ok: '{record['title'][:60]}'  ({chars} caracteres)")
        time.sleep(cfg["delay_seconds"])

    page.close()
    closer()
    conn.close()
    print(f"\nConcluído. {done} posts novos extraídos.")
    cmd_export(cfg)


# ---------------------------------------------------------------------------
# Exportação para JSONL
# ---------------------------------------------------------------------------
def cmd_export(cfg: dict) -> None:
    conn = db_connect()
    cur = conn.execute(
        "SELECT url,title,author,date,categories,content_text,images,scraped_at "
        "FROM posts ORDER BY date"
    )
    n = 0
    with open(JSONL_PATH, "w", encoding="utf-8") as fh:
        for row in cur:
            rec = {
                "url": row[0], "title": row[1], "author": row[2], "date": row[3],
                "categories": row[4], "content": row[5],
                "images": json.loads(row[6] or "[]"), "scraped_at": row[7],
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    conn.close()
    print(f"{n} posts exportados para {JSONL_PATH}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper do Opas Garage (com autorização do dono).")
    parser.add_argument("command", choices=["login", "discover", "scrape", "export", "all"],
                        help="etapa a executar")
    args = parser.parse_args()
    cfg = load_config()

    if args.command == "login":
        cmd_login(cfg)
    elif args.command == "discover":
        cmd_discover(cfg)
    elif args.command == "scrape":
        cmd_scrape(cfg)
    elif args.command == "export":
        cmd_export(cfg)
    elif args.command == "all":
        cmd_discover(cfg)
        cmd_scrape(cfg)


if __name__ == "__main__":
    main()
