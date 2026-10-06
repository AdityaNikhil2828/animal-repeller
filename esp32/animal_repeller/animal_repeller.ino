#define BUZZER_PIN 25

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.begin(115200);

  Serial.println("ESP32 Animal Repeller");
  Serial.println("Waiting for command...");
}

void loop() {

  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.print("Received: ");
    Serial.println(command);

    if (command == "TIGER") {

      Serial.println("TIGER DETECTED!");
      Serial.println("BUZZER ON");

      // Buzzer for 5 seconds
      unsigned long startTime = millis();

      while (millis() - startTime < 5000) {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(300);

        digitalWrite(BUZZER_PIN, LOW);
        delay(200);
      }

      digitalWrite(BUZZER_PIN, LOW);

      Serial.println("BUZZER OFF");
    }

    else if (command == "STOP") {
      digitalWrite(BUZZER_PIN, LOW);
      Serial.println("STOP");
    }
  }
}