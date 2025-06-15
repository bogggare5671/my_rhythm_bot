# game/serial_io.py

import serial
import time
from serial.serialutil import SerialException

from .config import SERIAL_PORT, BAUDRATE

class SerialIO:
    def __init__(self, port: str, baudrate: int, timeout: float = 1.0):
        # Установим таймаут 1 сек, чтобы собрать всю строку целиком
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def write(self, msg: bytes):
        """Записать байты в порт, сбросить буфер и дать устройству время обработать."""
        self.ser.write(msg)
        self.ser.flush()
        time.sleep(0.01)

    def read_line(self, timeout: float = None) -> str:
        """
        Считывает одну строку до LF (\n), ожидая не более timeout секунд.
        Если timeout не указан, используется timeout порта (1 сек).
        """
        # Если передан отдельный таймаут, временно поменяем его
        if timeout is not None:
            prev = self.ser.timeout
            self.ser.timeout = timeout

        try:
            raw = self.ser.readline()            # читаем до '\n' или таймаута
            return raw.decode(errors='ignore').strip()
        except SerialException:
            return ""
        finally:
            if timeout is not None:
                self.ser.timeout = prev

    def block_input(self):
        self.write(b"BLOCK_INPUT\n")

    def allow_input(self):
        self.write(b"ALLOW_INPUT\n")

    def show(self, btn: int):
        self.write(f"SHOW {btn}\n".encode())

    def led_off(self, btn: int):
        self.write(f"LED OFF {btn}\n".encode())

    def prize(self):
        self.write(b"PRIZE\n")

    def send_lcd(self, data: bytes):
        self.write(data)


# глобальный экземпляр с таймаутом 1 сек
_serial = SerialIO(SERIAL_PORT, BAUDRATE, timeout=1.0)

def block_input():      return _serial.block_input()
def allow_input():      return _serial.allow_input()
def show(btn: int):     return _serial.show(btn)
def led_off(btn: int):  return _serial.led_off(btn)
def prize():            return _serial.prize()
def read_line(timeout=None) -> str:
    return _serial.read_line(timeout)
def send_lcd(data: bytes):
    return _serial.send_lcd(data)
