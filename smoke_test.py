from engine import heuristic_diagnosis, run_engine

cases = [
    "No tengo presupuesto.",
    "Tengo una idea pero una empresa me dijo que no sabe si vaya a funcionar. Solo tengo el documento.",
    "No sé quién compraría esto.",
]

for c in cases:
    d = heuristic_diagnosis(c)
    r = run_engine(d)
    print("\\nCASO:", c)
    print("DIAGNÓSTICO:", d)
    print("RESULTADO:", r.get("type"), "-", r.get("title"))

# Follow-up conversational test: must explain the recommended tool instead of re-diagnosing.
from engine import tool_followup_answer
follow = tool_followup_answer("¿y qué es las tres lupas?", active_tool_id="PRO-006", last_reason="Prueba")
assert follow and follow["tool_id"] == "PRO-006"
print("\\nFOLLOW-UP OK:", follow["answer"][:140])
