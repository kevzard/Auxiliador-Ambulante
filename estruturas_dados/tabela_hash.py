"""
TAD (Tipo Abstrato de Dados) Tabela Hash.

Implementação própria — não usa dict do Python por baixo dos panos —
com tratamento de colisão por encadeamento separado (separate chaining)
e redimensionamento automático quando o fator de carga fica alto.

Por que essa estrutura foi escolhida para o carrinho (services/carrinho.py):
a operação mais frequente do carrinho é "dado um produto, ache/atualize a
quantidade dele" — o usuário pode clicar +/- em qualquer produto, em
qualquer ordem, não necessariamente na ordem que foi adicionado ao
carrinho. Isso é o cenário clássico de acesso por chave, onde uma tabela
hash dá busca/inserção/remoção em tempo médio O(1), independente de
quantos produtos estejam no carrinho.

Comparando com as alternativas:
    - Pilha / Fila: só dão acesso a uma ponta (topo / início). Achar um
      produto específico no meio exigiria "desmontar" a estrutura
      inteira, O(n) — não faz sentido para editar quantidades livremente.
    - Lista / Lista Ligada simples: buscar um produto é O(n), percorrendo
      item por item até achar o id procurado.
    - Árvore binária de busca: O(log n), melhor que lista, mas exige
      manter a árvore balanceada e uma chave ordenável — complexidade
      desnecessária para este problema.
    - Tabela Hash: O(1) em média para buscar, inserir e remover por
      chave. É a que melhor casa com o padrão de acesso do carrinho.
"""

from typing import Generic, Hashable, Optional, TypeVar

Chave = TypeVar("Chave", bound=Hashable)
Valor = TypeVar("Valor")


class _Nodo(Generic[Chave, Valor]):
    """Um elo da lista encadeada usada dentro de cada "balde" da tabela
    (é assim que o encadeamento separado resolve colisões: em vez de
    sobrescrever, empilha os itens que colidiram numa lista ligada)."""

    __slots__ = ("chave", "valor", "proximo")

    def __init__(self, chave: Chave, valor: Valor):
        self.chave = chave
        self.valor = valor
        self.proximo: Optional["_Nodo[Chave, Valor]"] = None


class TabelaHash(Generic[Chave, Valor]):
    """Tabela hash genérica: inserir(chave, valor), buscar(chave),
    remover(chave), contem(chave), valores(), limpar().

    Cresce sozinha: quando o fator de carga (itens / capacidade) passa de
    75%, a capacidade dobra e todos os itens são redistribuídos — mesma
    estratégia usada pelo dict do próprio Python e pela maioria das
    implementações de mercado (Java HashMap, etc.).
    """

    _CAPACIDADE_INICIAL = 8
    _FATOR_DE_CARGA_MAXIMO = 0.75

    def __init__(self) -> None:
        self._capacidade = self._CAPACIDADE_INICIAL
        self._baldes: list[Optional[_Nodo[Chave, Valor]]] = [None] * self._capacidade
        self._quantidade = 0

    def __len__(self) -> int:
        return self._quantidade

    # --- API pública do TAD -------------------------------------------------

    def inserir(self, chave: Chave, valor: Valor) -> None:
        """Insere um par (chave, valor). Se a chave já existir, só
        atualiza o valor (não duplica)."""
        if (self._quantidade + 1) / self._capacidade >= self._FATOR_DE_CARGA_MAXIMO:
            self._redimensionar()

        indice = self._indice_para(chave)
        nodo = self._baldes[indice]
        while nodo is not None:
            if nodo.chave == chave:
                nodo.valor = valor
                return
            nodo = nodo.proximo

        novo_nodo = _Nodo(chave, valor)
        novo_nodo.proximo = self._baldes[indice]  # entra na frente da lista do balde
        self._baldes[indice] = novo_nodo
        self._quantidade += 1

    def buscar(self, chave: Chave) -> Optional[Valor]:
        """Retorna o valor associado à chave, ou None se não existir."""
        indice = self._indice_para(chave)
        nodo = self._baldes[indice]
        while nodo is not None:
            if nodo.chave == chave:
                return nodo.valor
            nodo = nodo.proximo
        return None

    def contem(self, chave: Chave) -> bool:
        return self._encontrar_nodo(chave) is not None

    def remover(self, chave: Chave) -> None:
        """Remove a chave, se existir. Não faz nada se não existir."""
        indice = self._indice_para(chave)
        nodo = self._baldes[indice]
        anterior: Optional[_Nodo[Chave, Valor]] = None
        while nodo is not None:
            if nodo.chave == chave:
                if anterior is None:
                    self._baldes[indice] = nodo.proximo
                else:
                    anterior.proximo = nodo.proximo
                self._quantidade -= 1
                return
            anterior = nodo
            nodo = nodo.proximo

    def valores(self) -> list[Valor]:
        """Todos os valores guardados, em nenhuma ordem garantida
        (características normais de uma tabela hash)."""
        resultado: list[Valor] = []
        for balde in self._baldes:
            nodo = balde
            while nodo is not None:
                resultado.append(nodo.valor)
                nodo = nodo.proximo
        return resultado

    def limpar(self) -> None:
        self._capacidade = self._CAPACIDADE_INICIAL
        self._baldes = [None] * self._capacidade
        self._quantidade = 0

    # --- mecanismo interno ---------------------------------------------------

    def _indice_para(self, chave: Chave) -> int:
        """A função de hash propriamente dita: usa o hash nativo do
        Python (que já é bem distribuído) e reduz ao tamanho da tabela
        com módulo — a parte clássica de qualquer tabela hash."""
        return hash(chave) % self._capacidade

    def _encontrar_nodo(self, chave: Chave) -> Optional[_Nodo[Chave, Valor]]:
        nodo = self._baldes[self._indice_para(chave)]
        while nodo is not None:
            if nodo.chave == chave:
                return nodo
            nodo = nodo.proximo
        return None

    def _redimensionar(self) -> None:
        """Dobra a capacidade e reinsere todo mundo (os índices mudam,
        já que dependem do módulo pela capacidade)."""
        nodos_antigos = [nodo for balde in self._baldes for nodo in self._percorrer_balde(balde)]

        self._capacidade *= 2
        self._baldes = [None] * self._capacidade
        self._quantidade = 0
        for nodo in nodos_antigos:
            self.inserir(nodo.chave, nodo.valor)

    @staticmethod
    def _percorrer_balde(balde: Optional[_Nodo[Chave, Valor]]):
        nodo = balde
        while nodo is not None:
            yield nodo
            nodo = nodo.proximo
