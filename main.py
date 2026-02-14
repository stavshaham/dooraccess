from mfrc522 import MFRC522
import utime
from machine import Pin
from pico_i2c_display import I2cLcd

# PIN CONFIGURATION
# MFRC522 RFID reader pins
reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)

# Output pins
green_light = Pin(14, Pin.OUT)
red_light = Pin(15, Pin.OUT)
buzzer = Pin(16, Pin.OUT)

# Authorization settings
AUTHORIZED_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
AUTHORIZED_SECTOR = 1
AUTHORIZED_BLOCK = 0
AUTHORIZED_VALUE = 0xA5

# FUNCTIONS
# This function resets the output
def reset_outputs():
    """
    Resets all outputs (LEDs, buzzer, LCD) to default state.
    Called after access granted or denied.
    """
    green_light.low()
    red_light.low()
    buzzer.low()
    lcd.clear()
    lcd.putstr("Waiting for card")

# This function activates the electronics when the card is the correct one
def access_granted():
    """
    Activates green LED and welcome message on the LCD.
    Waits 5 seconds for the user, then resets outputs.
    """
    global red_light, green_light, lcd
    red_light.value(0)
    green_light.value(1)
    lcd.clear()
    lcd.putstr("Welcome!")
    utime.sleep(5) # Wait 5 second, giving the user time to open the door
    reset_outputs()

# This function activates the electronics when the card is the wrong one
def access_denied():
    """
    Activates the red LED, turns on buzzer, and displays an access denied message.
    Waits 3 seconds, then resets outputs.
    """
    red_light.value(1)
    green_light.value(0)
    buzzer.high()
    lcd.clear()
    lcd.putstr("Access denied!")
    utime.sleep(3) # Wait 3 second
    reset_outputs()
    
# This function writes the card data and gives the card an access
def allow_card_access(uid):
    """
    Writes the authorized value to the card sector to grant access.
    This function sets the first byte of the block to AUTHORIZED_VALUE and the rest to 0x00.
    
    Args:
        uid (list): UID of the card
    
    Returns:
        int: Status from writeSectorBlock (MFRC522.OK or MFRC522.ERR)
    """
    data_to_write = [AUTHORIZED_VALUE] + [0x00]*15
    return reader.writeSectorBlock(uid, AUTHORIZED_SECTOR, AUTHORIZED_BLOCK, data_to_write, keyA=AUTHORIZED_KEY)

# This function wriets the card data and removes the card access
def remove_card_access(uid):
    """
    Clears the authorized value from the card sector to remove access.
    
    Args:
        uid (list): UID of the card
    
    Returns:
        int: Status from writeSectorBlock (MFRC522.OK or MFRC522.ERR)
    """
    data_to_write = [0x00]*16
    return reader.writeSectorBlock(uid, AUTHORIZED_SECTOR, AUTHORIZED_BLOCK, data_to_write, keyA=AUTHORIZED_KEY)

# DISPLAY SETUP
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
devices = i2c.scan()
if len(devices) == 0:
    print("No I2C device found")
else:
    print("I2C Address:", hex(devices[0]))
    lcd = I2cLcd(i2c, devices[0], 2, 16)
    lcd.clear()
    lcd.putstr("Waiting for card")

print("Bring TAG closer...")


while True:
    # Initializing the reader
    # Used to re-initialize to make sure the reader is not stuck
    reader.init()
    
    # Checkes if a card is present
    stat, _ = reader.request(reader.REQIDL)
    
    if stat == reader.OK:
        # Gets the UID of the card
        stat, uid = reader.SelectTagSN()
        if stat == reader.OK:
            # Authenticate using the authorized key (Key A)
            status = reader.authKeys(uid, AUTHORIZED_SECTOR * 4, keyA=AUTHORIZED_KEY)
            if status == reader.OK:
                # For the first use, use this function to write the data:
                # allow_card_access(uid)
                # To remove access, use this function:
                # remove_card_access(uid)
                
                # Read the sector block to check authorization
                status, data = reader.readSectorBlock(uid, AUTHORIZED_SECTOR, AUTHORIZED_BLOCK, keyA=AUTHORIZED_KEY)
                
                # Grant or deny access based on the first byte value
                if status == reader.OK and data[0] == AUTHORIZED_VALUE:
                    access_granted()
                else:
                    access_denied()
    
    # Small delay to avoid multiple rapid reads
    utime.sleep_ms(300)
    
