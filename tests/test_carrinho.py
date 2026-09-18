"""Testes do serviço de carrinho.

Roda com: python -m pytest tests/

Note que nenhum teste aqui abre uma Page do Flet nem toca no SQLite —
essa é a vantagem prática de ter isolado a regra de negócio em
services/carrinho.py: dá pra validar "a conta fecha certo" e "não deixa
vender sem saldo" com testes rápidos e sem interface nenhuma.
"""

from models.produto import Produto
from services.carrinho import Carrinho


def _produto(id=1, nome="Paçoca", preco=1.0, imagem="pacoca.png") -> Produto:
    return Produto(id=id, nome=nome, preco=preco, imagem=imagem)


def test_carrinho_comeca_vazio():
    carrinho = Carrinho()
    assert carrinho.esta_vazio()
    assert carrinho.total() == 0
    assert carrinho.itens_selecionados() == []


def test_alterar_quantidade_soma_ao_total():
    carrinho = Carrinho()
    paçoca = _produto(id=1, preco=1.0)

    carrinho.alterar_quantidade(paçoca, 1)
    carrinho.alterar_quantidade(paçoca, 1)
    carrinho.alterar_quantidade(paçoca, 1)

    assert carrinho.total() == 3.0
    assert not carrinho.esta_vazio()


def test_quantidade_nao_fica_negativa():
    carrinho = Carrinho()
    paçoca = _produto(id=1, preco=1.0)

    nova_qtd = carrinho.alterar_quantidade(paçoca, -1)

    assert nova_qtd == 0
    assert carrinho.esta_vazio()


def test_dois_produtos_diferentes_somam_no_total():
    carrinho = Carrinho()
    paçoca = _produto(id=1, nome="Paçoca", preco=1.0)
    balas = _produto(id=2, nome="Balas Fini", preco=2.5)

    carrinho.alterar_quantidade(paçoca, 2)  # 2 x 1,00 = 2,00
    carrinho.alterar_quantidade(balas, 1)  # 1 x 2,50 = 2,50

    assert carrinho.total() == 4.5
    nomes = {item.produto.nome for item in carrinho.itens_selecionados()}
    assert nomes == {"Paçoca", "Balas Fini"}


def test_cabe_no_saldo():
    carrinho = Carrinho()
    paçoca = _produto(id=1, preco=1.0)
    carrinho.alterar_quantidade(paçoca, 5)  # total = 5.0

    assert carrinho.cabe_no_saldo(5.0) is True
    assert carrinho.cabe_no_saldo(4.99) is False


def test_limpar_zera_o_carrinho():
    carrinho = Carrinho()
    paçoca = _produto(id=1, preco=1.0)
    carrinho.alterar_quantidade(paçoca, 3)

    carrinho.limpar()

    assert carrinho.esta_vazio()
    assert carrinho.total() == 0
