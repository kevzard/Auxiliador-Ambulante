"""Tela 2 — Venda de produtos (equivalente a venda.html no protótipo).

A lógica de "quanto custa, cabe no saldo, zera o carrinho" mora em
services/carrinho.py — aqui só existe orquestração: pega os produtos do
repositório, monta os cards, escuta os cliques e decide o que mostrar.
"""

from typing import Callable

import flet as ft

from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository
from repositories.produto_repository import ProdutoRepository
from services.carrinho import Carrinho
from ui.components import criar_card_produto
from ui.modals import (
    criar_modal_aviso,
    criar_modal_confirmar_cancelamento,
    criar_modal_sucesso,
)
from ui.theme import CINZA_FUNDO, VERDE, formatar_reais


def montar_tela_venda(
    page: ft.Page,
    cliente: Cliente,
    cliente_repo: ClienteRepository,
    produto_repo: ProdutoRepository,
    ao_voltar_para_clientes: Callable[[], None],
) -> Callable[[], None]:
    carrinho = Carrinho()
    badges: dict[int, ft.Text] = {}

    texto_saldo = ft.Text(formatar_reais(cliente.saldo), color="#CCFFFFFF", size=13)
    texto_total = ft.Text(formatar_reais(0), size=15, weight=ft.FontWeight.W_500)
    texto_itens = ft.Text("Nenhum item selecionado", size=13, color="#888888")

    def atualizar_resumo():
        texto_total.value = formatar_reais(carrinho.total())
        itens = [
            f"{item.produto.nome} x{item.quantidade}"
            for item in carrinho.itens_selecionados()
        ]
        texto_itens.value = ", ".join(itens) if itens else "Nenhum item selecionado"

    def alterar_quantidade(produto, delta):
        nova_qtd = carrinho.alterar_quantidade(produto, delta)
        badges[produto.id].value = str(nova_qtd)
        atualizar_resumo()
        page.update()

    grade_produtos = ft.GridView(
        runs_count=2,
        spacing=12,
        run_spacing=12,
        child_aspect_ratio=0.7,
        expand=True,
        padding=ft.Padding.only(left=16, right=16, top=16, bottom=16),
    )

    for produto in produto_repo.listar():
        badge = ft.Text("0", size=15, weight=ft.FontWeight.W_600)
        badges[produto.id] = badge
        grade_produtos.controls.append(
            criar_card_produto(produto, badge, alterar_quantidade)
        )

    _, abrir_modal_aviso = criar_modal_aviso(page)
    _, abrir_modal_sucesso = criar_modal_sucesso(
        page, on_continuar=ao_voltar_para_clientes
    )
    _, abrir_modal_cancelar = criar_modal_confirmar_cancelamento(
        page, on_confirmar=ao_voltar_para_clientes
    )

    def finalizar_pedido(e):
        total = carrinho.total()

        if carrinho.esta_vazio():
            abrir_modal_aviso(
                "Nenhum item selecionado.",
                "Adicione pelo menos um produto antes de finalizar.",
            )
            return

        if not carrinho.cabe_no_saldo(cliente.saldo):
            abrir_modal_aviso(
                "Saldo insuficiente.",
                "O valor total da compra ultrapassa o crédito disponível do cliente.",
            )
            return

        novo_saldo = round(cliente.saldo - total, 2)
        cliente_repo.atualizar_saldo(cliente.id, novo_saldo)
        cliente.saldo = novo_saldo
        texto_saldo.value = formatar_reais(novo_saldo)

        carrinho.limpar()
        for badge in badges.values():
            badge.value = "0"
        atualizar_resumo()

        abrir_modal_sucesso(total)

    topbar = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color="white", size=22),
                            bgcolor="#40FFFFFF",
                            radius=22,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    cliente.nome,
                                    color="white",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                ),
                                texto_saldo,
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Button(
                    "Cancelar venda",
                    bgcolor="white",
                    color="#333333",
                    on_click=lambda e: abrir_modal_cancelar(),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor="#2196F3",
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
    )

    barra_carrinho = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [ft.Text("Total", weight=ft.FontWeight.W_500), texto_total],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                texto_itens,
                ft.Button(
                    "Finalizar Pedido",
                    bgcolor=VERDE,
                    color="white",
                    on_click=finalizar_pedido,
                ),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        bgcolor="white",
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
        border=ft.Border.only(top=ft.BorderSide(0.5, "#E0E0E0")),
    )

    def montar():
        page.clean()
        page.add(
            topbar,
            ft.Container(content=grade_produtos, bgcolor=CINZA_FUNDO, expand=True),
            barra_carrinho,
        )
        page.floating_action_button = None
        page.update()

    return montar
