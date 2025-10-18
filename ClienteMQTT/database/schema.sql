-- ============================================
-- SCHEMA POSTGRESQL PARA CLIENTE MQTT
-- Universidad Militar Nueva Granada
-- ============================================

-- Base de datos: SensoresMQTT
-- Usuario: postgres
-- Password: 2324Julibolt

-- ============================================
-- TABLA PRINCIPAL: mensajes_mqtt
-- ============================================

CREATE TABLE IF NOT EXISTS mensajes_mqtt (
    -- ID autoincremental como clave primaria
    id SERIAL PRIMARY KEY,
    
    -- Tópico MQTT del mensaje
    topico VARCHAR(255) NOT NULL,
    
    -- Contenido completo del mensaje (JSON)
    mensaje TEXT NOT NULL,
    
    -- Timestamp de llegada al cliente (automático)
    timestamp_llegada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ID del sensor que envió el mensaje
    sensor_id VARCHAR(100),
    
    -- Valor numérico extraído del mensaje (para consultas)
    valor_numerico DECIMAL(10,2),
    
    -- Unidad de medida del valor
    unidad VARCHAR(20),
    
    -- Información adicional
    ip_servidor INET,
    mensaje_procesado BOOLEAN DEFAULT TRUE
);

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS
-- ============================================

-- Índice en el tópico (búsquedas frecuentes por tópico)
CREATE INDEX IF NOT EXISTS idx_mensajes_topico 
ON mensajes_mqtt(topico);

-- Índice en timestamp_llegada (consultas temporales)
CREATE INDEX IF NOT EXISTS idx_mensajes_timestamp 
ON mensajes_mqtt(timestamp_llegada DESC);

-- Índice en sensor_id (seguimiento por sensor)
CREATE INDEX IF NOT EXISTS idx_mensajes_sensor 
ON mensajes_mqtt(sensor_id);

-- Índice compuesto para consultas complejas
CREATE INDEX IF NOT EXISTS idx_mensajes_topico_timestamp 
ON mensajes_mqtt(topico, timestamp_llegada DESC);

-- ============================================
-- VISTA PARA MENSAJES RECIENTES (ÚLTIMAS 24H)
-- ============================================

CREATE OR REPLACE VIEW mensajes_recientes AS
SELECT 
    id,
    topico,
    mensaje,
    timestamp_llegada,
    sensor_id,
    valor_numerico,
    unidad
FROM mensajes_mqtt
WHERE timestamp_llegada > NOW() - INTERVAL '24 hours'
ORDER BY timestamp_llegada DESC;

-- ============================================
-- VISTA PARA ESTADÍSTICAS POR TÓPICO
-- ============================================

CREATE OR REPLACE VIEW estadisticas_topicos AS
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
WHERE valor_numerico IS NOT NULL
GROUP BY topico
ORDER BY total_mensajes DESC;

-- ============================================
-- VISTA PARA ACTIVIDAD POR SENSOR
-- ============================================

CREATE OR REPLACE VIEW actividad_sensores AS
SELECT 
    sensor_id,
    COUNT(*) as total_mensajes,
    COUNT(DISTINCT topico) as topicos_diferentes,
    MIN(timestamp_llegada) as primer_mensaje,
    MAX(timestamp_llegada) as ultimo_mensaje,
    EXTRACT(EPOCH FROM (MAX(timestamp_llegada) - MIN(timestamp_llegada)))/60 as minutos_activo
FROM mensajes_mqtt
WHERE sensor_id IS NOT NULL
GROUP BY sensor_id
ORDER BY total_mensajes DESC;

-- ============================================
-- FUNCIÓN PARA LIMPIAR MENSAJES ANTIGUOS
-- ============================================

CREATE OR REPLACE FUNCTION limpiar_mensajes_antiguos(dias_antiguedad INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER;
BEGIN
    DELETE FROM mensajes_mqtt
    WHERE timestamp_llegada < NOW() - (dias_antiguedad || ' days')::INTERVAL;
    
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

-- Comentario de uso:
-- SELECT limpiar_mensajes_antiguos(30); -- Elimina mensajes de más de 30 días

-- ============================================
-- FUNCIÓN PARA OBTENER RESUMEN DEL DÍA
-- ============================================

CREATE OR REPLACE FUNCTION resumen_dia(fecha_consulta DATE DEFAULT CURRENT_DATE)
RETURNS TABLE(
    topico VARCHAR(255),
    cantidad_mensajes BIGINT,
    primer_mensaje TIMESTAMP,
    ultimo_mensaje TIMESTAMP,
    valor_promedio NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.topico,
        COUNT(*) as cantidad_mensajes,
        MIN(m.timestamp_llegada) as primer_mensaje,
        MAX(m.timestamp_llegada) as ultimo_mensaje,
        AVG(m.valor_numerico) as valor_promedio
    FROM mensajes_mqtt m
    WHERE DATE(m.timestamp_llegada) = fecha_consulta
    GROUP BY m.topico
    ORDER BY cantidad_mensajes DESC;
END;
$$ LANGUAGE plpgsql;

-- Comentario de uso:
-- SELECT * FROM resumen_dia(); -- Resumen del día actual
-- SELECT * FROM resumen_dia('2025-10-18'); -- Resumen de una fecha específica

-- ============================================
-- TABLA DE LOG DE CONEXIONES (OPCIONAL)
-- ============================================

CREATE TABLE IF NOT EXISTS log_conexiones (
    id SERIAL PRIMARY KEY,
    timestamp_conexion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cliente_id VARCHAR(100),
    servidor_mqtt VARCHAR(100),
    estado VARCHAR(50), -- 'conectado', 'desconectado', 'error'
    detalles TEXT
);

-- ============================================
-- CONSULTAS ÚTILES DOCUMENTADAS
-- ============================================

/*
-- Consultas de ejemplo para usar después de insertar datos:

-- 1. Ver últimos 10 mensajes
SELECT * FROM mensajes_mqtt ORDER BY timestamp_llegada DESC LIMIT 10;

-- 2. Contar mensajes por tópico
SELECT topico, COUNT(*) as cantidad FROM mensajes_mqtt GROUP BY topico ORDER BY cantidad DESC;

-- 3. Ver mensajes recientes (vista)
SELECT * FROM mensajes_recientes LIMIT 20;

-- 4. Estadísticas por tópico (vista)
SELECT * FROM estadisticas_topicos;

-- 5. Actividad por sensor (vista)
SELECT * FROM actividad_sensores;

-- 6. Mensajes de un sensor específico
SELECT * FROM mensajes_mqtt WHERE sensor_id = 'ESP32_01' ORDER BY timestamp_llegada DESC;

-- 7. Mensajes de un tópico específico en las últimas 24 horas
SELECT * FROM mensajes_mqtt 
WHERE topico LIKE 'incendio/%' 
AND timestamp_llegada > NOW() - INTERVAL '24 hours'
ORDER BY timestamp_llegada DESC;

-- 8. Promedio de valores por tópico
SELECT topico, AVG(valor_numerico) as promedio, COUNT(*) as cantidad
FROM mensajes_mqtt 
WHERE valor_numerico IS NOT NULL
GROUP BY topico;

-- 9. Resumen del día actual
SELECT * FROM resumen_dia();

-- 10. Último mensaje de cada tópico
SELECT DISTINCT ON (topico) topico, mensaje, timestamp_llegada, sensor_id
FROM mensajes_mqtt
ORDER BY topico, timestamp_llegada DESC;
*/

-- ============================================
-- COMENTARIOS FINALES
-- ============================================

-- Este schema está diseñado para:
-- 1. Almacenar todos los mensajes MQTT recibidos
-- 2. Facilitar consultas por tópico, sensor y tiempo
-- 3. Proporcionar vistas para análisis rápido
-- 4. Incluir funciones para mantenimiento
-- 5. Optimizar rendimiento con índices apropiados

-- Para ejecutar este archivo:
-- 1. Conectarse a PostgreSQL como usuario 'postgres'
-- 2. Crear base de datos: CREATE DATABASE "SensoresMQTT";
-- 3. Conectarse a la base: \c "SensoresMQTT"
-- 4. Ejecutar este archivo: \i schema.sql