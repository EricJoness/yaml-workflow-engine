"""Testes do ExecutionContext."""
import pytest
from yaml_workflow_engine.context import ExecutionContext


def test_context_set_e_get():
    ctx = ExecutionContext()
    ctx.set("chave", "valor")
    assert ctx.get("chave") == "valor"


def test_context_padrao():
    ctx = ExecutionContext()
    assert ctx.get("inexistente") is None
    assert ctx.get("inexistente", "padrão") == "padrão"


def test_context_dados_iniciais():
    ctx = ExecutionContext({"a": 1, "b": 2})
    assert ctx["a"] == 1
    assert ctx["b"] == 2


def test_context_get_nested():
    ctx = ExecutionContext({"resposta": {"corpo": {"id": 99}}})
    assert ctx.get_nested("resposta", "corpo", "id") == 99


def test_context_get_nested_fallback():
    ctx = ExecutionContext()
    assert ctx.get_nested("nao", "existe", padrao="x") == "x"


def test_context_tem():
    ctx = ExecutionContext({"x": 0})
    assert ctx.tem("x") is True
    assert ctx.tem("y") is False


def test_context_atualizar():
    ctx = ExecutionContext({"a": 1})
    ctx.atualizar({"b": 2, "c": 3})
    assert ctx["b"] == 2
    assert ctx["c"] == 3


def test_context_snapshot_e_imutavel():
    ctx = ExecutionContext({"x": 1})
    snap = ctx.snapshot()
    snap["x"] = 999
    assert ctx["x"] == 1  # original não deve mudar


def test_context_contem():
    ctx = ExecutionContext({"k": "v"})
    assert "k" in ctx
    assert "z" not in ctx


def test_context_len():
    ctx = ExecutionContext({"a": 1, "b": 2})
    assert len(ctx) == 2
