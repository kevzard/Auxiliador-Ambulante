"""
database.py
Camada de infraestrutura: abre a conexão com o SQLite, cria o schema e
popula os dados padrão na primeira execução.

Importante: este arquivo NÃO conhece Cliente/Produto nem faz nenhuma regra
de negócio — isso agora é responsabilidade dos repositórios (pasta
repositories/). Aqui só existe "como conversar com o arquivo .db".
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vendaaz.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão nova com o banco, já com row_factory para
    conseguirmos acessar as colunas pelo nome (ex: linha["nome"])."""
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

    # --- Clientes padrão (só na primeira execução) ---
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

    # --- Produtos padrão (só na primeira execução) ---
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
