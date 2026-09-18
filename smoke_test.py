"""Pruebas rápidas sin consumir la API de Groq."""

import sys
import types

if "groq" not in sys.modules:
    fake_groq = types.ModuleType("groq")
    fake_groq.Groq = type("Groq", (), {})
    sys.modules["groq"] = fake_groq

from engine import heuristic_diagnosis, methodology_qa, run_engine
from llm import coach_tool


def main() -> None:
    cases = {
        "No tengo presupuesto.": "action_service",
        "No sé quién compraría esto.": "tool",
        "Tengo una idea pero no sé si funciona; todavía no tengo prototipo.": "action_service",
    }
    for text, expected_type in cases.items():
        result = run_engine(heuristic_diagnosis(text))
        assert result["type"] == expected_type, (text, result)

    review = coach_tool(
        "IDE-001", "Árbol de Problemas", "Problema central", "no tengo dinero",
        {}, "", "", use_ai=False,
    )
    assert review["quality"] == "Por mejorar", review

    qa = methodology_qa()
    assert isinstance(qa, dict) and qa, qa
    print("OK: motor, reglas, revisión metodológica y archivos de datos")


if __name__ == "__main__":
    main()
