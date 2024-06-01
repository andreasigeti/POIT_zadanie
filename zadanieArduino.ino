#include <Wire.h>
#include <Adafruit_BMP085.h>

// inicializace senzoru BMP180 z knihovny BMP085
Adafruit_BMP085 bmp180;

void setup() {
  // komunikace přes sériovou linku rychlostí 9600 baud
  Serial.begin(9600);
  // zapnutí komunikace se senzorem BMP180
  bmp180.begin();
}

void loop() {
  // výpis teploty ve stupních Celsia
  //Serial.print("Teplota: ");
  Serial.print(bmp180.readTemperature());
  Serial.print(",");

  // výpis barometrického tlaku v hekto Pascalech
  //Serial.print("Atmosferický tlak: ");
  Serial.println(bmp180.readPressure()/100);
  //Serial.println(" hPa");

  //Serial.println("------------------------------");

  delay(1000);
}
