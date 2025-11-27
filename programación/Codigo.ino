#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ====================================
// 1. CONFIGURACIÓN DE LOS LEDS (2x11)
// ====================================

// Pines que controlan los transistores (filas/ánodos en tu configuración)
// Debes conectar estos pines a la base de tus transistores NPN.
const int rowPins[] = {13, 12, 14, 27, 26, 25, 33, 32, 5, 16, 17}; // R0 a R10
const int numRows = sizeof(rowPins) / sizeof(rowPins[0]);
const int NUM_ROWS = 11;

// Pines de las columnas (cátodos/alimentación)
// Debes conectar estos pines a la resistencia limitadora de corriente de cada columna.
const int colPins[] = {15, 2}; // C0 y C1
const int numCols = sizeof(colPins) / sizeof(colPins[0]);
const int NUM_COLS = 2;

// Almacena el estado de los 22 LEDs (true/false)
bool ledMatrix[NUM_ROWS][NUM_COLS] = {
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0},
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}
};

// Bandera para indicar si se necesita multiplexar (cuando hay 1 o más LEDs ON)
bool shouldMultiplex = false;


// ====================================
// 2. CONFIGURACIÓN DEL ADC (batería)
// ====================================
// Configuración para leer un divisor de tensión (simulación de batería)
const int ADC_PIN = 36;
const int ADC_RESOLUTION = 12;
#define ADC_ATTENUATION ADC_11db
const float VREF = 3.3;
const float DIVISOR_RATIO = 11.0; // Ajustar según el divisor de tensión real

// ====================================
// 3. CONFIGURACIÓN BLUETOOTH LOW ENERGY (BLE)
// ====================================

#define SERVICE_UUID        "4fa95e10-c1f3-4674-bc50-f80e03e541b1"
#define CHARACTERISTIC_UUID "4fa95e11-c1f3-4674-bc50-f80e03e541b1"
#define DEVICE_NAME         "ESP32-LED-Matrix"

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;

/**
 * @brief Fuerza todos los pines de control (filas y columnas) a LOW (0V).
 */
void setAllPinsLow() {
    for (int r = 0; r < numRows; r++) digitalWrite(rowPins[r], LOW);
    for (int c = 0; c < numCols; c++) digitalWrite(colPins[c], LOW);
}

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("Cliente BLE conectado.");
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("Cliente BLE desconectado. Reiniciando publicidad...");
      shouldMultiplex = false;
      setAllPinsLow(); // Asegura el apagado total
      BLEDevice::startAdvertising();
    }
};

class MyCharacteristicCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        const uint8_t* data = pCharacteristic->getData();
        size_t length = pCharacteristic->getLength();
        int activeLEDs = 0;

        if (length == 3) {
            
            // 1. Desempaquetar los 3 bytes y actualizar el estado de la matriz
            for (int i = 0; i < NUM_ROWS * NUM_COLS; i++) {
                int byteIndex = i / 8;
                int bitIndex = i % 8;
                int r = i / NUM_COLS;
                int c = i % NUM_COLS;

                bool state = (data[byteIndex] >> bitIndex) & 0x01;
                ledMatrix[r][c] = state;

                if (state) activeLEDs++;
            }
            
            setAllPinsLow(); // Apagamos todo antes de decidir el nuevo modo.

            // 2. LÓGICA DE CONTROL MODIFICADA: Ahora solo hay Matriz Apagada o Multiplexación.

            if (activeLEDs == 0) {
                // CERO LEDs: Se mantiene el estado de setAllPinsLow (0V en todos)
                shouldMultiplex = false;
                Serial.println("Modo: Matriz Apagada (todos los pines en 0V).");
            
            } else {
                // UNO o MÁS LEDs: OBLIGATORIO usar multiplexación.
                shouldMultiplex = true;
                Serial.printf("Modo: Multiplexación Dinámica. %d LEDs activos.\n", activeLEDs);
            }

        } else {
            Serial.printf("ADVERTENCIA: Se esperaba un payload de 3 bytes, se recibió %d.\n", length);
        }
    }
};

void initBLE() {
    Serial.println("Inicializando BLE...");
    BLEDevice::init(DEVICE_NAME);
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());
    BLEService *pService = pServer->createService(SERVICE_UUID);
    pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_WRITE
                    );
    pCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
    pService->start();
    BLEDevice::startAdvertising();
    Serial.println("Servidor BLE iniciado. Esperando conexión...");
}

// ====================================
// 4. FUNCIONES DE HARDWARE Y UTILIDAD
// ====================================

/**
 * @brief FUNCIÓN: Multiplexación (Scanning)
 * Itera rápidamente por las 11 filas para encender los LEDs activos.
 * Esto es necesario cuando hay 1 o más LEDs para evitar el ghosting.
 */
void updateLEDs() {
  if (!deviceConnected || !shouldMultiplex) {
      return;
  }
    
  // Duración del pulso HIGH: 50 microsegundos
  const int MUX_DELAY_US = 50;
    
  for (int r = 0; r < numRows; r++) {
    // 1. Activar fila actual (pulso HIGH)
    digitalWrite(rowPins[r], HIGH);

    // 2. Configurar columnas (pulso HIGH si el LED en esta posición está activo)
    for (int c = 0; c < numCols; c++) {
      // El pin de columna SÓLO se activa si el LED en [r][c] está activo.
      digitalWrite(colPins[c], ledMatrix[r][c] ? HIGH : LOW);
    }

    delayMicroseconds(MUX_DELAY_US); // Tiempo que el pulso está activo

    // 3. Apagar todo antes de pasar a la siguiente fila
    for (int c = 0; c < numCols; c++) digitalWrite(colPins[c], LOW);
    digitalWrite(rowPins[r], LOW);
  }
}

float readBatteryVoltage() {
  // Lectura del ADC
  int rawValue = analogRead(ADC_PIN);
  float voltage = (rawValue * VREF) / ((1 << ADC_RESOLUTION) - 1);
  voltage *= DIVISOR_RATIO;
  return voltage;
}

// ====================================
// 5. SETUP
// ====================================
void setup() {
  Serial.begin(115200);
  // Inicialización de pines como salida y en LOW
  for (int r = 0; r < numRows; r++) {
    pinMode(rowPins[r], OUTPUT);
    digitalWrite(rowPins[r], LOW);
  }
  for (int c = 0; c < numCols; c++) {
    pinMode(colPins[c], OUTPUT);
    digitalWrite(colPins[c], LOW);
  }
  // Configuración del ADC
  analogReadResolution(ADC_RESOLUTION);
  analogSetAttenuation(ADC_ATTENUATION);
  initBLE();
}

// ====================================
// 6. LOOP PRINCIPAL
// ====================================
void loop() {
  // Se ejecuta la multiplexación si hay 1 o más LEDs activos
  if (shouldMultiplex) {
    updateLEDs();
  }
    
  // Lectura de batería (cada 5 segundos)
  static unsigned long lastRead = 0;
  if (millis() - lastRead > 5000) {
    float battVoltage = readBatteryVoltage();
    // Aquí puedes agregar código para enviar el voltaje por BLE si lo necesitas.
    // Serial.print("Voltaje batería: ");
    // Serial.println(battVoltage);
    lastRead = millis();
  }
}