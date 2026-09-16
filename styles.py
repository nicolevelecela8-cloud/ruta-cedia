APP_CSS = """
<style>

/* =========================================================
   CEDIA · STREAMLIT UI
   Estilo: minimalista, limpio, ligero y accesible
   ========================================================= */

/* ---------------------------------------------------------
   1. VARIABLES DE COLOR
   --------------------------------------------------------- */

:root {
    --cedia-navy: #001F5C;
    --cedia-blue: #0066FF;

    --bg-main: #F4F6F9;
    --bg-soft: #F8FAFC;
    --bg-white: #FFFFFF;

    --card-bg: #EDF4FF;
    --card-border: #BFDBFE;

    --text-main: #1E293B;
    --text-secondary: #334155;
    --text-muted: #64748B;

    --border-soft: #DCE3EC;
}


/* ---------------------------------------------------------
   2. FONDO GENERAL DE LA APP
   --------------------------------------------------------- */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F4F6F9 !important;
    color: #1E293B !important;
}


/* ---------------------------------------------------------
   3. CONTENEDOR PRINCIPAL
   --------------------------------------------------------- */

.block-container {
    max-width: 1200px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}


/* ---------------------------------------------------------
   4. TIPOGRAFÍA GLOBAL
   IMPORTANTE:
   Ningún texto general debe aparecer blanco.
   --------------------------------------------------------- */

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp li,
.stApp div,
.stApp small,
.stApp strong,
.stApp em,
.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stMarkdown li,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
    color: #1E293B !important;
}


/* ---------------------------------------------------------
   5. TÍTULOS
   --------------------------------------------------------- */

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {
    color: #001F5C !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

.stApp h1 {
    font-size: clamp(2rem, 4vw, 3rem) !important;
    line-height: 1.1 !important;
}

.stApp h2 {
    font-size: clamp(1.5rem, 3vw, 2rem) !important;
    line-height: 1.2 !important;
}

.stApp h3 {
    font-size: 1.25rem !important;
    line-height: 1.3 !important;
}


/* ---------------------------------------------------------
   6. SIDEBAR
   --------------------------------------------------------- */

div[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

div[data-testid="stSidebar"] > div {
    background: #FFFFFF !important;
}

div[data-testid="stSidebar"] * {
    color: #001F5C !important;
}

div[data-testid="stSidebar"] h1,
div[data-testid="stSidebar"] h2,
div[data-testid="stSidebar"] h3 {
    color: #001F5C !important;
}


/* ---------------------------------------------------------
   7. RADIO BUTTONS DEL SIDEBAR
   --------------------------------------------------------- */

div[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 0.35rem 0.45rem !important;
    transition: all 0.18s ease !important;
}

div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #EDF4FF !important;
}

div[data-testid="stSidebar"] div[role="radiogroup"] label p,
div[data-testid="stSidebar"] div[role="radiogroup"] label span {
    color: #001F5C !important;
    font-weight: 500 !important;
}


/* ---------------------------------------------------------
   8. TARJETAS PERSONALIZADAS
   --------------------------------------------------------- */

.card {
    background: #EDF4FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.5rem !important;
    margin-bottom: 1rem !important;

    color: #334155 !important;

    box-shadow:
        0 1px 2px rgba(15, 23, 42, 0.03),
        0 6px 18px rgba(15, 23, 42, 0.04) !important;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease !important;
}

.card:hover {
    transform: translateY(-2px) !important;
    border-color: #93C5FD !important;

    box-shadow:
        0 4px 10px rgba(15, 23, 42, 0.05),
        0 10px 24px rgba(15, 23, 42, 0.06) !important;
}

.card h1,
.card h2,
.card h3,
.card h4,
.card .card-title {
    color: #001F5C !important;
    font-weight: 700 !important;
}

.card p,
.card span,
.card li,
.card label,
.card .card-body {
    color: #334155 !important;
}


/* ---------------------------------------------------------
   9. HERO / BANNER PRINCIPAL
   --------------------------------------------------------- */

.hero {
    background: linear-gradient(
        135deg,
        #001F5C 0%,
        #003C98 48%,
        #0066FF 100%
    ) !important;

    border-radius: 22px !important;
    padding: clamp(1.8rem, 4vw, 3.2rem) !important;
    margin-bottom: 2rem !important;

    box-shadow:
        0 12px 32px rgba(0, 31, 92, 0.15) !important;

    overflow: hidden !important;
}


/* CRÍTICO:
   Sobrescribe las reglas globales de texto oscuro
   únicamente dentro del hero.
*/

.hero,
.hero *,
.hero h1,
.hero h2,
.hero h3,
.hero h4,
.hero p,
.hero span,
.hero label,
.hero li,
.hero strong,
.hero em {
    color: #FFFFFF !important;
}

.hero h1 {
    font-weight: 750 !important;
    margin-bottom: 0.7rem !important;
}

.hero p {
    color: rgba(255, 255, 255, 0.92) !important;
    line-height: 1.65 !important;
}


/* ---------------------------------------------------------
   10. BOTONES STREAMLIT
   --------------------------------------------------------- */

div.stButton {
    width: 100% !important;
}

div.stButton > button,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"] {
    width: 100% !important;

    background: #0066FF !important;
    background-color: #0066FF !important;

    color: #FFFFFF !important;

    border: 1px solid #0066FF !important;
    border-radius: 12px !important;

    min-height: 46px !important;

    padding: 0.7rem 1.25rem !important;

    font-weight: 700 !important;
    font-size: 0.96rem !important;

    box-shadow: 0 4px 12px rgba(0, 102, 255, 0.14) !important;

    transition:
        background-color 0.18s ease,
        border-color 0.18s ease,
        transform 0.12s ease,
        box-shadow 0.18s ease !important;
}

div.stButton > button *,
[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-secondary"] * {
    color: #FFFFFF !important;
}


/* HOVER */

div.stButton > button:hover,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-secondary"]:hover {
    background: #001F5C !important;
    background-color: #001F5C !important;

    border-color: #001F5C !important;

    color: #FFFFFF !important;

    box-shadow: 0 6px 18px rgba(0, 31, 92, 0.18) !important;

    transform: translateY(-1px) !important;
}


/* CLICK / TOUCH */

div.stButton > button:active,
[data-testid="stBaseButton-primary"]:active,
[data-testid="stBaseButton-secondary"]:active {
    background: #001F5C !important;
    color: #FFFFFF !important;

    transform: scale(0.99) !important;
}


/* ---------------------------------------------------------
   11. INPUTS / TEXT AREA
   --------------------------------------------------------- */

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
.stTextInput input,
.stTextArea textarea {
    background: #FFFFFF !important;
    color: #1E293B !important;

    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;

    box-shadow: none !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #0066FF !important;
    box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.10) !important;
}


/* ---------------------------------------------------------
   12. SELECTBOX / MULTISELECT
   --------------------------------------------------------- */

[data-baseweb="select"] > div {
    background: #FFFFFF !important;

    border-color: #CBD5E1 !important;
    border-radius: 12px !important;

    color: #1E293B !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #1E293B !important;
}

[data-baseweb="popover"] {
    background: #FFFFFF !important;
}

[data-baseweb="menu"] {
    background: #FFFFFF !important;
}

[data-baseweb="menu"] li,
[data-baseweb="menu"] div,
[data-baseweb="menu"] span {
    color: #1E293B !important;
}


/* ---------------------------------------------------------
   13. EXPANDERS
   --------------------------------------------------------- */

[data-testid="stExpander"] {
    background: #FFFFFF !important;

    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;

    overflow: hidden !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: #001F5C !important;
    font-weight: 600 !important;
}


/* ---------------------------------------------------------
   14. ALERTAS / INFO / SUCCESS / WARNING
   --------------------------------------------------------- */

[data-testid="stAlert"] {
    border-radius: 14px !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: #1E293B !important;
}


/* ---------------------------------------------------------
   15. MÉTRICAS
   --------------------------------------------------------- */

[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}

[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"] * {
    color: #001F5C !important;
}


/* ---------------------------------------------------------
   16. TABS
   --------------------------------------------------------- */

button[data-baseweb="tab"] {
    color: #475569 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #001F5C !important;
    font-weight: 700 !important;
}

[data-baseweb="tab-highlight"] {
    background-color: #0066FF !important;
}


/* ---------------------------------------------------------
   17. DATAFRAMES / TABLAS
   --------------------------------------------------------- */

[data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}


/* ---------------------------------------------------------
   18. LINKS
   --------------------------------------------------------- */

.stApp a {
    color: #0057D9 !important;
    font-weight: 600 !important;
    text-decoration: none !important;
}

.stApp a:hover {
    color: #001F5C !important;
    text-decoration: underline !important;
}


/* Los links dentro del hero deben seguir blancos */

.hero a,
.hero a:visited,
.hero a:hover {
    color: #FFFFFF !important;
}


/* ---------------------------------------------------------
   19. DIVISORES
   --------------------------------------------------------- */

.stApp hr {
    border: none !important;
    border-top: 1px solid #E2E8F0 !important;
    margin: 1.5rem 0 !important;
}


/* ---------------------------------------------------------
   20. SCROLLBAR SUAVE
   --------------------------------------------------------- */

::-webkit-scrollbar {
    width: 9px;
    height: 9px;
}

::-webkit-scrollbar-track {
    background: #F1F5F9;
}

::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}


/* ---------------------------------------------------------
   21. RESPONSIVE · CELULARES
   --------------------------------------------------------- */

@media (max-width: 768px) {

    .block-container {
        padding-top: 1.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 3rem !important;
    }

    .hero {
        border-radius: 16px !important;
        padding: 1.5rem !important;
    }

    .hero h1 {
        font-size: 1.8rem !important;
    }

    .card {
        border-radius: 14px !important;
        padding: 1.1rem !important;
    }

    div.stButton > button {
        min-height: 48px !important;
        font-size: 1rem !important;
    }
}


/* ---------------------------------------------------------
   22. ACCESIBILIDAD / FOCUS
   --------------------------------------------------------- */

button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
a:focus-visible {
    outline: 3px solid rgba(0, 102, 255, 0.30) !important;
    outline-offset: 2px !important;
}


/* ---------------------------------------------------------
   23. ÚLTIMA PROTECCIÓN CONTRA TEXTO INVISIBLE
   --------------------------------------------------------- */

/*
   Streamlit cambia algunos selectores entre versiones.
   Esta regla mantiene oscuro cualquier texto general que
   accidentalmente herede blanco desde el tema.
*/

[data-testid="stAppViewContainer"]
[data-testid="stMarkdownContainer"]:not(.hero)
p,

[data-testid="stAppViewContainer"]
[data-testid="stMarkdownContainer"]:not(.hero)
span,

[data-testid="stAppViewContainer"]
[data-testid="stMarkdownContainer"]:not(.hero)
li {
    color: #1E293B !important;
}


/* ---------------------------------------------------------
   EXCEPCIONES FINALES:
   HERO Y BOTONES SIEMPRE BLANCOS
   --------------------------------------------------------- */

.hero *,
.hero p,
.hero span,
.hero h1,
.hero h2,
.hero h3,
.hero li {
    color: #FFFFFF !important;
}

div.stButton > button,
div.stButton > button *,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondary"] * {
    color: #FFFFFF !important;
}

</style>
"""
