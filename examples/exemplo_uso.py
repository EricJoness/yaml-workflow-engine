"""
Exemplo de uso do yaml-workflow-engine.

Demonstra:
  - Execução de workflow via arquivo YAML
  - Registro de handler customizado
  - Workflow com contexto compartilhado entre steps

Execute: python examples/exemplo_uso.py
"""
from yaml_workflow_engine import WorkflowEngine

# ── Exemplo 1: Workflow embutido com handler customizado ──────────────────

def exemplo_handler_customizado():
    print("\n" + "="*55)
    print("  Exemplo 1: Handler Customizado")
    print("="*55)

    engine = WorkflowEngine()

    @engine.registry.registrar("calcular_total")
    def handler_total(config, ctx):
        itens = config.get("itens", [])
        total = sum(itens)
        return {"total": total, "quantidade": len(itens)}

    resultado = engine.executar_yaml("""
    nome: Cálculo de Totais
    steps:
      - type: log
        mensagem: "Calculando totais..."

      - type: calcular_total
        itens: [10, 25, 7, 58]
        salvar_como: calculo

      - type: log
        mensagem: "Pronto!"
    """)

    print(f"\n  ✅ Sucesso: {resultado.teve_sucesso}")
    print(f"  🕐 Duração: {resultado.duracao_total_segundos:.3f}s")
    print(f"  📊 Contexto final: {resultado.contexto_final}")


# ── Exemplo 2: Workflow a partir de arquivo YAML ──────────────────────────

def exemplo_via_arquivo():
    import os
    print("\n" + "="*55)
    print("  Exemplo 2: Workflow via arquivo YAML")
    print("="*55)

    engine = WorkflowEngine(parar_na_falha=False)

    arquivo = os.path.join(os.path.dirname(__file__), "workflow_simples.yaml")

    try:
        resultado = engine.executar_arquivo(arquivo)
        print(f"\n  ✅ Sucesso: {resultado.teve_sucesso}")
        print(f"  📌 Steps: {resultado.total_sucesso}/{len(resultado.steps)} OK")
        print(f"  🕐 Duração: {resultado.duracao_total_segundos:.3f}s")
    except Exception as e:
        print(f"\n  ⚠️  Erro (sem conexão?): {e}")


if __name__ == "__main__":
    exemplo_handler_customizado()
    exemplo_via_arquivo()
