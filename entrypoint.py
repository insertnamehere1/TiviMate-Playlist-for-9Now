import subprocess
import threading
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import sys

# Path to playlist file
PLAYLIST_PATH = "/kodi.proxy/addons/slyguy.9now/playlist.m3u8"
PLUGIN_DIR = "/kodi.proxy/addon_data/slyguy.9now"

def plugin_installed():
    """Check if required plugin is installed."""
    return os.path.isdir(PLUGIN_DIR)

def trigger_playlist():
    """Run proxy.py to generate playlist asynchronously, retrying on failure."""
    while True:
        if not plugin_installed():
            print("WARNING: Required plugin 'slyguy.9now' not found. Waiting for installation...")
            time.sleep(30)  # check every 30s until plugin is installed
            continue

        try:
            print("Triggering playlist generation via proxy.py...")
            process = subprocess.Popen(
                ["python3", "proxy.py", "plugin://slyguy.9now/?_=playlist&output=playlist.m3u8"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL   # prevent interactive prompt
            )
            # Wait up to 30 seconds for process to finish
            timeout = 30
            start = time.time()
            while process.poll() is None:
                if time.time() - start > timeout:
                    print("proxy.py timed out, killing process and retrying...")
                    process.kill()
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Error generating playlist: {e}, retrying in 5s...")
            time.sleep(5)
            continue

        # Poll until playlist file exists and has content
        for _ in range(60):
            if os.path.exists(PLAYLIST_PATH) and os.path.getsize(PLAYLIST_PATH) > 0:
                print("Playlist file created successfully.")
                break
            time.sleep(1)

        # Wait 6 hours before next refresh
        time.sleep(6 * 60 * 60)

class PlaylistHandler(SimpleHTTPRequestHandler):
    """Serve the playlist.m3u8 file on /playlist.m3u8."""
    def do_GET(self):
        if self.path == "/playlist.m3u8":
            if os.path.exists(PLAYLIST_PATH) and os.path.getsize(PLAYLIST_PATH) > 0:
                self.send_response(200)
                self.send_header("Content-type", "application/vnd.apple.mpegurl")
                self.send_header("Content-Disposition", "attachment; filename=\"playlist.m3u8\"")
                self.end_headers()
                with open(PLAYLIST_PATH, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Playlist not found")
        else:
            self.send_response(404)
            self.end_headers()

def run_http():
    """Start the mini HTTP server on port 8181."""
    server = HTTPServer(("0.0.0.0", 8181), PlaylistHandler)
    print("Serving playlist on port 8181 at /playlist.m3u8")
    server.serve_forever()

if __name__ == "__main__":
    # Start playlist generation in background immediately
    threading.Thread(target=trigger_playlist, daemon=True).start()

    # Start HTTP server right away
    run_http()

