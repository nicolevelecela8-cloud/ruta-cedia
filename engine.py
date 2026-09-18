from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_FILE = Path(__file__).parent / "data" / "methodology.json"
ROUTE_FILE = Path(__file__).parent / "data" / "route_final.json"

NON_TOOL_BLOCKERS = {
    "validacion_tecnica": {
        "label": "Falta de evidencia de funcionamiento / validación técnica",
        "action": (
            "El bloqueo principal no parece resolverse con una plantilla. "
            "Se necesita generar evidencia de funcionamiento mediante una prueba, ensayo o prototipo "
            "acorde con el tipo de proyecto."
        ),
        "service": "Mentoría especializada para proyectos de innovación / apoyo técnico según disponibilidad y alcance",
        "support_tool_id": "VAL-002",
    },
    "financiamiento": {
        "label": "Restricción de presupuesto o financiamiento",
        "action": (
            "La necesidad principal es financiera. Antes de forzar una herramienta metodológica, "
            "conviene revisar alternativas de financiamiento, alcance mínimo de prueba y acompañamiento disponible."
        ),
        "service": "Orientación sobre financiamiento / acompañamiento CEDIA — por validar institucionalmente",
        "support_tool_id": None,
    },
    "propiedad_intelectual": {
        "label": "Duda de propiedad intelectual",
        "action": (
            "La necesidad requiere revisión especializada de propiedad intelectual. "
            "La IA no debe sustituir el criterio legal o institucional."
        ),
        "service": "Mentoría / servicio especializado de propiedad intelectual según disponibilidad",
        "support_tool_id": "TRA-003",
    },
    "regulatorio": {
        "label": "Duda regulatoria o de cumplimiento",
        "action": (
            "El proyecto necesita revisar requisitos regulatorios o de cumplimiento antes de continuar. "
            "No conviene sustituir esa revisión por una plantilla de innovación."
        ),
        "service": "Derivación a acompañamiento regulatorio/técnico — por validar CEDIA",
        "support_tool_id": None,
    },
    "validacion_usuarios": {
        "label": "Falta de validación con usuarios/clientes",
        "action": (
            "Hace falta obtener evidencia directa de uso, necesidad o respuesta del cliente. "
            "La siguiente acción es diseñar una prueba/entrevista/validación adecuada y registrar la evidencia."
        ),
        "service": "Acompañamiento para validación con usuarios/mercado — por validar CEDIA",
        "support_tool_id": "PRO-005",
    },
}

def load_methodology() -> Dict[str, List[Dict[str, Any]]]:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

M = load_methodology()
with ROUTE_FILE.open("r", encoding="utf-8") as f:
    ROUTE = json.load(f)

TOOLS = {r["ID_HERRAMIENTA"]: r for r in M["tools"]}
GAPS = {r["ID_BRECHA"]: r for r in M["gaps"]}
EVIDENCE_BY_TOOL = {r["ID_HERRAMIENTA_ORIGEN"]: r for r in M["evidence"]}
PREREQ_BY_TOOL = {r["ID_HERRAMIENTA"]: r for r in M["prerequisites"]}
PRIMARY_RULES = {
    r["ID_BRECHA"]: r
    for r in M["rules"]
    if str(r.get("ID_REGLA", "")).startswith("R-ACT-")
}
ITERATIVE_TOOLS = {
    r["ID_HERRAMIENTA_RECOMENDADA"]
    for r in M["rules"]
    if str(r.get("ID_REGLA", "")).startswith("R-ITR-")
}

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.lower()).strip()

def route_info_for_tool(tool_id: str) -> Dict[str, Any]:
    stage_raw = ROUTE.get("stage_by_tool", {}).get(tool_id)
    try:
        stage = int(stage_raw)
    except (TypeError, ValueError):
        return {}
    for item in ROUTE.get("route_defs", []):
        if int(item.get("orden", -1)) == stage:
            return {**item, "stage": stage, "route_abc": ROUTE.get("route_abc", {}).get(str(stage), ROUTE.get("route_abc", {}).get(stage))}
    return {}

def find_tool_in_text(text: str) -> Optional[str]:
    nt = normalize(text)
    if not nt:
        return None
    # Longest names first so e.g. "Tarjeta de Aprendizaje" wins over generic words.
    candidates = sorted(TOOLS.items(), key=lambda kv: len(kv[1].get("NOMBRE") or ""), reverse=True)
    for tid, tool in candidates:
        name = normalize(tool.get("NOMBRE") or "")
        if name and name in nt:
            return tid
    aliases = {
        "tres lupas": "PRO-006",
        "test card": "VAL-002",
        "tarjeta de experimento": "VAL-002",
        "learning card": "VAL-003",
        "tarjeta de aprendizaje": "VAL-003",
        "mapa de supuestos": "VAL-001",
        "libertad de operacion": "TRA-001",
        "freedom to operate": "TRA-001",
        "plan de maduracion": "MAD-001",
    }
    for alias, tid in aliases.items():
        if alias in nt:
            return tid
    return None

def tool_followup_answer(text: str, active_tool_id: Optional[str] = None, last_reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Responde preguntas de seguimiento sin volver a diagnosticar el proyecto."""
    nt = normalize(text)
    tid = find_tool_in_text(text) or active_tool_id
    followup_cues = [
        "que es", "que significa", "como la hago", "como lo hago", "como hago", "como se hace",
        "por que", "para que sirve", "que produce", "que resultado", "que evidencia",
        "que necesito", "explicame", "ayudame a aplic", "pasos"
    ]
    if not tid or not any(cue in nt for cue in followup_cues):
        return None
    t = tool_public_view(tid)
    route = route_info_for_tool(tid)
    if any(cue in nt for cue in ["como la hago", "como lo hago", "como hago", "como se hace", "pasos", "ayudame a aplic"]):
        answer = (
            f"**{t['name']}** se aplica así: {t.get('steps') or 'los pasos están por completar.'}\n\n"
            f"**Antes de empezar:** {t.get('prerequisite') or '—'}\n\n"
            f"**Al terminar deberías tener:** {t.get('evidence') or t.get('output') or '—'}"
        )
    elif "por que" in nt and last_reason:
        answer = f"Te la recomendé por esta razón: {last_reason}\n\nLa herramienta busca **{t.get('purpose') or 'resolver la brecha identificada'}**."
    elif any(cue in nt for cue in ["que produce", "que resultado", "que evidencia"]):
        answer = (
            f"**Resultado esperado:** {t.get('output') or '—'}\n\n"
            f"**Evidencia que debería quedar:** {t.get('evidence') or '—'}\n\n"
            f"**Criterio de calidad:** {t.get('evidence_quality') or '—'}"
        )
    elif "que necesito" in nt:
        answer = f"Para usar **{t['name']}** necesitas: {t.get('prerequisite') or '—'}"
    else:
        answer = (
            f"**{t['name']}** es una herramienta de **{t.get('family') or 'innovación'}**. "
            f"{t.get('description') or ''}\n\n"
            f"**Para qué sirve:** {t.get('purpose') or '—'}"
        )
    if route:
        answer += f"\n\nEn la ruta final se ubica principalmente en **{route.get('etapa')}**."
    return {"answer": answer, "tool_id": tid}

def tool_public_view(tool_id: str) -> Dict[str, Any]:
    t = TOOLS.get(tool_id, {})
    p = PREREQ_BY_TOOL.get(tool_id, {})
    e = EVIDENCE_BY_TOOL.get(tool_id, {})
    return {
        "id": tool_id,
        "name": t.get("NOMBRE"),
        "family": t.get("FAMILIA"),
        "description": t.get("DESCRIPCION_CORTA"),
        "purpose": t.get("PROPOSITO"),
        "when_use": t.get("CUANDO_USAR"),
        "when_not": t.get("CUANDO_NO_USAR"),
        "steps": t.get("PASOS_CLAVE"),
        "output": t.get("SALIDA_RESULTADO"),
        "evidence": e.get("NOMBRE_EVIDENCIA") or t.get("EVIDENCIA_GENERADA"),
        "evidence_quality": e.get("CRITERIO_CALIDAD"),
        "prerequisite": p.get("EVIDENCIA_O_INSUMO_NECESARIO") or t.get("ENTRADAS_PRERREQUISITOS"),
        "if_missing": p.get("SI_FALTA_EVIDENCIA"),
        "source": t.get("FUENTE_DOCUMENTO"),
        "validation": t.get("ESTADO_VALIDACION"),
        "route": route_info_for_tool(tool_id),
        "external_source": t.get("FUENTE_EXTERNA_PRINCIPAL"),
        "external_url": t.get("URL_FUENTE_EXTERNA"),
    }

def recommend_from_gap(gap_id: str, evidence_state: str = "No existe") -> Dict[str, Any]:
    rule = PRIMARY_RULES.get(gap_id)
    if not rule:
        return {
            "type": "manual_review",
            "title": "Revisión manual",
            "reason": "La brecha detectada todavía no tiene una regla primaria asociada.",
        }

    tool_id = rule["ID_HERRAMIENTA_RECOMENDADA"]
    tool = tool_public_view(tool_id)

    if evidence_state == "Válida y vigente":
        return {
            "type": "no_repeat",
            "title": "No repetir la herramienta",
            "gap_id": gap_id,
            "gap": GAPS.get(gap_id, {}).get("NOMBRE_BRECHA"),
            "reason": (
                "La evidencia asociada ya existe y se considera válida y vigente. "
                "La metodología indica reevaluar la brecha y el objetivo antes de repetir."
            ),
            "next": rule.get("SIGUIENTE_EVALUACION"),
        }

    if evidence_state == "Válida pero requiere actualización":
        if tool_id not in ITERATIVE_TOOLS:
            return {
                "type": "manual_review",
                "title": "Revisar si realmente debe repetirse",
                "gap_id": gap_id,
                "gap": GAPS.get(gap_id, {}).get("NOMBRE_BRECHA"),
                "reason": "La herramienta no está marcada como iterativa en la versión actual del motor.",
                "tool": tool,
            }
        title = f"Actualizar: {tool['name']}"
    else:
        title = tool["name"]

    return {
        "type": "tool",
        "title": title,
        "gap_id": gap_id,
        "gap": GAPS.get(gap_id, {}).get("NOMBRE_BRECHA"),
        "priority": rule.get("PRIORIDAD"),
        "reason": rule.get("JUSTIFICACION_PARA_USUARIO"),
        "tool": tool,
        "prerequisite": tool.get("prerequisite"),
        "if_missing": tool.get("if_missing"),
        "next": rule.get("SIGUIENTE_EVALUACION"),
        "criterion": rule.get("CRITERIO_SALIDA"),
        "validation_note": "Regla metodológica de la propuesta v12; validar institucionalmente antes de publicación/automatización oficial.",
    }

def recommend_non_tool(blocker_key: str) -> Dict[str, Any]:
    b = NON_TOOL_BLOCKERS[blocker_key]
    support = tool_public_view(b["support_tool_id"]) if b.get("support_tool_id") else None
    return {
        "type": "action_service",
        "title": b["label"],
        "reason": b["action"],
        "service": b["service"],
        "support_tool": support,
        "validation_note": "La derivación de servicio es una propuesta del proyecto y debe validarse con CEDIA.",
    }

def _contains_any(t: str, phrases: List[str]) -> bool:
    return any(p in t for p in phrases)

def heuristic_diagnosis(text: str, history_text: str = "") -> Dict[str, Any]:
    """
    Modo DEMO local. Sirve para probar la experiencia sin consumir una API.
    No sustituye la interpretación con IA.
    """
    t = normalize((history_text or "") + " " + (text or ""))

    # Non-tool blockers: check before forcing one of the 34 tools.
    # Validación técnica / prueba de funcionamiento.
    # Acepta lenguaje natural como "me dijeron que no saben si va a funcionar",
    # "no sé si funcionará", "solo tengo el documento", etc.
    uncertainty_cues = [
        "no se si", "no saben si", "dudan", "duda", "no confian",
        "no creen", "no estoy segura", "no estoy seguro", "me dijeron"
    ]
    function_cues = [
        "funciona", "funcionar", "funcionara", "sirve", "servira",
        "probar", "prueba", "validar", "demostrar", "prototipo"
    ]
    early_evidence_cues = [
        "solo tengo el documento", "solo tengo documento", "solo es un documento",
        "solo tengo la idea", "solo es una idea", "no tengo prototipo",
        "sin prototipo", "no lo he probado", "no hemos probado", "sin pruebas"
    ]

    technical_uncertainty = (
        (_contains_any(t, uncertainty_cues) and _contains_any(t, function_cues))
        or _contains_any(t, early_evidence_cues)
        or _contains_any(t, [
            "demostrar que funciona", "probar que funciona",
            "falta prueba tecnica", "evidencia tecnica", "validacion tecnica"
        ])
    )

    if technical_uncertainty:
        evidence = []
        if _contains_any(t, ["documento", "propuesta", "idea"]):
            evidence.append("Existe una propuesta/idea documentada.")
        if _contains_any(t, ["empresa", "cliente", "usuario"]):
            evidence.append("Existe al menos una conversación o reacción externa.")
        if not _contains_any(t, ["prototipo", "prueba", "ensayo", "funcionando"]):
            evidence.append("No se identifica todavía evidencia técnica de funcionamiento.")

        return {
            "summary": (
                "El bloqueo principal parece ser demostrar que la solución funciona. "
                "La reacción de la empresa expresa una incertidumbre técnica y todavía falta evidencia suficiente para responderla."
            ),
            "objective": "Diseñar la evidencia de funcionamiento que falta y decidir qué prueba o apoyo especializado se necesita.",
            "possible_gap_ids": [],
            "non_tool_blocker": "validacion_tecnica",
            "evidence_detected": evidence or ["La solución aún no cuenta con evidencia técnica suficiente."],
            "missing_info": [],
            "requires_question": False,
            "questions": [],
            "confidence": "alta",
        }

    if _contains_any(t, ["no tengo presupuesto", "no hay presupuesto", "sin presupuesto", "financiamiento", "fondos"]):
        return {
            "summary": "La principal restricción expresada es financiera.",
            "objective": "Encontrar una vía viable para continuar sin forzar una plantilla.",
            "possible_gap_ids": [],
            "non_tool_blocker": "financiamiento",
            "evidence_detected": [],
            "missing_info": ["Alcance mínimo de la próxima prueba", "Recursos ya disponibles"],
            "requires_question": False,
            "questions": [],
            "confidence": "alta",
        }

    if _contains_any(t, ["patente", "propiedad intelectual", "registrar mi idea", "proteger mi idea"]):
        return {
            "summary": "El usuario necesita orientación relacionada con propiedad intelectual.",
            "objective": "Determinar la ruta de protección o revisión institucional.",
            "possible_gap_ids": [],
            "non_tool_blocker": "propiedad_intelectual",
            "evidence_detected": [],
            "missing_info": [],
            "requires_question": False,
            "questions": [],
            "confidence": "alta",
        }

    if _contains_any(t, ["regulacion", "regulatorio", "permiso", "certificacion", "cumplimiento"]):
        return {
            "summary": "Existe una duda regulatoria o de cumplimiento que puede bloquear el avance.",
            "objective": "Clarificar requisitos regulatorios antes de continuar.",
            "possible_gap_ids": [],
            "non_tool_blocker": "regulatorio",
            "evidence_detected": [],
            "missing_info": [],
            "requires_question": False,
            "questions": [],
            "confidence": "media",
        }

    # If user is simply blocked, ask before classifying.
    if _contains_any(t, ["me bloquee", "me quede en seco", "no se que hacer", "no se por donde seguir",
                         "estoy estancado", "me estanque"]) and len(t.split()) < 45:
        return {
            "summary": "El usuario está estancado, pero todavía no hay información suficiente para identificar la causa.",
            "objective": "Entender qué está bloqueando el siguiente avance.",
            "possible_gap_ids": [],
            "non_tool_blocker": None,
            "evidence_detected": [],
            "missing_info": ["Estado actual", "Qué se ha probado", "Qué respuesta recibió del entorno"],
            "requires_question": True,
            "questions": [
                "¿Qué tienes hasta ahora: idea, investigación, prueba, prototipo o algo ya funcionando?",
                "¿Qué intentaste hacer antes de quedarte bloqueado y qué pasó?",
                "¿Qué te gustaría conseguir como siguiente resultado concreto?",
            ],
            "confidence": "baja",
        }

    patterns = [
        (["supuestos", "hipotesis criticas", "no se que validar primero", "que deberia probar primero"], "B-HIP-001"),
        (["como lo pruebo", "como probar", "disenar una prueba", "medir si funciona", "criterio de exito", "umbral"], "B-VAL-002"),
        (["ya hice una prueba", "hicimos una prueba", "ya probamos", "no se que aprendi", "que concluyo del experimento"], "B-VAL-003"),
        (["subir trl", "avanzar de trl", "llegar a trl", "plan de maduracion", "madurar la tecnologia"], "B-MAD-001"),
        (["libertad de operacion", "freedom to operate", "patente de terceros", "infringir patente", "derechos de terceros"], "B-PI-001"),
        (["cadena de valor", "quien fabrica", "quien distribuye", "actores de la cadena", "socios para escalar"], "B-ECO-001"),
        (["divulgar invencion", "divulgacion de invencion", "reportar a la otri", "informar a la otri"], "B-PI-002"),
        (["riesgos de adopcion", "barrera de adopcion", "cadena de suministro", "aceptacion del mercado", "licencia para operar"], "B-ADO-001"),
        (["no se que problema", "problema no esta claro", "no se exactamente que problema", "no se a quien afecta"], "B-PRO-003"),
        (["causas", "por que pasa", "causa raiz", "no entiendo por que"], "B-PRO-001"),
        (["no tengo ideas", "no se que solucion", "pocas ideas", "alternativas"], "B-IDE-001"),
        (["no se que investigar", "mucha informacion", "investigacion desordenada", "no se que informacion"], "B-INV-001"),
        (["preguntas", "entrevista", "que preguntar", "preguntas no sirven"], "B-INV-002"),
        (["no se quien compra", "no se quien compraria", "cliente ideal", "quien es mi cliente"], "B-MER-001"),
        (["que necesita el cliente", "necesidades del cliente", "trabajo del cliente", "para que lo usaria"], "B-USR-001"),
        (["frustraciones", "motivaciones", "como piensa el usuario", "como se siente"], "B-USR-002"),
        (["propuesta de valor", "no se si le aporta", "no le ven valor", "no lo necesita"], "B-VAL-001"),
        (["competencia", "competidores", "posicionamiento", "diferenciarme"], "B-POS-001"),
        (["modelo de negocio", "como gano dinero", "ingresos", "costos", "canales"], "B-NEG-001"),
        (["pitch", "presentar mi proyecto", "explicar mi proyecto", "no se como vender la idea"], "B-COM-002"),
        (["foda", "fortalezas", "debilidades", "amenazas", "oportunidades"], "B-EST-001"),
        (["requisitos", "especificaciones", "que debe cumplir"], "B-SOL-002"),
        (["que debe hacer mi solucion", "funciones de la solucion", "atributos de la solucion"], "B-SOL-001"),
        (["experiencia del usuario", "recorrido", "como usaria", "interaccion"], "B-PROTO-001"),
        (["deseabilidad", "factibilidad", "viabilidad", "vale la pena la idea"], "B-VIA-001"),
        (["servicio", "atencion", "prestacion del servicio", "experiencia de servicio"], "B-SER-001"),
        (["tendencias", "que esta cambiando", "futuro del sector"], "B-TEN-002"),
        (["oportunidad de innovacion", "aprovechar tendencia"], "B-TEN-003"),
    ]

    for phrases, gap_id in patterns:
        if _contains_any(t, phrases):
            return {
                "summary": f"Se detecta una necesidad compatible con: {GAPS[gap_id]['NOMBRE_BRECHA']}.",
                "objective": "Resolver la brecha principal expresada por el usuario.",
                "possible_gap_ids": [gap_id],
                "non_tool_blocker": None,
                "evidence_detected": [],
                "missing_info": [],
                "requires_question": False,
                "questions": [],
                "confidence": "media",
            }

    return {
        "summary": "Todavía no hay suficiente información para clasificar el bloqueo sin forzar una recomendación.",
        "objective": "Aclarar el siguiente obstáculo del proyecto.",
        "possible_gap_ids": [],
        "non_tool_blocker": None,
        "evidence_detected": [],
        "missing_info": ["Estado actual", "Evidencia disponible", "Objetivo inmediato"],
        "requires_question": True,
        "questions": [
            "¿Qué tienes construido o demostrado hasta ahora?",
            "¿Qué es exactamente lo que intentas conseguir como siguiente paso?",
            "¿Qué evidencia, comentario o resultado te hizo pensar que estás bloqueado?",
        ],
        "confidence": "baja",
    }

def run_engine(diagnosis: Dict[str, Any], evidence_state: str = "No existe") -> Dict[str, Any]:
    blocker = diagnosis.get("non_tool_blocker")
    if blocker in NON_TOOL_BLOCKERS:
        return recommend_non_tool(blocker)

    gap_ids = diagnosis.get("possible_gap_ids") or []
    if not gap_ids:
        return {
            "type": "need_more_info",
            "title": "Necesito entender un poco más",
            "reason": "La metodología no tiene evidencia suficiente para elegir una herramienta sin adivinar.",
        }

    return recommend_from_gap(gap_ids[0], evidence_state=evidence_state)


def next_checks_for_tool(tool_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve revisiones metodológicamente conectadas desde 07_DEPENDENCIAS.
    Solo usa relaciones que pueden sugerir una revisión posterior:
    - Antes de
    - Complementaria con
    No convierte estas relaciones en pasos obligatorios.
    """
    # Map each tool to its primary gap.
    gap_by_tool = {}
    for gap_id, rule in PRIMARY_RULES.items():
        tid = rule.get("ID_HERRAMIENTA_RECOMENDADA")
        if tid:
            gap_by_tool[tid] = gap_id

    out = []
    seen = set()
    for d in M["dependencies"]:
        if d.get("ID_HERRAMIENTA_ORIGEN") != tool_id:
            continue
        relation = d.get("RELACION")
        if relation not in ("Antes de", "Complementaria con"):
            continue
        dest = d.get("ID_HERRAMIENTA_DESTINO")
        if dest not in TOOLS or (relation, dest) in seen:
            continue
        seen.add((relation, dest))
        gid = gap_by_tool.get(dest)
        out.append({
            "dependency_id": d.get("ID_DEPENDENCIA"),
            "relation": relation,
            "tool_id": dest,
            "tool_name": TOOLS[dest].get("NOMBRE"),
            "gap_id": gid,
            "gap_name": GAPS.get(gid, {}).get("NOMBRE_BRECHA") if gid else None,
            "condition": d.get("CONDICION"),
            "evidence_required": d.get("EVIDENCIA_REQUERIDA"),
            "strength": d.get("FUERZA_DEPENDENCIA"),
        })
    # Directional "Antes de" first, then complementary.
    out.sort(key=lambda x: (0 if x["relation"] == "Antes de" else 1, x.get("tool_name") or ""))
    return out


def methodology_qa() -> Dict[str, Any]:
    """
    Control automático de consistencia estructural.
    No valida la corrección científica/institucional de las reglas.
    """
    tool_ids = set(TOOLS)
    gap_ids = set(GAPS)
    primary_rules = [
        r for r in M["rules"]
        if str(r.get("ID_REGLA", "")).startswith("R-ACT-")
    ]
    prereq_tools = {
        r.get("ID_HERRAMIENTA") for r in M["prerequisites"]
        if r.get("ID_HERRAMIENTA")
    }
    evidence_tools = {
        r.get("ID_HERRAMIENTA_ORIGEN") for r in M["evidence"]
        if r.get("ID_HERRAMIENTA_ORIGEN")
    }

    issues: List[str] = []

    # Every gap should have exactly one primary activation rule.
    rule_count_by_gap = {}
    for r in primary_rules:
        gid = r.get("ID_BRECHA")
        rule_count_by_gap[gid] = rule_count_by_gap.get(gid, 0) + 1

    for gid in sorted(gap_ids):
        count = rule_count_by_gap.get(gid, 0)
        if count != 1:
            issues.append(f"{gid}: tiene {count} reglas primarias; se esperaba 1.")

    # Every tool should be referenced by exactly one primary recommendation.
    rule_count_by_tool = {}
    for r in primary_rules:
        tid = r.get("ID_HERRAMIENTA_RECOMENDADA")
        rule_count_by_tool[tid] = rule_count_by_tool.get(tid, 0) + 1

    for tid in sorted(tool_ids):
        count = rule_count_by_tool.get(tid, 0)
        if count != 1:
            issues.append(f"{tid}: aparece {count} veces como herramienta primaria; se esperaba 1.")
        if tid not in prereq_tools:
            issues.append(f"{tid}: no tiene prerrequisito de evidencia.")
        if tid not in evidence_tools:
            issues.append(f"{tid}: no tiene evidencia de salida registrada.")

    # Dependency references must point to known tools.
    directional_adj: Dict[str, List[str]] = {}
    for d in M["dependencies"]:
        a = d.get("ID_HERRAMIENTA_ORIGEN")
        b = d.get("ID_HERRAMIENTA_DESTINO")
        if a and a not in tool_ids:
            issues.append(f"{d.get('ID_DEPENDENCIA')}: origen desconocido {a}.")
        if b and b not in tool_ids:
            issues.append(f"{d.get('ID_DEPENDENCIA')}: destino desconocido {b}.")
        if a in tool_ids and b in tool_ids and d.get("RELACION") in ("Antes de", "Bloquea a"):
            directional_adj.setdefault(a, []).append(b)

    # Detect directional cycles.
    color: Dict[str, int] = {}
    cycle_count = 0

    def dfs(u: str) -> bool:
        color[u] = 1
        for v in directional_adj.get(u, []):
            if color.get(v, 0) == 0:
                if dfs(v):
                    return True
            elif color.get(v) == 1:
                return True
        color[u] = 2
        return False

    for tid in sorted(tool_ids):
        if color.get(tid, 0) == 0 and dfs(tid):
            cycle_count += 1
            # Count at least one detected cycle; stop because the QA only needs a structural warning.
            break

    return {
        "tool_count": len(tool_ids),
        "gap_count": len(gap_ids),
        "tools_with_rule": sum(1 for tid in tool_ids if rule_count_by_tool.get(tid, 0) == 1),
        "gaps_with_rule": sum(1 for gid in gap_ids if rule_count_by_gap.get(gid, 0) == 1),
        "tools_with_prereq": len(tool_ids & prereq_tools),
        "tools_with_evidence": len(tool_ids & evidence_tools),
        "dependency_count": len(M["dependencies"]),
        "directional_cycles": cycle_count,
        "issues": issues,
    }
