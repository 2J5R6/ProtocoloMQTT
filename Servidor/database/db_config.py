"""
Configuración de Conexión a PostgreSQL
Taller MQTT - Universidad Militar Nueva Granada
"""

import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'mqtt_taller'),
    'user': os.getenv('DB_USER', 'mqtt_admin'),
    'password': os.getenv('DB_PASSWORD', 'mqtt_secure_2025')
}

# Pool de conexiones (opcional, para mejor rendimiento)
connection_pool = None

# ============================================
# FUNCIONES DE CONEXIÓN
# ============================================

def crear_conexion():
    """
    Crea y retorna una conexión a PostgreSQL
    
    Returns:
        connection: Objeto de conexión psycopg2
    """
    try:
        conexion = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print(f"✅ Conexión exitosa a PostgreSQL: {DB_CONFIG['database']}")
        return conexion
    except psycopg2.Error as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        return None


def inicializar_pool(min_conn=1, max_conn=10):
    """
    Inicializa un pool de conexiones para múltiples clientes
    
    Args:
        min_conn: Número mínimo de conexiones
        max_conn: Número máximo de conexiones
    """
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            min_conn,
            max_conn,
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print(f"✅ Pool de conexiones inicializado ({min_conn}-{max_conn} conexiones)")
        return connection_pool
    except psycopg2.Error as e:
        print(f"❌ Error al inicializar pool: {e}")
        return None


def obtener_conexion_pool():
    """
    Obtiene una conexión del pool
    
    Returns:
        connection: Conexión del pool
    """
    global connection_pool
    if connection_pool:
        try:
            return connection_pool.getconn()
        except psycopg2.Error as e:
            print(f"❌ Error al obtener conexión del pool: {e}")
            return None
    else:
        print("⚠️ Pool no inicializado, creando conexión directa")
        return crear_conexion()


def liberar_conexion_pool(conexion):
    """
    Devuelve una conexión al pool
    
    Args:
        conexion: Conexión a devolver
    """
    global connection_pool
    if connection_pool and conexion:
        connection_pool.putconn(conexion)


def cerrar_pool():
    """
    Cierra todas las conexiones del pool
    """
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("✅ Pool de conexiones cerrado")


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def probar_conexion():
    """
    Prueba la conexión a la base de datos
    
    Returns:
        bool: True si la conexión es exitosa
    """
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"📊 PostgreSQL Version: {version[0]}")
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"📊 Base de datos actual: {db_name[0]}")
            
            cursor.close()
            conexion.close()
            return True
        except psycopg2.Error as e:
            print(f"❌ Error al probar conexión: {e}")
            return False
    return False


def verificar_tabla(nombre_tabla='mensajes_mqtt'):
    """
    Verifica si una tabla existe en la base de datos
    
    Args:
        nombre_tabla: Nombre de la tabla a verificar
        
    Returns:
        bool: True si la tabla existe
    """
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (nombre_tabla,))
            existe = cursor.fetchone()[0]
            
            if existe:
                print(f"✅ Tabla '{nombre_tabla}' existe")
            else:
                print(f"⚠️ Tabla '{nombre_tabla}' NO existe")
            
            cursor.close()
            conexion.close()
            return existe
        except psycopg2.Error as e:
            print(f"❌ Error al verificar tabla: {e}")
            return False
    return False


def obtener_estadisticas():
    """
    Obtiene estadísticas básicas de la base de datos
    
    Returns:
        dict: Diccionario con estadísticas
    """
    conexion = crear_conexion()
    if conexion:
        try:
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
                SELECT timestamp_recepcion 
                FROM mensajes_mqtt 
                ORDER BY timestamp_recepcion DESC 
                LIMIT 1;
            """)
            ultimo_mensaje = cursor.fetchone()
            
            estadisticas = {
                'total_mensajes': total_mensajes,
                'mensajes_por_topico': mensajes_por_topico,
                'ultimo_mensaje': ultimo_mensaje[0] if ultimo_mensaje else None
            }
            
            cursor.close()
            conexion.close()
            return estadisticas
        except psycopg2.Error as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return None
    return None


# ============================================
# PRUEBA DEL MÓDULO
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("PRUEBA DE CONEXIÓN A POSTGRESQL")
    print("=" * 50)
    
    # Probar conexión
    if probar_conexion():
        print("\n✅ Conexión exitosa")
        
        # Verificar tabla
        verificar_tabla('mensajes_mqtt')
        
        # Obtener estadísticas
        print("\n📊 Estadísticas:")
        stats = obtener_estadisticas()
        if stats:
            print(f"   Total de mensajes: {stats['total_mensajes']}")
            print(f"   Último mensaje: {stats['ultimo_mensaje']}")
            print(f"   Mensajes por tópico:")
            for topico, cantidad in stats['mensajes_por_topico']:
                print(f"      {topico}: {cantidad}")
    else:
        print("\n❌ Error de conexión")
    
    print("=" * 50)
