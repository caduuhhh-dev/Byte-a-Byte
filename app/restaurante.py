"""Restaurante: coordena cardápio, clientes e pedidos (padrão Facade).

A interface gráfica só conversa com esta classe; ela aplica as regras de
negócio nas classes de domínio e delega a gravação ao BancoDados.
"""
import sqlite3
from datetime import date, datetime

from app.banco.banco_dados import BancoDados
from app.modelos.bebida import Bebida
from app.modelos.cliente import Cliente
from app.modelos.item_pedido import ItemPedido
from app.modelos.pedido import Pedido
from app.modelos.prato import Prato
from app.modelos.produto import Produto
from app.relatorio import Relatorio


class Restaurante:
    def __init__(self, nome: str, banco: BancoDados):
        self.nome = nome
        self.banco = banco
        self.produtos = banco.listar_produtos()
        self.clientes = banco.listar_clientes()
        self.pedidos = self._carregar_pedidos()

    def _carregar_pedidos(self) -> list:
        """Reconstrói os pedidos do banco ligando-os aos objetos já carregados."""
        clientes = {c.id_cliente: c for c in self.clientes}
        produtos = {p.id_produto: p for p in self.produtos}
        pedidos = []
        for linha in self.banco.listar_pedidos():
            pedido = Pedido(linha["numero"], clientes[linha["cliente_id"]],
                            linha["desconto"], linha["status"],
                            datetime.fromisoformat(linha["data"]))
            for item in self.banco.listar_itens_pedido(pedido.numero):
                produto = produtos[item["produto_id"]]
                # Pedido.adicionar_item recusa produtos indisponíveis, mas um
                # pedido antigo pode conter um produto que saiu do cardápio.
                pedido.itens.append(ItemPedido(produto, item["quantidade"]))
            pedidos.append(pedido)
        return pedidos

    # --- clientes ------------------------------------------------------
    def cadastrar_cliente(self, nome: str, telefone: str) -> Cliente:
        cliente = self.banco.salvar_cliente(Cliente(nome, telefone))
        self.clientes.append(cliente)
        return cliente

    def atualizar_cliente(self, cliente: Cliente, nome: str, telefone: str) -> None:
        cliente.atualizar_dados(nome, telefone)
        self.banco.salvar_cliente(cliente)

    def remover_cliente(self, cliente: Cliente) -> None:
        if any(p.cliente is cliente for p in self.pedidos):
            raise ValueError("Cliente possui pedidos e não pode ser removido.")
        self.banco.excluir_cliente(cliente.id_cliente)
        self.clientes.remove(cliente)

    # --- cardápio ------------------------------------------------------
    def cadastrar_prato(self, nome: str, preco: float, ingredientes: list,
                        tempo_preparo: int) -> Prato:
        return self._adicionar_produto(Prato(nome, preco, ingredientes, tempo_preparo))

    def cadastrar_bebida(self, nome: str, preco: float, volume_ml: int,
                         tipo: str) -> Bebida:
        return self._adicionar_produto(Bebida(nome, preco, volume_ml, tipo))

    def _adicionar_produto(self, produto: Produto) -> Produto:
        self.banco.salvar_produto(produto)
        self.produtos.append(produto)
        return produto

    def alterar_preco(self, produto: Produto, preco: float) -> None:
        produto.preco = preco  # o setter valida
        self.banco.salvar_produto(produto)

    def alterar_disponibilidade(self, produto: Produto, disponivel: bool) -> None:
        produto.disponivel = disponivel
        self.banco.salvar_produto(produto)

    def remover_produto(self, produto: Produto) -> None:
        try:
            self.banco.excluir_produto(produto.id_produto)
        except sqlite3.IntegrityError:
            raise ValueError("Produto já foi vendido; marque-o como "
                             "indisponível em vez de removê-lo.") from None
        self.produtos.remove(produto)

    def produtos_disponiveis(self) -> list:
        return [p for p in self.produtos if p.disponivel]

    # --- pedidos -------------------------------------------------------
    def criar_pedido(self, cliente: Cliente) -> Pedido:
        pedido = Pedido(self.banco.proximo_numero_pedido(), cliente)
        self.banco.salvar_pedido(pedido)
        self.pedidos.append(pedido)
        return pedido

    def adicionar_item_pedido(self, pedido: Pedido, produto: Produto,
                              quantidade: int = 1) -> None:
        self._exigir_pendente(pedido)
        pedido.adicionar_item(produto, quantidade)
        self.banco.salvar_pedido(pedido)

    def remover_item_pedido(self, pedido: Pedido, indice: int) -> None:
        self._exigir_pendente(pedido)
        pedido.remover_item(indice)
        self.banco.salvar_pedido(pedido)

    def aplicar_desconto(self, pedido: Pedido, percentual: float) -> None:
        pedido.aplicar_desconto(percentual)
        self.banco.salvar_pedido(pedido)

    def alterar_status_pedido(self, pedido: Pedido, novo_status: str) -> bool:
        if novo_status != "pendente" and not pedido.itens:
            return False  # não faz sentido preparar um pedido vazio
        if not pedido.alterar_status(novo_status):
            return False
        self.banco.salvar_pedido(pedido)
        return True

    def remover_pedido(self, pedido: Pedido) -> None:
        self.banco.excluir_pedido(pedido.numero)
        self.pedidos.remove(pedido)

    @staticmethod
    def _exigir_pendente(pedido: Pedido) -> None:
        if pedido.status != "pendente":
            raise ValueError("Só é possível alterar itens de pedidos pendentes.")

    # --- relatórios ----------------------------------------------------
    def gerar_relatorio(self, inicio: date = None, fim: date = None) -> Relatorio:
        return Relatorio(self.banco, inicio, fim)

