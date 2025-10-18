"""
============================================
CONSULTA Y ANÁLISIS DE DATOS MQTT
Cliente MQTT - Universidad Militar Nueva Granada
============================================

Este script proporciona herramientas para consultar y analizar
los datos almacenados en la base de datos PostgreSQL.

Funcionalidades:
- Consultas básicas de mensajes
- Estadísticas por tópico y sensor
- Análisis temporal
- Exportación de datos
- Visualización simple

Uso:
    python consultar_datos.py
"""

import psycopg2
import psycopg2.extras
import os
import sys
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Agregar path para importar módulos locales
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_config import crear_conexion, DB_CONFIG

# Cargar variables de entorno
load_dotenv()

# ============================================
# FUNCIONES DE CONSULTA
# ============================================

def obtener_ultimos_mensajes(limite=10):
    """
    Obtiene los últimos mensajes recibidos
    
    Args:
        limite (int): Número de mensajes a mostrar
    
    Returns:
        list: Lista de mensajes
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = """
        SELECT id, topico, mensaje, timestamp_llegada, sensor_id, valor_numerico, unidad
        FROM mensajes_mqtt
        ORDER BY timestamp_llegada DESC
        LIMIT %s;
        """
        
        cursor.execute(query, (limite,))
        mensajes = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return mensajes
        
    except Exception as e:
        print(f"❌ Error obteniendo últimos mensajes: {e}")
        return None


def obtener_estadisticas_generales():
    """
    Obtiene estadísticas generales del sistema
    
    Returns:
        dict: Estadísticas del sistema
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor()
        
        # Total de mensajes
        cursor.execute("SELECT COUNT(*) FROM mensajes_mqtt;")
        total_mensajes = cursor.fetchone()[0]
        
        # Número de tópicos únicos
        cursor.execute("SELECT COUNT(DISTINCT topico) FROM mensajes_mqtt;")
        total_topicos = cursor.fetchone()[0]
        
        # Número de sensores únicos
        cursor.execute("SELECT COUNT(DISTINCT sensor_id) FROM mensajes_mqtt WHERE sensor_id IS NOT NULL;")
        total_sensores = cursor.fetchone()[0]
        
        # Primer y último mensaje
        cursor.execute("SELECT MIN(timestamp_llegada), MAX(timestamp_llegada) FROM mensajes_mqtt;")
        primer_mensaje, ultimo_mensaje = cursor.fetchone()
        
        # Mensajes por día (últimos 7 días)
        cursor.execute("""
            SELECT DATE(timestamp_llegada) as fecha, COUNT(*) as cantidad
            FROM mensajes_mqtt
            WHERE timestamp_llegada > NOW() - INTERVAL '7 days'
            GROUP BY DATE(timestamp_llegada)
            ORDER BY fecha DESC;
        """)
        mensajes_por_dia = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return {
            'total_mensajes': total_mensajes,
            'total_topicos': total_topicos,
            'total_sensores': total_sensores,
            'primer_mensaje': primer_mensaje,
            'ultimo_mensaje': ultimo_mensaje,
            'mensajes_por_dia': mensajes_por_dia
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return None


def obtener_estadisticas_por_topico():
    """
    Obtiene estadísticas detalladas por tópico
    
    Returns:
        list: Lista de estadísticas por tópico
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = """
        SELECT 
            topico,
            COUNT(*) as total_mensajes,
            COUNT(DISTINCT sensor_id) as sensores_unicos,
            MIN(timestamp_llegada) as primer_mensaje,
            MAX(timestamp_llegada) as ultimo_mensaje,
            AVG(valor_numerico) as valor_promedio,
            MIN(valor_numerico) as valor_minimo,
            MAX(valor_numerico) as valor_maximo
        FROM mensajes_mqtt
        GROUP BY topico
        ORDER BY total_mensajes DESC;
        """
        
        cursor.execute(query)
        estadisticas = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return estadisticas
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas por tópico: {e}")
        return None


def obtener_mensajes_por_topico(topico, limite=20):
    """
    Obtiene mensajes de un tópico específico
    
    Args:
        topico (str): Tópico a consultar
        limite (int): Número de mensajes
    
    Returns:
        list: Lista de mensajes del tópico
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = """
        SELECT id, topico, mensaje, timestamp_llegada, sensor_id, valor_numerico, unidad
        FROM mensajes_mqtt
        WHERE topico LIKE %s
        ORDER BY timestamp_llegada DESC
        LIMIT %s;
        """
        
        cursor.execute(query, (f"%{topico}%", limite))
        mensajes = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return mensajes
        
    except Exception as e:
        print(f"❌ Error obteniendo mensajes del tópico: {e}")
        return None


def obtener_mensajes_por_sensor(sensor_id, limite=20):
    """
    Obtiene mensajes de un sensor específico
    
    Args:
        sensor_id (str): ID del sensor
        limite (int): Número de mensajes
    
    Returns:
        list: Lista de mensajes del sensor
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = """
        SELECT id, topico, mensaje, timestamp_llegada, sensor_id, valor_numerico, unidad
        FROM mensajes_mqtt
        WHERE sensor_id = %s
        ORDER BY timestamp_llegada DESC
        LIMIT %s;
        """
        
        cursor.execute(query, (sensor_id, limite))
        mensajes = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return mensajes
        
    except Exception as e:
        print(f"❌ Error obteniendo mensajes del sensor: {e}")
        return None


def obtener_mensajes_rango_tiempo(horas=24):
    """
    Obtiene mensajes en un rango de tiempo específico
    
    Args:
        horas (int): Número de horas hacia atrás
    
    Returns:
        list: Lista de mensajes en el rango
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = """
        SELECT topico, COUNT(*) as cantidad, AVG(valor_numerico) as promedio
        FROM mensajes_mqtt
        WHERE timestamp_llegada > NOW() - INTERVAL '%s hours'
        GROUP BY topico
        ORDER BY cantidad DESC;
        """
        
        cursor.execute(query, (horas,))
        estadisticas = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        return estadisticas
        
    except Exception as e:
        print(f"❌ Error obteniendo mensajes por tiempo: {e}")
        return None


# ============================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================

def mostrar_ultimos_mensajes(limite=10):
    """Muestra los últimos mensajes en formato tabla"""
    print(f"\n📋 ÚLTIMOS {limite} MENSAJES")
    print("=" * 80)
    
    mensajes = obtener_ultimos_mensajes(limite)
    if not mensajes:
        print("❌ No se pudieron obtener los mensajes")
        return
    
    if not mensajes:
        print("ℹ️  No hay mensajes en la base de datos")
        return
    
    for msg in mensajes:
        timestamp = msg['timestamp_llegada'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {msg['topico']}")
        
        if msg['sensor_id']:
            print(f"   📡 Sensor: {msg['sensor_id']}")
        
        if msg['valor_numerico'] is not None:
            valor = f"{msg['valor_numerico']}"
            if msg['unidad']:
                valor += f" {msg['unidad']}"
            print(f"   📊 Valor: {valor}")
        
        # Mostrar parte del mensaje JSON
        try:
            data = json.loads(msg['mensaje'])
            print(f"   💬 Mensaje: {json.dumps(data, indent=None)[:100]}...")
        except:
            print(f"   💬 Mensaje: {msg['mensaje'][:50]}...")
        
        print()


def mostrar_estadisticas_generales():
    """Muestra estadísticas generales del sistema"""
    print("\n📊 ESTADÍSTICAS GENERALES")
    print("=" * 60)
    
    stats = obtener_estadisticas_generales()
    if not stats:
        print("❌ No se pudieron obtener las estadísticas")
        return
    
    print(f"📨 Total de mensajes: {stats['total_mensajes']:,}")
    print(f"📂 Tópicos únicos: {stats['total_topicos']}")
    print(f"📡 Sensores únicos: {stats['total_sensores']}")
    
    if stats['primer_mensaje']:
        print(f"🕐 Primer mensaje: {stats['primer_mensaje']}")
    if stats['ultimo_mensaje']:
        print(f"🕑 Último mensaje: {stats['ultimo_mensaje']}")
    
    if stats['mensajes_por_dia']:
        print("\n📅 Mensajes por día (últimos 7 días):")
        for fecha, cantidad in stats['mensajes_por_dia']:
            print(f"   {fecha}: {cantidad:,} mensajes")


def mostrar_estadisticas_topicos():
    """Muestra estadísticas por tópico"""
    print("\n📂 ESTADÍSTICAS POR TÓPICO")
    print("=" * 80)
    
    stats = obtener_estadisticas_por_topico()
    if not stats:
        print("❌ No se pudieron obtener las estadísticas")
        return
    
    for stat in stats:
        print(f"\n🏷️  Tópico: {stat['topico']}")
        print(f"   📨 Mensajes: {stat['total_mensajes']:,}")
        print(f"   📡 Sensores: {stat['sensores_unicos']}")
        print(f"   🕐 Primer mensaje: {stat['primer_mensaje']}")
        print(f"   🕑 Último mensaje: {stat['ultimo_mensaje']}")
        
        if stat['valor_promedio'] is not None:
            print(f"   📊 Valor promedio: {stat['valor_promedio']:.2f}")
            print(f"   📉 Valor mínimo: {stat['valor_minimo']}")
            print(f"   📈 Valor máximo: {stat['valor_maximo']}")


def exportar_datos_csv(nombre_archivo, topico=None, horas=24):
    """
    Exporta datos a CSV
    
    Args:
        nombre_archivo (str): Nombre del archivo CSV
        topico (str): Tópico específico (opcional)
        horas (int): Horas hacia atrás
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return False
        
        cursor = conexion.cursor()
        
        if topico:
            query = """
            SELECT topico, mensaje, timestamp_llegada, sensor_id, valor_numerico, unidad
            FROM mensajes_mqtt
            WHERE topico LIKE %s AND timestamp_llegada > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp_llegada DESC;
            """
            cursor.execute(query, (f"%{topico}%", horas))
        else:
            query = """
            SELECT topico, mensaje, timestamp_llegada, sensor_id, valor_numerico, unidad
            FROM mensajes_mqtt
            WHERE timestamp_llegada > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp_llegada DESC;
            """
            cursor.execute(query, (horas,))
        
        datos = cursor.fetchall()
        
        # Escribir CSV
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("topico,timestamp,sensor_id,valor,unidad,mensaje\n")
            for fila in datos:
                f.write(f'"{fila[0]}","{fila[2]}","{fila[3]}","{fila[4]}","{fila[5]}","{fila[1]}"\n')
        
        cursor.close()
        conexion.close()
        
        print(f"✅ Datos exportados a {nombre_archivo}")
        print(f"📊 Total de registros: {len(datos)}")
        return True
        
    except Exception as e:
        print(f"❌ Error exportando datos: {e}")
        return False


# ============================================
# MENÚ INTERACTIVO
# ============================================

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 60)
    print("🔍 CONSULTA DE DATOS MQTT")
    print("=" * 60)
    print("1. 📋 Ver últimos mensajes")
    print("2. 📊 Estadísticas generales")
    print("3. 📂 Estadísticas por tópico")
    print("4. 🔍 Buscar por tópico")
    print("5. 📡 Buscar por sensor")
    print("6. ⏰ Estadísticas por tiempo")
    print("7. 💾 Exportar datos a CSV")
    print("8. 🔄 Actualizar vista")
    print("0. ❌ Salir")
    print("=" * 60)


def menu_interactivo():
    """Ejecuta el menú interactivo"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🎯 Selecciona una opción: ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                limite = input("📝 Número de mensajes (10): ").strip()
                limite = int(limite) if limite else 10
                mostrar_ultimos_mensajes(limite)
            elif opcion == "2":
                mostrar_estadisticas_generales()
            elif opcion == "3":
                mostrar_estadisticas_topicos()
            elif opcion == "4":
                topico = input("🏷️  Ingresa el tópico (ej: incendio, clima): ").strip()
                if topico:
                    mensajes = obtener_mensajes_por_topico(topico)
                    if mensajes:
                        print(f"\n📋 MENSAJES DEL TÓPICO: {topico}")
                        print("=" * 60)
                        for msg in mensajes:
                            timestamp = msg['timestamp_llegada'].strftime('%H:%M:%S')
                            print(f"[{timestamp}] {msg['sensor_id']} - {msg['valor_numerico']} {msg['unidad']}")
                    else:
                        print("❌ No se encontraron mensajes")
            elif opcion == "5":
                sensor = input("📡 Ingresa el ID del sensor (ej: ESP32_01): ").strip()
                if sensor:
                    mensajes = obtener_mensajes_por_sensor(sensor)
                    if mensajes:
                        print(f"\n📋 MENSAJES DEL SENSOR: {sensor}")
                        print("=" * 60)
                        for msg in mensajes:
                            timestamp = msg['timestamp_llegada'].strftime('%H:%M:%S')
                            print(f"[{timestamp}] {msg['topico']} - {msg['valor_numerico']} {msg['unidad']}")
                    else:
                        print("❌ No se encontraron mensajes")
            elif opcion == "6":
                horas = input("⏰ Horas hacia atrás (24): ").strip()
                horas = int(horas) if horas else 24
                stats = obtener_mensajes_rango_tiempo(horas)
                if stats:
                    print(f"\n📊 ESTADÍSTICAS ÚLTIMAS {horas} HORAS")
                    print("=" * 60)
                    for stat in stats:
                        promedio = f"{stat['promedio']:.2f}" if stat['promedio'] else "N/A"
                        print(f"{stat['topico']}: {stat['cantidad']} mensajes (promedio: {promedio})")
            elif opcion == "7":
                archivo = input("💾 Nombre del archivo CSV (datos.csv): ").strip()
                archivo = archivo if archivo else "datos.csv"
                topico = input("🏷️  Tópico específico (vacío = todos): ").strip()
                horas = input("⏰ Horas hacia atrás (24): ").strip()
                horas = int(horas) if horas else 24
                
                if topico:
                    exportar_datos_csv(archivo, topico, horas)
                else:
                    exportar_datos_csv(archivo, None, horas)
            elif opcion == "8":
                print("🔄 Actualizando vista...")
            else:
                print("❌ Opción no válida")
            
            input("\n⏸️  Presiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\n⏸️  Presiona Enter para continuar...")


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 HERRAMIENTA DE CONSULTA DE DATOS MQTT")
    print("   Universidad Militar Nueva Granada")
    print("=" * 60)
    print(f"🗄️  Base de datos: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
    print("=" * 60)
    
    # Verificar conexión
    from database.db_config import verificar_conexion
    if not verificar_conexion():
        print("❌ No se puede conectar a la base de datos")
        print("🔧 Verifica que PostgreSQL esté funcionando")
        return
    
    # Mostrar resumen rápido
    stats = obtener_estadisticas_generales()
    if stats:
        print(f"\n📊 Resumen: {stats['total_mensajes']:,} mensajes de {stats['total_sensores']} sensores")
        if stats['ultimo_mensaje']:
            print(f"🕑 Último mensaje: {stats['ultimo_mensaje']}")
    
    # Ejecutar menú
    menu_interactivo()


if __name__ == "__main__":
    main()