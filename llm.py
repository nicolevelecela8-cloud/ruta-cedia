from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List

from engine import GAPS, NON_TOOL_BLOCKERS, heuristic_diagnosis


def _gap_catalog() -> str:
    return "\n".join(f"- {k}: {v.get('NOMBRE_BRECHA')}" for k, v in GAPS.items())


def _blocker_catalog() -> str:
    return "\n".join(f"- {k}: {v['label']}" for k, v in NON_TOOL_BLOCKERS.items())


def _groq_chat(system_prompt: str, user_prompt: str) -> str:
    """Conexión directa y fluida con el modelo Qwen en la nube de Groq."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    target_model = "qwen-2.5-coder-32b" 
    
    payload = json.dumps({
        "model": target_model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 600
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
        return data.get("choices", [{}]).get("message", {}).get("content", "")
    except Exception as e:
        return f"Error de comunicación con la IA en la nube: {str(e)}"


def diagnose(
    latest_user_text: str,
    chat_history: List[Dict[str, str]],
    use_ai: bool = True,
) -> Dict[str, Any]:
    """Capa de interpretación conversacional dinámica con IA funcional."""
    
    # Si explícitamente se apaga la IA, usamos las reglas fijas básicas
    if not use_ai:
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
Eres el asesor experto en innovación de Ruta CEDIA Digital. Tu trabajo es escuchar el proyecto o problema del investigador, entender en qué etapa está y guiarlo de manera intuitiva haciendo preguntas inteligentes y personalizadas en lenguaje natural.

Para tu conocimiento metodológico, estas son las brechas tecnológicas del programa:
{_gap_catalog()}

Y estos son los bloqueos externos permitidos:
{_blocker_catalog()}

REGLAS DE RESPUESTA:
1. Analiza el mensaje actual del usuario y su historial.
2. Si el usuario te cuenta una idea temprana o que apenas está haciendo la teoría (como vasos comestibles marinos), no asumas que tiene un prototipo. Hazle preguntas dinámicas creadas por ti en este instante para averiguar qué materiales planea usar, qué pruebas iniciales le gustaría hacer o qué apoyo teórico le falta.
3. Genera entre 1 y 2 preguntas de guía que sean completamente redactadas por ti, personalizadas para su caso específico.
4. Para comunicarte con el motor de Streamlit, debes responder EXCLUSIVAMENTE con un objeto JSON plano que tenga este formato exacto (asegúrate de que sea un JSON válido y no pongas introducciones ni saludos fuera del JSON):

{{
  "rationale": "Escribe aquí tu análisis corto del proyecto en tiempo real.",
  "gaps": [],
  "non_tool_blocker": null,
  "questions": ["Escribe aquí tu primera pregunta dinámica personalizada", "Escribe aquí tu segunda pregunta dinámica personalizada (opcional)"]
}}
"""

    user_prompt = f"HISTORIAL DE CONVERSACIÓN anterior:\n{history}\n\nÚLTIMO MENSAJE EN VIVO DEL INVESTIGADOR:\n{latest_user_text}"

    try:
        # Llamamos a Qwen en la nube
        ai_response = _groq_chat(instructions, user_prompt).strip()
        
        # Limpieza de seguridad por si la IA pone bloques de código markdown
        if ai_response.startswith("```"):
            ai_response = ai_response.strip("`")
            if ai_response.lower().startswith("json"):
                ai_response = ai_response[4:].strip()
        
        start = ai_response.find("{")
        end = ai_response.rfind("}")
        if start >= 0 and end > start:
            ai_response = ai_response[start:end + 1]
            
        parsed = json.loads(ai_response)
        return parsed

    except Exception as e:
        # Si la red o el JSON fallan por completo, devolvemos un formato básico con una pregunta dinámica de emergencia
        return {
            "rationale": "Análisis conversacional activo.",
            "gaps": [],
            "non_tool_blocker": None,
            "questions": [f"Interesante propuesta sobre tu proyecto. Cuéntame más detalles: ¿qué pasos has imaginado para avanzar desde el punto actual?"]
        }

def coach_tool(*args, **kwargs) -> Any:
    return {}
