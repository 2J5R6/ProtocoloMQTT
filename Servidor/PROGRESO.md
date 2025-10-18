# 📊 ESTADO DEL PROYECTO MQTT

**Fecha de actualización:** 2025-10-17  
**Universidad Militar Nueva Granada**  
**Taller Comunicaciones - 50% Segundo Corte**

---

## ✅ COMPLETADO (12/18 tareas - 67%)

### 📁 Estructura Base
- ✅ Carpetas creadas: `broker/`, `sensores/`, `suscriptores/`, `database/`, `docs/`
- ✅ Archivo README.md principal con toda la documentación

### 🔧 Broker MQTT
- ✅ `broker/docker-compose.yml` - Configuración Docker para Mosquitto
- ✅ `broker/mosquitto.conf` - Configuración completa del broker
- ✅ Soporte para instalación nativa en Kali Linux

### 🗄️ Base de Datos PostgreSQL
- ✅ `database/schema.sql` - Esquema completo con tablas, índices y vistas
- ✅ `database/db_config.py` - Módulo de conexión con funciones auxiliares
- ✅ Tabla `mensajes_mqtt` con todos los campos requeridos
- ✅ Vistas y funciones de estadísticas

### 📦 Dependencias
- ✅ `requirements.txt` - paho-mqtt, psycopg2-binary, python-dotenv
- ✅ `.env.example` - Plantilla de variables de entorno

### 📡 Publicadores (Sensores)
- ✅ `sensores/esp32_sensores.ino` - Código Arduino completo
  - DHT11 (Temperatura + Humedad)
  - MQ-2 (Sensor de humo)
  - LDR (Sensor de luz)
  - PIR (Sensor de movimiento)
  - Reed Switch (Sensor de puerta)
  - Botón de alarma manual
  - **Total: 7 sensores en 5 tópicos diferentes** ✅
  
- ✅ `sensores/sensor_simulator.py` - Simulador Python completo
  - Simula los 7 sensores
  - Publicación automática cada 5 segundos
  - Valores aleatorios realistas

### 🎧 Suscriptores
- ✅ `suscriptores/suscriptor_admin.py` - **Suscriptor administrativo completo**
  - Suscrito a todos los tópicos (#)
  - Almacena en PostgreSQL automáticamente
  - Manejo de errores y reconexión
  - Estadísticas en tiempo real

### �️ Sistema Operacional (NUEVO)
- ✅ **MQTT Broker** - Docker container running (mqtt-server)
- ✅ **PostgreSQL 17.6** - Instalado y configurado en Kali Linux
- ✅ **Base de Datos** - mqtt_taller creada con schema completo
- ✅ **Usuario DB** - mqtt_admin configurado con permisos
- ✅ **Entorno Python** - Virtual environment con todas las dependencias
- ✅ **Integración Completa** - 56+ mensajes almacenados exitosamente
- ✅ **Documentación de Inicio** - STARTUP.md y TESTING.md creados

---

## 🚧 EN PROGRESO (0/18 tareas)

*(Todas las tareas prioritarias completadas)*

---

## 📋 PENDIENTE (6/18 tareas - 33%)

### 🎧 Suscriptores Temáticos (4 pendientes)
- ⏳ `suscriptor_1_tematico.py` - Bomberos (incendio/#)
- ⏳ `suscriptor_2_tematico.py` - Vigilancia UMNG (seguridad/# + clima/#)
- ⏳ `suscriptor_3_tematico.py` - Profesor (iluminacion/# + clima/#)
- ⏳ `suscriptor_4_tematico.py` - Policía (seguridad/# + incendio/#)

### 📚 Documentación Adicional (Opcional)
- ⏳ Guías de uso avanzadas
- ⏳ Diagramas de flujo

### ⭐ Bonus (+0.5 puntos)
- ⏳ Autenticación MQTT (`broker/passwd`)
- ⏳ Conectividad desde Internet (port forwarding, DDNS)

---

## 📊 PROGRESO POR COMPONENTE

```
Estructura Base       ████████████████████ 100%
Broker MQTT          ████████████████████ 100%
Base de Datos        ████████████████████ 100%
Publicadores         ████████████████████ 100%
Suscriptor Admin     ████████████████████ 100%
Sistema Operacional  ████████████████████ 100%
Documentación Guías  ████████████████████ 100%
Suscriptores Tema    ░░░░░░░░░░░░░░░░░░░░   0%
Bonus                ░░░░░░░░░░░░░░░░░░░░   0%
───────────────────────────────────────────
TOTAL                █████████████░░░░░░░  67%
```

---

## 📝 ARCHIVOS CREADOS

```
taller comunicaciones/
├── ✅ README.md (Documentación principal - Actualizada)
├── ✅ PROGRESO.md (Estado del proyecto - Actualizado)
├── ✅ STARTUP.md (Guía de inicio del sistema - NUEVO)
├── ✅ TESTING.md (Guía de pruebas y verificación - NUEVO)
├── ✅ requirements.txt
├── ✅ .env.example
├── ✅ .env (Configurado)
│
├── broker/
│   ├── ✅ docker-compose.yml
│   └── ✅ mosquitto.conf
│
├── sensores/
│   ├── ✅ esp32_sensores.ino (7 sensores)
│   └── ✅ sensor_simulator.py (Probado ✓)
│
├── suscriptores/
│   ├── ✅ suscriptor_admin.py (COMPLETO y PROBADO ✓)
│   ├── ⏳ suscriptor_1_tematico.py (Bomberos - Pendiente)
│   ├── ⏳ suscriptor_2_tematico.py (Vigilancia - Pendiente)
│   ├── ⏳ suscriptor_3_tematico.py (Profesor - Pendiente)
│   └── ⏳ suscriptor_4_tematico.py (Policía - Pendiente)
│
├── database/
│   ├── ✅ schema.sql (Ejecutado en PostgreSQL ✓)
│   └── ✅ db_config.py (Probado ✓)
│
└── .venv/
    └── ✅ Entorno virtual con todas las dependencias
```

---

## 🎯 PRÓXIMOS PASOS

### Prioridad Alta
1. **Completar los 4 suscriptores temáticos**
   - Implementar lógica específica para cada rol
   - Filtrado de tópicos correcto
   - Visualización en consola
   - Logs de eventos relevantes

### Prioridad Media
2. **Pruebas con ESP32 físico**
   - Subir código al ESP32
   - Conectar sensores reales
   - Verificar publicación MQTT

### Prioridad Baja (Bonus)
3. **Autenticación y acceso remoto**
   - Configurar usuarios con `mosquitto_passwd`
   - Port forwarding y DDNS
   - Documentar credenciales

---

## ✅ REQUISITOS DEL TALLER

| Requisito | Estado | Detalle |
|-----------|--------|---------|
| **5 Tópicos MQTT** | ✅ | incendio/, seguridad/, clima/, iluminacion/, sistema/ |
| **7+ Sensores** | ✅ | DHT11(2), MQ-2, LDR, PIR, Reed, Botón = 7 sensores |
| **2+ Sensores en ESP32** | ✅ | Todos los 7 sensores en un ESP32 |
| **4 Suscriptores Temáticos** | ⏳ | 0/4 completados (0%) - Por implementar |
| **1 Suscriptor Admin** | ✅ | Completo con almacenamiento en PostgreSQL |
| **Base de Datos** | ✅ | PostgreSQL 17.6 con schema completo |
| **Timestamp recepción** | ✅ | Implementado y probado |
| **Campo tópico** | ✅ | Implementado y probado |
| **Sistema Funcional** | ✅ | 56+ mensajes guardados exitosamente |

---

## 🏆 LOGROS RECIENTES (2025-10-17)

### Sistema Completamente Operacional
- ✅ **MQTT Broker:** Running en Docker (mqtt-server container)
- ✅ **PostgreSQL:** Instalado, configurado y probado
- ✅ **Simulador:** Publicando 7-8 sensores cada 5 segundos
- ✅ **Suscriptor Admin:** Guardando mensajes en tiempo real
- ✅ **56+ Mensajes:** Almacenados con 0 errores (100% accuracy)
- ✅ **Documentación:** STARTUP.md y TESTING.md creados

---

## 💡 NOTAS IMPORTANTES

### Sistema Operacional (Kali Linux)
```bash
# Servicios necesarios
sudo systemctl start docker        # MQTT Broker (container)
sudo docker start mqtt-server      # Iniciar contenedor MQTT
sudo systemctl start postgresql    # Base de datos

# Activar entorno Python
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate

# Iniciar simulador (Terminal 1)
python sensores/sensor_simulator.py

# Iniciar suscriptor admin (Terminal 2)
python suscriptores/suscriptor_admin.py
```

### Para el ESP32
- Modificar `ssid` y `password` del WiFi
- Cambiar `mqtt_server` con la IP del servidor Kali Linux
- Instalar librerías: PubSubClient, DHT sensor library, ArduinoJson

### Verificación Rápida
```bash
# Ver mensajes en tiempo real
mosquitto_sub -h localhost -t "#" -v

# Contar mensajes en DB
sudo -u postgres psql -d mqtt_taller -c "SELECT COUNT(*) FROM mensajes_mqtt;"

# Ver estadísticas
sudo -u postgres psql -d mqtt_taller -c "SELECT topico, COUNT(*) FROM mensajes_mqtt GROUP BY topico;"
```

### Guías de Referencia
- **STARTUP.md** - Cómo iniciar el sistema completo después de reiniciar
- **TESTING.md** - Comandos de prueba y verificación del sistema
- **README.md** - Documentación completa del proyecto

---

## 📞 CONTACTO

**Profesor:** Héctor Bernal  
**Correo:** hector.bernal@unimilitar.edu.co  
**Peso:** 50% del segundo corte

---

**Última actualización:** 2025-10-17 - 67% completado  
**Sistema:** ✅ Completamente Operacional  
**Mensajes Procesados:** 56+ (0 errores)  
**Próximo hito:** Implementar suscriptores temáticos
