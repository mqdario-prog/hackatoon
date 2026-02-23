# ♿ InclusivJob - Empleo Sin Barreras

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-005571.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**InclusivJob** es una plataforma de búsqueda de empleo diseñada específicamente para **personas con discapacidad**. El sistema centraliza ofertas de múltiples portales y ofrece herramientas de accesibilidad avanzadas para garantizar que nadie se quede atrás en el mercado laboral.

---

## ✨ Características Principales

*   **🕵️ Agregador Automático:** Motores de Web Scraping para InfoEmpleo y TecnoEmpleo.
*   **📍 Mapa de Oportunidades:** Visualización geográfica de vacantes mediante clusters interactivos.
*   **🤖 Asistente Virtual:** Chatbot con inteligencia para búsqueda rápida y consejos laborales.
*   **♿ Accesibilidad Universal (A11Y):**
    *   **Dictado por voz:** Búsqueda manos libres mediante voz.
    *   **Lectura de pantalla:** Síntesis de voz integrada para navegar por el contenido.
    *   **Modos visuales:** Filtros para Daltonismo (Protanopia, etc.), Alto Contraste y fuente para Dislexia.

---

## 🛠️ Stack Tecnológico

*   **Backend:** FastAPI (Python)
*   **Database:** MySQL (XAMPP / Docker)
*   **Scraping:** Selenium & BeautifulSoup4
*   **Frontend:** Tailwind CSS, Leaflet.js (Mapas), Jinja2
*   **Infraestructura:** Docker & Docker Compose

---

## 🚀 Instalación Rápida (Docker)

La forma más sencilla de ejecutar el proyecto es usando Docker:

1.  **Clonar y Construir:**
    ```bash
    git clone https://github.com/tu-usuario/inclusivjob.git
    cd inclusivjob
    docker-compose up --build
    ```

2.  **Llenar la Base de Datos:**
    Con los contenedores encendidos, abre otra terminal y ejecuta el scraper:
    ```bash
    docker exec -it inclusivjob_app python scraper.py
    ```

3.  **Disfrutar:**
    Ve a [http://localhost:8000](http://localhost:8000) en tu navegador.

---

## 👨‍💻 Autores
Proyecto desarrollado para **Hackathon OdiseIA4Good**. Enfocado en crear tecnología con impacto social.
pip install weasyprint jinja2
pip install weasyprint[fonts]
 main.py al final 
 from fastapi import Form, Request
from fastapi.responses import HTMLResponse
from weasyprint import HTML
from io import BytesIO
import zipfile

# Ruta para mostrar el formulario
@app.get("/cv", response_class=HTMLResponse)
def cv_form(request: Request):
    return templates.TemplateResponse("cv_form.html", {"request": request})

# Ruta POST para procesar formulario y generar PDF
@app.post("/generar-cv")
def generar_cv(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(None),
    linkedin: str = Form(None),
    puesto_actual: str = Form(...),
    empresa_actual: str = Form(...),
    experiencias: str = Form(None),
    habilidades: str = Form(None),
    educacion: str = Form(None)
):
    # Procesar listas
    experiencias_lista = [exp.strip() for exp in experiencias.split(',') if exp.strip()] if experiencias else []
    habilidades_lista = [hab.strip() for hab in habilidades.split(',') if hab.strip()] if habilidades else []
    
    # Renderizar el template del CV con los datos
    html_string = templates.get_template("cv_template.html").render({
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "linkedin": linkedin,
        "puesto_actual": puesto_actual,
        "empresa_actual": empresa_actual,
        "experiencias": experiencias_lista,
        "habilidades": habilidades_lista,
        "educacion": educacion
    })
    
    # Generar PDF desde HTML
    html = HTML(string=html_string)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    # Devolver el PDF para descargar
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=cv_{nombre.replace(' ', '_')}.pdf"
        }
    )
index.html el enlace 
<a href="/cv" class="bg-green-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-green-700 transition-all">
    📄 Crear mi CV
</a>

