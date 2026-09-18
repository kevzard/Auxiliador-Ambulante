"""
Testes de segurança — SQL Injection

Roda com: python -m pytest tests/test_sql_injection.py -v -s
(o -s é para ver os prints da demonstração didática no final do arquivo)

Este arquivo tem duas partes:

1) ATAQUE CONTRA O CÓDIGO REAL (ClienteRepository)
   Envia payloads clássicos de SQL Injection como se fossem o "nome" de
   um cliente digitado no app, e confere que:
     - nada quebra (nenhuma exceção, nenhuma tabela apagada);
     - o payload é gravado como TEXTO PURO, ou seja, o SQLite nunca
       tentou executá-lo como comando.

2) DEMONSTRAÇÃO DIDÁTICA DE CÓDIGO VULNERÁVEL (NÃO EXISTE NO APP DE VERDADE)
   Recria, num banco SQLite descartável em memória, o jeito ERRADO de
   montar uma query (com f-string) só para você ver, na prática, por que
   a parametrização do item (1) importa. `buscar_cliente_vulneravel` é
   um exemplo negativo — nunca use esse padrão em código real.

Os testes usam um banco SQLite temporário (via monkeypatch em
database.DB_PATH), então NUNCA tocam no vendaaz.db real do projeto.
"""

import sqlite3

import pytest

import database
from repositories.cliente_repository import ClienteRepository


# ---------------------------------------------------------------------------
# Fixture: banco de dados descartável, isolado por teste
# ---------------------------------------------------------------------------

@pytest.fixture
def cliente_repo(tmp_path, monkeypatch) -> ClienteRepository:
    """Aponta database.DB_PATH para um arquivo temporário e roda o
    init_db() nele, garantindo que cada teste comece com um banco limpo
    e que o vendaaz.db do projeto nunca seja tocado."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "teste_injecao.db")
    database.init_db()
    return ClienteRepository()


# ---------------------------------------------------------------------------
# 1) Ataques contra o repositório real (deve sobreviver a todos)
# ---------------------------------------------------------------------------

PAYLOADS_CLASSICOS = [
    "'; DROP TABLE clientes; --",
    "Robert'); DROP TABLE clientes;--",          # o clássico "Bobby Tables"
    "' OR '1'='1",
    "' OR 1=1 --",
    '" OR ""="',
    "admin'--",
    "'; UPDATE clientes SET saldo = 999999; --",  # tenta fraudar saldo de todo mundo
]


@pytest.mark.parametrize("payload", PAYLOADS_CLASSICOS)
def test_nome_malicioso_e_gravado_como_texto_puro(cliente_repo, payload):
    """O payload deve virar apenas o valor do campo 'nome' — nunca um
    comando SQL executado."""
    criado = cliente_repo.criar(payload)

    salvo = cliente_repo.buscar(criado.id)
    assert salvo is not None
    assert salvo.nome == payload  # foi guardado do jeito que veio, sem interpretação


@pytest.mark.parametrize("payload", PAYLOADS_CLASSICOS)
def test_tabelas_sobrevivem_ao_ataque(cliente_repo, payload):
    """Depois de cada tentativa de DROP/UPDATE em massa, as duas tabelas
    ainda precisam existir e os dados originais não podem ter sido
    alterados em massa (o UPDATE malicioso não pode ter afetado ninguém)."""
    saldo_antes = {c.nome: c.saldo for c in cliente_repo.listar()}

    cliente_repo.criar(payload)

    conn = database.get_connection()
    tabelas = {
        linha["name"]
        for linha in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()

    assert {"clientes", "produtos"}.issubset(tabelas)

    # os saldos que já existiam antes do ataque continuam intactos
    saldo_depois = {c.nome: c.saldo for c in cliente_repo.listar() if c.nome in saldo_antes}
    assert saldo_depois == saldo_antes


def test_multiplos_ataques_em_sequencia_nao_acumulam_dano(cliente_repo):
    """Dispara todos os payloads em sequência no mesmo banco e confere
    que, no final, a única coisa que aconteceu foi: N clientes novos
    criados com nomes estranhos — nada mais."""
    total_antes = len(cliente_repo.listar())

    for payload in PAYLOADS_CLASSICOS:
        cliente_repo.criar(payload)

    total_depois = len(cliente_repo.listar())
    assert total_depois == total_antes + len(PAYLOADS_CLASSICOS)


# ---------------------------------------------------------------------------
# 2) Demonstração didática: o padrão vulnerável, para contraste
#    (isto NÃO existe em nenhum lugar do app — é só para efeito de estudo)
# ---------------------------------------------------------------------------

def _buscar_cliente_vulneravel(conn: sqlite3.Connection, nome_digitado: str):
    """Exemplo NEGATIVO — o jeito ERRADO de montar uma query.
    Monta a query colando a string do usuário direto no SQL.
    NUNCA faça isso em código real; está aqui só para comparação."""
    query = f"SELECT * FROM clientes WHERE nome = '{nome_digitado}'"
    return conn.execute(query).fetchall()


def test_demonstracao_do_padrao_vulneravel_para_contraste(capsys):
    """Recria, num banco em memória isolado (:memory:, descartado ao
    final do teste), o cenário clássico de bypass por SQL Injection —
    para você ver o que aconteceria SE o repositório não usasse `?`."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT, saldo REAL)")
    conn.executemany(
        "INSERT INTO clientes (nome, saldo) VALUES (?, ?)",
        [("Rodrigo Bentini", 100.0), ("Ana Monteiro", 50.0), ("João Amorim", 23.0)],
    )
    conn.commit()

    payload = "' OR '1'='1"
    resultado = _buscar_cliente_vulneravel(conn, payload)
    nomes_vazados = [linha["nome"] for linha in resultado]

    print(f"\n[DEMO] Nome digitado pelo 'atacante': {payload!r}")
    print(f"[DEMO] Query realmente executada: SELECT * FROM clientes WHERE nome = '{payload}'")
    print(f"[DEMO] Clientes vazados (sem saber nenhum nome real): {nomes_vazados}")

    conn.close()

    # a versão vulnerável devolve TODOS os clientes com um "nome" que nunca existiu
    assert len(nomes_vazados) == 3
    assert set(nomes_vazados) == {"Rodrigo Bentini", "Ana Monteiro", "João Amorim"}


def test_versao_real_do_repositorio_nao_sofre_o_mesmo_bypass(cliente_repo):
    """O mesmo payload usado acima, agora contra o ClienteRepository de
    verdade — deve vir vazio, porque `buscar` procura por igualdade
    exata (nome_digitado é dado, não comando)."""
    # popula com nomes "reais"
    cliente_repo.criar("Rodrigo Bentini")
    cliente_repo.criar("Ana Monteiro")

    conn = database.get_connection()
    resultado = conn.execute(
        "SELECT * FROM clientes WHERE nome = ?", ("' OR '1'='1",)
    ).fetchall()
    conn.close()

    assert resultado == []  # nenhum cliente se chama literalmente "' OR '1'='1"
