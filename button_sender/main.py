import network
import urequests
import time
from machine import Pin
import dht
from config import *

WAKE_PIN = 9
LED_PIN = 2
DHT_PIN = 10
last_press_time = 0
DEBOUNCE_MS = 300
button_pressed = False
led = Pin(LED_PIN, Pin.OUT)
dht_sensor = dht.DHT11(Pin(DHT_PIN))


def start_webrepl():
    try:
        import webrepl
        webrepl.start(password=WEBREPL_PASSWORD)
        print("WebREPL started")
    except Exception as e:
        print(f"WebREPL failed: {e}")


def test_ha_connection():
    try:
        url = f"{HA_URL}/api/"
        headers = {"Authorization": f"Bearer {HA_TOKEN}"}
        response = urequests.get(url, headers=headers)
        print(f"HA Connection test - Status: {response.status_code}")
        response.close()
        return response.status_code == 200
    except Exception as e:
        print(f"HA Connection test failed: {e}")
        return False


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(10):
            if wlan.isconnected():
                break
            time.sleep(1)
    if wlan.isconnected():
        print("Network connected:")
        print("IP:", wlan.ifconfig()[0])
        return True
    else:
        print("Network connection error")
        return False


def send_dht_data(temperature, humidity):
    url = f"{HA_URL}/api/states/sensor.gate_temp"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    data_temp = {
        "state": temperature,
        "attributes": {
            "unit_of_measurement": "C",
            "friendly_name": "ESP Temperature",
            "state_class": "measurement"
        },
    }
    data_hum = {
        "state": humidity,
        "attributes": {
            "unit_of_measurement": "%",
            "friendly_name": "ESP Humidity",
            "state_class": "measurement"
        },
    }
    try:
        response_temp = urequests.post(url, json=data_temp, headers=headers)
        response_temp.close()
        url_hum = f"{HA_URL}/api/states/sensor.gate_hum"
        response_hum = urequests.post(url_hum, json=data_hum, headers=headers)
        response_hum.close()
        print("dht11 send")
        return response_temp.status_code == 200 and response_hum.status_code == 200
    except Exception as e:
        print(f"Error sending DHT data: {e}")
        return False


def send_open_request():
    try:
        print(f"Sending request to {TARGET_URL}")
        response = urequests.get(TARGET_URL)
        print(f"Status: {response.status_code}")
        response.close()
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending open request: {e}")
        return False


def handle_button_interrupt(pin):
    global button_pressed, last_press_time
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_press_time) > DEBOUNCE_MS:
        button_pressed = True
        last_press_time = current_time


def setup_button_interrupt():
    try:
        button = Pin(WAKE_PIN, Pin.IN, Pin.PULL_UP)
        button.irq(trigger=Pin.IRQ_FALLING, handler=handle_button_interrupt)
    except Exception as e:
        print(f"Failed to set up button interrupt: {e}")


def read_dht11():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        print(f"Temperature: {temp}C, Humidity: {hum}%")
        return temp, hum
    except Exception as e:
        print(f"Failed to read DHT11 sensor: {e}")
        return None, None


def main():
    global button_pressed
    wifi_connected = connect_wifi()

    if wifi_connected:
        start_webrepl()
        if test_ha_connection():
            print("HA connection OK")
        else:
            print("HA connection failed")

    setup_button_interrupt()
    i = 0

    while True:
        time.sleep(0.1)
        i += 1

        if button_pressed:
            print("Button pressed, sending open request...")
            button_pressed = False
            if wifi_connected:
                success = send_open_request()
                if success:
                    led.on()
                    time.sleep(0.2)
                    led.off()
                print("Task completed:", "success" if success else "fail")
            else:
                print("No network connection, cannot send request")

        if i >= 100:
            i = 0
            temp, hum = read_dht11()
            if temp is not None and hum is not None and wifi_connected:
                send_dht_data(temp, hum)


if __name__ == "__main__":
    main()