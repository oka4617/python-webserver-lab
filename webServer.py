# import socket module
from socket import *
# In order to terminate the program (kept from skeleton, not required for submission)
import sys
import os

SERVER_NAME = "NYU-Python-WebServer"


def safe_path(path: str) -> str:
    """
    Convert a URL path like /helloworld.html into a safe local path.
    Blocks directory traversal and strips query params.
    """
    # Strip query params if any
    path = path.split("?", 1)[0]

    # Default root request
    if path == "/":
        path = "/index.html"

    # Normalize and remove leading /
    local = os.path.normpath(path.lstrip("/"))

    # Block traversal / absolute paths
    if local.startswith("..") or os.path.isabs(local):
        return ""

    return local


def webServer(port=13331):
    serverSocket = socket(AF_INET, SOCK_STREAM)

    # Prepare a server socket
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(("", port))

    # Fill in start
    serverSocket.listen(1)
    # Fill in end

    while True:
        # Establish the connection
        # (Comment out prints before submitting to GradeScope if you want to be extra safe)
        # print('Ready to serve...')

        connectionSocket, addr = serverSocket.accept()

        try:
            message = connectionSocket.recv(1024).decode(errors="ignore")
            if not message:
                connectionSocket.close()
                continue

            # Parse request line: e.g. "GET /helloworld.html HTTP/1.1"
            request_line = message.splitlines()[0]
            parts = request_line.split()

            # Minimal validation
            if len(parts) < 2:
                connectionSocket.close()
                continue

            method = parts[0].upper()
            url_path = parts[1]

            # Only support GET for this assignment
            if method != "GET":
                body = b"<html><body><h1>404 Not Found</h1></body></html>"
                header = (
                    "HTTP/1.1 404 Not Found\r\n"
                    f"Server: {SERVER_NAME}\r\n"
                    "Content-Type: text/html; charset=UTF-8\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8")
                connectionSocket.sendall(header + body)
                connectionSocket.close()
                continue

            local_path = safe_path(url_path)
            if not local_path:
                raise FileNotFoundError

            # Open requested file as bytes
            with open(local_path, "rb") as f:
                file_bytes = f.read()

            # Basic content type (assignment mainly serves HTML)
            content_type = "text/html; charset=UTF-8" if local_path.endswith(".html") else "text/plain; charset=UTF-8"

            # Build full HTTP response (headers + blank line + body)
            header = (
                "HTTP/1.1 200 OK\r\n"
                f"Server: {SERVER_NAME}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(file_bytes)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode("utf-8")

            # Send everything in ONE send call
            connectionSocket.sendall(header + file_bytes)

            connectionSocket.close()

        except Exception:
            # Send response message for invalid request due to file not being found (404)
            body = b"<html><body><h1>404 Not Found</h1></body></html>"
            header = (
                "HTTP/1.1 404 Not Found\r\n"
                f"Server: {SERVER_NAME}\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode("utf-8")

            # Send everything in ONE send call
            connectionSocket.sendall(header + body)

            # Close client socket
            connectionSocket.close()

    # DO NOT UNCOMMENT / MOVE THESE (per skeleton note)
    # serverSocket.close()
    # sys.exit()


if __name__ == "__main__":
    webServer(13331)
