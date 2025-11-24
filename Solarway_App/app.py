# app.py
import eventlet
eventlet.monkey_patch()
import threading

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SolarWay_Secret_Key_2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# LAYOUT: filas con número de LEDs por fila (total 22 leds: 2 + 8 + 8 + 2 + 2)
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


# Definición de los patrones (Patrones para 22 LEDs)
PATTERNS = {
    "horizontal": {
        "name": "Líneas Centrales",
        "image": "/static/img/horizontal.png",
        # IDs 3 a 18 (Filas 2 y 3)
        "leds": ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'] 
    },
    "vertical": {
        "name": "Doble Línea Central",
        "image": "/static/img/vertical.png",
        # RE-CORRECCIÓN: IDs que forman el tronco central de la cruz (10 LEDs)
        "leds": ['1', '2', '6', '7', '14', '15', '19', '20', '21', '22'] 
    },
    "cross": {
        "name": "Patrón Cruz",
        "image": "/static/img/cross.png",
        # Combinar el patrón horizontal y el nuevo patrón vertical
        "leds": ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'] + ['1', '2', '6', '7', '14', '15', '19', '20', '21', '22']
    }
}

# Estado inicial
initial_leds = {id_: False for id_ in ALL_LED_IDS}
for led_id in PATTERNS["horizontal"]["leds"]:
    initial_leds[led_id] = True

state = {
    "leds": initial_leds,
    # Corrección de batería (11.8V)
    "battery": {"voltage": 11.8, "percent": 87, "charging": False}, 
    "current_court": "horizontal", 
    "last_alerts": []
}

courts = PATTERNS 

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
    
    for led_id in state['leds']:
        state['leds'][led_id] = False
    leds_to_turn_on = PATTERNS[pattern_id]['leds']
    for led_id in leds_to_turn_on:
        if led_id in state['leds']:
            state['leds'][led_id] = True
    
    socketio.emit('court_changed', {'court': pattern_id})
    socketio.emit('led_update', state['leds']) 
    
    return jsonify({"ok": True, "court": pattern_id, "leds": state['leds']})


@app.route('/api/set_led', methods=['POST'])
def api_set_led():
    data = request.get_json(force=True)
    led = data.get('led')
    value = data.get('value')
    
    if led == "ALL": 
        new_leds = {id_: bool(value) for id_ in ALL_LED_IDS}
        state['leds'].update(new_leds)
    elif led in state['leds']:
        state['leds'][led] = bool(value)
    else:
        return jsonify({"ok": False, "error": "invalid led"}), 400
    
    socketio.emit('led_update', state['leds'])
    return jsonify({"ok": True, "leds": state['leds']})

@socketio.on('connect')
def handle_connect():
    emit('initial_state', state)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)