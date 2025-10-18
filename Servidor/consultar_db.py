#!/usr/bin/env python3
"""
Script de consulta de base de datos MQTT
Uso: python consultar_db.py
o desde el venv: .venv/bin/python consultar_db.py
"""

import sys
from database.db_config import crear_conexion

def consultar_base_datos():
    """Consulta y muestra el estado actual de la base de datos MQTT"""
    try:
        conn = crear_conexion()
        cursor = conn.cursor()
        
        print("=" * 70)
        print("📊 CONSULTA DE BASE DE DATOS - SISTEMA MQTT")
        print("=" * 70)
        
        # 1. Total de mensajes
        cursor.execute("SELECT COUNT(*) FROM mensajes_mqtt;")
        total = cursor.fetchone()[0]
        print(f"\n📈 TOTAL DE MENSAJES GUARDADOS: {total}")
        
        # 2. Mensajes por tópico
        print(f"\n📊 MENSAJES POR TÓPICO:")
        print("-" * 70)
        cursor.execute("""
            SELECT topico, COUNT(*) as cantidad 
            FROM mensajes_mqtt 
            GROUP BY topico 
            ORDER BY cantidad DESC;
        """)
        for topic, count in cursor.fetchall():
            print(f"   {topic:30} → {count:4} mensajes")
        
        # 3. Últimos 10 mensajes
        print(f"\n🕒 ÚLTIMOS 10 MENSAJES RECIBIDOS:")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                timestamp_recepcion,
                topico, 
                sensor_id, 
                valor_numerico, 
                unidad
            FROM mensajes_mqtt 
            ORDER BY timestamp_recepcion DESC 
            LIMIT 10;
        """)
        
        for timestamp, topic, sensor, value, unit in cursor.fetchall():
            time_str = timestamp.strftime('%H:%M:%S')
            unit_str = unit if unit else ''
            print(f"   [{time_str}] {topic:25} | {sensor:12} | {value:6.1f} {unit_str}")
        
        # 4. Estadísticas por tópico
        print(f"\n📊 ESTADÍSTICAS POR TÓPICO:")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                topico,
                COUNT(*) as total,
                AVG(valor_numerico) as promedio,
                MIN(valor_numerico) as minimo,
                MAX(valor_numerico) as maximo
            FROM mensajes_mqtt
            WHERE valor_numerico IS NOT NULL
            GROUP BY topico
            ORDER BY topico;
        """)
        
        print(f"{'Tópico':<30} {'Total':>8} {'Promedio':>10} {'Min':>8} {'Max':>8}")
        for topic, total, avg, min_val, max_val in cursor.fetchall():
            avg_str = f"{avg:.1f}" if avg else "N/A"
            min_str = f"{min_val:.1f}" if min_val else "N/A"
            max_str = f"{max_val:.1f}" if max_val else "N/A"
            print(f"{topic:<30} {total:>8} {avg_str:>10} {min_str:>8} {max_str:>8}")
        
        # 5. Rango de tiempo de los mensajes
        print(f"\n⏰ RANGO TEMPORAL:")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                MIN(timestamp_recepcion) as primer_mensaje,
                MAX(timestamp_recepcion) as ultimo_mensaje,
                MAX(timestamp_recepcion) - MIN(timestamp_recepcion) as duracion
            FROM mensajes_mqtt;
        """)
        
        first, last, duration = cursor.fetchone()
        if first and last:
            print(f"   Primer mensaje: {first.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Último mensaje: {last.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duración:       {duration}")
        
        # 6. Sensores únicos
        print(f"\n🔬 SENSORES DETECTADOS:")
        print("-" * 70)
        cursor.execute("""
            SELECT DISTINCT sensor_id, COUNT(*) as mensajes
            FROM mensajes_mqtt
            WHERE sensor_id IS NOT NULL
            GROUP BY sensor_id
            ORDER BY mensajes DESC;
        """)
        
        for sensor_id, count in cursor.fetchall():
            print(f"   {sensor_id:20} → {count} mensajes")
        
        print("\n" + "=" * 70)
        print("✅ Consulta completada exitosamente")
        print("=" * 70)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    consultar_base_datos()
