# ─ Dockerfile ───────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1

# ▸ Koyeb's free instance must expose one HTTP port (8080 by convention)
EXPOSE 8080

# ▸ Tiny inline health-server + start your bot
CMD python - <<'PY'
import threading, http.server, socketserver, bot_stretch

class OK(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b'OK')

threading.Thread(
    target=lambda: socketserver.TCPServer(('', 8080), OK).serve_forever(),
    daemon=True
).start()

bot_stretch.main()          # ← runs your existing while-True loop
PY
