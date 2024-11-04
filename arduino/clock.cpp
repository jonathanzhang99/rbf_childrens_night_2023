#include <SPI.h>
#include <DMD2.h>
#include <fonts/SystemFont5x7.h>

// Pin configurations for P10 display
#define PIN_DMD_nOE 10  // Output Enable (active low)
#define PIN_DMD_A 6     // Address A
#define PIN_DMD_B 7     // Address B
#define PIN_DMD_CLK 13  // Clock (SCK)
#define PIN_DMD_SCLK 8  // Scan Clock
#define PIN_DMD_DATA 11 // Data (MOSI)

// Define display parameters
#define DISPLAY_WIDTH 1  // Number of panels wide
#define DISPLAY_HEIGHT 1 // Number of panels high

const uint8_t *FONT = System5x7;
String displayString;
double targetTime = -1;
double timeToTarget;
// Initialize DMD object
SoftDMD dmd(DISPLAY_WIDTH, DISPLAY_HEIGHT, PIN_DMD_nOE, PIN_DMD_A, PIN_DMD_B, PIN_DMD_SCLK, PIN_DMD_CLK, PIN_DMD_DATA);

void emitTimeSync()
{
    Serial.print(F("EMIT TIME_SYNC "));
    Serial.print(millis());
    Serial.println();
}

void setup()
{
    Serial.begin(9600);
    Serial.println("hello");
    dmd.setBrightness(255);
    dmd.selectFont(FONT);
    dmd.begin();
    displayString = String("00.00");
    emitTimeSync();
}

void loop()
{
    while (Serial.available() > 0)
    {
        targetTime = Serial.readString().toDouble();
        Serial.println(targetTime);
    }
    // put your main code here, to run repeatedly:
    timeToTarget = targetTime - millis();
    if (timeToTarget <= 0)
    {
        displayString = String("00.00");
    }
    else
    {
        displayString = String(timeToTarget / 1000, 2);
    }
    dmd.drawString(1, 4, displayString);
}
