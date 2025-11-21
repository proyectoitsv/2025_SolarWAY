# app.py
import eventlet
eventlet.monkey_patch() # Parchea las librerías estándar para el modo asíncrono

import asyncio
from bleak import BleakClient, BleakScanner 

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SolarWay_Secret_Key_2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# UUIDs de ESP32 BLE (DEBEN COINCIDIR CON EL CÓDIGO .ino)
LED_SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c2c68c12fbbd"
LED_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8" 

# Estado de la conexión BLE
ble_client = None
current_device_address = None

# LAYOUT: filas con número de LEDs por fila (total 22 leds)
LAYOUT = [2, 8, 8, 2, 2] 

# Generar IDs secuenciales 1..N
def generate_led_ids(layout):
    ids = []
    cur = 1
    for count in layout:
        row = []
        for _ in range(count):
            row.append(str(cur))
            cur += 1
        ids.append(row)
    return ids

LED_ROWS = generate_led_ids(LAYOUT)
ALL_LED_IDS = [id_ for row in LED_ROWS for id_ in row] # IDs de '1' a '22'

# Definición de los patrones 
PATTERNS = {
    "horizontal": {
        "name": "Líneas Centrales",
        "image": "/static/img/horizontal.png",
        "leds": ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'] 
    },
    "vertical": {
        "name": "Doble Línea Central",
        "image": "/static/img/vertical.png",
        "leds": ['1', '2', '6', '7', '14', '15', '19', '20', '21', '22'] 
    },
    "cross": {
        "name": "Patrón Cruz",
        "image": "/static/img/cross.png",
        "leds": ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'] + ['1', '2', '6', '7', '14', '15', '19', '20', '21', '22']
    }
}

# Estado inicial
initial_leds = {id_: False for id_ in ALL_LED_IDS}
for led_id in PATTERNS["horizontal"]["leds"]:
    initial_leds[led_id] = True

state = {
    "leds": initial_leds,
    "battery": {"voltage": 11.8, "percent": 87, "charging": False}, 
    "current_court": "horizontal", 
    "last_alerts": []
}

courts = PATTERNS 

# ====================================
# FUNCIÓN UTILITARIA: Ejecutar Tareas Async en un Hilo Separado (FIX)
# ====================================
def run_async_in_thread(func, *args):
    """Ejecuta una función asyncio.coroutine en un bucle separado para no bloquear Eventlet."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Se utiliza eventlet.spawn para no bloquear el bucle principal de Flask/SocketIO
    def run_coro():
        try:
            return loop.run_until_complete(func(*args))
        finally:
            loop.close()

    # Ejecuta en el hilo Eventlet y espera el resultado
    return eventlet.tpool.execute(run_coro)


# ====================================
# LÓGICA DE CONVERSIÓN Y COMANDO BLE
# ====================================

# Mapeo: ID Web (1-22) a Matriz ESP32 (Fila 0-10, Columna 0-1)
def map_id_to_matrix(led_id):
    """Convierte el ID secuencial (1-22) a coordenadas de matriz (fila, col)"""
    try:
        id_num = int(led_id)
        if 1 <= id_num <= 22:
            row = (id_num - 1) // 2
            col = (id_num - 1) % 2
            return row, col
    except ValueError:
        return None, None
    return None, None

# Envío del comando al ESP32
async def send_led_command(led_id, state):
    global ble_client
    if not ble_client or not ble_client.is_connected:
        return False
        
    row, col = map_id_to_matrix(led_id)
    if row is None:
        return False

    # Comando: F{Fila}C{Columna}S{Estado}\n (ej: F0C0S1\n)
    command = f"F{row}C{col}S{1 if state else 0}\n"
    
    try:
        await ble_client.write_gatt_char(
            LED_CHAR_UUID, 
            command.encode('utf-8'), 
            response=False
        )
        return True
    except Exception as e:
        # print(f"Error al enviar comando BLE: {e}")
        return False


# ====================================
# RUTAS DE LA APLICACIÓN
# ====================================

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/api/state', methods=['GET'])
def api_state():
    return jsonify({"ok": True, "state": state, "courts": courts, "layout": LAYOUT})

@app.route('/api/set_court', methods=['POST'])
def api_set_court():
    data = request.get_json(force=True)
    pattern_id = data.get('court')
    
    if pattern_id not in PATTERNS:
        return jsonify({"ok": False, "error": "invalid pattern"}), 400
    
    state['current_court'] = pattern_id
    
    # 1. Apagar todos los LEDs en la lógica (y enviar comandos)
    for led_id in state['leds']:
        state['leds'][led_id] = False
        run_async_in_thread(send_led_command, led_id, False)

    # 2. Encender los LEDs del nuevo patrón (y enviar comandos)
    leds_to_turn_on = PATTERNS[pattern_id]['leds']
    for led_id in leds_to_turn_on:
        if led_id in state['leds']:
            state['leds'][led_id] = True
            run_async_in_thread(send_led_command, led_id, True)
    
    socketio.emit('court_changed', {'court': pattern_id})
    socketio.emit('led_update', state['leds']) 
    
    return jsonify({"ok": True, "court": pattern_id, "leds": state['leds']})


@app.route('/api/set_led', methods=['POST'])
def api_set_led():
    data = request.get_json(force=True)
    led = data.get('led')
    value = data.get('value')
    
    if led == "ALL": 
        # Si son TODOS
        new_leds = {id_: bool(value) for id_ in ALL_LED_IDS}
        state['leds'].update(new_leds)
        
        for led_id in ALL_LED_IDS:
            run_async_in_thread(send_led_command, led_id, bool(value))
            
    elif led in state['leds']:
        # Si es un solo LED
        state['leds'][led] = bool(value)
        run_async_in_thread(send_led_command, led, bool(value))
        
    else:
        return jsonify({"ok": False, "error": "invalid led"}), 400
    
    socketio.emit('led_update', state['leds'])
    return jsonify({"ok": True, "leds": state['leds']})


# ====================================
# APIs para Gestión de Conexión BLE
# ====================================

# Función asíncrona para escanear
async def scan_devices_async():
    devices = await BleakScanner.discover(timeout=5.0) 
    return [{'name': d.name, 'address': d.address} for d in devices if d.name and "SolarWay" in d.name] 

@app.route('/api/scan_ble', methods=['GET'])
def api_scan_ble():
    # Ejecuta el escaneo en el hilo separado
    devices = run_async_in_thread(scan_devices_async)
    return jsonify({"ok": True, "devices": devices})


# Función asíncrona para conectar
async def connect_device_async(addr):
    global ble_client, current_device_address
    try:
        if ble_client and ble_client.is_connected:
            await ble_client.disconnect()
        
        new_client = BleakClient(addr)
        await new_client.connect()
        
        ble_client = new_client
        current_device_address = addr
        
        # Sincronizar el estado actual de los LEDs de la app al dispositivo
        for led_id, state_val in state['leds'].items():
            await send_led_command(led_id, state_val)
            
        return True, "Conectado exitosamente."
    except Exception as e:
        return False, f"Fallo la conexión: {e}"

@app.route('/api/connect_ble', methods=['POST'])
def api_connect_ble():
    data = request.get_json(force=True)
    address = data.get('address')
    
    # Ejecuta la conexión en el hilo separado
    success, message = run_async_in_thread(connect_device_async, address)
    
    if success:
        socketio.emit('ble_status', {'status': 'connected', 'address': address, 'message': message})
        return jsonify({"ok": True, "message": message, "address": address})
    else:
        socketio.emit('ble_status', {'status': 'disconnected', 'address': None, 'message': "Fallo al conectar"})
        return jsonify({"ok": False, "error": message}), 400

# ====================================
# SOCKET.IO EVENTOS
# ====================================
@socketio.on('connect')
def handle_connect():
    emit('initial_state', state)
    status = 'connected' if ble_client and ble_client.is_connected else 'disconnected'
    address = current_device_address if status == 'connected' else None
    emit('ble_status', {'status': status, 'address': address})


if __name__ == '__main__':
    # Usamos eventlet para el modo async.
    socketio.run(app, host='0.0.0.0', port=5000)