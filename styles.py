APP_CSS = """
<style>
    .stApp { background: #F4F6F9; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { letter-spacing: -0.02em; color: #001F5C !important; }
    .hero {
        background: linear-gradient(135deg, #001F5C 0%, #0066FF 100%);
        color: white;
        padding: 34px 38px;
        border-radius: 24px;
        margin-bottom: 24px;
        box-shadow: 0 12px 32px rgba(0,22,92,.16);
    }
    .hero h1 { color:white !important; margin:0 0 8px 0; font-size:2.25rem; }
    .hero p { color:#F2F3FB; font-size:1.05rem; max-width:850px; margin:0; }
    
    /* Cuadros transformados al Azul Corporativo de CEDIA */
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
        color: #1E293B !important;
    }
    .note * { color: #1E293B !important; }
    
    .successbox {
        background: #edf8f1;
        border-left: 4px solid #2f855a;
        padding: 14px 16px;
        border-radius: 10px;
        margin: 10px 0;
        color: #1E293B !important;
    }
    .successbox * { color: #1E293B !important; }
    
    /* Cuadro de resultados adaptado */
    .resultbox {
        background: #001F5C !important;
        border: 1px solid #0066FF;
        border-radius: 18px;
        padding: 22px;
        margin-top: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,.15);
    }
    .resultbox * { color: white !important; }
    
    .smallmuted { color: #6b7280; font-size: .88rem; }
    
    /* Menú lateral izquierdo con la identidad de CEDIA */
    div[data-testid="stSidebar"] { background: #001F5C; }
    div[data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="stSidebar"] .stRadio label { color: white !important; }
</style>
"""
