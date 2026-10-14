import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET_API_KEY = "shellapp_secure_key_123"

# قائمة مؤثّتة لتخزين آخر الطلبات في الذاكرة (تتحدث عند إعادة تشغيل السيرفر)
request_logs = []

class TrackedSecureHandler(BaseHTTPRequestHandler):
    def log_request_info(self, status_code, endpoint):
        client_ip = self.client_address[0]
        user_agent = self.headers.get("User-Agent", "Unknown")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        log_entry = {
            "time": timestamp,
            "ip": client_ip,
            "endpoint": endpoint,
            "status": status_code,
            "user_agent": user_agent
        }
        
        # إضافة الطلب إلى القائمة (نحتفظ باخر 20 طلب فقط)
        request_logs.insert(0, log_entry)
        if len(request_logs) > 20:
            request_logs.pop()
            
        print(f"[LOG] {timestamp} - IP: {client_ip} - Path: {endpoint} - Status: {status_code}")

    def do_GET(self):
        parsed_path = self.path
        auth_header = self.headers.get("Authorization")

        # مسار خاص لعرض سجلات التتبع (يحتاج إلى المفتاح السري حصرياً)
        if parsed_path == "/logs":
            if auth_header != f"Bearer {SECRET_API_KEY}":
                self.log_request_info(401, "/logs")
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "Unauthorized"}')
                return
            
            self.log_request_info(200, "/logs")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"total_logs": len(request_logs), "logs": request_logs}, indent=2).encode('utf-8'))
            return

        # المسار الرئيسي المحمي
        if auth_header != f"Bearer {SECRET_API_KEY}":
            self.log_request_info(401, parsed_path)
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized: Invalid or missing API Key"}')
            return

        self.log_request_info(200, parsed_path)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "success", "message": "Welcome to Shellapp Tracked & Secured Cloud API!"}')

port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), TrackedSecureHandler)
print(f"Tracked & Secure Server running on port {port}")
server.serve_forever()
