"""Camada de persistência: toda a comunicação com o SQLite passa por aqui."""
import sqlite3
from pathlib import Path

from app.modelos.bebida import Bebida
from app.modelos.cliente import Cliente
from app.modelos.pedido import Pedido
from app.modelos.prato import Prato
from app.modelos.produto import Produto

CAMINHO_PADRAO = Path(__file__).resolve().parents[2] / "data" / "restaurante.db"


class BancoDados:
    def __init__(self, caminho: str = CAMINHO_PADRAO):
        # ":memory:" cria um banco temporário (útil nos testes).
        if caminho != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self.conexao = sqlite3.connect(str(caminho))
        self.conexao.row_factory = sqlite3.Row
        self.conexao.execute("PRAGMA foreign_keys = ON")
        self.__criar_tabelas()

    def __criar_tabelas(self) -> None:
        """Método privado: garante que o schema exista."""
        self.conexao.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT NOT NULL,
                telefone   TEXT
            );
            CREATE TABLE IF NOT EXISTS produtos (
                id_produto    INTEGER PRIMARY KEY AUTOINCREMENT,
                nome          TEXT NOT NULL,
                preco         REAL NOT NULL CHECK (preco > 0),
                disponivel    INTEGER NOT NULL DEFAULT 1,
                categoria     TEXT NOT NULL CHECK (categoria IN ('prato', 'bebida')),
                ingredientes  TEXT,
                tempo_preparo INTEGER,
                volume_ml     INTEGER,
                tipo_bebida   TEXT
            );
            CREATE TABLE IF NOT EXISTS pedidos (
                numero      INTEGER PRIMARY KEY,
                cliente_id  INTEGER NOT NULL REFERENCES clientes(id_cliente),
                status      TEXT NOT NULL,
                desconto    REAL NOT NULL DEFAULT 0,
                valor_total REAL NOT NULL DEFAULT 0,
                data        TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id_item       INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_numero INTEGER NOT NULL
                              REFERENCES pedidos(numero) ON DELETE CASCADE,
                produto_id    INTEGER NOT NULL REFERENCES produtos(id_produto),
                quantidade    INTEGER NOT NULL CHECK (quantidade > 0),
                subtotal      REAL NOT NULL
            );
        """)
        self.conexao.commit()

    def fechar(self) -> None:
        self.conexao.close()

    # --- clientes ------------------------------------------------------
    def salvar_cliente(self, cliente: Cliente) -> Cliente:
        """Insere (sem id) ou atualiza (com id) o cliente."""
        with self.conexao:
            if cliente.id_cliente is None:
                cursor = self.conexao.execute(
                    "INSERT INTO clientes (nome, telefone) VALUES (?, ?)",
                    (cliente.nome, cliente.telefone))
                cliente.id_cliente = cursor.lastrowid
            else:
                self.conexao.execute(
                    "UPDATE clientes SET nome = ?, telefone = ? WHERE id_cliente = ?",
                    (cliente.nome, cliente.telefone, cliente.id_cliente))
        return cliente

    def listar_clientes(self) -> list:
        linhas = self.conexao.execute(
            "SELECT * FROM clientes ORDER BY nome").fetchall()
        return [Cliente(l["nome"], l["telefone"] or "", l["id_cliente"])
                for l in linhas]

    def excluir_cliente(self, id_cliente: int) -> None:
        with self.conexao:
            self.conexao.execute(
                "DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))

    # --- produtos ------------------------------------------------------
    def salvar_produto(self, produto: Produto) -> Produto:
        """Insere (sem id) ou atualiza (com id) um Prato ou uma Bebida."""
        if isinstance(produto, Prato):
            extras = (", ".join(produto.ingredientes), produto.tempo_preparo, None, None)
        elif isinstance(produto, Bebida):
            extras = (None, None, produto.volume_ml, produto.tipo)
        else:
            raise TypeError("Só é possível salvar pratos e bebidas.")
        valores = (produto.nome, produto.preco, int(produto.disponivel),
                   produto.categoria) + extras
        with self.conexao:
            if produto.id_produto is None:
                cursor = self.conexao.execute(
                    "INSERT INTO produtos (nome, preco, disponivel, categoria, "
                    "ingredientes, tempo_preparo, volume_ml, tipo_bebida) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", valores)
                produto.id_produto = cursor.lastrowid
            else:
                self.conexao.execute(
                    "UPDATE produtos SET nome = ?, preco = ?, disponivel = ?, "
                    "categoria = ?, ingredientes = ?, tempo_preparo = ?, "
                    "volume_ml = ?, tipo_bebida = ? WHERE id_produto = ?",
                    valores + (produto.id_produto,))
        return produto

    def listar_produtos(self) -> list:
        linhas = self.conexao.execute(
            "SELECT * FROM produtos ORDER BY categoria DESC, nome").fetchall()
        produtos = []
        for l in linhas:
            if l["categoria"] == "prato":
                ingredientes = [i.strip() for i in (l["ingredientes"] or "").split(",")
                                if i.strip()]
                produtos.append(Prato(l["nome"], l["preco"], ingredientes,
                                      l["tempo_preparo"], bool(l["disponivel"]),
                                      l["id_produto"]))
            else:
                produtos.append(Bebida(l["nome"], l["preco"], l["volume_ml"],
                                       l["tipo_bebida"], bool(l["disponivel"]),
                                       l["id_produto"]))
        return produtos

    def excluir_produto(self, id_produto: int) -> None:
        with self.conexao:
            self.conexao.execute(
                "DELETE FROM produtos WHERE id_produto = ?", (id_produto,))

    # --- pedidos -------------------------------------------------------
    def proximo_numero_pedido(self) -> int:
        linha = self.conexao.execute(
            "SELECT COALESCE(MAX(numero), 0) + 1 FROM pedidos").fetchone()
        return linha[0]

    def salvar_pedido(self, pedido: Pedido) -> None:
        """Grava o pedido e regrava todos os seus itens numa única transação."""
        with self.conexao:
            self.conexao.execute(
                "INSERT INTO pedidos (numero, cliente_id, status, desconto, "
                "valor_total, data) VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(numero) DO UPDATE SET cliente_id = excluded.cliente_id, "
                "status = excluded.status, desconto = excluded.desconto, "
                "valor_total = excluded.valor_total, data = excluded.data",
                (pedido.numero, pedido.cliente.id_cliente, pedido.status,
                 pedido.desconto, pedido.calcular_total(),
                 pedido.data.isoformat(timespec="seconds")))
            self.conexao.execute(
                "DELETE FROM itens_pedido WHERE pedido_numero = ?", (pedido.numero,))
            self.conexao.executemany(
                "INSERT INTO itens_pedido (pedido_numero, produto_id, quantidade, "
                "subtotal) VALUES (?, ?, ?, ?)",
                [(pedido.numero, item.produto.id_produto, item.quantidade,
                  item.calcular_subtotal()) for item in pedido.itens])

    def listar_pedidos(self) -> list:
        """Retorna as linhas da tabela pedidos (o Restaurante monta os objetos)."""
        return self.conexao.execute(
            "SELECT * FROM pedidos ORDER BY numero").fetchall()

    def listar_itens_pedido(self, numero: int) -> list:
        return self.conexao.execute(
            "SELECT * FROM itens_pedido WHERE pedido_numero = ? ORDER BY id_item",
            (numero,)).fetchall()

    def excluir_pedido(self, numero: int) -> None:
        with self.conexao:
            self.conexao.execute("DELETE FROM pedidos WHERE numero = ?", (numero,))

    # --- consultas genéricas (usadas pelo Relatorio) --------------------
    def consultar(self, sql: str, parametros: tuple = ()) -> list:
        return self.conexao.execute(sql, parametros).fetchall()
