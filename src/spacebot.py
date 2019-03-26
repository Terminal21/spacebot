from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import threading
import time


class SpaceApiHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        self.respond("""asdf""")

    def do_GET(self):
        self.respond("""geh weg""")

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)


def run():
    server = HTTPServer(('', 8889), SpaceApiHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    while True:
        time.sleep(20)
