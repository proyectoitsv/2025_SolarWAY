import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Estado inicial de LEDs (5 filas)
LED_MATRIX = [
    [0, 0],                      
    [0]*8,
    [0]*8,
    [0]*8,
    [0, 0]
]

@app.route("/")
def index():
    return render_template("index.html", matrix=LED_MATRIX)

@socketio.on("toggle_led")
def toggle_led(data):
    row = data["row"]
    col = data["col"]
    LED_MATRIX[row][col] ^= 1
    emit("update_matrix", LED_MATRIX, broadcast=True)

@socketio.on("set_all")
def set_all(state):
    for r in range(len(LED_MATRIX)):
        for c in range(len(LED_MATRIX[r])):
            LED_MATRIX[r][c] = state
    emit("update_matrix", LED_MATRIX, broadcast=True)

@socketio.on("select_cancha")
def select_cancha(cancha):
    emit("cancha_selected", cancha, broadcast=True)

if __name__ == "__main__":
    print("🌍 Servidor Solarway iniciado en http://0.0.0.0:5000")
    socketio.run(app, host="0.0.0.0", port=5000)
