# ESP32 Gate Controller System

A complete gate control system built with ESP32 microcontrollers using MicroPython. The system consists of two devices: a wireless button sender with temperature/humidity monitoring and a gate controller with relay control.

## 🎯 Features

### Gate Controller (Receiver)
- **HTTP API Server** - RESTful endpoint for gate control
- **Relay Control** - Pulse-based gate activation (400ms)
- **Cooldown Protection** - 5-second delay between activations
- **Health Check** - Simple endpoint for monitoring device status
- **WebREPL** - Remote debugging and maintenance

### Button Sender
- **Wireless Button** - Physical button with debouncing
- **DHT11 Sensor** - Temperature and humidity monitoring
- **Home Assistant Integration** - Automatic sensor data reporting
- **LED Feedback** - Visual confirmation of successful operations
- **Interrupt-based** - Low power consumption with pin interrupts

## 📋 Requirements

### Hardware
- 2x ESP32 development boards
- 1x Relay module (gate controller)
- 1x DHT11 temperature/humidity sensor (sender)
- 1x Push button (sender)
- 1x LED (sender)
- Jumper wires and breadboard

### Software
- MicroPython firmware for ESP32
- Home Assistant (optional, for sensor data)

## 🔌 Wiring

### Gate Controller
```
ESP32 Pin 10 → Relay IN
Relay VCC → 5V
Relay GND → GND
```

### Button Sender
```
ESP32 Pin 9  → Button (with pull-up)
ESP32 Pin 2  → LED (with resistor)
ESP32 Pin 10 → DHT11 Data
DHT11 VCC → 3.3V
DHT11 GND → GND
```

## ⚙️ Configuration

Create a `config.py` file on each ESP32:

### Gate Controller Config
```python
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"
WEBREPL_PASSWORD = "your_webrepl_password"
```

### Button Sender Config
```python
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"
WEBREPL_PASSWORD = "your_webrepl_password"
TARGET_URL = "http://GATE_CONTROLLER_IP/open"
HA_URL = "http://YOUR_HOME_ASSISTANT_IP:8123"
HA_TOKEN = "your_home_assistant_token"
```

## 🚀 Installation

1. **Flash MicroPython** on both ESP32 boards:
   ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-micropython.bin
   ```

2. **Upload files** using ampy, mpremote, or Thonny:
   ```bash
   # Gate Controller
   ampy --port /dev/ttyUSB0 put main.py
   ampy --port /dev/ttyUSB0 put config.py
   
   # Button Sender
   ampy --port /dev/ttyUSB1 put main.py
   ampy --port /dev/ttyUSB1 put config.py
   ```

3. **Reboot** both devices

## 📡 API Endpoints (Gate Controller)

### `GET /`
Health check endpoint
```bash
curl http://GATE_IP/
# Response: "."
```

### `GET /open` or `POST /open`
Trigger gate opening
```bash
curl http://GATE_IP/open
# Response: "OK" (200) or "Cooldown active. Wait Xs" (429)
```

## 🏠 Home Assistant Integration

The sender automatically reports sensor data to Home Assistant. Sensors will appear as:
- `sensor.gate_temp` - Temperature in °C
- `sensor.gate_hum` - Humidity in %

Update interval: 10 seconds

## 🔧 Customization

### Adjust Gate Pulse Duration
In gate controller `main.py`:
```python
PULSE_MS = 400  # Change to your gate's requirements (milliseconds)
```

### Adjust Cooldown Period
In gate controller `main.py`:
```python
COOLDOWN = 5  # Change cooldown time (seconds)
```

### Adjust Sensor Reading Interval
In sender `main.py`:
```python
if i >= 100:  # 100 * 0.1s = 10 seconds
```

## 🐛 Troubleshooting

### Gate controller not responding
- Check Wi-Fi connection: LED should indicate connection status
- Verify IP address: Check serial output for assigned IP
- Test with: `curl http://GATE_IP/`

### Button not working
- Check wiring and pull-up resistor
- Monitor serial output when pressing button
- Verify `WAKE_PIN` matches your wiring

### DHT11 sensor errors
- Ensure proper 3.3V power supply
- Check data pin connection
- Wait 2 seconds between readings

### WebREPL connection issues
- Verify password in `config.py`
- Connect to: `ws://DEVICE_IP:8266`
- Check firewall settings

## 📝 License

MIT License - feel free to modify and use for your projects

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Safety Notice

This system controls physical gate mechanisms. Ensure proper safety measures:
- Test thoroughly before connecting to actual gates
- Implement mechanical safety stops
- Consider adding timeout mechanisms
- Verify relay ratings match your gate motor
- Add manual override capabilities

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for home automation enthusiasts**
