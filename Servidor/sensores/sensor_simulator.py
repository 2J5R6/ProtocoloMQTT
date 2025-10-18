"""
============================================
SIMULADOR DE SENSORES MQTT
Taller Comunicaciones - Universidad Militar Nueva Granada
============================================

Este script simula 7 sensores publicando datos a un broker MQTT
en 5 tópicos diferentes. Útil para pruebas sin hardware físico.

Uso:
    python sensor_simulator.py
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================
# CONFIGURACIÓN
# ============================================
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
DEVICE_ID = os.getenv('DEVICE_ID', 'SIMULATOR_01')

# Intervalo de publicación (segundos)
PUBLISH_INTERVAL = 5

# ============================================
# TÓPICOS MQTT
# ============================================
TOPICS = {
    'humo': 'incendio/sensor_humo',
    'alarma': 'incendio/alarma',
    'puerta': 'seguridad/puerta',
    'temperatura': 'clima/temperatura',
    'humedad': 'clima/humedad',
    'viento': 'clima/viento',
    'luz': 'iluminacion/luz',
    'movimiento': 'seguridad/movimiento'
}

# ============================================
# VARIABLES GLOBALES
# ============================================
client = None
connected = False
message_count = 0

# Estados de sensores digitales
puerta_abierta = False
movimiento_detectado = False
alarma_activa = False

# ============================================
# CALLBACKS MQTT
# ============================================
def on_connect(client, userdata, flags, rc):
    """Callback al conectarse al broker"""
    global connected
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        print(f"📡 Servidor: {MQTT_BROKER}:{MQTT_PORT}")
        connected = True
    else:
        print(f"❌ Error de conexión. Código: {rc}")
        connected = False


def on_disconnect(client, userdata, rc):
    """Callback al desconectarse del broker"""
    global connected
    connected = False
    if rc != 0:
        print("⚠️ Desconexión inesperada. Reconectando...")


def on_publish(client, userdata, mid):
    """Callback al publicar un mensaje"""
    global message_count
    message_count += 1


# ============================================
# GENERADORES DE DATOS
# ============================================
def generar_temperatura():
    """Genera temperatura simulada (15°C - 35°C)"""
    base = 25.0
    variacion = random.uniform(-10.0, 10.0)
    return round(base + variacion, 1)


def generar_humedad():
    """Genera humedad simulada (30% - 90%)"""
    base = 60.0
    variacion = random.uniform(-30.0, 30.0)
    return round(max(30, min(90, base + variacion)), 1)


def generar_humo():
    """Genera nivel de humo simulado (0% - 100%)"""
    # Simula detección ocasional de humo
    if random.random() < 0.9:  # 90% del tiempo normal
        return round(random.uniform(0, 15), 1)
    else:  # 10% del tiempo alerta
        return round(random.uniform(50, 100), 1)


def generar_luz():
    """Genera nivel de luz simulado (0% - 100%)"""
    hora = datetime.now().hour
    if 6 <= hora <= 18:  # Día
        return round(random.uniform(60, 100), 1)
    else:  # Noche
        return round(random.uniform(0, 30), 1)


def generar_viento():
    """Genera velocidad de viento (0 - 50 km/h)"""
    return round(random.uniform(0, 50), 1)


def generar_puerta():
    """Simula cambio de estado de puerta"""
    global puerta_abierta
    if random.random() < 0.1:  # 10% probabilidad de cambio
        puerta_abierta = not puerta_abierta
    return puerta_abierta


def generar_movimiento():
    """Simula detección de movimiento"""
    global movimiento_detectado
    if random.random() < 0.15:  # 15% probabilidad de cambio
        movimiento_detectado = not movimiento_detectado
    return movimiento_detectado


def generar_alarma():
    """Simula activación de alarma manual"""
    global alarma_activa
    if random.random() < 0.02:  # 2% probabilidad de activación
        alarma_activa = True
    elif alarma_activa and random.random() < 0.5:
        alarma_activa = False
    return alarma_activa


# ============================================
# PUBLICACIÓN DE MENSAJES
# ============================================
def crear_mensaje(tipo, valor, unidad, estado=None):
    """
    Crea un mensaje JSON para publicar
    
    Args:
        tipo: Tipo de sensor
        valor: Valor medido
        unidad: Unidad de medida
        estado: Estado adicional (opcional)
    
    Returns:
        str: Mensaje JSON
    """
    mensaje = {
        'sensor_id': DEVICE_ID,
        'tipo': tipo,
        'valor': valor,
        'unidad': unidad,
        'timestamp': datetime.now().isoformat()
    }
    
    if estado:
        mensaje['estado'] = estado
    
    return json.dumps(mensaje)


def publicar_sensores():
    """Publica datos de todos los sensores"""
    if not connected:
        print("⚠️ No conectado. Esperando conexión...")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 Publicando sensores - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    # 1. Temperatura
    temp = generar_temperatura()
    mensaje = crear_mensaje('temperatura', temp, '°C')
    result = client.publish(TOPICS['temperatura'], mensaje)
    print(f"🌡️  Temperatura: {temp}°C -> {TOPICS['temperatura']}")
    
    time.sleep(0.1)
    
    # 2. Humedad
    hum = generar_humedad()
    mensaje = crear_mensaje('humedad', hum, '%')
    client.publish(TOPICS['humedad'], mensaje)
    print(f"💧 Humedad: {hum}% -> {TOPICS['humedad']}")
    
    time.sleep(0.1)
    
    # 3. Humo
    humo = generar_humo()
    estado = 'alerta' if humo > 50 else 'normal'
    mensaje = crear_mensaje('humo', humo, '%', estado)
    client.publish(TOPICS['humo'], mensaje)
    icono = '🔥' if humo > 50 else '✅'
    print(f"{icono} Humo: {humo}% ({estado}) -> {TOPICS['humo']}")
    
    time.sleep(0.1)
    
    # 4. Luz
    luz = generar_luz()
    mensaje = crear_mensaje('luz', luz, '%')
    client.publish(TOPICS['luz'], mensaje)
    print(f"💡 Luz: {luz}% -> {TOPICS['luz']}")
    
    time.sleep(0.1)
    
    # 5. Viento
    viento = generar_viento()
    mensaje = crear_mensaje('viento', viento, 'km/h')
    client.publish(TOPICS['viento'], mensaje)
    print(f"🌬️  Viento: {viento} km/h -> {TOPICS['viento']}")
    
    time.sleep(0.1)
    
    # 6. Puerta
    puerta = generar_puerta()
    estado = 'abierta' if puerta else 'cerrada'
    mensaje = crear_mensaje('puerta', 1 if puerta else 0, '', estado)
    client.publish(TOPICS['puerta'], mensaje)
    icono = '🔓' if puerta else '🔒'
    print(f"{icono} Puerta: {estado} -> {TOPICS['puerta']}")
    
    time.sleep(0.1)
    
    # 7. Movimiento
    movimiento = generar_movimiento()
    estado = 'detectado' if movimiento else 'sin_movimiento'
    mensaje = crear_mensaje('movimiento', 1 if movimiento else 0, '', estado)
    client.publish(TOPICS['movimiento'], mensaje)
    icono = '🚶' if movimiento else '🚫'
    print(f"{icono} Movimiento: {estado} -> {TOPICS['movimiento']}")
    
    # 8. Alarma (solo si está activa)
    if generar_alarma() and alarma_activa:
        mensaje = crear_mensaje('alarma_manual', 1, '', 'activada')
        client.publish(TOPICS['alarma'], mensaje)
        print(f"🚨 ALARMA ACTIVADA -> {TOPICS['alarma']}")
    
    print(f"\n✅ Total de mensajes publicados: {message_count}")


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================
def main():
    """Función principal"""
    global client
    
    print("=" * 60)
    print("🔬 SIMULADOR DE SENSORES MQTT")
    print("   Universidad Militar Nueva Granada")
    print("=" * 60)
    print(f"📡 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🆔 Device ID: {DEVICE_ID}")
    print(f"⏱️  Intervalo: {PUBLISH_INTERVAL}s")
    print("=" * 60)
    
    # Crear cliente MQTT
    client = mqtt.Client(client_id=f"{DEVICE_ID}_{random.randint(0, 1000)}")
    
    # Configurar credenciales si existen
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Configurar callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    
    # Conectar al broker
    try:
        print("\n🔄 Conectando al broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Esperar conexión
        time.sleep(2)
        
        if not connected:
            print("❌ No se pudo conectar al broker")
            return
        
        print("\n✅ Simulador iniciado. Presiona Ctrl+C para detener.\n")
        
        # Loop principal
        while True:
            publicar_sensores()
            time.sleep(PUBLISH_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo simulador...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        print("👋 Simulador detenido")
        print(f"📊 Total de mensajes publicados: {message_count}")


if __name__ == "__main__":
    main()
