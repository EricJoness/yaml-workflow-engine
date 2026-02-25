# yaml-workflow-engine

> Engine para execução de workflows declarativos em YAML — defina automações como arquivos YAML e execute-as com handlers Python registráveis.

[![CI](https://github.com/seu-usuario/yaml-workflow-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/seu-usuario/yaml-workflow-engine/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## O problema

Automações codificadas diretamente em Python são difíceis de configurar, auditar e reutilizar por times não-técnicos. Qualquer mudança no fluxo exige alteração de código.

**yaml-workflow-engine** permite definir workflows em YAML simples, executados por handlers Python — separando **o que fazer** (configuração) de **como fazer** (código).

---

## Instalação

```bash
pip install yaml-workflow-engine
```

Ou em modo de desenvolvimento:

```bash
git clone https://github.com/seu-usuario/yaml-workflow-engine.git
cd yaml-workflow-engine
pip install -e ".[dev]"
```

---

## Conceitos fundamentais

| Conceito | Descrição |
|---|---|
| `WorkflowEngine` | Executa o workflow lendo YAML e despachando handlers |
| `HandlerRegistry` | Registra funções Python como handlers para cada `type:` |
| `YAMLParser` | Faz parse e validação do arquivo YAML |
| `ExecutionContext` | Dicionário compartilhado entre todos os steps do workflow |

---

## Uso rápido

**1. Defina seu workflow em YAML:**

```yaml
# workflow.yaml
nome: Pipeline de Dados

steps:
  - type: log
    mensagem: "Iniciando pipeline..."

  - type: http_get
    url: "https://api.exemplo.com/dados"
    salvar_como: resposta

  - type: log
    mensagem: "Dados recebidos com sucesso!"
```

**2. Execute com Python:**

```python
from yaml_workflow_engine import WorkflowEngine

engine = WorkflowEngine()
resultado = engine.executar_arquivo("workflow.yaml")

print(resultado)
# ResultadoWorkflow(nome='Pipeline de Dados', sucesso=3/3, duracao=0.43s)
```

---

## Registrando handlers customizados

```python
engine = WorkflowEngine()

@engine.registry.registrar("enviar_email")
def handler_email(config, ctx):
    destinatario = config["para"]
    assunto = config["assunto"]
    corpo = ctx.get("relatorio", {}).get("texto", "")
    # sua lógica de envio aqui
    return {"enviado": True, "destinatario": destinatario}
```

YAML correspondente:

```yaml
steps:
  - type: enviar_email
    para: "time@empresa.com"
    assunto: "Relatório Diário"
    salvar_como: email_resultado
```

---

## Handlers built-in

| Type | Descrição |
|---|---|
| `log` | Exibe mensagem no console (com interpolação de contexto) |
| `http_get` | Faz requisição GET e salva resposta no contexto |

---

## ExecutionContext — dados entre steps

```python
# Step A salva dados → Step B lê:
engine.executar_yaml("""
steps:
  - type: buscar_usuario
    id: 42
    salvar_como: usuario

  - type: log
    mensagem: "Usuário: {usuario}"  # interpolação automática
""")
```

---

## Contexto inicial e parar na falha

```python
engine = WorkflowEngine(
    parar_na_falha=True,          # interrompe no primeiro erro
    dados_iniciais={"env": "prod"}  # dados disponíveis para todos os steps
)

resultado = engine.executar_arquivo("workflow.yaml", dados_iniciais={"run_id": "abc123"})

print(resultado.teve_sucesso)           # True / False
print(resultado.total_sucesso)          # nº de steps OK
print(resultado.contexto_final)         # snapshot do contexto pós-execução
```

---

## Executar os testes

```bash
pytest tests/ -v --cov=yaml_workflow_engine
```

---

## Estrutura do projeto

```
yaml-workflow-engine/
├── yaml_workflow_engine/
│   ├── engine.py         # WorkflowEngine (motor principal)
│   ├── parser.py         # YAMLParser + validação
│   ├── registry.py       # HandlerRegistry
│   ├── context.py        # ExecutionContext
│   └── handlers/
│       ├── log_handler.py
│       └── http_handler.py
├── tests/
│   ├── test_engine.py
│   └── test_parser.py
└── examples/
    ├── workflow_simples.yaml
    └── exemplo_uso.py
```

---

## Roadmap

- [ ] Execução condicional de steps (`if: ctx.get("flag")`)
- [ ] Retry por step via configuração YAML
- [ ] Steps paralelos (`parallel: true`)
- [ ] Handler `subprocess` para executar comandos shell
- [ ] Validação de schema com Pydantic
- [ ] CLI: `ywe run workflow.yaml`

---

## Licença

MIT © Seu Nome
