"""Ponto de entrada do sistema de pedidos.

    python main.py          abre a interface gráfica
    python main.py --demo   roda uma demonstração no terminal (banco em memória)
"""
import sys

from app.banco.banco_dados import BancoDados
from app.restaurante import Restaurante


def popular_cardapio_inicial(restaurante: Restaurante) -> None:
    """Na primeira execução, deixa o cardápio com alguns itens de exemplo."""
    if restaurante.produtos:
        return
    restaurante.cadastrar_prato("Lasanha à bolonhesa", 32.0,
                                ["massa", "molho bolonhesa", "queijo"], 25)
    restaurante.cadastrar_prato("Risoto de cogumelos", 38.5,
                                ["arroz arbóreo", "cogumelos", "parmesão"], 30)
    restaurante.cadastrar_bebida("Suco de laranja", 8.0, 300, "suco")
    restaurante.cadastrar_bebida("Refrigerante lata", 6.0, 350, "refrigerante")


def demonstracao() -> None:
    banco = BancoDados(":memory:")
    restaurante = Restaurante("Byte a Byte Bistrô", banco)
    popular_cardapio_inicial(restaurante)

    print("Cardápio:")
    for produto in restaurante.produtos:
        print(" ", produto.exibir_detalhes())  # polimorfismo

    ana = restaurante.cadastrar_cliente("Ana Souza", "(51) 99999-0001")
    bruno = restaurante.cadastrar_cliente("Bruno Lima", "(51) 99999-0002")
    lasanha, risoto, suco, refri = restaurante.produtos

    pedido1 = restaurante.criar_pedido(ana)
    restaurante.adicionar_item_pedido(pedido1, lasanha, 2)
    restaurante.adicionar_item_pedido(pedido1, suco, 2)
    restaurante.aplicar_desconto(pedido1, 10)
    for status in ("em preparo", "pronto", "entregue"):
        restaurante.alterar_status_pedido(pedido1, status)

    pedido2 = restaurante.criar_pedido(bruno)
    restaurante.adicionar_item_pedido(pedido2, risoto)
    restaurante.adicionar_item_pedido(pedido2, refri)
    aceito = restaurante.alterar_status_pedido(pedido2, "CANCELADO_TESTE")
    print(f"\nStatus inválido aceito? {aceito}")

    print()
    print(pedido1.exibir_detalhes())
    print(pedido2.exibir_detalhes())
    print()
    print(restaurante.gerar_relatorio().gerar_texto())
    banco.fechar()


def main() -> None:
    if "--demo" in sys.argv:
        demonstracao()
        return

    # Importado aqui para que a demonstração rode mesmo sem CustomTkinter.
    from app.interface.janela_principal import JanelaPrincipal

    banco = BancoDados()
    restaurante = Restaurante("Byte a Byte Bistrô", banco)
    popular_cardapio_inicial(restaurante)
    janela = JanelaPrincipal(restaurante)
    try:
        janela.mainloop()
    finally:
        banco.fechar()


if __name__ == "__main__":
    main()
