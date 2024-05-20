import http.server
import socketserver
import socket
import urllib.parse
import argparse
import requests
import select

from config.env import getenv


class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        # Extract the target host and port from the path
        target_host, target_port = self.path.split(":")
        target_port = int(target_port)

        # Connect to the target host
        try:
            with socket.create_connection((target_host, target_port)) as tunnel_socket:
                self.send_response(200, "Connection established")
                self.end_headers()

                # Tunnel data between the client and the target
                self._tunnel(self.connection, tunnel_socket)
        except Exception as e:
            self.send_error(502, f"Bad gateway: {e}")

    def _tunnel(self, client_socket, server_socket):
        sockets = [client_socket, server_socket]
        while True:
            readable, writable, exceptional = select.select(sockets, [], sockets, 60)
            if exceptional:
                break
            for s in readable:
                data = s.recv(4096)
                if s is client_socket:
                    other = server_socket
                else:
                    other = client_socket
                if data:
                    other.sendall(data)
                else:
                    return

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        parsed_url = urllib.parse.urlsplit(self.path)
        url = parsed_url.geturl()

        if not parsed_url.scheme:
            self.send_error(400, "Bad request: URL must be absolute")
            return

        try:
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                response = requests.post(url, data=post_data, headers=self.headers, stream=True)
            else:
                response = requests.get(url, headers=self.headers, stream=True)

            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
        except requests.RequestException as e:
            self.send_error(502, f"Bad gateway: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Wikipedia scrapper for phrase search and page information')
    parser.add_argument("--proxy_url", "-u", type=str, default='http://localhost:9919', help='Proxy URL to connect with Wikipedia website')
    args = parser.parse_args()

    PROXY_URL = args.proxy_url
    PORT = int(PROXY_URL.split(':')[-1])

    with socketserver.ThreadingTCPServer(("localhost", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()