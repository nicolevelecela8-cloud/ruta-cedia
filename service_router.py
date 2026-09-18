from __future__ import annotations
from typing import Any, Dict, List

# These entries separate documented/known mechanisms from proposal-level routing.
# Before public launch, CEDIA should confirm current names, eligibility, availability and owners.
SERVICE_CATALOG: List[Dict[str, Any]] = [
    {
        "id":"MENTORIA",
        "name":"Mentoría especializada para proyectos de innovación",
        "status":"Documentado en la base cargada; confirmar condiciones vigentes",
        "type":"Acompañamiento",
        "need":"Lectura integral de resultados, evidencia, brechas y hoja de ruta.",
        "stages":[1,2,3,4,5,6,7],
        "keywords":["diagnostico","brecha","ruta","maduracion","transferencia","validacion"],
    },
    {
        "id":"VIGILANCIA",
        "name":"Vigilancia tecnológica",
        "status":"Portafolio CEDIA documentado en la fuente de sistemas de innovación; verificar ficha vigente",
        "type":"Servicio especializado",
        "need":"Estado del arte, tendencias, tecnologías, competidores o información tecnológica externa.",
        "stages":[1,3,5],
        "keywords":["tendencia","estado del arte","competidor","tecnologia","patente","informacion"],
    },
    {
        "id":"PI",
        "name":"Propiedad intelectual",
        "status":"Portafolio CEDIA documentado; verificar alcance vigente",
        "type":"Servicio especializado",
        "need":"Protección, titularidad, divulgación, búsquedas, FTO u otras decisiones de PI.",
        "stages":[5,6],
        "keywords":["pi","propiedad intelectual","patente","fto","invencion","proteccion","titularidad"],
    },
    {
        "id":"TRANSFERENCIA",
        "name":"Transferencia tecnológica",
        "status":"Portafolio CEDIA documentado; verificar alcance vigente",
        "type":"Servicio especializado",
        "need":"Preparar, negociar o acompañar la transferencia/aplicación de un resultado de I+D+i.",
        "stages":[5,6,7],
        "keywords":["transferencia","licencia","empresa","adopcion","receptor","negociacion"],
    },
    {
        "id":"CAPACIDADES",
        "name":"Diagnóstico de capacidades",
        "status":"Portafolio CEDIA documentado; verificar ficha vigente",
        "type":"Servicio especializado",
        "need":"Identificar capacidades, infraestructura, conocimiento o brechas organizacionales.",
        "stages":[1,2,5,6],
        "keywords":["capacidad","infraestructura","laboratorio","recurso","organizacion"],
    },
    {
        "id":"CIEN",
        "name":"Plataforma CIEN / mecanismos de conexión",
        "status":"Mecanismo de intermediación documentado; verificar operación y condiciones actuales",
        "type":"Intermediación",
        "need":"Visibilizar tecnologías/capacidades y conectar con potenciales receptores o empresas.",
        "stages":[6,7],
        "keywords":["empresa","matching","conexion","tecnologia","mercado","receptor"],
    },
    {
        "id":"RUEDA",
        "name":"Rueda de Conexiones CTI",
        "status":"Mecanismo documentado; disponibilidad depende de convocatorias/eventos",
        "type":"Intermediación",
        "need":"Preparación, exposición y reuniones con actores interesados en tecnologías/capacidades.",
        "stages":[6,7],
        "keywords":["empresa","reunion","conexion","pitch","transferencia"],
    },
    {
        "id":"FONDO11",
        "name":"Fondo 1 a 1",
        "status":"Instrumento documentado; sujeto a convocatoria, elegibilidad y disponibilidad",
        "type":"Cofinanciamiento",
        "need":"Ejecutar proyectos universidad-organización con demanda real, aporte compartido y resultado verificable.",
        "stages":[5,6,7],
        "keywords":["financiamiento","fondo","empresa","proyecto","ejecucion","presupuesto"],
    },
    {
        "id":"COMINN",
        "name":"COMINN / articulación multiactor",
        "status":"Mecanismo documentado; activar solo cuando corresponda y exista disponibilidad",
        "type":"Articulación",
        "need":"Problemas compartidos que requieren varios actores, foco común, cartera y seguimiento.",
        "stages":[1,6,7],
        "keywords":["varias empresas","multiactor","sector","problema compartido","mision","articulacion"],
    },
]


def recommend_services(stage: int | None = None, text: str = "", gap: str = "", limit: int = 3) -> List[Dict[str, Any]]:
    hay = f"{text} {gap}".lower()
    scored=[]
    for s in SERVICE_CATALOG:
        score=0
        if stage and stage in s["stages"]:
            score += 3
        for kw in s["keywords"]:
            if kw in hay:
                score += 2
        if s["id"] == "MENTORIA":
            score += 1
        if score:
            scored.append((score,s))
    scored.sort(key=lambda x:(-x[0], x[1]["name"]))
    return [s for _,s in scored[:limit]]
