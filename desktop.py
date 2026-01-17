import webview
import threading
import sys
from app import app

def start_flask():
    # use_reloader=False prevents Flask from spawning a second process
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    t = threading.Thread(target=start_flask)
    t.daemon = True  # <--- CRITICAL: Kills server when app closes
    t.start()
    
    webview.create_window("Bhaagya Rekha", "http://127.0.0.1:5000")
    webview.start()
    
    # Optional: Force exit Python completely when window closes
    sys.exit()