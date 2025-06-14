import serial
import time
from .config import SERIAL_PORT, BAUDRATE

class SerialIO:
    def __init__(self, port=SERIAL_PORT, baud=BAUDRATE, timeout=1.0):
        self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)
        # Даем Arduino время на готовность
        time.sleep(2)

    def send(self, cmd: str):
        """Отправляет ASCII-команду (без \n), добавляя '\n' и перевод строки."""
        payload = (cmd.strip() + "\n").encode('ascii')
        self.ser.write(payload)

    def send_block(self):
        self.send("BLOCK_INPUT")

    def send_allow(self):
        self.send("ALLOW_INPUT")

    def send_show(self, btn: int):
        self.send(f"SHOW {btn}")

    def send_led_off(self, btn: int):
        self.send(f"LED OFF {btn}")

    def send_prize(self):
        self.send("PRIZE")

    def send_lcd(self, raw_payload: bytes):
        """
        Отправляет команду LCD с произвольными байтами (уже закодированными rus_to_lcd),
        например: ser.send_lcd(b'LCD '+payload)
        """
        self.ser.write(b"LCD " + raw_payload + b"\n")

    def read_line(self, timeout: float = None) -> str:
        """
        Считывает одну строку (без '\n') из UART.
        Если задан timeout, будет ожидать не дольше.
        """
        if timeout is not None:
            self.ser.timeout = timeout
        line = self.ser.readline().decode(errors='ignore').strip()
        return line

    def close(self):
        self.ser.close()


# Глобальный синглтон для удобного импорта
_serial = SerialIO()

def send(cmd: str):
    _serial.send(cmd)

def block_input():
    _serial.send_block()

def allow_input():
    _serial.send_allow()

def show(btn: int):
    _serial.send_show(btn)

def led_off(btn: int):
    _serial.send_led_off(btn)

def prize():
    _serial.send_prize()

def send_lcd(payload: bytes):
    _serial.send_lcd(payload)

def read_line(timeout: float = None) -> str:
    return _serial.read_line(timeout)
