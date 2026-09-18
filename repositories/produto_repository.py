"""Repositório de Produto."""

from pathlib import Path

from database import get_connection
from models.produto import Produto

_EXTENSOES_DE_IMAGEM = (".png", ".jpg", ".jpeg", ".webp")
_PASTA_IMG = Path(__file__).parent.parent / "img"


class ProdutoRepository:
    def listar(self) -> list[Produto]:
        conn = get_connection()
        linhas = conn.execute("SELECT * FROM produtos ORDER BY id").fetchall()
        conn.close()
        return [self._para_modelo(linha) for linha in linhas]

    def buscar(self, produto_id: int) -> Produto | None:
        conn = get_connection()
        linha = conn.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        conn.close()
        return self._para_modelo(linha) if linha else None

    def criar(self, nome: str, preco: float, imagem: str) -> Produto:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO produtos (nome, preco, imagem) VALUES (?, ?, ?)",
            (nome, preco, imagem),
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return Produto(id=novo_id, nome=nome, preco=preco, imagem=imagem)

    def atualizar(self, produto_id: int, nome: str, preco: float, imagem: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE produtos SET nome = ?, preco = ?, imagem = ? WHERE id = ?",
            (nome, preco, imagem, produto_id),
        )
        conn.commit()
        conn.close()

    def deletar(self, produto_id: int) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def listar_imagens_disponiveis() -> list[str]:
        """Lista os arquivos de imagem que já existem na pasta img/.

        O app não tem upload de imagem — ao criar/editar um produto, o
        usuário escolhe entre as fotos que já estão no projeto. Se um dia
        existir upload, é só trocar a implementação desta função."""
        if not _PASTA_IMG.exists():
            return []
        return sorted(
            arquivo.name
            for arquivo in _PASTA_IMG.iterdir()
            if arquivo.suffix.lower() in _EXTENSOES_DE_IMAGEM
        )

    @staticmethod
    def _para_modelo(linha) -> Produto:
        return Produto(id=linha["id"], nome=linha["nome"], preco=linha["preco"], imagem=linha["imagem"])
