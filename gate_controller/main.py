import network
import time
import socket
import sys
from machine import Pin
from config import *

PIN_RELAY = 10
PULSE_MS = 400
COOLDOWN = 5


relay = Pin(PIN_RELAY, Pin.OUT)
relay.off()

def log(msg):
    print("[esp-gate]", msg)
def connect_wifi(ssid, password, timeout_s=20):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if not wlan.isconnected():
        log(f"Connecting to Wi-Fi: {ssid} ...")
        wlan.connect(ssid, password)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
                log("Wi‑Fi timeout")
                break
            time.sleep(0.25)
    if wlan.isconnected():
        log(f"Connected: {wlan.ifconfig()}")
    else:
        log("Wi‑Fi error")
    return wlan
def pulse_gate(ms=PULSE_MS):
    log(f"Relay signal {ms} ms")
    relay.on()
    time.sleep_ms(ms)
    relay.off()
def http_response(conn, status="200 OK", body="", content_type="text/plain; charset=utf-8"):
    headers = [
        f"HTTP/1.1 {status}",
        f"Content-Type: {content_type}",
        "Connection: close",
        f"Content-Length: {len(body)}",
        "",
        ""
    ]
    try:
        conn.send("\r\n".join(headers))
        if body:
            conn.send(body)
    except Exception as e:
        log(f"Request error: {e}")


def serve(port=80):
    cooldown_start = time.time()

    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    log(f"HTTP server is listening on port :{port}")

    while True:
        try:
            conn, client = s.accept()
            conn.settimeout(5)
            req = conn.recv(1024)
            if not req:
                conn.close()
                continue

            first = req.split(b"\r\n", 1)[0].decode("utf-8", "ignore")
            parts = first.split()
            method = parts[0] if len(parts) > 0 else ""
            path = parts[1] if len(parts) > 1 else "/"

            # Health check endpoint
            if method == "GET" and path == "/":
                http_response(conn, "200 OK", ".")

            # Gate control endpoint
            elif method in ("GET", "POST") and path == "/open":
                elapsed_time = time.time() - cooldown_start

                if elapsed_time < COOLDOWN:
                    remaining = COOLDOWN - elapsed_time
                    http_response(conn, "429 Too Many Requests", f"Cooldown active. Wait {remaining:.1f}s")
                else:
                    cooldown_start = time.time()
                    pulse_gate()
                    http_response(conn, "200 OK", "OK")

            # Unknown endpoint
            else:
                http_response(conn, "404 Not Found", "Not Found")

        except Exception as e:
            log(f"Request error: {e}")
        finally:
            try:
                conn.close()
            except:
                pass


def main():
    wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    try:
        serve(80)
    except KeyboardInterrupt:
        log("Stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()