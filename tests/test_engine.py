"""Testes da engine e do parser do yaml-workflow-engine."""
from __future__ import annotations

import pytest
from yaml_workflow_engine.engine import WorkflowEngine, StatusStep
from yaml_workflow_engine.parser import YAMLParser, ErroDeValidacaoYAML
from yaml_workflow_engine.registry import HandlerNaoRegistradoError


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    return WorkflowEngine()


@pytest.fixture
def engine_sem_parar():
    return WorkflowEngine(parar_na_falha=False)


# ── Parser ─────────────────────────────────────────────────────────────────

def test_parser_valido():
    parser = YAMLParser()
    resultado = parser.carregar_texto("""
    nome: Teste
    steps:
      - type: log
        mensagem: "Olá!"
    """)
    assert resultado["nome"] == "Teste"
    assert len(resultado["steps"]) == 1


def test_parser_sem_steps_lanca_erro():
    parser = YAMLParser()
    with pytest.raises(ErroDeValidacaoYAML):
        parser.carregar_texto("nome: Teste")


def test_parser_steps_vazio_lanca_erro():
    parser = YAMLParser()
    with pytest.raises(ErroDeValidacaoYAML):
        parser.carregar_texto("steps: []")


def test_parser_step_sem_type_lanca_erro():
    parser = YAMLParser()
    with pytest.raises(ErroDeValidacaoYAML):
        parser.carregar_texto("""
        steps:
          - mensagem: "faltou o type"
        """)


# ── Engine ─────────────────────────────────────────────────────────────────

def test_engine_executa_step_log(engine, capsys):
    resultado = engine.executar_yaml("""
    nome: Teste Log
    steps:
      - type: log
        mensagem: "Mensagem de teste"
    """)

    assert resultado.teve_sucesso
    assert len(resultado.steps) == 1
    saida = capsys.readouterr().out
    assert "Mensagem de teste" in saida


def test_engine_nome_do_workflow(engine):
    resultado = engine.executar_yaml("""
    nome: Meu Workflow
    steps:
      - type: log
        mensagem: "ok"
    """)
    assert resultado.nome == "Meu Workflow"


def test_engine_handler_nao_registrado_para_na_falha(engine):
    resultado = engine.executar_yaml("""
    steps:
      - type: tipo_inexistente
    """)
    assert resultado.steps[0].status == StatusStep.FALHA
    assert not resultado.teve_sucesso


def test_engine_nao_parar_na_falha(engine_sem_parar):
    resultado = engine_sem_parar.executar_yaml("""
    steps:
      - type: tipo_inexistente
      - type: log
        mensagem: "este deve executar"
    """)
    assert len(resultado.steps) == 2
    assert resultado.steps[0].status == StatusStep.FALHA
    assert resultado.steps[1].status == StatusStep.SUCESSO


def test_engine_handler_customizado(engine):
    @engine.registry.registrar("somar")
    def handler_soma(config, ctx):
        return config["a"] + config["b"]

    resultado = engine.executar_yaml("""
    steps:
      - type: somar
        a: 40
        b: 2
        salvar_como: total
    """)

    assert resultado.teve_sucesso
    assert resultado.contexto_final["total"] == 42


def test_engine_contexto_compartilhado(engine):
    """Step posterior lê o resultado do anterior via ctx."""
    @engine.registry.registrar("definir_valor")
    def handler(config, ctx):
        return config["valor"]

    @engine.registry.registrar("ler_valor")
    def handler2(config, ctx):
        return ctx.get("minha_chave")

    resultado = engine.executar_yaml("""
    steps:
      - type: definir_valor
        valor: "hello"
        salvar_como: minha_chave
      - type: ler_valor
        salvar_como: lido
    """)

    assert resultado.contexto_final["lido"] == "hello"


def test_engine_dados_iniciais(engine):
    resultado = engine.executar_yaml(
        """
        steps:
          - type: log
            mensagem: "ambiente={ambiente}"
        """,
        dados_iniciais={"ambiente": "producao"},
    )
    assert resultado.teve_sucesso


def test_engine_duracao_preenchida(engine):
    resultado = engine.executar_yaml("""
    steps:
      - type: log
        mensagem: "ok"
    """)
    assert resultado.duracao_total_segundos >= 0
    assert resultado.steps[0].duracao_segundos >= 0
