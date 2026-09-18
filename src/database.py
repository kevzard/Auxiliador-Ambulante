"""
database.py
Camada de acesso a dados do Vendaaz, usando SQLite puro (sqlite3).

Responsável por:
- Criar o banco e as tabelas na primeira execução
- Popular clientes e produtos padrão (equivalentes aos DEFAULT_CLIENTS
  e à lista de produtos fixa que existiam no protótipo em HTML/JS)
- Expor funções simples de CRUD para o main.py usar
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vendaaz.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão nova com o banco, já com row_factory para
    conseguirmos acessar as colunas pelo nome (ex: cliente["nome"])."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Cria as tabelas (se não existirem) e popula os dados padrão
    apenas na primeira execução do app."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            saldo REAL NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            imagem TEXT NOT NULL
        )
        """
    )

    conn.commit()

    # --- Clientes padrão (equivalentes ao DEFAULT_CLIENTS do protótipo) ---
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_padrao = [
            ("Rodrigo Bentini", 100.00),
            ("Ana Monteiro", 50.00),
            ("João Amorim", 23.00),
        ]
        cursor.executemany(
            "INSERT INTO clientes (nome, saldo) VALUES (?, ?)", clientes_padrao
        )

    # --- Produtos padrão (equivalentes à grade fixa em venda.html) ---
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos_padrao = [
            ("Paçoca", 1.00, "pacoca.png"),
            ("Pé de Moça", 3.00, "pe-de-moca.png"),
            ("Amendoim Salgado", 3.00, "amendoim-salgado.png"),
            ("Balas Fini", 2.50, "balas-fini.png"),
            ("Balas Freegells", 2.00, "balas-freegells.png"),
            ("Balas Mentos", 2.50, "balas-mentos.png"),
            ("Chicletes Mentos", 3.50, "chicletes-mentos.png"),
        ]
        cursor.executemany(
            "INSERT INTO produtos (nome, preco, imagem) VALUES (?, ?, ?)",
            produtos_padrao,
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

def listar_clientes() -> list[sqlite3.Row]:
    """Retorna todos os clientes, na ordem de cadastro."""
    conn = get_connection()
    clientes = conn.execute("SELECT * FROM clientes ORDER BY id").fetchall()
    conn.close()
    return clientes


def buscar_cliente(cliente_id: int) -> sqlite3.Row | None:
    """Busca um único cliente pelo id."""
    conn = get_connection()
    cliente = conn.execute(
        "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
    ).fetchone()
    conn.close()
    return cliente


def criar_cliente(nome: str) -> int:
    """Cria um cliente novo com saldo inicial zero.
    Retorna o id do cliente criado."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO clientes (nome, saldo) VALUES (?, 0)", (nome,)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def atualizar_saldo(cliente_id: int, novo_saldo: float) -> None:
    """Atualiza o saldo (carteira) de um cliente.
    Usado tanto na recarga quanto ao debitar o valor de uma venda."""
    conn = get_connection()
    conn.execute(
        "UPDATE clientes SET saldo = ? WHERE id = ?", (novo_saldo, cliente_id)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Produtos
# ---------------------------------------------------------------------------

def listar_produtos() -> list[sqlite3.Row]:
    """Retorna todos os produtos disponíveis para venda."""
    conn = get_connection()
    produtos = conn.execute("SELECT * FROM produtos ORDER BY id").fetchall()
    conn.close()
    return produtos
