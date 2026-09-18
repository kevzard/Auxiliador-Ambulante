"""Regras de negócio do carrinho de compras.

Por baixo, o carrinho guarda os itens numa TabelaHash própria
(estruturas_dados/tabela_hash.py) em vez do dict nativo do Python —
essa troca é justamente a "Estrutura de Dados como base" pedida para
esta etapa. A interface pública da classe (alterar_quantidade, total,
itens_selecionados, esta_vazio, cabe_no_saldo, limpar) não mudou em nada,
então nenhuma tela precisou ser tocada: é a modularização em camadas
compensando — trocar a estrutura interna de dados é um detalhe só desta
classe.

Este arquivo também não importa nem Flet nem SQLite: só sabe somar
preços e validar quantidades. Isso permite escrever um teste automatizado
direto (`python -m pytest tests/test_carrinho.py`) sem precisar simular
tela nenhuma — útil na hora de defender a qualidade do código no TCC.
"""

from dataclasses import dataclass

from estruturas_dados.tabela_hash import TabelaHash
from models.produto import Produto


@dataclass
class ItemCarrinho:
    produto: Produto
    quantidade: int = 0

    @property
    def subtotal(self) -> float:
        return self.produto.preco * self.quantidade


class Carrinho:
    def __init__(self) -> None:
        # chave: produto.id -> valor: ItemCarrinho
        self._itens: TabelaHash[int, ItemCarrinho] = TabelaHash()

    def alterar_quantidade(self, produto: Produto, delta: int) -> int:
        """Soma `delta` à quantidade do produto (pode ser negativo).
        Nunca deixa a quantidade ficar negativa. Retorna a nova quantidade."""
        item = self._itens.buscar(produto.id)
        if item is None:
            item = ItemCarrinho(produto=produto)

        nova_quantidade = item.quantidade + delta
        if nova_quantidade < 0:
            return item.quantidade

        item.quantidade = nova_quantidade
        self._itens.inserir(produto.id, item)
        return item.quantidade

    def total(self) -> float:
        return sum(item.subtotal for item in self._itens.valores())

    def itens_selecionados(self) -> list[ItemCarrinho]:
        """Só os itens com quantidade > 0 — usado para montar o resumo na tela."""
        return [item for item in self._itens.valores() if item.quantidade > 0]

    def esta_vazio(self) -> bool:
        return self.total() == 0

    def cabe_no_saldo(self, saldo_disponivel: float) -> bool:
        return self.total() <= saldo_disponivel

    def limpar(self) -> None:
        self._itens.limpar()
