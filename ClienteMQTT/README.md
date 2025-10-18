# 🔌 Cliente MQTT - Universidad Militar Nueva Granada

## 📋 Descripción del Proyecto

Este proyecto implementa un **cliente MQTT** que se conecta a un servidor MQTT remoto para recibir datos de sensores y almacenarlos automáticamente en una base de datos PostgreSQL local.

### 🎯 Objetivos Cumplidos

✅ **4.1 Suscriptor administrativo** que se suscribe a todos los tópicos y almacena mensajes en base de datos  
✅ **4.2 Instalación y configuración** de base de datos PostgreSQL con tabla de mensajes y timestamp  
✅ **4.3 Script Python** constantemente conectado que almacena mensajes de todos los tópicos  

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│          SERVIDOR MQTT (Remoto)             │
│         5 Tópicos + 7 Sensores              │
└─────────────────┬───────────────────────────┘
                  │ Internet/Red Local
                  │
┌─────────────────▼───────────────────────────┐
│           CLIENTE MQTT (Local)              │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │     Suscriptor Administrativo       │    │
│  │   - Suscrito a todos los tópicos    │    │
│  │   - Procesa mensajes JSON           │    │
│  │   - Manejo de reconexión            │    │
│  └─────────────┬───────────────────────┘    │
│                │                            │
│  ┌─────────────▼───────────────────────┐    │
│  │      Base de Datos PostgreSQL      │    │
│  │   - Tabla: mensajes_mqtt            │    │
│  │   - Timestamp automático            │    │
│  │   - Índices optimizados             │    │
│  │   - Vistas para análisis            │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
ClienteMQTT/
├── 📄 README.md                    # Esta documentación
├── 📄 requirements.txt             # Dependencias Python
├── 📄 .env.example                 # Plantilla de configuración
├── 📄 .gitignore                   # Archivos a ignorar
├── 📄 setup_inicial.py             # Configuración automática
├── 📄 consultar_datos.py           # Herramientas de consulta
│
├── suscriptor/                     # Scripts del cliente MQTT
│   └── 📄 suscriptor_admin.py      # Suscriptor administrativo principal
│
├── database/                       # Configuración de base de datos
│   ├── 📄 db_config.py             # Módulo de conexión PostgreSQL
│   └── 📄 schema.sql               # Esquema completo de BD
│
└── config/                         # Archivos de configuración
    └── (archivos de configuración adicionales)
```

---

## 🚀 Instalación y Configuración

### 1️⃣ Prerrequisitos

#### **PostgreSQL**
```bash
# Windows: Descargar desde https://www.postgresql.org/download/windows/
# Linux: 
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### **Python 3.7+**
```bash
# Verificar versión
python --version
```

### 2️⃣ Instalación de Dependencias

```bash
# Navegar a la carpeta del proyecto
cd ClienteMQTT

# Instalar dependencias Python
pip install -r requirements.txt
```

### 3️⃣ Configuración Automática

```bash
# Ejecutar script de configuración inicial
python setup_inicial.py
```

Este script:
- ✅ Verifica PostgreSQL
- ✅ Crea la base de datos `SensoresMQTT`
- ✅ Crea el esquema de tablas
- ✅ Genera archivo `.env` con configuración
- ✅ Verifica conectividad MQTT

### 4️⃣ Configuración Manual (si es necesario)

#### **Crear archivo .env**
```bash
# Copiar plantilla
cp .env.example .env

# Editar configuración
nano .env
```

#### **Configuración .env**
```bash
# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=SensoresMQTT
DB_USER=postgres
DB_PASSWORD=2324Julibolt

# Servidor MQTT (CAMBIAR POR IP REAL)
MQTT_BROKER=192.168.1.100
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Cliente
CLIENT_ID=cliente_admin_umng
```

⚠️ **IMPORTANTE**: Cambiar `MQTT_BROKER` por la IP real del servidor donde está ejecutándose el broker MQTT.

---

## 🎮 Uso del Sistema

### 🔌 Iniciar el Suscriptor Administrativo

```bash
# Ejecutar suscriptor que almacena todos los mensajes
python suscriptor/suscriptor_admin.py
```

**Salida esperada:**
```
============================================================
🔌 CLIENTE MQTT - SUSCRIPTOR ADMINISTRATIVO
   Universidad Militar Nueva Granada
============================================================
📡 Servidor MQTT: 192.168.1.100:1883
🗄️  Base de datos: SensoresMQTT @ localhost
🆔 Client ID: cliente_admin_umng
============================================================

🔄 Conectando a PostgreSQL...
✅ Conectado a PostgreSQL
🗄️  Base de datos: SensoresMQTT @ localhost
🔄 Conectando al servidor MQTT 192.168.1.100:1883...
✅ Conectado al servidor MQTT
📡 Servidor: 192.168.1.100:1883
📥 Suscrito a: # (todos los tópicos)
============================================================
🎧 Escuchando mensajes del servidor...

[14:30:15] 💾 [incendio/sensor_humo] Sensor: ESP32_01 Valor: 245.0  | Total: 1
[14:30:20] 💾 [clima/temperatura] Sensor: ESP32_01 Valor: 25.3 °C | Total: 2
[14:30:25] 💾 [seguridad/puerta] Sensor: ESP32_01 Valor: 1.0  | Total: 3
```

### 🔍 Consultar Datos Almacenados

```bash
# Ejecutar herramienta de consulta
python consultar_datos.py
```

**Menú de opciones:**
```
============================================================
🔍 CONSULTA DE DATOS MQTT
============================================================
1. 📋 Ver últimos mensajes
2. 📊 Estadísticas generales
3. 📂 Estadísticas por tópico
4. 🔍 Buscar por tópico
5. 📡 Buscar por sensor
6. ⏰ Estadísticas por tiempo
7. 💾 Exportar datos a CSV
8. 🔄 Actualizar vista
0. ❌ Salir
============================================================
```

---

## 📊 Base de Datos

### 🗄️ Esquema Principal

#### **Tabla: mensajes_mqtt**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | SERIAL | ID autoincremental (clave primaria) |
| `topico` | VARCHAR(255) | Tópico MQTT del mensaje |
| `mensaje` | TEXT | Contenido completo del mensaje (JSON) |
| `timestamp_llegada` | TIMESTAMP | **Timestamp de llegada automático** |
| `sensor_id` | VARCHAR(100) | ID del sensor que envió el mensaje |
| `valor_numerico` | DECIMAL(10,2) | Valor numérico extraído |
| `unidad` | VARCHAR(20) | Unidad de medida |
| `ip_servidor` | INET | IP del servidor MQTT |

### 📈 Vistas Creadas

- **`mensajes_recientes`**: Mensajes de las últimas 24 horas
- **`estadisticas_topicos`**: Estadísticas agrupadas por tópico
- **`actividad_sensores`**: Actividad por sensor

### 🔍 Consultas Útiles

```sql
-- Ver últimos 10 mensajes
SELECT * FROM mensajes_mqtt ORDER BY timestamp_llegada DESC LIMIT 10;

-- Estadísticas por tópico
SELECT * FROM estadisticas_topicos;

-- Mensajes recientes
SELECT * FROM mensajes_recientes;

-- Mensajes de un sensor específico
SELECT * FROM mensajes_mqtt WHERE sensor_id = 'ESP32_01';
```

---

## 🔧 Funcionalidades Técnicas

### 🔌 Suscriptor Administrativo

- **Conexión MQTT**: Se conecta al servidor remoto
- **Suscripción universal**: Suscrito a `#` (todos los tópicos)
- **Procesamiento JSON**: Extrae datos estructurados de mensajes
- **Almacenamiento automático**: Guarda en PostgreSQL con timestamp
- **Reconexión automática**: Maneja desconexiones de red
- **Estadísticas en tiempo real**: Muestra progreso de mensajes

### 🗄️ Base de Datos

- **PostgreSQL**: Motor de base de datos robusto
- **Timestamp automático**: Cada mensaje tiene timestamp de llegada
- **Índices optimizados**: Consultas rápidas por tópico, sensor y tiempo
- **Vistas analíticas**: Estadísticas precalculadas
- **Funciones de mantenimiento**: Limpieza automática de datos antiguos

### 🔍 Herramientas de Consulta

- **Menú interactivo**: Interfaz de línea de comandos amigable
- **Consultas dinámicas**: Búsqueda por tópico, sensor y tiempo
- **Exportación CSV**: Datos exportables para análisis externo
- **Estadísticas en tiempo real**: Resúmenes y análisis de datos

---

## 🎯 Tópicos Esperados del Servidor

Basándose en el análisis del código del servidor, estos son los tópicos que el cliente puede recibir:

### 🔥 Incendio
- `incendio/sensor_humo` - Datos del sensor MQ-2
- `incendio/alarma` - Activación manual de alarma

### 🔒 Seguridad
- `seguridad/puerta` - Estado de puerta (Reed Switch)
- `seguridad/movimiento` - Detección de movimiento (PIR)

### 🌡️ Clima
- `clima/temperatura` - Temperatura (DHT11)
- `clima/humedad` - Humedad (DHT11)
- `clima/viento` - Velocidad del viento (simulado)

### 💡 Iluminación
- `iluminacion/luz` - Nivel de luz (LDR)

### ⚙️ Sistema
- `sistema/estado` - Estado del ESP32

---

## 🚨 Solución de Problemas

### ❌ Error de Conexión PostgreSQL

```bash
# Verificar que PostgreSQL esté funcionando
# Windows:
net start postgresql-x64-15

# Linux:
sudo systemctl start postgresql
sudo systemctl status postgresql
```

**Verificar credenciales:**
```bash
# Conectar manualmente
psql -U postgres -d SensoresMQTT
```

### ❌ Error de Conexión MQTT

1. **Verificar IP del servidor**:
   ```bash
   ping 192.168.1.100
   ```

2. **Verificar puerto MQTT**:
   ```bash
   telnet 192.168.1.100 1883
   ```

3. **Editar archivo .env**:
   ```bash
   nano .env
   # Cambiar MQTT_BROKER por IP correcta
   ```

### ❌ Dependencias Python Faltantes

```bash
# Reinstalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Si persisten errores en Windows
pip install psycopg2-binary --force-reinstall
```

---

## 📋 Lista de Verificación

### ✅ Instalación Completa

- [ ] PostgreSQL instalado y funcionando
- [ ] Python 3.7+ instalado
- [ ] Dependencias Python instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos `SensoresMQTT` creada
- [ ] Archivo `.env` configurado con IP del servidor MQTT
- [ ] Conectividad de red al servidor MQTT

### ✅ Funcionamiento

- [ ] `python setup_inicial.py` ejecutado exitosamente
- [ ] `python suscriptor/suscriptor_admin.py` se conecta al servidor
- [ ] Mensajes aparecen en tiempo real
- [ ] `python consultar_datos.py` muestra datos almacenados
- [ ] Estadísticas de base de datos son coherentes

---

## 🔐 Credenciales del Sistema

### PostgreSQL
- **Usuario**: `postgres`
- **Contraseña**: `2324Julibolt`
- **Base de datos**: `SensoresMQTT`
- **Host**: `localhost`
- **Puerto**: `5432`

### MQTT (Configurar según servidor)
- **Broker**: `[IP_DEL_SERVIDOR]` (cambiar en .env)
- **Puerto**: `1883`
- **Usuario**: (opcional)
- **Contraseña**: (opcional)

---

## 📞 Soporte y Contacto

**Proyecto**: Taller Comunicaciones - Corte II (50%)  
**Institución**: Universidad Militar Nueva Granada  
**Asignatura**: Comunicaciones  

### 🐛 Reportar Problemas

Si encuentras algún error:

1. Verificar la **lista de verificación** anterior
2. Revisar los **logs** del suscriptor
3. Verificar **conectividad** a PostgreSQL y MQTT
4. Consultar la sección de **solución de problemas**

---

## 📝 Notas Técnicas

### 🔄 Flujo de Datos

1. **ESP32/Sensores** → **Broker MQTT** (en servidor remoto)
2. **Cliente MQTT** → **Suscripción** a todos los tópicos (#)
3. **Procesamiento** → **Extracción** de datos JSON
4. **PostgreSQL** → **Almacenamiento** con timestamp automático
5. **Consultas** → **Análisis** y exportación de datos

### 🎯 Características Clave

- ✅ **Suscripción universal**: Recibe TODOS los mensajes de TODOS los tópicos
- ✅ **Timestamp automático**: Cada mensaje incluye momento exacto de llegada
- ✅ **Reconexión automática**: Maneja interrupciones de red
- ✅ **Procesamiento inteligente**: Extrae datos estructurados de JSON
- ✅ **Almacenamiento optimizado**: Índices para consultas rápidas
- ✅ **Herramientas de análisis**: Consultas y exportación de datos

### 💡 Extensiones Futuras

- 📊 Dashboard web en tiempo real
- 📱 Notificaciones móviles por alertas
- 📈 Gráficos y visualizaciones avanzadas
- 🔔 Sistema de alertas por umbrales
- 📤 API REST para acceso a datos

---

**✨ ¡Sistema listo para recibir y almacenar datos del servidor MQTT!**