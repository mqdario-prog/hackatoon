from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from weasyprint import HTML
from io import BytesIO
from pydantic import BaseModel
import pandas as pd
import os
import random
import math
from chatbot_service import obtener_respuesta_ia
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from sqlalchemy import create_engine
from fastapi.staticfiles import StaticFiles


engine = create_engine('mysql+pymysql://root@db/inclusivjob')

# Iniciamos el geolocalizador (Pon un nombre único en user_agent)
geolocator = Nominatim(user_agent="mi_buscador_empleo_v1")

# Caché simple para no preguntar a internet todo el rato
coords_cache = {}

def obtener_coords(ciudad):
    if not ciudad: return None
    ciudad = ciudad.lower().strip()
    
    ciudad_limpia = ciudad.split(',')[0] 
    
    if ciudad_limpia in coords_cache: return coords_cache[ciudad_limpia]
    
    try:
        # Buscamos en España
        location = geolocator.geocode(f"{ciudad_limpia}, España", timeout=10)
        if location:
            punto = (location.latitude, location.longitude)
            coords_cache[ciudad_limpia] = punto
            return punto
    except:
        return None
    return None


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    # 1. Cargar datos
    try:
        df = pd.read_sql("SELECT * FROM ofertas", engine)
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
    
    # B) Filtro por Ubicación + Radio (Lógica Nueva)
    # Capturamos el radio desde la URL (si no viene, es 0)
    try: 
        radio_km = int(request.query_params.get("radio", 0))
    except: 
        radio_km = 0

    if not ubicacion.strip():
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

    # --- BLOQUE DE PAGINACIÓN (Sácalo fuera de cualquier IF/ELSE) ---
    TOTAL_POR_PAGINA = 5
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