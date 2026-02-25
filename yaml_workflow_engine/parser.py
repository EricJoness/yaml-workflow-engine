"""
YAMLParser — lê e valida arquivos de workflow YAML.

Estrutura esperada:

    nome: Meu Workflow
    descricao: Descrição opcional
    steps:
      - type: log
        mensagem: "Olá, mundo!"
      - type: http_get
        url: "https://api.exemplo.com/dados"
        salvar_como: resposta_api
"""
from __future__ import annotations

import os
from typing import Any

try:
    import yaml
except ImportError as e:
    raise ImportError(
        "PyYAML não instalado. Execute: pip install pyyaml"
    ) from e


class ErroDeValidacaoYAML(Exception):
    """Lançada quando o workflow YAML tem estrutura inválida."""


class YAMLParser:
    """
    Faz parsing e validação de workflows definidos em YAML.

    Exemplo::

        parser = YAMLParser()
        workflow = parser.carregar_arquivo("workflow.yaml")
        # workflow → {"nome": "...", "steps": [...]}

        workflow = parser.carregar_texto('''
          nome: Teste
          steps:
            - type: log
              mensagem: "Olá!"
        ''')
    """

    CAMPOS_OBRIGATORIOS_WORKFLOW = {"steps"}
    CAMPOS_OBRIGATORIOS_STEP = {"type"}

    def carregar_arquivo(self, caminho: str) -> dict[str, Any]:
        """
        Lê e valida um workflow a partir de um arquivo YAML.

        Args:
            caminho: Caminho absoluto ou relativo ao arquivo YAML.

        Returns:
            Dicionário com a definição do workflow.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            ErroDeValidacaoYAML: Se o YAML for inválido ou mal estruturado.
        """
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo de workflow não encontrado: {caminho!r}")

        with open(caminho, encoding="utf-8") as f:
            conteudo = f.read()

        return self.carregar_texto(conteudo, origem=caminho)

    def carregar_texto(
        self, texto: str, origem: str = "<string>"
    ) -> dict[str, Any]:
        """
        Faz parsing e validação de um workflow a partir de uma string YAML.

        Args:
            texto: Conteúdo YAML como string.
            origem: Identificador da origem (para mensagens de erro).

        Returns:
            Dicionário com a definição do workflow.

        Raises:
            ErroDeValidacaoYAML: Se o YAML for inválido ou mal estruturado.
        """
        try:
            dados = yaml.safe_load(texto)
        except yaml.YAMLError as e:
            raise ErroDeValidacaoYAML(
                f"Erro ao fazer parsing do YAML ({origem}): {e}"
            ) from e

        if not isinstance(dados, dict):
            raise ErroDeValidacaoYAML(
                f"O workflow deve ser um objeto YAML — recebido: {type(dados).__name__}"
            )

        self._validar_workflow(dados, origem)
        return dados

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------

    def _validar_workflow(self, dados: dict[str, Any], origem: str) -> None:
        ausentes = self.CAMPOS_OBRIGATORIOS_WORKFLOW - set(dados.keys())
        if ausentes:
            raise ErroDeValidacaoYAML(
                f"Campo(s) obrigatório(s) ausente(s) no workflow ({origem}): {ausentes}"
            )

        steps = dados["steps"]
        if not isinstance(steps, list):
            raise ErroDeValidacaoYAML(
                f"'steps' deve ser uma lista, recebido: {type(steps).__name__}"
            )

        if not steps:
            raise ErroDeValidacaoYAML("O workflow deve ter pelo menos um step.")

        for idx, step in enumerate(steps):
            self._validar_step(step, idx, origem)

    def _validar_step(
        self, step: Any, indice: int, origem: str
    ) -> None:
        if not isinstance(step, dict):
            raise ErroDeValidacaoYAML(
                f"Step #{indice} inválido ({origem}): deve ser um objeto, "
                f"recebido: {type(step).__name__}"
            )

        ausentes = self.CAMPOS_OBRIGATORIOS_STEP - set(step.keys())
        if ausentes:
            raise ErroDeValidacaoYAML(
                f"Step #{indice} ({origem}) está faltando campo(s): {ausentes}"
            )
