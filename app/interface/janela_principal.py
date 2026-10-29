"""Interface gráfica em CustomTkinter.

A janela só chama métodos do Restaurante (Facade): não executa SQL nem
mexe diretamente nas listas internas das entidades.
"""
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from app.modelos.pedido import Pedido
from app.restaurante import Restaurante


class ListaSelecao(ctk.CTkScrollableFrame):
    """Lista rolável em que o usuário escolhe um objeto por vez."""

    def __init__(self, master, ao_selecionar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.ao_selecionar = ao_selecionar
        self.variavel = ctk.IntVar(value=-1)
        self.objetos = []
        self.botoes = []

    def definir_itens(self, itens: list, manter_selecao: bool = True) -> None:
        """itens: lista de (texto, objeto)."""
        anterior = self.selecionado if manter_selecao else None
        for botao in self.botoes:
            botao.destroy()
        self.objetos = [obj for _, obj in itens]
        self.botoes = []
        self.variavel.set(-1)
        for indice, (texto, obj) in enumerate(itens):
            botao = ctk.CTkRadioButton(self, text=texto, variable=self.variavel,
                                       value=indice, command=self._selecionou)
            botao.pack(anchor="w", padx=6, pady=3)
            self.botoes.append(botao)
            if obj is anterior:
                self.variavel.set(indice)

    @property
    def selecionado(self):
        indice = self.variavel.get()
        return self.objetos[indice] if 0 <= indice < len(self.objetos) else None

    def _selecionou(self) -> None:
        if self.ao_selecionar:
            self.ao_selecionar(self.selecionado)


class AbaClientes(ctk.CTkFrame):
    def __init__(self, master, restaurante: Restaurante, ao_mudar):
        super().__init__(master, fg_color="transparent")
        self.restaurante = restaurante
        self.ao_mudar = ao_mudar

        formulario = ctk.CTkFrame(self)
        formulario.pack(side="left", fill="y", padx=(0, 10))
        ctk.CTkLabel(formulario, text="Cliente", font=("", 16, "bold")).pack(pady=(12, 8))
        self.nome = ctk.CTkEntry(formulario, placeholder_text="Nome", width=220)
        self.nome.pack(padx=12, pady=4)
        self.telefone = ctk.CTkEntry(formulario, placeholder_text="Telefone", width=220)
        self.telefone.pack(padx=12, pady=4)
        for texto, comando in (("Cadastrar", self.cadastrar),
                               ("Atualizar selecionado", self.atualizar),
                               ("Remover selecionado", self.remover),
                               ("Limpar campos", self.limpar)):
            ctk.CTkButton(formulario, text=texto, command=comando).pack(
                padx=12, pady=4, fill="x")

        self.lista = ListaSelecao(self, ao_selecionar=self.preencher,
                                  label_text="Clientes cadastrados")
        self.lista.pack(side="left", fill="both", expand=True)
        self.atualizar_lista()

    def atualizar_lista(self) -> None:
        self.lista.definir_itens([(c.exibir_dados(), c)
                                  for c in self.restaurante.clientes])

    def preencher(self, cliente) -> None:
        self.limpar(manter_selecao=True)
        self.nome.insert(0, cliente.nome)
        self.telefone.insert(0, cliente.telefone)

    def limpar(self, manter_selecao: bool = False) -> None:
        self.nome.delete(0, "end")
        self.telefone.delete(0, "end")
        if not manter_selecao:
            self.lista.variavel.set(-1)

    def cadastrar(self) -> None:
        if _tentar(lambda: self.restaurante.cadastrar_cliente(
                self.nome.get(), self.telefone.get())):
            self.limpar()
            self.ao_mudar()

    def atualizar(self) -> None:
        cliente = _exigir(self.lista.selecionado, "Selecione um cliente.")
        if cliente and _tentar(lambda: self.restaurante.atualizar_cliente(
                cliente, self.nome.get(), self.telefone.get())):
            self.ao_mudar()

    def remover(self) -> None:
        cliente = _exigir(self.lista.selecionado, "Selecione um cliente.")
        if (cliente and messagebox.askyesno("Confirmar", f"Remover {cliente.nome}?")
                and _tentar(lambda: self.restaurante.remover_cliente(cliente))):
            self.limpar()
            self.ao_mudar()


class AbaCardapio(ctk.CTkFrame):
    def __init__(self, master, restaurante: Restaurante, ao_mudar):
        super().__init__(master, fg_color="transparent")
        self.restaurante = restaurante
        self.ao_mudar = ao_mudar

        formulario = ctk.CTkFrame(self)
        formulario.pack(side="left", fill="y", padx=(0, 10))
        ctk.CTkLabel(formulario, text="Produto", font=("", 16, "bold")).pack(pady=(12, 8))
        self.categoria = ctk.CTkSegmentedButton(formulario, values=["Prato", "Bebida"],
                                                command=self._trocar_categoria)
        self.categoria.set("Prato")
        self.categoria.pack(padx=12, pady=4, fill="x")
        self.nome = ctk.CTkEntry(formulario, placeholder_text="Nome", width=220)
        self.nome.pack(padx=12, pady=4)
        self.preco = ctk.CTkEntry(formulario, placeholder_text="Preço (R$)", width=220)
        self.preco.pack(padx=12, pady=4)
        # Os dois campos extras mudam de significado conforme a categoria.
        self.extra1 = ctk.CTkEntry(formulario, width=220)
        self.extra1.pack(padx=12, pady=4)
        self.extra2 = ctk.CTkEntry(formulario, width=220)
        self.extra2.pack(padx=12, pady=4)
        self._trocar_categoria("Prato")
        for texto, comando in (("Cadastrar", self.cadastrar),
                               ("Alterar preço do selecionado", self.alterar_preco),
                               ("Ativar/desativar selecionado", self.alternar),
                               ("Remover selecionado", self.remover)):
            ctk.CTkButton(formulario, text=texto, command=comando).pack(
                padx=12, pady=4, fill="x")

        self.lista = ListaSelecao(self, label_text="Cardápio")
        self.lista.pack(side="left", fill="both", expand=True)
        self.atualizar_lista()

    def _trocar_categoria(self, categoria: str) -> None:
        if categoria == "Prato":
            dicas = ("Ingredientes (separados por vírgula)", "Tempo de preparo (min)")
        else:
            dicas = ("Volume (ml)", "Tipo (suco, refrigerante...)")
        for campo, dica in zip((self.extra1, self.extra2), dicas):
            campo.delete(0, "end")
            campo.configure(placeholder_text=dica)
        self.focus()  # devolve o placeholder aos campos vazios

    def atualizar_lista(self) -> None:
        self.lista.definir_itens([(p.exibir_detalhes(), p)
                                  for p in self.restaurante.produtos])

    def cadastrar(self) -> None:
        def acao():
            preco = _numero(self.preco.get(), "Preço")
            if self.categoria.get() == "Prato":
                ingredientes = [i.strip() for i in self.extra1.get().split(",")
                                if i.strip()]
                tempo = int(_numero(self.extra2.get(), "Tempo de preparo"))
                self.restaurante.cadastrar_prato(self.nome.get().strip(), preco,
                                                 ingredientes, tempo)
            else:
                volume = int(_numero(self.extra1.get(), "Volume"))
                self.restaurante.cadastrar_bebida(self.nome.get().strip(), preco,
                                                  volume, self.extra2.get().strip())

        if not self.nome.get().strip():
            messagebox.showwarning("Atenção", "Informe o nome do produto.")
        elif _tentar(acao):
            for campo in (self.nome, self.preco, self.extra1, self.extra2):
                campo.delete(0, "end")
            self.focus()
            self.ao_mudar()

    def alterar_preco(self) -> None:
        produto = _exigir(self.lista.selecionado, "Selecione um produto.")
        if produto and _tentar(lambda: self.restaurante.alterar_preco(
                produto, _numero(self.preco.get(), "Preço"))):
            self.ao_mudar()

    def alternar(self) -> None:
        produto = _exigir(self.lista.selecionado, "Selecione um produto.")
        if produto:
            self.restaurante.alterar_disponibilidade(produto, not produto.disponivel)
            self.ao_mudar()

    def remover(self) -> None:
        produto = _exigir(self.lista.selecionado, "Selecione um produto.")
        if (produto and messagebox.askyesno("Confirmar", f"Remover {produto.nome}?")
                and _tentar(lambda: self.restaurante.remover_produto(produto))):
            self.ao_mudar()


class AbaPedidos(ctk.CTkFrame):
    def __init__(self, master, restaurante: Restaurante, ao_mudar):
        super().__init__(master, fg_color="transparent")
        self.restaurante = restaurante
        self.ao_mudar = ao_mudar
        self.clientes = {}
        self.produtos = {}

        esquerda = ctk.CTkFrame(self, fg_color="transparent")
        esquerda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        novo = ctk.CTkFrame(esquerda)
        novo.pack(fill="x", pady=(0, 8))
        self.cliente = ctk.CTkOptionMenu(novo, values=[""])
        self.cliente.pack(side="left", padx=8, pady=8, fill="x", expand=True)
        ctk.CTkButton(novo, text="Novo pedido", width=110,
                      command=self.novo_pedido).pack(side="left", padx=8)
        self.lista = ListaSelecao(esquerda, ao_selecionar=lambda _: self.mostrar(),
                                  label_text="Pedidos")
        self.lista.pack(fill="both", expand=True)

        direita = ctk.CTkFrame(self)
        direita.pack(side="left", fill="both", expand=True)
        self.detalhes = ctk.CTkTextbox(direita, height=180, font=("Consolas", 13))
        self.detalhes.pack(fill="both", expand=True, padx=8, pady=8)

        linha_item = ctk.CTkFrame(direita, fg_color="transparent")
        linha_item.pack(fill="x", padx=8, pady=2)
        self.produto = ctk.CTkOptionMenu(linha_item, values=[""])
        self.produto.pack(side="left", fill="x", expand=True)
        self.quantidade = ctk.CTkEntry(linha_item, width=50)
        self.quantidade.insert(0, "1")
        self.quantidade.pack(side="left", padx=6)
        ctk.CTkButton(linha_item, text="Adicionar", width=90,
                      command=self.adicionar_item).pack(side="left")

        linha_remover = ctk.CTkFrame(direita, fg_color="transparent")
        linha_remover.pack(fill="x", padx=8, pady=2)
        self.item = ctk.CTkOptionMenu(linha_remover, values=[""])
        self.item.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(linha_remover, text="Remover item", width=110,
                      command=self.remover_item).pack(side="left", padx=(6, 0))

        linha_desconto = ctk.CTkFrame(direita, fg_color="transparent")
        linha_desconto.pack(fill="x", padx=8, pady=2)
        self.desconto = ctk.CTkEntry(linha_desconto, placeholder_text="Desconto (%)")
        self.desconto.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(linha_desconto, text="Aplicar desconto", width=130,
                      command=self.aplicar_desconto).pack(side="left", padx=(6, 0))

        linha_status = ctk.CTkFrame(direita, fg_color="transparent")
        linha_status.pack(fill="x", padx=8, pady=2)
        self.status = ctk.CTkOptionMenu(linha_status, values=list(Pedido.STATUS_VALIDOS))
        self.status.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(linha_status, text="Alterar status", width=130,
                      command=self.alterar_status).pack(side="left", padx=(6, 0))

        ctk.CTkButton(direita, text="Excluir pedido", fg_color="#b23b3b",
                      hover_color="#8f2f2f", command=self.remover_pedido).pack(
            padx=8, pady=(6, 8), fill="x")
        self.atualizar_lista()

    def atualizar_lista(self) -> None:
        self.clientes = {c.exibir_dados(): c for c in self.restaurante.clientes}
        _opcoes(self.cliente, list(self.clientes), "cadastre um cliente")
        self.produtos = {f"{p.nome} — R$ {p.calcular_preco():.2f}": p
                         for p in self.restaurante.produtos_disponiveis()}
        _opcoes(self.produto, list(self.produtos), "nenhum produto disponível")
        self.lista.definir_itens([
            (f"#{p.numero} {p.cliente.nome} — {p.status} — "
             f"R$ {p.calcular_total():.2f}", p)
            for p in reversed(self.restaurante.pedidos)])
        self.mostrar()

    def mostrar(self) -> None:
        pedido = self.lista.selecionado
        self.detalhes.configure(state="normal")
        self.detalhes.delete("1.0", "end")
        if pedido:
            self.detalhes.insert("1.0", pedido.exibir_detalhes())
            itens = [f"{i + 1}. {item.exibir_detalhes()}"
                     for i, item in enumerate(pedido.itens)]
            _opcoes(self.item, itens, "pedido sem itens")
            self.status.set(pedido.status)
        else:
            self.detalhes.insert("1.0", "Selecione ou crie um pedido.")
            _opcoes(self.item, [], "nenhum pedido selecionado")
        self.detalhes.configure(state="disabled")

    def _pedido(self):
        return _exigir(self.lista.selecionado, "Selecione um pedido.")

    def novo_pedido(self) -> None:
        cliente = self.clientes.get(self.cliente.get())
        if _exigir(cliente, "Cadastre/selecione um cliente primeiro."):
            pedido = self.restaurante.criar_pedido(cliente)
            self.ao_mudar()
            self.lista.variavel.set(self.lista.objetos.index(pedido))
            self.mostrar()

    def adicionar_item(self) -> None:
        pedido = self._pedido()
        produto = self.produtos.get(self.produto.get())
        if pedido and _exigir(produto, "Selecione um produto.") and _tentar(
                lambda: self.restaurante.adicionar_item_pedido(
                    pedido, produto, int(_numero(self.quantidade.get(), "Quantidade")))):
            self.ao_mudar()

    def remover_item(self) -> None:
        pedido = self._pedido()
        if not pedido:
            return
        texto = self.item.get()
        if not texto[:1].isdigit():
            messagebox.showwarning("Atenção", "Selecione um item.")
            return
        indice = int(texto.split(".")[0]) - 1
        if _tentar(lambda: self.restaurante.remover_item_pedido(pedido, indice)):
            self.ao_mudar()

    def aplicar_desconto(self) -> None:
        pedido = self._pedido()
        if pedido and _tentar(lambda: self.restaurante.aplicar_desconto(
                pedido, _numero(self.desconto.get(), "Desconto"))):
            self.desconto.delete(0, "end")
            self.focus()
            self.ao_mudar()

    def alterar_status(self) -> None:
        pedido = self._pedido()
        if not pedido:
            return
        if self.restaurante.alterar_status_pedido(pedido, self.status.get()):
            self.ao_mudar()
        else:
            messagebox.showwarning(
                "Status inválido",
                "O status só pode avançar (pendente → em preparo → pronto → "
                "entregue) e o pedido precisa ter ao menos um item.")
            self.status.set(pedido.status)

    def remover_pedido(self) -> None:
        pedido = self._pedido()
        if pedido and messagebox.askyesno("Confirmar", f"Excluir o pedido #{pedido.numero}?"):
            self.restaurante.remover_pedido(pedido)
            self.ao_mudar()


class AbaRelatorio(ctk.CTkFrame):
    def __init__(self, master, restaurante: Restaurante):
        super().__init__(master, fg_color="transparent")
        self.restaurante = restaurante
        filtros = ctk.CTkFrame(self)
        filtros.pack(fill="x", pady=(0, 8))
        self.inicio = ctk.CTkEntry(filtros, placeholder_text="Início (dd/mm/aaaa)")
        self.inicio.pack(side="left", padx=8, pady=8)
        self.fim = ctk.CTkEntry(filtros, placeholder_text="Fim (dd/mm/aaaa)")
        self.fim.pack(side="left", padx=(0, 8))
        ctk.CTkButton(filtros, text="Gerar relatório", command=self.gerar).pack(side="left")
        self.texto = ctk.CTkTextbox(self, font=("Consolas", 13))
        self.texto.pack(fill="both", expand=True)
        self.gerar()

    def gerar(self) -> None:
        try:
            inicio, fim = _data(self.inicio.get()), _data(self.fim.get())
        except ValueError:
            messagebox.showerror("Erro", "Use datas no formato dd/mm/aaaa.")
            return
        texto = self.restaurante.gerar_relatorio(inicio, fim).gerar_texto()
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.configure(state="disabled")


class JanelaPrincipal(ctk.CTk):
    def __init__(self, restaurante: Restaurante):
        super().__init__()
        self.restaurante = restaurante
        self.title(f"{restaurante.nome} — Byte a Byte")
        self.geometry("1050x620")
        self.minsize(900, 520)

        abas = ctk.CTkTabview(self)
        abas.pack(fill="both", expand=True, padx=12, pady=12)
        self.clientes = AbaClientes(abas.add("Clientes"), restaurante, self.atualizar)
        self.cardapio = AbaCardapio(abas.add("Cardápio"), restaurante, self.atualizar)
        self.pedidos = AbaPedidos(abas.add("Pedidos"), restaurante, self.atualizar)
        self.relatorio = AbaRelatorio(abas.add("Relatório"), restaurante)
        for aba in (self.clientes, self.cardapio, self.pedidos, self.relatorio):
            aba.pack(fill="both", expand=True)
        abas.set("Pedidos")

    def atualizar(self) -> None:
        """Redesenha todas as abas depois de qualquer alteração."""
        self.clientes.atualizar_lista()
        self.cardapio.atualizar_lista()
        self.pedidos.atualizar_lista()
        self.relatorio.gerar()


# --- utilitários da interface -------------------------------------------
def _tentar(acao) -> bool:
    """Executa a ação e mostra a mensagem de erro de regra de negócio, se houver."""
    try:
        acao()
        return True
    except (ValueError, IndexError) as erro:
        messagebox.showerror("Erro", str(erro))
        return False


def _exigir(valor, mensagem: str):
    if valor is None:
        messagebox.showwarning("Atenção", mensagem)
    return valor


def _numero(texto: str, campo: str) -> float:
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        raise ValueError(f"{campo}: informe um número válido.") from None


def _data(texto: str):
    texto = texto.strip()
    return datetime.strptime(texto, "%d/%m/%Y").date() if texto else None


def _opcoes(menu: ctk.CTkOptionMenu, valores: list, vazio: str) -> None:
    atual = menu.get()
    menu.configure(values=valores or [vazio])
    menu.set(atual if atual in valores else (valores[0] if valores else vazio))
