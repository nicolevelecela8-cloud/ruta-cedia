from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from groq import Groq

from engine import GAPS, NON_TOOL_BLOCKERS, heuristic_diagnosis

DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
PREFERRED_GROQ_MODELS = (
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
)
_AVAILABLE_MODEL_IDS: set[str] | None = None


def _setting(name: str, default: str = "") -> str:
    """Lee variables locales o Streamlit Secrets sin exponerlas."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


def ai_is_configured() -> bool:
    return bool(_setting("GROQ_API_KEY"))


def _gap_catalog() -> str:
    return "\n".join(f"- {k}: {v.get('NOMBRE_BRECHA')}" for k, v in GAPS.items())


def _blocker_catalog() -> str:
    return "\n".join(f"- {k}: {v['label']}" for k, v in NON_TOOL_BLOCKERS.items())


def _resolve_model(client: Groq, configured_model: str) -> str:
    """Usa el modelo configurado si la clave tiene acceso; si no, elige uno disponible."""
    global _AVAILABLE_MODEL_IDS
    if _AVAILABLE_MODEL_IDS is None:
        response = client.models.list()
        _AVAILABLE_MODEL_IDS = {
            item.id for item in response.data
            if getattr(item, "id", None) and getattr(item, "active", True)
        }

    if configured_model in _AVAILABLE_MODEL_IDS:
        return configured_model
    for model_id in PREFERRED_GROQ_MODELS:
        if model_id in _AVAILABLE_MODEL_IDS:
            return model_id

    excluded_terms = ("whisper", "guard", "orpheus", "tts")
    usable = sorted(
        model_id for model_id in _AVAILABLE_MODEL_IDS
        if not any(term in model_id.lower() for term in excluded_terms)
    )
    if usable:
        return usable[0]
    raise RuntimeError("La clave de Groq no tiene acceso a ningún modelo de texto compatible.")


def _groq_chat(system_prompt: str, user_prompt: str, max_tokens: int = 900) -> str:
    """Conexión mediante el cliente oficial de Groq."""
    api_key = _setting("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Falta configurar GROQ_API_KEY en Streamlit Secrets.")
    configured_model = _setting("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    try:
        client = Groq(api_key=api_key, timeout=35.0, max_retries=2)
        target_model = _resolve_model(client, configured_model)
        request_options = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_completion_tokens": max_tokens,
            "stream": False,
        }
        if target_model.startswith("openai/gpt-oss"):
            request_options["reasoning_effort"] = "low"
            request_options["max_completion_tokens"] = max(max_tokens, 2000)

        response = client.chat.completions.create(
            **request_options,
        )
    except Exception as exc:
        raise RuntimeError(f"No fue posible completar la consulta con Groq: {exc}") from exc

    if not response.choices:
        raise RuntimeError("Groq respondió sin alternativas de texto.")
    message = response.choices[0].message
    content = message.content
    if not content:
        content = getattr(message, "reasoning", None) or getattr(message, "reasoning_content", None)
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Groq respondió sin contenido utilizable.")
    return content.strip()


def _parse_json_object(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.I | re.S)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("La respuesta no contiene un objeto JSON.")
    result = json.loads(cleaned[start:end + 1])
    if not isinstance(result, dict):
        raise ValueError("La respuesta JSON no es un objeto.")
    return result


def _normalize_diagnosis(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Unifica respuestas nuevas y antiguas con el contrato que usa app.py."""
    gap_ids = raw.get("possible_gap_ids", raw.get("gaps", []))
    if isinstance(gap_ids, str):
        gap_ids = [gap_ids]
    gap_ids = [gap for gap in (gap_ids or []) if gap in GAPS][:3]

    blocker = raw.get("non_tool_blocker")
    if blocker not in NON_TOOL_BLOCKERS:
        blocker = None

    questions = raw.get("questions") or []
    if isinstance(questions, str):
        questions = [questions]
    questions = [str(item).strip() for item in questions if str(item).strip()][:3]

    evidence = raw.get("evidence_detected") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    missing = raw.get("missing_info") or []
    if isinstance(missing, str):
        missing = [missing]

    enough = bool(gap_ids or blocker)
    requires_question = bool(raw.get("requires_question", not enough))
    if enough:
        requires_question = False
        questions = []

    return {
        "summary": str(raw.get("summary") or raw.get("rationale") or "Análisis completado.").strip(),
        "objective": str(raw.get("objective") or "Definir el siguiente avance verificable.").strip(),
        "possible_gap_ids": gap_ids,
        "non_tool_blocker": blocker,
        "evidence_detected": [str(item).strip() for item in evidence if str(item).strip()],
        "missing_info": [str(item).strip() for item in missing if str(item).strip()],
        "requires_question": requires_question,
        "questions": questions,
        "confidence": str(raw.get("confidence") or ("media" if enough else "baja")).lower(),
    }


def diagnose(
    latest_user_text: str,
    chat_history: List[Dict[str, str]],
    use_ai: bool = True,
) -> Dict[str, Any]:
    """Capa de interpretación conversacional dinámica con IA funcional."""
    
    if not use_ai or not ai_is_configured():
        history_text = " ".join(
            m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"
        )
        return heuristic_diagnosis(latest_user_text, history_text)

    # 1. Recuperamos el historial para que la IA tenga memoria de la conversación
    recent_history = list(chat_history[-8:])
    if recent_history and recent_history[-1].get("role") == "user" and recent_history[-1].get("content", "").strip() == latest_user_text.strip():
        recent_history = recent_history[:-1]
        
    history = "\n".join(
        f"{m.get('role','user').upper()}: {m.get('content','')}"
        for m in recent_history
    )

    # 2. Le damos las instrucciones de negocio y el catálogo a la IA
    instructions = f"""
Eres la capa de interpretación de Ruta CEDIA Innovación. Identifica la necesidad
actual del proyecto sin inventar evidencia, nivel de madurez, servicios ni resultados.

Para tu conocimiento metodológico, estas son las brechas tecnológicas del programa:
{_gap_catalog()}

Y estos son los bloqueos externos permitidos:
{_blocker_catalog()}

Responde EXCLUSIVAMENTE con un objeto JSON válido con este contrato exacto:

{{
  "summary": "Síntesis clara de lo entendido",
  "objective": "Siguiente resultado que necesita el usuario",
  "possible_gap_ids": [],
  "non_tool_blocker": null,
  "evidence_detected": [],
  "missing_info": [],
  "requires_question": true,
  "questions": [],
  "confidence": "alta|media|baja"
}}

Si hay información suficiente, selecciona como máximo tres identificadores permitidos
o un bloqueo y usa requires_question=false. Si falta información, no adivines: deja
las brechas vacías, usa requires_question=true y formula de una a tres preguntas
específicas. No agregues saludos ni texto fuera del JSON.
"""

    user_prompt = f"HISTORIAL DE CONVERSACIÓN anterior:\n{history}\n\nÚLTIMO MENSAJE EN VIVO DEL INVESTIGADOR:\n{latest_user_text}"

    try:
        return _normalize_diagnosis(_parse_json_object(_groq_chat(instructions, user_prompt)))
    except Exception as exc:
        history_text = " ".join(
            m.get("content", "") for m in chat_history[-8:] if m.get("role") == "user"
        )
        fallback = heuristic_diagnosis(latest_user_text, history_text)
        fallback["_ai_error"] = str(exc)
        return fallback


def coach_tool(
    tool_id: str,
    tool_name: str,
    field_label: str,
    value: str,
    answers: Dict[str, Any],
    purpose: str,
    steps: str,
    use_ai: bool = True,
) -> Dict[str, str]:
    """Revisa un campo sin inventar información del proyecto."""
    if not value.strip():
        return {
            "quality": "Incompleto",
            "feedback": "Este campo todavía está vacío.",
            "missing": "Escribe información real y verificable de tu proyecto.",
            "example": "",
        }
    if not use_ai or not ai_is_configured():
        return {
            "quality": "Revisión básica",
            "feedback": "El campo contiene información, pero requiere revisión metodológica.",
            "missing": "Comprueba que sea específico, verificable y coherente con el propósito de la herramienta.",
            "example": "",
        }

    system_prompt = """
Eres un revisor metodológico de Ruta CEDIA. Evalúa el campo sin inventar datos ni
convertir ejemplos en hechos. Responde solo JSON válido con las claves quality,
feedback, missing y example. El ejemplo debe identificarse como ilustrativo.
"""
    user_prompt = json.dumps({
        "tool_id": tool_id,
        "tool_name": tool_name,
        "purpose": purpose,
        "steps": steps,
        "field": field_label,
        "field_value": value,
        "other_answers": answers,
    }, ensure_ascii=False)
    try:
        raw = _parse_json_object(_groq_chat(system_prompt, user_prompt, max_tokens=500))
        return {
            "quality": str(raw.get("quality") or "Por revisar"),
            "feedback": str(raw.get("feedback") or "No se recibió retroalimentación suficiente."),
            "missing": str(raw.get("missing") or ""),
            "example": str(raw.get("example") or ""),
        }
    except Exception as exc:
        return {
            "quality": "Revisión no disponible",
            "feedback": "La IA no pudo revisar este campo en este momento.",
            "missing": "Conserva tu respuesta y vuelve a intentarlo.",
            "example": "",
            "_ai_error": str(exc),
        }
