"""
WorkflowEngine — motor de execução de workflows definidos em YAML.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from yaml_workflow_engine.context import ExecutionContext
from yaml_workflow_engine.parser import YAMLParser
from yaml_workflow_engine.registry import HandlerRegistry, HandlerNaoRegistradoError

logger = logging.getLogger(__name__)


class StatusStep(str, Enum):
    SUCESSO = "sucesso"
    FALHA = "falha"
    PULADO = "pulado"


@dataclass
class ResultadoStep:
    """Resultado da execução de um step do workflow."""

    indice: int
    tipo: str
    status: StatusStep
    retorno: Any = None
    erro: Optional[Exception] = None
    duracao_segundos: float = 0.0

    @property
    def teve_sucesso(self) -> bool:
        return self.status == StatusStep.SUCESSO

    def __repr__(self) -> str:
        return (
            f"ResultadoStep(tipo={self.tipo!r}, "
            f"status={self.status.value!r}, "
            f"duracao={self.duracao_segundos:.2f}s)"
        )


@dataclass
class ResultadoWorkflow:
    """Resultado completo da execução de um workflow."""

    nome: str
    steps: list[ResultadoStep] = field(default_factory=list)
    duracao_total_segundos: float = 0.0
    contexto_final: dict[str, Any] = field(default_factory=dict)

    @property
    def teve_sucesso(self) -> bool:
        return all(r.teve_sucesso for r in self.steps)

    @property
    def total_sucesso(self) -> int:
        return sum(1 for r in self.steps if r.teve_sucesso)

    @property
    def total_falha(self) -> int:
        return sum(1 for r in self.steps if r.status == StatusStep.FALHA)

    def __repr__(self) -> str:
        return (
            f"ResultadoWorkflow(nome={self.nome!r}, "
            f"sucesso={self.total_sucesso}/{len(self.steps)}, "
            f"duracao={self.duracao_total_segundos:.2f}s)"
        )


class WorkflowEngine:
    """
    Executa workflows definidos em arquivos YAML.

    Cada step tem um `type:` que mapeia para um handler registrado.
    O resultado de cada handler é salvo no contexto com a chave `salvar_como`,
    se definida — caso contrário, usa o `type` como chave.

    Exemplo::

        engine = WorkflowEngine()

        @engine.registry.registrar("log")
        def log_handler(config, ctx):
            print(config.get("mensagem", ""))

        resultado = engine.executar_arquivo("workflow.yaml")
        print(resultado)

    Args:
        parar_na_falha: Interrompe o workflow ao primeiro erro (padrão: True).
        dados_iniciais: Dados pré-populados no contexto de execução.
    """

    def __init__(
        self,
        parar_na_falha: bool = True,
        dados_iniciais: Optional[dict[str, Any]] = None,
    ) -> None:
        self.parar_na_falha = parar_na_falha
        self._dados_iniciais = dados_iniciais or {}
        self.registry = HandlerRegistry()
        self.parser = YAMLParser()

        # Registrar handlers built-in
        self._registrar_handlers_builtin()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def executar_arquivo(
        self,
        caminho: str,
        dados_iniciais: Optional[dict[str, Any]] = None,
    ) -> ResultadoWorkflow:
        """
        Lê um arquivo YAML e executa o workflow.

        Args:
            caminho: Caminho para o arquivo .yaml.
            dados_iniciais: Contexto adicional para esta execução.

        Returns:
            ResultadoWorkflow com o resultado de cada step.
        """
        definicao = self.parser.carregar_arquivo(caminho)
        return self._executar(definicao, dados_iniciais)

    def executar_yaml(
        self,
        texto: str,
        dados_iniciais: Optional[dict[str, Any]] = None,
    ) -> ResultadoWorkflow:
        """
        Recebe YAML como string e executa o workflow.

        Args:
            texto: Conteúdo YAML do workflow.
            dados_iniciais: Contexto adicional para esta execução.

        Returns:
            ResultadoWorkflow com o resultado de cada step.
        """
        definicao = self.parser.carregar_texto(texto)
        return self._executar(definicao, dados_iniciais)

    # ------------------------------------------------------------------
    # Execução interna
    # ------------------------------------------------------------------

    def _executar(
        self,
        definicao: dict[str, Any],
        dados_iniciais: Optional[dict[str, Any]] = None,
    ) -> ResultadoWorkflow:
        nome = definicao.get("nome", "Workflow")
        steps_def = definicao["steps"]

        ctx_dados = {**self._dados_iniciais, **(dados_iniciais or {})}
        ctx = ExecutionContext(ctx_dados)

        resultado_workflow = ResultadoWorkflow(nome=nome)
        inicio_total = time.monotonic()

        logger.info("Iniciando workflow '%s' com %d step(s)", nome, len(steps_def))

        for idx, step_def in enumerate(steps_def):
            tipo = step_def["type"]
            resultado_step = self._executar_step(idx, tipo, step_def, ctx)
            resultado_workflow.steps.append(resultado_step)

            if resultado_step.teve_sucesso and resultado_step.retorno is not None:
                chave = step_def.get("salvar_como", tipo)
                ctx.set(chave, resultado_step.retorno)

            elif not resultado_step.teve_sucesso:
                logger.error(
                    "Step #%d '%s' falhou: %s", idx, tipo, resultado_step.erro
                )
                if self.parar_na_falha:
                    break

        resultado_workflow.duracao_total_segundos = time.monotonic() - inicio_total
        resultado_workflow.contexto_final = ctx.snapshot()

        logger.info(
            "Workflow '%s' finalizado: %d/%d OK em %.2fs",
            nome,
            resultado_workflow.total_sucesso,
            len(resultado_workflow.steps),
            resultado_workflow.duracao_total_segundos,
        )
        return resultado_workflow

    def _executar_step(
        self,
        indice: int,
        tipo: str,
        config: dict[str, Any],
        ctx: ExecutionContext,
    ) -> ResultadoStep:
        inicio = time.monotonic()
        logger.debug("Executando step #%d: type=%s", indice, tipo)

        try:
            handler = self.registry.resolver(tipo)
        except HandlerNaoRegistradoError as e:
            return ResultadoStep(
                indice=indice,
                tipo=tipo,
                status=StatusStep.FALHA,
                erro=e,
                duracao_segundos=time.monotonic() - inicio,
            )

        try:
            retorno = handler(config, ctx)
            return ResultadoStep(
                indice=indice,
                tipo=tipo,
                status=StatusStep.SUCESSO,
                retorno=retorno,
                duracao_segundos=time.monotonic() - inicio,
            )
        except Exception as e:
            return ResultadoStep(
                indice=indice,
                tipo=tipo,
                status=StatusStep.FALHA,
                erro=e,
                duracao_segundos=time.monotonic() - inicio,
            )

    # ------------------------------------------------------------------
    # Handlers built-in
    # ------------------------------------------------------------------

    def _registrar_handlers_builtin(self) -> None:
        from yaml_workflow_engine.handlers import log_handler, http_handler

        self.registry.registrar_handler("log", log_handler.executar)
        self.registry.registrar_handler("http_get", http_handler.executar)
