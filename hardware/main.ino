/*
 * Project: "Te Cuido" - Biomedical IoT Simulation
 * Board: Arduino UNO (simulation constraint)
 *
 * NOTE:
 * This code is written for Arduino UNO because the simulation platform requires it.
 * In real implementation, ESP32 or similar should be used due to:
 * - Better ADC resolution
 * - WiFi connectivity
 * - More processing power
 *
 * Displays (LCD) will NOT be used in real product as UI will represent real time values.
 */

#include <Adafruit_LiquidCrystal.h>
#include <Adafruit_GFX.h>
#include <Adafruit_LEDBackpack.h>
#include <math.h>

// ===================== CONSTANTS =====================

// Analog pins
const int PIN_TEMP   = A0;
const int PIN_PPG_F  = A1;
const int PIN_SPO2_F = A2;
const int PIN_FLEX   = A3;

// PWM pins
const int PIN_PPG_L  = 9;
const int PIN_SPO2_L = 10;

// LCDs (I2C addresses - adjust if needed)
Adafruit_LiquidCrystal lcd_1(0);
Adafruit_LiquidCrystal lcd_breath(1);


// 7-seg display
Adafruit_7segment disp_ispo2 = Adafruit_7segment();

// ===================== VARIABLES =====================
int phase = 0;

int pwmValue = 0;
int pwmDirection = 1;

// ===================== FUNCTIONS =====================

// Read temperature (TMP36-like)
float readTemperatureC() {
  int raw = analogRead(PIN_TEMP);
  float voltage = raw * (5.0 / 1023.0);
  float tempC = (voltage - 0.5) * 100.0;
  return tempC;
}

float toFahrenheit(float c) {
  return (c * 9.0 / 5.0) + 32.0;
}

// Simulate PPG signal
int readPPG() {
  int raw = analogRead(PIN_PPG_F);
  return map(raw, 0, 1023, 60, 100); // fake BPM range
}
void showBreathStatus() {

  static unsigned long lastUpdate = 0;
  static unsigned long lastPeakTime = 0;
  static bool rising = false;
  static float rpm = 0;

  int value = analogRead(PIN_FLEX);

  const int thresholdHigh = 30;
  const int thresholdLow  = 0;

    unsigned long now = millis();
    unsigned long interval = now - lastPeakTime;

    String state;

    if (value > 22) {
      state = "Stress";
    } else if (value >= 12 && value <= 20) {
      state = "Normal";
    } else if (value > 0 && value < 12) {
      state = "Relax";
    } else {
      state = "No data";
    }

    lcd_breath.setCursor(0,0);
    lcd_breath.print("RPM:      ");
    lcd_breath.setCursor(5,0);
    lcd_breath.print(value);

    lcd_breath.setCursor(0,1);
    lcd_breath.print("State:    ");
    lcd_breath.setCursor(7,1);
    lcd_breath.print(state);
  }

// LED PWM effect
void updatePWM() {
  int pwmValue = 0;
  analogWrite(PIN_PPG_L, pwmValue);
  analogWrite(PIN_SPO2_L, pwmValue);
  // ---- SPO2 ----
  disp_ispo2.print(pwmValue);
  disp_ispo2.writeDisplay();
  delay(200);
  pwmValue = 100;
  analogWrite(PIN_PPG_L, pwmValue);
  analogWrite(PIN_SPO2_L, pwmValue);
  // ---- SPO2 ----
  disp_ispo2.print(pwmValue);
  disp_ispo2.writeDisplay();
  delay(300);
  pwmValue = 200;
  analogWrite(PIN_PPG_L, pwmValue);
  analogWrite(PIN_SPO2_L, pwmValue);
  // ---- SPO2 ----
  disp_ispo2.print(pwmValue);
  disp_ispo2.writeDisplay();
  delay(200); 
  pwmValue = 255;
  analogWrite(PIN_PPG_L, pwmValue);
  analogWrite(PIN_SPO2_L, pwmValue);
  // ---- SPO2 ----
  disp_ispo2.print(pwmValue);
  disp_ispo2.writeDisplay();
  delay(500);
}

// ===================== SETUP =====================

void setup() {
  // Initialize pins
  pinMode(PIN_PPG_L, OUTPUT);
  pinMode(PIN_SPO2_L, OUTPUT);

  pinMode(PIN_TEMP, INPUT);
  pinMode(PIN_PPG_F, INPUT);
  pinMode(PIN_SPO2_F, INPUT);
  pinMode(PIN_FLEX, INPUT);
  
  // Initialize I2C
  Wire.begin();

  // LCDs
  lcd_1.begin(16, 2);
  lcd_breath.begin(16, 2);
  lcd_1.print("Welcome ");
  lcd_breath.print("to Te Cuido App");

  // 7-seg
  disp_ispo2.begin(0x70);

  // Clear displays
  lcd_1.clear();
  lcd_breath.clear();
  Serial.begin(9600);
}

// ===================== LOOP =====================

void loop() {
  lcd_1.setBacklight(1);
  lcd_breath.setBacklight(1);
  // Update LED signals
  updatePWM();

  // ---- TEMPERATURE ----
  lcd_1.setCursor(0,0);
  float tempC = readTemperatureC();
  float tempF = toFahrenheit(tempC);
  lcd_1.print("Temp ");
  lcd_1.print(tempC);
  lcd_1.print("C");
  
  // ---- PPG ----
  int bpm = readPPG();
  lcd_1.setCursor(0,1);
  lcd_1.print("PPG ");
  lcd_1.print(bpm);
  
  // ---- Breath ---
  showBreathStatus();
}

/*
===================== ESP32 VERSION (REFERENCE) =====================

IMPORTANT:
- LCDs are NOT used in ESP32 version (UI handled by app)
- Uses WiFi + MQTT to send data to "Te Cuido"

Example:

#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASS";
const char* mqtt_server = "broker_ip";

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    client.connect("ESP32_TeCuido");
  }
}

void setup() {
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  String payload = "{ \"temp\": 25, \"spo2\": 98 }";
  client.publish("tecuido/data", payload.c_str());

  delay(2000);
}

====================================================================
*/
