# Etapa 3 — Implementação e Documentação Técnica

## 1. Estrutura do código

```
Byte-a-Byte/
├── main.py                        # ponto de entrada (GUI ou --demo)
├── app/
│   ├── modelos/
│   │   ├── produto.py             # Produto (classe base)
│   │   ├── prato.py               # Prato(Produto)
│   │   ├── bebida.py              # Bebida(Produto)
│   │   ├── cliente.py             # Cliente
│   │   ├── item_pedido.py         # ItemPedido
│   │   └── pedido.py              # Pedido
│   ├── banco/banco_dados.py       # BancoDados (SQLite)
│   ├── restaurante.py             # Restaurante (Facade)
│   ├── relatorio.py               # Relatorio
│   └── interface/janela_principal.py  # telas em CustomTkinter
├── tests/                         # pytest (37 casos)
└── data/restaurante.db            # criado na primeira execução
```

### Como executar

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python main.py           # interface gráfica
python main.py --demo    # demonstração no terminal, com banco em memória
python -m pytest         # testes automatizados
```

## 2. Cumprimento dos requisitos de POO

| Requisito | Onde está no código |
|---|---|
| Mínimo de 5 classes | 9 classes de domínio e infraestrutura, mais 6 classes de interface |
| Herança | `class Prato(Produto)` e `class Bebida(Produto)` |
| Polimorfismo | `calcular_preco()` e `exibir_detalhes()` sobrescritos em `Prato` e `Bebida`. O cardápio chama `produto.exibir_detalhes()` sem saber o tipo concreto |
| Associação | `Pedido.cliente` → `Cliente`; `Pedido.itens` → `ItemPedido`; `ItemPedido.produto` → `Produto`; `Restaurante.banco` → `BancoDados` |
| Atributo privado | `Produto.__preco`, `Pedido.__desconto` |
| Método privado | `Pedido.__validar_status()`, `BancoDados.__criar_tabelas()` |
| Instanciação mínima | `main.py` cria `BancoDados` e `Restaurante`. Em `--demo`, cria também clientes, produtos e dois pedidos completos |

## 3. Bibliotecas utilizadas

| Biblioteca | Tipo | Para que serve no projeto |
|---|---|---|
| `customtkinter` | externa | Janela, abas (`CTkTabview`), campos (`CTkEntry`), menus (`CTkOptionMenu`), botões e caixas de texto com visual moderno e tema claro/escuro automático. |
| `tkinter.messagebox` | padrão | Diálogos de erro, aviso e confirmação. |
| `sqlite3` | padrão | Conexão com o banco, transações (`with conexao:`), consultas parametrizadas e `sqlite3.Row` para acessar colunas pelo nome. |
| `datetime` | padrão | Data/hora de criação do pedido e filtros de período do relatório. |
| `pathlib` | padrão | Caminho do arquivo do banco, independente do sistema operacional. |
| `sys` | padrão | Leitura do argumento `--demo`. |
| `pytest` | externa (dev) | Execução dos testes, *fixtures* (banco em memória) e parametrização de casos. |

## 4. Esquema do banco e operações CRUD

O schema é criado por `BancoDados.__criar_tabelas()` com `CREATE TABLE IF NOT
EXISTS`. As chaves estrangeiras são ativadas por `PRAGMA foreign_keys = ON`.

| Tabela | PK | FK | Colunas |
|---|---|---|---|
| `clientes` | `id_cliente` AUTOINCREMENT | — | `nome` TEXT NOT NULL, `telefone` TEXT |
| `produtos` | `id_produto` AUTOINCREMENT | — | `nome`, `preco` REAL CHECK > 0, `disponivel` INTEGER, `categoria` ('prato'/'bebida'), `ingredientes`, `tempo_preparo`, `volume_ml`, `tipo_bebida` |
| `pedidos` | `numero` | `cliente_id` → `clientes` | `status`, `desconto`, `valor_total`, `data` (ISO 8601) |
| `itens_pedido` | `id_item` AUTOINCREMENT | `pedido_numero` → `pedidos` (ON DELETE CASCADE), `produto_id` → `produtos` | `quantidade` CHECK > 0, `subtotal` |

| Operação | Clientes | Produtos | Pedidos |
|---|---|---|---|
| **Create** | `salvar_cliente()` sem id → `INSERT` | `salvar_produto()` sem id → `INSERT` | `salvar_pedido()` → `INSERT … ON CONFLICT` |
| **Read** | `listar_clientes()` | `listar_produtos()` (instancia `Prato` ou `Bebida`) | `listar_pedidos()`, `listar_itens_pedido()` |
| **Update** | `salvar_cliente()` com id → `UPDATE` | `salvar_produto()` com id → `UPDATE` | `salvar_pedido()` → `ON CONFLICT DO UPDATE` e regrava os itens |
| **Delete** | `excluir_cliente()` | `excluir_produto()` | `excluir_pedido()` (itens apagados em cascata) |

Integridade: um produto já vendido ou um cliente com pedidos não pode ser
excluído, porque a chave estrangeira impede. O `Restaurante` transforma esse
erro numa mensagem amigável e sugere desativar o produto em vez de apagá-lo.

## 5. Cenários de teste

Os testes ficam em `tests/` e rodam com `python -m pytest`. Resultado atual:
**37 testes, todos passando.**

| Código | Objetivo | Entrada | Resultado esperado | Teste |
|---|---|---|---|---|
| CT-01 | Validação de preço privado | Preços `0`, `-1`, `"10"`, `None`, `True`; setter com `-5` | `ValueError`; o preço anterior é mantido; `__preco` inacessível de fora | `test_preco_invalido_levanta_erro`, `test_setter_valida_preco`, `test_atributo_privado_nao_e_acessivel_direto` |
| CT-02 | Polimorfismo do cardápio | `exibir_detalhes()` em `Prato` e `Bebida` | Prato mostra ingredientes e tempo; Bebida mostra volume e tipo | `test_polimorfismo_exibir_detalhes` |
| CT-03 | Transição de status | `alterar_status("CANCELADO_TESTE")`; retroceder de "entregue" para "pronto" | Retorna `False` e mantém o status | `test_ct03_status_invalido_mantem_estado`, `test_status_avanca_mas_nao_volta` |
| CT-04 | Subtotal e desconto | 2 × R$ 25,00 com 10% de desconto | Subtotal R$ 50,00; total R$ 45,00 | `test_ct04_subtotal_e_desconto` |
| CT-05 | Persistência relacional | Gravar prato e bebida e reler; gravar pedido e recriar o `Restaurante` | Objetos recuperados com os mesmos dados e tipos | `test_ct05_salva_e_recupera_produtos`, `test_pedido_persiste_e_recarrega` |
| CT-06 | Regras do Facade | Alterar itens de pedido em preparo; avançar pedido vazio; excluir produto vendido | Operação recusada | `test_nao_altera_itens_de_pedido_em_preparo`, `test_pedido_vazio_nao_avanca`, `test_nao_remove_produto_vendido_nem_cliente_com_pedido` |
| CT-07 | Relatórios | Um pedido entregue e um pendente; filtro de datas | Faturamento só do entregue, ranking correto, filtro por período respeitado | `test_relatorio`, `test_relatorio_filtra_periodo` |

## 6. Limitações conhecidas

- **Usuário único:** não há login nem perfis (garçom, cozinha, gerente).
- **Sem cancelamento:** o fluxo de status não tem o estado "cancelado". O
  pedido pode ser excluído, mas o registro dele se perde.
- **Preço não é congelado:** se o preço de um produto muda, os pedidos antigos
  recalculam o total pelo novo preço ao serem exibidos. O valor salvo em
  `valor_total` e `subtotal` no banco continua sendo o da última gravação, e é
  esse valor que os relatórios usam.
- **Sem mesas nem pagamento:** o sistema não controla mesas, formas de
  pagamento nem emissão de cupom fiscal.
- **Desktop local:** o SQLite em arquivo serve uma única máquina. Vários
  terminais exigiriam um servidor de banco.
- **Cobertura de testes:** os testes cobrem modelos, banco e regras. A
  interface gráfica foi testada manualmente e por script, sem suíte automatizada.

## 7. Oportunidades de expansão

1. Guardar o **preço unitário no `ItemPedido`** no momento da venda.
2. Adicionar o status **"cancelado"** com motivo, mantendo o histórico.
3. Criar **controle de mesas** e **formas de pagamento**, com fechamento de caixa diário.
4. Adicionar **login com perfis** e uma tela específica para a cozinha (fila de pedidos em preparo).
5. **Exportar relatórios** em PDF/CSV e mostrar gráficos de vendas por dia.
6. **Controle de estoque** ligado aos ingredientes dos pratos, com indisponibilidade automática.
7. Migrar para PostgreSQL e uma **API web** para uso em tablets e celulares.

## 8. Roteiro sugerido para a apresentação

1. Mostrar o histórico de commits no GitHub e relacioná-lo ao cronograma da Etapa 1.
2. Rodar `python main.py --demo` para mostrar a criação dos objetos, o
   polimorfismo do cardápio, o status inválido recusado e o relatório.
3. Rodar `python -m pytest` e mostrar os 37 testes passando.
4. Abrir `python main.py` e fazer um fluxo completo: cadastrar cliente →
   cadastrar bebida → abrir pedido → adicionar itens → aplicar desconto →
   avançar status até "entregue" → gerar relatório.
5. Fechar e reabrir o programa para mostrar que os dados continuam salvos (SQLite).
