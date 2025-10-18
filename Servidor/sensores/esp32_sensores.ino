/*
 * ============================================
 * ESP32-S3 - SENSORES MQTT CON POTENCIÓMETROS
 * Taller Comunicaciones - Universidad Militar Nueva Granada
 * ============================================
 * 
 * Este código implementa un sistema de sensores simulados con 
 * POTENCIÓMETROS en ESP32-S3 que publica datos a un broker MQTT.
 * 
 * FORMATO JSON (compatible con suscriptor_admin.py):
 * {
 *   "device_id": "ESP32_01",
 *   "value": 25.5,
 *   "unit": "°C",
 *   "status": "normal",    (opcional)
 *   "timestamp": 12345
 * }
 * 
 * POTENCIÓMETROS IMPLEMENTADOS (8 sensores):
 * 1. GPIO 1 (ADC1_CH0) -> Temperatura (0-50°C) -> clima/temperatura
 * 2. GPIO 2 (ADC1_CH1) -> Humedad (0-100%) -> clima/humedad
 * 3. GPIO 3 (ADC1_CH2) -> Humo (0-100%) -> incendio/sensor_humo
 * 4. GPIO 4 (ADC1_CH3) -> Luz (0-100%) -> iluminacion/luz
 * 5. GPIO 5 (ADC1_CH4) -> Movimiento (digital simulado) -> seguridad/movimiento
 * 6. GPIO 6 (ADC1_CH5) -> Puerta (digital simulado) -> seguridad/puerta
 * 7. GPIO 7 (ADC1_CH6) -> Alarma (>80% activa) -> incendio/alarma
 * 8. GPIO 8 (ADC1_CH7) -> Viento (0-100 km/h) -> clima/viento
 * 
 * HARDWARE: ESP32-S3 DevKit
 * ADC Resolución: 12 bits (0-4095)
 * ============================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURACIÓN WIFI
// ============================================
const char* ssid = "TuRedWiFi";           // Cambiar por tu SSID
const char* password = "TuPassword";       // Cambiar por tu contraseña

// ============================================
// CONFIGURACIÓN MQTT
// ============================================
const char* mqtt_server = "192.168.1.100"; // IP del servidor Kali Linux
const int mqtt_port = 1883;
const char* mqtt_user = "";                // Dejar vacío si allow_anonymous = true
const char* mqtt_password = "";
const char* device_id = "ESP32_01";

// ============================================
// PINES DE SENSORES - ESP32-S3 (POTENCIÓMETROS)
// ============================================
// IMPORTANTE: ESP32-S3 tiene ADC1 (GPIO 1-10) y ADC2 (GPIO 11-20)
// Usamos ADC1 para evitar conflictos con WiFi

#define TEMP_POT_PIN 1          // ADC1_CH0 - Potenciómetro Temperatura (0-100°C)
#define HUM_POT_PIN 2           // ADC1_CH1 - Potenciómetro Humedad (0-100%)
#define HUMO_POT_PIN 3          // ADC1_CH2 - Potenciómetro Humo (0-100%)
#define LUZ_POT_PIN 4           // ADC1_CH3 - Potenciómetro Luz (0-100%)
#define MOV_POT_PIN 5           // ADC1_CH4 - Potenciómetro Movimiento (0=no, >50%=sí)
#define PUERTA_POT_PIN 6        // ADC1_CH5 - Potenciómetro Puerta (0=cerrada, >50%=abierta)
#define ALARMA_POT_PIN 7        // ADC1_CH6 - Potenciómetro Alarma (>80%=activada)
#define VIENTO_POT_PIN 8        // ADC1_CH7 - Potenciómetro Viento (0-100 km/h) - OPCIONAL

#define LED_STATUS 48           // LED RGB integrado en ESP32-S3

// ============================================
// TÓPICOS MQTT
// ============================================
const char* TOPIC_TEMPERATURA = "clima/temperatura";
const char* TOPIC_HUMEDAD = "clima/humedad";
const char* TOPIC_VIENTO = "clima/viento";
const char* TOPIC_HUMO = "incendio/sensor_humo";
const char* TOPIC_ALARMA = "incendio/alarma";
const char* TOPIC_PUERTA = "seguridad/puerta";
const char* TOPIC_MOVIMIENTO = "seguridad/movimiento";
const char* TOPIC_LUZ = "iluminacion/luz";
const char* TOPIC_STATUS = "sistema/estado";

// ============================================
// OBJETOS GLOBALES
// ============================================
WiFiClient espClient;
PubSubClient client(espClient);

// ============================================
// VARIABLES GLOBALES
// ============================================
unsigned long lastMsg = 0;
unsigned long lastStatusMsg = 0;
const long interval = 5000;        // Intervalo de publicación (5 segundos)
const long statusInterval = 30000; // Intervalo de estado (30 segundos)

// Resolución ADC del ESP32-S3: 12 bits (0-4095)
const int ADC_RESOLUTION = 4095;

// ============================================
// CONFIGURACIÓN INICIAL
// ============================================
void setup() {
  Serial.begin(115200);
  Serial.println("\n============================================");
  Serial.println("ESP32 - SENSORES MQTT");
  Serial.println("Universidad Militar Nueva Granada");
  Serial.println("============================================\n");

  // Configurar pines ADC (potenciómetros)
  pinMode(TEMP_POT_PIN, INPUT);
  pinMode(HUM_POT_PIN, INPUT);
  pinMode(HUMO_POT_PIN, INPUT);
  pinMode(LUZ_POT_PIN, INPUT);
  pinMode(MOV_POT_PIN, INPUT);
  pinMode(PUERTA_POT_PIN, INPUT);
  pinMode(ALARMA_POT_PIN, INPUT);
  pinMode(VIENTO_POT_PIN, INPUT);
  pinMode(LED_STATUS, OUTPUT);

  // Configurar resolución ADC (12 bits = 0-4095)
  analogReadResolution(12);
  Serial.println("✅ Pines ADC configurados (8 potenciómetros)");

  // Conectar WiFi
  setup_wifi();

  // Configurar MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  Serial.println("\n✅ Sistema listo");
  digitalWrite(LED_STATUS, HIGH);
}

// ============================================
// CONEXIÓN WIFI
// ============================================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_STATUS, !digitalRead(LED_STATUS));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi conectado");
    Serial.print("📡 Dirección IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("📶 Intensidad señal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n❌ Error: No se pudo conectar a WiFi");
  }
}

// ============================================
// CALLBACK MQTT (RECEPCIÓN)
// ============================================
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("📩 Mensaje recibido [");
  Serial.print(topic);
  Serial.print("]: ");
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
}

// ============================================
// RECONEXIÓN MQTT
// ============================================
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT...");
    
    String clientId = String(device_id) + "-" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println(" ✅ Conectado");
      
      // Publicar mensaje de conexión
      publishStatus("online");
      
      // Suscribirse a tópicos si es necesario
      // client.subscribe("incendio/activar_sirena");
      
    } else {
      Serial.print(" ❌ Error, rc=");
      Serial.print(client.state());
      Serial.println(" Reintentando en 5s...");
      digitalWrite(LED_STATUS, LOW);
      delay(5000);
    }
  }
  digitalWrite(LED_STATUS, HIGH);
}

// ============================================
// PUBLICAR MENSAJE JSON
// ============================================
void publishSensor(const char* topic, const char* tipo, float valor, const char* unidad, const char* estado = "") {
  StaticJsonDocument<256> doc;
  
  // Formato compatible con el simulador y suscriptor_admin.py
  doc["device_id"] = device_id;  // Cambio: sensor_id -> device_id
  doc["value"] = valor;           // Cambio: valor -> value
  doc["unit"] = unidad;           // Cambio: unidad -> unit
  
  if (strlen(estado) > 0) {
    doc["status"] = estado;       // Cambio: estado -> status
  }
  
  // Timestamp en formato epoch Unix (segundos desde 1970)
  // Nota: Para timestamp ISO 8601 necesitarías RTC o NTP
  doc["timestamp"] = millis() / 1000;  // Convertir a segundos
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  if (client.publish(topic, buffer)) {
    Serial.print("📤 [");
    Serial.print(topic);
    Serial.print("] ");
    Serial.println(buffer);
  } else {
    Serial.print("❌ Error publicando en: ");
    Serial.println(topic);
  }
}

// ============================================
// PUBLICAR ESTADO DEL SISTEMA
// ============================================
void publishStatus(const char* estado) {
  StaticJsonDocument<256> doc;
  
  doc["device_id"] = device_id;
  doc["estado"] = estado;
  doc["ip"] = WiFi.localIP().toString();
  doc["rssi"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  doc["free_heap"] = ESP.getFreeHeap();
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  client.publish(TOPIC_STATUS, buffer);
}

// ============================================
// LEER POTENCIÓMETROS Y CONVERTIR A VALORES
// ============================================
void readSensors() {
  int adcValue;
  float mappedValue;

  // 1. Potenciómetro Temperatura (0-50°C)
  adcValue = analogRead(TEMP_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 5000) / 100.0; // 0.0 - 50.0°C
  publishSensor(TOPIC_TEMPERATURA, "temperatura", mappedValue, "°C");
  delay(50);

  // 2. Potenciómetro Humedad (0-100%)
  adcValue = analogRead(HUM_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 10000) / 100.0; // 0.0 - 100.0%
  publishSensor(TOPIC_HUMEDAD, "humedad", mappedValue, "%");
  delay(50);

  // 3. Potenciómetro Humo (0-100%)
  adcValue = analogRead(HUMO_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 10000) / 100.0; // 0.0 - 100.0%
  const char* humoStatus = (mappedValue > 50) ? "alerta" : "normal";
  publishSensor(TOPIC_HUMO, "humo", mappedValue, "%", humoStatus);
  delay(50);

  // 4. Potenciómetro Luz (0-100%)
  adcValue = analogRead(LUZ_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 10000) / 100.0; // 0.0 - 100.0%
  publishSensor(TOPIC_LUZ, "luz", mappedValue, "%");
  delay(50);

  // 5. Potenciómetro Movimiento (digital simulado: <50% = 0, >=50% = 1)
  adcValue = analogRead(MOV_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 100);
  bool movDetectado = (mappedValue >= 50);
  const char* movStatus = movDetectado ? "detectado" : "sin_movimiento";
  publishSensor(TOPIC_MOVIMIENTO, "movimiento", movDetectado ? 1.0 : 0.0, "", movStatus);
  delay(50);

  // 6. Potenciómetro Puerta (digital simulado: <50% = cerrada, >=50% = abierta)
  adcValue = analogRead(PUERTA_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 100);
  bool puertaAbierta = (mappedValue >= 50);
  const char* puertaStatus = puertaAbierta ? "abierta" : "cerrada";
  publishSensor(TOPIC_PUERTA, "puerta", puertaAbierta ? 1.0 : 0.0, "", puertaStatus);
  delay(50);

  // 7. Potenciómetro Alarma (>80% = activada)
  adcValue = analogRead(ALARMA_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 100);
  if (mappedValue > 80) {
    publishSensor(TOPIC_ALARMA, "alarma_manual", 1.0, "", "activada");
  }
  delay(50);

  // 8. Potenciómetro Viento (0-100 km/h) - OPCIONAL
  adcValue = analogRead(VIENTO_POT_PIN);
  mappedValue = map(adcValue, 0, ADC_RESOLUTION, 0, 10000) / 100.0; // 0.0 - 100.0 km/h
  publishSensor(TOPIC_VIENTO, "viento", mappedValue, "km/h");
  delay(50);
}

// ============================================
// LOOP PRINCIPAL
// ============================================
void loop() {
  // Mantener conexión MQTT
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();

  // Publicar lecturas de sensores periódicamente
  if (now - lastMsg > interval) {
    lastMsg = now;
    readSensors();
  }

  // Publicar estado del sistema periódicamente
  if (now - lastStatusMsg > statusInterval) {
    lastStatusMsg = now;
    publishStatus("online");
  }
}

// ============================================
// NOTAS DE IMPLEMENTACIÓN - POTENCIÓMETROS
// ============================================
/*
 * CONEXIONES FÍSICAS DE POTENCIÓMETROS (10kΩ recomendado):
 * 
 * Cada potenciómetro se conecta así:
 *   - Terminal 1 -> 3.3V
 *   - Terminal 2 (wiper/central) -> GPIO ADC correspondiente
 *   - Terminal 3 -> GND
 * 
 * DISTRIBUCIÓN DE POTENCIÓMETROS:
 * 
 * POT 1 (GPIO 1) - Temperatura:
 *   Rango: 0-50°C
 *   Girar para simular cambios de temperatura
 * 
 * POT 2 (GPIO 2) - Humedad:
 *   Rango: 0-100%
 *   Girar para simular cambios de humedad
 * 
 * POT 3 (GPIO 3) - Humo:
 *   Rango: 0-100%
 *   >50% = Estado "alerta"
 * 
 * POT 4 (GPIO 4) - Luz:
 *   Rango: 0-100%
 *   Girar para simular día/noche
 * 
 * POT 5 (GPIO 5) - Movimiento:
 *   <50% = Sin movimiento (0)
 *   >=50% = Movimiento detectado (1)
 * 
 * POT 6 (GPIO 6) - Puerta:
 *   <50% = Cerrada (0)
 *   >=50% = Abierta (1)
 * 
 * POT 7 (GPIO 7) - Alarma:
 *   <80% = Desactivada
 *   >80% = ALARMA ACTIVADA
 * 
 * POT 8 (GPIO 8) - Viento:
 *   Rango: 0-100 km/h
 *   Girar para simular velocidad del viento
 * 
 * LIBRERÍAS NECESARIAS (Arduino IDE):
 *   - PubSubClient by Nick O'Leary
 *   - ArduinoJson by Benoit Blanchon
 *   - WiFi (incluida con ESP32)
 * 
 * CONFIGURACIÓN ANTES DE CARGAR:
 *   1. Seleccionar placa: "ESP32S3 Dev Module"
 *   2. Modificar ssid y password (líneas 40-41)
 *   3. Modificar mqtt_server con IP del servidor Kali (línea 47)
 *   4. Conectar 8 potenciómetros a los pines GPIO 1-8
 *   5. Cargar el código
 * 
 * VENTAJAS DE USAR POTENCIÓMETROS:
 *   ✅ No necesitas sensores reales (más económico)
 *   ✅ Control manual de valores para pruebas
 *   ✅ Simula cualquier rango de valores
 *   ✅ Ideal para demostraciones y desarrollo
 */
