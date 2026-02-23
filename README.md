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
