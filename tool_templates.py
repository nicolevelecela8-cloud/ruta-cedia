from __future__ import annotations

import html
import re
from typing import Any, Dict, List

# Visual template configuration. The method content still comes from methodology.json.
# These schemas only define how the user develops and visualizes each tool in the app.
SCHEMAS: Dict[str, Dict[str, Any]] = {
    "IDE-001": {"visual":"tree", "fields":[("problem","Problema central"),("cause1","Causa directa 1"),("cause2","Causa directa 2"),("cause3","Causa directa 3"),("effect1","Efecto directo 1"),("effect2","Efecto directo 2"),("effect3","Efecto directo 3")]},
    "IDE-002": {"visual":"ideas", "fields":[("challenge","Reto o pregunta de ideación"),("idea1","Idea 1"),("idea2","Idea 2"),("idea3","Idea 3"),("idea4","Idea 4"),("idea5","Idea 5"),("priority","Idea prioritaria y por qué")]},
    "IDE-003": {"visual":"brief", "fields":[("background","Antecedentes"),("objective","Objetivo general"),("info","Información específica requerida"),("audience","Público objetivo"),("hypotheses","Hipótesis"),("analysis","Necesidades de análisis"),("method","Metodología y recolección")]},
    "IDE-004": {"visual":"questions", "fields":[("what","¿Qué?"),("who","¿Quién?"),("how","¿Cómo?"),("where","¿Dónde?"),("when","¿Cuándo?"),("assumption","Supuesto o proyección a cuestionar"),("powerful","Pregunta poderosa final")]},
    "IDE-005": {"visual":"fishbone", "fields":[("problem","Problema / efecto"),("cat1","Categoría de causa 1"),("cat2","Categoría de causa 2"),("cat3","Categoría de causa 3"),("cause1","Causa específica 1"),("cause2","Causa específica 2"),("cause3","Causa específica 3"),("action","Acción de seguimiento")]},
    "IDE-006": {"visual":"hmw", "fields":[("insight","Insight o necesidad"),("user","Usuario / actor"),("need","Necesidad"),("constraint","Restricción relevante"),("hmw","¿Cómo podríamos…?"),("idea","Primera idea de respuesta")]},
    "IDE-007": {"visual":"lotus", "fields":[("challenge","Reto central"),("i1","Idea 1"),("i2","Idea 2"),("i3","Idea 3"),("i4","Idea 4"),("i5","Idea 5"),("i6","Idea 6"),("i7","Idea 7"),("i8","Idea 8"),("priority","Idea priorizada")]},
    "IDE-008": {"visual":"statement", "fields":[("topic","Tema"),("who","¿Quién?"),("what","¿Qué ocurre?"),("situation","Situación / contexto"),("why1","¿Por qué importa? / beneficio deseable"),("why2","Valor o impacto esperado"),("statement","Planteamiento final del problema")]},
    "MKT-001": {"visual":"persona", "fields":[("name","Nombre / arquetipo"),("profile","Perfil general"),("demographics","Datos relevantes"),("goals","Objetivos"),("challenges","Retos"),("help","Cómo podemos ayudar"),("objections","Objeciones / comentarios"),("marketing","Mensaje de marketing"),("sales","Mensaje de ventas")]},
    "MKT-002": {"visual":"golden", "fields":[("why","¿Por qué?"),("how","¿Cómo?"),("what","¿Qué?"),("purpose","Declaración integrada")]},
    "MKT-003": {"visual":"swot", "fields":[("strengths","Fortalezas"),("weaknesses","Debilidades"),("opportunities","Oportunidades"),("threats","Amenazas"),("decision","Implicación / decisión principal")]},
    "MKT-004": {"visual":"positioning", "fields":[("xaxis","Atributo eje X"),("yaxis","Atributo eje Y"),("competitors","Competidores / alternativas"),("perception","Percepción / evidencia"),("position","Posición propia"),("opportunity","Espacio de oportunidad")]},
    "MKT-005": {"visual":"pitch", "fields":[("change","Cambio"),("pain","Problema / dolor"),("solution","Producto / servicio"),("beta","Versión beta / evidencia"),("unique","Unicidad"),("traction","Tracción"),("business","Modelo de negocio"),("investment","Inversión / recursos"),("team","Equipo"),("cta","Llamado a la acción"),("whyyou","Por qué ustedes / por qué ahora")]},
    "NEG-001": {"visual":"bmc", "fields":[("segments","Segmentos de clientes"),("value","Propuesta de valor"),("channels","Canales"),("relationships","Relaciones con clientes"),("revenues","Fuentes de ingresos"),("resources","Recursos clave"),("activities","Actividades clave"),("partners","Aliados clave"),("costs","Estructura de costos")]},
    "NEG-002": {"visual":"vpc", "fields":[("jobs","Customer Jobs"),("pains","Pains"),("gains","Gains"),("products","Productos / servicios"),("relievers","Pain Relievers"),("creators","Gain Creators"),("fit","Hipótesis de encaje")]},
    "PRO-001": {"visual":"jtbd", "fields":[("user","Usuario / situación"),("jobs","Trabajos por resolver"),("importance","Importancia"),("satisfaction","Satisfacción actual"),("persona","Soy / Necesito / Para"),("sketch","Boceto preliminar de solución")]},
    "PRO-002": {"visual":"empathy", "fields":[("think","Piensa / siente"),("see","Ve"),("say","Dice / hace"),("hear","Escucha"),("pains","Frustraciones / esfuerzos"),("gains","Motivaciones / resultados")]},
    "PRO-003": {"visual":"solution", "fields":[("job","Trabajo a resolver"),("functional","Atributos funcionales"),("needs","Necesidades principales"),("alternatives","Soluciones actuales / alternativas"),("personal","Dimensión emocional personal"),("social","Dimensión emocional social")]},
    "PRO-004": {"visual":"requirements", "fields":[("functional","Requisitos funcionales"),("technical","Requisitos tecnológicos"),("expressive","Requisitos expresivos"),("must","Requisitos obligatorios"),("verify","Cómo se verificará cada requisito")]},
    "PRO-005": {"visual":"storyboard", "fields":[("problem","Problema / historia"),("f1","Frame 1"),("f2","Frame 2"),("f3","Frame 3"),("f4","Frame 4"),("f5","Frame 5"),("f6","Frame 6"),("f7","Frame 7"),("f8","Frame 8"),("insights","Observaciones / insights")]},
    "PRO-006": {"visual":"venn3", "fields":[("desirability","Deseabilidad: ¿qué demanda el mercado/usuario?"),("feasibility","Factibilidad: ¿qué es técnicamente posible?"),("viability","Viabilidad: ¿qué es económicamente viable?"),("weak","Dimensión más débil"),("decision","Decisión / siguiente evidencia")]},
    "SER-001": {"visual":"service", "fields":[("base","Servicio base"),("subsequent","Servicio subsecuente"),("complementary","Servicio complementario"),("secondary","Servicio secundario"),("star","Servicio estrella"),("moments","Momentos de verdad"),("actors","Prestadores / personal / otros clientes"),("system","Sistema / soporte")]},
    "TEN-001": {"visual":"trend3", "fields":[("technical","Conocimiento técnico"),("demand","Demanda"),("sustainability","Sostenibilidad a largo plazo"),("trend1","Tendencia 1"),("trend2","Tendencia 2"),("trend3","Tendencia 3"),("intersection","Patrones / intersecciones"),("opportunity","Oportunidad de innovación")]},
    "TEN-002": {"visual":"compass", "fields":[("problem","Definición del problema"),("statement","Declaración"),("reframe","Nueva formulación"),("causes","Causas"),("effects","Efectos indeseados"),("context","Contexto espacio-temporal"),("actors","Actores clave"),("testimonials","Testimonios / evidencia")]},
    "TEN-003": {"visual":"trendmap", "fields":[("sector","Sector / área"),("trend","Línea de tendencia"),("factors","Factores clave"),("convergence","Convergencias"),("opportunities","Oportunidades"),("impact","Impactos potenciales")]},
    "TEN-004": {"visual":"trendcanvas", "fields":[("trend","Tendencia seleccionada"),("needs","Necesidades básicas"),("drivers","Causas del cambio"),("expectations","Expectativas emergentes"),("inspiration","Inspiración de otros sectores"),("potential","Potencial de innovación"),("vision","Visión a largo plazo"),("offer","Adaptación / nueva oferta"),("segment","Segmento objetivo"),("concept","Concepto de innovación")]},
    "VAL-001": {"visual":"assumptions", "fields":[("decision","Idea / decisión a evaluar"),("desirability","Supuestos de deseabilidad"),("feasibility","Supuestos de factibilidad"),("viability","Supuestos de viabilidad"),("adaptation","Supuestos de adaptación / supervivencia"),("evidence","Fuerza de evidencia"),("critical","Hipótesis crítica priorizada")]},
    "VAL-002": {"visual":"testcard", "fields":[("hypothesis","Hipótesis: creemos que…"),("test","Para verificarlo, haremos…"),("metric","Mediremos…"),("threshold","Tendremos razón si…"),("conditions","Participantes / condiciones"),("evidence","Evidencia esperada")]},
    "VAL-003": {"visual":"learningcard", "fields":[("hypothesis","Hipótesis / prueba realizada"),("observations","Observamos…"),("threshold","Comparación con umbral"),("learning","Aprendimos…"),("decision","Por lo tanto decidimos…"),("update","Qué evidencia/herramienta se actualiza")]},
    "MAD-001": {"visual":"roadmap", "fields":[("current","TRL actual y evidencia"),("target","TRL objetivo"),("gaps","Brechas críticas"),("activities","Actividades / pruebas"),("metrics","Métricas / criterios de decisión"),("milestones","Hitos / calendario"),("owners","Responsables / recursos"),("evidence","Evidencia de salida") ]},
    "TRA-001": {"visual":"fto", "fields":[("scope","Producto/proceso + jurisdicción"),("rights","Derechos / patentes relevantes"),("comparison","Comparación con explotación prevista"),("risks","Riesgos / incertidumbres"),("actions","Acciones de mitigación / consulta") ]},
    "TRA-002": {"visual":"valuechain", "fields":[("value","Valor / resultado entregado"),("activities","Actividades de la cadena"),("capabilities","Capacidades requeridas / disponibles"),("actors","Actores / socios"),("gaps","Brechas / cuellos de botella"),("alliances","Alianzas / capacidades a desarrollar") ]},
    "TRA-003": {"visual":"disclosure", "fields":[("invention","Invención / resultado y problema resuelto"),("inventors","Inventores / contribuyentes"),("funding","Financiación / acuerdos"),("disclosures","Divulgaciones previas / previstas"),("evidence","Evidencia técnica / aplicaciones"),("thirdparties","Terceros / interés conocido"),("next","Remisión / siguiente evaluación institucional") ]},
    "ADO-001": {"visual":"adoption", "fields":[("application","Aplicación / objetivo de adopción"),("value","Riesgos de propuesta de valor"),("market","Riesgos de aceptación de mercado"),("resources","Riesgos de madurez de recursos"),("license","Riesgos de licencia para operar"),("evidence","Evidencia disponible"),("priority","Barreras prioritarias"),("actions","Acciones / responsables") ]},
}


def schema_for(tool_id: str, tool: Dict[str, Any]) -> Dict[str, Any]:
    if tool_id in SCHEMAS:
        return SCHEMAS[tool_id]
    # Safe fallback from PASOS_CLAVE.
    steps = str(tool.get("PASOS_CLAVE") or "").strip()
    chunks = [x.strip(" .") for x in re.split(r"(?:^|\s)\d+[\)\.]\s*", steps) if x.strip(" .")]
    if not chunks:
        chunks = ["Contenido principal", "Evidencia / resultado"]
    fields = [(f"step{i+1}", c[:80]) for i, c in enumerate(chunks[:10])]
    return {"visual":"cards", "fields":fields}


def empty_answers(tool_id: str, tool: Dict[str, Any]) -> Dict[str, str]:
    return {key:"" for key, _ in schema_for(tool_id, tool)["fields"]}


def _esc(v: Any, placeholder: str = "Pendiente") -> str:
    text = str(v or "").strip()
    return html.escape(text if text else placeholder)


def _card(label: str, value: str, cls: str = "") -> str:
    return f'<div class="vcard {cls}"><b>{html.escape(label)}</b><div>{_esc(value)}</div></div>'


def _cards(fields: List, answers: Dict[str,str]) -> str:
    return '<div class="grid2">' + ''.join(_card(label, answers.get(key,"")) for key,label in fields) + '</div>'


def render_preview(tool_id: str, tool: Dict[str, Any], answers: Dict[str, str]) -> str:
    schema = schema_for(tool_id, tool)
    fields = schema["fields"]
    v = schema["visual"]
    name = html.escape(tool.get("NOMBRE") or "Herramienta")
    subtitle = html.escape(tool.get("SALIDA_RESULTADO") or "Vista previa de la herramienta finalizada")

    def val(k, ph="Pendiente"):
        return _esc(answers.get(k), ph)

    body = ""
    if v == "tree":
        body = f'''<div class="tree">
          <div class="row effects">{_card('Efecto 1',answers.get('effect1',''),'green')}{_card('Efecto 2',answers.get('effect2',''),'green')}{_card('Efecto 3',answers.get('effect3',''),'green')}</div>
          <div class="connector">🌿</div><div class="center red"><b>PROBLEMA CENTRAL</b><div>{val('problem')}</div></div><div class="connector">🌱</div>
          <div class="row causes">{_card('Causa 1',answers.get('cause1',''),'blue')}{_card('Causa 2',answers.get('cause2',''),'blue')}{_card('Causa 3',answers.get('cause3',''),'blue')}</div>
        </div>'''
    elif v == "fishbone":
        body = f'''<div class="fish"><div class="bones">
        {_card(val('cat1','Categoría 1'),answers.get('cause1',''),'blue')}{_card(val('cat2','Categoría 2'),answers.get('cause2',''),'blue')}{_card(val('cat3','Categoría 3'),answers.get('cause3',''),'blue')}
        </div><div class="spine">━━━━━━━━━━━━━━━━━━━━▶</div><div class="center red"><b>EFECTO / PROBLEMA</b><div>{val('problem')}</div></div><div class="footerline"><b>Seguimiento:</b> {val('action')}</div></div>'''
    elif v == "lotus":
        cells=[]
        for i in range(1,9): cells.append(_card(f"Idea {i}",answers.get(f"i{i}",""),'blue'))
        body = '<div class="lotus">'+''.join(cells[:4])+f'<div class="vcard red"><b>RETO CENTRAL</b><div>{val("challenge")}</div></div>'+''.join(cells[4:])+f'</div><div class="footerline"><b>Prioridad:</b> {val("priority")}</div>'
    elif v == "swot":
        body = '<div class="quad">'+_card('FORTALEZAS',answers.get('strengths',''),'green')+_card('DEBILIDADES',answers.get('weaknesses',''),'red')+_card('OPORTUNIDADES',answers.get('opportunities',''),'blue')+_card('AMENAZAS',answers.get('threats',''),'amber')+'</div>'+f'<div class="footerline"><b>Decisión:</b> {val("decision")}</div>'
    elif v == "golden":
        body = f'''<div class="golden"><div class="circle c1"><b>WHY</b><span>{val('why')}</span></div><div class="circle c2"><b>HOW</b><span>{val('how')}</span></div><div class="circle c3"><b>WHAT</b><span>{val('what')}</span></div></div><div class="footerline"><b>Propósito:</b> {val('purpose')}</div>'''
    elif v == "positioning":
        body = f'''<div class="position"><div class="axis y">{val('yaxis','Eje Y')}</div><div class="plane"><span class="dot d1">Competidores</span><span class="dot d2">Alternativas</span><span class="dot me">Tu propuesta</span></div><div class="axis x">{val('xaxis','Eje X')}</div></div><div class="grid2">{_card('Percepción / evidencia',answers.get('perception',''))}{_card('Oportunidad',answers.get('opportunity',''))}</div>'''
    elif v == "bmc":
        labels=[('partners','Aliados clave'),('activities','Actividades clave'),('value','Propuesta de valor'),('relationships','Relación con clientes'),('segments','Segmentos'),('resources','Recursos clave'),('channels','Canales'),('costs','Costos'),('revenues','Ingresos')]
        body='<div class="bmc">'+''.join(_card(l,answers.get(k,''),'blue' if k=='value' else '') for k,l in labels)+'</div>'
    elif v == "vpc":
        body=f'''<div class="split"><div class="panel"><h4>Perfil del cliente</h4>{_card('Jobs',answers.get('jobs',''))}{_card('Pains',answers.get('pains',''),'red')}{_card('Gains',answers.get('gains',''),'green')}</div><div class="panel"><h4>Mapa de valor</h4>{_card('Productos / servicios',answers.get('products',''))}{_card('Pain Relievers',answers.get('relievers',''),'blue')}{_card('Gain Creators',answers.get('creators',''),'green')}</div></div><div class="footerline"><b>Hipótesis de encaje:</b> {val('fit')}</div>'''
    elif v == "empathy":
        body='<div class="quad">'+_card('PIENSA / SIENTE',answers.get('think',''),'blue')+_card('VE',answers.get('see',''))+_card('DICE / HACE',answers.get('say',''))+_card('ESCUCHA',answers.get('hear',''))+'</div><div class="grid2">'+_card('FRUSTRACIONES',answers.get('pains',''),'red')+_card('MOTIVACIONES',answers.get('gains',''),'green')+'</div>'
    elif v == "storyboard":
        frames=''.join(f'<div class="frame"><b>{i}</b><div>{val(f"f{i}","Escena")}</div></div>' for i in range(1,9))
        body=f'<div class="footerline"><b>Historia / problema:</b> {val("problem")}</div><div class="story">{frames}</div><div class="footerline"><b>Insights:</b> {val("insights")}</div>'
    elif v == "venn3":
        body=f'''<div class="venn"><div class="bubble b1"><b>Deseabilidad</b><span>{val('desirability')}</span></div><div class="bubble b2"><b>Factibilidad</b><span>{val('feasibility')}</span></div><div class="bubble b3"><b>Viabilidad</b><span>{val('viability')}</span></div></div><div class="grid2">{_card('Dimensión débil',answers.get('weak',''),'amber')}{_card('Decisión',answers.get('decision',''),'green')}</div>'''
    elif v == "assumptions":
        body=f'''<div class="matrix"><div class="ylabel">IMPORTANCIA ↑</div><div class="quadcell q1"><b>Alta importancia / baja evidencia</b><p>{val('critical','Hipótesis crítica')}</p></div><div class="quadcell"><b>Alta importancia / alta evidencia</b><p>{val('evidence')}</p></div><div class="quadcell"><b>Baja importancia / baja evidencia</b><p>{val('adaptation')}</p></div><div class="quadcell"><b>Baja importancia / alta evidencia</b><p>{val('viability')}</p></div></div><div class="footerline"><b>Decisión:</b> {val('decision')}</div>'''
    elif v == "testcard":
        body='<div class="grid2">'+_card('1. Creemos que…',answers.get('hypothesis',''),'red')+_card('2. Para verificarlo, haremos…',answers.get('test',''),'blue')+_card('3. Mediremos…',answers.get('metric',''),'green')+_card('4. Tendremos razón si…',answers.get('threshold',''),'amber')+_card('5. Condiciones / participantes',answers.get('conditions',''))+_card('6. Evidencia esperada',answers.get('evidence',''))+'</div>'
    elif v == "learningcard":
        body='<div class="grid2">'+_card('Hipótesis / prueba',answers.get('hypothesis',''))+_card('Observamos',answers.get('observations',''),'blue')+_card('Vs. umbral',answers.get('threshold',''),'amber')+_card('Aprendimos',answers.get('learning',''),'green')+_card('Decidimos',answers.get('decision',''),'red')+_card('Actualizamos',answers.get('update',''))+'</div>'
    elif v == "roadmap":
        body=f'''<div class="road"><div class="milestone"><b>AHORA</b><span>{val('current')}</span></div><div class="arrow">→</div><div class="milestone"><b>BRECHAS</b><span>{val('gaps')}</span></div><div class="arrow">→</div><div class="milestone"><b>ACTIVIDADES</b><span>{val('activities')}</span></div><div class="arrow">→</div><div class="milestone"><b>OBJETIVO</b><span>{val('target')}</span></div></div><div class="grid2">{_card('Métricas / criterios',answers.get('metrics',''))}{_card('Evidencia de salida',answers.get('evidence',''))}{_card('Hitos',answers.get('milestones',''))}{_card('Responsables / recursos',answers.get('owners',''))}</div>'''
    elif v == "fto":
        body='<div class="grid2">'+_card('Alcance y jurisdicción',answers.get('scope',''))+_card('Derechos relevantes',answers.get('rights',''),'blue')+_card('Comparación técnica',answers.get('comparison',''))+_card('Riesgos',answers.get('risks',''),'red')+'</div>'+f'<div class="footerline"><b>Acciones:</b> {val("actions")}</div>'
    elif v == "valuechain":
        body=f'''<div class="chain"><div>{val('value','Valor')}</div><span>→</span><div>{val('activities','Actividades')}</div><span>→</span><div>{val('capabilities','Capacidades')}</div><span>→</span><div>{val('actors','Actores')}</div><span>→</span><div>{val('alliances','Alianzas')}</div></div><div class="footerline"><b>Brechas / cuellos de botella:</b> {val('gaps')}</div>'''
    elif v == "adoption":
        body='<div class="quad">'+_card('PROPUESTA DE VALOR',answers.get('value',''),'blue')+_card('ACEPTACIÓN DE MERCADO',answers.get('market',''),'green')+_card('MADUREZ DE RECURSOS',answers.get('resources',''),'amber')+_card('LICENCIA PARA OPERAR',answers.get('license',''),'red')+'</div><div class="grid2">'+_card('Barreras prioritarias',answers.get('priority',''))+_card('Acciones',answers.get('actions',''))+'</div>'
    elif v == "pitch":
        body=_cards(fields,answers)
    elif v == "persona":
        body=f'''<div class="persona"><div class="avatar">👤</div><div><h3>{val('name','Persona')}</h3><p>{val('profile')}</p></div></div><div class="grid2">{_card('Objetivos',answers.get('goals',''),'green')}{_card('Retos',answers.get('challenges',''),'red')}{_card('Cómo ayudar',answers.get('help',''),'blue')}{_card('Objeciones',answers.get('objections',''),'amber')}</div><div class="footerline"><b>Mensaje:</b> {val('marketing')}</div>'''
    elif v == "hmw":
        body=f'''<div class="quote">¿CÓMO PODRÍAMOS…?<div>{val('hmw')}</div></div><div class="grid2">{_card('Insight',answers.get('insight',''))}{_card('Usuario',answers.get('user',''))}{_card('Necesidad',answers.get('need',''))}{_card('Restricción',answers.get('constraint',''))}</div><div class="footerline"><b>Idea inicial:</b> {val('idea')}</div>'''
    elif v == "service":
        body='<div class="grid2">'+_card('Servicio base',answers.get('base',''),'blue')+_card('Servicio estrella',answers.get('star',''),'green')+_card('Complementario',answers.get('complementary',''))+_card('Secundario',answers.get('secondary',''))+'</div><div class="grid2">'+_card('Momentos de verdad',answers.get('moments',''),'amber')+_card('Actores / sistema',answers.get('actors','')+' '+answers.get('system',''))+'</div>'
    elif v == "disclosure":
        body=_cards(fields,answers)
    else:
        body=_cards(fields,answers)

    css = '''<style>
    *{box-sizing:border-box}body{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f6f8fb;margin:0;color:#17324d}.sheet{background:white;border:1px solid #dde7f0;border-radius:22px;padding:22px;box-shadow:0 8px 24px rgba(15,39,68,.08)}.head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;border-bottom:1px solid #edf1f5;padding-bottom:14px;margin-bottom:18px}.head h2{margin:0;color:#123f67}.head p{margin:5px 0 0;color:#6b7b8c;font-size:13px}.badge{background:#eaf3fb;color:#185b8c;padding:7px 10px;border-radius:999px;font-size:12px;font-weight:700}.row,.grid2,.quad{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.grid2,.quad{grid-template-columns:repeat(2,1fr)}.vcard{background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:12px;min-height:78px;font-size:12px;line-height:1.35}.vcard b{display:block;color:#194d75;margin-bottom:6px}.vcard.green{background:#edf8f0;border-color:#d5eadb}.vcard.red{background:#fff0ef;border-color:#f0d0cd}.vcard.blue{background:#edf5ff;border-color:#d6e7fb}.vcard.amber{background:#fff8e6;border-color:#f1dfaa}.center{max-width:65%;margin:auto;text-align:center;border-radius:16px;padding:16px}.connector{text-align:center;font-size:32px;margin:6px}.footerline{margin-top:12px;padding:12px;border-radius:12px;background:#f4f7fa;font-size:12px}.lotus{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.golden{display:flex;align-items:center;justify-content:center;gap:0;min-height:260px}.circle{border-radius:50%;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:18px;position:relative}.circle span{font-size:11px}.c1{width:240px;height:240px;background:#fff1c9}.c2{width:180px;height:180px;background:#cfe8fb;margin-left:-210px}.c3{width:115px;height:115px;background:#fff;margin-left:-148px;border:2px solid #89bfe4}.position{height:260px;position:relative;border-left:2px solid #99aabb;border-bottom:2px solid #99aabb;margin:25px}.plane{position:absolute;inset:10px}.dot{position:absolute;padding:7px 9px;border-radius:999px;background:#dceaf5;font-size:11px}.d1{left:15%;top:30%}.d2{left:60%;top:60%}.me{left:66%;top:20%;background:#d8f1de;color:#1a6c38;font-weight:bold}.axis{font-size:11px;font-weight:700}.axis.y{position:absolute;left:-20px;top:0;writing-mode:vertical-rl}.axis.x{text-align:right;position:absolute;right:0;bottom:-24px}.bmc{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.bmc .vcard:nth-child(3){grid-row:span 2}.bmc .vcard:nth-child(8),.bmc .vcard:nth-child(9){grid-column:span 2}.split{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border:1px solid #e2e8f0;border-radius:16px;padding:12px}.story{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.frame{border:1px solid #dce4eb;border-radius:12px;min-height:100px;padding:9px;font-size:11px;background:#fbfcfd}.venn{height:300px;position:relative;max-width:600px;margin:auto}.bubble{position:absolute;width:230px;height:230px;border-radius:50%;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:35px;opacity:.82}.bubble span{font-size:11px}.b1{left:60px;top:5px;background:#f4d6d3}.b2{left:240px;top:5px;background:#d9ebfb}.b3{left:150px;top:125px;background:#d9f0df}.matrix{display:grid;grid-template-columns:1fr 1fr;gap:8px}.quadcell{min-height:120px;border:1px solid #dce4eb;border-radius:13px;padding:12px;background:#f8fafc}.q1{background:#fff0ef;border-color:#efc9c6}.road,.chain{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap}.milestone,.chain div{flex:1;min-width:120px;background:#edf5ff;border:1px solid #d2e4f6;border-radius:14px;padding:15px;text-align:center}.milestone span{display:block;font-size:11px;margin-top:6px}.arrow,.chain span{font-size:25px;color:#678}.persona{display:flex;gap:18px;align-items:center;margin-bottom:15px}.avatar{width:80px;height:80px;border-radius:50%;background:#e9f3fb;display:flex;align-items:center;justify-content:center;font-size:38px}.quote{padding:28px;border-radius:18px;background:#e9f3fb;text-align:center;font-weight:800;font-size:20px;margin-bottom:15px}.quote div{font-size:16px;font-weight:600;margin-top:10px}.fish{display:grid;grid-template-columns:2fr .3fr 1fr;align-items:center}.bones{display:grid;grid-template-columns:1fr 1fr;gap:10px}.spine{text-align:center;color:#6a8297;white-space:nowrap}.tree .row{grid-template-columns:repeat(3,1fr)}@media(max-width:800px){.grid2,.quad,.row,.split,.bmc,.story{grid-template-columns:1fr}.center{max-width:100%}}
    </style>'''
    return css + f'<div class="sheet"><div class="head"><div><h2>{name}</h2><p>{subtitle}</p></div><span class="badge">Vista final</span></div>{body}</div>'
