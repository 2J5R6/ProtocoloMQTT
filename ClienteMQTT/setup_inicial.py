"""
============================================
CONFIGURACIÓN INICIAL DEL SISTEMA
Cliente MQTT - Universidad Militar Nueva Granada
============================================

Este script automatiza la configuración inicial completa del sistema:
1. Verificación de PostgreSQL
2. Creación de base de datos "SensoresMQTT"
3. Creación de tablas y esquema
4. Configuración de variables de entorno
5. Verificación de conectividad MQTT

Credenciales del sistema:
- Usuario PostgreSQL: postgres
- Contraseña: 2324Julibolt
- Base de datos: SensoresMQTT

Uso:
    python setup_inicial.py
"""

import psycopg2
import os
import sys
import subprocess
import shutil
from dotenv import load_dotenv

# ============================================
# CONFIGURACIÓN
# ============================================

# Credenciales según especificaciones del usuario
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '2324Julibolt',
    'database': 'SensoresMQTT'
}

# Configuración por defecto para el archivo .env
DEFAULT_ENV_CONFIG = {
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'SensoresMQTT',
    'DB_USER': 'postgres',
    'DB_PASSWORD': '2324Julibolt',
    'MQTT_BROKER': '192.168.1.100',  # Cambiar por IP real del servidor
    'MQTT_PORT': '1883',
    'MQTT_USERNAME': '',
    'MQTT_PASSWORD': '',
    'CLIENT_ID': 'cliente_admin_umng'
}

# ============================================
# FUNCIONES DE VERIFICACIÓN
# ============================================

def verificar_postgresql():
    """
    Verifica si PostgreSQL está instalado y funcionando
    
    Returns:
        bool: True si PostgreSQL está disponible
    """
    try:
        # Intentar conectar con PostgreSQL
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG['host'],
            port=POSTGRES_CONFIG['port'],
            user=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password'],
            database='postgres'  # Base de datos por defecto
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL está funcionando")
        print(f"   Versión: {version}")
        return True
        
    except psycopg2.OperationalError as e:
        print("❌ Error conectando a PostgreSQL:")
        print(f"   {e}")
        print("\n🔧 Verifica que:")
        print("   1. PostgreSQL está instalado")
        print("   2. El servicio está iniciado")
        print("   3. El usuario 'postgres' existe")
        print("   4. La contraseña '2324Julibolt' es correcta")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def verificar_python_packages():
    """
    Verifica si las librerías Python necesarias están instaladas
    
    Returns:
        bool: True si todas las librerías están disponibles
    """
    required_packages = ['paho-mqtt', 'psycopg2', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'paho-mqtt':
                import paho.mqtt.client
            elif package == 'psycopg2':
                import psycopg2
            elif package == 'python-dotenv':
                import dotenv
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Faltan librerías Python:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 Para instalar:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas las librerías Python están instaladas")
        return True


# ============================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================

def crear_base_datos():
    """
    Crea la base de datos SensoresMQTT si no existe
    
    Returns:
        bool: True si la base de datos fue creada o ya existe
    """
    try:
        # Conectar a PostgreSQL (base por defecto)
        conn = psycopg2.connect(
            host=POSTGRES_CONFIG['host'],
            port=POSTGRES_CONFIG['port'],
            user=POSTGRES_CONFIG['user'],
            password=POSTGRES_CONFIG['password'],
            database='postgres'
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar si la base de datos ya existe
        cursor.execute("""
            SELECT 1 FROM pg_database 
            WHERE datname = %s;
        """, (POSTGRES_CONFIG['database'],))
        
        if cursor.fetchone():
            print("✅ Base de datos 'SensoresMQTT' ya existe")
        else:
            # Crear base de datos
            cursor.execute(f'CREATE DATABASE "{POSTGRES_CONFIG["database"]}";')
            print("✅ Base de datos 'SensoresMQTT' creada exitosamente")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False


def crear_esquema_tablas():
    """
    Crea las tablas y esquema en la base de datos
    
    Returns:
        bool: True si el esquema fue creado exitosamente
    """
    try:
        # Conectar a la base de datos específica
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        # Leer y ejecutar el archivo schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"❌ No se encontró el archivo schema.sql en {schema_path}")
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Ejecutar el esquema
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Esquema de base de datos creado exitosamente")
        
        # Verificar que las tablas se crearon
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        
        tablas = cursor.fetchall()
        print("📊 Tablas creadas:")
        for tabla in tablas:
            print(f"   - {tabla[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creando esquema: {e}")
        return False


def crear_archivo_env():
    """
    Crea el archivo .env con la configuración por defecto
    
    Returns:
        bool: True si el archivo fue creado exitosamente
    """
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Si ya existe, preguntar si sobrescribir
        if os.path.exists(env_path):
            respuesta = input("El archivo .env ya existe. ¿Sobrescribir? (s/N): ")
            if respuesta.lower() != 's':
                print("ℹ️  Manteniendo archivo .env existente")
                return True
        
        # Crear archivo .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# ============================================\n")
            f.write("# CONFIGURACIÓN CLIENTE MQTT\n")
            f.write("# Generado automáticamente por setup_inicial.py\n")
            f.write("# ============================================\n\n")
            
            for key, value in DEFAULT_ENV_CONFIG.items():
                f.write(f"{key}={value}\n")
            
            f.write("\n# IMPORTANTE: Cambiar MQTT_BROKER por la IP real del servidor\n")
        
        print("✅ Archivo .env creado exitosamente")
        print(f"📁 Ubicación: {env_path}")
        print("⚠️  IMPORTANTE: Edita el archivo .env y cambia MQTT_BROKER por la IP real del servidor")
        return True
        
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False


def verificar_conectividad_mqtt():
    """
    Intenta verificar conectividad al servidor MQTT
    
    Returns:
        bool: True si puede conectar (opcional)
    """
    try:
        import paho.mqtt.client as mqtt
        
        # Cargar configuración
        load_dotenv()
        broker = os.getenv('MQTT_BROKER', '192.168.1.100')
        port = int(os.getenv('MQTT_PORT', 1883))
        
        print(f"🔄 Probando conectividad MQTT a {broker}:{port}...")
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✅ Conectividad MQTT exitosa")
                client.disconnect()
            else:
                print(f"❌ Error de conexión MQTT: {rc}")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        # Timeout corto para la prueba
        client.connect(broker, port, 5)
        client.loop_start()
        
        import time
        time.sleep(2)  # Esperar respuesta
        
        client.loop_stop()
        return True
        
    except Exception as e:
        print(f"⚠️  No se pudo verificar conectividad MQTT: {e}")
        print("   Esto es normal si el servidor aún no está disponible")
        return False


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal del setup"""
    print("=" * 60)
    print("🚀 CONFIGURACIÓN INICIAL - CLIENTE MQTT")
    print("   Universidad Militar Nueva Granada")
    print("=" * 60)
    print("📋 Este script configurará:")
    print("   1. Base de datos PostgreSQL 'SensoresMQTT'")
    print("   2. Esquema de tablas")
    print("   3. Archivo de configuración .env")
    print("   4. Verificación de dependencias")
    print("=" * 60 + "\n")
    
    exito_total = True
    
    # Paso 1: Verificar librerías Python
    print("1️⃣ Verificando librerías Python...")
    if not verificar_python_packages():
        exito_total = False
        print("⚠️  Instala las dependencias antes de continuar\n")
    print()
    
    # Paso 2: Verificar PostgreSQL
    print("2️⃣ Verificando PostgreSQL...")
    if not verificar_postgresql():
        exito_total = False
        print("⚠️  Configura PostgreSQL antes de continuar\n")
    print()
    
    # Paso 3: Crear base de datos
    if exito_total:
        print("3️⃣ Creando base de datos...")
        if not crear_base_datos():
            exito_total = False
        print()
    
    # Paso 4: Crear esquema
    if exito_total:
        print("4️⃣ Creando esquema de tablas...")
        if not crear_esquema_tablas():
            exito_total = False
        print()
    
    # Paso 5: Crear archivo .env
    print("5️⃣ Creando archivo de configuración...")
    crear_archivo_env()  # No es crítico si falla
    print()
    
    # Paso 6: Verificar MQTT (opcional)
    print("6️⃣ Verificando conectividad MQTT...")
    verificar_conectividad_mqtt()  # No es crítico
    print()
    
    # Resumen final
    print("=" * 60)
    if exito_total:
        print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("✅ Sistema listo para usar")
        print("\n📝 Próximos pasos:")
        print("   1. Editar archivo .env con la IP real del servidor MQTT")
        print("   2. Ejecutar: python suscriptor/suscriptor_admin.py")
        print("   3. Verificar que los mensajes se almacenan en la BD")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("=" * 60)
        print("⚠️  Resolver los errores antes de continuar")
    
    print("=" * 60)


if __name__ == "__main__":
    main()