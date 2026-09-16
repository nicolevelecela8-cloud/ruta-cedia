APP_CSS = """
<style>
    /* Fondo general de la app (Gris azulado ultra claro, descansa la vista) */
    .stApp { background: #F4F6F9; }
    .block-container { max-width: 1180px; padding-top: 1.5rem; padding-bottom: 3rem; }
    
    /* Títulos principales en Azul Marino de CEDIA */
    h1, h2, h3 { letter-spacing: -0.02em; color: #001F5C !important; font-weight: 700; }
    
    /* Textos normales en gris oscuro nítido (Legible en celulares) */
    p, span, label, .smallmuted { color: #334155 !important; font-size: 1rem; }
    
    /* Banner de bienvenida (Degradado premium y suave) */
    .hero {
        background: linear-gradient(135deg, #001F5C 0%, #0044CC 100%);
        color: white;
        padding: 30px 35px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(0,31,92,0.1);
    }
    .hero h1 { color: white !important; margin: 0 0 8px 0; font-size: 2.1rem; }
    .hero p { color: #E2E8F0 !important; font-size: 1.05rem; max-width: 850px; margin: 0; }
    
    /* Tarjetas en AZUL CIELO PASTEL (Adictivas y suaves al ojo) */
    .card {
        background: #EBF4FF !important; /* Azul pastel suave */
        border: 1px solid #BFDBFE;       /* Borde sutil */
        border-radius: 20px;
        padding: 22px;
        min-height: 160px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 14px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    /* Efecto flotante al pasar el mouse */
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,102,255,0.08);
    }
    .card h3 { color: #001F5C !important; margin-top: 0; font-size: 1.3rem; }
    .card p { color: #1E293B !important; font-size: 0.95rem; line-height: 1.5; }
    
    /* Botones de acción inferiores (Azul brillante interactivo) */
    div.stButton > button {
        background-color: #0066FF !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.15) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #001F5C !important;
        box-shadow: 0 6px 16px rgba(0, 31, 92, 0.25) !important;
    }
    
    /* Alertas y notas suaves */
    .note {
        background: #FEF3C7;
        border-left: 4px solid #D97706;
        padding: 12px 14px;
        border-radius: 12px;
        margin: 12px 0;
    }
    .note * { color: #78350F !important; }
    
    .successbox {
        background: #DCFCE7;
        border-left: 4px solid #16A34A;
        padding: 14px 16px;
        border-radius: 12px;
        margin: 10px 0;
    }
    .successbox * { color: #14532D !important; }
    
    /* Menú lateral izquierdo (Blanco limpio y espacioso) */
    div[data-testid="stSidebar"] { 
        background: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0;
    }
    div[data-testid="stSidebar"] * { color: #001F5C !important; }
    div[data-testid="stSidebar"] .stRadio label { color: #1E293B !important; font-weight: 500; }
</style>
"""
