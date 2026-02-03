from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd
import os
import random
import math
from chatbot_service import obtener_respuesta_avanzada
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Iniciamos el geolocalizador (Pon un nombre único en user_agent)
geolocator = Nominatim(user_agent="mi_buscador_empleo_v1")

# Caché simple para no preguntar a internet todo el rato
coords_cache = {}

def obtener_coords(ciudad):
    if not ciudad: return None
    ciudad = ciudad.lower().strip()
    if ciudad in coords_cache: return coords_cache[ciudad]
    
    try:
        # Buscamos en España
        location = geolocator.geocode(f"{ciudad}, España", timeout=5)
        if location:
            punto = (location.latitude, location.longitude)
            coords_cache[ciudad] = punto
            return punto
    except:
        return None
    return None


app = FastAPI()
templates = Jinja2Templates(directory="templates")

class MensajeChat(BaseModel):
    texto: str

# --- CEREBRO GRATUITO (Lógica Python) ---
def cerebro_gratuito(pregunta, df):
    pregunta = pregunta.lower()
    
    # 1. Saludos básicos
    if any(x in pregunta for x in ['hola', 'buenos días', 'buenas']):
        return "¡Hola! Soy tu asistente de empleo inclusivo. Pregúntame por ofertas (ej: 'busco administrativo' o 'trabajo en Madrid')."
    
    # 2. Si no hay datos cargados
    if df.empty:
        return "Lo siento, ahora mismo no tengo acceso a la base de datos de ofertas. Prueba a ejecutar el scraper."

    # 3. Búsqueda inteligente en el CSV
    ofertas_encontradas = []
    
    # Buscamos coincidencias en Título o Ubicación
    for _, row in df.iterrows():
        titulo = str(row.get('Titulo', '')).lower()
        ubicacion = str(row.get('Ubicacion', '')).lower()
        
        # Si la palabra clave del usuario está en el título o ubicación
        palabras_usuario = [p for p in pregunta.split() if len(p) > 3] # Ignoramos palabras cortas (de, la, en...)
        
        match = False
        for palabra in palabras_usuario:
            if palabra in titulo or palabra in ubicacion:
                match = True
                break
        
        if match:
            ofertas_encontradas.append(f"- {row['Titulo']} en {row['Empresa']} ({row['Ubicacion']})")

    # 4. Generar respuesta
    if ofertas_encontradas:
        num = len(ofertas_encontradas)
        lista_txt = "<br>".join(ofertas_encontradas[:3]) # Mostramos máx 3
        return f"¡He encontrado {num} ofertas que podrían interesarte!<br><br>{lista_txt}<br><br>¿Te gustaría ver el enlace de alguna?"
    
    # 5. Respuestas genéricas si no entiende
    respuestas_fallback = [
        "No he encontrado ofertas exactas con esos términos. ¿Prueba a buscar por ciudad (ej: 'Madrid')?",
        "Mmm, no veo nada específico para eso ahora mismo. ¿Te interesa ver todas las ofertas disponibles?",
        "Entendido. Para ayudarte mejor, ¿buscas un puesto específico o prefieres filtrar por ubicación?"
    ]
    return random.choice(respuestas_fallback)

# En main.py

@app.get("/", response_class=HTMLResponse)
def home(request: Request, pagina: int = 1, busqueda: str = "", ubicacion: str = ""):
    # 1. Cargar datos
    try:
        df = pd.read_csv('ofertas_discapacidad.csv')
        # IMPRESCINDIBLE: Rellenar vacíos para que no falle el filtro
        df = df.fillna("") 
    except Exception as e:
        print(f"Error cargando CSV: {e}")
        df = pd.DataFrame(columns=["Titulo", "Empresa", "Ubicacion", "Enlace", "Fuente", "Etiquetas"])

       # ---------------------------------------------------------
    # 2. FILTRADO (BÚSQUEDA + UBICACIÓN + DISTANCIA)
    # ---------------------------------------------------------
    
    # A) Filtro por Palabra Clave
    if busqueda:
        busqueda = busqueda.lower().strip()
        df = df[
            df['Titulo'].str.lower().str.contains(busqueda, na=False) | 
            df['Etiquetas'].str.lower().str.contains(busqueda, na=False) |
            df['Empresa'].str.lower().str.contains(busqueda, na=False)
        ]
    
    # B) Filtro por Ubicación + Radio (Lógica Nueva)
    # Capturamos el radio desde la URL (si no viene, es 0)
    try: 
        radio_km = int(request.query_params.get("radio", 0))
    except: 
        radio_km = 0

    if ubicacion:
        ubicacion_usuario = ubicacion.lower().strip()
        
        if radio_km > 0:
            # --- CÁLCULO DE DISTANCIA (Geopy) ---
            coords_origen = obtener_coords(ubicacion_usuario)
            
            if coords_origen:
                indices_validos = []
                for idx, row in df.iterrows():
                    loc_oferta = str(row['Ubicacion']).lower().strip()
                    
                    # 1. Coincidencia exacta (siempre vale)
                    if ubicacion_usuario in loc_oferta:
                        indices_validos.append(idx)
                        continue
                    
                    # 2. Cálculo de distancia
                    coords_destino = obtener_coords(loc_oferta)
                    if coords_destino:
                        try:
                            dist = geodesic(coords_origen, coords_destino).km
                            if dist <= radio_km:
                                indices_validos.append(idx)
                        except: pass
                
                # Filtramos el DataFrame con los índices que cumplen
                df = df.loc[indices_validos]
            else:
                # Si falla geocodificación, volvemos a búsqueda de texto simple
                df = df[df['Ubicacion'].str.lower().str.contains(ubicacion_usuario, na=False)]
        else:
            # --- BÚSQUEDA EXACTA (Sin radio) ---
            df = df[df['Ubicacion'].str.lower().str.contains(ubicacion_usuario, na=False)]

    TOTAL_POR_PAGINA = 10


    # --- BLOQUE DE PAGINACIÓN (Sácalo fuera de cualquier IF/ELSE) ---
    TOTAL_POR_PAGINA = 10
    total_ofertas = len(df)
    
    if total_ofertas > 0:
        total_paginas = math.ceil(total_ofertas / TOTAL_POR_PAGINA)
    else:
        total_paginas = 1

    if pagina < 1: pagina = 1
    if pagina > total_paginas: pagina = total_paginas

    inicio = (pagina - 1) * TOTAL_POR_PAGINA
    fin = inicio + TOTAL_POR_PAGINA
    
    # ESTA LÍNEA ES LA QUE TE FALTA O NO SE LEÍA
    ofertas_paginadas = df.iloc[inicio:fin].to_dict(orient='records')
        # Generar datos para el mapa (Solo de las ofertas paginadas para no saturar)
    # O mejor: de TODAS las ofertas filtradas (para ver el panorama completo)
    marcadores_mapa = []
    
    # Agrupamos por ciudad para no poner 100 puntos en el mismo sitio
    conteo_ciudades = df['Ubicacion'].value_counts()
    
    for ciudad, cantidad in conteo_ciudades.items():
        coords = obtener_coords(ciudad)
        if coords:
            marcadores_mapa.append({
                "lat": coords[0],
                "lon": coords[1],
                "ciudad": ciudad,
                "cantidad": int(cantidad) # Convertir a int nativo para JSON
            })


    # --- RETORNO FINAL ---
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ofertas": ofertas_paginadas,  
        "total_ofertas": total_ofertas,
        "pagina_actual": pagina,
        "total_paginas": total_paginas,
        "busqueda": busqueda,
        "ubicacion": ubicacion,
        "radio": radio_km,  
        "marcadores": marcadores_mapa 
    })





@app.post("/api/chat")
async def chat_endpoint(mensaje: MensajeChat):
    # Cargar datos frescos
    df = pd.DataFrame()
    if os.path.exists('ofertas_discapacidad.csv'):
        try:
            df = pd.read_csv('ofertas_discapacidad.csv')
        except:
            pass
    
    # Usar el cerebro gratuito
    respuesta = cerebro_gratuito(mensaje.texto, df)
    return JSONResponse(content={"respuesta": respuesta})


class MensajeChat(BaseModel):
    mensaje: str

@app.post("/api/chat") # O la ruta que uses
def chatear(datos: MensajeChat):
    respuesta = obtener_respuesta_avanzada(datos.mensaje)
    return {"respuesta": respuesta}





