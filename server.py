import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# مفتاح الحماية السري (يمكنك تغييره بأي كلمة سر قوية)
SECRET_API_KEY = "shellapp_secure_key_123"

class SecureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # استخراج الهيدرز والتحقق من المفتاح السري
        auth_header = self.headers.get("Authorization")
        
        # طريقة أخرى للتحقق عبر الـ Query Parameters (مثل ?key=...)
        # يمكنك أيضاً استخدام الهيدرز مباشرة
        if auth_header != f"Bearer {SECRET_API_KEY}":
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized: Invalid or missing API Key"}')
            return

        # إذا كان المفتاح صحيحاً، اعرض البيانات المحمية
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "success", "message": "Welcome to Shellapp Secured Cloud API!"}')

port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), SecureHandler)
print(f"Secure Server running on port {port}")
server.serve_forever()
