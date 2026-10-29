# Etapa 1 — Proposta de Projeto

**Disciplina:** Programação Orientada a Objetos
**Projeto:** Sistema de Pedidos para Restaurante
**Equipe:** Byte a Byte

| Integrante | Papel principal |
|---|---|
| Carlos Eduardo Lopes de Rodrigues | Lógica de classes / POO |
| Leonardo Lague Bachernitsan | Interface gráfica (CustomTkinter) |
| Pedro Villela Monteiro | Banco de dados, relatórios e testes |

## 1. Identidade visual

**Nome:** "Byte a Byte" faz um trocadilho entre *byte* (unidade de informação) e
*bite* (mordida). A ideia é construir o sistema pedaço por pedaço, como uma
refeição servida prato a prato.

**Proposta de logotipo:** um prato visto de cima cuja borda é um anel de
código binário (`01100010`, o caractere "b" em ASCII). No centro ficam um
garfo e um cursor de texto (`|`) cruzados. Logotipo plano, em duas cores:

- Laranja-tomate `#E4572E`: apetite, cozinha.
- Azul-ardósia `#29335C`: tecnologia, confiabilidade.
- Fundo creme `#F3F1EA` nos materiais impressos.

**Tipografia sugerida:** *JetBrains Mono* no logotipo (remete a código) e
*Inter* nos textos dos relatórios e da interface.

## 2. Ambiente de desenvolvimento

| Ferramenta | Uso | Justificativa |
|---|---|---|
| **Python 3** | Linguagem do sistema | Exigida pela disciplina. Sintaxe clara e biblioteca padrão rica (inclui `sqlite3`). |
| **VS Code** | Editor | Gratuito e leve. Tem extensão oficial de Python (depuração, *linting* PEP 8, execução de testes) e integração nativa com Git. |
| **Git + GitHub** | Versionamento | Histórico de cada alteração, trabalho paralelo em *branches* e revisão por *pull requests*. Os commits servem de evidência do cronograma. |
| **CustomTkinter** | Interface gráfica | Construída sobre o Tkinter (já incluso no Python), com visual moderno, tema claro/escuro e API simples. Não exige navegador nem servidor. |
| **SQLite3** | Persistência | Banco relacional em arquivo único, sem instalação de servidor. O módulo `sqlite3` já vem no Python. Suporta SQL padrão, chaves estrangeiras e transações. |
| **pytest** | Testes automatizados | Sintaxe enxuta (`assert`), *fixtures* e parametrização de casos. |
| **Mermaid / draw.io** | Diagramas UML | O Mermaid é texto versionado junto com o código e renderizado pelo GitHub. O draw.io serve para a versão visual da apresentação. |

## 3. Proposta do problema

Restaurantes de pequeno porte costumam controlar os pedidos com comandas de
papel e o caixa com planilhas soltas. Isso gera problemas recorrentes:

- **Comandas perdidas ou ilegíveis**, que causam pratos errados e retrabalho na cozinha.
- **Erros de cálculo** no fechamento da conta, principalmente quando há descontos.
- **Falta de visibilidade do status:** o salão não sabe se o pedido está em preparo ou pronto.
- **Cardápio desatualizado:** itens em falta continuam sendo oferecidos.
- **Sem dados para decisão:** faturamento por período e produtos mais vendidos
  exigem somar planilhas à mão.

O **Sistema de Pedidos Byte a Byte** centraliza essas informações numa
aplicação desktop orientada a objetos. O sistema cuida de:

1. Cadastro de clientes.
2. Cardápio de pratos e bebidas, com controle de disponibilidade.
3. Abertura de pedidos com itens, quantidades e descontos.
4. Acompanhamento do status do pedido (pendente → em preparo → pronto → entregue).
5. Relatórios de faturamento e vendas por período.

Todos os dados ficam em um banco SQLite e continuam disponíveis entre as execuções.

## 4. Requisitos e fluxo de dados

### Requisitos funcionais

| ID | Requisito |
|---|---|
| RF01 | Cadastrar, editar, listar e remover clientes (nome e telefone). |
| RF02 | Cadastrar pratos (ingredientes, tempo de preparo) e bebidas (volume, tipo). |
| RF03 | Alterar preço e disponibilidade de produtos. Preços devem ser maiores que zero. |
| RF04 | Abrir pedido para um cliente e adicionar/remover itens com quantidade. |
| RF05 | Aplicar desconto percentual (0 a 100%) a um pedido. |
| RF06 | Alterar o status do pedido apenas para frente no fluxo. |
| RF07 | Gerar relatório de faturamento, ticket médio, pedidos por status e produtos mais vendidos, com filtro de período. |
| RF08 | Persistir todos os dados em banco SQLite. |

### Requisitos não funcionais

- 100% Python orientado a objetos, com pelo menos 5 classes, herança,
  polimorfismo, associação, atributos e métodos privados.
- Código seguindo a PEP 8, versionado no GitHub.
- Interface gráfica responsiva em CustomTkinter.

### Fluxo de dados

```
ENTRADAS (interface)            PROCESSAMENTO                   SAÍDAS
─────────────────────           ───────────────────             ──────────────────────
Cadastro de clientes   ─┐                                   ┌─► Lista de clientes
Cadastro de produtos   ─┼─► Restaurante (Facade) ──► regras ─┼─► Cardápio com detalhes
Itens, qtd., desconto  ─┤        │      de negócio nas       ├─► Comanda (itens, subtotal,
Mudança de status      ─┘        │      classes de domínio   │    desconto, total)
Período do relatório   ─────────►│                           ├─► Status do pedido
                                 ▼                           └─► Relatório financeiro
                            BancoDados (SQLite)
```

## 5. Cronograma e divisão de papéis

Período: **22/10 a 18/11**.

| Semana | Período | Atividades | Responsável principal |
|---|---|---|---|
| 1 | 22/10 – 28/10 | Proposta (Etapa 1), estrutura do repositório, classes `Produto`, `Prato`, `Bebida` | Todos / Carlos |
| 2 | 29/10 – 04/11 | Diagrama UML (Etapa 2), classes `Cliente`, `ItemPedido`, `Pedido`, `Restaurante`; esquema do banco | Carlos / Pedro |
| 3 | 05/11 – 11/11 | Classe `BancoDados` e CRUD, classe `Relatorio`, telas em CustomTkinter | Pedro / Leonardo |
| 4 | 12/11 – 18/11 | Integração, testes automatizados, documentação técnica (Etapa 3), ensaio da apresentação | Todos |

### Matriz de responsabilidade (RACI)

R = responsável, A = aprova, C = consultado, I = informado.

| Entrega | Carlos | Leonardo | Pedro |
|---|---|---|---|
| Classes de domínio (POO) | **R/A** | C | C |
| Diagrama UML | **R** | C | A |
| Interface CustomTkinter | C | **R/A** | I |
| Banco de dados SQLite | C | I | **R/A** |
| Relatórios | I | C | **R/A** |
| Testes automatizados | C | C | **R/A** |
| Documentação e apresentação | R | R | R |
