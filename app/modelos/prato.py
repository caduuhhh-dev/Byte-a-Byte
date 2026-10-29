"""Pratos do cardápio (herda de Produto)."""
from app.modelos.produto import Produto


class Prato(Produto):
    def __init__(self, nome: str, preco: float, ingredientes: list, tempo_preparo: int,
                 disponivel: bool = True):
        super().__init__(nome, preco, disponivel)
        self.ingredientes = list(ingredientes)
        self.tempo_preparo = tempo_preparo  # em minutos

    def calcular_preco(self) -> float:
        # Regra própria de preço pode entrar aqui (ex.: taxa de preparo).
        # Por enquanto, usa o preço base.
        return super().calcular_preco()

    def exibir_detalhes(self) -> str:
        base = super().exibir_detalhes()
        ingredientes = ", ".join(self.ingredientes)
        return f"[Prato] {base} | Ingredientes: {ingredientes} | Preparo: {self.tempo_preparo} min"