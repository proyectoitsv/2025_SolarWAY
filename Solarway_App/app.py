from flask import Flask, render_template, jsonify, request
import serial

app = Flask(__name__)

# Conexión con el ESP32 (ajustá el puerto)
# En Windows suele ser COM3 o COM4
try:
    esp32 = serial.Serial('COM3', 115200, timeout=1)
except:
    esp32 = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    comando = data.get("accion")

    if esp32:
        esp32.write(comando.encode())

    return jsonify({"status": "ok", "accion": comando})

@app.route('/api/estado')
def estado():
    # Ejemplo: podrías recibir datos de energía o fallas
    estado_sistema = {
        "energia": "Alta",
        "modo": "Handball",
        "fallas": "Ninguna"
    }
    return jsonify(estado_sistema)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)