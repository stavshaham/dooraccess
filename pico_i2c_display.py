from machine import I2C
import time

class I2cLcd:
    def __init__(self, i2c, addr, rows, cols):
        self.i2c = i2c
        self.addr = addr
        self.rows = rows
        self.cols = cols

        self.backlight = 0x08
        self.enable = 0x04

        self._init_lcd()

    def _write(self, data):
        self.i2c.writeto(self.addr, bytes([data | self.backlight]))

    def _pulse(self, data):
        self._write(data | self.enable)
        time.sleep_us(1)
        self._write(data & ~self.enable)
        time.sleep_us(50)

    def _send(self, value, mode):
        high = mode | (value & 0xF0)
        low = mode | ((value << 4) & 0xF0)
        self._pulse(high)
        self._pulse(low)

    def command(self, cmd):
        self._send(cmd, 0x00)

    def write_char(self, char):
        self._send(ord(char), 0x01)

    def putstr(self, string):
        for c in string:
            self.write_char(c)

    def clear(self):
        self.command(0x01)
        time.sleep_ms(2)
        
    def move_to(self, col, row):
        row_offsets = [0x00, 0x40]  # for 2-line LCDs, add 0x14, 0x54 for 4-line LCDs
        self.command(0x80 | (col + row_offsets[row]))
        
    def show(self, msg):
        self.clear()
        self.move_to(0, 0)
        self.putstr(msg)

    def _init_lcd(self):
        time.sleep_ms(50)
        self.command(0x33)
        self.command(0x32)
        self.command(0x28)
        self.command(0x0C)
        self.command(0x06)
        self.clear()
