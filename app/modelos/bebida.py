"""Bebidas do cardápio (herda de Produto)."""
from app.modelos.produto import Produto


class Bebida(Produto):
    def __init__(self, nome: str, preco: float, volume_ml: int, tipo: str,
                 disponivel: bool = True):
        super().__init__(nome, preco, disponivel)
        self.volume_ml = volume_ml
        self.tipo = tipo  # ex.: "refrigerante", "suco", "alcoólica"

    def exibir_detalhes(self) -> str:
        base = super().exibir_detalhes()
        return f"[Bebida] {base} | {self.volume_ml} ml | Tipo: {self.tipo}"