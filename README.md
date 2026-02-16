# Raspberry Pi Pico 2 W RFID Access Control System

This project implements an **RFID-based access control system** using a **Raspberry Pi Pico 2 W**, an **MFRC522 RFID reader**, and a **16x2 I2C LCD display**. The system grants access to authorized cards, triggers LEDs and a buzzer, and displays status messages on the LCD.

---

## Features

- Detects and reads **MIFARE Classic RFID cards**.
- **Access granted** for authorized cards (green LED + welcome message).  
- **Access denied** for unauthorized cards (red LED + buzzer + denied message).  
- Add or remove card access dynamically using `allow_card_access(uid)` or `remove_card_access(uid)`.  
- Displays all status messages on a **16x2 I2C LCD**.  
- Runs entirely on a **Raspberry Pi Pico 2 W**.

---

## Hardware Requirements

| Component | Notes |
|-----------|-------|
| Raspberry Pi Pico 2 W | Microcontroller |
| MFRC522 RFID Reader | SPI interface |
| MIFARE Classic RFID Cards | ISO 14443A compatible |
| I2C LCD Display | 16x2 recommended |
| LEDs | Green (access granted), Red (access denied) |
| Buzzer | Optional, triggers on access denied |
| Jumper Wires | For connections |
| Breadboard | Optional |

---

## Wiring

**MFRC522 → Raspberry Pi Pico 2 W (SPI interface)**  

| MFRC522 Pin | Pico Pin |
|-------------|----------|
| SDA (CS)    | GPIO 5  |
| SCK         | GPIO 6  |
| MOSI        | GPIO 7  |
| MISO        | GPIO 4  |
| RST         | GPIO 22 |
| 3.3V        | 3.3V     |
| GND         | GND      |

**I2C LCD → Raspberry Pi Pico 2 W**  

| LCD Pin | Pico Pin |
|---------|----------|
| SDA     | GPIO 0  |
| SCL     | GPIO 1  |
| VCC     | 3.3V    |
| GND     | GND     |

**LEDs, Buttons and Buzzer**  

| Component  | Pico Pin |
|------------|----------|
| Red Button (Remove access)     | GPIO 13 |
| Green Button (Add Access)      | GPIO 12 |
| Blue Button (Check access)     | GPIO 11 |
| Green LED                      | GPIO 14 |
| Red LED                        | GPIO 15 |
| Buzzer                         | GPIO 16 |

---

## Software Requirements

- MicroPython firmware on the Raspberry Pi Pico 2 W
- Libraries:
  - `mfrc522.py` (included)
  - `pico_i2c_display.py` (included)
- Python 3 for editing scripts

---

## How It Works

1. The Pico initializes the **MFRC522 reader** and **LCD display**.
2. Click a button by the desired access
3. When a card is placed near the reader:
   - The **UID** is read from the card.
   - Checks by the button what to do
   - `authKeys()` authenticates the card’s sector using the **configured key**.
   - `readSectorBlock()` reads the block to check for the **authorized value (`0xA5`)**.
   - `writeSectorBlock()` writes the block to apply for the **authorized value (`0xA5`)** or **unauthorized value**.
4. Depending on the data:
   - **Authorized** → Green LED + LCD “Welcome!” message
   - **Unauthorized** → Red LED + buzzer + LCD “Access denied!” message
   - **Add Access** → Green LED + LCD “Access added!” message
   - **Remove Access** → Red LED + buzzer + LCD “Access removed!” message
5. Outputs are reset after a short delay to allow multiple scans.

> Random cards or credit cards will **not pass authentication** because they do not have MIFARE Classic memory sectors.

---

## Authorizing Cards

To give a card access:

```python
status = allow_card_access(uid)
```

To remove access:
```python
status = remove_card_access(uid)
```

- `uid` is the UID of the card read by the MFRC522.  
- `allow_card_access()` writes the value `0xA5` to the first byte of the authorized block, enabling access.  
- `remove_card_access()` clears the block, revoking access.  

---

## Code Structure

- **main.py** → Main program, handles scanning, authorization, and outputs  
- **mfrc522.py** → MFRC522 driver for SPI communication  
- **pico_i2c_display.py** → LCD driver for I2C display  

---

## Tips

- Use a **unique key** for your authorized cards for security.  
- For multi-card setups, maintain a **list of UIDs** and check against it.  
- Add a **short delay** to prevent multiple rapid triggers when a card is held near the reader.  

---

## License

This project is licensed under the **MIT License** – you can freely use, modify, and share the code with credit to the author.
