import pytest

from app.modelos.bebida import Bebida
from app.modelos.cliente import Cliente
from app.modelos.item_pedido import ItemPedido
from app.modelos.pedido import Pedido
from app.modelos.prato import Prato


@pytest.fixture
def pedido():
    return Pedido(1, Cliente("Ana", "9999-0000", 1))


def test_cliente_exige_nome():
    with pytest.raises(ValueError):
        Cliente("   ", "123")


def test_item_calcula_subtotal():
    item = ItemPedido(Bebida("Suco", 8.0, 300, "suco"), 3)
    assert item.calcular_subtotal() == 24.0


@pytest.mark.parametrize("invalida", [0, -2, 1.5, True])
def test_item_quantidade_invalida(invalida):
    with pytest.raises(ValueError):
        ItemPedido(Bebida("Suco", 8.0, 300, "suco"), invalida)


def test_ct04_subtotal_e_desconto(pedido):
    prato = Prato("Parmegiana", 25.0, ["frango", "queijo"], 20)
    pedido.adicionar_item(prato, 2)
    pedido.aplicar_desconto(10)
    assert pedido.calcular_subtotal() == 50.0
    assert pedido.calcular_total() == 45.0


@pytest.mark.parametrize("invalido", [-1, 101, "10"])
def test_desconto_invalido_mantem_anterior(pedido, invalido):
    pedido.aplicar_desconto(5)
    with pytest.raises(ValueError):
        pedido.aplicar_desconto(invalido)
    assert pedido.desconto == 5


def test_desconto_e_privado(pedido):
    with pytest.raises(AttributeError):
        pedido.__desconto
    with pytest.raises(AttributeError):
        pedido.desconto = 50  # só via aplicar_desconto()


def test_nao_adiciona_produto_indisponivel(pedido):
    with pytest.raises(ValueError):
        pedido.adicionar_item(Bebida("Suco", 8.0, 300, "suco", disponivel=False))


def test_remover_item(pedido):
    pedido.adicionar_item(Bebida("Suco", 8.0, 300, "suco"))
    pedido.remover_item(0)
    assert pedido.itens == []
    with pytest.raises(IndexError):
        pedido.remover_item(0)


def test_ct03_status_invalido_mantem_estado(pedido):
    assert pedido.alterar_status("CANCELADO_TESTE") is False
    assert pedido.status == "pendente"


def test_status_avanca_mas_nao_volta(pedido):
    assert pedido.alterar_status("em preparo")
    assert pedido.alterar_status("entregue")  # pode pular etapas
    assert pedido.alterar_status("pronto") is False
    assert pedido.status == "entregue"


def test_validar_status_e_privado(pedido):
    with pytest.raises(AttributeError):
        pedido.__validar_status("pronto")
