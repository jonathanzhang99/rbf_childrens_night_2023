#include <SPI.h>
#include <DMD2.h>
#include <fonts/SystemFont5x7.h>

// Pin configurations for P10 display
#define PIN_DMD_nOE    10    // Output Enable (active low)
#define PIN_DMD_A      6    // Address A
#define PIN_DMD_B      7    // Address B
#define PIN_DMD_CLK   13    // Clock (SCK)
#define PIN_DMD_SCLK   8    // Scan Clock
#define PIN_DMD_DATA  11    // Data (MOSI)

// Define display parameters
#define DISPLAY_WIDTH  1     // Number of panels wide
#define DISPLAY_HEIGHT 1     // Number of panels high

const uint8_t *FONT = System5x7;
String incomingString;
// Initialize DMD object
SoftDMD dmd(DISPLAY_WIDTH, DISPLAY_HEIGHT, PIN_DMD_nOE, PIN_DMD_A, PIN_DMD_B, PIN_DMD_SCLK, PIN_DMD_CLK, PIN_DMD_DATA);

void setup() {
  Serial.println(F("SCORE BOARD ACTIVE"));
  dmd.setBrightness(255);
  dmd.selectFont(FONT);
  dmd.begin();
  incomingString = String("00000");
}

void loop() {
  Serial.begin(9600);
  while (Serial.available() > 0) {
    incomingString = Serial.readString();
    // Serial.println(incomingString);
    // Serial.println(incomingString.length());

  }
  // put your main code here, to run repeatedly:
  dmd.drawString(1, 4, incomingString);
}
