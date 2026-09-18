"""Componentes de UI reutilizáveis.

Cada função aqui monta UM pedacinho de interface e devolve um ft.Control
pronto. Elas não conhecem repositório nem banco — só recebem os dados já
prontos (Cliente, Produto) e callbacks para avisar a tela quando algo
acontece. Isso é o que permite reaproveitar, por exemplo, o card de
cliente em outra tela no futuro sem duplicar código.
"""

from typing import Callable

import flet as ft

from models.cliente import Cliente
from models.produto import Produto
from ui.theme import AZUL, CIANO, CINZA_BORDA, VERDE, VERMELHO, formatar_reais


def criar_botao_qtd(icone: str, on_click: Callable) -> ft.Container:
    """Botãozinho circular escuro usado para +/- quantidade nos produtos."""
    return ft.Container(
        content=ft.Icon(icone, color="white", size=18),
        width=36,
        height=36,
        border_radius=ft.BorderRadius.all(18),
        bgcolor="#222222",
        alignment=ft.Alignment.CENTER,
        on_click=on_click,
        ink=True,
    )


def criar_card_cliente(
    cliente: Cliente,
    page: ft.Page,
    ao_realizar_venda: Callable[[Cliente], None],
    ao_recarregar: Callable[[Cliente], None],
    ao_editar: Callable[[Cliente], None],
    ao_excluir: Callable[[Cliente], None],
) -> ft.Container:
    """Card expansível da lista de clientes: toque para abrir/fechar as
    ações (venda, recarga, editar, excluir — o CRUD inteiro num só lugar)."""

    acoes = ft.Column(
        [
            ft.Row(
                [
                    ft.Button(
                        "Realizar venda",
                        bgcolor=VERDE,
                        color="white",
                        on_click=lambda e: ao_realizar_venda(cliente),
                        expand=1,
                    ),
                    ft.Button(
                        "Recarregar carteira",
                        bgcolor=CIANO,
                        color="white",
                        on_click=lambda e: ao_recarregar(cliente),
                        expand=1,
                    ),
                ],
                spacing=10,
            ),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Editar",
                        on_click=lambda e: ao_editar(cliente),
                        expand=1,
                    ),
                    ft.Button(
                        "Excluir",
                        bgcolor=VERMELHO,
                        color="white",
                        on_click=lambda e: ao_excluir(cliente),
                        expand=1,
                    ),
                ],
                spacing=10,
            ),
        ],
        spacing=10,
        visible=False,
    )

    linha_principal = ft.Row(
        [
            ft.CircleAvatar(
                content=ft.Icon(ft.Icons.PERSON, color="#AAAAAA", size=18),
                bgcolor=CINZA_BORDA,
                radius=18,
            ),
            ft.Text(cliente.nome, size=15, color="#222222", expand=True),
            ft.Text(formatar_reais(cliente.saldo), size=14, color="#444444"),
        ],
        spacing=12,
    )

    def alternar(e):
        acoes.visible = not acoes.visible
        page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=linha_principal,
                    padding=ft.Padding.symmetric(vertical=14, horizontal=16),
                    on_click=alternar,
                    ink=True,
                ),
                ft.Container(
                    content=acoes,
                    padding=ft.Padding.only(left=16, right=16, top=12, bottom=12),
                    border=ft.Border.only(top=ft.BorderSide(0.5, "#ECECEC")),
                ),
            ],
            spacing=0,
        ),
        bgcolor="white",
        border_radius=ft.BorderRadius.all(10),
        border=ft.Border.all(0.5, CINZA_BORDA),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )


def criar_seletor_imagem(
    page: ft.Page,
    imagens_disponiveis: list[str],
    imagem_inicial: str | None = None,
) -> tuple[ft.Control, Callable[[], str | None], Callable[[str], None]]:
    """Grade horizontal de miniaturas clicáveis para escolher a imagem do
    produto entre as que já existem em img/ — o app não tem upload de
    imagem, só reaproveita fotos que já estão no projeto.

    Retorna (controle_visual, obter_selecionada, selecionar):
        - `controle_visual` é o que a tela/modal deve colocar no layout;
        - `obter_selecionada()` devolve o nome do arquivo escolhido agora;
        - `selecionar(nome_arquivo)` marca uma miniatura como escolhida
          (usado para pré-selecionar a imagem atual ao editar um produto).
    """
    estado = {"selecionada": imagem_inicial}
    miniaturas: dict[str, ft.Container] = {}

    def borda_para(nome_arquivo: str) -> ft.Border:
        selecionada = estado["selecionada"] == nome_arquivo
        cor = AZUL if selecionada else CINZA_BORDA
        largura = 3 if selecionada else 1
        return ft.Border.all(largura, cor)

    def selecionar(nome_arquivo: str) -> None:
        anterior = estado["selecionada"]
        estado["selecionada"] = nome_arquivo
        if anterior in miniaturas:
            miniaturas[anterior].border = borda_para(anterior)
        if nome_arquivo in miniaturas:
            miniaturas[nome_arquivo].border = borda_para(nome_arquivo)
        page.update()

    itens = []
    for nome_arquivo in imagens_disponiveis:
        miniatura = ft.Container(
            content=ft.Image(src=nome_arquivo, width=64, height=64, fit=ft.BoxFit.COVER),
            width=68,
            height=68,
            border=borda_para(nome_arquivo),
            border_radius=ft.BorderRadius.all(8),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            on_click=lambda e, n=nome_arquivo: selecionar(n),
            ink=True,
        )
        miniaturas[nome_arquivo] = miniatura
        itens.append(miniatura)

    controle = ft.Row(itens, spacing=8, scroll=ft.ScrollMode.AUTO)

    def obter_selecionada() -> str | None:
        return estado["selecionada"]

    return controle, obter_selecionada, selecionar


def criar_card_produto_admin(
    produto: Produto,
    page: ft.Page,
    ao_editar: Callable[[Produto], None],
    ao_excluir: Callable[[Produto], None],
) -> ft.Container:
    """Card de produto na tela de gerenciamento (CRUD): miniatura, nome e
    preço numa linha; toque para abrir Editar/Excluir — mesmo padrão de
    interação do card de cliente, pra manter o app consistente."""

    acoes = ft.Row(
        [
            ft.OutlinedButton("Editar", on_click=lambda e: ao_editar(produto), expand=1),
            ft.Button(
                "Excluir",
                bgcolor=VERMELHO,
                color="white",
                on_click=lambda e: ao_excluir(produto),
                expand=1,
            ),
        ],
        spacing=10,
        visible=False,
    )

    linha_principal = ft.Row(
        [
            ft.Container(
                content=ft.Image(src=produto.imagem, width=44, height=44, fit=ft.BoxFit.COVER),
                width=44,
                height=44,
                border_radius=ft.BorderRadius.all(8),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            ft.Text(produto.nome, size=15, color="#222222", expand=True),
            ft.Text(formatar_reais(produto.preco), size=14, color="#444444"),
        ],
        spacing=12,
    )

    def alternar(e):
        acoes.visible = not acoes.visible
        page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=linha_principal,
                    padding=ft.Padding.symmetric(vertical=14, horizontal=16),
                    on_click=alternar,
                    ink=True,
                ),
                ft.Container(
                    content=acoes,
                    padding=ft.Padding.only(left=16, right=16, top=12, bottom=12),
                    border=ft.Border.only(top=ft.BorderSide(0.5, "#ECECEC")),
                ),
            ],
            spacing=0,
        ),
        bgcolor="white",
        border_radius=ft.BorderRadius.all(10),
        border=ft.Border.all(0.5, CINZA_BORDA),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )


def criar_card_produto(
    produto: Produto,
    badge_quantidade: ft.Text,
    ao_alterar_quantidade: Callable[[Produto, int], None],
) -> ft.Container:
    """Card de produto na grade da tela de venda: imagem, nome, preço e
    os botões +/- de quantidade.

    `badge_quantidade` é criado pela tela (views/tela_venda.py), que
    precisa manter uma referência para atualizar o número depois — o
    componente só recebe e posiciona esse Text, não é dono dele.
    """
    return ft.Container(
        content=ft.Column(
            [
                ft.Image(src=produto.imagem, height=110, fit=ft.BoxFit.COVER),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(produto.nome, size=14, color="#333333"),
                            ft.Row(
                                [
                                    ft.Text(
                                        formatar_reais(produto.preco),
                                        color=AZUL,
                                        weight=ft.FontWeight.W_500,
                                        size=15,
                                    ),
                                    ft.Row(
                                        [
                                            criar_botao_qtd(
                                                ft.Icons.REMOVE,
                                                lambda e, p=produto: ao_alterar_quantidade(p, -1),
                                            ),
                                            badge_quantidade,
                                            criar_botao_qtd(
                                                ft.Icons.ADD,
                                                lambda e, p=produto: ao_alterar_quantidade(p, 1),
                                            ),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding.only(left=12, right=12, top=10, bottom=12),
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        bgcolor="white",
        border_radius=ft.BorderRadius.all(12),
        border=ft.Border.all(0.5, CINZA_BORDA),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )
