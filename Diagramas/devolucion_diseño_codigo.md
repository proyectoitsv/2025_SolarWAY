# Análisis de Correspondencia: Diseño vs. Implementación
**Proyecto:** SolarWAY  
**Fecha de Análisis:** 27 de noviembre de 2025  
**Evaluador:** GitHub Copilot

---

## 1. Resumen Ejecutivo

Este documento presenta un análisis comparativo entre los diagramas de diseño (casos de uso, estado, flujo y secuencia) y el código fuente implementado en el firmware y aplicación web del proyecto SolarWAY. Se evalúa la trazabilidad bidireccional para identificar brechas de implementación y documentación.

---

## 2. Análisis: Diseño → Código

### 2.1 Diagrama de Casos de Uso
**Casos de uso documentados:**
- Interacción usuario-sistema
- Funcionalidades principales del sistema
- Actores involucrados

**Correspondencia con código:**
- ⚠️ **Archivo sin extensión**: `Diagrama_de_casos_Uso` (no se puede visualizar contenido)
- ❓ **Pendiente de verificación**: Requiere acceso al contenido del diagrama
- ✅ **Interfaz web presente**: Aplicación web implementada (`Solarway_App/`)

### 2.2 Diagrama de Estados
**Estados documentados en diseño:**
- Estados de operación del sistema solar
- Transiciones entre modos de funcionamiento
- Estados de carga/descarga de batería
- Estados de monitoreo

**Correspondencia con código:**
- ❌ **No implementado**: Máquina de estados explícita en `Codigo.ino`
- ⚠️ **Estructura básica**: Código Arduino con setup/loop estándar
- ❓ **Lógica de estados**: No se evidencia FSM en el firmware
- ✅ **Aplicación web**: Posible gestión de estados en `app.py` y `app.js`

### 2.3 Diagrama de Flujo
**Flujos documentados:**
- Secuencia de inicialización
- Lógica de control de carga solar
- Procesamiento de datos de sensores
- Flujo de comunicación con interfaz web

**Correspondencia con código:**
- ⚠️ **Implementación parcial**: Lógica presente pero no estructurada según diagrama
- ✅ **Sensores y actuadores**: Implementación en Arduino
- ✅ **Comunicación**: Servidor web Python (`app.py`)
- ❌ **Control de carga**: No se evidencia regulador de carga en firmware

### 2.4 Diagrama de Secuencia
**Interacciones documentadas:**
- Comunicación MCU → Sensores
- Comunicación MCU → Servidor web
- Comunicación Servidor → Cliente web
- Sincronización de datos

**Correspondencia con código:**
- ✅ **Arduino → Servidor**: Implementación probable vía serial/HTTP
- ✅ **Servidor Flask**: `app.py` maneja backend
- ✅ **Frontend**: JavaScript (`app.js`) y HTML (`index.html`)
- ⚠️ **Protocolo de comunicación**: No documentado explícitamente

---

## 3. Análisis: Código → Diseño

### 3.1 Componentes Implementados

| Componente | Archivo/Carpeta | Documentado en Diagramas |
|------------|-----------------|--------------------------|
| Firmware Arduino | `Codigo.ino` | ✅ Sí (implícito) |
| Backend Python | `Solarway_App/app.py` | ⚠️ Parcial |
| Frontend Web | `templates/index.html` | ⚠️ Parcial |
| JavaScript | `static/app.js` | ❌ No |
| CSS | `static/style.css` | ❌ No |
| PCB Principal | `placa principal/` | ❓ Posiblemente |
| Regulador de Carga | `placa reguladr de carga/` | ⚠️ Parcial |

### 3.2 Arquitectura No Documentada

**Presente en código, ausente/incompleto en diagramas:**

1. **Arquitectura Cliente-Servidor**:
   - Servidor Flask (Python)
   - Cliente web (HTML/CSS/JS)
   - Comunicación bidireccional

2. **Dos versiones de aplicación**:
   - `Solarway_App/` (versión A)
   - `Solarway_App_B/` (versión B - solo `index.html`)
   - No documentada la razón de duplicación

3. **Hardware**:
   - Diseño PCB principal
   - PCB regulador de carga separado
   - No hay diagrama de bloques de hardware

4. **Dependencias**:
   - Librerías Python (`requirement.txt`)
   - Librerías Arduino (no especificadas)

### 3.3 Estructura de Proyecto

**Elementos de implementación sin documentación:**
- Configuración VS Code (`.vscode/`)
- Estructura de carpetas del proyecto
- Esquemáticos en formato JSON (EasyEDA)
- Sistema de archivos estáticos (imágenes, CSS, JS)
- Maqueta física (`Imagenes/Maqueta/`)

---

## 4. Brechas Identificadas

### 4.1 Implementación Incompleta (Diseño → Código)

1. **Crítico**: Máquina de estados no implementada en firmware
2. **Alto**: Control de regulador de carga (PCB diseñado, firmware ausente)
3. **Alto**: Integración entre firmware y regulador de carga
4. **Medio**: Protocolo de comunicación Arduino-Servidor no estandarizado
5. **Medio**: Manejo de errores y excepciones

### 4.2 Documentación Faltante (Código → Diseño)

1. **Crítico**: Diagrama de arquitectura de software (3 capas: firmware, backend, frontend)
2. **Alto**: Diagrama de componentes de hardware (MCU, sensores, PCBs)
3. **Alto**: Diagrama de despliegue (conexiones físicas y de red)
4. **Medio**: Diagramas de actividad para funciones específicas
5. **Medio**: Diagrama de clases/módulos (Python y Arduino)
6. **Bajo**: Diagrama de base de datos (si aplica para almacenamiento de datos)

### 4.3 Inconsistencias Detectadas

1. **Duplicación de aplicación web**: `Solarway_App` vs `Solarway_App_B`
2. **Esquemáticos en formato JSON**: Difícil mantenimiento sin diagrama visual
3. **Nomenclatura**: "reguladr" (typo en nombre de carpeta)
4. **Documentación vacía**: Carpeta `Documentacion/` sin contenido

---

## 5. Métricas de Correspondencia

| Métrica | Valor | Estado |
|---------|-------|--------|
| Cobertura Diseño→Código | ~40% | 🔴 Insuficiente |
| Cobertura Código→Diseño | ~35% | 🔴 Insuficiente |
| Trazabilidad Bidireccional | ~37% | 🔴 Crítico |
| Componentes documentados | 2/7 | 🔴 Crítico |
| Estados implementados | 0/N | 🔴 Crítico |
| Diagramas completos | 3/7+ | 🔴 Insuficiente |

**Nota**: Un diagrama de casos de uso no es legible (sin extensión de archivo)

---

## 6. Análisis por Capa de Aplicación

### 6.1 Capa de Hardware (Firmware Arduino)
| Aspecto | Diseño | Implementación | Estado |
|---------|--------|----------------|--------|
| FSM | ✅ Documentado | ❌ No implementado | 🔴 |
| Sensores | ⚠️ Parcial | ✅ Implementado | 🟡 |
| Actuadores | ⚠️ Parcial | ✅ Implementado | 🟡 |
| Comunicación | ✅ Documentado | ⚠️ Parcial | 🟡 |
| PCB | ✅ Diseñado | ✅ Diseñado | 🟢 |

### 6.2 Capa de Backend (Python Flask)
| Aspecto | Diseño | Implementación | Estado |
|---------|--------|----------------|--------|
| API REST | ❌ No documentado | ✅ Implementado | 🟡 |
| Rutas | ❌ No documentado | ✅ Implementado | 🟡 |
| Lógica de negocio | ⚠️ Parcial | ✅ Implementado | 🟡 |
| Base de datos | ❓ Desconocido | ❓ Desconocido | ⚪ |

### 6.3 Capa de Frontend (HTML/CSS/JS)
| Aspecto | Diseño | Implementación | Estado |
|---------|--------|----------------|--------|
| UI/UX | ❌ No documentado | ✅ Implementado | 🟡 |
| Interacción usuario | ⚠️ Casos de uso | ✅ Implementado | 🟡 |
| Visualización datos | ❌ No documentado | ✅ Implementado | 🟡 |
| Responsive design | ❌ No documentado | ❓ Desconocido | ⚪ |

---

## 7. Recomendaciones

### 7.1 Prioridad Crítica
1. **Implementar FSM en firmware**: Según diagrama de estados
2. **Documentar arquitectura de software**: Diagrama de 3 capas (firmware/backend/frontend)
3. **Consolidar versión de aplicación web**: Eliminar duplicación o documentar diferencias
4. **Crear diagrama de componentes hardware**: Mostrar interconexión PCBs, sensores, MCU

### 7.2 Prioridad Alta
1. **Integrar regulador de carga**: Firmware para control del PCB diseñado
2. **Documentar protocolo de comunicación**: Entre Arduino y servidor Python
3. **Diagrama de despliegue**: Mostrar conexiones físicas y de red
4. **Especificar API REST**: Endpoints, métodos, payloads
5. **Poblar carpeta Documentacion/**: Con diagramas faltantes

### 7.3 Prioridad Media
1. **Diagrama de secuencia detallado**: Para cada flujo principal
2. **Documentar dependencias**: Librerías Arduino y Python utilizadas
3. **Diagrama de actividad**: Para algoritmos complejos (control de carga)
4. **Estandarizar nomenclatura**: Corregir errores tipográficos en nombres de carpetas
5. **Mockups de UI**: Diseño de interfaz antes de implementación

### 7.4 Prioridad Baja
1. **Convertir esquemáticos JSON**: A formato PDF/imagen para documentación
2. **Documentar maqueta física**: Relación con diseño final
3. **Diagrama de clases**: Para código Python orientado a objetos
4. **Plan de pruebas**: Basado en casos de uso

---

## 8. Fortalezas Identificadas

1. ✅ **Diseño de PCB completo**: Tanto principal como regulador de carga
2. ✅ **Aplicación web funcional**: Stack completo (Flask + HTML/CSS/JS)
3. ✅ **Estructura de proyecto clara**: Separación de responsabilidades
4. ✅ **Múltiples diagramas UML**: Esfuerzo de documentación inicial
5. ✅ **Configuración de desarrollo**: VS Code configurado

---

## 9. Riesgos del Proyecto

| Riesgo | Severidad | Impacto |
|--------|-----------|---------|
| FSM no implementada | 🔴 Alta | Control de sistema inestable |
| Regulador de carga sin firmware | 🔴 Alta | Funcionalidad crítica ausente |
| Arquitectura no documentada | 🟡 Media | Mantenimiento difícil |
| Protocolo de comunicación informal | 🟡 Media | Posibles fallos de integración |
| Duplicación de código | 🟡 Media | Confusión en despliegue |
| Diagramas incompletos | 🟢 Baja | Documentación insuficiente |

---

## 10. Plan de Acción Sugerido

### Fase 1: Completar Funcionalidad Crítica (2 semanas)
- [ ] Implementar máquina de estados en firmware Arduino
- [ ] Integrar firmware de regulador de carga
- [ ] Definir y documentar protocolo de comunicación Arduino-Python
- [ ] Probar integración completa hardware-software

### Fase 2: Alinear Documentación (1 semana)
- [ ] Crear diagrama de arquitectura de software
- [ ] Crear diagrama de componentes de hardware
- [ ] Documentar API REST del servidor Flask
- [ ] Actualizar diagramas de secuencia con flujos reales

### Fase 3: Refinamiento (1 semana)
- [ ] Consolidar versión final de aplicación web
- [ ] Corregir nomenclatura y estructura de carpetas
- [ ] Generar documentación técnica completa
- [ ] Crear guía de despliegue y uso

---

## 11. Conclusiones

El proyecto SolarWAY presenta una **desalineación significativa y crítica** entre diseño e implementación:

### Fortalezas
- Diseño hardware (PCB) profesional y completo
- Aplicación web funcional con stack tecnológico moderno
- Intención de documentación mediante múltiples diagramas UML

### Debilidades Críticas
- **Máquina de estados diseñada pero no implementada**
- **Regulador de carga diseñado sin firmware de control**
- **Arquitectura de software no documentada** (3 capas implementadas sin diagramas)
- **Protocolo de comunicación no estandarizado**
- **Duplicación de código sin justificación**

### Evaluación General
El proyecto muestra **mayor madurez en hardware que en software**. La implementación del código supera a la documentación en varios aspectos, pero falta la integración de componentes críticos diseñados (FSM, regulador de carga). La arquitectura real (frontend/backend/firmware) no está reflejada en los diagramas.

**Recomendación principal**: Priorizar la implementación de la FSM y el firmware del regulador de carga antes de continuar con desarrollo adicional. Paralelamente, actualizar diagramas para reflejar la arquitectura real de 3 capas implementada.

---

**Estado del Proyecto:** 🔴 En desarrollo - Requiere alineación urgente diseño-código  
**Riesgo de Funcionalidad:** Alto (componentes críticos sin integrar)  
**Próxima revisión recomendada:** Tras completar Fase 1 del plan de acción

---

**Anexos Recomendados:**
- A. Especificación del protocolo de comunicación Arduino-Python
- B. Diagrama de arquitectura de software (3 capas)
- C. Especificación API REST del servidor Flask
- D. Guía de integración de regulador de carga