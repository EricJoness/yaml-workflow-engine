"""
ExecutionContext — contexto de execução compartilhado entre steps do workflow.

Funciona como um dicionário tipado que flui entre todos os handlers,
permitindo que cada step leia dados produzidos pelos anteriores.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional


class ExecutionContext:
    """
    Armazena e compartilha dados entre os steps de um workflow.

    Suporta acesso por chave (dict-like) e notação de ponto
    para subchaves aninhadas via `get_nested`.

    Exemplo::

        ctx = ExecutionContext({"ambiente": "producao"})
        ctx.set("usuario", "admin")
        ctx.get("usuario")           # → "admin"
        ctx.get("inexistente", "?")  # → "?"
    """

    def __init__(self, dados_iniciais: Optional[dict[str, Any]] = None) -> None:
        self._dados: dict[str, Any] = dados_iniciais.copy() if dados_iniciais else {}

    # ------------------------------------------------------------------
    # Acesso
    # ------------------------------------------------------------------

    def get(self, chave: str, padrao: Any = None) -> Any:
        """Retorna o valor associado à chave, ou `padrao` se não encontrado."""
        return self._dados.get(chave, padrao)

    def set(self, chave: str, valor: Any) -> None:
        """Armazena um valor no contexto com a chave informada."""
        self._dados[chave] = valor

    def get_nested(self, *chaves: str, padrao: Any = None) -> Any:
        """
        Acessa um valor aninhado por sequência de chaves.

        Exemplo::

            ctx.get_nested("login", "usuario")
            # equivale a ctx["login"]["usuario"]
        """
        atual: Any = self._dados
        for chave in chaves:
            if not isinstance(atual, dict):
                return padrao
            atual = atual.get(chave, padrao)
            if atual is padrao:
                return padrao
        return atual

    def atualizar(self, dados: dict[str, Any]) -> None:
        """Mescla um dicionário no contexto atual."""
        self._dados.update(dados)

    def tem(self, chave: str) -> bool:
        """Retorna True se a chave existe no contexto."""
        return chave in self._dados

    def snapshot(self) -> dict[str, Any]:
        """Retorna uma cópia superficial do estado atual do contexto."""
        return self._dados.copy()

    # ------------------------------------------------------------------
    # Protocol dict-like
    # ------------------------------------------------------------------

    def __getitem__(self, chave: str) -> Any:
        return self._dados[chave]

    def __setitem__(self, chave: str, valor: Any) -> None:
        self._dados[chave] = valor

    def __contains__(self, chave: object) -> bool:
        return chave in self._dados

    def __iter__(self) -> Iterator[str]:
        return iter(self._dados)

    def __len__(self) -> int:
        return len(self._dados)

    def __repr__(self) -> str:
        chaves = list(self._dados.keys())
        return f"ExecutionContext(chaves={chaves})"
