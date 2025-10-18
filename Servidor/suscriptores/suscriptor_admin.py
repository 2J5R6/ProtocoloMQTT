"""
============================================
SUSCRIPTOR ADMINISTRATIVO - BASE DE DATOS
Taller Comunicaciones - Universidad Militar Nueva Granada
============================================

Este suscriptor se conecta a TODOS los tópicos (#) y almacena
todos los mensajes recibidos en la base de datos PostgreSQL.

Funcionalidades:
- Suscripción a todos los tópicos
- Almacenamiento automático en PostgreSQL
- Procesamiento de mensajes JSON
- Registro de timestamp de recepción
- Manejo de errores y reconexión

Uso:
    python suscriptor_admin.py
"""

import paho.mqtt.client as mqtt
import json
import psycopg2
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Agregar path para importar db_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_config import crear_conexion, DB_CONFIG

# Cargar variables de entorno
load_dotenv()

# ============================================
# CONFIGURACIÓN
# ============================================
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')

# Identificador del cliente
CLIENT_ID = "suscriptor_admin"

# Suscripción a TODOS los tópicos
TOPIC_ALL = "#"

# ============================================
# VARIABLES GLOBALES
# ============================================
db_connection = None
message_count = 0
error_count = 0

# ============================================
# FUNCIONES DE BASE DE DATOS
# ============================================
def conectar_base_datos():
    """Conecta a la base de datos PostgreSQL"""
    global db_connection
    try:
        db_connection = crear_conexion()
        if db_connection:
            print("✅ Conectado a PostgreSQL")
            return True
        else:
            print("❌ Error al conectar a PostgreSQL")
            return False
    except Exception as e:
        print(f"❌ Error de conexión DB: {e}")
        return False


def guardar_mensaje(topico, mensaje_texto, sensor_id=None, valor_numerico=None, unidad=None, ip_origen=None):
    """
    Guarda un mensaje en la base de datos
    
    Args:
        topico: Tópico MQTT
        mensaje_texto: Contenido del mensaje (JSON string)
        sensor_id: ID del sensor
        valor_numerico: Valor numérico extraído
        unidad: Unidad de medida
        ip_origen: IP de origen (opcional)
    
    Returns:
        bool: True si se guardó exitosamente
    """
    global db_connection, message_count, error_count
    
    try:
        if not db_connection or db_connection.closed:
            print("⚠️ Reconectando a base de datos...")
            if not conectar_base_datos():
                return False
        
        cursor = db_connection.cursor()
        
        query = """
        INSERT INTO mensajes_mqtt 
        (topico, mensaje, sensor_id, valor_numerico, unidad, ip_origen)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            topico,
            mensaje_texto,
            sensor_id,
            valor_numerico,
            unidad,
            ip_origen
        ))
        
        db_connection.commit()
        cursor.close()
        
        message_count += 1
        return True
        
    except psycopg2.Error as e:
        error_count += 1
        print(f"❌ Error al guardar en DB: {e}")
        
        # Intentar reconectar
        try:
            if db_connection:
                db_connection.rollback()
            conectar_base_datos()
        except:
            pass
        
        return False


def procesar_mensaje_json(topico, mensaje_texto):
    """
    Procesa un mensaje JSON y extrae información relevante
    
    Args:
        topico: Tópico MQTT
        mensaje_texto: Mensaje recibido
    
    Returns:
        tuple: (sensor_id, valor_numerico, unidad)
    """
    try:
        data = json.loads(mensaje_texto)
        
        sensor_id = data.get('sensor_id', None)
        valor_numerico = data.get('valor', None)
        unidad = data.get('unidad', None)
        
        return (sensor_id, valor_numerico, unidad)
    
    except json.JSONDecodeError:
        # Si no es JSON, retornar None
        return (None, None, None)
    except Exception as e:
        print(f"⚠️ Error procesando JSON: {e}")
        return (None, None, None)


# ============================================
# CALLBACKS MQTT
# ============================================
def on_connect(client, userdata, flags, rc):
    """Callback al conectarse al broker"""
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        print(f"📡 Servidor: {MQTT_BROKER}:{MQTT_PORT}")
        
        # Suscribirse a TODOS los tópicos
        client.subscribe(TOPIC_ALL)
        print(f"📥 Suscrito a: {TOPIC_ALL} (todos los tópicos)")
        print("=" * 60)
        print("🎧 Escuchando mensajes...\n")
    else:
        print(f"❌ Error de conexión MQTT. Código: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback al desconectarse del broker"""
    if rc != 0:
        print("⚠️ Desconexión inesperada del broker. Reconectando...")


def on_message(client, userdata, msg):
    """
    Callback al recibir un mensaje
    
    Args:
        client: Cliente MQTT
        userdata: Datos de usuario
        msg: Mensaje recibido
    """
    global message_count
    
    try:
        topico = msg.topic
        mensaje_texto = msg.payload.decode('utf-8')
        
        # Procesar mensaje JSON
        sensor_id, valor_numerico, unidad = procesar_mensaje_json(topico, mensaje_texto)
        
        # Guardar en base de datos
        if guardar_mensaje(topico, mensaje_texto, sensor_id, valor_numerico, unidad):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] 💾 [{topico}] ", end='')
            
            if sensor_id:
                print(f"Sensor: {sensor_id} ", end='')
            if valor_numerico is not None:
                print(f"Valor: {valor_numerico}", end='')
                if unidad:
                    print(f" {unidad}", end='')
            
            print(f" | Total: {message_count}")
        else:
            print(f"❌ Error guardando mensaje de {topico}")
    
    except Exception as e:
        global error_count
        error_count += 1
        print(f"❌ Error procesando mensaje: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback al suscribirse exitosamente"""
    print(f"✅ Suscripción confirmada. QoS: {granted_qos}")


# ============================================
# FUNCIONES AUXILIARES
# ============================================
def mostrar_estadisticas():
    """Muestra estadísticas del suscriptor"""
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DEL SUSCRIPTOR")
    print("=" * 60)
    print(f"✅ Mensajes guardados: {message_count}")
    print(f"❌ Errores: {error_count}")
    
    # Obtener estadísticas de la base de datos
    try:
        if db_connection and not db_connection.closed:
            cursor = db_connection.cursor()
            
            # Total por tópico
            cursor.execute("""
                SELECT topico, COUNT(*) as cantidad
                FROM mensajes_mqtt
                GROUP BY topico
                ORDER BY cantidad DESC
                LIMIT 10
            """)
            
            print("\n📈 Top 10 tópicos con más mensajes:")
            for topico, cantidad in cursor.fetchall():
                print(f"   {topico}: {cantidad}")
            
            cursor.close()
    except Exception as e:
        print(f"⚠️ No se pudieron obtener estadísticas: {e}")
    
    print("=" * 60 + "\n")


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================
def main():
    """Función principal"""
    print("=" * 60)
    print("👨‍💼 SUSCRIPTOR ADMINISTRATIVO - BASE DE DATOS")
    print("   Universidad Militar Nueva Granada")
    print("=" * 60)
    print(f"📡 Broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🗄️  Base de datos: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print(f"🆔 Client ID: {CLIENT_ID}")
    print("=" * 60 + "\n")
    
    # Conectar a base de datos
    print("🔄 Conectando a base de datos...")
    if not conectar_base_datos():
        print("❌ No se pudo conectar a la base de datos. Verifica la configuración.")
        return
    
    # Crear cliente MQTT
    print("🔄 Creando cliente MQTT...")
    client = mqtt.Client(client_id=CLIENT_ID)
    
    # Configurar credenciales si existen
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        print("🔐 Autenticación configurada")
    
    # Configurar callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    
    # Conectar al broker
    try:
        print(f"🔄 Conectando a broker MQTT...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        print("\n✅ Suscriptor iniciado. Presiona Ctrl+C para detener.\n")
        
        # Loop principal
        client.loop_forever()
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo suscriptor...")
        mostrar_estadisticas()
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Limpiar recursos
        if client:
            client.disconnect()
        if db_connection and not db_connection.closed:
            db_connection.close()
            print("🔌 Conexión a base de datos cerrada")
        print("👋 Suscriptor detenido")


if __name__ == "__main__":
    main()
