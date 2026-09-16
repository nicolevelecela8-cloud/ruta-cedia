from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List

from engine import GAPS, NON_TOOL_BLOCKERS, heuristic_diagnosis


def _extract_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def _gap_catalog() -> str:
    return "\n".join(f"- {k}: {v.get('NOMBRE_BRECHA')}" for k, v in GAPS.items())


def _blocker_catalog() -> str:
    return "\n".join(f"- {k}: {v['label']}" for k, v in NON_TOOL_BLOCKERS.items())


def _ollama_chat(model: str, system_prompt: str, user_prompt: str) -> str:
    payload = json.dumps({
        "model": model,
        "stream": False,
        "format": "json",
        "keep_alive": "10m",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {
            "temperature": 0.0,
            "num_predict": 320,
            "num_ctx": 4096
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("message", {}).get("content", "")




def _simple_question_plan(latest_user_text: str, chat_history: List[Dict[str, str]]) -> List[str]:
    """Plan de preguntas concreto para evitar que un modelo pequeño pida al usuario diseñar la metodología."""
    text = " ".join(
        [m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"]
        + [latest_user_text]
    ).lower()

    # Etapa de idea temprana: no pedir causas/metodología; primero averiguar qué existe y qué busca lograr.
    early_idea = any(x in text for x in [
        "tengo la idea", "solo tengo la idea", "es una idea", "idea de una investig", "quiero investigar",
        "se me ocurrio", "se me ocurrió", "aun es una idea", "aún es una idea"
    ]) and not any(x in text for x in [
        "prototipo", "prueba de laboratorio", "probé", "probe", "ensayo", "piloto", "modelo funcional"
    ])
    if early_idea:
        return [
            "¿Por ahora tienes solo la idea, o ya existe algo concreto como un material, formulación, diseño, cálculo, prototipo o prueba?",
            "¿Qué quieres conseguir primero: definir mejor el problema de investigación, comprobar si la idea podría ser técnicamente viable o preparar una primera prueba?",
        ]

    # Ya existe algo construido y hay duda de funcionamiento.
    technical_validation = any(x in text for x in [
        "no sabe si funciona", "no saben si funciona", "no sabe si funcionara", "no sabe si funcionará",
        "funcionara en condiciones reales", "funcionará en condiciones reales", "solo laboratorio",
        "prototipo", "validar en condiciones reales", "no lo he probado", "no se si funciona", "no sé si funciona"
    ])
    if technical_validation:
        return [
            "¿En qué condiciones reales se usaría la solución y qué cambia respecto de la prueba que ya hiciste?",
            "¿Qué aspecto necesitas comprobar primero: desempeño técnico, resistencia/estabilidad, seguridad, aceptación del usuario u otro?",
        ]

    # Señales de mercado/usuario.
    user_validation = any(x in text for x in [
        "cliente", "usuario", "empresa", "mercado", "no lo quiere", "no les interesa", "no comprarían", "no comprarian"
    ])
    if user_validation:
        return [
            "¿Con quién has hablado o probado la propuesta hasta ahora y qué te dijeron exactamente?",
            "¿Qué decisión quieres tomar con esa información: entender la necesidad, ajustar la solución o comprobar intención de uso/compra?",
        ]

    # Preguntas generales que cualquier investigador puede contestar sin conocer metodología.
    return [
        "¿Qué tienes hoy de forma concreta: solo una idea, un documento, un diseño, un prototipo, resultados de prueba u otra evidencia?",
        "¿Cuál es el siguiente resultado que quieres conseguir con el proyecto?",
    ]


def _questions_are_too_methodological(questions: List[str]) -> bool:
    joined = " ".join(questions or []).lower()
    bad_cues = [
        "qué pruebas de campo deberían", "que pruebas de campo deberian",
        "cuáles son las causas específicas", "cuales son las causas especificas",
        "qué aspectos de la investigación no han sido explorados", "que aspectos de la investigacion no han sido explorados",
        "qué preguntas generaría", "que preguntas generaria",
        "qué metodología", "que metodologia", "qué herramienta", "que herramienta",
        "qué estrategia debería", "que estrategia deberia", "diseña", "diseñar la prueba"
    ]
    return any(cue in joined for cue in bad_cues)


def _sanitize_evidence(evidence: List[str], latest_user_text: str) -> List[str]:
    """Evita llamar evidencia a una idea o intención declarada."""
    out: List[str] = []
    for item in evidence or []:
        low = str(item).lower().strip()
        if not low:
            continue
        # Una idea, intención o deseo no es evidencia empírica.
        if any(cue in low for cue in ["tiene una idea", "idea de", "quiere investigar", "busca desarrollar", "pretende"]):
            continue
        out.append(str(item).strip())
    return out[:4]

def diagnose(
    latest_user_text: str,
    chat_history: List[Dict[str, str]],
    use_ai: bool = True,
) -> Dict[str, Any]:
    """
    Capa de interpretación conversacional.
    - Con OLLAMA_MODEL configurado usa un modelo local vía localhost.
    - Sin modelo local usa el clasificador DEMO, también local.
    Ninguna de las dos rutas sube la conversación a la nube.
    """
    model = os.getenv("OLLAMA_MODEL", "").strip()

    if not use_ai or not model:
        history_text = " ".join(
            m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"
        )
        return heuristic_diagnosis(latest_user_text, history_text)

    try:
        recent_history = list(chat_history[-10:])
        if recent_history and recent_history[-1].get("role") == "user" and recent_history[-1].get("content", "").strip() == latest_user_text.strip():
            recent_history = recent_history[:-1]
        history = "\n".join(
            f"{m.get('role','user').upper()}: {m.get('content','')}"
            for m in recent_history
        )

        instructions = f"""
Eres la capa de INTERPRETACIÓN CONVERSACIONAL de Ruta CEDIA Digital.
NO recomiendes herramientas. NO asignes TRL/CRL. NO inventes criterios CEDIA.
Tu trabajo es traducir lenguaje natural de investigadores a:
(a) una o varias brechas conocidas, o
(b) un bloqueo que no debe forzarse a una herramienta.

BRECHAS PERMITIDAS:
{_gap_catalog()}

BLOQUEOS NO-HERRAMIENTA PERMITIDOS:
{_blocker_catalog()}

Reglas:
1. Si el usuario solo dice "me bloqueé/no sé qué hacer", pregunta antes de clasificar.
2. Si no sabe si la solución funciona o necesita demostrar funcionamiento, prioriza el bloqueo de validación técnica; el motor decidirá si una Test Card puede ayudar como soporte.
3. Si el problema es presupuesto, usa non_tool_blocker="financiamiento".
4. No conviertas automáticamente todo problema en una de las 34 herramientas.
5. Haz entre 1 y 2 preguntas si falta información. Pregunta una cosa concreta por pregunta.
6. Las preguntas de aclaración deben pedir HECHOS que el usuario pueda conocer o describir: qué existe, qué se probó, en qué condiciones, qué resultado obtuvo, qué quiere conseguir, qué comentó la empresa/usuario o qué documentación tiene.
7. NO le preguntes al usuario que diseñe la solución metodológica que precisamente está buscando. Ejemplo incorrecto: «¿Qué pruebas de campo deberían realizarse?». Ejemplo correcto: «¿En qué condiciones reales se usaría el envase y qué fue exactamente lo que la empresa puso en duda?».
8. Distingue entre evidencia declarada y evidencia realmente demostrada.
9. Si el mensaje ya permite identificar una brecha principal con confianza media/alta, pregunta solo lo indispensable para elegir la acción; no conviertas el diagnóstico en un interrogatorio.
10. Si el proyecto está apenas en idea, NO preguntes por “causas del bloqueo”, “aspectos no explorados” ni “qué preguntas generaría”. Primero pregunta qué existe realmente y qué quiere lograr como siguiente resultado.
11. Una idea, intención o descripción del proyecto NO cuenta como evidencia. Solo registra como evidencia documentos, datos, pruebas, prototipos, entrevistas, resultados, observaciones u otros soportes concretos declarados.
12. Devuelve SOLO JSON válido, sin markdown, con esta forma exacta:
{{
  "summary": "resumen simple",
  "objective": "objetivo inmediato probable",
  "possible_gap_ids": ["B-..."],
  "non_tool_blocker": null,
  "evidence_detected": ["..."],
  "missing_info": ["..."],
  "requires_question": true,
  "questions": ["..."],
  "confidence": "baja|media|alta"
}}
"""
        user_input = f"""
CONVERSACIÓN RECIENTE:
{history}

MENSAJE MÁS RECIENTE:
{latest_user_text}
"""
        data = _extract_json(_ollama_chat(model, instructions, user_input))
        data["possible_gap_ids"] = [
            x for x in (data.get("possible_gap_ids") or []) if x in GAPS
        ][:3]
        blocker = data.get("non_tool_blocker")
        if blocker not in NON_TOOL_BLOCKERS:
            data["non_tool_blocker"] = None
        data["evidence_detected"] = _sanitize_evidence(data.get("evidence_detected") or [], latest_user_text)
        questions = (data.get("questions") or [])[:2]
        if data.get("requires_question") and (not questions or _questions_are_too_methodological(questions)):
            questions = _simple_question_plan(latest_user_text, chat_history)
        else:
            # En etapa de idea temprana usamos preguntas simples aunque el modelo haya generado otras aceptables.
            simple_plan = _simple_question_plan(latest_user_text, chat_history)
            combined_text = " ".join([m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"] + [latest_user_text]).lower()
            if any(x in combined_text for x in ["tengo la idea", "solo tengo la idea", "idea de una investig", "quiero investigar"]) and not any(x in combined_text for x in ["prototipo", "prueba de laboratorio", "probé", "probe", "ensayo", "piloto"]):
                questions = simple_plan
        data["questions"] = questions[:2]
        data["requires_question"] = bool(data.get("requires_question"))
        return data

    except Exception as exc:
        fallback = heuristic_diagnosis(
            latest_user_text,
            " ".join(m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"),
        )
        fallback["_local_ai_error"] = str(exc)
        return fallback


def coach_tool(
    tool_id: str,
    tool_name: str,
    field_label: str,
    current_value: str,
    answers: Dict[str, str],
    tool_purpose: str = "",
    tool_steps: str = "",
    use_ai: bool = True,
) -> Dict[str, Any]:
    """AI coach for one field of a tool. Never fabricates project facts."""
    model = os.getenv("OLLAMA_MODEL", "").strip()
    context = "\n".join(
        f"- {k}: {v}" for k, v in answers.items() if str(v or "").strip()
    )
    if not use_ai or not model:
        suggestion = (
            f"Completa **{field_label}** con información verificable de tu proyecto. "
            "Separa lo que sabes de lo que todavía supones y evita presentar una hipótesis como hecho."
        )
        if current_value.strip():
            suggestion = (
                f"Tu respuesta ya contiene contenido para **{field_label}**. Revísala para que sea específica, "
                "observable y sustentada en evidencia cuando corresponda."
            )
        return {
            "quality":"orientativa",
            "feedback":suggestion,
            "example":"Ejemplo ilustrativo: redacta una afirmación concreta y verificable adaptada a tu proyecto.",
            "missing":"Indica fuente, evidencia o supuesto cuando sea relevante.",
        }

    system_prompt = f"""
Eres un COACH METODOLÓGICO de Ruta CEDIA Digital.
Estás ayudando a desarrollar la herramienta: {tool_name} ({tool_id}).
Propósito metodológico: {tool_purpose}
Pasos oficiales/adaptados registrados en la base: {tool_steps}

Tu tarea es ayudar SOLO con el campo «{field_label}».
Reglas obligatorias:
1. No inventes datos, clientes, pruebas, métricas, resultados, patentes ni cifras del proyecto.
2. Distingue siempre entre hecho/evidencia, supuesto e información faltante.
3. Si el texto es débil, explica cómo mejorarlo; no lo completes como si fuera verdadero.
4. Puedes dar UN ejemplo claramente marcado como ilustrativo, no como respuesta real del usuario.
5. Responde SOLO JSON válido:
{{
  "quality":"vacío|incompleto|bien encaminado|sólido",
  "feedback":"retroalimentación breve y concreta",
  "example":"ejemplo ilustrativo",
  "missing":"qué evidencia o precisión falta"
}}
"""
    user_prompt = f"""
CONTEXTO YA COMPLETADO EN LA HERRAMIENTA:
{context or 'Sin otros campos completados.'}

CAMPO ACTUAL: {field_label}
RESPUESTA DEL USUARIO:
{current_value or '[vacío]'}
"""
    try:
        data = _extract_json(_ollama_chat(model, system_prompt, user_prompt))
        return {
            "quality":data.get("quality") or "orientativa",
            "feedback":data.get("feedback") or "Revisa que el contenido sea específico y verificable.",
            "example":data.get("example") or "",
            "missing":data.get("missing") or "",
        }
    except Exception as exc:
        return {
            "quality":"orientativa",
            "feedback":"No pude consultar la IA local en este momento. Conserva el campo y revisa que sea específico, verificable y basado en evidencia.",
            "example":"",
            "missing":"",
            "_local_ai_error":str(exc),
        }
