"""Relatórios de faturamento e vendas, calculados direto no banco."""
from datetime import date

from app.banco.banco_dados import BancoDados


class Relatorio:
    def __init__(self, banco: BancoDados, inicio: date = None, fim: date = None):
        self.banco = banco
        self.inicio = inicio
        self.fim = fim

    def _filtro_periodo(self) -> tuple:
        """Monta o trecho WHERE do período (datas inclusivas)."""
        condicoes, parametros = ["1 = 1"], []
        if self.inicio:
            condicoes.append("date(p.data) >= ?")
            parametros.append(self.inicio.isoformat())
        if self.fim:
            condicoes.append("date(p.data) <= ?")
            parametros.append(self.fim.isoformat())
        return " AND ".join(condicoes), tuple(parametros)

    def faturamento_total(self) -> float:
        """Soma dos pedidos entregues no período."""
        where, params = self._filtro_periodo()
        linha = self.banco.consultar(
            f"SELECT COALESCE(SUM(p.valor_total), 0) FROM pedidos p "
            f"WHERE {where} AND p.status = 'entregue'", params)
        return round(linha[0][0], 2)

    def quantidade_pedidos(self) -> int:
        where, params = self._filtro_periodo()
        return self.banco.consultar(
            f"SELECT COUNT(*) FROM pedidos p WHERE {where}", params)[0][0]

    def ticket_medio(self) -> float:
        where, params = self._filtro_periodo()
        linha = self.banco.consultar(
            f"SELECT AVG(p.valor_total) FROM pedidos p "
            f"WHERE {where} AND p.status = 'entregue'", params)
        return round(linha[0][0] or 0.0, 2)

    def pedidos_por_status(self) -> dict:
        where, params = self._filtro_periodo()
        linhas = self.banco.consultar(
            f"SELECT p.status, COUNT(*) FROM pedidos p WHERE {where} "
            f"GROUP BY p.status", params)
        return {status: total for status, total in linhas}

    def produtos_mais_vendidos(self, limite: int = 5) -> list:
        """Lista de (nome, quantidade, receita) ordenada pela quantidade."""
        where, params = self._filtro_periodo()
        linhas = self.banco.consultar(
            f"SELECT pr.nome, SUM(i.quantidade), SUM(i.subtotal) "
            f"FROM itens_pedido i "
            f"JOIN pedidos p ON p.numero = i.pedido_numero "
            f"JOIN produtos pr ON pr.id_produto = i.produto_id "
            f"WHERE {where} GROUP BY pr.id_produto "
            f"ORDER BY SUM(i.quantidade) DESC, pr.nome LIMIT ?",
            params + (limite,))
        return [(nome, qtd, round(receita, 2)) for nome, qtd, receita in linhas]

    def gerar_texto(self) -> str:
        if self.inicio or self.fim:
            de = self.inicio.strftime("%d/%m/%Y") if self.inicio else "início"
            ate = self.fim.strftime("%d/%m/%Y") if self.fim else "hoje"
            periodo = f"{de} a {ate}"
        else:
            periodo = "todo o histórico"
        linhas = [
            f"RELATÓRIO — {periodo}",
            f"Pedidos registrados: {self.quantidade_pedidos()}",
            f"Faturamento (entregues): R$ {self.faturamento_total():.2f}",
            f"Ticket médio: R$ {self.ticket_medio():.2f}",
            "",
            "Pedidos por status:",
        ]
        por_status = self.pedidos_por_status()
        linhas += [f"  {s}: {por_status.get(s, 0)}"
                   for s in ("pendente", "em preparo", "pronto", "entregue")]
        linhas += ["", "Produtos mais vendidos:"]
        mais_vendidos = self.produtos_mais_vendidos()
        if not mais_vendidos:
            linhas.append("  (nenhuma venda no período)")
        linhas += [f"  {nome}: {qtd} un. — R$ {receita:.2f}"
                   for nome, qtd, receita in mais_vendidos]
        return "\n".join(linhas)
