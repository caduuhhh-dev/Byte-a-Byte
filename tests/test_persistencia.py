from datetime import date, datetime, timedelta

import pytest

from app.banco.banco_dados import BancoDados
from app.modelos.bebida import Bebida
from app.modelos.cliente import Cliente
from app.modelos.prato import Prato
from app.restaurante import Restaurante


@pytest.fixture
def banco():
    banco = BancoDados(":memory:")
    yield banco
    banco.fechar()


@pytest.fixture
def restaurante(banco):
    r = Restaurante("Teste", banco)
    r.cadastrar_prato("Lasanha", 30.0, ["massa", "queijo"], 25)
    r.cadastrar_bebida("Suco", 8.0, 300, "suco")
    r.cadastrar_cliente("Ana", "9999-0000")
    return r


def test_cria_tabelas(banco):
    tabelas = {l[0] for l in banco.consultar(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"clientes", "produtos", "pedidos", "itens_pedido"} <= tabelas


def test_ct05_salva_e_recupera_produtos(banco):
    banco.salvar_produto(Prato("Lasanha", 30.0, ["massa", "queijo"], 25))
    banco.salvar_produto(Bebida("Suco", 8.0, 300, "suco", disponivel=False))
    prato, bebida = banco.listar_produtos()
    assert isinstance(prato, Prato) and prato.ingredientes == ["massa", "queijo"]
    assert prato.tempo_preparo == 25 and prato.preco == 30.0
    assert isinstance(bebida, Bebida) and bebida.volume_ml == 300
    assert bebida.disponivel is False


def test_crud_cliente(banco):
    cliente = banco.salvar_cliente(Cliente("Ana", "1"))
    assert cliente.id_cliente is not None
    cliente.atualizar_dados("Ana Maria", "2")
    banco.salvar_cliente(cliente)
    [lido] = banco.listar_clientes()
    assert (lido.nome, lido.telefone) == ("Ana Maria", "2")
    banco.excluir_cliente(cliente.id_cliente)
    assert banco.listar_clientes() == []


def test_pedido_persiste_e_recarrega(banco, restaurante):
    lasanha, suco = restaurante.produtos
    pedido = restaurante.criar_pedido(restaurante.clientes[0])
    restaurante.adicionar_item_pedido(pedido, lasanha, 2)
    restaurante.adicionar_item_pedido(pedido, suco)
    restaurante.aplicar_desconto(pedido, 10)
    restaurante.alterar_status_pedido(pedido, "em preparo")

    recarregado = Restaurante("Teste", banco)  # mesmo banco, objetos novos
    [p] = recarregado.pedidos
    assert p.numero == pedido.numero and p.status == "em preparo"
    assert p.cliente is recarregado.clientes[0]
    assert [(i.produto.nome, i.quantidade) for i in p.itens] == [("Lasanha", 2), ("Suco", 1)]
    assert p.calcular_total() == pytest.approx(61.2)


def test_numero_de_pedido_incrementa(restaurante):
    cliente = restaurante.clientes[0]
    assert restaurante.criar_pedido(cliente).numero == 1
    assert restaurante.criar_pedido(cliente).numero == 2


def test_nao_altera_itens_de_pedido_em_preparo(restaurante):
    lasanha, _ = restaurante.produtos
    pedido = restaurante.criar_pedido(restaurante.clientes[0])
    restaurante.adicionar_item_pedido(pedido, lasanha)
    restaurante.alterar_status_pedido(pedido, "em preparo")
    with pytest.raises(ValueError):
        restaurante.adicionar_item_pedido(pedido, lasanha)


def test_pedido_vazio_nao_avanca(restaurante):
    pedido = restaurante.criar_pedido(restaurante.clientes[0])
    assert restaurante.alterar_status_pedido(pedido, "em preparo") is False


def test_nao_remove_produto_vendido_nem_cliente_com_pedido(restaurante):
    lasanha, suco = restaurante.produtos
    cliente = restaurante.clientes[0]
    pedido = restaurante.criar_pedido(cliente)
    restaurante.adicionar_item_pedido(pedido, lasanha)
    with pytest.raises(ValueError):
        restaurante.remover_produto(lasanha)
    with pytest.raises(ValueError):
        restaurante.remover_cliente(cliente)
    restaurante.remover_produto(suco)  # nunca vendido: pode remover
    assert suco not in restaurante.produtos


def test_excluir_pedido_remove_itens(banco, restaurante):
    lasanha, _ = restaurante.produtos
    pedido = restaurante.criar_pedido(restaurante.clientes[0])
    restaurante.adicionar_item_pedido(pedido, lasanha)
    restaurante.remover_pedido(pedido)
    assert banco.consultar("SELECT COUNT(*) FROM itens_pedido")[0][0] == 0


def test_relatorio(banco, restaurante):
    lasanha, suco = restaurante.produtos
    cliente = restaurante.clientes[0]
    entregue = restaurante.criar_pedido(cliente)
    restaurante.adicionar_item_pedido(entregue, lasanha, 2)
    restaurante.adicionar_item_pedido(entregue, suco, 1)
    restaurante.alterar_status_pedido(entregue, "entregue")
    pendente = restaurante.criar_pedido(cliente)
    restaurante.adicionar_item_pedido(pendente, suco, 5)

    relatorio = restaurante.gerar_relatorio()
    assert relatorio.quantidade_pedidos() == 2
    assert relatorio.faturamento_total() == 68.0  # só o entregue
    assert relatorio.pedidos_por_status() == {"entregue": 1, "pendente": 1}
    assert relatorio.produtos_mais_vendidos()[0] == ("Suco", 6, 48.0)
    assert "Faturamento" in relatorio.gerar_texto()


def test_relatorio_filtra_periodo(banco, restaurante):
    lasanha, _ = restaurante.produtos
    pedido = restaurante.criar_pedido(restaurante.clientes[0])
    pedido.data = datetime.now() - timedelta(days=10)
    restaurante.adicionar_item_pedido(pedido, lasanha)
    restaurante.alterar_status_pedido(pedido, "entregue")

    hoje = date.today()
    assert restaurante.gerar_relatorio(inicio=hoje).quantidade_pedidos() == 0
    antigo = restaurante.gerar_relatorio(fim=hoje - timedelta(days=5))
    assert antigo.faturamento_total() == 30.0
