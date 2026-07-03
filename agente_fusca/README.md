# Agente de IA sobre Fusca (acervo Opas Garage)

Um assistente que responde perguntas sobre fusca usando o acervo que você
extraiu do Opas Garage. Ele **busca** os posts mais relevantes e a **Claude**
responde com base neles, citando as fontes.

Como funciona (RAG):
1. `build_index.py` lê o `posts.jsonl`, quebra em pedaços e cria um índice de busca (roda **local**, sem custo).
2. `perguntar.py` recebe sua pergunta, acha os trechos certos e pede à Claude para responder usando só esse conteúdo.

## Instalação (Windows)

Precisa de **Python 3.9+**. Na pasta do agente:

```powershell
python -m pip install -r requirements.txt
```

## Passo 1 — Trazer os posts

Copie o arquivo **`posts.jsonl`** (gerado pelo scraper, em
`Scraper\data\posts.jsonl`) para dentro desta pasta.

## Passo 2 — Chave da API da Claude

1. Crie uma chave em **https://console.anthropic.com/** (menu *API Keys*).
2. No PowerShell, defina a variável (uma vez só) e **reabra o terminal**:
   ```powershell
   setx ANTHROPIC_API_KEY "cole-sua-chave-aqui"
   ```

> A Claude é paga por uso. Para um agente pessoal o custo é baixo. Se quiser
> gastar menos, no `config.py` troque `MODEL` para `claude-sonnet-5`
> (bom custo-benefício) ou `claude-haiku-4-5` (mais barato).

## Passo 3 — Construir o índice (uma vez)

```powershell
python build_index.py
```
Na primeira vez ele baixa o modelo de busca (~100 MB) e gera os embeddings.
Cria os arquivos `indice.npz` e `chunks.json`.

## Passo 4 — Conversar com o agente

```powershell
python perguntar.py
```
Faça perguntas como:
- *"Como regular o ponto do motor 1600?"*
- *"Qual óleo usar no fusca?"*
- *"Diferença entre fusca 1300 e 1500?"*

Digite `sair` para encerrar. Cada resposta mostra os **posts consultados**.

## Ajustes (config.py)

| Opção | O que faz |
|---|---|
| `MODEL` | Modelo da Claude (opus-4-8 / sonnet-5 / haiku-4-5) |
| `TOP_K` | Quantos trechos de posts usar por pergunta (padrão 6) |
| `CHUNK_CHARS` | Tamanho dos pedaços de texto na busca |

## Observações

- Sempre que atualizar o `posts.jsonl` (novos posts), rode `build_index.py` de novo.
- O agente responde **apenas** com base no acervo — se algo não estiver nos posts, ele diz que não encontrou, em vez de inventar.
- Tudo roda na sua máquina; só a geração da resposta usa a API da Claude.
