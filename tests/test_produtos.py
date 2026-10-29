import pytest

from app.modelos.bebida import Bebida
from app.modelos.prato import Prato
from app.modelos.produto import Produto


def test_produto_guarda_preco():
    p = Produto("Água", 3.5)
    assert p.preco == 3.5
    assert p.calcular_preco() == 3.5


@pytest.mark.parametrize("invalido", [0, -1, "10", None, True])
def test_preco_invalido_levanta_erro(invalido):
    with pytest.raises(ValueError):
        Produto("Teste", invalido)


def test_setter_valida_preco():
    p = Produto("Água", 3.5)
    with pytest.raises(ValueError):
        p.preco = -5
    assert p.preco == 3.5  # não mudou


def test_atributo_privado_nao_e_acessivel_direto():
    p = Produto("Água", 3.5)
    with pytest.raises(AttributeError):
        p.__preco


def test_prato_herda_de_produto():
    prato = Prato("Lasanha", 32.0, ["massa", "queijo"], 25)
    assert isinstance(prato, Produto)
    assert prato.calcular_preco() == 32.0


def test_polimorfismo_exibir_detalhes():
    itens = [
        Prato("Lasanha", 32.0, ["massa", "queijo"], 25),
        Bebida("Suco", 8.0, 300, "suco"),
    ]
    textos = [i.exibir_detalhes() for i in itens]
    assert "[Prato]" in textos[0] and "25 min" in textos[0]
    assert "[Bebida]" in textos[1] and "300 ml" in textos[1]