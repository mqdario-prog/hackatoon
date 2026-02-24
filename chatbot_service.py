from ollama import Client
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root@db/inclusivjob')
client = Client(host='http://ollama:11434')

def generar_tarjeta_html(row):
    """Genera la tarjeta visual (esto no lo hace la IA, lo hace Python al momento)"""
    inicial = row['Empresa'][0].upper() if row['Empresa'] else "?"
    color_fuente = "bg-orange-100 text-orange-800 border-orange-200"
    if "Tecno" in row['Fuente']: color_fuente = "bg-purple-100 text-purple-800 border-purple-200"
    elif "Indeed" in row['Fuente']: color_fuente = "bg-blue-100 text-blue-800 border-blue-200"

    return f'''
    <div class="bg-white dark:bg-dark-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 my-2">
        <div class="flex flex-row items-center gap-3">
            <div class="flex-1 min-w-0">
                <h4 class="font-bold text-sm"><a href="{row['Enlace']}" target="_blank" class="text-blue-900 dark:text-blue-400 hover:underline block truncate">{row['Titulo']}</a></h4>
                <p class="text-gray-500 dark:text-gray-400 text-xs truncate">{row['Empresa']} | {row['Ubicacion']}</p>
                <div class="flex flex-wrap gap-1 mt-2">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-800 border border-green-200">✓ >33%</span>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border {color_fuente}">🌐 {row['Fuente']}</span>
                </div>
            </div>
        </div>
    </div>
    '''

def obtener_respuesta_ia(mensaje_usuario):
    try:
        # 1. BUSQUEDA EN LA BASE DE DATOS (Contexto real)
        palabras = [p for p in mensaje_usuario.split() if len(p) > 3]
        query = "SELECT * FROM ofertas LIMIT 2"
        if palabras:
            filtros = " OR ".join([f"Titulo LIKE '%%{p}%%' OR Ubicacion LIKE '%%{p}%%'" for p in palabras])
            query = f"SELECT * FROM ofertas WHERE {filtros} LIMIT 2"
        
        df = pd.read_sql(query, engine)
        
        # Creamos un resumen de texto para que la IA lo lea
        resumen_ofertas = ""
        for _, r in df.iterrows():
            resumen_ofertas += f"- Puesto: {r['Titulo']} en {r['Empresa']} ({r['Ubicacion']})\n"

        # 2. LA IA PROCESA LA INFO (Le damos los datos en texto plano)
        # Usamos phi3:mini que es inteligente pero rápido
        response = client.chat(model='phi3:mini', messages=[
            {
                'role': 'system',
                'content': f"""ACTÚA COMO UN ASISTENTE DE EMPLEO.
                
                CONTEXTO: Acabas de consultar la base de datos y HAS ENCONTRADO estas ofertas reales:
                {resumen_ofertas}
                
                INSTRUCCIONES OBLIGATORIAS:
                1. NUNCA digas que no tienes acceso a datos o internet. ¡TIENES LOS DATOS ARRIBA!
                2. Empieza la frase con "¡Buenas noticias!" o "He encontrado esto:".
                3. Menciona brevemente (1 frase) qué has encontrado.
                4. Sé amable y directo.
                """
            },
            {
                'role': 'user',
                'content': f"El usuario pregunta: {mensaje_usuario}. ¿Qué le respondo sobre las ofertas que encontré?",
            },
        ])

        respuesta_humana = response['message']['content']
        
        # 3. UNIMOS LA INTELIGENCIA CON EL DISEÑO
        if not df.empty:
            tarjetas_html = "".join([generar_tarjeta_html(row) for _, row in df.iterrows()])
            return f"{respuesta_humana}<br><br>{tarjetas_html}"
        else:
            return respuesta_humana
    
    except Exception as e:
        print(f"Error: {e}")
        return "Lo siento, estoy teniendo problemas para conectar con mi cerebro. ¿Puedes probar de nuevo?"