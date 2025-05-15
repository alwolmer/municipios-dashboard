import threading
import http.server
import socketserver
import os

PORT = 4472
TILE_DIR = 'tiles_recife'

def start_tile_server():
    handler = http.server.SimpleHTTPRequestHandler
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
    os.chdir(os.path.join(script_dir, TILE_DIR))  # Serve from tile folder relative to script directory
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving tiles at http://localhost:{PORT}")
        httpd.serve_forever()


start_tile_server()

# # Start server in a background thread
# thread = threading.Thread(target=start_tile_server)
# thread.start()