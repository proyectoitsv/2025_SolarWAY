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
        LAYOUT = j.layout || [2, 8, 8, 2, 2]; 
        
        renderBattery(state.battery);
        populateLeds(state.leds);
        populateCourts(courts, state.current_court);
        attachGlobalListeners();
        attachBleListeners(); // NUEVO: Listeners para BLE
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
        updateLedStatuses(leds); 
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

    // NUEVO: Listener de estado de conexión BLE
    socket.on('ble_status', d => {
        const statusText = document.getElementById('current-status');
        const bleBtn = document.getElementById('connect-ble-btn');

        if (d.status === 'connected') {
            statusText.textContent = `Estado: CONECTADO (${d.address})`;
            bleBtn.textContent = '✅ Conectado';
            bleBtn.style.backgroundColor = 'var(--verde)';
            bleModal.style.display = 'none'; // Cerrar modal al conectar
        } else {
            statusText.textContent = `Estado: Desconectado`;
            bleBtn.textContent = '🔗 Conectar';
            bleBtn.style.backgroundColor = 'var(--azul)';
        }
    });
});

// --- Funciones de Renderizado ---

function renderBattery(b) {
    const level = document.getElementById('battery-level');
    const text = document.getElementById('battery-text');
    
    const V_MAX = 12.0; 
    const V_MIN = 10.5; 
    const voltage = b.voltage || 0;
    
    let calculatedPercent = ((voltage - V_MIN) / (V_MAX - V_MIN)) * 100;
    
    const finalPct = Math.max(0, Math.min(100, Math.round(calculatedPercent)));
    
    level.style.width = finalPct + '%';
    text.textContent = `${finalPct}% (${voltage.toFixed(2)}V) ${b.charging ? '⚡' : ''}`;
}


function populateLeds(leds) {
    const matrix = document.getElementById('led-matrix');
    matrix.innerHTML = '';
    
    const layoutCounts = LAYOUT; 
    
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
            led.onclick = () => toggleLed(id); 
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
        
        card.innerHTML = `<img src="${info.image}" alt="${info.name}" title="${info.name}">`;
        card.onclick = () => selectCourt(id);
        list.appendChild(card);
    }
}

// --- Funciones de Interacción con el Backend (Envío de Datos) ---

async function toggleLed(id) { 
    const current_value = state.leds[id]; 
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

// --- Funciones para la Conexión BLE (NUEVO) ---

const bleModal = document.getElementById('ble-modal');
const bleBtn = document.getElementById('connect-ble-btn');
const closeBtn = document.querySelector('.close-btn');
const scanBtn = document.getElementById('scan-btn');
const deviceList = document.getElementById('device-list');
// statusText se actualiza via SocketIO

function attachBleListeners() {
    // Abrir/Cerrar Modal
    bleBtn.onclick = () => bleModal.style.display = 'block';
    closeBtn.onclick = () => bleModal.style.display = 'none';
    window.onclick = (event) => {
        if (event.target == bleModal) {
            bleModal.style.display = 'none';
        }
    };
    
    // Iniciar escaneo
    scanBtn.onclick = scanDevices;
}

// Función para buscar dispositivos
async function scanDevices() {
    scanBtn.disabled = true;
    scanBtn.textContent = 'Escaneando...';
    deviceList.innerHTML = '<p style="color: var(--azul);">Buscando dispositivos cercanos...</p>';
    
    const resp = await fetch('/api/scan_ble');
    const j = await resp.json();

    scanBtn.disabled = false;
    scanBtn.textContent = 'Buscar Dispositivos';
    deviceList.innerHTML = '';
    
    if (j.ok && j.devices.length > 0) {
        j.devices.forEach(device => {
            const item = document.createElement('div');
            item.className = 'device-item';
            
            // Mostrar solo la parte principal del nombre, si existe
            const name = device.name.replace('SolarWay', 'SW'); 

            item.innerHTML = `<span>${name}</span><button class="btn" data-address="${device.address}">Conectar</button>`;
            
            item.querySelector('button').onclick = () => connectDevice(device.address);
            deviceList.appendChild(item);
        });
    } else {
        deviceList.innerHTML = '<p style="color: red;">No se encontraron dispositivos "SolarWay". Asegúrate que el ESP32 esté encendido.</p>';
    }
}

// Función para conectar a un dispositivo
async function connectDevice(address) {
    const statusText = document.getElementById('current-status');
    statusText.textContent = 'Estado: Intentando conectar...';
    deviceList.innerHTML = `<p style="color: var(--azul);">Conectando a ${address}...</p>`;
    
    const resp = await fetch('/api/connect_ble', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({address: address})
    });
    
    const j = await resp.json();
    
    if (!j.ok) {
        // El estado final se actualizará via SocketIO, pero mostramos el error inmediato
        alert(`Fallo la conexión: ${j.error}`);
        statusText.textContent = `Estado: Fallo la conexión.`;
        scanDevices(); // Volver a escanear
    }
}