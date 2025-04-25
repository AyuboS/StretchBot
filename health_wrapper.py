# health_wrapper.py
import threading, http.server, socketserver, main  # ← imports your bot code

class OK(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

# start a 0-logic HTTP server for Koyeb’s health-check
threading.Thread(
    target=lambda: socketserver.TCPServer(("", 8080), OK).serve_forever(),
    daemon=True
).start()

if __name__ == "__main__":
    main()
