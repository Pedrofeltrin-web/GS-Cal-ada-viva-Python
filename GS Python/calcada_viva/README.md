# Calçada Viva - Parte de Python

**FIAP | Global Solution 2026.2 | CitizenTech | Disciplina: Python**

Plataforma colaborativa para registrar e acompanhar barreiras em calçadas (buracos, obstáculos, rampas inadequadas e iluminação insuficiente). Esta entrega é o programa de console em Python, que usa a mesma lógica do projeto completo (API, React e ESP32 são entregues nas outras disciplinas).

## Integrantes

| Nome | RM |
|------|-----|
| Gustavo Basso | 572623 |
| Kaick Lima | 574060 |
| Guilherme Sales | 572933 |
| Pedro Feltrin | 569038 |
| Guilherme Failla | 571611 |

Os nomes e RMs também aparecem no banner de abertura e no menu **8 - Sobre o projeto**. Para alterar, edite só o arquivo `integrantes.py`.

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```bash
python main.py              # usa dados.json (criado automaticamente)
python main.py outro.json   # usa outro arquivo de dados
```

Dica para demonstração: menu **7 - Dados de exemplo** carrega trechos, ocorrências e leituras simulados (marcados com `*` nas telas). Dá para removê-los depois pelo mesmo menu.

## Funcionalidades

| Menu | O que faz |
|------|-----------|
| 1 - Trechos | Cadastrar, listar, editar e remover trechos de calçada (CRUD) |
| 2 - Ocorrências | Registrar relatos por categoria e gravidade; consultar com filtros por trecho, categoria e status |
| 3 - Administração | Validar ou rejeitar relatos pendentes; registrar resolução; ver histórico de mudanças |
| 4 - Iluminação | Registrar leituras do LDR (ADC 12 bits) e classificar em Normal, Atenção, Crítico ou Falha |
| 5 - Índice de barreiras | Índice por trecho, ranking e exposição acumulada de um trajeto |
| 6 - Relatórios | Painel geral, por trecho, por categoria, por status e tempos médios de validação e resolução |
| 7 - Exemplos | Carrega ou remove dados simulados |
| 8 - Sobre | Projeto, integrantes e limitações |

### Fluxo de uma ocorrência

`pendente` -> `validada` ou `rejeitada`; `validada` -> `resolvida`. Cada mudança fica no histórico com data e observação. Só ocorrências **validadas** entram no índice, e as resolvidas saem do cálculo.

### Decisão baseada no sensor

O LDR participa de uma decisão: o estado da última leitura válida define a nota de iluminação do trecho (Normal = 0, Atenção = 3, Crítico = 5), que altera o índice de barreiras. Leituras com Falha (valor fora de 0 a 4095) são ignoradas no índice e contadas nos relatórios.

## Modelo matemático (experimental)

```
b(x) = (s(x) + o(x) + r(x) + l(x)) / 20      cada componente de 0 a 5, logo 0 <= b <= 1
B(L) = integral de 0 até L de b(x) dx        exposição acumulada ao longo do trajeto
```

Como `b` é constante dentro de cada trecho, a integral vira `B = soma de b_i x comprimento_i`. A barreira média do trajeto é `B / L`.

- `s` = buracos e irregularidades, `o` = obstáculos, `r` = rampas, `l` = iluminação.
- Cada componente usa a maior gravidade entre as ocorrências validadas da categoria.
- Faixas: Baixa (< 0,25), Moderada (< 0,50), Alta (>= 0,50).

**Limitações:** os pesos são iguais e foram definidos pelo grupo, sem validação estatística. O índice **não é um padrão oficial de acessibilidade**. O LDR mede somente a iluminação; as barreiras físicas vêm dos relatos da comunidade. Os dados de exemplo são simulados.

## Estrutura do código (interface, lógica e dados separados)

| Arquivo | Papel |
|---------|-------|
| `main.py` | Ponto de entrada |
| `interface.py` | Menus e telas (único que usa `input` e `print` para o fluxo) |
| `validacoes.py` | Leitura e validação de entradas (texto, inteiro, decimal, opção, confirmação) |
| `servicos.py` | Regras de negócio e CRUD, sem entrada nem saída |
| `calculos.py` | Estados do LDR, índice de barreiras, exposição acumulada e tempos |
| `persistencia.py` | Leitura e gravação do JSON (gravação segura, tratamento de arquivo corrompido) |
| `exemplos.py` | Dados simulados para demonstração |
| `integrantes.py` | Nomes e RMs do grupo |

## Persistência (JSON)

Os dados ficam em `dados.json` com as listas `trechos`, `ocorrencias` e `leituras` e contadores de ID. O arquivo é gravado após cada alteração, usando arquivo temporário para evitar perda. Se o JSON estiver corrompido, o programa guarda uma cópia `.corrompido` e inicia vazio.

## Uso de IA

Este código foi desenvolvido com apoio do Claude (Anthropic) a partir do planejamento do grupo. O grupo deve revisar, testar e adaptar o código e registrar aqui, conforme a exigência da disciplina, quais partes foram geradas com IA e como foram verificadas.
