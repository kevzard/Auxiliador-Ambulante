"""Modais (AlertDialog) do app.

Cada função `criar_modal_*` monta UM diálogo e devolve uma tupla
`(dialog, abrir)`:
    - `dialog`  é o ft.AlertDialog em si (raramente precisa ser usado
      fora daqui, mas fica disponível caso a tela precise inspecioná-lo);
    - `abrir(...)` é a função que a tela chama para exibi-lo, já cuidando
      de resetar campos e repassar dados (ex: nome do cliente na recarga).

Assim, se um modal tiver um bug (ex: campo não limpa, botão não fecha),
o problema está isolado numa função pequena e fácil de achar — em vez de
procurar no meio de centenas de linhas da tela inteira.
"""

from typing import Callable

import flet as ft

from ui.components import criar_seletor_imagem
from ui.theme import AZUL, CIANO, CINZA_TEXTO, VERDE, VERMELHO, formatar_reais


def criar_modal_novo_cliente(
    page: ft.Page, on_confirmar: Callable[[str], None]
) -> tuple[ft.AlertDialog, Callable[[], None]]:
    campo_nome = ft.TextField(label="Nome do cliente", max_length=60, autofocus=True)

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e):
        nome = (campo_nome.value or "").strip()
        if not nome:
            campo_nome.focus()
            return
        page.pop_dialog()
        on_confirmar(nome)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Novo cliente"),
        content=campo_nome,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Criar", bgcolor=AZUL, color="white", on_click=confirmar),
        ],
    )

    def abrir():
        campo_nome.value = ""
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_recarga(
    page: ft.Page, on_confirmar: Callable[[int, float], None]
) -> tuple[ft.AlertDialog, Callable[[object], None]]:
    """`on_confirmar(cliente_id, valor)` é chamado com o valor já validado."""
    cliente_atual = {"id": None}
    texto_nome = ft.Text(size=16, weight=ft.FontWeight.W_500)
    campo_valor = ft.TextField(
        label="Qual o valor da recarga?",
        prefix="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
    )

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e):
        texto = (campo_valor.value or "").strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            valor = 0
        if valor <= 0:
            campo_valor.focus()
            return
        page.pop_dialog()
        on_confirmar(cliente_atual["id"], valor)

    dialog = ft.AlertDialog(
        modal=True,
        content=ft.Column([texto_nome, campo_valor], tight=True, spacing=16),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Confirmar", bgcolor=CIANO, color="white", on_click=confirmar),
        ],
    )

    def abrir(cliente):
        cliente_atual["id"] = cliente.id
        texto_nome.value = cliente.nome
        campo_valor.value = ""
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_editar_cliente(
    page: ft.Page, on_confirmar: Callable[[int, str], None]
) -> tuple[ft.AlertDialog, Callable[[object], None]]:
    """`on_confirmar(cliente_id, novo_nome)`. `abrir(cliente)` já vem com
    o campo preenchido com o nome atual, pronto para corrigir."""
    cliente_atual = {"id": None}
    campo_nome = ft.TextField(label="Nome do cliente", max_length=60, autofocus=True)

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e):
        novo_nome = (campo_nome.value or "").strip()
        if not novo_nome:
            campo_nome.focus()
            return
        page.pop_dialog()
        on_confirmar(cliente_atual["id"], novo_nome)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar cliente"),
        content=campo_nome,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Salvar", bgcolor=AZUL, color="white", on_click=confirmar),
        ],
    )

    def abrir(cliente):
        cliente_atual["id"] = cliente.id
        campo_nome.value = cliente.nome
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_confirmar_exclusao_cliente(
    page: ft.Page, on_confirmar: Callable[[int], None]
) -> tuple[ft.AlertDialog, Callable[[object], None]]:
    """`on_confirmar(cliente_id)`. Mostra o nome do cliente e, se ele
    ainda tiver saldo, avisa antes de deixar excluir — a exclusão é
    definitiva e não existe desfazer."""
    cliente_atual = {"id": None}
    texto_mensagem = ft.Text(size=14, color=CINZA_TEXTO)

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e=None):
        page.pop_dialog()
        on_confirmar(cliente_atual["id"])

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir cliente?"),
        content=texto_mensagem,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Sim, excluir", bgcolor=VERMELHO, color="white", on_click=confirmar),
        ],
    )

    def abrir(cliente):
        cliente_atual["id"] = cliente.id
        if cliente.saldo > 0:
            texto_mensagem.value = (
                f"{cliente.nome} ainda tem {formatar_reais(cliente.saldo)} de saldo. "
                "Essa ação não pode ser desfeita. Deseja excluir mesmo assim?"
            )
        else:
            texto_mensagem.value = (
                f"Tem certeza que deseja excluir {cliente.nome}? Essa ação não pode ser desfeita."
            )
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_novo_produto(
    page: ft.Page,
    on_confirmar: Callable[[str, float, str], None],
    imagens_disponiveis: Callable[[], list[str]],
) -> tuple[ft.AlertDialog, Callable[[], None]]:
    """`on_confirmar(nome, preco, imagem)`.

    `imagens_disponiveis` é uma FUNÇÃO (não uma lista pronta) porque a
    pasta img/ pode ganhar arquivos novos entre uma abertura do modal e
    outra — assim ela é relida toda vez que o modal abre.
    """
    campo_nome = ft.TextField(label="Nome do produto", max_length=60, autofocus=True)
    campo_preco = ft.TextField(
        label="Preço", prefix="R$ ", keyboard_type=ft.KeyboardType.NUMBER
    )
    area_seletor = ft.Column(spacing=8)
    seletor_atual = {"obter_selecionada": lambda: None}

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e):
        nome = (campo_nome.value or "").strip()
        preco_texto = (campo_preco.value or "").strip().replace(",", ".")
        imagem = seletor_atual["obter_selecionada"]()

        if not nome:
            campo_nome.focus()
            return
        try:
            preco = float(preco_texto)
        except ValueError:
            preco = -1
        if preco <= 0:
            campo_preco.focus()
            return
        if not imagem:
            return  # sem imagem disponível/selecionada — não deixa confirmar

        page.pop_dialog()
        on_confirmar(nome, preco, imagem)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Novo produto"),
        content=ft.Column(
            [campo_nome, campo_preco, ft.Text("Escolha uma imagem", size=12, color=CINZA_TEXTO), area_seletor],
            tight=True,
            spacing=16,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Criar", bgcolor=AZUL, color="white", on_click=confirmar),
        ],
    )

    def abrir():
        campo_nome.value = ""
        campo_preco.value = ""
        imagens = imagens_disponiveis()
        imagem_padrao = imagens[0] if imagens else None
        seletor, obter_selecionada, _ = criar_seletor_imagem(page, imagens, imagem_inicial=imagem_padrao)
        seletor_atual["obter_selecionada"] = obter_selecionada
        area_seletor.controls = [seletor]
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_editar_produto(
    page: ft.Page,
    on_confirmar: Callable[[int, str, float, str], None],
    imagens_disponiveis: Callable[[], list[str]],
) -> tuple[ft.AlertDialog, Callable[[object], None]]:
    """`on_confirmar(produto_id, nome, preco, imagem)`. `abrir(produto)`
    já vem com nome, preço e imagem atuais preenchidos."""
    produto_atual = {"id": None}
    campo_nome = ft.TextField(label="Nome do produto", max_length=60, autofocus=True)
    campo_preco = ft.TextField(
        label="Preço", prefix="R$ ", keyboard_type=ft.KeyboardType.NUMBER
    )
    area_seletor = ft.Column(spacing=8)
    seletor_atual = {"obter_selecionada": lambda: None}

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e):
        nome = (campo_nome.value or "").strip()
        preco_texto = (campo_preco.value or "").strip().replace(",", ".")
        imagem = seletor_atual["obter_selecionada"]()

        if not nome:
            campo_nome.focus()
            return
        try:
            preco = float(preco_texto)
        except ValueError:
            preco = -1
        if preco <= 0:
            campo_preco.focus()
            return
        if not imagem:
            return

        page.pop_dialog()
        on_confirmar(produto_atual["id"], nome, preco, imagem)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar produto"),
        content=ft.Column(
            [campo_nome, campo_preco, ft.Text("Escolha uma imagem", size=12, color=CINZA_TEXTO), area_seletor],
            tight=True,
            spacing=16,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Salvar", bgcolor=AZUL, color="white", on_click=confirmar),
        ],
    )

    def abrir(produto):
        produto_atual["id"] = produto.id
        campo_nome.value = produto.nome
        campo_preco.value = f"{produto.preco:.2f}"
        seletor, obter_selecionada, _ = criar_seletor_imagem(
            page, imagens_disponiveis(), imagem_inicial=produto.imagem
        )
        seletor_atual["obter_selecionada"] = obter_selecionada
        area_seletor.controls = [seletor]
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_confirmar_exclusao_produto(
    page: ft.Page, on_confirmar: Callable[[int], None]
) -> tuple[ft.AlertDialog, Callable[[object], None]]:
    """`on_confirmar(produto_id)`."""
    produto_atual = {"id": None}
    texto_mensagem = ft.Text(size=14, color=CINZA_TEXTO)

    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e=None):
        page.pop_dialog()
        on_confirmar(produto_atual["id"])

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir produto?"),
        content=texto_mensagem,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Sim, excluir", bgcolor=VERMELHO, color="white", on_click=confirmar),
        ],
    )

    def abrir(produto):
        produto_atual["id"] = produto.id
        texto_mensagem.value = (
            f"Tem certeza que deseja excluir {produto.nome}? Essa ação não pode ser desfeita."
        )
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_aviso(page: ft.Page) -> tuple[ft.AlertDialog, Callable[[str, str], None]]:
    """Modal genérico de aviso — usado tanto para 'carrinho vazio' quanto
    para 'saldo insuficiente'. `abrir(titulo, mensagem)`."""
    texto_titulo = ft.Text(size=17, weight=ft.FontWeight.W_500)
    texto_mensagem = ft.Text(size=14, color=CINZA_TEXTO)

    def fechar(e=None):
        page.pop_dialog()

    dialog = ft.AlertDialog(
        modal=True,
        title=texto_titulo,
        content=texto_mensagem,
        actions=[ft.FilledButton("Ok", bgcolor=AZUL, color="white", on_click=fechar)],
    )

    def abrir(titulo: str, mensagem: str):
        texto_titulo.value = titulo
        texto_mensagem.value = mensagem
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_sucesso(
    page: ft.Page, on_continuar: Callable[[], None]
) -> tuple[ft.AlertDialog, Callable[[float], None]]:
    """Modal de venda concluída. `abrir(total)` mostra o valor da venda."""
    texto_total = ft.Text(weight=ft.FontWeight.W_700)

    def continuar(e=None):
        page.pop_dialog()
        on_continuar()

    dialog = ft.AlertDialog(
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
                        texto_total,
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
        actions=[ft.FilledButton("Continuar", bgcolor=VERDE, color="white", on_click=continuar)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    def abrir(total: float):
        texto_total.value = formatar_reais(total)
        page.show_dialog(dialog)

    return dialog, abrir


def criar_modal_confirmar_cancelamento(
    page: ft.Page, on_confirmar: Callable[[], None]
) -> tuple[ft.AlertDialog, Callable[[], None]]:
    def fechar(e=None):
        page.pop_dialog()

    def confirmar(e=None):
        page.pop_dialog()
        on_confirmar()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cancelar venda?"),
        content=ft.Text("Os itens selecionados serão perdidos. Deseja mesmo cancelar?"),
        actions=[
            ft.TextButton("Voltar", on_click=fechar),
            ft.FilledButton("Sim, cancelar", bgcolor=VERMELHO, color="white", on_click=confirmar),
        ],
    )

    def abrir():
        page.show_dialog(dialog)

    return dialog, abrir
