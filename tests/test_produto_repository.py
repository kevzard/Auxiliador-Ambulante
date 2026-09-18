"""Testes do CRUD de produtos (ProdutoRepository).

Roda com: python -m pytest tests/test_produto_repository.py -v
"""

import pytest

import database
from repositories.produto_repository import ProdutoRepository


@pytest.fixture
def produto_repo(tmp_path, monkeypatch) -> ProdutoRepository:
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "teste_produtos.db")
    database.init_db()
    return ProdutoRepository()


# --- Create -----------------------------------------------------------

def test_criar_produto(produto_repo):
    produto = produto_repo.criar("Chiclete de Melancia", 2.0, "chicletes-mentos.png")

    assert produto.id is not None
    assert produto.nome == "Chiclete de Melancia"
    assert produto.preco == 2.0
    assert produto.imagem == "chicletes-mentos.png"


# --- Read ---------------------------------------------------------------

def test_listar_inclui_os_padrao_e_os_criados(produto_repo):
    total_inicial = len(produto_repo.listar())  # os 7 produtos padrão do seed

    produto_repo.criar("Novo Doce", 1.5, "pacoca.png")

    produtos = produto_repo.listar()
    assert len(produtos) == total_inicial + 1
    assert any(p.nome == "Novo Doce" for p in produtos)


def test_buscar_por_id(produto_repo):
    criado = produto_repo.criar("Bala Extra", 1.0, "balas-fini.png")

    encontrado = produto_repo.buscar(criado.id)

    assert encontrado is not None
    assert encontrado.nome == "Bala Extra"


def test_buscar_id_inexistente_retorna_none(produto_repo):
    assert produto_repo.buscar(99999) is None


# --- Update -----------------------------------------------------------

def test_atualizar_produto_troca_nome_preco_e_imagem(produto_repo):
    criado = produto_repo.criar("Nome Errado", 1.0, "pacoca.png")

    produto_repo.atualizar(criado.id, "Nome Certo", 5.5, "balas-mentos.png")

    atualizado = produto_repo.buscar(criado.id)
    assert atualizado.nome == "Nome Certo"
    assert atualizado.preco == 5.5
    assert atualizado.imagem == "balas-mentos.png"


# --- Delete -----------------------------------------------------------

def test_deletar_remove_o_produto(produto_repo):
    criado = produto_repo.criar("Produto Descontinuado", 1.0, "pacoca.png")
    total_antes = len(produto_repo.listar())

    produto_repo.deletar(criado.id)

    assert produto_repo.buscar(criado.id) is None
    assert len(produto_repo.listar()) == total_antes - 1


def test_deletar_um_produto_nao_afeta_os_outros(produto_repo):
    a = produto_repo.criar("Produto A", 1.0, "pacoca.png")
    b = produto_repo.criar("Produto B", 2.0, "balas-fini.png")

    produto_repo.deletar(a.id)

    assert produto_repo.buscar(a.id) is None
    assert produto_repo.buscar(b.id) is not None
    assert produto_repo.buscar(b.id).nome == "Produto B"


# --- Imagens disponíveis (pasta img/) ----------------------------------

def test_listar_imagens_disponiveis_encontra_as_fotos_do_projeto(produto_repo):
    imagens = ProdutoRepository.listar_imagens_disponiveis()

    assert "pacoca.png" in imagens
    assert "pe-de-moca.png" in imagens
    assert all(nome.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) for nome in imagens)
