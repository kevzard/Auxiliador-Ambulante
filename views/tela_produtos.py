"""Tela de gerenciamento de produtos (CRUD).

Mesmo padrão das outras telas: só orquestra repositório + componentes +
modais prontos. As imagens vêm sempre da pasta img/ (ProdutoRepository.
listar_imagens_disponiveis()) — não existe upload de imagem no app, o
cadastro/edição de produto escolhe entre as fotos que já estão no projeto.
"""

from typing import Callable

import flet as ft

from repositories.produto_repository import ProdutoRepository
from ui.components import criar_card_produto_admin
from ui.modals import (
    criar_modal_confirmar_exclusao_produto,
    criar_modal_editar_produto,
    criar_modal_novo_produto,
)
from ui.theme import AZUL, AZUL_CLARO, CINZA_FUNDO


def montar_tela_produtos(
    page: ft.Page,
    produto_repo: ProdutoRepository,
    ao_voltar: Callable[[], None],
) -> Callable[[], None]:
    lista_col = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    def atualizar_lista():
        produtos = produto_repo.listar()
        lista_col.controls = [
            criar_card_produto_admin(
                produto,
                page,
                ao_editar=lambda p: abrir_modal_editar(p),
                ao_excluir=lambda p: abrir_modal_excluir(p),
            )
            for produto in produtos
        ]
        page.update()

    def novo_produto_confirmado(nome: str, preco: float, imagem: str):
        produto_repo.criar(nome, preco, imagem)
        atualizar_lista()

    def edicao_confirmada(produto_id: int, nome: str, preco: float, imagem: str):
        produto_repo.atualizar(produto_id, nome, preco, imagem)
        atualizar_lista()

    def exclusao_confirmada(produto_id: int):
        produto_repo.deletar(produto_id)
        atualizar_lista()

    _, abrir_modal_novo_produto = criar_modal_novo_produto(
        page,
        on_confirmar=novo_produto_confirmado,
        imagens_disponiveis=produto_repo.listar_imagens_disponiveis,
    )
    _, abrir_modal_editar = criar_modal_editar_produto(
        page,
        on_confirmar=edicao_confirmada,
        imagens_disponiveis=produto_repo.listar_imagens_disponiveis,
    )
    _, abrir_modal_excluir = criar_modal_confirmar_exclusao_produto(
        page, on_confirmar=exclusao_confirmada
    )

    topbar = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_BACK, color="white"),
                    on_click=lambda e: ao_voltar(),
                    ink=True,
                    border_radius=ft.BorderRadius.all(20),
                    padding=8,
                ),
                ft.Text("Produtos", color="white", size=18, weight=ft.FontWeight.W_500, expand=True),
            ],
            spacing=8,
        ),
        bgcolor=AZUL,
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
    )

    def montar():
        atualizar_lista()
        page.clean()
        page.add(
            topbar,
            ft.Container(content=lista_col, bgcolor=CINZA_FUNDO, padding=16, expand=True),
        )
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=AZUL_CLARO,
            on_click=lambda e: abrir_modal_novo_produto(),
        )
        page.update()

    return montar
