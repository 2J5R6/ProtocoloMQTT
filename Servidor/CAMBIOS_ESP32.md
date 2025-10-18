# 📝 CAMBIOS REALIZADOS EN ESP32_SENSORES.INO

## Fecha: 17 de Octubre, 2025

---

## ✅ Actualizaciones Implementadas

### 1. **Formato JSON Compatible** 🔄

#### ANTES:
```json
{
  "sensor_id": "ESP32_01",
  "tipo": "temperatura",
  "valor": 25.5,
  "unidad": "°C",
  "estado": "normal",
  "timestamp": 12345678
}
```

#### AHORA:
```json
{
  "device_id": "ESP32_01",
  "value": 25.5,
  "unit": "°C",
  "status": "normal",
  "timestamp": 12345
}
```

### 2. **Cambios en los Nombres de Campos**

| Campo Anterior | Campo Nuevo | Razón |
|----------------|-------------|-------|
| `sensor_id` | `device_id` | Compatibilidad con suscriptor_admin.py |
| `valor` | `value` | Estándar en inglés |
| `unidad` | `unit` | Estándar en inglés |
| `estado` | `status` | Estándar en inglés |
| `tipo` | *(removido)* | No se usa en la base de datos |

### 3. **Timestamp Simplificado**

- **ANTES:** `millis()` - timestamp en milisegundos desde el inicio
- **AHORA:** `millis() / 1000` - timestamp en segundos (más compatible)

### 4. **Publicación Continua de Sensores Digitales**

**Sensores afectados:**
- `seguridad/movimiento` (PIR)
- `seguridad/puerta` (Reed Switch)

**ANTES:** Solo publicaban cuando había cambio de estado
**AHORA:** Publican en cada ciclo (cada 5 segundos) como el simulador

### 5. **Valores como Float**

Todos los valores numéricos ahora se envían como `float` explícitamente:
- Movimiento: `1.0` o `0.0` (antes `1` o `0`)
- Puerta: `1.0` o `0.0` (antes `1` o `0`)
- Humo y Luz: Mayor precisión con decimales

---

## 🔧 Compatibilidad

### ✅ Compatible con:
- ✅ `suscriptor_admin.py` - Procesa los campos correctamente
- ✅ Base de datos PostgreSQL - Extrae `device_id`, `value`, `unit`
- ✅ `sensor_simulator.py` - Mismo formato JSON

### ⚠️ Diferencias con el Simulador:

| Característica | ESP32 | Simulador |
|----------------|-------|-----------|
| Timestamp | Epoch Unix (segundos) | ISO 8601 string |
| Tópicos | 7 sensores | 8 sensores (incluye viento) |
| Device ID | ESP32_01 | SIMULATOR_01 |

**Nota:** El simulador incluye `clima/viento` porque es virtual. El ESP32 no lo tiene porque requeriría un anemómetro físico.

---

## 📊 Estructura de Mensajes por Tópico

### 1. **Clima - Temperatura**
```json
{
  "device_id": "ESP32_01",
  "value": 25.5,
  "unit": "°C",
  "timestamp": 12345
}
```

### 2. **Clima - Humedad**
```json
{
  "device_id": "ESP32_01",
  "value": 65.2,
  "unit": "%",
  "timestamp": 12345
}
```

### 3. **Incendio - Sensor de Humo**
```json
{
  "device_id": "ESP32_01",
  "value": 8.5,
  "unit": "%",
  "status": "normal",
  "timestamp": 12345
}
```

### 4. **Iluminación - Luz**
```json
{
  "device_id": "ESP32_01",
  "value": 45.2,
  "unit": "%",
  "timestamp": 12345
}
```

### 5. **Seguridad - Movimiento**
```json
{
  "device_id": "ESP32_01",
  "value": 1.0,
  "unit": "",
  "status": "detectado",
  "timestamp": 12345
}
```

### 6. **Seguridad - Puerta**
```json
{
  "device_id": "ESP32_01",
  "value": 0.0,
  "unit": "",
  "status": "cerrada",
  "timestamp": 12345
}
```

### 7. **Incendio - Alarma Manual**
```json
{
  "device_id": "ESP32_01",
  "value": 1.0,
  "unit": "",
  "status": "activada",
  "timestamp": 12345
}
```

---

## 🚀 Pasos para Cargar el Código Actualizado

### 1. **Configuración WiFi**
```cpp
const char* ssid = "TuRedWiFi";           // ⚠️ CAMBIAR
const char* password = "TuPassword";       // ⚠️ CAMBIAR
```

### 2. **Configuración MQTT**
```cpp
const char* mqtt_server = "192.168.1.100"; // ⚠️ IP de tu Kali Linux
const char* device_id = "ESP32_01";        // ⚠️ ID único del dispositivo
```

### 3. **Verificar Pines** (opcional)
Si tus conexiones físicas son diferentes, ajusta:
```cpp
#define DHT_PIN 11              // DHT11
#define MQ2_PIN 34              // Sensor de humo
#define LDR_PIN 35              // LDR
#define PIR_PIN 13              // PIR
#define REED_PIN 14             // Reed Switch
#define ALARM_BUTTON_PIN 12     // Botón alarma
```

### 4. **Librerías Requeridas** (Arduino IDE)
- PubSubClient (by Nick O'Leary)
- DHT sensor library (by Adafruit)
- ArduinoJson (by Benoit Blanchon)

### 5. **Cargar al ESP32**
1. Conectar ESP32 por USB
2. Seleccionar placa: "ESP32 Dev Module" o "ESP32-S3 Dev Module"
3. Seleccionar puerto COM correcto
4. Click en "Upload"

---

## ✅ Verificación Post-Carga

### 1. **Monitor Serial**
Deberías ver:
```
============================================
ESP32 - SENSORES MQTT
Universidad Militar Nueva Granada
============================================

✅ DHT11 inicializado
Conectando a WiFi: TuRedWiFi
.....
✅ WiFi conectado
📡 Dirección IP: 192.168.1.X
📶 Intensidad señal: -45 dBm
Conectando a MQTT... ✅ Conectado
📤 [clima/temperatura] {"device_id":"ESP32_01","value":25.5,"unit":"°C","timestamp":12}
📤 [clima/humedad] {"device_id":"ESP32_01","value":65.2,"unit":"%","timestamp":12}
...
```

### 2. **Terminal MQTT (Kali Linux)**
```bash
mosquitto_sub -h localhost -t "sensores/#" -v
```

Deberías ver mensajes del ESP32:
```
clima/temperatura {"device_id":"ESP32_01","value":25.5,"unit":"°C","timestamp":12}
clima/humedad {"device_id":"ESP32_01","value":65.2,"unit":"%","timestamp":12}
```

### 3. **Base de Datos**
```bash
.venv/bin/python consultar_db.py
```

Deberías ver datos de `ESP32_01` guardándose en la base de datos.

---

## 🔍 Solución de Problemas

### ❌ No conecta a WiFi
- Verificar SSID y contraseña
- Verificar que ESP32 esté en rango del router
- Verificar que la red sea 2.4GHz (ESP32 no soporta 5GHz)

### ❌ No conecta a MQTT
- Verificar IP del broker (usar `ip addr` en Kali)
- Verificar que Docker MQTT esté corriendo: `sudo docker ps`
- Ping desde ESP32 al servidor

### ❌ Sensores no leen correctamente
- Verificar conexiones físicas (VCC, GND, pines de datos)
- Verificar que DHT11 tenga 3.3V (no 5V)
- Verificar que MQ-2 tenga tiempo de calentamiento (2-3 minutos)

---

## 📚 Referencias

- **Código original:** `sensores/esp32_sensores.ino`
- **Simulador:** `sensores/sensor_simulator.py`
- **Suscriptor:** `suscriptores/suscriptor_admin.py`
- **Base de datos:** `database/schema.sql`

---

**Última actualización:** 17 de Octubre, 2025
**Estado:** ✅ Listo para usar
