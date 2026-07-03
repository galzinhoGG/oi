#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de IA sobre fusca — responde perguntas usando o acervo do Opas Garage.

Fluxo (RAG):
  1. transforma sua pergunta em embedding
  2. busca os trechos de posts mais parecidos (contexto)
  3. pede à Claude que responda usando SÓ esse contexto, citando as fontes

Uso:
    python perguntar.py
    (digite perguntas; 'sair' para encerrar)

Precisa da variável de ambiente ANTHROPIC_API_KEY.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

import config

ROOT = Path(__file__).resolve().parent

SYSTEM = (
    "Você é um especialista em Fusca (VW Type 1) e assistente do acervo do blog "
    "Opas Garage. Responda SEMPRE em português do Brasil, de forma clara e prática.\n\n"
    "Use APENAS as informações dos trechos de posts fornecidos como contexto. "
    "Se a resposta não estiver no contexto, diga com honestidade que não encontrou "
    "essa informação no acervo — não invente. Quando usar um post, cite o título "
    "dele. Seja direto e útil, como um mecânico experiente explicando para um colega."
)


def carregar_indice():
    idx = ROOT / config.INDEX_FILE
    chk = ROOT / config.CHUNKS_FILE
    if not idx.exists() or not chk.exists():
        sys.exit("Índice não encontrado. Rode antes:  python build_index.py")
    emb = np.load(idx)["emb"]
    with open(chk, "r", encoding="utf-8") as fh:
        chunks = json.load(fh)
    return emb, chunks


def buscar(pergunta, modelo_emb, emb, chunks, k):
    # e5 recomenda o prefixo "query: " nas perguntas.
    q = modelo_emb.encode(
        [f"query: {pergunta}"], normalize_embeddings=True, convert_to_numpy=True
    ).astype("float32")[0]
    scores = emb @ q  # produto escalar = similaridade de cosseno (vetores normalizados)
    top = np.argsort(-scores)[:k]
    return [chunks[i] for i in top]


def montar_contexto(trechos):
    partes = []
    for i, t in enumerate(trechos, 1):
        cabecalho = f"[Post {i}] {t['titulo']}"
        if t.get("data"):
            cabecalho += f" ({t['data']})"
        partes.append(f"{cabecalho}\n{t['texto']}\nFonte: {t.get('url','')}")
    return "\n\n---\n\n".join(partes)


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "Defina a variável ANTHROPIC_API_KEY com a sua chave da API da Claude.\n"
            "Windows (PowerShell):  setx ANTHROPIC_API_KEY \"sua-chave\"  (reabra o terminal)\n"
            "Pegue a chave em: https://console.anthropic.com/"
        )

    import anthropic
    from sentence_transformers import SentenceTransformer

    print("Carregando índice e modelo de busca...")
    emb, chunks = carregar_indice()
    modelo_emb = SentenceTransformer(config.EMBED_MODEL)
    client = anthropic.Anthropic()

    print("\nAgente de fusca pronto! Faça sua pergunta (ou 'sair' para encerrar).\n")
    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "quit"):
            break

        trechos = buscar(pergunta, modelo_emb, emb, chunks, config.TOP_K)
        contexto = montar_contexto(trechos)

        mensagem_usuario = (
            f"Contexto (trechos do acervo Opas Garage):\n\n{contexto}\n\n"
            f"Pergunta: {pergunta}"
        )

        print("\nAgente: ", end="", flush=True)
        with client.messages.stream(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=SYSTEM,
            messages=[{"role": "user", "content": mensagem_usuario}],
        ) as stream:
            for texto in stream.text_stream:
                print(texto, end="", flush=True)
        print("\n")

        # Mostra as fontes usadas
        vistos, fontes = set(), []
        for t in trechos:
            chave = t.get("url") or t.get("titulo")
            if chave not in vistos:
                vistos.add(chave)
                fontes.append(f"  - {t['titulo']}  {t.get('url','')}".rstrip())
        print("Fontes consultadas:")
        print("\n".join(fontes))
        print()

    print("Até mais! 🚗")


if __name__ == "__main__":
    main()
