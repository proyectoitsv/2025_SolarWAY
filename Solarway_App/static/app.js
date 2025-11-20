// app.js
const socket = io();
let state = null;
let courts = {};
let LAYOUT = []; 

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Obtener estado inicial (CRÍTICO para obtener el LAYOUT y el estado)
    const resp = await fetch('/api/state');
    const j = await resp.json();
    
    if (j.ok) {
        state = j.state;
        courts = j.courts || {};
        LAYOUT = j.layout || [2, 8, 8, 2, 2]; // Aseguramos el layout de 22 LEDs
        
        renderBattery(state.battery);
        populateLeds(state.leds);
        populateCourts(courts, state.current_court);
        attachGlobalListeners();
    }

    // 2. SocketIO Listeners para actualizaciones en tiempo real
    socket.on('connect', () => console.log('Conectado a Socket.io'));
    
    socket.on('initial_state', s => {
        state = s;
        renderBattery(state.battery);
        populateLeds(state.leds);
        populateCourts(courts, state.current_court);
    });
    
    socket.on('battery_update', battery => {
        state.battery = battery;
        renderBattery(battery);
    });
    
    socket.on('led_update', leds => {
        state.leds = leds;
        updateLedStatuses(leds); // Actualiza los colores de los LEDs
    });
    
    socket.on('court_changed', d => {
        state.current_court = d.court;
        populateCourts(courts, state.current_court);
    });
    
    socket.on('alert', d => {
        const list = document.getElementById('alerts-list');
        const node = document.createElement('div');
        node.textContent = `[${new Date().toLocaleTimeString()}] ${d.message}`;
        list.prepend(node);
    });
});

// --- Funciones de Renderizado ---
function renderBattery(b) {
    const level = document.getElementById('battery-level');
    const text = document.getElementById('battery-text');
    const pct = Math.max(0, Math.min(100, Math.round(b.percent || 0)));
    
    level.style.width = pct + '%';
    text.textContent = `${pct}% (${(b.voltage||0).toFixed(2)}V) ${b.charging ? '⚡' : ''}`;
}

function populateLeds(leds) {
    const matrix = document.getElementById('led-matrix');
    matrix.innerHTML = '';
    
    const layoutCounts = LAYOUT; 
    
    // Mapear los conteos de LEDs a IDs secuenciales (1...22)
    let currentId = 1;
    const layoutMap = layoutCounts.map(count => {
        const row = [];
        for (let i = 0; i < count; i++) {
            row.push(String(currentId++));
        }
        return row;
    });

    const maxCols = Math.max(...layoutCounts); 
    matrix.style.gridTemplateColumns = `repeat(${maxCols}, auto)`;
    
    layoutMap.forEach(row => {
        const leadingPadding = (maxCols - row.length) / 2;
        
        // Espaciador izquierdo para centrar
        for (let i = 0; i < Math.floor(leadingPadding); i++) {
            const spacer = document.createElement('div');
            matrix.appendChild(spacer);
        }
        
        // LEDs
        row.forEach(id => {
            const led = document.createElement('div');
            led.className = `led ${leds[id] ? 'on' : 'off'}`;
            led.id = `led-${id}`;
            led.dataset.id = id;
            led.onclick = () => toggleLed(id, leds[id]);
            matrix.appendChild(led);
        });

        // Espaciador derecho para centrar
        for (let i = 0; i < Math.ceil(leadingPadding); i++) {
            const spacer = document.createElement('div');
            matrix.appendChild(spacer);
        }
    });
}

function updateLedStatuses(leds) {
    for (const [id, val] of Object.entries(leds)) {
        const ledElement = document.getElementById(`led-${id}`);
        if (ledElement) {
            ledElement.classList.toggle('on', val);
            ledElement.classList.toggle('off', !val);
        }
    }
}


function populateCourts(courtsMap, current) {
    const list = document.getElementById('court-list');
    list.innerHTML = '';
    
    for (const [id, info] of Object.entries(courtsMap)) {
        const card = document.createElement('div');
        card.className = 'court-card';
        if (id === current) {
            card.classList.add('selected');
        }
        
        // Asumiendo que las imágenes son horizontal.png, vertical.png, cross.png, etc.
        card.innerHTML = `<img src="${info.image}" alt="${info.name}" title="${info.name}">`;
        card.onclick = () => selectCourt(id);
        list.appendChild(card);
    }
}

// --- Funciones de Interacción con el Backend (Envío de Datos) ---

async function toggleLed(id, current_value) {
    const new_value = !current_value;
    await fetch('/api/set_led', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({led: id, value: new_value})
    });
}

async function selectCourt(id) {
    await fetch('/api/set_court', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({court: id})
    });
}

async function setAllLeds(value) {
    await fetch('/api/set_led', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({led: "ALL", value: value})
    });
}

function attachGlobalListeners() {
    document.getElementById('turn-all-on').onclick = () => setAllLeds(true);
    document.getElementById('turn-all-off').onclick = () => setAllLeds(false);
}