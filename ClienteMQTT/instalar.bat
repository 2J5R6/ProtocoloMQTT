@echo off
REM ============================================
REM SCRIPT DE INSTALACIÓN RÁPIDA - WINDOWS
REM Cliente MQTT - Universidad Militar Nueva Granada
REM ============================================

echo ============================================
echo 🚀 INSTALACIÓN CLIENTE MQTT
echo    Universidad Militar Nueva Granada
echo ============================================

REM Verificar Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo 📦 Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% encontrado

REM Verificar pip
echo 🔍 Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip no está disponible
    echo 📦 Ejecuta: python -m ensurepip --upgrade
    pause
    exit /b 1
)

echo ✅ pip encontrado

REM Instalar dependencias
echo 📦 Instalando dependencias Python...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Dependencias instaladas correctamente
) else (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

REM Crear archivo .env si no existe
if not exist .env (
    echo 📄 Creando archivo .env...
    copy .env.example .env >nul
    echo ✅ Archivo .env creado
    echo ⚠️  IMPORTANTE: Edita .env y cambia MQTT_BROKER por la IP del servidor
) else (
    echo ℹ️  Archivo .env ya existe
)

REM Ejecutar configuración inicial
echo 🔧 Ejecutando configuración inicial...
python setup_inicial.py

echo.
echo ============================================
echo 🎉 INSTALACIÓN COMPLETADA
echo ============================================
echo 📝 Próximos pasos:
echo    1. Editar archivo .env con IP del servidor MQTT
echo    2. Ejecutar: python suscriptor/suscriptor_admin.py
echo    3. Consultar datos: python consultar_datos.py
echo ============================================
pause