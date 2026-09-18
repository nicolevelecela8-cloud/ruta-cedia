from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from groq import Groq

from engine import GAPS, NON_TOOL_BLOCKERS, heuristic_diagnosis, normalize

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


def _apply_methodological_guardrails(result: Dict[str, Any], conversation: str) -> Dict[str, Any]:
    """Evita recomendaciones incompatibles con el estado y resultado buscado."""
    text = normalize(conversation)
    prototype_goal = any(cue in text for cue in (
        "primer prototipo", "crear el primer", "hacer el primer", "construir el primer",
        "fabricar el primer", "estoy en concepto", "fase de concepto", "etapa de concepto",
        "necesito crear", "quiero crear un prototipo",
    ))
    explicit_financial_block = any(cue in text for cue in (
        "no tengo presupuesto", "sin presupuesto", "no hay presupuesto",
        "no tengo financiamiento", "necesito financiamiento",
    ))

    # Si existe una solución definida y el resultado inmediato es construir el primer
    # prototipo, primero se especifica qué debe cumplir. No se regresa artificialmente
    # al Árbol de Problemas ni se convierte una mención vaga de recursos en financiamiento.
    if prototype_goal and not explicit_financial_block:
        result["possible_gap_ids"] = ["B-SOL-002"]
        result["non_tool_blocker"] = None
        result["objective"] = (
            "Definir los requisitos funcionales, constructivos y de seguridad que orientarán "
            "el diseño del primer prototipo."
        )
        result["requires_question"] = False
        result["questions"] = []
        result["confidence"] = "alta" if "prototipo" in text else "media"
    return result


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
  "evidence_detected": ["solo resultados, documentos, pruebas o decisiones que el usuario afirmó tener"],
  "missing_info": [],
  "requires_question": true,
  "questions": [],
  "confidence": "alta|media|baja"
}}

Solo diagnostica cuando el historial permite conocer: (a) qué existe actualmente,
(b) qué resultado inmediato busca y (c) qué lo está frenando o qué incertidumbre debe
resolver. Si falta uno de esos datos, no adivines: deja las brechas vacías, usa
requires_question=true y formula como máximo dos preguntas específicas. Un saludo no
cuenta como información del proyecto. No agregues texto fuera del JSON.

REGLAS DE CONTINUIDAD:
- Lee el historial como una sola conversación acumulativa.
- El mensaje actual puede ser la respuesta a la última pregunta del asistente; no lo
  analices como si fuera un proyecto nuevo.
- Incorpora las respuestas anteriores en la decisión.
- evidence_detected no puede copiar el mensaje ni registrar una idea, intención o deseo
  como evidencia. Solo incluye pruebas, prototipos, documentos, resultados, entrevistas,
  diseños, fórmulas u otras salidas que el usuario diga que realmente posee.
- Nunca repitas una pregunta que ya fue formulada o respondida.
- No cierres por número de turnos. Cierra únicamente cuando exista información suficiente.
- Pregunta por el estado y el bloqueo inmediato; no hagas cuestionarios genéricos sobre
  mercado, regulación, finanzas y propiedad intelectual al mismo tiempo.
- Usa B-PRO-001 únicamente cuando el problema central, sus causas y sus efectos sean la
  necesidad explícita. No lo uses como categoría genérica por falta de información.
- Si existe una solución concreta, está en concepto y el usuario quiere construir su primer
  prototipo, prioriza B-SOL-002 para definir los requisitos de la solución.
- No clasifiques "recursos" como financiamiento salvo que el usuario exprese claramente
  falta de presupuesto o necesidad de fondos.
"""

    user_prompt = (
        f"HISTORIAL DE CONVERSACIÓN anterior:\n{history}\n\n"
        f"ÚLTIMO MENSAJE EN VIVO DEL INVESTIGADOR:\n{latest_user_text}"
    )

    try:
        result = _normalize_diagnosis(_parse_json_object(_groq_chat(instructions, user_prompt)))
        return result
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
    normalized_value = normalize(value)
    normalized_field = normalize(field_label)
    if tool_id == "IDE-001" and "problema central" in normalized_field:
        resource_only = any(phrase in normalized_value for phrase in (
            "no tengo dinero", "falta dinero", "no hay dinero", "sin dinero",
            "no tengo presupuesto", "falta presupuesto", "sin presupuesto",
            "no tengo recursos", "falta de recursos",
        ))
        if resource_only:
            return {
                "quality": "Por mejorar",
                "feedback": (
                    "La frase describe una restricción de recursos, no el problema central "
                    "que el proyecto busca resolver. No debe aceptarse como adecuada para el árbol."
                ),
                "missing": (
                    "Define la situación negativa principal: quién está afectado, qué ocurre "
                    "y cuál es la consecuencia observable, sin redactarla como falta de dinero."
                ),
                "example": (
                    "Ejemplo ilustrativo: Los proyectos con potencial de innovación no avanzan "
                    "a una primera prueba por falta de una ruta técnica y recursos priorizados."
                ),
            }

    if not use_ai or not ai_is_configured():
        return {
            "quality": "Revisión básica",
            "feedback": "El campo contiene información, pero requiere revisión metodológica.",
            "missing": "Comprueba que sea específico, verificable y coherente con el propósito de la herramienta.",
            "example": "",
        }

    system_prompt = """
Eres un revisor metodológico estricto de Ruta CEDIA. Evalúa la calidad metodológica,
no solo si el texto es gramaticalmente válido. Una frase vaga, un síntoma, una causa,
una solución o una restricción de dinero no debe aprobarse como problema central.
Valora especificidad, coherencia con el campo, evidencia y utilidad para completar
la herramienta. Usa quality únicamente: "Sólido", "Por mejorar" o "Incompleto".
Responde solo JSON válido con las claves quality, feedback, missing y example.
Cada valor debe ser texto plano. example debe ser una frase breve marcada como
"Ejemplo ilustrativo:"; nunca devuelvas objetos, listas, código ni datos inventados
como si pertenecieran al proyecto.
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
        example = raw.get("example") or ""
        if isinstance(example, (dict, list)):
            example = "Ejemplo ilustrativo: revisa el campo siguiendo el criterio metodológico indicado."
        return {
            "quality": str(raw.get("quality") or "Por revisar"),
            "feedback": str(raw.get("feedback") or "No se recibió retroalimentación suficiente."),
            "missing": str(raw.get("missing") or ""),
            "example": str(example),
        }
    except Exception as exc:
        return {
            "quality": "Revisión no disponible",
            "feedback": "La IA no pudo revisar este campo en este momento.",
            "missing": "Conserva tu respuesta y vuelve a intentarlo.",
            "example": "",
            "_ai_error": str(exc),
        }
