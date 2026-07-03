# -*- coding: utf-8 -*-
"""Configuração do agente de IA sobre fusca (Opas Garage)."""

# Arquivo com os posts extraídos pelo scraper (data/posts.jsonl).
# Copie o posts.jsonl para esta pasta, ou aponte o caminho completo aqui.
POSTS_FILE = "posts.jsonl"

# Onde o índice de busca é salvo (gerado pelo build_index.py).
INDEX_FILE = "indice.npz"
CHUNKS_FILE = "chunks.json"

# Modelo da Claude que responde as perguntas.
#   claude-opus-4-8  -> mais capaz (padrão)
#   claude-sonnet-5  -> mais barato, ótimo custo-benefício
#   claude-haiku-4-5 -> mais rápido e barato, para respostas simples
MODEL = "claude-opus-4-8"
MAX_TOKENS = 2048

# Modelo de embeddings (roda local, multilíngue — bom para português).
EMBED_MODEL = "intfloat/multilingual-e5-small"

# Busca: quantos trechos de posts usar como contexto por pergunta.
TOP_K = 6

# Fatiamento do texto dos posts em pedaços (chunks) para a busca.
CHUNK_CHARS = 1400      # tamanho de cada pedaço (em caracteres)
CHUNK_OVERLAP = 200     # sobreposição entre pedaços
