# app.py
import eventlet
eventlet.monkey_patch()
import threading # <- Estas y las siguientes líneas deben ir después
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambia_esto_en_produccion'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# LAYOUT: filas con número de LEDs por fila (el layout de tu imagen)
# Fila 1: 1, 2
# Fila 2: 3, 4, 5, 6, 7, 8, 9, 10
# Fila 3: 11, 12, 13, 14, 15, 16, 17, 18
# Fila 4: 19, 20, 21, 22, 23, 24, 25, 26
# Fila 5: 27, 28
LAYOUT = [2, 8, 8, 8, 2]  # total 28 leds

# Generar IDs secuenciales 1..N según LAYOUT
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
ALL_LED_IDS = [id_ for row in LED_ROWS for id_ in row]


# Definición de los patrones y los LEDs que deben encender
PATTERNS = {
    "horizontal": {
        "name": "2 Líneas Horizontales",
        "image": "/static/img/horizontal.png",
        # LEDs de las dos filas centrales (Fila 2 y Fila 3)
        "leds": ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'] 
    },
    "vertical": {
        "name": "2 Líneas Verticales",
        "image": "/static/img/vertical.png",
        # IDs que forman dos columnas verticales (posiciones 4 y 5 de las filas de 8 LEDs, más los extremos)
        "leds": ['1', '2', '6', '7', '14', '15', '22', '23', '27', '28']
    },
    "cross": {
        "name": "Patrón Cruz",
        "image": "/static/img/cross.png",
        # LEDs de las dos filas centrales (horizontal) más los LEDs de la columna central (vertical)
        "leds": ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'] + ['1', '2', '6', '7', '14', '15', '22', '23', '27', '28']
    }
}

# Estado inicial
state = {
    "leds": {id_: False for id_ in ALL_LED_IDS},
    "battery": {"voltage": 0.0, "percent": 0, "charging": False},
    "current_court": "horizontal", # Patrón inicial
    "last_alerts": []
}

courts = PATTERNS # Usamos PATTERNS para el front

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para que el ESP32 reporte estado (POST JSON)
@app.route('/api/report', methods=['POST'])
def api_report():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"ok": False, "error": "no json"}), 400

    if 'leds' in data and isinstance(data['leds'], dict):
        state['leds'].update(data['leds'])
        socketio.emit('led_update', state['leds'])

    if 'battery' in data and isinstance(data['battery'], dict):
        state['battery'].update(data['battery'])
        socketio.emit('battery_update', state['battery'])

    if 'alert' in data:
        state['last_alert'] = data['alert']
        socketio.emit('alert', {'message': data['alert']})

    return jsonify({"ok": True}), 200

# Endpoint para obtener estado actual
@app.route('/api/state', methods=['GET'])
def api_state():
    return jsonify({"ok": True, "state": state, "courts": courts})

# Endpoint para cambiar patrón (desde frontend)
@app.route('/api/set_court', methods=['POST'])
def api_set_court():
    data = request.get_json(force=True)
    pattern_id = data.get('court')
    
    if pattern_id not in PATTERNS:
        return jsonify({"ok": False, "error": "invalid pattern"}), 400
    
    state['current_court'] = pattern_id
    
    # 1. Apagar todos los LEDs
    for led_id in state['leds']:
        state['leds'][led_id] = False
        
    # 2. Encender los LEDs del patrón seleccionado
    leds_to_turn_on = PATTERNS[pattern_id]['leds']
    for led_id in leds_to_turn_on:
        if led_id in state['leds']:
            state['leds'][led_id] = True
    
    # Notificar al frontend del cambio de patrón y del nuevo estado de los LEDs
    socketio.emit('court_changed', {'court': pattern_id})
    socketio.emit('led_update', state['leds']) # Enviar el nuevo estado de los LEDs
    
    return jsonify({"ok": True, "court": pattern_id, "leds": state['leds']})


# Endpoint para encender/apagar LEDs desde frontend / app (opcional)
@app.route('/api/set_led', methods=['POST'])
def api_set_led():
    data = request.get_json(force=True)
    led = data.get('led')
    value = data.get('value')
    if led not in state['leds']:
        return jsonify({"ok": False, "error": "invalid led"}), 400
    state['leds'][led] = bool(value)
    # Emitimos evento para front
    socketio.emit('led_update', state['leds'])
    return jsonify({"ok": True, "leds": state['leds']})

# SocketIO connect
@socketio.on('connect')
def handle_connect():
    emit('initial_state', state)

if __name__ == '__main__':
    # Para dev: python app.py y después abrir http://localhost:5000
    socketio.run(app, host='0.0.0.0', port=5000)