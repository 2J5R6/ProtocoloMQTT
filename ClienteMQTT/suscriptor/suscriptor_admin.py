"""
============================================
SUSCRIPTOR ADMINISTRATIVO CLIENTE MQTT
Universidad Militar Nueva Granada
============================================

Este script se conecta al servidor MQTT remoto y almacena
todos los mensajes recibidos en la base de datos PostgreSQL local.

Funcionalidades principales:
- Conexión al servidor MQTT remoto
- Suscripción a todos los tópicos (#)
- Almacenamiento automático en PostgreSQL
- Procesamiento de mensajes JSON
- Manejo de reconexión automática
- Registro de estadísticas en tiempo real

Configuración requerida:
- Archivo .env con credenciales de BD y servidor MQTT
- PostgreSQL instalado con base de datos "SensoresMQTT"
- Conectividad de red al servidor MQTT

Uso:
    python suscriptor_admin.py
"""

import paho.mqtt.client as mqtt
import json
import psycopg2
from datetime import datetime
import os
import sys
import time
import signal
from dotenv import load_dotenv

# Agregar path para importar módulos locales
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_config import crear_conexion, DB_CONFIG

# Cargar variables de entorno
load_dotenv()

# ============================================
# CONFIGURACIÓN MQTT
# ============================================
MQTT_BROKER = os.getenv('MQTT_BROKER', '192.168.1.100')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
CLIENT_ID = os.getenv('CLIENT_ID', 'cliente_admin_umng')

# Suscripción a todos los tópicos
TOPIC_ALL = "#"

# ============================================
# VARIABLES GLOBALES DE ESTADO
# ============================================
db_connection = None
mqtt_client = None
mensaje_count = 0
error_count = 0
running = True
conectado_mqtt = False

# Estadísticas por tópico
topicos_stats = {}

# ============================================
# FUNCIONES DE BASE DE DATOS
# ============================================

def conectar_postgresql():
    """
    Establece conexión con PostgreSQL
    
    Returns:
        bool: True si la conexión es exitosa
    """
    global db_connection
    try:
        db_connection = crear_conexion()
        if db_connection:
            print("✅ Conectado a PostgreSQL")
            print(f"🗄️  Base de datos: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
            return True
        else:
            print("❌ Error al conectar con PostgreSQL")
            return False
    except Exception as e:
        print(f"❌ Error de conexión PostgreSQL: {e}")
        return False


def guardar_mensaje_bd(topico, mensaje_texto, datos_json=None):
    """
    Guarda un mensaje en la base de datos PostgreSQL
    
    Args:
        topico (str): Tópico MQTT
        mensaje_texto (str): Contenido del mensaje
        datos_json (dict): Datos JSON parseados del mensaje
    
    Returns:
        bool: True si se guardó exitosamente
    """
    global db_connection, mensaje_count, error_count
    
    try:
        # Verificar conexión a BD
        if not db_connection or db_connection.closed:
            print("⚠️ Reconectando a PostgreSQL...")
            if not conectar_postgresql():
                return False
        
        cursor = db_connection.cursor()
        
        # Extraer datos del JSON si está disponible
        sensor_id = None
        valor_numerico = None
        unidad = None
        
        if datos_json:
            sensor_id = datos_json.get('sensor_id')
            valor_numerico = datos_json.get('valor')
            unidad = datos_json.get('unidad')
            
            # También puede estar como 'value' en lugar de 'valor'
            if valor_numerico is None:
                valor_numerico = datos_json.get('value')
        
        # Query de inserción
        query = """
        INSERT INTO mensajes_mqtt 
        (topico, mensaje, sensor_id, valor_numerico, unidad, ip_servidor)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            topico,
            mensaje_texto,
            sensor_id,
            valor_numerico,
            unidad,
            MQTT_BROKER
        ))
        
        db_connection.commit()
        cursor.close()
        
        mensaje_count += 1
        
        # Actualizar estadísticas por tópico
        if topico not in topicos_stats:
            topicos_stats[topico] = 0
        topicos_stats[topico] += 1
        
        return True
        
    except psycopg2.Error as e:
        error_count += 1
        print(f"❌ Error PostgreSQL: {e}")
        
        # Intentar reconectar
        try:
            if db_connection:
                db_connection.rollback()
            conectar_postgresql()
        except:
            pass
        
        return False
    except Exception as e:
        error_count += 1
        print(f"❌ Error inesperado guardando mensaje: {e}")
        return False


def procesar_mensaje_json(mensaje_texto):
    """
    Intenta parsear el mensaje como JSON
    
    Args:
        mensaje_texto (str): Mensaje recibido
    
    Returns:
        dict: Datos JSON parseados o None si no es JSON válido
    """
    try:
        return json.loads(mensaje_texto)
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


# ============================================
# CALLBACKS MQTT
# ============================================

def on_connect(client, userdata, flags, rc):
    """Callback ejecutado al conectarse al broker MQTT"""
    global conectado_mqtt
    
    if rc == 0:
        conectado_mqtt = True
        print("✅ Conectado al servidor MQTT")
        print(f"📡 Servidor: {MQTT_BROKER}:{MQTT_PORT}")
        
        # Suscribirse a todos los tópicos
        client.subscribe(TOPIC_ALL)
        print(f"📥 Suscrito a: {TOPIC_ALL} (todos los tópicos)")
        print("=" * 60)
        print("🎧 Escuchando mensajes del servidor...\n")
    else:
        conectado_mqtt = False
        print(f"❌ Error de conexión MQTT. Código: {rc}")
        error_messages = {
            1: "Protocolo incorrecto",
            2: "ID de cliente inválido",
            3: "Servidor no disponible",
            4: "Usuario/contraseña incorrectos",
            5: "No autorizado"
        }
        if rc in error_messages:
            print(f"   Detalle: {error_messages[rc]}")


def on_disconnect(client, userdata, rc):
    """Callback ejecutado al desconectarse del broker"""
    global conectado_mqtt
    conectado_mqtt = False
    
    if rc != 0:
        print("⚠️ Desconexión inesperada del servidor MQTT")
        print("🔄 Intentando reconectar...")


def on_message(client, userdata, msg):
    """
    Callback ejecutado al recibir un mensaje MQTT
    
    Args:
        client: Cliente MQTT
        userdata: Datos de usuario
        msg: Mensaje recibido
    """
    try:
        topico = msg.topic
        mensaje_texto = msg.payload.decode('utf-8')
        
        # Procesar JSON si es posible
        datos_json = procesar_mensaje_json(mensaje_texto)
        
        # Guardar en base de datos
        if guardar_mensaje_bd(topico, mensaje_texto, datos_json):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] 💾 [{topico}] ", end='')
            
            # Mostrar información del sensor si está disponible
            if datos_json:
                if 'sensor_id' in datos_json:
                    print(f"Sensor: {datos_json['sensor_id']} ", end='')
                if 'valor' in datos_json:
                    valor = datos_json['valor']
                    unidad = datos_json.get('unidad', '')
                    print(f"Valor: {valor} {unidad} ", end='')
                elif 'value' in datos_json:
                    valor = datos_json['value']
                    unit = datos_json.get('unit', datos_json.get('unidad', ''))
                    print(f"Valor: {valor} {unit} ", end='')
            
            print(f"| Total: {mensaje_count}")
        else:
            print(f"❌ Error guardando mensaje de {topico}")
    
    except Exception as e:
        global error_count
        error_count += 1
        print(f"❌ Error procesando mensaje: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback ejecutado al confirmar suscripción"""
    print(f"✅ Suscripción confirmada. QoS: {granted_qos}")


# ============================================
# FUNCIONES DE CONTROL
# ============================================

def signal_handler(sig, frame):
    """Maneja la señal de interrupción (Ctrl+C)"""
    global running
    print("\n\n⏹️  Recibida señal de interrupción...")
    running = False


def mostrar_estadisticas():
    """Muestra estadísticas del cliente"""
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DEL CLIENTE MQTT")
    print("=" * 60)
    print(f"✅ Mensajes almacenados: {mensaje_count}")
    print(f"❌ Errores: {error_count}")
    print(f"🔗 Estado MQTT: {'Conectado' if conectado_mqtt else 'Desconectado'}")
    
    if topicos_stats:
        print("\n📈 Mensajes por tópico:")
        sorted_topics = sorted(topicos_stats.items(), key=lambda x: x[1], reverse=True)
        for topico, cantidad in sorted_topics[:10]:  # Top 10
            print(f"   {topico}: {cantidad}")
    
    # Estadísticas de la base de datos
    try:
        if db_connection and not db_connection.closed:
            cursor = db_connection.cursor()
            
            # Total en BD
            cursor.execute("SELECT COUNT(*) FROM mensajes_mqtt;")
            total_bd = cursor.fetchone()[0]
            print(f"\n🗄️  Total en base de datos: {total_bd}")
            
            # Último mensaje
            cursor.execute("""
                SELECT topico, timestamp_llegada 
                FROM mensajes_mqtt 
                ORDER BY timestamp_llegada DESC 
                LIMIT 1;
            """)
            ultimo = cursor.fetchone()
            if ultimo:
                print(f"🕐 Último mensaje: {ultimo[0]} a las {ultimo[1]}")
            
            cursor.close()
    except Exception as e:
        print(f"⚠️ No se pudieron obtener estadísticas de BD: {e}")
    
    print("=" * 60 + "\n")


def conectar_mqtt():
    """
    Establece conexión con el servidor MQTT
    
    Returns:
        bool: True si la conexión es exitosa
    """
    global mqtt_client
    
    try:
        # Crear cliente MQTT
        mqtt_client = mqtt.Client(client_id=CLIENT_ID)
        
        # Configurar credenciales si existen
        if MQTT_USERNAME and MQTT_PASSWORD:
            mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            print("🔐 Autenticación MQTT configurada")
        
        # Configurar callbacks
        mqtt_client.on_connect = on_connect
        mqtt_client.on_disconnect = on_disconnect
        mqtt_client.on_message = on_message
        mqtt_client.on_subscribe = on_subscribe
        
        # Conectar al broker
        print(f"🔄 Conectando al servidor MQTT {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a MQTT: {e}")
        return False


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal del cliente"""
    global running
    
    print("=" * 60)
    print("🔌 CLIENTE MQTT - SUSCRIPTOR ADMINISTRATIVO")
    print("   Universidad Militar Nueva Granada")
    print("=" * 60)
    print(f"📡 Servidor MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🗄️  Base de datos: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print(f"🆔 Client ID: {CLIENT_ID}")
    print("=" * 60 + "\n")
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    # Conectar a PostgreSQL
    print("🔄 Conectando a PostgreSQL...")
    if not conectar_postgresql():
        print("❌ No se pudo conectar a PostgreSQL. Verifica:")
        print("   1. PostgreSQL está instalado e iniciado")
        print("   2. Base de datos 'SensoresMQTT' existe")
        print("   3. Credenciales en .env son correctas")
        return
    
    # Conectar a MQTT
    if not conectar_mqtt():
        print("❌ No se pudo conectar al servidor MQTT")
        return
    
    try:
        print("\n✅ Cliente iniciado. Presiona Ctrl+C para detener.\n")
        
        # Iniciar loop MQTT en hilo separado
        mqtt_client.loop_start()
        
        # Loop principal
        while running:
            time.sleep(1)
            
            # Verificar conexión MQTT cada 30 segundos
            if mensaje_count > 0 and mensaje_count % 30 == 0:
                if not conectado_mqtt:
                    print("⚠️ Conexión MQTT perdida, reintentando...")
                    try:
                        mqtt_client.reconnect()
                    except:
                        pass
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo cliente...")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        # Limpiar recursos
        running = False
        
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("📡 Desconectado del servidor MQTT")
        
        if db_connection and not db_connection.closed:
            db_connection.close()
            print("🗄️  Conexión PostgreSQL cerrada")
        
        mostrar_estadisticas()
        print("👋 Cliente detenido correctamente")


if __name__ == "__main__":
    main()