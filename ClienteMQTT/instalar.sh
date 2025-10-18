#!/bin/bash

# ============================================
# SCRIPT DE INSTALACIÓN RÁPIDA
# Cliente MQTT - Universidad Militar Nueva Granada
# ============================================

echo "============================================"
echo "🚀 INSTALACIÓN CLIENTE MQTT"
echo "   Universidad Militar Nueva Granada"
echo "============================================"

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "📦 Instala Python desde: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION encontrado"

# Verificar pip
echo "🔍 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip no está disponible"
    echo "📦 Instala pip: python3 -m ensurepip --upgrade"
    exit 1
fi

echo "✅ pip encontrado"

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas correctamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📄 Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita .env y cambia MQTT_BROKER por la IP del servidor"
else
    echo "ℹ️  Archivo .env ya existe"
fi

# Ejecutar configuración inicial
echo "🔧 Ejecutando configuración inicial..."
python3 setup_inicial.py

echo ""
echo "============================================"
echo "🎉 INSTALACIÓN COMPLETADA"
echo "============================================"
echo "📝 Próximos pasos:"
echo "   1. Editar archivo .env con IP del servidor MQTT"
echo "   2. Ejecutar: python3 suscriptor/suscriptor_admin.py"
echo "   3. Consultar datos: python3 consultar_datos.py"
echo "============================================"