// Ardunio_Screen_Pressure_ADS.ino
// Hardware used:
//      Arduino Uno
//      Pressure Transducer (0.5V–4.5V, 0–30 PSI)
//      OLED screen (SSD1306)
//      ADS1115 ADC module

// Craig Winchester - 6/8/2025


#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_ADS1X15.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pressure sensor calibration
const float voltageMin = 0.5;   // Voltage at 0 PSI
const float voltageMax = 4.5;   // Voltage at 30 PSI
const float psiMin = 0.0;
const float psiMax = 30.0;

// Global sensor variables
float voltage = 0;
float psi = 0;
float bar = 0;

// ADS1115 setup
Adafruit_ADS1115 ads;

void setup() {
  Serial.begin(9600);

  // Init OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("OLED failed to initialize"));
    while (true);
  }

  // Init ADS1115
  if (!ads.begin()) {
    Serial.println(F("ADS1115 failed to initialize"));
    while (true);
  }
  ads.setGain(GAIN_TWOTHIRDS);  // ±6.144V input range (0.1875 mV/bit)

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.display();
}

void loop() {
  // Read voltage from ADS1115 channel 0
  int16_t rawADC = ads.readADC_SingleEnded(0);
  voltage = rawADC * 0.1875 / 1000.0;  // Convert mV to volts

  // Convert voltage to PSI
  if (voltage <= voltageMin) {
    psi = psiMin;
  } else if (voltage >= voltageMax) {
    psi = psiMax;
  } else {
    psi = psiMin + (psiMax - psiMin) * ((voltage - voltageMin) / (voltageMax - voltageMin));
  }

  // Convert PSI to bar
  bar = psi * 0.0689476;

  // Output to serial
  Serial.println(bar, 2);

  // OLED Display
  display.clearDisplay();

  // === Bargraph at top (yellow zone) ===
  int barHeight = 16;
  int barWidth = map(psi, 0, psiMax, 0, SCREEN_WIDTH);
  int barY = 0;

  display.drawRect(0, barY, SCREEN_WIDTH, barHeight, SSD1306_WHITE);
  display.fillRect(1, barY + 1, barWidth - 2, barHeight - 2, SSD1306_WHITE);

  // === BAR text in blue zone ===
  display.setTextSize(2);
  display.setCursor(0, 24);
  display.print(bar, 2);
  display.print(" BAR");

  // === Bubble animation (bottom 24px) ===
  const int maxBubbles = 12;
  int numBubbles = map(psi, 0, psiMax, 1, maxBubbles);

  static int bubbleY[maxBubbles];
  static int bubbleX[maxBubbles];
  static bool bubblesInit = false;

  if (!bubblesInit) {
    for (int i = 0; i < maxBubbles; i++) {
      bubbleX[i] = random(0, SCREEN_WIDTH);
      bubbleY[i] = SCREEN_HEIGHT - random(8);
    }
    bubblesInit = true;
  }

  for (int i = 0; i < numBubbles; i++) {
    bubbleY[i] -= 1;
    if (bubbleY[i] < 40) {
      bubbleY[i] = SCREEN_HEIGHT - 1;
      bubbleX[i] = random(0, SCREEN_WIDTH);
    }
    display.drawCircle(bubbleX[i], bubbleY[i], 2, SSD1306_WHITE);
  }

  display.display();
  delay(250);
}
