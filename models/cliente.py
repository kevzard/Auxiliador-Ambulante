"""Entidade de domínio Cliente.

Um dataclass simples, sem nenhuma dependência de Flet ou SQLite — é apenas
o formato de dado que trafega entre as camadas (repositório <-> serviço <-> UI).
"""

from dataclasses import dataclass


@dataclass
class Cliente:
    id: int
    nome: str
    saldo: float
