import functools
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


class FileServer(threading.Thread):
    def __init__(self, directory: str, port: int = 8000):
        super().__init__()
        self.directory = directory
        self.port = port
        self.httpd = None

    def run(self) -> None:
        handler = functools.partial(SimpleHTTPRequestHandler, directory=self.directory)
        self.httpd = HTTPServer(("0.0.0.0", self.port), handler)
        self.httpd.serve_forever()

    def stop(self) -> None:
        if self.httpd:
            self.httpd.shutdown()
