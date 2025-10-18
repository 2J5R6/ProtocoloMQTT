"""
============================================
CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL
Cliente MQTT - Universidad Militar Nueva Granada
============================================

Módulo para gestionar la conexión y operaciones con PostgreSQL
usando las credenciales específicas del proyecto.

Configuración del usuario:
- USERNAME_PG: "postgres"
- PASSWORD: "2324Julibolt"
- DATABASE: "SensoresMQTT"
"""

import psycopg2
import psycopg2.extras
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'SensoresMQTT'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '2324Julibolt')
}

# ============================================
# FUNCIONES DE CONEXIÓN
# ============================================

def crear_conexion():
    """
    Crea una conexión a la base de datos PostgreSQL
    
    Returns:
        psycopg2.connection: Conexión a la base de datos o None si falla
    """
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except psycopg2.Error as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al conectar: {e}")
        return None


def verificar_conexion():
    """
    Verifica si la conexión a la base de datos es exitosa
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conexion.close()
            print(f"✅ Conexión exitosa a PostgreSQL: {version}")
            return True
        else:
            print("❌ No se pudo establecer la conexión")
            return False
    except Exception as e:
        print(f"❌ Error verificando conexión: {e}")
        return False


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def ejecutar_query(query, parametros=None, retornar_resultados=False):
    """
    Ejecuta una consulta SQL
    
    Args:
        query (str): Consulta SQL a ejecutar
        parametros (tuple): Parámetros para la consulta
        retornar_resultados (bool): Si debe retornar resultados
    
    Returns:
        list: Resultados de la consulta si retornar_resultados=True
        bool: True si la ejecución fue exitosa
    """
    conexion = None
    try:
        conexion = crear_conexion()
        if not conexion:
            return False
        
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if parametros:
            cursor.execute(query, parametros)
        else:
            cursor.execute(query)
        
        if retornar_resultados:
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()
            return resultados
        else:
            conexion.commit()
            cursor.close()
            conexion.close()
            return True
            
    except psycopg2.Error as e:
        print(f"❌ Error ejecutando query: {e}")
        if conexion:
            conexion.rollback()
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if conexion:
            conexion.close()


def obtener_estadisticas_bd():
    """
    Obtiene estadísticas básicas de la base de datos
    
    Returns:
        dict: Estadísticas de la base de datos
    """
    try:
        conexion = crear_conexion()
        if not conexion:
            return None
        
        cursor = conexion.cursor()
        
        # Total de mensajes
        cursor.execute("SELECT COUNT(*) FROM mensajes_mqtt;")
        total_mensajes = cursor.fetchone()[0]
        
        # Mensajes por tópico
        cursor.execute("""
            SELECT topico, COUNT(*) as cantidad 
            FROM mensajes_mqtt 
            GROUP BY topico 
            ORDER BY cantidad DESC;
        """)
        mensajes_por_topico = cursor.fetchall()
        
        # Último mensaje
        cursor.execute("""
            SELECT timestamp_llegada 
            FROM mensajes_mqtt 
            ORDER BY timestamp_llegada DESC 
            LIMIT 1;
        """)
        ultimo_mensaje = cursor.fetchone()
        ultimo_mensaje = ultimo_mensaje[0] if ultimo_mensaje else None
        
        cursor.close()
        conexion.close()
        
        return {
            'total_mensajes': total_mensajes,
            'mensajes_por_topico': mensajes_por_topico,
            'ultimo_mensaje': ultimo_mensaje
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return None


# ============================================
# FUNCIÓN DE PRUEBA
# ============================================

def main():
    """Función para probar la configuración de la base de datos"""
    print("=" * 60)
    print("🔧 PRUEBA DE CONFIGURACIÓN POSTGRESQL")
    print("=" * 60)
    print(f"🏠 Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"🗄️  Base de datos: {DB_CONFIG['database']}")
    print(f"👤 Usuario: {DB_CONFIG['user']}")
    print("=" * 60)
    
    # Verificar conexión
    if verificar_conexion():
        print("✅ Configuración correcta")
        
        # Mostrar estadísticas si la tabla existe
        try:
            stats = obtener_estadisticas_bd()
            if stats:
                print(f"\n📊 Total de mensajes: {stats['total_mensajes']}")
                if stats['ultimo_mensaje']:
                    print(f"🕐 Último mensaje: {stats['ultimo_mensaje']}")
        except:
            print("ℹ️  Tabla 'mensajes_mqtt' no existe aún")
    else:
        print("❌ Configuración incorrecta")
        print("\n🔧 Verificar:")
        print("1. PostgreSQL está instalado e iniciado")
        print("2. Base de datos 'SensoresMQTT' existe")
        print("3. Usuario 'postgres' tiene permisos")
        print("4. Contraseña '2324Julibolt' es correcta")


if __name__ == "__main__":
    main()