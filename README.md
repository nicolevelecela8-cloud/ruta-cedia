# Ruta CEDIA Innovación — v5 FINAL

Versión local y portable del prototipo **Ruta CEDIA Digital**.

## Qué incorpora esta versión

- Diagnóstico conversacional con IA local mediante Ollama (`qwen2.5:3b-instruct`).
- Motor metodológico separado de la IA: brecha + evidencia + prerrequisitos + objetivo.
- 34 herramientas: 26 del inventario CEDIA + 8 propuestas benchmark.
- Ruta metodológica final de 7 etapas.
- **Desarrollo guiado de cada herramienta con IA**.
- **Vista visual dinámica de cómo debe quedar cada herramienta finalizada**.
- Retroalimentación de IA campo por campo sin inventar información del proyecto.
- Conexión orientativa entre herramientas y servicios/mecanismos de innovación.
- Pasaporte del proyecto.
- Exportación de cada herramienta en Markdown y JSON.
- Exportación de respaldo completo del proyecto.
- TRL/CRL orientativo basado en la metodología cargada.

## Principio de arquitectura

`Usuario → IA interpreta → motor metodológico decide → IA explica/acompaña → evidencia → reevaluación → servicio cuando corresponda`

La IA no selecciona libremente herramientas ni inventa evidencia.

## Ejecutar en Windows

1. Tener Python instalado.
2. Tener Ollama instalado.
3. Descargar el modelo una sola vez:

```powershell
ollama pull qwen2.5:3b-instruct
```

4. Ejecutar:

`INICIAR_RUTA_CEDIA.bat`

5. Abrir la URL local que muestre Streamlit.

## IA local

El archivo `.env` ya incluye:

`OLLAMA_MODEL=qwen2.5:3b-instruct`

La app consulta Ollama por `http://127.0.0.1:11434`.

## Desarrollo de herramientas

Desde **Explorar herramientas**, **Diagnóstico con IA** o el menú **Desarrollar herramienta**:

- selecciona una herramienta;
- completa sus campos;
- usa **Revisar con IA** para recibir retroalimentación;
- observa a la derecha la plantilla visual final que se actualiza con tus respuestas;
- descarga la herramienta o sus datos.

La vista visual es generada por código; no depende de imágenes estáticas y existe para las 34 herramientas.

## Servicios y mecanismos

La app incluye una capa de orientación hacia mentoría, vigilancia tecnológica, propiedad intelectual, transferencia, diagnóstico de capacidades, CIEN/conexión, Rueda CTI, Fondo 1 a 1 y COMINN. Antes de una publicación institucional, CEDIA debe confirmar nombres, vigencia, disponibilidad, elegibilidad y responsables.

## Archivos metodológicos

- `data/methodology.json`
- `data/route_final.json`
- `data/Plantilla_Maestra_Ruta_CEDIA_v12_RUTA_IA_COMUNICACION.xlsx`

Estos archivos son la fuente de verdad del prototipo; el modelo de IA no reemplaza la metodología.


## v5.2 — Conversación más natural
- Preguntas de aclaración concretas y respondibles por el investigador.
- Una idea ya no se registra como evidencia.
- La IA no pide al usuario diseñar la metodología.
- Se eliminó la burbuja vacía durante el spinner de análisis.


## v6.0 - CEDIA BRAND
- Identidad visual alineada a CEDIA: base azul corporativo, blanco y grises.
- No se introducen colores externos como identidad propia. Si Comunicación desea diferenciar etapas, debe usar exclusivamente la cromática oficial de apoyo/Ecosistema CTI definida por CEDIA.
- El prototipo se presenta como evolución digital complementaria, no como producto principal.
- La propuesta principal es el sistema Ruta CEDIA: portafolio + campaña + acompañamiento + conexión a servicios.
