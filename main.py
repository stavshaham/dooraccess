from mfrc522 import MFRC522
import utime
from machine import Pin
from pico_i2c_display import I2cLcd

# Pins - Make sure configured correctly on the board
reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)
green_light = Pin(14, Pin.OUT)
red_light = Pin(15, Pin.OUT)
buzzer = Pin(16, Pin.OUT)

print("Bring TAG closer...")

# Display
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
devices = i2c.scan()
if len(devices) == 0:
    print("No I2C device found")
else:
    print("I2C Address:", hex(devices[0]))
    lcd = I2cLcd(i2c, devices[0], 2, 16)
    lcd.clear()
    lcd.putstr("Waiting for card")



while True:
    reader.init()
    # Checkes if a card is present
    (stat, tag_type) = reader.request(reader.REQIDL)
    lcd.clear()
    lcd.putstr("Waiting for card")
    if stat == reader.OK:
        # Getting the UID of the card
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            # Converts the card array from bytes (UID) to a number
            card = int.from_bytes(bytes(uid),"little",False)
            print("Card ID: ", card)
            if card == 45912990:
                red_light.value(0)
                green_light.value(1)
                lcd.clear()
                lcd.putstr("Welcome!")
                utime.sleep(5) # Wait 5 second, giving the user time to open the door
            else:
                red_light.value(1)
                green_light.value(0)
                buzzer.high()
                lcd.clear()
                lcd.putstr("Access denied!")
                utime.sleep(3) # Wait 3 second
        else:
            buzzer.low()
            green_light.value(0)
            red_light.value(0)
                
    else:
        buzzer.low()
        green_light.value(0)
        red_light.value(0)
