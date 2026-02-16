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

# Input pins
red_button = Pin(13, Pin.IN, Pin.PULL_UP)
remove_access = False

green_button = Pin(12, Pin.IN, Pin.PULL_UP)
add_access = False

blue_button = Pin(11, Pin.IN, Pin.PULL_UP)
check_access = False

button_pressed = False

# Authorization settings
AUTHORIZED_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
AUTHORIZED_SECTOR = 1
AUTHORIZED_BLOCK = 0
AUTHORIZED_VALUE = 0xA5

# FUNCTIONS
# This function checks if a button has been pressed
def check_buttons():
    """
    This function checks if a button has been pressed
    If a button has been pressed, then the corresponding boolean will be true
    """
    global button_pressed, remove_access, add_access, check_access
    button_pressed = True
    if red_button.value() == 0:
        remove_access = True
        add_access = False
        check_access = False
        lcd.clear()
        lcd.putstr("Waiting for card")
    elif green_button.value() == 0:
        remove_access = False
        add_access = True
        check_access = False
        lcd.clear()
        lcd.putstr("Waiting for card")
    elif blue_button.value() == 0:
        remove_access = False
        add_access = False
        check_access = True
        lcd.clear()
        lcd.putstr("Waiting for card")
        
# This function resets the output
def reset_outputs():
    """
    Resets all outputs (LEDs, buzzer, LCD) to default state.
    Called after access granted or denied.
    """
    global remove_access, add_access, check_access, button_pressed
    green_light.low()
    red_light.low()
    buzzer.low()
    lcd.clear()
    remove_access = False
    add_access = False
    check_access = False
    button_pressed = False
    lcd.putstr("Waiting for")
    lcd.move_to(0, 1)
    lcd.putstr("button")

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
    reader.writeSectorBlock(uid, AUTHORIZED_SECTOR, AUTHORIZED_BLOCK, data_to_write, keyA=AUTHORIZED_KEY)
    lcd.clear()
    lcd.putstr("Access added")
    green_light.value(1)
    utime.sleep(3)
    reset_outputs()

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
    reader.writeSectorBlock(uid, AUTHORIZED_SECTOR, AUTHORIZED_BLOCK, data_to_write, keyA=AUTHORIZED_KEY)
    lcd.clear()
    lcd.putstr("Access removed")
    buzzer.high()
    red_light.value(1)
    utime.sleep(3)
    reset_outputs()

# DISPLAY SETUP
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
devices = i2c.scan()
if len(devices) == 0:
    print("No I2C device found")
else:
    print("I2C Address:", hex(devices[0]))
    lcd = I2cLcd(i2c, devices[0], 2, 16)
    lcd.clear()
    lcd.putstr("Waiting for")
    lcd.move_to(0, 1)
    lcd.putstr("button")


while True:
    # Initializing the reader
    # Used to re-initialize to make sure the reader is not stuck
    check_buttons()
    
    if remove_access or add_access or check_access:
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
                                        
                    if remove_access:
                        remove_card_access(uid)
                        print("Access removed: ", uid)
                    elif add_access:
                        allow_card_access(uid)
                        print("Access added: ", uid)
                    elif check_access:
                        # Read the sector block to check authorization
                        status, data = reader.readSectorBlock(uid, AUTHORIZED_SECTOR, AUTHORIZED_BLOCK, keyA=AUTHORIZED_KEY)
                        
                        # Grant or deny access based on the first byte value
                        if status == reader.OK and data[0] == AUTHORIZED_VALUE:
                            access_granted()
                        else:
                            access_denied()
        # Small delay to avoid multiple rapid reads
        utime.sleep_ms(300)
    
