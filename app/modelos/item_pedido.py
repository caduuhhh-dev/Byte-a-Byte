"""Item de um pedido: liga um Produto a uma quantidade (associação)."""
from app.modelos.produto import Produto


class ItemPedido:
    def __init__(self, produto: Produto, quantidade: int = 1):
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValueError("A quantidade deve ser um inteiro maior que zero.")
        self.produto = produto
        self.quantidade = quantidade

    def calcular_subtotal(self) -> float:
        # Usa calcular_preco(), então cada tipo de produto aplica sua regra.
        return self.produto.calcular_preco() * self.quantidade

    def exibir_detalhes(self) -> str:
        return (f"{self.quantidade}x {self.produto.nome} — "
                f"R$ {self.calcular_subtotal():.2f}")
