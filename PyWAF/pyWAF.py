import http.server
import socketserver
import requests
import re
from urllib.parse import unquote

WAF_PORT = 9000
TARGET_URL = "http://127.0.0.1:5000"

RULES = {
    "sql_injection": r"(union\s+select|or\s+1=1|drop\s+table|insert\s+into|--)",
    "xss": r"(<script>|javascript:|alert\(|onerror=)",
    "path_traversal": r"(\.\./|\.\.\\|/etc/passwd|c:\\windows)"
}

class WAFHandler(http.server.SimpleHTTPRequestHandler):
    def inspect_request(self, method, path, body=""):
        decoded_path = unquote(path).lower()
        decoded_body = unquote(body).lower()
        print(f"inspecting {method}: {path}")
        for attack_type, pattern in RULES.items():
            if re.search(pattern, decoded_path) or re.search(pattern, decoded_body):
                print(f"Blocked {attack_type} attack: {decoded_path} {decoded_body}")
                return False
        return True
    
    def do_GET(self):
        if not self.inspect_request("GET", self.path):
            self.send_error(403, "Forbidden: Malicious request detected blocked by WAF")
            return
        try:
            resp = requests.get(f"{TARGET_URL}{self.path}", timeout=3)
            self.send_response(resp.status_code)
            self.send_header('Content-Length', len(resp.content))
            self.send_header('connection', 'close')
            for key, value in resp.headers.items():
                if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_error(500, f"server error: {e}")
            
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_length).decode('utf-8')
            if not self.inspect_request("POST", self.path, post_body):
                self.send_error(403, "Forbidden: Malicious request detected blocked by WAF")
                return
            resp = requests.post(f"{TARGET_URL}{self.path}", data=post_body)
            self.send_response(resp.status_code)
            self.send_header('Content-Length', len(resp.content))
            self.send_header('connection', 'close')
            for key, value in resp.headers.items():
                if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_error(500, f"server error: {e}")
            
if __name__ == '__main__':
    print(f"WAF shield active on port {WAF_PORT}")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", WAF_PORT), WAFHandler) as httpd:
        httpd.serve_forever()

# Test URLs:
#http://localhost:9000/search?q=union%20select
#http://localhost:9000/search?q=<script>alert(1)</script>
#http://localhost:9000/search?q=../../etc/passwd
#http://localhost:9000/search?q=halo