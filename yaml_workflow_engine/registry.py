"""
HandlerRegistry — registro de handlers por tipo de step.

Cada step YAML tem um campo `type:` que mapeia para um handler Python.
O registro conecta esses dois lados.
"""
from __future__ import annotations

from typing import Callable, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from yaml_workflow_engine.context import ExecutionContext

HandlerFn = Callable[[dict[str, Any], "ExecutionContext"], Optional[Any]]


class HandlerNaoRegistradoError(Exception):
    """Lançada quando um tipo de step não possui handler registrado."""

    def __init__(self, tipo: str, registrados: list[str]) -> None:
        self.tipo = tipo
        self.registrados = registrados
        super().__init__(
            f"Handler não registrado para o tipo '{tipo}'. "
            f"Disponíveis: {registrados}"
        )


class HandlerRegistry:
    """
    Registra e resolve handlers para tipos de steps YAML.

    Exemplo::

        registry = HandlerRegistry()

        @registry.registrar("log")
        def handler_log(step_config, ctx):
            print(step_config["mensagem"])

        @registry.registrar("http_get")
        def handler_http(step_config, ctx):
            import requests
            resposta = requests.get(step_config["url"])
            return resposta.json()
    """

    def __init__(self) -> None:
        self._handlers: dict[str, HandlerFn] = {}

    def registrar(self, tipo: str) -> Callable[[HandlerFn], HandlerFn]:
        """
        Decorador para registrar um handler por tipo.

        Args:
            tipo: Nome do tipo de step (deve bater com `type:` no YAML).

        Returns:
            O próprio decorador.
        """
        def decorador(fn: HandlerFn) -> HandlerFn:
            self._handlers[tipo] = fn
            return fn
        return decorador

    def registrar_handler(self, tipo: str, handler: HandlerFn) -> None:
        """Registra um handler diretamente (sem decorador)."""
        self._handlers[tipo] = handler

    def resolver(self, tipo: str) -> HandlerFn:
        """
        Retorna o handler para o tipo informado.

        Raises:
            HandlerNaoRegistradoError: Se o tipo não estiver registrado.
        """
        if tipo not in self._handlers:
            raise HandlerNaoRegistradoError(tipo, list(self._handlers.keys()))
        return self._handlers[tipo]

    def tipos_registrados(self) -> list[str]:
        """Retorna a lista de todos os tipos registrados."""
        return list(self._handlers.keys())

    def __contains__(self, tipo: str) -> bool:
        return tipo in self._handlers

    def __repr__(self) -> str:
        return f"HandlerRegistry(tipos={self.tipos_registrados()})"
