import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET_API_KEY = "shellapp_secure_key_123"
PHONE_TUNNEL_URL = "https://9a1db21039e615.lhr.life"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get("Authorization")
        if auth_header != f"Bearer {SECRET_API_KEY}":
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        try:
            req = urllib.request.Request(f"{PHONE_TUNNEL_URL}{self.path}")
            with urllib.request.urlopen(req) as response:
                phone_response = response.read()
                
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(phone_response)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(f'{{"error": "Phone offline or unreachable", "details": "{str(e)}"}}'.encode('utf-8'))

port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), ProxyHandler)
print(f"Proxy Gateway running on port {port}")
server.serve_forever()
