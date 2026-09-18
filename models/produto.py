"""Entidade de domínio Produto."""

from dataclasses import dataclass


@dataclass
class Produto:
    id: int
    nome: str
    preco: float
    imagem: str
