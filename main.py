"""
main.py
Ponto de entrada do Vendaaz.

Depois da modularização, este arquivo não desenha mais nada — ele só:
1. Configura a Page;
2. Cria as instâncias dos repositórios (camada de dados);
3. Liga as duas telas entre si (quem chama quem ao navegar).

Toda a interface está em views/, os componentes reutilizáveis e modais
em ui/, a regra do carrinho em services/, e o acesso ao banco em
repositories/ + database.py.

Observação sobre a versão do Flet: este código usa a API do Flet 1.0
(>= 0.80) — ft.run(), page.show_dialog()/page.pop_dialog(),
ft.Padding/ft.Border/ft.BorderRadius (maiúsculo) em vez das funções
antigas ft.padding.*/ft.border.*. Confira com `pip show flet` se
encontrar código de exemplo com uma sintaxe diferente dessa.
"""

import flet as ft

import database as db
from repositories.cliente_repository import ClienteRepository
from repositories.produto_repository import ProdutoRepository
from views.tela_clientes import montar_tela_clientes
from views.tela_produtos import montar_tela_produtos
from views.tela_venda import montar_tela_venda


def main(page: ft.Page):
    page.title = "Vendas"
    page.padding = 0
    page.bgcolor = "#F5F5F5"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 390
    page.window.height = 844

    db.init_db()

    cliente_repo = ClienteRepository()
    produto_repo = ProdutoRepository()

    def ir_para_clientes():
        montar_tela_clientes_atual()

    def ir_para_venda(cliente):
        montar_venda = montar_tela_venda(
            page,
            cliente,
            cliente_repo,
            produto_repo,
            ao_voltar_para_clientes=ir_para_clientes,
        )
        montar_venda()

    def ir_para_produtos():
        montar_produtos = montar_tela_produtos(
            page, produto_repo, ao_voltar=ir_para_clientes
        )
        montar_produtos()

    montar_tela_clientes_atual = montar_tela_clientes(
        page,
        cliente_repo,
        ao_realizar_venda=ir_para_venda,
        ao_abrir_produtos=ir_para_produtos,
    )
    montar_tela_clientes_atual()


ft.run(main, assets_dir="img")
