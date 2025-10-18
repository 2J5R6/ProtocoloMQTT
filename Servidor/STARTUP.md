# 🚀 GUÍA DE INICIO DEL SISTEMA MQTT

> **Guía completa paso a paso para iniciar todo el sistema MQTT después de reiniciar el computador**

**Universidad Militar Nueva Granada**  
**Taller de Comunicaciones - Sistema MQTT IoT**

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Verificar Servicios del Sistema](#paso-1-verificar-servicios-del-sistema)
3. [Paso 2: Iniciar MQTT Broker](#paso-2-iniciar-mqtt-broker)
4. [Paso 3: Iniciar PostgreSQL](#paso-3-iniciar-postgresql)
5. [Paso 4: Activar Entorno Python](#paso-4-activar-entorno-python)
6. [Paso 5: Iniciar Simulador de Sensores](#paso-5-iniciar-simulador-de-sensores)
7. [Paso 6: Iniciar Suscriptor Administrativo](#paso-6-iniciar-suscriptor-administrativo)
8. [Paso 7: Verificar Sistema Completo](#paso-7-verificar-sistema-completo)
9. [Comandos Rápidos](#comandos-rápidos)
10. [Solución de Problemas](#solución-de-problemas)

---

## ⚙️ Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ Kali Linux en funcionamiento
- ✅ Docker instalado (para MQTT Broker)
- ✅ PostgreSQL 17+ instalado
- ✅ Python 3.13+ instalado
- ✅ Proyecto clonado en: `/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones`

---

## 📝 Paso 1: Verificar Servicios del Sistema

### 1.1 Abrir Terminal

```bash
# Navegar al directorio del proyecto
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
```

### 1.2 Verificar Docker

```bash
# Verificar que Docker esté ejecutándose
sudo systemctl status docker
```

**Salida esperada:** `Active: active (running)`

Si no está activo:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 1.3 Verificar PostgreSQL

```bash
# Verificar estado de PostgreSQL
sudo systemctl status postgresql
```

**Salida esperada:** `Active: active (exited)`

---

## 🔧 Paso 2: Iniciar MQTT Broker

### 2.1 Verificar si el contenedor ya existe

```bash
sudo docker ps -a | grep mqtt-server
```

### 2.2 Si el contenedor existe pero está detenido

```bash
# Iniciar el contenedor existente
sudo docker start mqtt-server
```

### 2.3 Si el contenedor NO existe

```bash
# Navegar al directorio del broker
cd broker

# Iniciar con Docker Compose
sudo docker-compose up -d

# Volver al directorio principal
cd ..
```

### 2.4 Verificar que el broker está corriendo

```bash
# Ver contenedores en ejecución
sudo docker ps

# Verificar logs del broker
sudo docker logs mqtt-server --tail 20
```

**Salida esperada:** Deberías ver el contenedor `mqtt-server` con estado `Up`

### 2.5 Probar conectividad del broker

```bash
# Publicar mensaje de prueba
mosquitto_pub -h localhost -t "test/startup" -m "Sistema iniciado"
```

**Si funciona:** No habrá salida (esto es normal)

---

## 🗄️ Paso 3: Iniciar PostgreSQL

### 3.1 Iniciar el servicio

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql

# Habilitar inicio automático
sudo systemctl enable postgresql
```

### 3.2 Verificar estado

```bash
sudo systemctl status postgresql
```

**Salida esperada:** `Active: active (exited)` o `Active: active (running)`

### 3.3 Verificar conexión a la base de datos

```bash
# Conectar a la base de datos
sudo -u postgres psql -d mqtt_taller -c "SELECT COUNT(*) FROM mensajes_mqtt;"
```

**Salida esperada:** Un número mostrando la cantidad de mensajes almacenados

---

## 🐍 Paso 4: Activar Entorno Python

### 4.1 Navegar al proyecto (si no estás ahí)

```bash
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
```

### 4.2 Verificar que el entorno virtual existe

```bash
ls -la .venv
```

**Si NO existe el directorio .venv:**
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4.3 Activar el entorno virtual

```bash
source .venv/bin/activate
```

**Indicador:** Tu prompt debería mostrar `(.venv)` al inicio

### 4.4 Verificar paquetes instalados

```bash
pip list
```

**Paquetes requeridos:**
- paho-mqtt (1.6.1)
- psycopg2-binary (2.9.11)
- python-dotenv (1.1.1)

---

## 📡 Paso 5: Iniciar Simulador de Sensores

### 5.1 Abrir una nueva terminal (Terminal 1)

```bash
# Navegar al proyecto
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"

# Activar entorno virtual
source .venv/bin/activate

# Iniciar simulador
python sensores/sensor_simulator.py
```

### 5.2 Salida esperada

```
============================================================
🔬 SIMULADOR DE SENSORES MQTT
   Universidad Militar Nueva Granada
============================================================
📡 Broker: localhost:1883
🆔 Device ID: SIMULATOR_01
⏱️  Intervalo: 5s
============================================================

🔄 Conectando al broker...
✅ Conectado al broker MQTT
📡 Servidor: localhost:1883

✅ Simulador iniciado. Presiona Ctrl+C para detener.
```

### 5.3 Dejar ejecutándose

**No cierres esta terminal.** El simulador debe seguir corriendo para publicar datos.

---

## 💾 Paso 6: Iniciar Suscriptor Administrativo

### 6.1 Abrir OTRA nueva terminal (Terminal 2)

```bash
# Navegar al proyecto
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"

# Activar entorno virtual
source .venv/bin/activate

# Iniciar suscriptor administrativo
python suscriptores/suscriptor_admin.py
```

### 6.2 Salida esperada

```
============================================================
👨‍💼 SUSCRIPTOR ADMINISTRATIVO - BASE DE DATOS
   Universidad Militar Nueva Granada
============================================================
📡 Broker MQTT: localhost:1883
🗄️  Base de datos: mqtt_taller @ localhost
🆔 Client ID: suscriptor_admin
============================================================

🔄 Conectando a base de datos...
✅ Conexión exitosa a PostgreSQL: mqtt_taller
✅ Conectado a PostgreSQL
🔄 Creando cliente MQTT...
🔄 Conectando a broker MQTT...

✅ Suscriptor iniciado. Presiona Ctrl+C para detener.

✅ Conectado al broker MQTT
📡 Servidor: localhost:1883
📥 Suscrito a: # (todos los tópicos)
============================================================
🎧 Escuchando mensajes...
```

### 6.3 Verificar que está guardando mensajes

Deberías ver mensajes como:
```
[21:00:16] 💾 [clima/temperatura] Sensor: SIMULATOR_01 Valor: 25.3 °C | Total: 1
[21:00:16] 💾 [clima/humedad] Sensor: SIMULATOR_01 Valor: 65.0 % | Total: 2
```

---

## ✅ Paso 7: Verificar Sistema Completo

### 7.1 Abrir una tercera terminal (Terminal 3) para monitoreo

```bash
# Navegar al proyecto
cd "/home/daniel/Documents/COMUNICACIONES/taller en kali/taller-comunicaciones"
```

### 7.2 Monitorear mensajes MQTT en tiempo real

```bash
# Suscribirse a todos los tópicos
mosquitto_sub -h localhost -t "#" -v
```

Deberías ver los mensajes JSON llegando cada 5 segundos.

### 7.3 Verificar base de datos

```bash
# Ver total de mensajes
sudo -u postgres psql -d mqtt_taller -c "SELECT COUNT(*) FROM mensajes_mqtt;"

# Ver mensajes por tópico
sudo -u postgres psql -d mqtt_taller -c "SELECT topico, COUNT(*) as cantidad FROM mensajes_mqtt GROUP BY topico ORDER BY cantidad DESC;"

# Ver últimos 5 mensajes
sudo -u postgres psql -d mqtt_taller -c "SELECT topico, sensor_id, valor_numerico, unidad, timestamp_recepcion FROM mensajes_mqtt ORDER BY timestamp_recepcion DESC LIMIT 5;"
```

### 7.4 Estado esperado del sistema

**Terminales abiertas:**
- **Terminal 1:** Simulador de sensores (publicando cada 5s)
- **Terminal 2:** Suscriptor administrativo (guardando en DB)
- **Terminal 3:** Monitoreo opcional

**Servicios corriendo:**
- ✅ Docker (mqtt-server container)
- ✅ PostgreSQL (servicio activo)
- ✅ Simulador (publicando 7-8 sensores)
- ✅ Suscriptor admin (almacenando mensajes)

---

## ⚡ Comandos Rápidos

### Script de Inicio Completo

Puedes copiar y pegar esto en una terminal:

```bash
#!/bin/bash
echo "🚀 Iniciando Sistema MQTT..."

# 1. Iniciar Docker
echo "📦 Iniciando Docker..."
sudo systemctl start docker

# 2. Iniciar contenedor MQTT
echo "📡 Iniciando MQTT Broker..."
sudo docker start mqtt-server

# 3. Iniciar PostgreSQL
echo "🗄️  Iniciando PostgreSQL..."
sudo systemctl start postgresql

# 4. Verificar servicios
echo "✅ Verificando servicios..."
sleep 2

if sudo docker ps | grep -q mqtt-server; then
    echo "✅ MQTT Broker: Running"
else
    echo "❌ MQTT Broker: Failed"
fi

if sudo systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL: Running"
else
    echo "❌ PostgreSQL: Failed"
fi

echo ""
echo "🎉 Servicios base iniciados!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Abrir nueva terminal y ejecutar: source .venv/bin/activate && python sensores/sensor_simulator.py"
echo "   2. Abrir otra terminal y ejecutar: source .venv/bin/activate && python suscriptores/suscriptor_admin.py"
echo ""
```

### Guardar como script ejecutable

```bash
# Crear archivo de script
nano start_mqtt_system.sh

# Pegar el contenido de arriba y guardar (Ctrl+X, Y, Enter)

# Hacer ejecutable
chmod +x start_mqtt_system.sh

# Ejecutar
./start_mqtt_system.sh
```

---

## 🛠️ Solución de Problemas

### Problema 1: MQTT Broker no se inicia

**Síntoma:** `sudo docker start mqtt-server` falla

**Solución:**
```bash
# Ver logs del contenedor
sudo docker logs mqtt-server

# Si el contenedor no existe, crearlo de nuevo
cd broker
sudo docker-compose up -d
cd ..
```

### Problema 2: Puerto 1883 en uso

**Síntoma:** Error "Address already in use"

**Solución:**
```bash
# Ver qué está usando el puerto
sudo netstat -tlnp | grep 1883

# Si es otro proceso, detenerlo o usar el contenedor existente
sudo docker start mqtt-server
```

### Problema 3: PostgreSQL no conecta

**Síntoma:** Error "could not connect to server"

**Solución:**
```bash
# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Verificar que está corriendo
sudo systemctl status postgresql

# Verificar que el usuario existe
sudo -u postgres psql -c "\du"
```

### Problema 4: Entorno Python sin paquetes

**Síntoma:** `ModuleNotFoundError: No module named 'paho'`

**Solución:**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

### Problema 5: No se guardan mensajes en DB

**Síntoma:** El suscriptor no muestra mensajes guardándose

**Verificación:**
```bash
# Verificar conexión a base de datos
source .venv/bin/activate
python -c "from database.db_config import crear_conexion; conn = crear_conexion(); print('✅ Conexión exitosa' if conn else '❌ Error')"

# Verificar que los sensores están publicando
mosquitto_sub -h localhost -t "#" -v
```

### Problema 6: Permisos de base de datos

**Síntoma:** Error "permission denied for table"

**Solución:**
```bash
sudo -u postgres psql -d mqtt_taller <<EOF
GRANT ALL PRIVILEGES ON TABLE mensajes_mqtt TO mqtt_admin;
GRANT USAGE, SELECT ON SEQUENCE mensajes_mqtt_id_seq TO mqtt_admin;
EOF
```

---

## 📊 Verificación Final

### Lista de verificación rápida:

```bash
# 1. ¿Docker corriendo?
sudo systemctl is-active docker && echo "✅ Docker OK" || echo "❌ Docker Failed"

# 2. ¿MQTT Broker activo?
sudo docker ps | grep mqtt-server && echo "✅ MQTT Broker OK" || echo "❌ MQTT Broker Failed"

# 3. ¿PostgreSQL activo?
sudo systemctl is-active postgresql && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL Failed"

# 4. ¿Puedo publicar a MQTT?
mosquitto_pub -h localhost -t "test/check" -m "test" && echo "✅ MQTT Publish OK" || echo "❌ MQTT Publish Failed"

# 5. ¿Base de datos accesible?
sudo -u postgres psql -d mqtt_taller -c "SELECT 1;" > /dev/null 2>&1 && echo "✅ Database OK" || echo "❌ Database Failed"
```

---

## 🎯 Orden Recomendado de Inicio

1. ✅ **Docker** → `sudo systemctl start docker`
2. ✅ **MQTT Broker** → `sudo docker start mqtt-server`
3. ✅ **PostgreSQL** → `sudo systemctl start postgresql`
4. ✅ **Entorno Python** → `source .venv/bin/activate`
5. ✅ **Simulador** → `python sensores/sensor_simulator.py` (Terminal 1)
6. ✅ **Suscriptor Admin** → `python suscriptores/suscriptor_admin.py` (Terminal 2)

---

## 📞 Contacto y Soporte

**Profesor:** Héctor Bernal  
**Correo:** hector.bernal@unimilitar.edu.co  
**Institución:** Universidad Militar Nueva Granada

---

**Última actualización:** Octubre 17, 2025  
**Versión:** 1.0  
**Estado del Sistema:** Completamente Operacional ✅
