"""Testes do CRUD de clientes (ClienteRepository).

Cobre as 4 operações: criar (Create), listar/buscar (Read),
atualizar_nome/atualizar_saldo (Update) e deletar (Delete).

Roda com: python -m pytest tests/test_cliente_repository.py -v
"""

import pytest

import database
from repositories.cliente_repository import ClienteRepository


@pytest.fixture
def cliente_repo(tmp_path, monkeypatch) -> ClienteRepository:
    """Banco SQLite temporário e isolado por teste — nunca toca no
    vendaaz.db real do projeto."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "teste_crud.db")
    database.init_db()
    return ClienteRepository()


# --- Create ---------------------------------------------------------------

def test_criar_cliente_com_saldo_zero(cliente_repo):
    cliente = cliente_repo.criar("Fulano de Tal")

    assert cliente.id is not None
    assert cliente.nome == "Fulano de Tal"
    assert cliente.saldo == 0.0


# --- Read -------------------------------------------------------------

def test_listar_inclui_os_padrao_e_os_criados(cliente_repo):
    total_inicial = len(cliente_repo.listar())  # os 3 clientes padrão do seed

    cliente_repo.criar("Novo Cliente")

    clientes = cliente_repo.listar()
    assert len(clientes) == total_inicial + 1
    assert any(c.nome == "Novo Cliente" for c in clientes)


def test_buscar_por_id_encontra_o_cliente_certo(cliente_repo):
    criado = cliente_repo.criar("Cliente Buscado")

    encontrado = cliente_repo.buscar(criado.id)

    assert encontrado is not None
    assert encontrado.nome == "Cliente Buscado"


def test_buscar_id_inexistente_retorna_none(cliente_repo):
    assert cliente_repo.buscar(99999) is None


# --- Update -----------------------------------------------------------

def test_atualizar_nome_corrige_o_cadastro(cliente_repo):
    criado = cliente_repo.criar("Nome com Erro de Digitação")

    cliente_repo.atualizar_nome(criado.id, "Nome Corrigido")

    atualizado = cliente_repo.buscar(criado.id)
    assert atualizado.nome == "Nome Corrigido"


def test_atualizar_saldo_reflete_na_leitura(cliente_repo):
    criado = cliente_repo.criar("Cliente com Recarga")

    cliente_repo.atualizar_saldo(criado.id, 42.50)

    atualizado = cliente_repo.buscar(criado.id)
    assert atualizado.saldo == 42.50


# --- Delete -----------------------------------------------------------

def test_deletar_remove_o_cliente(cliente_repo):
    criado = cliente_repo.criar("Cliente a ser removido")
    total_antes = len(cliente_repo.listar())

    cliente_repo.deletar(criado.id)

    assert cliente_repo.buscar(criado.id) is None
    assert len(cliente_repo.listar()) == total_antes - 1


def test_deletar_um_cliente_nao_afeta_os_outros(cliente_repo):
    a = cliente_repo.criar("Cliente A")
    b = cliente_repo.criar("Cliente B")

    cliente_repo.deletar(a.id)

    assert cliente_repo.buscar(a.id) is None
    assert cliente_repo.buscar(b.id) is not None
    assert cliente_repo.buscar(b.id).nome == "Cliente B"
