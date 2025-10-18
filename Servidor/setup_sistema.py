#!/usr/bin/env python3
"""
Script de Configuración Automática del Sistema MQTT
Universidad Militar Nueva Granada - Taller de Comunicaciones

Este script configura automáticamente:
1. Servidor MQTT (Docker/Mosquitto)
2. Base de datos PostgreSQL
3. Verificación de servicios
4. Creación de tablas y esquema

Uso: python setup_sistema.py
o desde el venv: .venv/bin/python setup_sistema.py
"""

import subprocess
import sys
import os
import time
import psycopg2
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime un encabezado con formato"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(step_num, total, text):
    """Imprime el paso actual"""
    print(f"{Colors.OKCYAN}[{step_num}/{total}]{Colors.ENDC} {Colors.BOLD}{text}{Colors.ENDC}")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    """Imprime información"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def run_command(command, shell=True, check=True, capture_output=True):
    """Ejecuta un comando del sistema y retorna el resultado"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_docker_installed():
    """Verifica si Docker está instalado"""
    print_step(1, 7, "Verificando instalación de Docker...")
    success, stdout, stderr = run_command("docker --version")
    
    if success:
        version = stdout.strip()
        print_success(f"Docker instalado: {version}")
        return True
    else:
        print_error("Docker no está instalado")
        print_info("Instalar con: sudo apt update && sudo apt install -y docker.io")
        return False

def check_postgresql_installed():
    """Verifica si PostgreSQL está instalado"""
    print_step(2, 7, "Verificando instalación de PostgreSQL...")
    success, stdout, stderr = run_command("psql --version")
    
    if success:
        version = stdout.strip()
        print_success(f"PostgreSQL instalado: {version}")
        return True
    else:
        print_error("PostgreSQL no está instalado")
        print_info("Instalar con: sudo apt update && sudo apt install -y postgresql postgresql-contrib")
        return False

def setup_mqtt_broker():
    """Configura y arranca el broker MQTT usando Docker"""
    print_step(3, 7, "Configurando servidor MQTT (Mosquitto)...")
    
    # Verificar si el contenedor ya existe
    success, stdout, stderr = run_command("sudo docker ps -a --filter name=mqtt-server --format '{{.Names}}'")
    
    if "mqtt-server" in stdout:
        print_info("Contenedor mqtt-server ya existe")
        
        # Verificar si está corriendo
        success, stdout, stderr = run_command("sudo docker ps --filter name=mqtt-server --format '{{.Names}}'")
        
        if "mqtt-server" in stdout:
            print_success("Servidor MQTT ya está corriendo")
            return True
        else:
            print_info("Iniciando contenedor existente...")
            success, stdout, stderr = run_command("sudo docker start mqtt-server")
            
            if success:
                print_success("Servidor MQTT iniciado")
                return True
            else:
                print_error(f"Error al iniciar contenedor: {stderr}")
                return False
    else:
        print_info("Creando nuevo contenedor MQTT...")
        
        # Cambiar al directorio del broker
        broker_dir = Path(__file__).parent / "broker"
        
        if not broker_dir.exists():
            print_error(f"Directorio broker/ no encontrado: {broker_dir}")
            return False
        
        os.chdir(broker_dir)
        
        # Ejecutar docker-compose
        success, stdout, stderr = run_command("sudo docker-compose up -d")
        
        if success:
            print_success("Servidor MQTT creado e iniciado")
            time.sleep(3)  # Esperar a que el servicio esté listo
            return True
        else:
            print_error(f"Error al crear contenedor MQTT: {stderr}")
            return False

def check_postgresql_service():
    """Verifica y arranca el servicio PostgreSQL"""
    print_step(4, 7, "Verificando servicio PostgreSQL...")
    
    # Verificar estado del servicio
    success, stdout, stderr = run_command("sudo systemctl is-active postgresql")
    
    if "active" in stdout:
        print_success("Servicio PostgreSQL está activo")
        return True
    else:
        print_info("Iniciando servicio PostgreSQL...")
        success, stdout, stderr = run_command("sudo systemctl start postgresql")
        
        if success:
            print_success("Servicio PostgreSQL iniciado")
            time.sleep(2)
            return True
        else:
            print_error(f"Error al iniciar PostgreSQL: {stderr}")
            return False

def setup_database():
    """Configura la base de datos PostgreSQL"""
    print_step(5, 7, "Configurando base de datos PostgreSQL...")
    
    try:
        # Verificar si el usuario mqtt_admin ya existe
        print_info("Verificando usuario mqtt_admin...")
        check_user_cmd = "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='mqtt_admin'\""
        success, stdout, stderr = run_command(check_user_cmd)
        
        if "1" not in stdout:
            print_info("Creando usuario mqtt_admin...")
            create_user_cmd = "sudo -u postgres psql -c \"CREATE USER mqtt_admin WITH PASSWORD 'mqtt_secure_2025';\""
            success, stdout, stderr = run_command(create_user_cmd)
            
            if success:
                print_success("Usuario mqtt_admin creado")
            else:
                print_warning("El usuario ya existe o hubo un error")
        else:
            print_success("Usuario mqtt_admin ya existe")
        
        # Verificar si la base de datos ya existe
        print_info("Verificando base de datos mqtt_taller...")
        check_db_cmd = "sudo -u postgres psql -tAc \"SELECT 1 FROM pg_database WHERE datname='mqtt_taller'\""
        success, stdout, stderr = run_command(check_db_cmd)
        
        if "1" not in stdout:
            print_info("Creando base de datos mqtt_taller...")
            create_db_cmd = "sudo -u postgres psql -c \"CREATE DATABASE mqtt_taller OWNER mqtt_admin;\""
            success, stdout, stderr = run_command(create_db_cmd)
            
            if success:
                print_success("Base de datos mqtt_taller creada")
            else:
                print_error(f"Error al crear base de datos: {stderr}")
                return False
        else:
            print_success("Base de datos mqtt_taller ya existe")
        
        # Otorgar privilegios
        print_info("Otorgando privilegios...")
        grant_cmd = "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE mqtt_taller TO mqtt_admin;\""
        run_command(grant_cmd, check=False)
        
        return True
        
    except Exception as e:
        print_error(f"Error en configuración de base de datos: {e}")
        return False

def create_database_schema():
    """Crea el esquema de la base de datos"""
    print_step(6, 7, "Creando esquema de base de datos...")
    
    schema_file = Path(__file__).parent / "database" / "schema.sql"
    
    if not schema_file.exists():
        print_error(f"Archivo schema.sql no encontrado: {schema_file}")
        return False
    
    print_info(f"Ejecutando {schema_file}...")
    
    # Leer el archivo SQL
    with open(schema_file, 'r') as f:
        sql_content = f.read()
    
    # Ejecutar el SQL usando psycopg2
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mqtt_taller",
            user="mqtt_admin",
            password="mqtt_secure_2025"
        )
        cursor = conn.cursor()
        
        # Ejecutar el script SQL
        cursor.execute(sql_content)
        conn.commit()
        
        print_success("Esquema de base de datos creado exitosamente")
        
        # Verificar que las tablas se crearon
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if tables:
            print_info("Tablas creadas:")
            for table in tables:
                print(f"   • {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print_error(f"Error al crear esquema: {e}")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return False

def verify_services():
    """Verifica que todos los servicios estén funcionando"""
    print_step(7, 7, "Verificando servicios...")
    
    all_ok = True
    
    # Verificar MQTT
    print_info("Verificando MQTT broker...")
    success, stdout, stderr = run_command("sudo docker ps --filter name=mqtt-server --format '{{.Status}}'")
    
    if success and "Up" in stdout:
        print_success("✓ MQTT broker: Funcionando")
    else:
        print_error("✗ MQTT broker: No funciona")
        all_ok = False
    
    # Verificar PostgreSQL
    print_info("Verificando PostgreSQL...")
    success, stdout, stderr = run_command("sudo systemctl is-active postgresql")
    
    if "active" in stdout:
        print_success("✓ PostgreSQL: Funcionando")
    else:
        print_error("✗ PostgreSQL: No funciona")
        all_ok = False
    
    # Verificar conexión a base de datos
    print_info("Verificando conexión a base de datos...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mqtt_taller",
            user="mqtt_admin",
            password="mqtt_secure_2025",
            connect_timeout=5
        )
        conn.close()
        print_success("✓ Conexión a base de datos: OK")
    except Exception as e:
        print_error(f"✗ Conexión a base de datos: Error - {e}")
        all_ok = False
    
    # Verificar puerto MQTT
    print_info("Verificando puerto MQTT 1883...")
    success, stdout, stderr = run_command("sudo netstat -tuln | grep 1883 || sudo ss -tuln | grep 1883")
    
    if success and ("1883" in stdout):
        print_success("✓ Puerto MQTT 1883: Abierto")
    else:
        print_warning("⚠ Puerto MQTT 1883: No detectado (puede ser normal)")
    
    return all_ok

def print_summary():
    """Imprime un resumen de la configuración"""
    print_header("RESUMEN DE CONFIGURACIÓN")
    
    print(f"{Colors.BOLD}Servicios Configurados:{Colors.ENDC}")
    print(f"  🐳 Docker MQTT Broker: {Colors.OKGREEN}mqtt-server{Colors.ENDC} (puerto 1883)")
    print(f"  🗄️  PostgreSQL Database: {Colors.OKGREEN}mqtt_taller{Colors.ENDC}")
    print(f"  👤 Usuario Base de Datos: {Colors.OKGREEN}mqtt_admin{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Comandos Útiles:{Colors.ENDC}")
    print(f"  Ver logs MQTT:    {Colors.OKCYAN}sudo docker logs -f mqtt-server{Colors.ENDC}")
    print(f"  Test MQTT:        {Colors.OKCYAN}mosquitto_sub -h localhost -t 'sensores/#' -v{Colors.ENDC}")
    print(f"  Consultar DB:     {Colors.OKCYAN}.venv/bin/python consultar_db.py{Colors.ENDC}")
    print(f"  Iniciar sensores: {Colors.OKCYAN}.venv/bin/python sensores/sensor_simulator.py{Colors.ENDC}")
    print(f"  Suscriptor admin: {Colors.OKCYAN}.venv/bin/python suscriptores/suscriptor_admin.py{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Archivos de Configuración:{Colors.ENDC}")
    print(f"  .env              Configuración de variables de entorno")
    print(f"  STARTUP.md        Guía de inicio del sistema")
    print(f"  TESTING.md        Guía de pruebas")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Sistema listo para usar!{Colors.ENDC}\n")

def main():
    """Función principal"""
    print_header("CONFIGURACIÓN AUTOMÁTICA DEL SISTEMA MQTT")
    print(f"{Colors.BOLD}Universidad Militar Nueva Granada{Colors.ENDC}")
    print(f"{Colors.BOLD}Taller de Comunicaciones - 50% Corte 2{Colors.ENDC}\n")
    
    # Lista para rastrear el éxito de cada paso
    steps_success = []
    
    # 1. Verificar Docker
    steps_success.append(check_docker_installed())
    if not steps_success[-1]:
        print_error("No se puede continuar sin Docker")
        sys.exit(1)
    
    # 2. Verificar PostgreSQL
    steps_success.append(check_postgresql_installed())
    if not steps_success[-1]:
        print_error("No se puede continuar sin PostgreSQL")
        sys.exit(1)
    
    # 3. Configurar MQTT
    steps_success.append(setup_mqtt_broker())
    if not steps_success[-1]:
        print_error("Error al configurar MQTT broker")
        sys.exit(1)
    
    # 4. Verificar servicio PostgreSQL
    steps_success.append(check_postgresql_service())
    if not steps_success[-1]:
        print_error("Error al verificar servicio PostgreSQL")
        sys.exit(1)
    
    # 5. Configurar base de datos
    steps_success.append(setup_database())
    if not steps_success[-1]:
        print_error("Error al configurar base de datos")
        sys.exit(1)
    
    # 6. Crear esquema
    steps_success.append(create_database_schema())
    if not steps_success[-1]:
        print_warning("Esquema no creado (puede que ya exista)")
    
    # 7. Verificar servicios
    steps_success.append(verify_services())
    
    # Resumen final
    if all(steps_success):
        print_summary()
        sys.exit(0)
    else:
        print_header("CONFIGURACIÓN COMPLETADA CON ADVERTENCIAS")
        print_warning("Algunos pasos tuvieron advertencias. Verifica los mensajes arriba.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Configuración cancelada por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
