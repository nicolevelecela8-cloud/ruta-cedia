APP_CSS = """
<style>
    /* Fondo general de la aplicación (Gris claro súper suave que descansa el ojo) */
    .stApp { background: #F8FAFC !important; }
    .block-container { max-width: 1120px; padding-top: 1.5rem; padding-bottom: 3rem; }
    
    /* Títulos principales bien nítidos en Azul Marino */
    h1, h2, h3 { color: #001F5C !important; font-weight: 700; letter-spacing: -0.02em; }
    
    /* Textos normales SIEMPRE oscuros para que se lean perfecto en celular */
    p, span, label, li, .smallmuted { color: #1E293B !important; font-size: 1rem; }
    
    /* Banner de bienvenida elegante con los colores oficiales de CEDIA */
    .hero {
        background: linear-gradient(135deg, #001F5C 0%, #0066FF 100%);
        color: white !important;
        padding: 28px 32px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(0,31,92,0.08);
    }
    .hero h1 { color: white !important; margin: 0 0 6px 0; font-size: 2rem; }
    .hero p { color: #F1F5F9 !important; font-size: 1.02rem; max-width: 850px; margin: 0; }
    
    /* Tarjetas en un Hermoso Azul Cielo Pastel (Suave y adictivo) */
    .card {
        background: #EDF4FF !important; 
        border: 1px solid #BFDBFE !important;
        border-radius: 18px;
        padding: 20px;
        min-height: 150px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        margin-bottom: 14px;
        transition: transform 0.2s ease;
    }
    .card:hover { transform: translateY(-2px); }
    .card h3 { color: #001F5C !important; margin-top: 0; }
    .card p { color: #334155 !important; }
    
    /* Cuadro de resultados de IA (Limpio y legible) */
    .resultbox {
        background: #F0Fdf4 !important; /* Un tono verde/azul de éxito muy suave */
        border: 1px solid #BBF7D0;
        border-radius: 18px;
        padding: 22px;
        margin-top: 12px;
    }
    
    /* Botones de acción inferiores (Azul brillante de CEDIA) */
    div.stButton > button {
        background-color: #0066FF !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0, 102, 255, 0.15) !important;
    }
    div.stButton > button:hover {
        background-color: #001F5C !important;
    }
    
    /* Menú lateral izquierdo (Blanco moderno con letras azul marino) */
    div[data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0;
    }
    div[data-testid="stSidebar"] * { color: #001F5C !important; }
    div[data-testid="stSidebar"] .stRadio label { color: #334155 !important; font-weight: 600; }
</style>
"""
