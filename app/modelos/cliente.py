"""Clientes do restaurante."""


class Cliente:
    def __init__(self, nome: str, telefone: str, id_cliente: int = None):
        self.id_cliente = id_cliente  # preenchido ao salvar no banco
        self.nome = ""
        self.telefone = ""
        self.atualizar_dados(nome, telefone)

    def atualizar_dados(self, nome: str, telefone: str) -> None:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome do cliente é obrigatório.")
        self.nome = nome
        self.telefone = telefone.strip()

    def exibir_dados(self) -> str:
        telefone = self.telefone or "sem telefone"
        return f"#{self.id_cliente} {self.nome} ({telefone})"
