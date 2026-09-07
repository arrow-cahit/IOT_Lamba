import http.server
import socketserver
import json
import os
import socket
from datetime import datetime
from urllib.parse import urlparse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def read_data():
    if not os.path.exists(DATA_FILE):
        initial = {
            "lamba": False,
            "relayA": False,
            "relayB": False,
            "durum": "KAPALI",
            "son_guncelleme": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        write_data(initial)
        return initial
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "lamba": False,
            "relayA": False,
            "relayB": False,
            "durum": "KAPALI",
            "son_guncelleme": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def write_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class IoTRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/api/status", "/api/data", "/data.json"):
            data = read_data()
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Statik dosya sunumu (index.html vb.)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            req_data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            req_data = {}

        current_data = read_data()

        if parsed.path == "/api/toggle":
            target = req_data.get("target", "lamba")
            if target == "lamba":
                new_state = not current_data.get("lamba", False)
                current_data["lamba"] = new_state
                current_data["relayA"] = new_state
                current_data["durum"] = "ACIK" if new_state else "KAPALI"
            elif target == "relayA":
                new_state = not current_data.get("relayA", False)
                current_data["relayA"] = new_state
                current_data["lamba"] = new_state
                current_data["durum"] = "ACIK" if new_state else "KAPALI"
            elif target == "relayB":
                new_state = not current_data.get("relayB", False)
                current_data["relayB"] = new_state
            else:
                current_data[target] = not current_data.get(target, False)

            current_data["son_guncelleme"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_data(current_data)

            payload = json.dumps(current_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        elif parsed.path == "/api/set":
            target = req_data.get("target", "lamba")
            value = bool(req_data.get("value", False))
            current_data[target] = value
            if target in ("lamba", "relayA"):
                current_data["lamba"] = value
                current_data["relayA"] = value
                current_data["durum"] = "ACIK" if value else "KAPALI"

            current_data["son_guncelleme"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_data(current_data)

            payload = json.dumps(current_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    local_ip = get_local_ip()
    print("=" * 60)
    print("  [+] IOT Lamba Kontrol Sunucusu Baslatildi")
    print(f"  [+] Web Arayuzu:        http://localhost:{PORT}")
    print(f"  [+] ESP8266 Veri URL'i: http://{local_ip}:{PORT}/data.json")
    print(f"  [+] Durum Dosyasi:      {DATA_FILE}")
    print("=" * 60)

    class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadingServer(("", PORT), IoTRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu durduruldu.")
