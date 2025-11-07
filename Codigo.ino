#include <Arduino.h>

// ====================================
// CONFIGURACIÓN DE LOS LEDS (2x11)
// ====================================

// Pines que controlan los transistores (conectan LEDs a GND)
const int rowPins[] = {13, 12, 14, 27, 26, 25, 33, 32, 5, 16, 17};  // fila1 → fila11
const int numRows = sizeof(rowPins) / sizeof(rowPins[0]);

// Pines de las columnas (que dan 3.3V a los LEDs)
const int colPins[] = {15, 2};  // C1 y C2
const int numCols = sizeof(colPins) / sizeof(colPins[0]);

// Matriz lógica de LEDs (2 columnas × 11 filas = 22 LEDs)
bool ledMatrix[11][2] = {
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1},
  {1, 1}
  
};

// ====================================
// CONFIGURACIÓN DEL ADC (batería)
// ====================================

const int ADC_PIN = 36;       // Pin donde llega el divisor resistivo
const int ADC_RESOLUTION = 12;
#define ADC_ATTENUATION ADC_11db
const float VREF = 3.3;
const float DIVISOR_RATIO = 11.0;

// ====================================
// SETUP
// ====================================
void setup() {
  Serial.begin(115200);
  Serial.println("Sistema iniciado: Matriz 2x11 + Lectura batería");

  // Configurar filas (transistores)
  for (int r = 0; r < numRows; r++) {
    pinMode(rowPins[r], OUTPUT);
    digitalWrite(rowPins[r], LOW);
  }

  // Configurar columnas (alimentación LED)
  for (int c = 0; c < numCols; c++) {
    pinMode(colPins[c], OUTPUT);
    digitalWrite(colPins[c], LOW);
  }

  // Configurar ADC
 analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_ATTENUATION);
}

// ====================================
// FUNCIÓN: Multiplexación LEDs
// ====================================
void updateLEDs() {
  for (int r = 0; r < numRows; r++) {
    // Activar fila actual → transistor a GND
    digitalWrite(rowPins[r], HIGH);

    // Configurar columnas (3.3V para cada LED activo)
    for (int c = 0; c < numCols; c++) {
      digitalWrite(colPins[c], ledMatrix[r][c] ? HIGH : LOW);
    }

    delay(1000);  // Persistencia visual

    // Apagar todo antes de pasar a la siguiente fila
    for (int c = 0; c < numCols; c++) digitalWrite(colPins[c], LOW);
    digitalWrite(rowPins[r], LOW);
  }
}

// ====================================
// FUNCIÓN: Leer voltaje batería
// ====================================
float readBatteryVoltage() {
  int rawValue = analogRead(ADC_PIN);
  float voltage = (rawValue * VREF) / ((1 << ADC_RESOLUTION) - 1);
  voltage *= DIVISOR_RATIO;
  return voltage;
}

// ====================================
// FUNCIÓN: Encender/apagar LED específico
// ====================================
// fila (0–10), col (0–1)
void setLED(int row, int col, bool state) {
  if (row >= 0 && row < numRows && col >= 0 && col < numCols) {
    ledMatrix[row][col] = state;
  }
}

// ====================================
// LOOP PRINCIPAL
// ====================================
void loop() {
  // Actualiza LEDs (multiplexación)
  updateLEDs();

  // Lee voltaje batería cada 1 segundo
  static unsigned long lastRead = 0;
  if (millis() - lastRead > 1000) {
    float battVoltage = readBatteryVoltage();
    Serial.print("Voltaje batería: ");
    Serial.print(battVoltage);
    Serial.println(" V");
    lastRead = millis();
  }
}