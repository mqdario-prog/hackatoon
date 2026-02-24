/* ==========================================================
   1. EJECUCIÓN INMEDIATA (Evita el parpadeo blanco)
   ========================================================== */
   (function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
})();

/* ==========================================================
   2. FUNCIONES DE ACCESIBILIDAD GLOBALES
   ========================================================== */

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Sincronizar el icono del botón
    const icon = document.getElementById('theme-icon');
    if (icon) icon.innerText = isDark ? '☀️' : '🌙';
}

let fontSize = 100;
function changeFontSize(amount) {
    fontSize += amount * 10;
    if (fontSize < 80) fontSize = 80;
    if (fontSize > 150) fontSize = 150;
    document.body.style.fontSize = fontSize + '%';
    localStorage.setItem('fontSize', fontSize);
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
    if (!type) return;
    if (type === 'grayscale') {
        html.style.filter = 'grayscale(100%)';
    } else {
        html.style.filter = `url(#${type})`;
    }
}

/* ==========================================================
   3. INICIALIZACIÓN CUANDO EL DOM ESTÁ LISTO
   ========================================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // A. Sincronizar UI de Accesibilidad
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.innerText = document.documentElement.classList.contains('dark') ? '☀️' : '🌙';
    }

    // B. Autocompletado de Provincias (Solo si existe el input)
    const inputUbi = document.getElementById('input-ubicacion');
    const listaProv = document.getElementById('lista-provincias');
    if (inputUbi && listaProv) {
        const provincias = [
            "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona", "Burgos", "Cáceres", 
            "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca", "Girona", "Granada", "Guadalajara", 
            "Guipúzcoa", "Huelva", "Huesca", "Islas Baleares", "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", 
            "Lleida", "Lugo", "Madrid", "Málaga", "Murcia", "Navarra", "Ourense", "Palencia", "Pontevedra", "Salamanca", 
            "Santa Cruz de Tenerife", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia", 
            "Valladolid", "Vizcaya", "Zamora", "Zaragoza", "Ceuta", "Melilla"
        ];

        inputUbi.addEventListener('keyup', function() {
            const texto = inputUbi.value.toLowerCase();
            listaProv.innerHTML = '';
            if (texto.length === 0) { listaProv.classList.add('hidden'); return; }

            const filtradas = provincias.filter(p => p.toLowerCase().startsWith(texto));
            if (filtradas.length > 0) {
                listaProv.classList.remove('hidden');
                filtradas.forEach(prov => {
                    const li = document.createElement('li');
                    li.className = "px-4 py-3 hover:bg-inclusion-blue/10 dark:hover:bg-slate-700 cursor-pointer text-gray-700 dark:text-gray-200 border-b dark:border-slate-700 last:border-0";
                    li.textContent = prov;
                    li.onclick = () => { inputUbi.value = prov; listaProv.classList.add('hidden'); };
                    listaProv.appendChild(li);
                });
            } else {
                listaProv.classList.add('hidden');
            }
        });
    }

    // C. Mapa de Ofertas (Blindado contra errores de carga)
    const mapDiv = document.getElementById('mapa-ofertas');
    if (mapDiv && typeof L !== 'undefined') {
        const map = L.map('mapa-ofertas').setView([40.416775, -3.703790], 6);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        }).addTo(map);

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
                marker.bindPopup(`
                    <div class="text-center">
                        <h4 class="font-bold text-gray-800">${m.ciudad}</h4>
                        <p class="text-sm text-blue-600 font-bold">${m.cantidad} ofertas</p>
                        <a href="/?ubicacion=${m.ciudad}" class="text-xs underline text-gray-500">Ver listado</a>
                    </div>
                `);
                markers.addLayer(marker);
            }
        });
        map.addLayer(markers);
        if (data.length > 0) map.fitBounds(markers.getBounds(), {padding: [50, 50]});
    }

    // D. Pantalla de Carga
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                overlay.classList.remove('hidden');
                overlay.classList.add('flex');
            });
        });
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
    
    // Mensaje Usuario
    chatBox.innerHTML += `<div class="flex justify-end"><div class="bg-inclusion-blue text-white rounded-lg p-3 shadow-sm max-w-[85%] text-sm font-medium">${msg}</div></div>`;
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Loading IA
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
        document.getElementById(loadId).remove();
        
        // Respuesta IA (Usamos innerHTML para las tarjetas de ofertas)
        chatBox.innerHTML += `<div class="flex justify-start"><div class="bg-white dark:bg-slate-800 border dark:border-slate-700 dark:text-gray-100 rounded-lg p-3 shadow-sm max-w-[95%] text-sm">${data.respuesta}</div></div>`;
    } catch (error) {
        document.getElementById(loadId).innerHTML = "Error de conexión.";
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* ==========================================================
   5. RECONOCIMIENTO Y LECTURA DE VOZ
   ========================================================== */

function toggleVoice() {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) { alert("Tu navegador no soporta reconocimiento de voz."); return; }
    
    const rec = new Speech();
    rec.lang = 'es-ES';
    rec.onstart = () => document.getElementById('mic-btn').classList.add('bg-red-500', 'text-white');
    rec.onend = () => document.getElementById('mic-btn').classList.remove('bg-red-500', 'text-white');
    
    rec.onresult = (e) => {
        const text = e.results[0][0].transcript;
        document.getElementById('user-input').value = text;
        enviarMensaje();
    };
    rec.start();
}

const synth = window.speechSynthesis;
function speak(text) {
    if (synth.speaking) synth.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'es-ES';
    utter.rate = 1.1;
    synth.speak(utter);
}

// Opcional: Leer elementos al enfocar con TAB
document.addEventListener('focusin', (e) => {
    if (document.body.classList.contains('voice-active')) {
        speak(e.target.innerText || e.target.ariaLabel || "");
    }
});