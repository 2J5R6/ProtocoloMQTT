# 🔌 GUÍA DE CONEXIONES - ESP32-S3 CON POTENCIÓMETROS

## 📅 Fecha: 17 de Octubre, 2025

---

## 🎯 CONFIGURACIÓN PARA ESP32-S3

### ✅ Hardware Requerido:
- 1x ESP32-S3 DevKit
- 8x Potenciómetros 10kΩ (recomendado)
- 1x Protoboard
- Cables jumper macho-macho

---

## 📊 TABLA DE CONEXIONES DE POTENCIÓMETROS

| POT # | GPIO | ADC | Sensor Simulado | Rango | Tópico MQTT |
|-------|------|-----|-----------------|-------|-------------|
| **POT 1** | GPIO 1 | ADC1_CH0 | 🌡️ Temperatura | 0-50°C | `clima/temperatura` |
| **POT 2** | GPIO 2 | ADC1_CH1 | 💧 Humedad | 0-100% | `clima/humedad` |
| **POT 3** | GPIO 3 | ADC1_CH2 | 🔥 Humo | 0-100% | `incendio/sensor_humo` |
| **POT 4** | GPIO 4 | ADC1_CH3 | 💡 Luz | 0-100% | `iluminacion/luz` |
| **POT 5** | GPIO 5 | ADC1_CH4 | 🚶 Movimiento | Digital | `seguridad/movimiento` |
| **POT 6** | GPIO 6 | ADC1_CH5 | 🚪 Puerta | Digital | `seguridad/puerta` |
| **POT 7** | GPIO 7 | ADC1_CH6 | 🚨 Alarma | >80% activa | `incendio/alarma` |
| **POT 8** | GPIO 8 | ADC1_CH7 | 🌬️ Viento | 0-100 km/h | `clima/viento` |

---

## 🔧 ESQUEMA DE CONEXIÓN DE CADA POTENCIÓMETRO

### Conexión Estándar (para todos los potenciómetros):

```
POTENCIÓMETRO (Vista frontal)
     ___
    |   |
    | ⚪ |  <- Eje giratorio
    |___|
    
   1  2  3   <- Terminales

Terminal 1 (Izquierda)  -> 3.3V del ESP32-S3
Terminal 2 (Centro)     -> GPIO ADC correspondiente
Terminal 3 (Derecha)    -> GND del ESP32-S3
```

### ⚠️ IMPORTANTE:
- **NUNCA uses 5V** - El ESP32-S3 solo soporta 3.3V en pines ADC
- **Terminal central (wiper)** debe ir al GPIO
- **Terminales externos** van a 3.3V y GND (orden no importa)

---

## 📐 DIAGRAMA DE PROTOBOARD

```
ESP32-S3                    PROTOBOARD
┌─────────────┐
│             │             3.3V Rail (+)
│         3.3V├────────────────█████████████
│             │
│         GND ├────────────────═════════════
│             │             GND Rail (-)
│             │
│   GPIO 1 ◄──┼────┐
│             │    │        POT 1 (Temperatura)
│   GPIO 2 ◄──┼────┼────┐   Terminal 1 -> 3.3V
│             │    │    │   Terminal 2 -> GPIO
│   GPIO 3 ◄──┼────┼────┼────┐ Terminal 3 -> GND
│             │    │    │    │
│   GPIO 4 ◄──┼────┼────┼────┼────┐
│             │    │    │    │    │
│   GPIO 5 ◄──┼────┼────┼────┼────┼────┐
│             │    │    │    │    │    │
│   GPIO 6 ◄──┼────┼────┼────┼────┼────┼────┐
│             │    │    │    │    │    │    │
│   GPIO 7 ◄──┼────┼────┼────┼────┼────┼────┼────┐
│             │    │    │    │    │    │    │    │
│   GPIO 8 ◄──┼────┼────┼────┼────┼────┼────┼────┼────┐
│             │    │    │    │    │    │    │    │    │
└─────────────┘    │    │    │    │    │    │    │    │
                   ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
                  POT  POT  POT  POT  POT  POT  POT  POT
                   1    2    3    4    5    6    7    8
```

---

## 🔍 VERIFICACIÓN DE PINES ADC ESP32-S3

### ✅ Pines ADC1 (Usados - No conflicto con WiFi):
| GPIO | ADC | Estado | Uso |
|------|-----|--------|-----|
| GPIO 1 | ADC1_CH0 | ✅ ADC | Temperatura |
| GPIO 2 | ADC1_CH1 | ✅ ADC | Humedad |
| GPIO 3 | ADC1_CH2 | ✅ ADC | Humo |
| GPIO 4 | ADC1_CH3 | ✅ ADC | Luz |
| GPIO 5 | ADC1_CH4 | ✅ ADC | Movimiento |
| GPIO 6 | ADC1_CH5 | ✅ ADC | Puerta |
| GPIO 7 | ADC1_CH6 | ✅ ADC | Alarma |
| GPIO 8 | ADC1_CH7 | ✅ ADC | Viento |
| GPIO 9 | ADC1_CH8 | - | Reserva |
| GPIO 10 | ADC1_CH9 | - | Reserva |

### ⚠️ Pines ADC2 (No usar - conflicto con WiFi):
Los pines GPIO 11-20 (ADC2) **NO FUNCIONAN** cuando WiFi está activo.

---

## 🎛️ COMPORTAMIENTO DE CADA POTENCIÓMETRO

### 1️⃣ **POT 1 - Temperatura (GPIO 1)**
- **Totalmente a la izquierda:** 0°C
- **Centro:** 25°C
- **Totalmente a la derecha:** 50°C
- **Publicación:** Cada 5 segundos
- **Formato JSON:** `{"device_id":"ESP32_01","value":25.5,"unit":"°C","timestamp":123}`

### 2️⃣ **POT 2 - Humedad (GPIO 2)**
- **Totalmente a la izquierda:** 0%
- **Centro:** 50%
- **Totalmente a la derecha:** 100%
- **Publicación:** Cada 5 segundos
- **Formato JSON:** `{"device_id":"ESP32_01","value":65.2,"unit":"%","timestamp":123}`

### 3️⃣ **POT 3 - Humo (GPIO 3)**
- **Totalmente a la izquierda:** 0% (Normal)
- **Centro:** 50% (Límite)
- **Totalmente a la derecha:** 100% (**ALERTA**)
- **Publicación:** Cada 5 segundos
- **Estado especial:** Si >50% agrega `"status":"alerta"`
- **Formato JSON:** `{"device_id":"ESP32_01","value":75.0,"unit":"%","status":"alerta","timestamp":123}`

### 4️⃣ **POT 4 - Luz (GPIO 4)**
- **Totalmente a la izquierda:** 0% (Oscuridad total)
- **Centro:** 50%
- **Totalmente a la derecha:** 100% (Máxima luz)
- **Publicación:** Cada 5 segundos
- **Formato JSON:** `{"device_id":"ESP32_01","value":45.2,"unit":"%","timestamp":123}`

### 5️⃣ **POT 5 - Movimiento (GPIO 5)** 🎯 Digital Simulado
- **< 50%:** Sin movimiento (value = 0.0)
- **≥ 50%:** Movimiento detectado (value = 1.0)
- **Publicación:** Cada 5 segundos
- **Formato JSON:** `{"device_id":"ESP32_01","value":1.0,"unit":"","status":"detectado","timestamp":123}`

### 6️⃣ **POT 6 - Puerta (GPIO 6)** 🎯 Digital Simulado
- **< 50%:** Puerta cerrada (value = 0.0)
- **≥ 50%:** Puerta abierta (value = 1.0)
- **Publicación:** Cada 5 segundos
- **Formato JSON:** `{"device_id":"ESP32_01","value":0.0,"unit":"","status":"cerrada","timestamp":123}`

### 7️⃣ **POT 7 - Alarma (GPIO 7)** 🚨 Activación Especial
- **< 80%:** Alarma desactivada (no publica)
- **> 80%:** **ALARMA ACTIVADA** (publica inmediatamente)
- **Publicación:** Solo cuando se activa (>80%)
- **Formato JSON:** `{"device_id":"ESP32_01","value":1.0,"unit":"","status":"activada","timestamp":123}`

### 8️⃣ **POT 8 - Viento (GPIO 8)**
- **Totalmente a la izquierda:** 0 km/h (Sin viento)
- **Centro:** 50 km/h
- **Totalmente a la derecha:** 100 km/h (Huracán)
- **Publicación:** Cada 5 segundos
- **Formato JSON:** `{"device_id":"ESP32_01","value":45.0,"unit":"km/h","timestamp":123}`

---

## 🛠️ PASOS DE INSTALACIÓN

### 1. **Preparar Hardware**
```
✅ Conectar los 8 potenciómetros según la tabla
✅ Verificar que todos los pines centrales vayan a GPIO 1-8
✅ Verificar que todos compartan 3.3V y GND
✅ NO usar 5V en ningún potenciómetro
```

### 2. **Configurar Arduino IDE**
```
✅ Instalar soporte para ESP32-S3:
   - Archivo > Preferencias > URLs adicionales:
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   
✅ Herramientas > Placa > ESP32 Arduino > ESP32S3 Dev Module

✅ Instalar librerías:
   - Sketch > Incluir Biblioteca > Administrar Bibliotecas
   - Buscar e instalar:
     * PubSubClient (by Nick O'Leary)
     * ArduinoJson (by Benoit Blanchon)
```

### 3. **Configurar Código**
Editar en `esp32_sensores.ino`:
```cpp
const char* ssid = "TuRedWiFi";              // ⚠️ CAMBIAR
const char* password = "TuPasswordWiFi";     // ⚠️ CAMBIAR
const char* mqtt_server = "192.168.1.100";   // ⚠️ IP de tu Kali Linux
```

### 4. **Cargar Código**
```
✅ Conectar ESP32-S3 por USB
✅ Seleccionar puerto COM correcto
✅ Click en "Upload" (Subir)
✅ Esperar mensaje "Done uploading"
```

### 5. **Verificar en Monitor Serial**
```
Abrir Monitor Serial (115200 baud)

Deberías ver:
============================================
ESP32-S3 - SENSORES MQTT CON POTENCIÓMETROS
Universidad Militar Nueva Granada
============================================

✅ Pines ADC configurados (8 potenciómetros)
Conectando a WiFi: TuRedWiFi
.....
✅ WiFi conectado
📡 Dirección IP: 192.168.1.XX
Conectando a MQTT... ✅ Conectado
📤 [clima/temperatura] {"device_id":"ESP32_01","value":25.5,...}
```

---

## ✅ PRUEBAS Y VERIFICACIÓN

### Test 1: Verificar Publicación MQTT
```bash
# En Kali Linux
mosquitto_sub -h localhost -t "sensores/#" -v
```

**Resultado esperado:**
```
clima/temperatura {"device_id":"ESP32_01","value":25.5,"unit":"°C","timestamp":123}
clima/humedad {"device_id":"ESP32_01","value":65.2,"unit":"%","timestamp":124}
...
```

### Test 2: Probar Cada Potenciómetro
1. **POT 1 (Temperatura):** Girar y ver cambios de 0-50°C
2. **POT 2 (Humedad):** Girar y ver cambios de 0-100%
3. **POT 3 (Humo):** Girar >50% y verificar "status":"alerta"
4. **POT 4 (Luz):** Girar y ver cambios de 0-100%
5. **POT 5 (Movimiento):** Girar >50% y verificar value: 1.0
6. **POT 6 (Puerta):** Girar >50% y verificar "status":"abierta"
7. **POT 7 (Alarma):** Girar >80% y verificar publicación inmediata
8. **POT 8 (Viento):** Girar y ver cambios de 0-100 km/h

### Test 3: Verificar Base de Datos
```bash
cd /home/daniel/Documents/COMUNICACIONES/taller\ en\ kali/taller-comunicaciones
.venv/bin/python consultar_db.py
```

**Resultado esperado:**
- Mensajes de `ESP32_01` guardándose en la base de datos
- 8 tópicos diferentes publicando datos

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### ❌ Lecturas ADC inestables
**Causa:** Cables demasiado largos o mala conexión  
**Solución:** Usar cables cortos (<20cm) y conexiones firmes

### ❌ Valores siempre en 0 o 4095
**Causa:** Potenciómetro mal conectado  
**Solución:** Verificar que el terminal central vaya al GPIO

### ❌ ESP32 se resetea constantemente
**Causa:** Usando 5V en pines ADC  
**Solución:** **SOLO usar 3.3V** para potenciómetros

### ❌ No conecta a WiFi
**Causa:** Red 5GHz o credenciales incorrectas  
**Solución:** Usar red 2.4GHz y verificar SSID/password

### ❌ Algunos potenciómetros no leen
**Causa:** Pines ADC2 (GPIO 11-20) no funcionan con WiFi  
**Solución:** Usar **SOLO GPIO 1-10** (ADC1)

---

## 📚 REFERENCIAS TÉCNICAS

### Especificaciones ESP32-S3 ADC:
- **Resolución:** 12 bits (0-4095)
- **Voltaje máximo:** 3.3V (¡NUNCA 5V!)
- **ADC1:** GPIO 1-10 (✅ Compatible con WiFi)
- **ADC2:** GPIO 11-20 (❌ No usar con WiFi)
- **Precisión:** ±2% (típica)

### Librerías Utilizadas:
- **PubSubClient:** Cliente MQTT para Arduino
- **ArduinoJson:** Serialización/deserialización JSON
- **WiFi:** Conectividad WiFi (incluida con ESP32)

---

## 🎓 CONSEJOS PARA LA DEMOSTRACIÓN

1. **Etiqueta cada potenciómetro** con su función (Temp, Hum, etc.)
2. **Marca la posición del 50%** en POT 5, 6 (umbral digital)
3. **Marca la posición del 80%** en POT 7 (activación alarma)
4. **Practica antes** girando cada uno y viendo los valores
5. **Ten abierto** el Monitor Serial + mosquitto_sub + consultar_db.py

---

**Última actualización:** 17 de Octubre, 2025  
**Plataforma:** ESP32-S3 DevKit  
**Estado:** ✅ Listo para implementación con potenciómetros
