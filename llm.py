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


def _groq_chat(model: str, system_prompt: str, user_prompt: str) -> str:
    # Intenta leer la clave desde los Secrets seguros de Streamlit o del entorno
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    
    # Si no hay clave, usamos el modelo por defecto de Groq (Llama de Meta)
    # Puedes cambiar "llama3-8b-8192" por "qwen-2.5-coder-32b" si está disponible en tu plan de Groq
    target_model = "llama3-8b-8192" 
    
    payload = json.dumps({
        "model": target_model,
        "stream": False,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 320
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "https://groq.com",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return json.dumps({"error": f"Error de conexión a la nube: {str(e)}"})


def _simple_question_plan(latest_user_text: str, chat_history: List[Dict[str, str]]) -> List[str]:
    """Plan de preguntas concreto para evitar que un modelo pequeño pida al usuario diseñar la metodología."""
    text = " ".join(
        [m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"]
        + [latest_user_text]
    ).lower()

    # Etapa de idea temprana
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

    # Ya existe algo construido
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

    # Señales de mercado/usuario
    user_validation = any(x in text for x in [
        "cliente", "usuario", "empresa", "mercado", "no lo quiere", "no les interesa", "no comprarían", "no comprarian"
    ])
    if user_validation:
        return [
            "¿Con quién has hablado o probado la propuesta hasta ahora y qué te dijeron exactamente?",
            "¿Qué decision quieres tomar con esa información: entender la necesidad, ajustar la solución o comprobar intención de uso/compra?",
        ]

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
    Capa de interpretación conversacional adaptada para la nube con Groq.
    """
    # Forzamos a True en la nube para activar la IA funcional
    model = "groq"

    if not use_ai:
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
7. NO le preguntes al usuario que diseñe la solución metodológica que precisamente está buscando.
Retorna UNICAMENTE un objeto JSON con este formato:
{{"rationale": "razonamiento", "gaps": ["ID_BRECHA"], "non_tool_blocker": "ID_BLOQUEO o null", "questions": ["pregunta1"]}}
"""

        user_prompt = f"HISTORIAL DE CONVERSACIÓN:\n{history}\n\nÚLTIMO MENSAJE DEL USUARIO:\n{latest_user_text}"
        
        # Llamamos a nuestra nueva función de la nube
        ai_response = _groq_chat(model, instructions, user_prompt)
        
        parsed = _extract_json(ai_response)
        
        # Validaciones de seguridad para mantener la lógica original del motor
        if _questions_are_too_methodological(parsed.get("questions", [])):
            parsed["questions"] = _simple_question_plan(latest_user_text, chat_history)
            
        parsed["evidence"] = _sanitize_evidence(parsed.get("evidence", []), latest_user_text)
        return parsed

    except Exception:
        history_text = " ".join(
            m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"
        )
        return heuristic_diagnosis(latest_user_text, history_text)
