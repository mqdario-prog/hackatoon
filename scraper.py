import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine
import random

# --- CONFIGURACIÓN DEL NAVEGADOR (Mejorada para evitar bloqueos) ---
def setup_driver():
    options = Options()
    options.add_argument('--headless') # OBLIGATORIO EN DOCKER
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0...")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- 1. INFOEMPLEO (Selector mejorado) ---
def scrape_infoempleo(driver, busqueda="discapacidad", ubicacion="", objetivo=30):
    print(f"🔄 INFOEMPLEO: Buscando ofertas...")
    url = f"https://www.infoempleo.com/trabajo/i/{busqueda}/"
    driver.get(url)
    time.sleep(5)
    
    ofertas = []
    try:
        try: driver.find_element(By.ID, "didomi-notice-agree-button").click()
        except: pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Buscamos cada bloque de oferta (el <li> completo)
        bloques = soup.find_all('li', class_='offerblock')
        
        for bloque in bloques:
            if len(ofertas) >= objetivo: break
            try:
                # 1. Título y Enlace
                t_tag = bloque.find('h2', class_='title')
                enlace_tag = t_tag.find('a') if t_tag else None
                if not enlace_tag: continue
                
                titulo = enlace_tag.text.strip()
                link = "https://www.infoempleo.com" + enlace_tag['href']
                
                # 2. Empresa (está dentro de div.logoplusname -> span.extra-data)
                empresa = "InfoEmpleo"
                emp_div = bloque.find('div', class_='logoplusname')
                if emp_div:
                    emp_span = emp_div.find('span', class_='extra-data')
                    if emp_span: empresa = emp_span.text.strip()
                
                # 3. Ubicación (buscamos el <p class="extra-data"> que tiene el icono del mapa)
                loc = "España"
                parrafos_extra = bloque.find_all('p', class_='extra-data')
                for p in parrafos_extra:
                    # Si el párrafo tiene el SVG del marcador de mapa
                    if p.find('svg', class_='icon-map-marker'):
                        loc = p.get_text(strip=True)
                        break

                ofertas.append({
                    "Titulo": titulo, 
                    "Empresa": empresa, 
                    "Ubicacion": loc, 
                    "Enlace": link, 
                    "Fuente": "InfoEmpleo", 
                    "Etiquetas": "General"
                })
            except Exception as e: 
                continue

    except Exception as e:
        print(f"⚠️ Error InfoEmpleo: {e}")
    
    print(f"✅ InfoEmpleo: {len(ofertas)} ofertas.")
    return ofertas

# --- 2. TECNOEMPLEO (Búsqueda por H3) ---
def scrape_tecnoempleo(driver, busqueda="discapacidad", objetivo=30):
    print(f"🔄 TECNOEMPLEO: Buscando ofertas IT...")
    url = f"https://www.tecnoempleo.com/ofertas-trabajo/?te={busqueda}"
    driver.get(url)
    time.sleep(5)
    
    ofertas = []
    try:
        # Intentar cerrar cookies
        try: driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except: pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Cada oferta está en un div con clase 'row fs--15'
        bloques = soup.find_all('div', class_='row fs--15')
        
        for bloque in bloques:
            if len(ofertas) >= objetivo: break
            try:
                # 1. Título y Enlace (Dentro del h3)
                h3_tag = bloque.find('h3')
                if not h3_tag: continue
                enlace_tag = h3_tag.find('a')
                if not enlace_tag: continue
                
                titulo = enlace_tag.get_text(strip=True)
                link = enlace_tag['href']
                
                # 2. Empresa (Es un enlace con clase 'text-primary')
                empresa = "TecnoEmpleo"
                emp_tag = bloque.find('a', class_='text-primary')
                if emp_tag:
                    empresa = emp_tag.get_text(strip=True)
                
                # 3. Ubicación (Tecnoempleo la pone dentro de una etiqueta <b>)
                # Suele aparecer como <b>Madrid</b> (Híbrido)
                loc = "España"
                loc_tag = bloque.find('b')
                if loc_tag:
                    loc = loc_tag.get_text(strip=True)

                ofertas.append({
                    "Titulo": titulo, 
                    "Empresa": empresa, 
                    "Ubicacion": loc, 
                    "Enlace": link, 
                    "Fuente": "TecnoEmpleo", 
                    "Etiquetas": "Tecnología"
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"⚠️ Error TecnoEmpleo: {e}")
        
    print(f"✅ TecnoEmpleo: {len(ofertas)} ofertas.")
    return ofertas

# --- 3. INDEED (Arreglado para versión 2025/2026) ---
def scrape_indeed(driver, busqueda="discapacidad", ubicacion="España", objetivo=30):
    print(f"🔄 INDEED: Buscando ofertas...")
    ofertas = []
    # Indeed bloquea mucho si pasas paginas rápido. Hacemos solo la página 1 y 2 con cuidado.
    urls = [
        f"https://es.indeed.com/jobs?q={busqueda}&l={ubicacion}",
        f"https://es.indeed.com/jobs?q={busqueda}&l={ubicacion}&start=10"
    ]
    
    for url in urls:
        if len(ofertas) >= objetivo: break
        driver.get(url)
        time.sleep(random.uniform(5, 8)) # Espera larga para parecer humano
        
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Nuevo selector Indeed 2025: Buscamos <h2> con clase jobTitle
            job_titles = soup.find_all('h2', class_='jobTitle')
            
            # Si falla, intentamos selector genérico de enlaces
            if not job_titles:
                 job_titles = soup.find_all('a', class_='jcs-JobTitle')

            for h2 in job_titles:
                try:
                    # A veces el h2 contiene el link, a veces es el link mismo
                    if h2.name == 'a':
                        link_tag = h2
                    else:
                        link_tag = h2.find('a')
                    
                    if not link_tag: continue

                    titulo = link_tag.text.strip()
                    href = link_tag['href']
                    if not href.startswith('http'):
                        enlace = "https://es.indeed.com" + href
                    else:
                        enlace = href
                    
                    # Intentar sacar empresa (es difícil en Indeed por clases dinámicas)
                    # Ponemos un valor por defecto para no romper el código
                    empresa = "Empresa en Indeed"
                    contenedor = h2.find_parent('div', class_='job_seen_beacon') or h2.find_parent('td')
                    
                    if contenedor:
                        emp_span = contenedor.find('span', {'data-testid': 'company-name'})
                        if emp_span: empresa = emp_span.text.strip()
                        
                        loc_div = contenedor.find('div', {'data-testid': 'text-location'})
                        if loc_div: ubicacion = loc_div.text.strip()

                    ofertas.append({
                        "Titulo": titulo, 
                        "Empresa": empresa, 
                        "Ubicacion": ubicacion, 
                        "Enlace": enlace, 
                        "Fuente": "Indeed", 
                        "Etiquetas": "Inclusiva"
                    })
                except: continue
        except Exception as e:
            print(f"⚠️ Error parcial Indeed: {e}")
            continue

    print(f"✅ Indeed: {len(ofertas)} ofertas.")
    return ofertas

# --- EJECUCIÓN GLOBAL ---
def ejecutar_scraping_completo():
    driver = setup_driver()
    datos_totales = []
    
    try:
        # 1. InfoEmpleo
        datos_totales.extend(scrape_infoempleo(driver))
        time.sleep(2)
        
        # 2. TecnoEmpleo
        datos_totales.extend(scrape_tecnoempleo(driver))
        time.sleep(2)

        # 3. Indeed
        datos_totales.extend(scrape_indeed(driver))
        
    finally:
        driver.quit()
    
    df = pd.DataFrame(datos_totales)
    if not df.empty:
        # Eliminamos duplicados antes de guardar
        df = df.drop_duplicates(subset=['Enlace'])
        engine = create_engine('mysql+pymysql://root@db/inclusivjob')
        df.to_sql('ofertas', con=engine, if_exists='replace', index=False)
        return df
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    df_resultado = ejecutar_scraping_completo()
    if not df_resultado.empty:
        print(f"💾 Base de datos actualizada con {len(df_resultado)} ofertas.")
    else:
        print("❌ No se encontraron ofertas nuevas.")
