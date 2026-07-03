#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constrói o índice de busca (RAG) a partir do posts.jsonl.

Lê cada post, quebra o texto em pedaços, gera os "embeddings" (representação
numérica de significado) com um modelo local, e salva tudo para o agente usar.

Uso:
    python build_index.py
"""

import json
import sys
from pathlib import Path

import numpy as np

import config

ROOT = Path(__file__).resolve().parent


def carregar_posts(caminho: Path) -> list:
    if not caminho.exists():
        sys.exit(
            f"Não encontrei {caminho.name}.\n"
            "Copie o arquivo posts.jsonl (gerado pelo scraper, na pasta data/) "
            "para esta pasta, ou ajuste POSTS_FILE no config.py."
        )
    posts = []
    with open(caminho, "r", encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.strip()
            if linha:
                posts.append(json.loads(linha))
    return posts


def fatiar(texto: str, tam: int, over: int) -> list:
    """Quebra um texto em pedaços com sobreposição."""
    texto = (texto or "").strip()
    if not texto:
        return []
    if len(texto) <= tam:
        return [texto]
    pedacos, i = [], 0
    while i < len(texto):
        pedacos.append(texto[i:i + tam])
        i += tam - over
    return pedacos


def main() -> None:
    posts = carregar_posts(ROOT / config.POSTS_FILE)
    print(f"{len(posts)} posts carregados.")

    # Monta a lista de pedaços com metadados (título, url, data).
    chunks = []
    for p in posts:
        conteudo = p.get("content") or p.get("content_text") or ""
        titulo = p.get("title", "")
        for pedaco in fatiar(conteudo, config.CHUNK_CHARS, config.CHUNK_OVERLAP):
            chunks.append({
                "titulo": titulo,
                "url": p.get("url", ""),
                "data": p.get("date", ""),
                "categorias": p.get("categories", ""),
                # inclui o título no texto do pedaço melhora a busca
                "texto": f"{titulo}\n{pedaco}",
            })

    if not chunks:
        sys.exit("Nenhum texto encontrado nos posts. O posts.jsonl está vazio?")
    print(f"{len(chunks)} pedaços (chunks) gerados. Carregando modelo de embeddings...")

    from sentence_transformers import SentenceTransformer

    modelo = SentenceTransformer(config.EMBED_MODEL)
    # e5 recomenda o prefixo "passage: " nos documentos.
    textos = [f"passage: {c['texto']}" for c in chunks]
    print("Gerando embeddings (pode demorar alguns minutos na primeira vez)...")
    emb = modelo.encode(
        textos, batch_size=64, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True,
    ).astype("float32")

    np.savez_compressed(ROOT / config.INDEX_FILE, emb=emb)
    with open(ROOT / config.CHUNKS_FILE, "w", encoding="utf-8") as fh:
        json.dump(chunks, fh, ensure_ascii=False)

    print(f"\nOK! Índice salvo em {config.INDEX_FILE} e {config.CHUNKS_FILE}")
    print("Agora rode:  python perguntar.py")


if __name__ == "__main__":
    main()
