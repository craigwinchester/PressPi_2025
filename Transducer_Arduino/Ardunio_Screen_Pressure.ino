//  Ardunio_Screen_Pressure.ino
//  Hardware used:
//      Arduino Uno
//      Pressure Transducer - 
//      OLED screen -       

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Pressure sensor config
const int sensorPin = A0;
const float voltageMin = 0.5;   // Voltage at 0 PSI
const float voltageMax = 4.5;   // Voltage at 30 PSI
const float psiMin = 0.0;
const float psiMax = 30.0;

float sensorValue = 0;
float voltage = 0;
float psi = 0;
float bar = 0;

void setup() {
  Serial.begin(9600);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("OLED failed to initialize"));
    while (true);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.display();
}

void loop() {
  sensorValue = analogRead(sensorPin);
  voltage = sensorValue * (5.0 / 1023.0);

  if (voltage <= voltageMin) {
    psi = psiMin;
  } else if (voltage >= voltageMax) {
    psi = psiMax;
  } else {
    psi = psiMin + (psiMax - psiMin) * ((voltage - voltageMin) / (voltageMax - voltageMin));
  }

  bar = psi * 0.0689476;

  //Serial.print("BAR: ");
  Serial.println(bar, 2);

  // OLED Display
  display.clearDisplay();

  // === Bargraph at top (yellow zone) ===
  int barHeight = 16;  // Fill yellow zone height
  int barWidth = map(psi, 0, psiMax, 0, SCREEN_WIDTH);
  int barY = 0;

  display.drawRect(0, barY, SCREEN_WIDTH, barHeight, SSD1306_WHITE);
  display.fillRect(1, barY + 1, barWidth - 2, barHeight - 2, SSD1306_WHITE);

  // === BAR text in blue zone ===
  display.setTextSize(2);  // Medium font
  display.setCursor(0, 24);  // Start below the bar (row 16+)
  display.print(bar, 2);
  display.print(" BAR");

  // === Bubble animation (bottom 24px) ===

  const int maxBubbles = 12;
  int numBubbles = map(psi, 0, psiMax, 1, maxBubbles);  // Pressure controls bubble count

  static int bubbleY[maxBubbles];
  static int bubbleX[maxBubbles];

  // Initialize bubble positions if first run
  static bool bubblesInit = false;
  if (!bubblesInit) {
    for (int i = 0; i < maxBubbles; i++) {
      bubbleX[i] = random(0, SCREEN_WIDTH);
      bubbleY[i] = SCREEN_HEIGHT - random(8);  // Random start height
    }
    bubblesInit = true;
  }

  for (int i = 0; i < numBubbles; i++) {
    // Move bubble upward
    bubbleY[i] -= 1;

    // If it goes above the bubble zone, reset it
    if (bubbleY[i] < 40) {
      bubbleY[i] = SCREEN_HEIGHT - 1;
      bubbleX[i] = random(0, SCREEN_WIDTH);
    }

    // Draw the bubble
    display.drawCircle(bubbleX[i], bubbleY[i], 2, SSD1306_WHITE);  // radius 2
  }


  display.display();
  delay(250);
}
