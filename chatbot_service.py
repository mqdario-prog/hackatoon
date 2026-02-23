import random
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root@db/inclusivjob')

def cargar_ofertas():
    try:
        # Consulta a MySQL
        return pd.read_sql("SELECT * FROM ofertas", engine)
    except:
        return pd.DataFrame()

df_ofertas = cargar_ofertas()

def buscar_ofertas_por_palabra(palabra):
    """Busca ofertas en el CSV que contengan la palabra clave"""
    if df_ofertas.empty:
        return []
    
    # Filtrar
    filtro = df_ofertas[
        df_ofertas['Titulo'].str.contains(palabra, case=False, na=False) | 
        df_ofertas['Ubicacion'].str.contains(palabra, case=False, na=False)
    ]
    
    # Devolver las 3 primeras como lista de diccionarios
    return filtro.head(3).to_dict(orient='records')

def obtener_respuesta_avanzada(mensaje):
    mensaje = mensaje.lower()
    
    # --- 1. BÚSQUEDA DE OFERTAS (INTELIGENTE) ---
    # Si el usuario dice "busco trabajo de administrativo" o "ofertas en Madrid"
    palabras_clave_busqueda = ["busco", "trabajo de", "ofertas en", "empleo de", "puesto de"]
    
    for key in palabras_clave_busqueda:
        if key in mensaje:
            # Intentar extraer la palabra clave (ej: "administrativo")
            busqueda = mensaje.split(key)[-1].strip().split()[0] # Coge la primera palabra tras la clave
            if len(busqueda) > 2:
                resultados = buscar_ofertas_por_palabra(busqueda)
                if resultados:
                    respuesta = f"He encontrado estas ofertas para '{busqueda}':<br>"
                    for oferta in resultados:
                        respuesta += f"🔹 <a href='{oferta['Enlace']}' target='_blank'>{oferta['Titulo']}</a> ({oferta['Ubicacion']})<br>"
                    return respuesta + "<br>Puedes ver más en el buscador principal."
                else:
                    return f"No he encontrado ofertas específicas para '{busqueda}' ahora mismo, pero prueba buscando en la barra superior."

    # --- 2. CATEGORÍAS DE PREGUNTAS ---
    
    # A) ENTREVISTAS
    if any(x in mensaje for x in ["entrevista", "nervioso", "que digo", "ropa", "vestimenta"]):
        respuestas = [
            "Para la entrevista: Sé puntual, investiga la empresa y sé sincero sobre tus capacidades. Si necesitas adaptación, dilo con naturalidad.",
            "Un consejo: Prepara ejemplos de problemas que hayas resuelto. Enfócate en lo que SÍ puedes hacer, no en tus limitaciones.",
            "Sobre la discapacidad en la entrevista: No es obligatorio mencionarla salvo que el puesto requiera adaptación específica o sea un Centro Especial de Empleo."
        ]
        return random.choice(respuestas)

    # B) CURRICULUM (CV)
    elif any(x in mensaje for x in ["cv", "curriculum", "hoja de vida", "foto"]):
        return ("Tu CV debe ser claro y accesible. Tips: <br>"
                "1. Usa letra legible (Arial, Sans-serif).<br>"
                "2. Destaca herramientas que manejas.<br>"
                "3. Si tienes certificado de discapacidad, ponlo en 'Otros datos' si la oferta es para personas con discapacidad.")

    # C) LEGAL / DERECHOS
    elif any(x in mensaje for x in ["ley", "derecho", "contrato", "despido", "baja"]):
        return ("Importante: Las empresas de +50 empleados deben reservar el 2% de puestos. "
                "Tienes derecho a solicitar adaptaciones del puesto de trabajo según la Ley General de Derechos de las Personas con Discapacidad.")

    # D) FORMACIÓN / CURSOS
    elif any(x in mensaje for x in ["curso", "estudiar", "formacion", "aprender"]):
        return ("La formación es clave. Te recomiendo mirar cursos gratuitos en: <br>"
                "👉 <a href='https://www.fundaciononce.es/' target='_blank'>Fundación ONCE</a><br>"
                "👉 <a href='https://www.fundae.es/' target='_blank'>Fundae (Cursos estatales)</a>")

    # E) AYUDAS / PRESTACIONES
    elif any(x in mensaje for x in ["ayuda", "paga", "subvencion", "dinero"]):
        return "Sobre ayudas: Existen deducciones fiscales para trabajadores activos con discapacidad y bonificaciones a la empresa. Para prestaciones específicas, consulta la web de la Seguridad Social."

    # F) SALUDO / DESPEDIDA
    elif any(x in mensaje for x in ["hola", "buenas", "hey"]):
        return "¡Hola! 👋 Soy tu asistente virtual. Puedo buscar ofertas por ti (ej: 'busco trabajo de limpieza') o darte consejos de entrevista. ¿En qué te ayudo?"
    
    elif any(x in mensaje for x in ["adios", "chao", "gracias"]):
        return "¡Gracias a ti! Mucha suerte en tu búsqueda. Aquí estaré si necesitas más ayuda. 💪"

    # RESPUESTA GENÉRICA
    else:
        return ("No estoy seguro de haberte entendido bien. 😅<br>"
                "Prueba a decirme cosas como:<br>"
                "- 'Busco trabajo de administrativo'<br>"
                "- 'Consejos para entrevista'<br>"
                "- 'Cómo mejorar mi CV'")

