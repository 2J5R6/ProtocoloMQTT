-- ============================================
-- SCHEMA SQL PARA TALLER MQTT
-- Universidad Militar Nueva Granada
-- Base de Datos: mqtt_taller
-- ============================================

-- Conectar a PostgreSQL como superusuario y ejecutar:
-- CREATE DATABASE mqtt_taller;
-- CREATE USER mqtt_admin WITH PASSWORD 'mqtt_secure_2025';
-- GRANT ALL PRIVILEGES ON DATABASE mqtt_taller TO mqtt_admin;

-- Luego conectar a la base de datos mqtt_taller:
-- \c mqtt_taller

-- ============================================
-- TABLA PRINCIPAL: mensajes_mqtt
-- ============================================
CREATE TABLE IF NOT EXISTS mensajes_mqtt (
    -- ID autoincremental
    id SERIAL PRIMARY KEY,
    
    -- Información del tópico MQTT
    topico VARCHAR(255) NOT NULL,
    
    -- Contenido del mensaje (formato JSON)
    mensaje TEXT NOT NULL,
    
    -- Timestamp de recepción (automático)
    timestamp_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Información del sensor
    sensor_id VARCHAR(100),
    
    -- Valor numérico extraído (para facilitar consultas)
    valor_numerico DECIMAL(10,2),
    
    -- Unidad de medida
    unidad VARCHAR(20),
    
    -- Metadata adicional (opcional)
    ip_origen INET,
    
    -- Estado del mensaje
    procesado BOOLEAN DEFAULT FALSE
);

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================

-- Índice en tópico (búsquedas frecuentes por tópico)
CREATE INDEX idx_topico ON mensajes_mqtt(topico);

-- Índice en timestamp (consultas temporales)
CREATE INDEX idx_timestamp ON mensajes_mqtt(timestamp_recepcion DESC);

-- Índice en sensor_id (seguimiento por sensor)
CREATE INDEX idx_sensor_id ON mensajes_mqtt(sensor_id);

-- Índice compuesto (tópico + timestamp)
CREATE INDEX idx_topico_timestamp ON mensajes_mqtt(topico, timestamp_recepcion DESC);

-- Índice para mensajes no procesados
CREATE INDEX idx_procesado ON mensajes_mqtt(procesado) WHERE procesado = FALSE;

-- ============================================
-- TABLA DE ESTADÍSTICAS (OPCIONAL)
-- ============================================
CREATE TABLE IF NOT EXISTS estadisticas_sensores (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(100) NOT NULL,
    topico VARCHAR(255) NOT NULL,
    total_mensajes INTEGER DEFAULT 0,
    ultimo_mensaje TIMESTAMP,
    valor_promedio DECIMAL(10,2),
    valor_minimo DECIMAL(10,2),
    valor_maximo DECIMAL(10,2),
    UNIQUE(sensor_id, topico)
);

-- ============================================
-- VISTA PARA MENSAJES RECIENTES
-- ============================================
CREATE OR REPLACE VIEW mensajes_recientes AS
SELECT 
    id,
    topico,
    mensaje,
    timestamp_recepcion,
    sensor_id,
    valor_numerico,
    unidad
FROM mensajes_mqtt
WHERE timestamp_recepcion > NOW() - INTERVAL '24 hours'
ORDER BY timestamp_recepcion DESC;

-- ============================================
-- VISTA PARA ESTADÍSTICAS POR TÓPICO
-- ============================================
CREATE OR REPLACE VIEW estadisticas_topicos AS
SELECT 
    topico,
    COUNT(*) as total_mensajes,
    COUNT(DISTINCT sensor_id) as sensores_unicos,
    MIN(timestamp_recepcion) as primer_mensaje,
    MAX(timestamp_recepcion) as ultimo_mensaje,
    AVG(valor_numerico) as valor_promedio,
    MIN(valor_numerico) as valor_minimo,
    MAX(valor_numerico) as valor_maximo
FROM mensajes_mqtt
GROUP BY topico
ORDER BY total_mensajes DESC;

-- ============================================
-- FUNCIÓN PARA LIMPIAR MENSAJES ANTIGUOS
-- ============================================
CREATE OR REPLACE FUNCTION limpiar_mensajes_antiguos(dias INTEGER)
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER;
BEGIN
    DELETE FROM mensajes_mqtt
    WHERE timestamp_recepcion < NOW() - (dias || ' days')::INTERVAL;
    
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

-- Ejemplo de uso:
-- SELECT limpiar_mensajes_antiguos(30); -- Elimina mensajes de más de 30 días

-- ============================================
-- PERMISOS PARA USUARIO mqtt_admin
-- ============================================
GRANT ALL PRIVILEGES ON TABLE mensajes_mqtt TO mqtt_admin;
GRANT ALL PRIVILEGES ON TABLE estadisticas_sensores TO mqtt_admin;
GRANT USAGE, SELECT ON SEQUENCE mensajes_mqtt_id_seq TO mqtt_admin;
GRANT USAGE, SELECT ON SEQUENCE estadisticas_sensores_id_seq TO mqtt_admin;
GRANT SELECT ON mensajes_recientes TO mqtt_admin;
GRANT SELECT ON estadisticas_topicos TO mqtt_admin;

-- ============================================
-- CONSULTAS ÚTILES
-- ============================================

-- Ver últimos 10 mensajes
-- SELECT * FROM mensajes_mqtt ORDER BY timestamp_recepcion DESC LIMIT 10;

-- Contar mensajes por tópico
-- SELECT topico, COUNT(*) FROM mensajes_mqtt GROUP BY topico;

-- Mensajes de las últimas 24 horas
-- SELECT * FROM mensajes_recientes;

-- Estadísticas por tópico
-- SELECT * FROM estadisticas_topicos;

-- Buscar mensajes de un sensor específico
-- SELECT * FROM mensajes_mqtt WHERE sensor_id = 'ESP32_01' ORDER BY timestamp_recepcion DESC;
