"""Pedido (comanda): agrega itens e está associado a um cliente."""
from datetime import datetime

from app.modelos.cliente import Cliente
from app.modelos.item_pedido import ItemPedido
from app.modelos.produto import Produto


class Pedido:
    # Ordem do fluxo: o pedido só avança, nunca volta.
    STATUS_VALIDOS = ("pendente", "em preparo", "pronto", "entregue")

    def __init__(self, numero: int, cliente: Cliente, desconto: float = 0.0,
                 status: str = "pendente", data: datetime = None):
        if status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {status}")
        self.numero = numero
        self.cliente = cliente
        self.itens = []
        self.status = status
        self.data = data or datetime.now()
        self.__desconto = 0.0   # atributo privado (percentual de 0 a 100)
        self.aplicar_desconto(desconto)

    # --- itens ---------------------------------------------------------
    def adicionar_item(self, produto: Produto, quantidade: int = 1) -> ItemPedido:
        if not produto.disponivel:
            raise ValueError(f"{produto.nome} não está disponível.")
        item = ItemPedido(produto, quantidade)
        self.itens.append(item)
        return item

    def remover_item(self, indice: int) -> None:
        if not 0 <= indice < len(self.itens):
            raise IndexError("Item inexistente no pedido.")
        del self.itens[indice]

    # --- desconto (encapsulado) ----------------------------------------
    @property
    def desconto(self) -> float:
        return self.__desconto

    def aplicar_desconto(self, percentual: float) -> None:
        if (not isinstance(percentual, (int, float)) or isinstance(percentual, bool)
                or not 0 <= percentual <= 100):
            raise ValueError("O desconto deve ser um percentual entre 0 e 100.")
        self.__desconto = float(percentual)

    # --- valores -------------------------------------------------------
    def calcular_subtotal(self) -> float:
        return sum(item.calcular_subtotal() for item in self.itens)

    def calcular_total(self) -> float:
        total = self.calcular_subtotal() * (1 - self.__desconto / 100)
        return round(total, 2)

    # --- status --------------------------------------------------------
    def __validar_status(self, novo_status: str) -> bool:
        """Método privado: aceita só status conhecidos e que avancem o fluxo."""
        if novo_status not in self.STATUS_VALIDOS:
            return False
        atual = self.STATUS_VALIDOS.index(self.status)
        return self.STATUS_VALIDOS.index(novo_status) > atual

    def alterar_status(self, novo_status: str) -> bool:
        if not self.__validar_status(novo_status):
            return False
        self.status = novo_status
        return True

    def exibir_detalhes(self) -> str:
        linhas = [f"Pedido #{self.numero} — {self.cliente.nome} — {self.status}"]
        linhas += [f"  {item.exibir_detalhes()}" for item in self.itens]
        linhas.append(f"  Subtotal: R$ {self.calcular_subtotal():.2f}")
        if self.__desconto:
            linhas.append(f"  Desconto: {self.__desconto:.0f}%")
        linhas.append(f"  Total: R$ {self.calcular_total():.2f}")
        return "\n".join(linhas)
