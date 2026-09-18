"""Repositório de Cliente.

Isola todo o SQL relacionado a clientes num único lugar. Se amanhã o
critério de busca mudar, ou o banco trocar de SQLite para outra coisa,
só este arquivo precisa ser tocado — nenhuma tela ou serviço depende de SQL.
"""

from database import get_connection
from models.cliente import Cliente


class ClienteRepository:
    def listar(self) -> list[Cliente]:
        conn = get_connection()
        linhas = conn.execute("SELECT * FROM clientes ORDER BY id").fetchall()
        conn.close()
        return [self._para_modelo(linha) for linha in linhas]

    def buscar(self, cliente_id: int) -> Cliente | None:
        conn = get_connection()
        linha = conn.execute(
            "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
        conn.close()
        return self._para_modelo(linha) if linha else None

    def criar(self, nome: str) -> Cliente:
        """Cria um cliente novo com saldo inicial zero e retorna o objeto criado."""
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO clientes (nome, saldo) VALUES (?, 0)", (nome,)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return Cliente(id=novo_id, nome=nome, saldo=0.0)

    def atualizar_saldo(self, cliente_id: int, novo_saldo: float) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE clientes SET saldo = ? WHERE id = ?", (novo_saldo, cliente_id)
        )
        conn.commit()
        conn.close()

    def atualizar_nome(self, cliente_id: int, novo_nome: str) -> None:
        """Corrige/edita o nome de um cliente já cadastrado (o 'U' do CRUD
        que faltava — atualizar_saldo cobre só o caso da recarga)."""
        conn = get_connection()
        conn.execute(
            "UPDATE clientes SET nome = ? WHERE id = ?", (novo_nome, cliente_id)
        )
        conn.commit()
        conn.close()

    def deletar(self, cliente_id: int) -> None:
        """Remove um cliente definitivamente. Não há tabela de vendas
        vinculada ainda, então não existe risco de deixar registro órfão."""
        conn = get_connection()
        conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def _para_modelo(linha) -> Cliente:
        return Cliente(id=linha["id"], nome=linha["nome"], saldo=linha["saldo"])
