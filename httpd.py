#!/usr/bin/env python

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import filter


class S(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/favicon.ico":
            import io
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(io.open("res/favicon.ico", "rb").read())

        if self.path == "/":
            import io
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(io.open("README", "rb").read())

        else:
            self.send_response(200)
            self.send_header('Content-type',  'text/plain')
            self.end_headers()
            output = None
            url = None
            include = None
            exclude = None

            if "url" in parse_qs(urlparse(self.path).query):
                url = parse_qs(urlparse(self.path).query)['url'][0]
                if "include" in parse_qs(urlparse(self.path).query):
                    include = parse_qs(urlparse(self.path).query)['include'][0]

                if "exclude" in parse_qs(urlparse(self.path).query):
                    exclude = parse_qs(urlparse(self.path).query)['exclude'][0]

            output = filter.output(url, include, exclude)

            self.wfile.write(str(output).encode("utf8"))


def run(server_class=HTTPServer, handler_class=S, addr="0.0.0.0", port=17304):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd server on " + addr + ":" + str(port))
    httpd.serve_forever()


if __name__ == "__main__":
    run()
