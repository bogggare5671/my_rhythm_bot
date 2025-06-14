#include <Wire.h>
#include <LiquidCrystal_I2C_Cyrillic.h>
#include <Servo.h>

// ── Пины ───────────────────────────────────────────
const uint8_t BTN_PINS[3] = {2, 3, 4};    // кнопки D2–D4
const uint8_t LED_PINS[3] = {5, 6, 7};    // светодиоды D5–D7
const uint8_t RESET_PIN   = 8;           // кнопка START/RESET
const uint8_t SERVO_PIN   = 9;           // сервопривод (приз)

// ── Объекты ────────────────────────────────────────
LiquidCrystal_I2C_Cyrillic lcd(0x27, 16, 2);
Servo                 prizeServo;
bool                  inputAllowed = false;
char                  screenBuf[64];    // буфер для команд по UART

// ── Инициализация ──────────────────────────────────
void setup() {
  Serial.begin(9600);

  // LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.printCyrillic("P" "\x098" "\x09F" "\x09C" "-" "\x080" "o" "\x09F", 4, 0);
  lcd.printCyrillic("\x081" "OTOB", 5, 1);  // ASCII-сообщение, потом попадёт из Python
/* Коды символов
Б \x080
Г \x081
Ё \x082
Ж \x083
З \x084
И \x085
Й \x086
Л \x087
П \x088
У \x089
Ф \x08A 
Ч \x08B
Ш \x08C
Ъ \x08D
Ы \x08E
Э \x08F
Ю \x090
Я \x091
б \x092
в \x093
г \x094
ё \x095
ж \x096
з \x097
и \x098
й \x099
к \x09A
л \x09B
м \x09C
н \x09D
п \x09E
т \x09F
ч \x0A0
ш \0xA1
ъ \x0A2
ы \x0A3
ь \x0A4
э \x0A5
ю \x0A6
я \x0A7
Д \x0A8
Ц \x0A9
Щ \x0AA
д \x0AB
ф \x0AC
ц \x0AD
щ \x0AE
*/
  // кнопки и светодиоды
  for (uint8_t i = 0; i < 3; ++i) {
    pinMode(BTN_PINS[i], INPUT_PULLUP);
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
  pinMode(RESET_PIN, INPUT_PULLUP);

  // сервопривод
  prizeServo.attach(SERVO_PIN);
  prizeServo.write(0);
}

// ── Главный цикл ───────────────────────────────────
void loop() {
  // 1) СТАРТ/СБРОС
  if (digitalRead(RESET_PIN) == LOW) {
    Serial.println("RESET");
    while (digitalRead(RESET_PIN) == LOW);
    delay(100);
    return;  // сразу возвращаемся, чтобы Python успел обработать RESET
  }

  // 2) Приём команд от Orange Pi
  if (Serial.available()) {
    int len = Serial.readBytesUntil('\n', screenBuf, sizeof(screenBuf) - 1);
    screenBuf[len] = '\0';

    // LCD <текст CP1251>
    if (len > 4 && strncmp(screenBuf, "LCD ", 4) == 0) {
      lcd.clear();
      lcd.printCyrillic(screenBuf + 4, 0, 0);
    }
    // SHOW <№>
    else if (strncmp(screenBuf, "SHOW ", 5) == 0) {
      int b = atoi(screenBuf + 5);
      if (b >= 0 && b < 3) {
        digitalWrite(LED_PINS[b], HIGH);
        inputAllowed = false;
      }
    }
    // LED OFF <№>
    else if (strncmp(screenBuf, "LED OFF ", 8) == 0) {
      int b = atoi(screenBuf + 8);
      if (b >= 0 && b < 3) {
        digitalWrite(LED_PINS[b], LOW);
      }
    }
    // разрешить и запретить ввод кнопок
    else if (strcmp(screenBuf, "ALLOW_INPUT") == 0) {
      inputAllowed = true;
    }
    else if (strcmp(screenBuf, "BLOCK_INPUT") == 0) {
      inputAllowed = false;
    }
    // PRIZE — выдача приза
    else if (strcmp(screenBuf, "PRIZE") == 0) {
      prizeServo.write(180);
      delay(1000);
      prizeServo.write(0);
    }
  }

  // 3) Опрос кнопок игрока (только когда inputAllowed == true)
  if (inputAllowed) {
    for (uint8_t i = 0; i < 3; ++i) {
      if (digitalRead(BTN_PINS[i]) == LOW) {
        // отправляем номер кнопки в Python
        Serial.print("BTN ");
        Serial.println(i);

        // мигнул светодиод
        digitalWrite(LED_PINS[i], HIGH);
        delay(150);
        digitalWrite(LED_PINS[i], LOW);

        // ждём отпускания
        while (digitalRead(BTN_PINS[i]) == LOW);
        delay(40);
      }
    }
  }
}
