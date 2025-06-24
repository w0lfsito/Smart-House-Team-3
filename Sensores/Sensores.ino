#include <DHT.h>

// ---------- CONFIGURACIÓN SENSORES ----------
// Sensor DHT
#define DHTPIN 2
#define DHTTYPE DHT22  // o DHT22 si usas ese
DHT dht(DHTPIN, DHTTYPE);

// Sensor ultrasónico
#define TRIG_PIN 3
#define ECHO_PIN 5

// Sensor de luz (LDR)
#define LDR_PIN A0

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  // Leer temperatura y humedad
  float temperatura = dht.readTemperature();
  float humedad = dht.readHumidity();

  // Leer distancia (ultrasónico)
  long duracion, distancia;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duracion = pulseIn(ECHO_PIN, HIGH);
  distancia = duracion * 0.034 / 2; // Convertir a cm

  // Leer luz (LDR)
  int luzRaw = analogRead(LDR_PIN);
  float luz = map(luzRaw, 0, 1023, 0, 300); // Escalar a lux aproximado

  // Validar datos (pueden ser NaN con DHT)
  if (isnan(temperatura) || isnan(humedad)) {
    temperatura = 0;
    humedad = 0;
  }

  // Enviar datos al serial separados por comas
  Serial.print(temperatura);
  Serial.print(",");
  Serial.print(humedad);
  Serial.print(",");
  Serial.print(distancia);
  Serial.print(",");
  Serial.println(luz);

  delay(1000); // Esperar 1 segundo antes de repetir
}