#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi credentials
const char* ssid = "vinstheking";
const char* password = "56789012";

// MQTT broker details
const char* mqtt_server = "192.168.154.42";
const int mqtt_port = 1883;

// Entry RFID module pins
#define RST_PIN_ENTRY 22
#define SS_PIN_ENTRY  5

// Exit RFID module pins
#define RST_PIN_EXIT 2
#define SS_PIN_EXIT  21

// IR sensor pins
#define IR_SENSOR_1 32
#define IR_SENSOR_2 4
#define IR_SENSOR_3 25
#define IR_SENSOR_4 15

MFRC522 rfidEntry(SS_PIN_ENTRY, RST_PIN_ENTRY);
MFRC522 rfidExit(SS_PIN_EXIT, RST_PIN_EXIT);

WiFiClient espClient;
PubSubClient client(espClient);

// Function to connect to WiFi
void setupWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" Connected!");
}

// Function to connect to MQTT broker
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32_Client")) {
      Serial.println(" Connected!");
      if (client.subscribe("parking/gates/status")) {
        Serial.println("Subscribed to parking/gates/status");
      } else {
        Serial.println("Subscription failed!");
      }
    } else {
      Serial.print(" Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

// Callback function for received MQTT messages
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message received [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // Process gate control messages
  if (String(topic) == "parking/gates/status") {
    if (message.startsWith("entry:open")) {
      Serial.println("Access authorized. Opening entry gate...");
    } else if (message.startsWith("entry:unauthorized")) {
      Serial.println("Access unauthorized. Entry gate remains closed.");
    } else if (message.startsWith("exit:open")) {
      Serial.println("Opening exit gate...");
    }
  }
}

// Function to publish IR sensor statuses
void updateSlotStatus() {
  for (int i = 1; i <= 4; i++) {
    int sensorState = 0;
    switch (i) {
      case 1: sensorState = digitalRead(IR_SENSOR_1); break;
      case 2: sensorState = digitalRead(IR_SENSOR_2); break;
      case 3: sensorState = digitalRead(IR_SENSOR_3); break;
      case 4: sensorState = digitalRead(IR_SENSOR_4); break;
    }
    String status = (sensorState == LOW) ? "occupied" : "free";
    String message = (i <= 2) ? String(i) + ":" + status : String(i + 2) + ":" + status;
    if (client.publish("parking/slots", message.c_str())) {
      Serial.println("Slot " + String(i) + " status sent to MQTT: " + message);
    } else {
      Serial.println("Failed to publish slot status for slot " + String(i));
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Initialize SPI bus and RFID modules
  SPI.begin();
  rfidEntry.PCD_Init();
  rfidExit.PCD_Init();

  // Initialize WiFi and MQTT
  setupWiFi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Initialize IR sensor pins
  pinMode(IR_SENSOR_1, INPUT);
  pinMode(IR_SENSOR_2, INPUT);
  pinMode(IR_SENSOR_3, INPUT);
  pinMode(IR_SENSOR_4, INPUT);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  // Check for Entry RFID
  if (rfidEntry.PICC_IsNewCardPresent() && rfidEntry.PICC_ReadCardSerial()) {
    String rfid = "";
    for (byte i = 0; i < rfidEntry.uid.size; i++) {
      rfid += String(rfidEntry.uid.uidByte[i], HEX);
    }
    rfid.toUpperCase();
    Serial.println("Entry RFID detected: " + rfid);
    String message = "entry:" + rfid;
    if (client.publish("parking/rfid", message.c_str())) {
      Serial.println("Entry RFID data sent to MQTT: " + message);
    } else {
      Serial.println("Failed to publish Entry RFID data.");
    }
    rfidEntry.PICC_HaltA();
    rfidEntry.PCD_StopCrypto1();
  }
  delay(500);
  // Check for Exit RFID
  if (rfidExit.PICC_IsNewCardPresent() && rfidExit.PICC_ReadCardSerial()) {
    String rfid = "";
    for (byte i = 0; i < rfidExit.uid.size; i++) {
      rfid += String(rfidExit.uid.uidByte[i], HEX);
    }
    rfid.toUpperCase();
    Serial.println("Exit RFID detected: " + rfid);
    String message = "exit:" + rfid;
    if (client.publish("parking/rfid", message.c_str())) {
      Serial.println("Exit RFID data sent to MQTT: " + message);
    } else {
      Serial.println("Failed to publish Exit RFID data.");
    }
    rfidExit.PICC_HaltA();
    rfidExit.PCD_StopCrypto1();
  }

  // Update IR sensor statuses every 9 seconds
  static unsigned long lastUpdateTime = 0;
  const unsigned long updateInterval = 9000;
  if (millis() - lastUpdateTime >= updateInterval) {
    lastUpdateTime = millis();
    updateSlotStatus();
  }
}
