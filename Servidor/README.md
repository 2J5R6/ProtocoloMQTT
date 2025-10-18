# Taller: Implementación de un Servidor MQTT con Múltiples Tópicos y Sensores

> **⚡ CONTEXTO PARA IA:** Este README documenta un proyecto de implementación MQTT para la asignatura de Comunicaciones. El sistema incluye un broker Mosquitto en Kali Linux, PostgreSQL como base de datos, ESP32 con 7 sensores, y múltiples suscriptores Python. Estado actual: 44% completado (8/18 tareas). Ver `PROGRESO.md` para detalles del avance.

## 📋 Información del Proyecto

**Asignatura:** Comunicaciones  
**Peso:** 50% del segundo corte  
**Modalidad:** Grupal (mismo grupo de laboratorio) o Individual  
**Presentación:** Presencial tipo Demostración + Informe de implementación  
**Correo de envío:** hector.bernal@unimilitar.edu.co

**🔧 Entorno de Desarrollo:**
- **Servidor:** Kali Linux
- **Base de Datos:** PostgreSQL 15+
- **Microcontrolador:** ESP32-S3
- **Lenguajes:** Python 3.x, C++ (Arduino)

---

## 🎯 Objetivo

Implementar un servidor MQTT con **cinco tópicos** y **al menos siete sensores**. El sistema debe incluir:
- **4 suscriptores temáticos** que reciben datos según su área de interés
- **1 suscriptor administrativo** que almacena todos los mensajes en base de datos
- **Opcional (+0.5):** Conectividad desde Internet con autenticación

---

## 📚 Requisitos Previos

- ✅ Conocimientos básicos de redes y protocolos IoT
- ✅ Experiencia con Linux y línea de comandos
- ✅ Conocimientos básicos de Python
- ✅ **Sistema Operativo:** Kali Linux (servidor)
- ✅ **Base de Datos:** PostgreSQL
- ✅ Mosquitto (broker MQTT)
- ✅ Librería `paho-mqtt` en Python

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     BROKER MQTT (Mosquitto)                  │
│                         Puerto 1883                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬─────────────┬─────────────┐
        │            │            │             │             │
   ┌────▼───┐   ┌───▼────┐  ┌───▼────┐   ┌────▼───┐   ┌─────▼──────┐
   │Tópico 1│   │Tópico 2│  │Tópico 3│   │Tópico 4│   │  Tópico 5  │
   └────┬───┘   └───┬────┘  └───┬────┘   └────┬───┘   └─────┬──────┘
        │           │           │             │             │
   ┌────▼──────────────────────────────────────────────────────┐
   │              PUBLICADORES (Sensores)                       │
   │  - ESP32 con 2+ sensores de distintos tópicos             │
   │  - Mínimo 7 sensores en total                             │
   └────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌───▼────┐           ┌────▼─────┐
   │Suscr. 1 │           │Suscr. 2│           │Suscr. 3  │
   │Temático │           │Temático│           │Temático  │
   └─────────┘           └────────┘           └──────────┘
                              │
                         ┌────▼────┐
                         │Suscr. 4 │
                         │Temático │
                         └────┬────┘
                              │
                    ┌─────────▼──────────┐
                    │  Suscriptor Admin  │
                    │   (Todos los       │
                    │    tópicos)        │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   BASE DE DATOS    │
                    │   (PostgreSQL/     │
                    │    MongoDB)        │
                    └────────────────────┘
```

---

## 📝 Estructura del Proyecto

> **📊 ESTADO DE ARCHIVOS:** ✅ Completado | 🔄 En progreso | ⏳ Pendiente

```
taller comunicaciones/
├── ✅ README.md                          # Este archivo (Documentación principal)
├── ✅ PROGRESO.md                        # Estado detallado del proyecto
├── ✅ .env.example                       # Plantilla de variables de entorno
├── ✅ requirements.txt                   # Dependencias Python
├── 📄 Corte2_50porciento_TallerMQTT.docx # Documento original del taller
│
├── broker/                               # ✅ Configuración del servidor MQTT
│   ├── ✅ docker-compose.yml            # Docker para Mosquitto en Kali Linux
│   ├── ✅ mosquitto.conf                # Configuración completa del broker
│   ├── ⏳ data/                         # Datos persistentes (creado en runtime)
│   ├── ⏳ log/                          # Logs del broker (creado en runtime)
│   └── ⏳ passwd                        # Archivo de usuarios (Bonus +0.5)
│
├── sensores/                             # ✅ Publicadores (ESP32)
│   ├── ✅ esp32_sensores.ino            # Código Arduino completo (7 sensores)
│   └── ✅ sensor_simulator.py           # Simulador Python completo
│
├── suscriptores/                         # 🔄 Clientes MQTT (1/5 completados)
│   ├── 🔄 suscriptor_1_tematico.py      # Bomberos (incendio/#) - En progreso
│   ├── ⏳ suscriptor_2_tematico.py      # Vigilancia (seguridad/#, clima/#)
│   ├── ⏳ suscriptor_3_tematico.py      # Profesor (iluminacion/#, clima/#)
│   ├── ⏳ suscriptor_4_tematico.py      # Policía (seguridad/#, incendio/#)
│   └── ✅ suscriptor_admin.py           # Suscriptor administrativo (DB) COMPLETO
│
├── database/                             # ✅ Base de datos PostgreSQL
│   ├── ✅ schema.sql                    # Esquema completo con vistas e índices
│   └── ✅ db_config.py                  # Módulo de conexión con funciones auxiliares
│
└── docs/                                 # ⏳ Documentación técnica
    ├── ⏳ INSTALACION.md                # Guía de instalación paso a paso
    ├── ⏳ CONFIGURACION.md              # Guía de configuración del sistema
    └── ⏳ PRUEBAS.md                    # Casos de prueba y validación
```

**📈 Progreso Global:** 44% completado (8/18 tareas)  
**🎯 Próximo objetivo:** Completar los 4 suscriptores temáticos

---

## 🔧 Componentes del Sistema

### 1. Servidor MQTT (Broker)

**Plataforma:** Kali Linux  
**Instalación:** Mosquitto nativo o contenedor Docker

#### Opción A: Instalación Nativa en Kali Linux
```bash
# Actualizar repositorios
sudo apt update

# Instalar Mosquitto broker y cliente
sudo apt install mosquitto mosquitto-clients -y

# Habilitar servicio en inicio
sudo systemctl enable mosquitto

# Iniciar servicio
sudo systemctl start mosquitto

# Verificar estado
sudo systemctl status mosquitto
```

#### Opción B: Docker en Kali Linux
```bash
# Instalar Docker (si no está instalado)
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

**Configuración (`/etc/mosquitto/conf.d/mqtt.conf`):**
```conf
listener 1883
allow_anonymous true
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
log_type all
```

**Opcional - Seguridad:**
```conf
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

**Reiniciar servicio después de cambios:**
```bash
sudo systemctl restart mosquitto
```

---

### 2. Tópicos MQTT

#### Opción 1: Sensores Ambientales
| Sensor | Tópico MQTT |
|--------|-------------|
| Temperatura | `sensores/temperatura` |
| Humedad | `sensores/humedad` |
| Luz | `sensores/luz` |
| Presión | `sensores/presion` |
| Movimiento | `sensores/movimiento` |

#### Opción 2: Sistema de Seguridad (Ejemplo de Clase)
| Sensor | Tópico MQTT |
|--------|-------------|
| Sensor de humo | `incendio/sensor_humo` |
| Alarma manual | `incendio/alarma` |
| Estado de puerta | `seguridad/puerta` |
| Temperatura | `clima/temperatura` |
| Viento | `clima/viento` |
| Luz solar | `iluminacion/luz` |
| Activación sirena | `incendio/activar_sirena` |

---

### 3. Publicadores (Sensores)

**Requisitos:**
- Mínimo **7 sensores** en total
- Al menos **2 sensores** de distintos tópicos en un **ESP32**
- Publicación periódica de datos en formato JSON

**Ejemplo de mensaje:**
```json
{
  "sensor_id": "ESP32_01",
  "tipo": "temperatura",
  "valor": 25.3,
  "unidad": "°C",
  "timestamp": "2025-10-16T14:30:00Z"
}
```

---

### 4. Suscriptores Temáticos

#### Ejemplo 1: Sensores Ambientales
- **Suscriptor 1:** Sensores Ambientales (`sensores/temperatura`, `sensores/humedad`)
- **Suscriptor 2:** Iluminación (`sensores/luz`)
- **Suscriptor 3:** Presión (`sensores/presion`)
- **Suscriptor 4:** Movimiento (`sensores/movimiento`)

#### Ejemplo 2: Sistema de Seguridad
- **Suscriptor 1 (Bomberos):** Suscrito a `incendio/#`
- **Suscriptor 2 (Vigilancia UMNG):** Suscrito a `seguridad/#`, `clima/#`
- **Suscriptor 3 (Profesor):** Suscrito a `iluminacion/#`, `clima/#`
- **Suscriptor 4 (Policía):** Suscrito a `seguridad/#`, `incendio/#`

---

### 5. Suscriptor Administrativo

**Función:** Suscrito a **todos los tópicos** (`#`) para almacenar en base de datos

**Características:**
- Conexión permanente al broker
- Almacenamiento automático de todos los mensajes
- Registro de timestamp de recepción

---

### 6. Base de Datos PostgreSQL

**Plataforma:** Kali Linux  
**Motor:** PostgreSQL 15+

#### Instalación en Kali Linux
```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar instalación
sudo systemctl status postgresql
```

#### Configuración Inicial
```bash
# Acceder como usuario postgres
sudo -u postgres psql

# Crear base de datos
CREATE DATABASE mqtt_taller;

# Crear usuario
CREATE USER mqtt_admin WITH PASSWORD 'mqtt_secure_2025';

# Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE mqtt_taller TO mqtt_admin;

# Salir
\q
```

#### Esquema de Tabla `mensajes_mqtt`

```sql
-- Conectar a la base de datos
\c mqtt_taller

-- Crear tabla
CREATE TABLE mensajes_mqtt (
    id SERIAL PRIMARY KEY,
    topico VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    timestamp_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(100),
    valor_numerico DECIMAL(10,2),
    unidad VARCHAR(20)
);

-- Crear índices para optimizar consultas
CREATE INDEX idx_topico ON mensajes_mqtt(topico);
CREATE INDEX idx_timestamp ON mensajes_mqtt(timestamp_recepcion);
CREATE INDEX idx_sensor_id ON mensajes_mqtt(sensor_id);

-- Dar permisos al usuario
GRANT ALL PRIVILEGES ON TABLE mensajes_mqtt TO mqtt_admin;
GRANT USAGE, SELECT ON SEQUENCE mensajes_mqtt_id_seq TO mqtt_admin;
```

#### Configuración de Acceso Remoto (Opcional)
```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf
# Cambiar: listen_addresses = '*'

# Editar pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Agregar: host all all 0.0.0.0/0 md5

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

---

## 🚀 Pasos de Implementación

### Fase 1: Instalación del Servidor MQTT (Kali Linux)
1. ✅ Actualizar sistema: `sudo apt update && sudo apt upgrade -y`
2. ✅ Instalar Mosquitto: `sudo apt install mosquitto mosquitto-clients -y`
3. ✅ Configurar `/etc/mosquitto/conf.d/mqtt.conf`
4. ✅ Iniciar servicio: `sudo systemctl start mosquitto`
5. ✅ Verificar con `mosquitto_sub -h localhost -t test`
6. ✅ Configurar firewall: `sudo ufw allow 1883/tcp`

### Fase 2: Configuración de Sensores
1. ✅ Programar ESP32 con librerías MQTT
2. ✅ Configurar WiFi y conexión al broker
3. ✅ Implementar lectura de sensores
4. ✅ Publicar datos en formato JSON
5. ✅ Probar publicación con `mosquitto_sub`

### Fase 3: Implementación de Suscriptores
1. ✅ Crear scripts Python para suscriptores temáticos
2. ✅ Configurar filtros de tópicos
3. ✅ Implementar lógica de procesamiento
4. ✅ Probar recepción de mensajes

### Fase 4: Base de Datos PostgreSQL
1. ✅ Instalar PostgreSQL: `sudo apt install postgresql postgresql-contrib -y`
2. ✅ Crear base de datos `mqtt_taller`
3. ✅ Crear usuario `mqtt_admin` con contraseña
4. ✅ Ejecutar script de esquema `schema.sql`
5. ✅ Implementar suscriptor administrativo con `psycopg2`
6. ✅ Configurar almacenamiento automático
7. ✅ Verificar inserción con consultas SQL

### Fase 5: Pruebas Integrales
1. ✅ Verificar flujo completo de mensajes
2. ✅ Comprobar almacenamiento en BD
3. ✅ Validar funcionamiento de suscriptores
4. ✅ Documentar resultados

### Fase 6 (Opcional): Conectividad Internet
1. ✅ Configurar puerto forwarding en router
2. ✅ Obtener IP pública o usar servicio DDNS
3. ✅ Habilitar autenticación en Mosquitto
4. ✅ Crear usuarios con `mosquitto_passwd`
5. ✅ Probar conexión desde red externa
6. ✅ Compartir credenciales en grupo

---

## 📦 Dependencias Python

### En Kali Linux (Servidor)
```bash
# Instalar pip si no está disponible
sudo apt install python3-pip -y

# Instalar dependencias del sistema para psycopg2
sudo apt install libpq-dev python3-dev -y

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar librerías
pip install paho-mqtt==1.6.1
pip install psycopg2-binary==2.9.9
pip install python-dotenv==1.0.0
```

### En Windows (Cliente ESP32/Desarrollo)
```powershell
pip install -r requirements.txt
```

**requirements.txt:**
```txt
paho-mqtt==1.6.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

---

## 🧪 Pruebas y Validación

### Test 1: Verificar Mosquitto en Kali Linux
```bash
# Verificar servicio
sudo systemctl status mosquitto

# Ver logs en tiempo real
sudo tail -f /var/log/mosquitto/mosquitto.log

# Probar suscripción local
mosquitto_sub -h localhost -t "test" -v
```

### Test 2: Publicación Manual
```bash
# Desde Kali Linux
mosquitto_pub -h localhost -t "sensores/temperatura" -m '{"valor":25.5,"unidad":"C"}'

# Desde otra máquina (usar IP de Kali)
mosquitto_pub -h 192.168.X.X -t "sensores/temperatura" -m '{"valor":25.5,"unidad":"C"}'
```

### Test 3: Suscripción Manual
```bash
# Suscribirse a todos los tópicos
mosquitto_sub -h localhost -t "#" -v

# Suscribirse a tópicos específicos
mosquitto_sub -h localhost -t "sensores/#" -v
```

### Test 4: Verificar PostgreSQL
```bash
# Conectar a la base de datos
sudo -u postgres psql -d mqtt_taller

# Consultas SQL
```
```sql
-- Ver todos los mensajes
SELECT * FROM mensajes_mqtt ORDER BY timestamp_recepcion DESC LIMIT 10;

-- Estadísticas por tópico
SELECT topico, COUNT(*) as total_mensajes, MAX(timestamp_recepcion) as ultimo_mensaje
FROM mensajes_mqtt
GROUP BY topico
ORDER BY total_mensajes DESC;

-- Mensajes de las últimas 24 horas
SELECT topico, COUNT(*) as cantidad
FROM mensajes_mqtt
WHERE timestamp_recepcion > NOW() - INTERVAL '24 hours'
GROUP BY topico;
```

### Test 5: Verificar Conectividad de Red
```bash
# En Kali Linux - Obtener IP
ip addr show

# Verificar puerto abierto
sudo netstat -tulpn | grep 1883

# Probar desde otra máquina
ping IP_KALI_LINUX
telnet IP_KALI_LINUX 1883
```

---

## 🌐 Conectividad desde Internet (Opcional +0.5)

### Requisitos:
1. **IP Pública:** Obtener del proveedor o usar servicio DDNS (No-IP, DuckDNS)
2. **Port Forwarding:** Redirigir puerto 1883 en router al servidor
3. **Autenticación:** Crear usuarios con contraseñas seguras
4. **Firewall:** Configurar reglas de seguridad

### Configuración de Usuarios en Kali Linux:
```bash
# Crear directorio si no existe
sudo mkdir -p /etc/mosquitto

# Crear archivo de contraseñas
sudo mosquitto_passwd -c /etc/mosquitto/passwd usuario1
# Ingresar contraseña cuando lo solicite

# Agregar más usuarios (sin -c para no sobreescribir)
sudo mosquitto_passwd /etc/mosquitto/passwd usuario2

# Actualizar /etc/mosquitto/conf.d/mqtt.conf
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd

# Reiniciar servicio
sudo systemctl restart mosquitto
```

### Conexión Externa:
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.username_pw_set("usuario1", "password123")
client.connect("IP_PUBLICA", 1883, 60)
client.subscribe("sensores/#")
```

### Información a Compartir:
- 📍 **IP Pública:** `XX.XX.XX.XX`
- 🔌 **Puerto:** `1883`
- 📂 **Tópicos disponibles:** `sensores/#`, `incendio/#`, etc.
- 👤 **Usuario:** `estudiante_umng`
- 🔑 **Contraseña:** `SecurePass2025!`

---

## 📊 Entregables

### 1. Demostración Presencial
- ✅ Sistema funcionando en tiempo real
- ✅ Mostrar publicadores (ESP32)
- ✅ Demostrar suscriptores temáticos
- ✅ Verificar almacenamiento en BD
- ✅ (Opcional) Conexión desde Internet

### 2. Informe de Implementación
**Contenido mínimo:**
1. Portada con integrantes
2. Objetivo del proyecto
3. Arquitectura del sistema (diagrama)
4. Configuración del broker MQTT
5. Descripción de sensores y tópicos
6. Implementación de suscriptores
7. Diseño de base de datos
8. Resultados y pruebas
9. Código fuente (anexos o repositorio GitHub)
10. Conclusiones y recomendaciones

**Formato:** PDF  
**Envío:** hector.bernal@unimilitar.edu.co

---

## 🛠️ Tecnologías Utilizadas

- **Sistema Operativo:** Kali Linux (Servidor)
- **Broker MQTT:** Eclipse Mosquitto
- **Base de Datos:** PostgreSQL 15+
- **Microcontrolador:** ESP32
- **Lenguaje:** Python 3.x, C++ (Arduino)
- **Librerías Python:** paho-mqtt, psycopg2-binary, python-dotenv
- **Opcional:** Docker (para virtualización)

---

## 📖 Referencias

- [Eclipse Mosquitto Documentation](https://mosquitto.org/documentation/)
- [Paho MQTT Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [MQTT Protocol Specification](https://mqtt.org/mqtt-specification/)
- [ESP32 MQTT Examples](https://github.com/espressif/esp-idf/tree/master/examples/protocols/mqtt)

---

## 👥 Equipo de Desarrollo

**Integrantes:**
- [ ] Nombre 1
- [ ] Nombre 2
- [ ] Nombre 3

**Fecha de inicio:** Octubre 16, 2025  
**Fecha de entrega:** _______________

---

## 🤖 INFORMACIÓN PARA ASISTENTE IA

### Estado Actual del Proyecto
**Última actualización:** 2025-10-16  
**Progreso:** 44% (8/18 tareas completadas)

### Archivos Completados y Listos para Usar
1. ✅ **Infraestructura Base**
   - `broker/docker-compose.yml` - Mosquitto listo para Kali Linux
   - `broker/mosquitto.conf` - Configuración completa con persistencia y logs
   - `database/schema.sql` - Schema PostgreSQL con tablas, vistas, índices
   - `database/db_config.py` - Módulo Python de conexión a PostgreSQL
   - `requirements.txt` - Todas las dependencias Python necesarias

2. ✅ **Publicadores (Sensores)**
   - `sensores/esp32_sensores.ino` - 7 sensores completos en ESP32:
     * DHT11 (Temperatura + Humedad) → `clima/temperatura`, `clima/humedad`
     * MQ-2 (Humo) → `incendio/sensor_humo`
     * LDR (Luz) → `iluminacion/luz`
     * PIR (Movimiento) → `seguridad/movimiento`
     * Reed Switch (Puerta) → `seguridad/puerta`
     * Botón Alarma → `incendio/alarma`
   - `sensores/sensor_simulator.py` - Simulador completo para pruebas sin hardware

3. ✅ **Suscriptor Administrativo**
   - `suscriptores/suscriptor_admin.py` - COMPLETO y funcional
     * Suscrito a todos los tópicos (#)
     * Almacena en PostgreSQL automáticamente
     * Manejo de errores y reconexión
     * Estadísticas en tiempo real

### Tareas Pendientes (Prioridad Alta)
1. 🔄 **Suscriptores Temáticos (3 restantes)**
   - `suscriptor_2_tematico.py` - Vigilancia UMNG (seguridad/# + clima/#)
   - `suscriptor_3_tematico.py` - Profesor (iluminacion/# + clima/#)
   - `suscriptor_4_tematico.py` - Policía (seguridad/# + incendio/#)

2. ⏳ **Documentación Técnica**
   - `docs/INSTALACION.md` - Comandos para Kali Linux + PostgreSQL
   - `docs/CONFIGURACION.md` - Variables de entorno y parámetros
   - `docs/PRUEBAS.md` - Casos de prueba y validación

### Estructura de Tópicos Implementada
```
incendio/
├── sensor_humo       (MQ-2 en ESP32)
└── alarma            (Botón en ESP32)

seguridad/
├── puerta            (Reed Switch en ESP32)
└── movimiento        (PIR en ESP32)

clima/
├── temperatura       (DHT11 en ESP32)
├── humedad           (DHT11 en ESP32)
└── viento            (Solo en simulador)

iluminacion/
└── luz               (LDR en ESP32)

sistema/
└── estado            (Estado del ESP32)
```

### Configuración Requerida Antes de Ejecutar

1. **En Kali Linux:**
```bash
# Instalar Mosquitto
sudo apt install mosquitto mosquitto-clients -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE mqtt_taller;
CREATE USER mqtt_admin WITH PASSWORD 'mqtt_secure_2025';
GRANT ALL PRIVILEGES ON DATABASE mqtt_taller TO mqtt_admin;
\c mqtt_taller
\i database/schema.sql
```

2. **Crear archivo .env** (basado en .env.example):
```bash
cp .env.example .env
# Editar .env con la IP del servidor Kali
```

3. **Instalar dependencias Python:**
```bash
pip install -r requirements.txt
```

### Comandos de Prueba Rápida

```bash
# Terminal 1: Iniciar simulador
python sensores/sensor_simulator.py

# Terminal 2: Iniciar suscriptor admin
python suscriptores/suscriptor_admin.py

# Terminal 3: Monitorear mensajes
mosquitto_sub -h localhost -t "#" -v

# Terminal 4: Verificar base de datos
psql -U mqtt_admin -d mqtt_taller -c "SELECT topico, COUNT(*) FROM mensajes_mqtt GROUP BY topico;"
```

### Notas Importantes para IA
- El sistema usa **formato JSON** para todos los mensajes MQTT
- Cada mensaje incluye: `sensor_id`, `tipo`, `valor`, `unidad`, `timestamp`
- Los sensores digitales también incluyen campo `estado` (ej: "abierta", "cerrada")
- La base de datos almacena **timestamp de recepción** automáticamente
- El ESP32 publica cada 5 segundos, el simulador también
- Todos los scripts Python usan **variables de entorno** (.env)

---

## 📝 Notas Importantes

⚠️ **Recordatorios:**
- Mínimo 7 sensores en total
- Al menos 2 sensores de distintos tópicos en un ESP32
- 4 suscriptores temáticos + 1 administrativo
- Base de datos con timestamp de recepción
- Demostración presencial obligatoria

✨ **Bonus (+0.5):**
- Conectividad desde Internet con autenticación
- Compartir IP, tópicos y credenciales en grupo

---

## 📞 Contacto

**Profesor:** Héctor Bernal  
**Correo:** hector.bernal@unimilitar.edu.co  
**Institución:** Universidad Militar Nueva Granada

---

**Última actualización:** Octubre 16, 2025  
**Progreso:** 44% completado (8/18 tareas)  
**Ver:** `PROGRESO.md` para estado detallado del proyecto
