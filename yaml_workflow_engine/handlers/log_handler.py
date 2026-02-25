"""
Handler built-in para steps do tipo `log`.

Configuração YAML:

    - type: log
      mensagem: "Texto a exibir"
      nivel: info   # opcional: debug, info, warning, error (padrão: info)
"""
from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from yaml_workflow_engine.context import ExecutionContext

logger = logging.getLogger(__name__)

_NIVEIS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def executar(config: dict[str, Any], ctx: "ExecutionContext") -> None:
    """
    Exibe uma mensagem de log.

    Campos:
        mensagem (obrigatório): Texto a ser exibido.
        nivel (opcional): debug | info | warning | error. Padrão: info.
    """
    mensagem = config.get("mensagem", "")
    nivel_str = str(config.get("nivel", "info")).lower()
    nivel = _NIVEIS.get(nivel_str, logging.INFO)

    # Interpolação simples: {chave} → ctx.get("chave")
    try:
        mensagem = mensagem.format(**ctx.snapshot())
    except (KeyError, ValueError):
        pass  # mantém mensagem original se interpolação falhar

    logger.log(nivel, "[log] %s", mensagem)
    print(f"[LOG:{nivel_str.upper()}] {mensagem}")
