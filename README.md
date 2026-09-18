# Ruta CEDIA Innovación 2026

Prototipo Streamlit limpio para orientar proyectos mediante el portafolio metodológico de CEDIA.

## Arquitectura

`Usuario → IA interpreta → motor valida → herramienta recomendada → desarrollo guiado → evidencia`

La IA conversa, extrae contexto y propone una brecha. `engine.py` verifica los identificadores y aplica exclusivamente las reglas registradas en `data/methodology.json`. La aplicación no debe inventar herramientas, servicios, evidencia, precios ni condiciones institucionales.

## Funciones

- diagnóstico conversacional con preguntas adaptativas;
- 34 herramientas de innovación;
- desarrollo guiado y revisión metodológica campo por campo;
- vistas finales dinámicas;
- ruta metodológica de siete etapas;
- pasaporte del proyecto;
- orientación TRL/CRL;
- catálogo de servicios CEDIA separado del diagnóstico metodológico;
- exportación de resultados y respaldo del proyecto.

## Despliegue en Streamlit Community Cloud

1. Sube el contenido de esta carpeta a la raíz del repositorio de GitHub.
2. Configura en Streamlit Secrets:

```toml
GROQ_API_KEY = "tu_clave"
```

3. El archivo principal es `app.py`.
4. No subas `.env` ni `secrets.toml`.

## Ejecución local

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Fuente de verdad

- `data/methodology.json`
- `data/route_final.json`
- `data/Plantilla_Maestra_Ruta_CEDIA_v12_RUTA_IA_COMUNICACION.xlsx`

## Nota institucional

Las herramientas, reglas, servicios y condiciones señaladas como propuestas deben validarse con CEDIA antes de una publicación institucional definitiva.
