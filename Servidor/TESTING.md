# 🧪 GUÍA DE PRUEBAS Y VERIFICACIÓN DEL SISTEMA MQTT

> **Comandos y procedimientos para verificar que todo funciona correctamente**

**Universidad Militar Nueva Granada**  
**Taller de Comunicaciones - Sistema MQTT IoT**

---

## 📋 Tabla de Contenidos

1. [Verificación Rápida del Sistema](#verificación-rápida-del-sistema)
2. [Pruebas del MQTT Broker](#pruebas-del-mqtt-broker)
3. [Pruebas de Base de Datos](#pruebas-de-base-de-datos)
4. [Pruebas del Simulador](#pruebas-del-simulador)
5. [Pruebas del Suscriptor Administrativo](#pruebas-del-suscriptor-administrativo)
6. [Pruebas de Integración Completa](#pruebas-de-integración-completa)
7. [Consultas SQL Útiles](#consultas-sql-útiles)
8. [Monitoreo en Tiempo Real](#monitoreo-en-tiempo-real)

---

## ⚡ Verificación Rápida del Sistema

### Script de Verificación Automática

```bash
#!/bin/bash
echo "🔍 VERIFICACIÓN DEL SISTEMA MQTT"
echo "================================"
echo ""

# Test 1: Docker
echo "1️⃣  Docker Service..."
if sudo systemctl is-active --quiet docker; then
    echo "   ✅ Docker está corriendo"
else
    echo "   ❌ Docker NO está corriendo"
fi

# Test 2: MQTT Broker
echo "2️⃣  MQTT Broker..."
if sudo docker ps | grep -q mqtt-server; then
    echo "   ✅ MQTT Broker está corriendo"
    echo "   📊 Puerto: 1883"
else
    echo "   ❌ MQTT Broker NO está corriendo"
fi

# Test 3: PostgreSQL
echo "3️⃣  PostgreSQL..."
if sudo systemctl is-active --quiet postgresql; then
    echo "   ✅ PostgreSQL está corriendo"
else
    echo "   ❌ PostgreSQL NO está corriendo"
fi

# Test 4: Conexión MQTT
echo "4️⃣  Conectividad MQTT..."
if mosquitto_pub -h localhost -t "test/verify" -m "test" 2>/dev/null; then
    echo "   ✅ Puede publicar a MQTT"
else
    echo "   ❌ NO puede publicar a MQTT"
fi

# Test 5: Base de datos
echo "5️⃣  Base de Datos..."
if sudo -u postgres psql -d mqtt_taller -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ Base de datos accesible"
    COUNT=$(sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;")
    echo "   📊 Mensajes almacenados: $COUNT"
else
    echo "   ❌ Base de datos NO accesible"
fi

# Test 6: Entorno Python
echo "6️⃣  Entorno Python..."
if [ -d ".venv" ]; then
    echo "   ✅ Entorno virtual existe"
    source .venv/bin/activate
    if python -c "import paho.mqtt.client" 2>/dev/null; then
        echo "   ✅ paho-mqtt instalado"
    else
        echo "   ❌ paho-mqtt NO instalado"
    fi
    if python -c "import psycopg2" 2>/dev/null; then
        echo "   ✅ psycopg2 instalado"
    else
        echo "   ❌ psycopg2 NO instalado"
    fi
else
    echo "   ❌ Entorno virtual NO existe"
fi

echo ""
echo "================================"
echo "✅ Verificación completada"
```

**Guardar como:** `verify_system.sh`

```bash
chmod +x verify_system.sh
./verify_system.sh
```

---

## 📡 Pruebas del MQTT Broker

### Prueba 1: Verificar que el broker está escuchando

```bash
# Ver si el puerto 1883 está abierto
sudo netstat -tlnp | grep 1883
```

**Salida esperada:**
```
tcp   0   0   0.0.0.0:1883   0.0.0.0:*   LISTEN   1234/docker-proxy
```

### Prueba 2: Publicar mensaje simple

```bash
# Publicar un mensaje de prueba
mosquitto_pub -h localhost -t "test/simple" -m "Hola MQTT"
```

**Resultado esperado:** Sin salida = éxito

### Prueba 3: Publicar mensaje JSON

```bash
# Publicar mensaje con formato JSON
mosquitto_pub -h localhost -t "test/json" -m '{"sensor_id":"TEST","valor":25.5,"unidad":"C"}'
```

### Prueba 4: Suscribirse y verificar recepción

**Terminal 1:**
```bash
# Suscriptor (dejar corriendo)
mosquitto_sub -h localhost -t "test/#" -v
```

**Terminal 2:**
```bash
# Publicador
mosquitto_pub -h localhost -t "test/demo" -m "Mensaje de prueba"
```

**Resultado esperado:** En Terminal 1 deberías ver:
```
test/demo Mensaje de prueba
```

### Prueba 5: Verificar todos los tópicos del proyecto

```bash
# Publicar a cada tópico del proyecto
mosquitto_pub -h localhost -t "clima/temperatura" -m '{"sensor_id":"TEST","valor":23.5,"unidad":"C"}'
mosquitto_pub -h localhost -t "clima/humedad" -m '{"sensor_id":"TEST","valor":65.0,"unidad":"%"}'
mosquitto_pub -h localhost -t "incendio/sensor_humo" -m '{"sensor_id":"TEST","valor":5.0,"unidad":"%"}'
mosquitto_pub -h localhost -t "seguridad/puerta" -m '{"sensor_id":"TEST","valor":0,"estado":"cerrada"}'
mosquitto_pub -h localhost -t "seguridad/movimiento" -m '{"sensor_id":"TEST","valor":0,"estado":"sin_movimiento"}'
mosquitto_pub -h localhost -t "iluminacion/luz" -m '{"sensor_id":"TEST","valor":75.0,"unidad":"%"}'
```

### Prueba 6: Monitorear TODOS los mensajes

```bash
# Suscribirse a TODOS los tópicos (wildcard #)
mosquitto_sub -h localhost -t "#" -v
```

---

## 🗄️ Pruebas de Base de Datos

### Prueba 1: Conectar a la base de datos

```bash
# Conectar como usuario postgres
sudo -u postgres psql -d mqtt_taller
```

**Comandos dentro de psql:**
```sql
-- Ver tablas
\dt

-- Ver información de la tabla principal
\d mensajes_mqtt

-- Salir
\q
```

### Prueba 2: Contar mensajes totales

```bash
sudo -u postgres psql -d mqtt_taller -c "SELECT COUNT(*) as total_mensajes FROM mensajes_mqtt;"
```

### Prueba 3: Ver mensajes por tópico

```bash
sudo -u postgres psql -d mqtt_taller -c "
SELECT 
    topico, 
    COUNT(*) as cantidad,
    MAX(timestamp_recepcion) as ultimo_mensaje
FROM mensajes_mqtt
GROUP BY topico
ORDER BY cantidad DESC;
"
```

### Prueba 4: Ver últimos 10 mensajes

```bash
sudo -u postgres psql -d mqtt_taller -c "
SELECT 
    id,
    topico,
    sensor_id,
    valor_numerico,
    unidad,
    timestamp_recepcion
FROM mensajes_mqtt
ORDER BY timestamp_recepcion DESC
LIMIT 10;
"
```

### Prueba 5: Insertar mensaje manual

```bash
sudo -u postgres psql -d mqtt_taller -c "
INSERT INTO mensajes_mqtt (topico, mensaje, sensor_id, valor_numerico, unidad)
VALUES ('test/manual', '{\"test\":\"value\"}', 'MANUAL_TEST', 99.9, 'test');
"
```

### Prueba 6: Usar las vistas creadas

```bash
# Ver mensajes recientes (últimas 24 horas)
sudo -u postgres psql -d mqtt_taller -c "SELECT * FROM mensajes_recientes LIMIT 5;"

# Ver estadísticas por tópico
sudo -u postgres psql -d mqtt_taller -c "SELECT * FROM estadisticas_topicos;"
```

### Prueba 7: Verificar conexión desde Python

```bash
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate

python3 << EOF
from database.db_config import crear_conexion

conn = crear_conexion()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mensajes_mqtt;")
    count = cursor.fetchone()[0]
    print(f"✅ Conexión exitosa! Mensajes en DB: {count}")
    cursor.close()
    conn.close()
else:
    print("❌ Error al conectar")
EOF
```

---

## 🔬 Pruebas del Simulador

### Prueba 1: Ejecutar simulador por 30 segundos

```bash
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate

# Ejecutar y detener después de 30 segundos
timeout 30s python sensores/sensor_simulator.py
```

### Prueba 2: Verificar que publica a todos los tópicos

**Terminal 1** (Monitoreo):
```bash
mosquitto_sub -h localhost -t "#" -v | grep "SIMULATOR_01"
```

**Terminal 2** (Simulador):
```bash
source .venv/bin/activate
python sensores/sensor_simulator.py
```

**Verificar que aparecen los 7-8 sensores:**
- clima/temperatura
- clima/humedad
- incendio/sensor_humo
- iluminacion/luz
- clima/viento
- seguridad/puerta
- seguridad/movimiento
- incendio/alarma (ocasional)

### Prueba 3: Verificar formato JSON

```bash
# Capturar un mensaje y verificar estructura
mosquitto_sub -h localhost -t "clima/temperatura" -C 1

# Debería mostrar algo como:
# {"sensor_id": "SIMULATOR_01", "tipo": "temperatura", "valor": 25.3, "unidad": "°C", "timestamp": "2025-10-17T..."}
```

---

## 💾 Pruebas del Suscriptor Administrativo

### Prueba 1: Ejecutar suscriptor por 1 minuto

```bash
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate

# Ejecutar por 60 segundos
timeout 60s python suscriptores/suscriptor_admin.py
```

### Prueba 2: Verificar almacenamiento en DB

```bash
# Antes de iniciar el suscriptor, contar mensajes
BEFORE=$(sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;")
echo "Mensajes antes: $BEFORE"

# Ejecutar suscriptor por 30 segundos con simulador
# (En otra terminal ejecuta el simulador)
timeout 30s python suscriptores/suscriptor_admin.py

# Después, contar mensajes
AFTER=$(sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;")
echo "Mensajes después: $AFTER"
echo "Nuevos mensajes: $((AFTER - BEFORE))"
```

### Prueba 3: Verificar que captura TODOS los tópicos

```bash
# Publicar a diferentes tópicos
for topic in "clima/temperatura" "seguridad/puerta" "incendio/sensor_humo"; do
    mosquitto_pub -h localhost -t "$topic" -m "{\"sensor_id\":\"TEST\",\"valor\":1}"
    sleep 1
done

# Verificar en la base de datos
sudo -u postgres psql -d mqtt_taller -c "
SELECT topico, COUNT(*) 
FROM mensajes_mqtt 
WHERE sensor_id='TEST' 
GROUP BY topico;
"
```

---

## 🔗 Pruebas de Integración Completa

### Prueba 1: Sistema completo por 2 minutos

**Terminal 1** - Simulador:
```bash
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate
timeout 120s python sensores/sensor_simulator.py
```

**Terminal 2** - Suscriptor:
```bash
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate
timeout 120s python suscriptores/suscriptor_admin.py
```

**Terminal 3** - Verificación:
```bash
# Contar mensajes cada 10 segundos
watch -n 10 'sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;"'
```

### Prueba 2: Verificar flujo de datos completo

```bash
# Script de prueba completa
#!/bin/bash

echo "🧪 Iniciando prueba de integración completa..."

# Contar mensajes iniciales
INITIAL=$(sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;" | tr -d ' ')
echo "📊 Mensajes iniciales: $INITIAL"

echo ""
echo "🚀 Iniciando componentes..."
echo "   (Espera 60 segundos)"

# Iniciar simulador en background
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
source .venv/bin/activate
python sensores/sensor_simulator.py > /tmp/simulator.log 2>&1 &
SIM_PID=$!

# Iniciar suscriptor en background  
python suscriptores/suscriptor_admin.py > /tmp/subscriber.log 2>&1 &
SUB_PID=$!

# Esperar 60 segundos
sleep 60

# Detener procesos
kill $SIM_PID $SUB_PID 2>/dev/null

echo ""
echo "🔍 Verificando resultados..."

# Contar mensajes finales
FINAL=$(sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;" | tr -d ' ')
ADDED=$((FINAL - INITIAL))

echo "📊 Mensajes finales: $FINAL"
echo "📈 Mensajes nuevos: $ADDED"

if [ $ADDED -gt 0 ]; then
    echo "✅ ¡Prueba exitosa! Se guardaron $ADDED mensajes"
else
    echo "❌ Prueba fallida. No se guardaron mensajes nuevos"
fi

# Mostrar estadísticas
echo ""
echo "📊 Estadísticas por tópico:"
sudo -u postgres psql -d mqtt_taller -c "
SELECT topico, COUNT(*) as cantidad
FROM mensajes_mqtt
GROUP BY topico
ORDER BY cantidad DESC
LIMIT 10;
"
```

---

## 📊 Consultas SQL Útiles

### Consultas Básicas

```sql
-- 1. Total de mensajes
SELECT COUNT(*) as total FROM mensajes_mqtt;

-- 2. Mensajes por tópico
SELECT topico, COUNT(*) as cantidad
FROM mensajes_mqtt
GROUP BY topico
ORDER BY cantidad DESC;

-- 3. Últimos 5 mensajes
SELECT topico, sensor_id, valor_numerico, unidad, timestamp_recepcion
FROM mensajes_mqtt
ORDER BY timestamp_recepcion DESC
LIMIT 5;

-- 4. Mensajes de las últimas 24 horas
SELECT COUNT(*) as mensajes_recientes
FROM mensajes_mqtt
WHERE timestamp_recepcion > NOW() - INTERVAL '24 hours';

-- 5. Promedio de valores por tópico
SELECT topico, 
       AVG(valor_numerico) as promedio,
       MIN(valor_numerico) as minimo,
       MAX(valor_numerico) as maximo
FROM mensajes_mqtt
WHERE valor_numerico IS NOT NULL
GROUP BY topico;
```

### Consultas Avanzadas

```sql
-- 6. Mensajes por hora del día
SELECT 
    EXTRACT(HOUR FROM timestamp_recepcion) as hora,
    COUNT(*) as cantidad
FROM mensajes_mqtt
GROUP BY hora
ORDER BY hora;

-- 7. Sensores más activos
SELECT sensor_id, COUNT(*) as mensajes
FROM mensajes_mqtt
WHERE sensor_id IS NOT NULL
GROUP BY sensor_id
ORDER BY mensajes DESC;

-- 8. Tópicos con más actividad en la última hora
SELECT topico, COUNT(*) as cantidad
FROM mensajes_mqtt
WHERE timestamp_recepcion > NOW() - INTERVAL '1 hour'
GROUP BY topico
ORDER BY cantidad DESC
LIMIT 5;

-- 9. Mensajes de alerta (humo alto)
SELECT *
FROM mensajes_mqtt
WHERE topico = 'incendio/sensor_humo'
  AND valor_numerico > 50
ORDER BY timestamp_recepcion DESC;

-- 10. Tendencia de temperatura
SELECT 
    DATE_TRUNC('minute', timestamp_recepcion) as minuto,
    AVG(valor_numerico) as temp_promedio
FROM mensajes_mqtt
WHERE topico = 'clima/temperatura'
  AND timestamp_recepcion > NOW() - INTERVAL '1 hour'
GROUP BY minuto
ORDER BY minuto DESC
LIMIT 10;
```

### Mantenimiento

```sql
-- Limpiar mensajes antiguos (más de 30 días)
SELECT limpiar_mensajes_antiguos(30);

-- Ver tamaño de la tabla
SELECT pg_size_pretty(pg_total_relation_size('mensajes_mqtt'));

-- Resetear contador de mensajes (CUIDADO!)
-- TRUNCATE TABLE mensajes_mqtt RESTART IDENTITY;
```

---

## 👁️ Monitoreo en Tiempo Real

### Opción 1: Monitoreo MQTT

```bash
# Ver TODOS los mensajes en tiempo real
mosquitto_sub -h localhost -t "#" -v

# Ver solo un tópico específico
mosquitto_sub -h localhost -t "clima/temperatura" -v

# Ver múltiples tópicos
mosquitto_sub -h localhost -t "clima/#" -t "seguridad/#" -v
```

### Opción 2: Monitoreo de Base de Datos

```bash
# Ver conteo de mensajes actualizándose cada segundo
watch -n 1 'sudo -u postgres psql -d mqtt_taller -t -c "SELECT COUNT(*) FROM mensajes_mqtt;"'

# Ver últimos mensajes actualizándose
watch -n 2 'sudo -u postgres psql -d mqtt_taller -c "SELECT topico, valor_numerico, timestamp_recepcion FROM mensajes_mqtt ORDER BY timestamp_recepcion DESC LIMIT 5;"'
```

### Opción 3: Logs del sistema

```bash
# Ver logs del MQTT Broker
sudo docker logs -f mqtt-server

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-17-main.log

# Ver salida del simulador (si está en background)
tail -f /tmp/simulator.log

# Ver salida del suscriptor
tail -f /tmp/subscriber.log
```

---

## ✅ Checklist de Pruebas Completas

### Antes de la demostración, verificar:

- [ ] MQTT Broker responde a ping
- [ ] Puede publicar mensajes
- [ ] Puede suscribirse a tópicos
- [ ] PostgreSQL acepta conexiones
- [ ] Base de datos tiene tablas creadas
- [ ] Simulador se conecta al broker
- [ ] Simulador publica a todos los tópicos (7-8)
- [ ] Suscriptor se conecta al broker
- [ ] Suscriptor se conecta a la base de datos
- [ ] Mensajes se almacenan correctamente
- [ ] Consultas SQL funcionan
- [ ] Sin errores en logs
- [ ] Formato JSON correcto en mensajes
- [ ] Timestamps correctos
- [ ] Valores numéricos razonables

---

## 📞 Información de Contacto

**Profesor:** Héctor Bernal  
**Correo:** hector.bernal@unimilitar.edu.co  
**Institución:** Universidad Militar Nueva Granada

---

**Última actualización:** Octubre 17, 2025  
**Versión:** 1.0  
**Estado:** Pruebas Validadas ✅
