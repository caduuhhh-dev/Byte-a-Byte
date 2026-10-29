"""Bebidas do cardápio (herda de Produto)."""
from app.modelos.produto import Produto


class Bebida(Produto):
    def __init__(self, nome: str, preco: float, volume_ml: int, tipo: str,
                 disponivel: bool = True, id_produto: int = None):
        super().__init__(nome, preco, disponivel, id_produto)
        self.volume_ml = volume_ml
        self.tipo = tipo  # ex.: "refrigerante", "suco", "alcoólica"

    @property
    def categoria(self) -> str:
        return "bebida"

    def calcular_preco(self) -> float:
        # Mesmo ponto de extensão do Prato (ex.: taxa de bebidas alcoólicas).
        return super().calcular_preco()

    def exibir_detalhes(self) -> str:
        base = super().exibir_detalhes()
        return f"[Bebida] {base} | {self.volume_ml} ml | Tipo: {self.tipo}"
