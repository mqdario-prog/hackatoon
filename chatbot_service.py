from ollama import Client
import pandas as pd
from sqlalchemy import create_engine

# Conexión a la DB
engine = create_engine('mysql+pymysql://root@db/inclusivjob')

# Cliente de Ollama
client = Client(host='http://ollama:11434')

def obtener_respuesta_ia(mensaje_usuario):
    try:
        # 1. Cargamos las ofertas incluyendo la columna "Enlace"
        contexto_ofertas = ""
        try:
            # Seleccionamos las columnas necesarias
            df = pd.read_sql("SELECT Titulo, Empresa, Ubicacion, Enlace FROM ofertas LIMIT 6", engine)
            
            # Formateamos el contexto para que la IA entienda qué link corresponde a qué oferta
            for _, row in df.iterrows():
                contexto_ofertas += f"- Puesto: {row['Titulo']}, Empresa: {row['Empresa']}, Ciudad: {row['Ubicacion']}, URL: {row['Enlace']}\n"
        except Exception as e:
            print(f"Error cargando DB: {e}")
            contexto_ofertas = "No hay ofertas disponibles ahora."

        # 2. Llamada a Ollama con instrucciones de formato HTML
        response = client.chat(model='llama3', messages=[
            {
                'role': 'system',
                'content': f"""Eres el asistente de InclusivJob. Ayudas a personas con discapacidad a encontrar empleo.
                
                REGLA DE ORO: Cuando menciones una oferta de trabajo del contexto, DEBES poner el título como un enlace HTML 
                usando este formato exacto: <a href='URL' target='_blank' style='color: #1E40AF; font-weight: bold; text-decoration: underline;'>Título del Puesto</a>.

                CONTEXTO DISPONIBLE:
                {contexto_ofertas}

                Responde de forma muy humana, empática y en español. Si no hay una oferta que coincida exactamente, 
                recomienda las más cercanas del contexto."""
            },
            {
                'role': 'user',
                'content': mensaje_usuario,
            },
        ])

        return response['message']['content']
    
    except Exception as e:
        print(f"Error Ollama: {e}")
        return "Lo siento, mi cerebro de IA está descansando. ¿Puedes intentarlo en un momento?"