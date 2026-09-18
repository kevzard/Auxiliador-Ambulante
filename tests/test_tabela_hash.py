"""Testes do TAD TabelaHash, isolados de qualquer regra de carrinho.

Roda com: python -m pytest tests/test_tabela_hash.py -v
"""

from estruturas_dados.tabela_hash import TabelaHash


def test_tabela_comeca_vazia():
    tabela = TabelaHash()
    assert len(tabela) == 0
    assert tabela.buscar("qualquer") is None
    assert tabela.contem("qualquer") is False


def test_inserir_e_buscar():
    tabela = TabelaHash()
    tabela.inserir("pacoca", 1.0)

    assert len(tabela) == 1
    assert tabela.buscar("pacoca") == 1.0
    assert tabela.contem("pacoca") is True


def test_inserir_mesma_chave_atualiza_em_vez_de_duplicar():
    tabela = TabelaHash()
    tabela.inserir("pacoca", 1.0)
    tabela.inserir("pacoca", 2.5)  # mesma chave, valor novo

    assert len(tabela) == 1
    assert tabela.buscar("pacoca") == 2.5


def test_remover_uma_chave_nao_afeta_as_outras():
    tabela = TabelaHash()
    tabela.inserir("pacoca", 1.0)
    tabela.inserir("balas", 2.5)

    tabela.remover("pacoca")

    assert tabela.contem("pacoca") is False
    assert tabela.buscar("balas") == 2.5
    assert len(tabela) == 1


def test_remover_chave_inexistente_nao_da_erro():
    tabela = TabelaHash()
    tabela.remover("nao existe")  # não deve lançar exceção
    assert len(tabela) == 0


def test_valores_traz_tudo_que_foi_inserido():
    tabela = TabelaHash()
    for i in range(5):
        tabela.inserir(i, f"item-{i}")

    valores = tabela.valores()
    assert sorted(valores) == [f"item-{i}" for i in range(5)]


def test_limpar_esvazia_a_tabela():
    tabela = TabelaHash()
    tabela.inserir("a", 1)
    tabela.inserir("b", 2)

    tabela.limpar()

    assert len(tabela) == 0
    assert tabela.valores() == []


# --- Colisão forçada -------------------------------------------------------

class _ChaveComHashFixo:
    """Toda instância dessa classe cai no MESMO índice da tabela,
    de propósito — para testar se o encadeamento separado realmente
    resolve colisões (em vez de uma chave sobrescrever a outra)."""

    def __init__(self, valor: str):
        self.valor = valor

    def __hash__(self) -> int:
        return 42  # sempre o mesmo hash, força colisão

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _ChaveComHashFixo) and self.valor == other.valor


def test_colisao_e_resolvida_por_encadeamento():
    tabela = TabelaHash()
    chave_a = _ChaveComHashFixo("a")
    chave_b = _ChaveComHashFixo("b")
    chave_c = _ChaveComHashFixo("c")

    tabela.inserir(chave_a, "valor de A")
    tabela.inserir(chave_b, "valor de B")
    tabela.inserir(chave_c, "valor de C")

    # as três foram parar no mesmo índice (hash sempre 42) — mesmo assim,
    # cada uma tem que devolver o valor certo
    assert tabela.buscar(chave_a) == "valor de A"
    assert tabela.buscar(chave_b) == "valor de B"
    assert tabela.buscar(chave_c) == "valor de C"
    assert len(tabela) == 3


def test_remover_uma_chave_colidida_preserva_as_outras():
    tabela = TabelaHash()
    chave_a = _ChaveComHashFixo("a")
    chave_b = _ChaveComHashFixo("b")
    tabela.inserir(chave_a, "valor de A")
    tabela.inserir(chave_b, "valor de B")

    tabela.remover(chave_a)

    assert tabela.contem(chave_a) is False
    assert tabela.buscar(chave_b) == "valor de B"


# --- Redimensionamento ------------------------------------------------------

def test_redimensiona_e_mantem_todos_os_dados_integros():
    tabela = TabelaHash()
    total_de_itens = 200  # bem mais que a capacidade inicial (8), força vários redimensionamentos

    for i in range(total_de_itens):
        tabela.inserir(i, i * 10)

    assert len(tabela) == total_de_itens
    for i in range(total_de_itens):
        assert tabela.buscar(i) == i * 10
