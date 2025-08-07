# 2025_SolarWAY
# ⚡ SolarWay — Proyecto de Electrónica Digital IV

> 📅 Entrega: 31/07/2025  
> 👨‍🔧 Curso: 7°B — Electrónica Digital IV  
> 🧑‍💻 Alumnos: Massimo Sahonero, Agustín Paz, Santino Fulgenzi  
> 👨‍🏫 Profesores: Federico Ferraro, Matías Schulthess, Marco Remedi, Juan Cruz Becerra

---

## 🟢 Resumen Ejecutivo

**SolarWay** es un sistema modular que reemplaza el piso de las canchas escolares por paneles solares resistentes. Estos generan energía para alimentar luces LED usadas en señalización deportiva (handball, vóley, básquet), y si sobra energía, se destina a otros sectores del colegio.

Los módulos:
- Se activan automáticamente en recreos y clases.
- Se configuran desde una app conectada a un **ESP32**.
- Notifican fallas del sistema.
- Permiten elegir el tipo de cancha desde la app.

---

## 🎯 Objetivos del Proyecto

### Objetivo general:
Diseñar una cancha modular con iluminación deportiva alimentada por energía solar, controlada mediante un sistema embebido.

### Objetivos específicos:
- Diseñar módulos con paneles solares integrables al piso.
- Controlar patrones LED con un ESP32 y una app.
- Conectividad por Bluetooth o Wi-Fi.
- Optimización energética por horario.
- Detección y notificación de fallos.

---

## ⚙️ Especificaciones del Sistema

### Requerimientos funcionales:
- Encendido de luces LED según el deporte seleccionado.
- Comunicación inalámbrica entre app y ESP32.
- Activación automática por horarios predefinidos.
- Notificación de errores del sistema.

### Requerimientos no funcionales:
- Interfaz intuitiva de la app.
- Consumo energético eficiente.
- Alta resistencia mecánica del piso.

### Restricciones:
- Presupuesto limitado.
- Variabilidad climática.
- No interferir con otras actividades escolares.

---

## 🔩 Diseño de Hardware

### Componentes principales:
| Componente     | Justificación                           |
|----------------|------------------------------------------|
| ESP32          | Bajo consumo, Wi-Fi + Bluetooth          |
| Panel solar    | Fuente energética limpia                 |
| LEDs           | Iluminación versátil                     |
| Transistores NPN | Multiplexación eficiente de LEDs     |
| PCB matriz 8x5 | Organización modular del sistema         |

### Consumo estimado:
- Consumo por LED: ~20 mA  
- Tensión general: 5V  
- GPIO ESP32: 3.3V (usa transistores para manejar LEDs de 5V)  
- Consumo pico: ~800 mA

---

## 🧠 Diseño de Firmware / Software Embebido

### Arquitectura modular:
- Módulos: **Comunicación**, **Control**, **Iluminación**, **Gestión de errores**

### Tecnologías usadas:
- **Lenguaje:** C/C++ con Arduino IDE
- **Librerías:** FastLED o Adafruit NeoPixel

### Funcionalidades clave:
- Inicializar Bluetooth/Wi-Fi
- Recibir comandos desde la app
- Encender patrones LED según el deporte
- Monitorear sensores (opcional)
- Validar datos y cortar corriente en caso de sobrecorriente

### Periféricos utilizados:
- GPIO, UART/Bluetooth, transistores, resistencias de shunt

---

## 📡 Comunicación y Conectividad

- **Protocolo principal:** Bluetooth clásico (SerialBT)
- **Opcional:** Conectividad Wi-Fi para expansión futura
- **Formato de datos:** JSON o tramas simples (`"MODO:HANDBALL"`)
- **Flujo de datos:**
  - App → ESP32: comandos de control
  - ESP32 → App: estados y errores

---

## 🧪 Pruebas y Validación

### Metodología:
- Pruebas unitarias (hardware y firmware)
- Pruebas de integración con la app
- Testeo en recreos y clases reales

### Resultados esperados:
- Iluminación LED correcta por modo seleccionado
- Comunicación estable sin errores
- Baja tasa de fallos

### Ajustes realizados:
- Mejora en estabilidad de comunicación Bluetooth
- Revisión de valores de resistencias por consumo real

---

## 📈 Conclusiones y Futuro Desarrollo

### Funcionó correctamente:
- Integración hardware-software
- Comunicación efectiva con app
- Iluminación clara y funcional

### Mejoras futuras:
- Agregado de sensores de luz y temperatura
- Conexión con red escolar
- Supervisión remota desde PC

---

## 📎 Anexos

- Código fuente del ESP32
- Datasheets (ESP32, Panel solar)
- Manual de uso de la aplicación

---

🛠️ **Este proyecto fue desarrollado como trabajo final para la materia Electrónica Digital IV.**
