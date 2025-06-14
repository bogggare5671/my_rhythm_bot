#!/bin/bash

echo "📦 Установленные библиотеки:"
arduino-cli lib list

echo "🛠 Компиляция..."
arduino-cli compile --fqbn arduino:avr:uno /root/my_rhythm_bot
if [ $? -ne 0 ]; then
  echo "❌ Ошибка компиляции"
  exit 1
fi

echo "🚀 Загрузка в Arduino..."
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno /root/my_rhythm_bot
if [ $? -ne 0 ]; then
  echo "❌ Ошибка загрузки. Проверь подключение!"
  exit 1
fi

echo "✅ Готово!"
