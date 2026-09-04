"""
main.py
Vendaaz — app do vendedor ambulante (MVP).

Conversão do protótipo em HTML + CSS + JS (index.html / venda.html) para
Python + Flet + SQLite, seguindo os diagramas de atividade:
- Cadastro de clientes
- Venda de produtos
- Recarga da carteirinha

Observação sobre a versão do Flet:
Este arquivo usa a API do Flet 1.0 (>= 0.80), que mudou em alguns pontos
importantes em relação a tutoriais mais antigos que você possa encontrar
por aí:
    - ft.run(main, ...)                  em vez de ft.app(target=main, ...)
    - page.show_dialog(dlg) / page.pop_dialog()   em vez de page.open()/page.close()
    - ft.Padding.symmetric(...), ft.Border.all(...), ft.BorderRadius.all(...)
      em vez de ft.padding.symmetric(...), ft.border.all(...), ft.border_radius.all(...)
    - ft.Colors / ft.Icons (maiúsculo)   em vez de ft.colors / ft.icons
Se você instalar uma versão mais antiga do Flet (< 0.80), esse código não
vai funcionar como está — confira com `pip show flet`.
"""

import flet as ft

import database as db

# --- Paleta de cores (extraída do style.css / style-clientes.css originais) ---
AZUL = "#2196F3"
AZUL_CLARO = "#42A5F5"
VERDE = "#4CAF50"
CIANO = "#00BCD4"
VERMELHO = "#F44336"
CINZA_FUNDO = "#F5F5F5"
CINZA_BORDA = "#E0E0E0"
CINZA_TEXTO = "#666666"


def formatar_reais(valor: float) -> str:
    """Formata um float como 'R$ 12,34', igual ao toFixed(2) do protótipo."""
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def main(page: ft.Page):
    page.title = "Vendaaz"
    page.padding = 0
    page.bgcolor = CINZA_FUNDO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 390
    page.window.height = 844

    db.init_db()

    # =========================================================================
    # TELA 1 — Lista de clientes (index.html)
    # =========================================================================

    lista_clientes_col = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    # --- Modal: novo cliente ---
    campo_nome_cliente = ft.TextField(
        label="Nome do cliente", max_length=60, autofocus=True
    )

    def fechar_modal_novo_cliente(e=None):
        page.pop_dialog()

    def confirmar_novo_cliente(e):
        nome = (campo_nome_cliente.value or "").strip()
        if not nome:
            campo_nome_cliente.focus()
            return
        db.criar_cliente(nome)
        page.pop_dialog()
        mostrar_tela_clientes()

    modal_novo_cliente = ft.AlertDialog(
        modal=True,
        title=ft.Text("Novo cliente"),
        content=campo_nome_cliente,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_modal_novo_cliente),
            ft.FilledButton(
                "Criar",
                bgcolor=AZUL,
                color="white",
                on_click=confirmar_novo_cliente,
            ),
        ],
    )

    def abrir_modal_novo_cliente(e):
        campo_nome_cliente.value = ""
        page.show_dialog(modal_novo_cliente)

    # --- Modal: recarregar carteira ---
    cliente_em_recarga = {"id": None}
    texto_nome_recarga = ft.Text(size=16, weight=ft.FontWeight.W_500)
    campo_valor_recarga = ft.TextField(
        label="Qual o valor da recarga?",
        prefix="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
    )

    def fechar_modal_recarga(e=None):
        page.pop_dialog()

    def confirmar_recarga(e):
        texto = (campo_valor_recarga.value or "").strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            valor = 0
        if valor <= 0:
            campo_valor_recarga.focus()
            return

        cliente = db.buscar_cliente(cliente_em_recarga["id"])
        novo_saldo = round(cliente["saldo"] + valor, 2)
        db.atualizar_saldo(cliente["id"], novo_saldo)

        page.pop_dialog()
        mostrar_tela_clientes()

    modal_recarga = ft.AlertDialog(
        modal=True,
        content=ft.Column(
            [texto_nome_recarga, campo_valor_recarga],
            tight=True,
            spacing=16,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_modal_recarga),
            ft.FilledButton(
                "Confirmar",
                bgcolor=CIANO,
                color="white",
                on_click=confirmar_recarga,
            ),
        ],
    )

    def abrir_modal_recarga(cliente):
        cliente_em_recarga["id"] = cliente["id"]
        texto_nome_recarga.value = cliente["nome"]
        campo_valor_recarga.value = ""
        page.show_dialog(modal_recarga)

    # --- Card de cliente (com "sanfona" de ações, igual ao protótipo) ---
    def criar_card_cliente(cliente) -> ft.Container:
        acoes = ft.Row(
            [
                ft.Button(
                    "Realizar venda",
                    bgcolor=VERDE,
                    color="white",
                    on_click=lambda e, c=cliente: mostrar_tela_venda(c),
                    expand=1,
                ),
                ft.Button(
                    "Recarregar carteira",
                    bgcolor=CIANO,
                    color="white",
                    on_click=lambda e, c=cliente: abrir_modal_recarga(c),
                    expand=1,
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
                ft.Text(cliente["nome"], size=15, color="#222222", expand=True),
                ft.Text(
                    formatar_reais(cliente["saldo"]), size=14, color="#444444"
                ),
            ],
            spacing=12,
        )

        def alternar_card(e):
            acoes.visible = not acoes.visible
            page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=linha_principal,
                        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
                        on_click=alternar_card,
                        ink=True,
                    ),
                    ft.Container(
                        content=acoes,
                        padding=ft.Padding.only(
                            left=16, right=16, top=12, bottom=12
                        ),
                        border=ft.Border.only(
                            top=ft.BorderSide(0.5, "#ECECEC")
                        ),
                    ),
                ],
                spacing=0,
            ),
            bgcolor="white",
            border_radius=ft.BorderRadius.all(10),
            border=ft.Border.all(0.5, CINZA_BORDA),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    def mostrar_tela_clientes():
        clientes = db.listar_clientes()
        lista_clientes_col.controls = [criar_card_cliente(c) for c in clientes]

        topbar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.MENU, color="white"),
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

        page.clean()
        page.add(
            topbar,
            ft.Container(
                content=lista_clientes_col,
                bgcolor=CINZA_FUNDO,
                padding=16,
                expand=True,
            ),
        )
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=AZUL_CLARO,
            on_click=abrir_modal_novo_cliente,
        )
        page.update()

    # =========================================================================
    # TELA 2 — Venda de produtos (venda.html)
    # =========================================================================

    def mostrar_tela_venda(cliente):
        carrinho: dict[str, dict] = {}  # { nome: {"preco": .., "qtd": ..} }
        cliente_atual = {
            "id": cliente["id"],
            "nome": cliente["nome"],
            "saldo": cliente["saldo"],
        }
        badges: dict[str, ft.Text] = {}

        texto_saldo = ft.Text(
            formatar_reais(cliente_atual["saldo"]),
            color="#CCFFFFFF",
            size=13,
        )
        texto_total = ft.Text(formatar_reais(0), size=15, weight=ft.FontWeight.W_500)
        texto_itens = ft.Text(
            "Nenhum item selecionado", size=13, color="#888888"
        )

        def recalcular_total() -> float:
            total = sum(item["preco"] * item["qtd"] for item in carrinho.values())
            texto_total.value = formatar_reais(total)
            itens = [
                f"{nome} x{item['qtd']}"
                for nome, item in carrinho.items()
                if item["qtd"] > 0
            ]
            texto_itens.value = ", ".join(itens) if itens else "Nenhum item selecionado"
            return total

        def alterar_quantidade(nome, preco, delta):
            item = carrinho.setdefault(nome, {"preco": preco, "qtd": 0})
            nova_qtd = item["qtd"] + delta
            if nova_qtd < 0:
                return
            item["qtd"] = nova_qtd
            badges[nome].value = str(nova_qtd)
            recalcular_total()
            page.update()

        def botao_qtd(icone, on_click) -> ft.Container:
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

        # --- Grade de produtos ---
        grade_produtos = ft.GridView(
            runs_count=2,
            spacing=12,
            run_spacing=12,
            child_aspect_ratio=0.68,
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=16, bottom=16),
        )

        for produto in db.listar_produtos():
            nome_produto = produto["nome"]
            preco_produto = produto["preco"]

            badge_qtd = ft.Text("0", size=15, weight=ft.FontWeight.W_600)
            badges[nome_produto] = badge_qtd

            grade_produtos.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(
                                src=produto["imagem"],
                                height=110,
                                fit=ft.BoxFit.COVER,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(nome_produto, size=14, color="#333333"),
                                        ft.Row(
                                            [
                                                ft.Text(
                                                    formatar_reais(preco_produto),
                                                    color=AZUL,
                                                    weight=ft.FontWeight.W_500,
                                                    size=15,
                                                ),
                                                ft.Row(
                                                    [
                                                        botao_qtd(
                                                            ft.Icons.REMOVE,
                                                            lambda e, n=nome_produto, p=preco_produto: alterar_quantidade(n, p, -1),
                                                        ),
                                                        badge_qtd,
                                                        botao_qtd(
                                                            ft.Icons.ADD,
                                                            lambda e, n=nome_produto, p=preco_produto: alterar_quantidade(n, p, 1),
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
            )

        # --- Modal: aviso (nenhum item / saldo insuficiente) ---
        texto_aviso_titulo = ft.Text(size=17, weight=ft.FontWeight.W_500)
        texto_aviso_msg = ft.Text(size=14, color=CINZA_TEXTO)

        def fechar_modal_aviso(e=None):
            page.pop_dialog()

        modal_aviso = ft.AlertDialog(
            modal=True,
            title=texto_aviso_titulo,
            content=texto_aviso_msg,
            actions=[
                ft.FilledButton("Ok", bgcolor=AZUL, color="white", on_click=fechar_modal_aviso)
            ],
        )

        def abrir_modal_aviso(titulo, mensagem):
            texto_aviso_titulo.value = titulo
            texto_aviso_msg.value = mensagem
            page.show_dialog(modal_aviso)

        # --- Modal: sucesso ---
        texto_sucesso_total = ft.Text(weight=ft.FontWeight.W_700)

        def continuar_apos_sucesso(e=None):
            page.pop_dialog()
            mostrar_tela_clientes()

        modal_sucesso = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.CHECK, color=VERDE, size=26),
                        width=52,
                        height=52,
                        border_radius=ft.BorderRadius.all(26),
                        bgcolor="#E8F5E9",
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text("Pedido realizado!", size=17, weight=ft.FontWeight.W_500),
                    ft.Row(
                        [
                            ft.Text("Venda de", size=14, color=CINZA_TEXTO),
                            texto_sucesso_total,
                            ft.Text("concluída com sucesso.", size=14, color=CINZA_TEXTO),
                        ],
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.FilledButton(
                    "Continuar", bgcolor=VERDE, color="white", on_click=continuar_apos_sucesso
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        # --- Modal: confirmar cancelamento da venda ---
        def fechar_modal_cancelar(e=None):
            page.pop_dialog()

        def confirmar_cancelamento(e=None):
            page.pop_dialog()
            mostrar_tela_clientes()

        modal_cancelar = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cancelar venda?"),
            content=ft.Text(
                "Os itens selecionados serão perdidos. Deseja mesmo cancelar?"
            ),
            actions=[
                ft.TextButton("Voltar", on_click=fechar_modal_cancelar),
                ft.FilledButton(
                    "Sim, cancelar",
                    bgcolor=VERMELHO,
                    color="white",
                    on_click=confirmar_cancelamento,
                ),
            ],
        )

        def abrir_modal_cancelar(e):
            page.show_dialog(modal_cancelar)

        # --- Finalizar pedido ---
        def finalizar_pedido(e):
            total = recalcular_total()

            if total == 0:
                abrir_modal_aviso(
                    "Nenhum item selecionado.",
                    "Adicione pelo menos um produto antes de finalizar.",
                )
                return

            if total > cliente_atual["saldo"]:
                abrir_modal_aviso(
                    "Saldo insuficiente.",
                    "O valor total da compra ultrapassa o crédito disponível do cliente.",
                )
                return

            novo_saldo = round(cliente_atual["saldo"] - total, 2)
            db.atualizar_saldo(cliente_atual["id"], novo_saldo)
            cliente_atual["saldo"] = novo_saldo
            texto_saldo.value = formatar_reais(novo_saldo)

            carrinho.clear()
            for badge in badges.values():
                badge.value = "0"
            recalcular_total()

            texto_sucesso_total.value = formatar_reais(total)
            page.show_dialog(modal_sucesso)

        # --- Barra superior e barra do carrinho ---
        topbar_venda = ft.Container(
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
                                        cliente_atual["nome"],
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
                        on_click=abrir_modal_cancelar,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=AZUL,
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
            border=ft.Border.only(top=ft.BorderSide(0.5, CINZA_BORDA)),
        )

        page.clean()
        page.add(
            topbar_venda,
            ft.Container(content=grade_produtos, bgcolor=CINZA_FUNDO, expand=True),
            barra_carrinho,
        )
        page.floating_action_button = None
        page.update()

    # =========================================================================
    # Início do app
    # =========================================================================
    mostrar_tela_clientes()


ft.run(main, assets_dir="img")
