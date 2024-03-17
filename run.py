from web import app
from web.sentry import watchman

from waitress import serve
import sys
import time
import threading

try:
    if sys.argv[1] != "80":
        port = int(sys.argv[1])
    else:
        port = 80
except IndexError:
    port = 80

def web():
    serve(app, host="0.0.0.0", port=port)

if __name__ == '__main__':
    threading.Thread(target=web, daemon=True).start()
    threading.Thread(target=watchman, daemon=True).start()
    while True:
        time.sleep(1)
    