/* ==========================================================
   1. PERSISTENCIA TOTAL (Ejecución Inmediata)
   ========================================================== */
   (function() {
    // A. Modo Oscuro
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.classList.add('dark');
    }
    // B. Alto Contraste
    if (localStorage.getItem('high-contrast') === 'true') {
        document.documentElement.classList.add('high-contrast');
    }
    // C. Fuente Dislexia
    if (localStorage.getItem('dyslexia') === 'true') {
        document.documentElement.classList.add('dyslexia-font');
    }
    // D. Tamaño de Fuente
    const savedSize = localStorage.getItem('fontSize');
    if (savedSize) {
        document.documentElement.style.fontSize = savedSize + '%';
    }
    // E. Filtros de Color (Daltonismo)
    const savedFilter = localStorage.getItem('colorFilter');
    if (savedFilter && savedFilter !== 'none') {
        if (savedFilter === 'grayscale') {
            document.documentElement.style.filter = 'grayscale(100%)';
        } else {
            document.documentElement.style.filter = `url(#${savedFilter})`;
        }
    }
})();

/* ==========================================================
   2. FUNCIONES DE ACCESIBILIDAD GLOBALES (Con Guardado)
   ========================================================== */

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    const icon = document.getElementById('theme-icon');
    if (icon) icon.innerText = isDark ? '☀️' : '🌙';
}

function toggleContrast() {
    const isActive = document.documentElement.classList.toggle('high-contrast');
    localStorage.setItem('high-contrast', isActive);
}

function toggleDyslexia() {
    const isActive = document.documentElement.classList.toggle('dyslexia-font');
    localStorage.setItem('dyslexia', isActive);
}

function changeFontSize(amount) {
    let currentSize = parseInt(localStorage.getItem('fontSize')) || 100;
    currentSize += amount * 10;
    if (currentSize < 80) currentSize = 80;
    if (currentSize > 150) currentSize = 150;
    document.documentElement.style.fontSize = currentSize + '%';
    localStorage.setItem('fontSize', currentSize);
}

function applyColorFilter(type) {
    const html = document.documentElement;
    if (!type || type === "") {
        html.style.filter = 'none';
        localStorage.setItem('colorFilter', 'none');
    } else {
        const filterValue = type === 'grayscale' ? 'grayscale(100%)' : `url(#${type})`;
        html.style.filter = filterValue;
        localStorage.setItem('colorFilter', type);
    }
}

/* ==========================================================
   3. INICIALIZACIÓN (DOMContentLoaded)
   ========================================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- A. Sincronizar Icono de Tema ---
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.innerText = document.documentElement.classList.contains('dark') ? '☀️' : '🌙';
    }

    // --- B. Autocompletado de Provincias ---
    const inputUbi = document.getElementById('input-ubicacion');
    const listaProv = document.getElementById('lista-provincias');
    
    if (inputUbi && listaProv) {
        const provincias = ["Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Girona", "Granada", "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", "Islas Baleares", "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", "Lleida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra", "Ourense", "Palencia", "Pontevedra", "Salamanca", "Santa Cruz de Tenerife", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia", "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta", "Melilla"];

        inputUbi.addEventListener('keyup', function() {
            const texto = inputUbi.value.toLowerCase();
            listaProv.innerHTML = '';
            if (texto.length === 0) { listaProv.classList.add('hidden'); return; }

            const filtradas = provincias.filter(p => p.toLowerCase().startsWith(texto));
            if (filtradas.length > 0) {
                listaProv.classList.remove('hidden');
                filtradas.forEach(prov => {
                    const li = document.createElement('li');
                    li.className = "px-4 py-3 hover:bg-inclusion-blue/10 dark:hover:bg-slate-700 cursor-pointer text-gray-700 dark:text-gray-200 border-b dark:border-slate-700 last:border-0 transition-colors";
                    li.textContent = prov;
                    li.onclick = () => { inputUbi.value = prov; listaProv.classList.add('hidden'); };
                    listaProv.appendChild(li);
                });
            } else { listaProv.classList.add('hidden'); }
        });

        document.addEventListener('click', (e) => {
            if (!inputUbi.contains(e.target) && !listaProv.contains(e.target)) listaProv.classList.add('hidden');
        });
    }

    // --- C. Mapa de Ofertas (Leaflet) ---
    const mapDiv = document.getElementById('mapa-ofertas');
    if (mapDiv && typeof L !== 'undefined') {
        const map = L.map('mapa-ofertas').setView([40.416775, -3.703790], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OSM' }).addTo(map);

        const markers = L.markerClusterGroup({ showCoverageOnHover: false });
        const blueIcon = new L.Icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
        });

        const data = window.marcadores || [];
        data.forEach(m => {
            if (m.lat && m.lon) {
                const marker = L.marker([m.lat, m.lon], {icon: blueIcon});
                marker.bindPopup(`<div class="text-center"><h4 class="font-bold">${m.ciudad}</h4><p class="text-sm">${m.cantidad} ofertas</p><a href="/?ubicacion=${m.ciudad}" class="text-xs underline text-blue-600">Ver listado</a></div>`);
                markers.addLayer(marker);
            }
        });
        map.addLayer(markers);
        if (data.length > 0) map.fitBounds(markers.getBounds(), {padding: [50, 50]});
    }

    // --- D. Validación de Formularios ---
    const overlay = document.getElementById('loading-overlay');
    
    // Buscador Home
    const searchForm = document.querySelector('form[action="/"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const inputPuesto = document.querySelector('input[name="busqueda"]');
            const selectRadio = document.querySelector('select[name="radio"]');
            const errorDiv = document.getElementById('form-error');

            const radioValue = parseInt(selectRadio?.value || 0);
            const ubiValue = inputUbi ? inputUbi.value.trim() : "";
            const puestoValue = inputPuesto ? inputPuesto.value.trim() : "";

            if (puestoValue === "" && ubiValue === "") {
                e.preventDefault();
                mostrarError(errorDiv, inputUbi, "Escribe al menos un puesto o una ubicación.");
                return;
            }
            if (radioValue > 0 && ubiValue === "") {
                e.preventDefault();
                mostrarError(errorDiv, inputUbi, "⚠️ Indica una ciudad para buscar por cercanía.");
                inputUbi.focus();
                return;
            }
            if (overlay) overlay.classList.remove('hidden'), overlay.classList.add('flex');
        });
    }

    // Generador de CV
    const cvForm = document.querySelector('form[action="/generar-cv"]');
    if (cvForm) {
        cvForm.addEventListener('submit', function(e) {
            const errorDiv = document.getElementById('cv-error');
            const nombre = cvForm.querySelector('input[name="nombre"]').value.trim();
            const email = cvForm.querySelector('input[name="email"]').value.trim();
            const puesto = cvForm.querySelector('input[name="puesto_actual"]').value.trim();
            const empresa = cvForm.querySelector('input[name="empresa_actual"]').value.trim();

            let mensaje = "";
            if (nombre === "" || email === "" || puesto === "" || empresa === "") {
                mensaje = "❌ Por favor, rellena todos los campos obligatorios (*).";
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                mensaje = "❌ El formato del correo electrónico no es válido.";
            }

            if (mensaje !== "") {
                e.preventDefault();
                errorDiv.textContent = mensaje;
                errorDiv.classList.remove('hidden');
                errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                errorDiv.classList.add('hidden');
                const btn = cvForm.querySelector('button[type="submit"]');
                btn.innerHTML = "⌛ Procesando PDF...";
                btn.classList.add('opacity-50', 'cursor-not-allowed');
            }
        });
    }

    function mostrarError(div, input, mensaje) {
        if (!div) return;
        div.textContent = mensaje;
        div.classList.remove('hidden');
        if (input) input.classList.add('border-orange-500', 'ring-2');
        setTimeout(() => {
            div.classList.add('hidden');
            if (input) input.classList.remove('border-orange-500', 'ring-2');
        }, 4000);
    }
});

/* ==========================================================
   4. LOGICA DEL CHATBOT IA
   ========================================================== */

function toggleChat() {
    const win = document.getElementById('chat-window');
    if (win) win.classList.toggle('hidden');
}

function handleKeyPress(e) {
    if (e.key === 'Enter') enviarMensaje();
}

async function enviarMensaje() {
    const input = document.getElementById('user-input');
    const msg = input.value.trim();
    if (!msg) return;

    const chatBox = document.getElementById('chat-messages');
    chatBox.innerHTML += `<div class="flex justify-end"><div class="bg-inclusion-blue text-white rounded-lg p-3 shadow-sm max-w-[85%] text-sm font-medium">${msg}</div></div>`;
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    const loadId = 'loading-' + Date.now();
    chatBox.innerHTML += `<div id="${loadId}" class="flex justify-start"><div class="bg-gray-100 dark:bg-slate-700 p-3 rounded-lg text-xs italic">La IA está pensando...</div></div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: msg })
        });
        const data = await response.json();
        const loader = document.getElementById(loadId);
        if (loader) loader.remove();
        
        chatBox.innerHTML += `<div class="flex justify-start"><div class="bg-white dark:bg-slate-800 border dark:border-slate-700 dark:text-gray-100 rounded-lg p-3 shadow-sm max-w-[95%] text-sm">${data.respuesta}</div></div>`;
    } catch (error) {
        const loader = document.getElementById(loadId);
        if (loader) loader.innerHTML = "Error de conexión con la IA.";
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* ==========================================================
   5. RECONOCIMIENTO Y LECTURA DE VOZ
   ========================================================== */

let voiceEnabled = false;

// Esta función se activa con CUALQUIER interacción del usuario (tecla o clic)
function inicializarVozAutomatica() {
    if (voiceEnabled) return; // Evitar inicializar dos veces
    
    voiceEnabled = true;
    
    // Saludo inicial para que el usuario sepa que la web ya le escucha
    speak("Bienvenido a InclusivJob. El lector de voz se ha activado. Use la tecla Tabulador para explorar las ofertas y secciones.");
    
    // Eliminar los escuchadores para no saturar el sistema
    document.removeEventListener('keydown', inicializarVozAutomatica);
    document.removeEventListener('click', inicializarVozAutomatica);
}

// Escuchamos la primera interacción para desbloquear el audio del navegador
document.addEventListener('keydown', inicializarVozAutomatica);
document.addEventListener('click', inicializarVozAutomatica);

// Lógica de lectura al mover el FOCO con el TABULADOR
document.addEventListener('focusin', (e) => {
    if (!voiceEnabled) return;

    const target = e.target;
    let textToRead = "";

    // 1. Identificar el tipo de elemento para que el ciego se ubique
    let tipo = "";
    if (target.tagName === 'A') tipo = "Enlace a: ";
    if (target.tagName === 'BUTTON') tipo = "Botón de: ";
    if (target.tagName === 'INPUT') {
        tipo = "Campo de texto para " + (target.placeholder || "escribir") + ". ";
    }
    if (target.tagName === 'SELECT') tipo = "Menú desplegable. ";

    // 2. Prioridad de lectura: aria-label -> texto interno -> placeholder
    textToRead = target.ariaLabel || target.innerText || target.placeholder || target.title || "";

    if (textToRead.trim() !== "") {
        speak(tipo + textToRead);
    }
});

// Función central de síntesis de voz
function speak(text) {
    // Si ya está hablando, cortamos la frase anterior para no solapar
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }
    
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'es-ES';
    utter.rate = 1.1; // Un poco más rápido para usuarios expertos
    utter.pitch = 1.0;

    // Intentar usar una voz de calidad en español
    const voices = window.speechSynthesis.getVoices();
    const spanishVoice = voices.find(v => v.lang.includes('es-ES'));
    if (spanishVoice) utter.voice = spanishVoice;

    window.speechSynthesis.speak(utter);
}