APP_CSS = """
<style>
    .stApp { background: #F4F6F9; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { letter-spacing: -0.02em; color: #001F5C !important; }
    
    /* Forzar a que los textos normales de la página sean oscuros y legibles */
    p, span, label, .smallmuted { color: #1E293B !important; }
    
    .hero {
        background: linear-gradient(135deg, #001F5C 0%, #0066FF 100%);
        color: white;
        padding: 34px 38px;
        border-radius: 24px;
        margin-bottom: 24px;
        box-shadow: 0 12px 32px rgba(0,22,92,.16);
    }
    .hero h1 { color:white !important; margin:0 0 8px 0; font-size:2.25rem; }
    .hero p { color:#F2F3FB !important; font-size:1.05rem; max-width:850px; margin:0; }
    
    /* Cuadros principales de CEDIA */
    .card {
        background: #001F5C !important;
        border: 1px solid #0066FF;
        border-radius: 18px;
        padding: 20px;
        min-height: 150px;
        box-shadow: 0 6px 18px rgba(0,0,0,.15);
        margin-bottom: 14px;
    }
    .card * { color: white !important; }
    
    /* Ajuste definitivo para los botones de Streamlit bajo los cuadros */
    div.stButton > button {
        background-color: #0066FF !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0, 102, 255, 0.2) !important;
    }
    div.stButton > button:hover {
        background-color: #001F5C !important;
        color: white !important;
    }
    
    .pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #0066FF;
        color: white !important;
        font-size: .78rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .note {
        background: #fff7da;
        border-left: 4px solid #d5a21b;
        padding: 12px 14px;
        border-radius: 10px;
        margin: 12px 0;
    }
    .note * { color: #1E293B !important; }
    
    .successbox {
        background: #edf8f1;
        border-left: 4px solid #2f855a;
        padding: 14px 16px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .successbox * { color: #1E293B !important; }
    
    .resultbox {
        background: #001F5C !important;
        border: 1px solid #0066FF;
        border-radius: 18px;
        padding: 22px;
        margin-top: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,.15);
    }
    .resultbox * { color: white !important; }
    
    /* Menú lateral */
    div[data-testid="stSidebar"] { background: #001F5C; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stRadio label { color: white !important; }
</style>
"""
