/* ===================================
   JAVASCRIPT - InclusivJob
   =================================== */

// ===================================
// 1. AUTOCOMPLETADO DE PROVINCIAS
// ===================================

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('input-ubicacion');
    const lista = document.getElementById('lista-provincias');
    
    // Lista completa de provincias
    const provincias = [
        "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", 
        "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Girona", "Granada", "Guadalajara", 
        "Guipúzcoa", "Huelva", "Huesca", "Islas Baleares", "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", 
        "Lleida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra", "Ourense", "Palencia", "Pontevedra", "Salamanca", 
        "Santa Cruz de Tenerife", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia", 
        "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta", "Melilla"
    ];

    // Función al escribir
    input.addEventListener('keyup', function() {
        const texto = input.value.toLowerCase();
        lista.innerHTML = ''; // Limpiar lista
        
        if (texto.length === 0) {
            lista.classList.add('hidden');
            return;
        }

        // Filtrar: Solo las que EMPIEZAN por lo escrito
        const filtradas = provincias.filter(p => p.toLowerCase().startsWith(texto));

        if (filtradas.length > 0) {
            lista.classList.remove('hidden');
            filtradas.forEach(prov => {
                const li = document.createElement('li');
                li.className = "px-4 py-3 hover:bg-blue-50 cursor-pointer text-gray-700 border-b border-gray-100 last:border-0 transition-colors";
                li.textContent = prov;
                
                // Al hacer clic, rellenar y cerrar
                li.onclick = function() {
                    input.value = prov;
                    lista.classList.add('hidden');
                };
                
                lista.appendChild(li);
            });
        } else {
            lista.classList.add('hidden');
        }
    });

    // Cerrar si clic fuera
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !lista.contains(e.target)) {
            lista.classList.add('hidden');
        }
    });
});


// ===================================
// 2. MODO OSCURO
// ===================================

function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    document.getElementById('theme-icon').innerText = isDark ? '☀️' : '🌙';
}


// ===================================
// 3. ACCESIBILIDAD
// ===================================

let fontSize = 100;

function changeFontSize(amount) {
    fontSize += amount * 10;
    if (fontSize < 80) fontSize = 80;
    if (fontSize > 150) fontSize = 150;
    document.body.style.fontSize = fontSize + '%';
}

function toggleDyslexia() {
    document.body.classList.toggle('dyslexia-font');
}

function toggleContrast() {
    document.body.classList.toggle('high-contrast');
}

function applyColorFilter(type) {
    const html = document.documentElement;
    html.style.filter = 'none';
    if (type === 'protanopia') html.style.filter = 'url(#protanopia)';
    else if (type === 'deuteranopia') html.style.filter = 'url(#deuteranopia)';
    else if (type === 'tritanopia') html.style.filter = 'url(#tritanopia)';
    else if (type === 'grayscale') html.style.filter = 'grayscale(100%)';
}


// ===================================
// 4. CHATBOT
// ===================================

function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    const chatBtn = document.getElementById('chat-btn');
    const isHidden = chatWindow.classList.contains('hidden');
    
    if (isHidden) {
        chatWindow.classList.remove('hidden');
        chatWindow.setAttribute('aria-hidden', 'false');
        chatBtn.setAttribute('aria-expanded', 'true');
        setTimeout(() => document.getElementById('user-input').focus(), 100);
    } else {
        chatWindow.classList.add('hidden');
        chatWindow.setAttribute('aria-hidden', 'true');
        chatBtn.setAttribute('aria-expanded', 'false');
        chatBtn.focus();
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') enviarMensaje();
}

async function enviarMensaje() {
    const input = document.getElementById('user-input');
    const mensaje = input.value.trim();
    if (!mensaje) return;

    const chatBox = document.getElementById('chat-messages');
    
    // Mensaje del Usuario
    const msgUser = document.createElement('div');
    msgUser.className = "flex justify-end";
    msgUser.innerHTML = `<div class="bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 rounded-lg p-3 shadow-sm max-w-[90%] text-sm font-medium">${mensaje}</div>`;
    chatBox.appendChild(msgUser);
    
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Indicador de carga
    const loadingId = 'loading-' + Date.now();
    const msgLoading = document.createElement('div');
    msgLoading.id = loadingId;
    msgLoading.className = "flex justify-start text-xs text-gray-500 dark:text-gray-400 p-2 italic";
    msgLoading.innerText = "Pensando...";
    chatBox.appendChild(msgLoading);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: mensaje })
        });
        const data = await response.json();
        document.getElementById(loadingId).remove();
        
        // Mensaje del Bot
        const msgBot = document.createElement('div');
        msgBot.className = "flex justify-start";
        msgBot.innerHTML = `<div class="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 text-gray-800 dark:text-gray-200 rounded-lg p-3 shadow-sm max-w-[90%] text-sm">${data.respuesta}</div>`;
        chatBox.appendChild(msgBot);

        box.innerHTML += `<div class="flex justify-start"><span class="bg-white p-2 rounded-lg border">${data.respuesta}</span></div>`;
        
        // Opcional: Leer respuesta automáticamente
        // speak(data.respuesta.replace(/<[^>]*>/g, ''));
    } catch (error) {
        document.getElementById(loadingId).innerText = "Error.";
    }
    
    chatBox.scrollTop = chatBox.scrollHeight;
}


// ===================================
// 5. DICTADO POR VOZ (Speech-to-Text)
// ===================================

let recognition;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        document.getElementById('listening-indicator').classList.remove('hidden');
        document.getElementById('mic-btn').classList.add('bg-red-100', 'text-red-600');
    };

    recognition.onend = function() {
        document.getElementById('listening-indicator').classList.add('hidden');
        document.getElementById('mic-btn').classList.remove('bg-red-100', 'text-red-600');
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user-input').value = transcript;
        
        // Enviar automáticamente
        enviarMensaje();
    };
} else {
    const micBtn = document.getElementById('mic-btn');
    if (micBtn) micBtn.style.display = 'none';
}

function toggleVoice() {
    if (recognition) {
        try {
            recognition.start();
        } catch (e) {
            recognition.stop();
        }
    } else {
        alert("Navegador no compatible con voz.");
    }
}


// ===================================
// 6. LECTURA POR VOZ (Text-to-Speech)
// ===================================

const synth = window.speechSynthesis;
let voices = [];

function loadVoices() {
    voices = synth.getVoices();
}

if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = loadVoices;
}
loadVoices();

function speak(text) {
    if (synth.speaking) synth.cancel();
    const utterThis = new SpeechSynthesisUtterance(text);
    const spanishVoice = voices.find(voice => voice.lang.includes('es'));
    if (spanishVoice) utterThis.voice = spanishVoice;
    utterThis.rate = 1.1;
    synth.speak(utterThis);
}

// Leer al hacer foco en elementos (opcional)
document.addEventListener('focusin', (e) => {
    const target = e.target;
    let textToRead = "";
    
    if (target.getAttribute('aria-label')) {
        textToRead = target.getAttribute('aria-label');
    } else if (target.tagName === 'IMG' && target.alt) {
        textToRead = "Imagen: " + target.alt;
    } else if (target.innerText) {
        textToRead = target.innerText;
    }
    
    if (target.tagName === 'A') textToRead += ", enlace";
    if (target.tagName === 'BUTTON') textToRead += ", botón";

    if (textToRead) speak(textToRead);
});


// ===================================
// 7. PANTALLA DE CARGA
// ===================================

document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
            overlay.classList.add('flex');
        }
    });
});

window.addEventListener('pageshow', function() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
        overlay.classList.remove('flex');
    }
});


// ===================================
// 8. MAPA DE OFERTAS (Leaflet)
// ===================================

// Esta función se ejecutará cuando el DOM esté listo
function initMap() {
    const mapElement = document.getElementById('mapa-ofertas');
    if (!mapElement) {
        console.log('Elemento mapa no encontrado');
        return;
    }
    
    // Inicializar mapa
    const map = L.map('mapa-ofertas').setView([40.416775, -3.703790], 6);

    // Capa base (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Crear grupo de clusters
    const markers = L.markerClusterGroup({
        showCoverageOnHover: false,
        disableClusteringAtZoom: 17
    });

    // Icono personalizado
    const blueIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    // Obtener datos del servidor (variables renderizadas por Jinja2)
    // NOTA: Esta parte requiere que el backend pase la variable 'marcadores'
    const marcadores = typeof window.marcadores !== 'undefined' ? window.marcadores : [];
    console.log("Datos del mapa:", marcadores);

    if (marcadores && marcadores.length > 0) {
        marcadores.forEach(function(m) {
            if (m.lat && m.lon) {
                const marker = L.marker([m.lat, m.lon], {icon: blueIcon});
                
                marker.bindPopup(`
                    <div class="text-center">
                        <h4 class="font-bold text-gray-800">${m.ciudad}</h4>
                        <p class="text-sm text-blue-600 font-bold">${m.cantidad} ofertas</p>
                        <a href="/?ubicacion=${m.ciudad}" class="text-xs underline text-gray-500 hover:text-blue-500">Ver listado</a>
                    </div>
                `);

                markers.addLayer(marker);
            }
        });

        // Añadir grupo al mapa
        map.addLayer(markers);

        // Ajustar zoom para ver todos los puntos
        map.fitBounds(markers.getBounds(), {padding: [50, 50]});
    }
    
    // Forzar actualización del tamaño del mapa
    setTimeout(function() {
        map.invalidateSize();
    }, 100);
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMap);
} else {
    initMap();
}