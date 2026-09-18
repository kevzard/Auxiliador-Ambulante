"""Tela 1 — Lista de clientes (equivalente a index.html no protótipo).

Esta função não desenha nada sozinha: ela chama os componentes prontos
(ui.components) e os modais prontos (ui.modals), e só cuida de "amarrar"
tudo com o repositório de clientes. Se um dia o layout do card mudar, mexe
em ui/components.py; se a regra de recarga mudar, mexe aqui.
"""

from typing import Callable

import flet as ft

from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository
from ui.components import criar_card_cliente
from ui.modals import (
    criar_modal_confirmar_exclusao_cliente,
    criar_modal_editar_cliente,
    criar_modal_novo_cliente,
    criar_modal_recarga,
)
from ui.theme import AZUL, AZUL_CLARO, CINZA_FUNDO


def montar_tela_clientes(
    page: ft.Page,
    cliente_repo: ClienteRepository,
    ao_realizar_venda: Callable[[Cliente], None],
    ao_abrir_produtos: Callable[[], None],
) -> Callable[[], None]:
    """Prepara a tela e retorna a função `montar()` que a exibe.

    Mantida como uma função retornada (em vez de já montar de cara) para
    que main.py decida QUANDO trocar de tela — por exemplo, para poder
    remontá-la depois de voltar de uma venda.
    """

    lista_col = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    def atualizar_lista():
        clientes = cliente_repo.listar()
        lista_col.controls = [
            criar_card_cliente(
                cliente,
                page,
                ao_realizar_venda=ao_realizar_venda,
                ao_recarregar=lambda c: abrir_modal_recarga(c),
                ao_editar=lambda c: abrir_modal_editar(c),
                ao_excluir=lambda c: abrir_modal_excluir(c),
            )
            for cliente in clientes
        ]
        page.update()

    def novo_cliente_confirmado(nome: str):
        cliente_repo.criar(nome)
        atualizar_lista()

    def recarga_confirmada(cliente_id: int, valor: float):
        cliente = cliente_repo.buscar(cliente_id)
        novo_saldo = round(cliente.saldo + valor, 2)
        cliente_repo.atualizar_saldo(cliente_id, novo_saldo)
        atualizar_lista()

    def edicao_confirmada(cliente_id: int, novo_nome: str):
        cliente_repo.atualizar_nome(cliente_id, novo_nome)
        atualizar_lista()

    def exclusao_confirmada(cliente_id: int):
        cliente_repo.deletar(cliente_id)
        atualizar_lista()

    _, abrir_modal_novo_cliente = criar_modal_novo_cliente(
        page, on_confirmar=novo_cliente_confirmado
    )
    _, abrir_modal_recarga = criar_modal_recarga(page, on_confirmar=recarga_confirmada)
    _, abrir_modal_editar = criar_modal_editar_cliente(page, on_confirmar=edicao_confirmada)
    _, abrir_modal_excluir = criar_modal_confirmar_exclusao_cliente(
        page, on_confirmar=exclusao_confirmada
    )

    topbar = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.MENU, color="white"),
                    on_click=lambda e: ao_abrir_produtos(),
                    ink=True,
                    border_radius=ft.BorderRadius.all(20),
                    padding=8,
                ),
                ft.Row(
                    [
                        ft.Text("Adm.", color="white", size=15, weight=ft.FontWeight.W_500),
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color="white", size=17),
                            bgcolor="#4DFFFFFF",
                            radius=16,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
            on_click=lambda e: abrir_modal_novo_cliente(),
        )
        page.update()

    return montar
