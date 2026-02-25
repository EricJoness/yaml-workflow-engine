"""
yaml-workflow-engine — Engine para execução de workflows definidos em YAML.

Permite descrever automações como arquivos YAML e executá-las
com handlers registráveis e contexto compartilhado entre steps.
"""

from yaml_workflow_engine.engine import WorkflowEngine
from yaml_workflow_engine.registry import HandlerRegistry
from yaml_workflow_engine.context import ExecutionContext
from yaml_workflow_engine.parser import YAMLParser

__version__ = "0.1.0"
__author__ = "Seu Nome"

__all__ = [
    "WorkflowEngine",
    "HandlerRegistry",
    "ExecutionContext",
    "YAMLParser",
]
