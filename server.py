cat << 'EOF' > server.py
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
import secrets
import os

request_records = {}
active_tokens = set()
blacklisted_ips = {}

MAX_REQUESTS = 10
TIME_WINDOW = 10
BAN_DURATION = 30
MAX_OFFENSES = 3

class PublicCloudAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def get_client_ip(self):
        forwarded_for = self.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return self.client_address[0]

    def is_blacklisted(self, client_ip):
        now = datetime.now()
        if client_ip in blacklisted_ips:
            if now < blacklisted_ips[client_ip]:
                return True
            else:
                del blacklisted_ips[client_ip]
        return False

    def register_offense(self, client_ip):
        now = datetime.now()
        if client_ip not in request_records:
            request_records[client_ip] = {"requests": [], "offenses": 0}
        request_records[client_ip]["offenses"] += 1
        if request_records[client_ip]["offenses"] >= MAX_OFFENSES:
            blacklisted_ips[client_ip] = now + timedelta(seconds=BAN_DURATION)

    def check_rate_limit(self, client_ip):
        now = datetime.now()
        if client_ip not in request_records:
            request_records[client_ip] = {"requests": [], "offenses": 0}
        request_records[client_ip]["requests"] = [
            t for t in request_records[client_ip]["requests"] 
            if now - t < timedelta(seconds=TIME_WINDOW)
        ]
        if len(request_records[client_ip]["requests"]) >= MAX_REQUESTS:
            return False
        request_records[client_ip]["requests"].append(now)
        return True

    def handle_security(self):
        client_ip = self.get_client_ip()
        if self.is_blacklisted(client_ip):
            return False
        if not self.check_rate_limit(client_ip):
            self.register_offense(client_ip)
            self.send_json_response(429, {"status": "error", "msg": "Too many requests."})
            return False
        return True

    def do_POST(self):
        if not self.handle_security():
            return
        client_ip = self.get_client_ip()
        if self.path == "/api/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                if data.get("username") == "shellapp" and data.get("password") == "tech123":
                    token = secrets.token_hex(16)
                    active_tokens.add(token)
                    self.send_json_response(200, {"status": "success", "token": token})
                else:
                    self.register_offense(client_ip)
                    self.send_json_response(401, {"status": "error", "msg": "Invalid credentials"})
            except Exception:
                self.send_json_response(400, {"status": "error", "msg": "Bad request"})
        else:
            self.send_json_response(404, {"status": "error", "msg": "Not found"})

    def do_GET(self):
        if not self.handle_security():
            return
        client_ip = self.get_client_ip()
        path = self.path
        auth_header = self.headers.get('Authorization')

        if path == "/":
            self.send_json_response(200, {"message": "Public Cloud API Server is Live!"})
        elif path == "/api/status":
            self.send_json_response(200, {"status": "online", "firewall": "active"})
        elif path == "/api/admin/panel":
            token_valid = False
            if auth_header and auth_header.startswith("Bearer "):
                if auth_header.split(" ")[1] in active_tokens:
                    token_valid = True

            if token_valid:
                self.send_json_response(200, {"secret_data": "Welcome to the public cloud admin dashboard!"})
            else:
                self.register_offense(client_ip)
                self.send_json_response(403, {"status": "error", "msg": "Unauthorized"})
        else:
            self.send_json_response(404, {"status": "error", "msg": "Not found"})

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=4).encode('utf-8'))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, PublicCloudAPIHandler)
    print(f"[*] Public Cloud Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
