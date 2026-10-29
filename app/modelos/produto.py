"""Classe base dos itens do cardápio."""


class Produto:
    def __init__(self, nome: str, preco: float, disponivel: bool = True):
        self.nome = nome
        self.__preco = 0.0      # atributo privado
        self.preco = preco      # passa pelo setter, que valida
        self.disponivel = disponivel

    # --- encapsulamento do preço --------------------------------------
    @property
    def preco(self) -> float:
        return self.__preco

    @preco.setter
    def preco(self, valor: float) -> None:
        if not self._validar_preco(valor):
            raise ValueError("O preço deve ser um número maior que zero.")
        self.__preco = float(valor)

    def _validar_preco(self, valor: float) -> bool:
        """Método protegido: só deve ser usado pela classe e suas filhas."""
        return (
            isinstance(valor, (int, float))
            and not isinstance(valor, bool)
            and valor > 0
        )

    # --- comportamento (as filhas podem sobrescrever) -----------------
    def calcular_preco(self) -> float:
        return self.__preco

    def exibir_detalhes(self) -> str:
        status = "disponível" if self.disponivel else "indisponível"
        return f"{self.nome} — R$ {self.calcular_preco():.2f} ({status})"