"""
Handler built-in para steps do tipo `http_get`.

Configuração YAML:

    - type: http_get
      url: "https://api.exemplo.com/dados"
      salvar_como: resposta_api   # opcional
      timeout: 10                 # opcional (segundos)
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from yaml_workflow_engine.context import ExecutionContext


def executar(config: dict[str, Any], ctx: "ExecutionContext") -> dict[str, Any]:
    """
    Faz uma requisição HTTP GET e retorna o corpo da resposta.

    Campos:
        url (obrigatório): URL a ser requisitada.
        timeout (opcional): Timeout em segundos (padrão: 10).

    Returns:
        Dicionário com `status_code`, `headers` e `corpo` (JSON ou texto).

    Raises:
        ImportError: Se `requests` não estiver instalado.
        Exception: Se a requisição falhar.
    """
    try:
        import requests
    except ImportError as e:
        raise ImportError(
            "Pacote 'requests' não instalado. Execute: pip install requests"
        ) from e

    url: str = config["url"]
    # Interpolação simples de URL com contexto
    try:
        url = url.format(**ctx.snapshot())
    except (KeyError, ValueError):
        pass

    timeout: int = config.get("timeout", 10)

    resposta = requests.get(url, timeout=timeout)
    resposta.raise_for_status()

    try:
        corpo = resposta.json()
    except Exception:
        corpo = resposta.text

    return {
        "status_code": resposta.status_code,
        "headers": dict(resposta.headers),
        "corpo": corpo,
    }
