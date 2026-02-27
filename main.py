import time
import pandas as pd
import os
import random
import math
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from weasyprint import HTML
from io import BytesIO
from pydantic import BaseModel
from chatbot_service import obtener_respuesta_ia
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from sqlalchemy import create_engine
from fastapi.staticfiles import StaticFiles


engine = create_engine('mysql+pymysql://root@db/inclusivjob')

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Iniciamos el geolocalizador (Pon un nombre único en user_agent)
geolocator = Nominatim(user_agent="InclusivJob_Social_Project_Hackathon_2026_Final")

# Caché simple para no preguntar a internet todo el rato
coords_cache = {}

COORDS_PREDETERMINADAS = {
    "madrid": (40.4167, -3.7037),
    "barcelona": (41.3851, 2.1734),
    "valencia": (39.4699, -0.3763),
    "sevilla": (37.3891, -5.9845),
    "malaga": (36.7213, -4.4213),
    "zaragoza": (41.6488, -0.8891),
    "murcia": (37.9922, -1.1307),
    "palma": (39.5696, 2.6502),
    "vigo": (42.2406, -8.7207),
    "alicante": (38.3452, -0.4815),
    "bilbao": (43.2630, -2.9350),
    "vallromanes": (41.5311, 2.3025),
    "alcasser": (39.3695, -0.4452),
    "benavente": (42.0025, -5.6769),
    "logroño": (42.4627, -2.4450),
    "alcala de guadaira": (37.3333, -5.8500),
    "getafe": (40.3084, -3.7312),
    "borox": (40.0706, -3.7356),
    "leganes": (40.3282, -3.7635),
    "santiago de compostela": (42.8782, -8.5448),
    "gÜimar": (28.3144, -16.4136),
    "selva del camp": (41.2144, 1.1372),
    "paracuellos del jarama": (40.5050, -3.4900)
}

def obtener_coords(ciudad):
    if not ciudad: return None
    ciudad = ciudad.lower().strip()
    
    ciudad_limpia = str(ciudad).split(',')[0].split('(')[0].strip()
    c_key = ciudad_limpia.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
    
    # 2. CASO ESPECIAL: ESPAÑA O REMOTO
    if c_key in ["españa", "100% remoto", "remoto", "vagas", "varias"]:
        return (40.4637, -3.7492) # Centro de España

    # 3. BUSCAR EN DICCIONARIO LOCAL (Evita llamar a la API y el error 429)
    if c_key in COORDS_PREDETERMINADAS:
        return COORDS_PREDETERMINADAS[c_key]

    # 4. BUSCAR EN CACHÉ DE SESIÓN
    if ciudad_limpia in coords_cache:
        return coords_cache[ciudad_limpia]
    
    try:
        # Buscamos en España
        time.sleep(0.5) 
        location = geolocator.geocode(f"{ciudad_limpia}, España", timeout=10)
        if location:
            punto = (location.latitude, location.longitude)
            coords_cache[ciudad_limpia] = punto
            return punto
    except Exception as e:
        print(f"⚠️ Error API en {ciudad_limpia}: {e}")
        return None
    return None


class MensajeChat(BaseModel):
    texto: str

# Generador CVs

@app.get("/cv", response_class=HTMLResponse)
def cv_form(request: Request):
    # Asegúrate de que cv_form.html esté en la carpeta templates/
    return templates.TemplateResponse("cv_form.html", {"request": request})

@app.post("/generar-cv")
def generar_cv(
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(None),
    linkedin: str = Form(None),
    ciudad: str = Form(None),
    certificado_discapacidad: str = Form(...),
    perfil: str = Form(None),
    puesto_actual: str = Form(...),
    empresa_actual: str = Form(...),
    experiencias: str = Form(None),
    habilidades: str = Form(None),
    educacion: str = Form(None),
    idiomas: str = Form(None)
):
    # Procesar strings a listas
    experiencias_lista = [exp.strip() for exp in experiencias.split(',') if exp.strip()] if experiencias else []
    habilidades_lista = [hab.strip() for hab in habilidades.split(',') if hab.strip()] if habilidades else []
    idiomas_lista = [lang.strip() for lang in idiomas.split(',') if lang.strip()] if idiomas else []
    
    html_string = templates.get_template("cv_template.html").render({
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "linkedin": linkedin,
        "ciudad": ciudad,
        "certificado_discapacidad": certificado_discapacidad,
        "perfil": perfil,
        "puesto_actual": puesto_actual,
        "empresa_actual": empresa_actual,
        "experiencias": experiencias_lista,
        "habilidades": habilidades_lista,
        "educacion": educacion,
        "idiomas": idiomas_lista
    })
    
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=CV_{nombre.replace(' ', '_')}.pdf"}
    )

# En main.py

@app.get("/", response_class=HTMLResponse)
def home(request: Request, pagina: int = 1, busqueda: str = "", ubicacion: str = ""):
    # 1. Cargar datos (Optimizado: solo traemos las columnas necesarias)
    try:
        df = pd.read_sql("SELECT Titulo, Empresa, Ubicacion, Enlace, Fuente, Etiquetas FROM ofertas", engine)
        df = df.fillna("") 
    except Exception as e:
        print(f"Error cargando MySQL: {e}")
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
    
    # B) Filtro por Ubicación + Radio
    try: 
        radio_km = int(request.query_params.get("radio", 0))
    except: 
        radio_km = 0

    if not ubicacion.strip():
        radio_km = 0

    if ubicacion:
        ubicacion_usuario = ubicacion.lower().strip()
        
        if radio_km > 0:
            coords_origen = obtener_coords(ubicacion_usuario)
            if coords_origen:
                indices_validos = []
                for idx, row in df.iterrows():
                    loc_oferta = str(row['Ubicacion']).lower().strip()
                    # Coincidencia exacta
                    if ubicacion_usuario in loc_oferta:
                        indices_validos.append(idx)
                        continue
                    # Cálculo de distancia
                    coords_destino = obtener_coords(loc_oferta)
                    if coords_destino:
                        try:
                            dist = geodesic(coords_origen, coords_destino).km
                            if dist <= radio_km:
                                indices_validos.append(idx)
                        except: pass
                df = df.loc[indices_validos]
            else:
                df = df[df['Ubicacion'].str.lower().str.contains(ubicacion_usuario, na=False)]
        else:
            df = df[df['Ubicacion'].str.lower().str.contains(ubicacion_usuario, na=False)]

    # --- BLOQUE DE PAGINACIÓN (Optimizado para evitar errores de rango) ---
    TOTAL_POR_PAGINA = 5
    total_ofertas = len(df)
    total_paginas = max(1, math.ceil(total_ofertas / TOTAL_POR_PAGINA))

    # Aseguramos que la página esté en el rango correcto
    pagina = max(1, min(pagina, total_paginas))

    inicio = (pagina - 1) * TOTAL_POR_PAGINA
    fin = inicio + TOTAL_POR_PAGINA
    
    ofertas_paginadas = df.iloc[inicio:fin].to_dict(orient='records')

    # --- RETORNO FINAL (Ya no procesamos el mapa aquí para ganar velocidad) ---
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ofertas": ofertas_paginadas,  
        "total_ofertas": total_ofertas,
        "pagina_actual": pagina,
        "total_paginas": total_paginas,
        "busqueda": busqueda,
        "ubicacion": ubicacion,
        "radio": radio_km
    })

@app.get("/api/marcadores")
async def api_marcadores():
    try:
        df = pd.read_sql("SELECT Ubicacion FROM ofertas", engine)
        top_ciudades = df['Ubicacion'].value_counts().head(15)
        
        marcadores = []
        for ciudad, cantidad in top_ciudades.items():
            coords = obtener_coords(ciudad) # Esta función usa el diccionario y el sleep
            if coords:
                marcadores.append({
                    "lat": coords[0],
                    "lon": coords[1],
                    "ciudad": ciudad,
                    "cantidad": int(cantidad)
                })
        return marcadores
    except Exception as e:
        print(f"Error al obtener marcadores: {e}")
        return []

@app.get("/privacidad", response_class=HTMLResponse)
def privacidad(request: Request):
    return templates.TemplateResponse("privacidad.html", {"request": request})

@app.get("/terminos", response_class=HTMLResponse)
def terminos(request: Request):
    return templates.TemplateResponse("terminos.html", {"request": request})

@app.get("/cookies", response_class=HTMLResponse)
def cookies(request: Request):
    return templates.TemplateResponse("cookies.html", {"request": request})

@app.post("/api/chat") # O la ruta que uses
def chatear(datos: MensajeChat):
    respuesta = obtener_respuesta_ia(datos.texto)
    return {"respuesta": respuesta}