import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import random

# --- CONFIGURACIÓN DEL NAVEGADOR (Mejorada para evitar bloqueos) ---
def setup_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--start-maximized")
    # User Agent de Chrome real actualizado (Enero 2026)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# --- 1. INFOEMPLEO (Selector mejorado) ---
def scrape_infoempleo(driver, busqueda="discapacidad", ubicacion="", objetivo=30):
    print(f"🔄 INFOEMPLEO: Buscando ofertas...")
    url = f"https://www.infoempleo.com/trabajo/i/{busqueda}/"
    driver.get(url)
    time.sleep(5)
    
    ofertas = []
    try:
        # Intentar cerrar cookies (varios selectores posibles)
        try: driver.find_element(By.ID, "didomi-notice-agree-button").click()
        except: pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Estrategia: Buscar todos los H2 con clase 'title' (es lo más estable)
        titulos = soup.find_all('h2', class_='title')
        
        for t in titulos:
            if len(ofertas) >= objetivo: break
            try:
                enlace_tag = t.find('a')
                if not enlace_tag: continue
                
                titulo = enlace_tag.text.strip()
                link = "https://www.infoempleo.com" + enlace_tag['href']
                
                # Intentamos buscar la empresa y ubicación subiendo al padre
                contenedor = t.find_parent('li') or t.find_parent('div')
                
                empresa = "InfoEmpleo"
                loc = "España"
                
                if contenedor:
                    emp_tag = contenedor.find('p', class_='company')
                    if emp_tag: empresa = emp_tag.text.strip()
                    
                    loc_tag = contenedor.find('span', class_='location')
                    if loc_tag: loc = loc_tag.text.strip()

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
def scrape_tecnoempleo(driver, busqueda="discapacidad", ubicacion="", objetivo=30):
    print(f"🔄 TECNOEMPLEO: Buscando ofertas IT...")
    url = f"https://www.tecnoempleo.com/ofertas-trabajo/?te={busqueda}"
    driver.get(url)
    time.sleep(5)
    
    ofertas = []
    try:
        try: driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except: pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # TecnoEmpleo usa H3 para los títulos de las ofertas. Buscamos eso directamente.
        titulos = soup.find_all('h3')
        
        for t in titulos:
            if len(ofertas) >= objetivo: break
            try:
                enlace_tag = t.find('a')
                if not enlace_tag: continue
                
                titulo = t.text.strip()
                link = enlace_tag['href']
                
                # Subir al contenedor padre para buscar empresa
                contenedor = t.find_parent('div')
                
                empresa = "TecnoEmpleo"
                loc = "España"
                
                if contenedor:
                    # Buscar la empresa (suele ser un link con clase text-primary)
                    emp_tag = contenedor.find('a', class_='text-primary')
                    if emp_tag: empresa = emp_tag.text.strip()
                    
                    # Buscar ubicación (texto muted o span)
                    loc_tag = contenedor.find('span', class_='text-muted')
                    if loc_tag: loc = loc_tag.text.strip()
                
                ofertas.append({
                    "Titulo": titulo, 
                    "Empresa": empresa, 
                    "Ubicacion": loc, 
                    "Enlace": link, 
                    "Fuente": "TecnoEmpleo", 
                    "Etiquetas": "Tecnología"
                })
            except: continue
    except: pass
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
        df = df.drop_duplicates(subset=['Enlace'])
        return df
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    df = ejecutar_scraping_completo()
    df.to_csv('ofertas_discapacidad.csv', index=False)
    print(f"💾 Archivo actualizado con {len(df)} ofertas de 3 portales (Indeed, InfoEmpleo, TecnoEmpleo).")



