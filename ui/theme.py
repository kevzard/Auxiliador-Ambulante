"""Paleta de cores (extraída do style.css / style-clientes.css originais)
e helpers de formatação usados em toda a UI.

Centralizar aqui evita "cor mágica" espalhada pelo código — se um dia
quiser trocar o azul do app, é um lugar só para editar.
"""

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
