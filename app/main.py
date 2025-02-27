# Uncomment this to pass the first stage
import gzip
import socket
from threading import Thread
import os
import sys


def response_body_builder(
    res_body: str, content_type: str = "text/plain", is_encoded: bool = False
):
    if is_encoded is False:

        return (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(res_body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{res_body}"
            "\r\n"
        ).encode()

    res_body = compress_body(data=res_body)

    return (
        "HTTP/1.1 200 OK\r\n"
        "Content-Encoding: gzip\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(res_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() + res_body


def content_compression(data: str):

    headers, _ = data.split("\r\n\r\n", 1)

    allowed_compression = False
    for header in headers.splitlines():
        if header.lower().startswith("accept-encoding:"):
            compression = str(header.split(":")[1].strip())
            compression_list = compression.split(", ")
            if "gzip" in compression_list:
                allowed_compression = True

                break

    return allowed_compression


def body_builder(connection: socket.socket, data: str):
    headers, body = data.split("\r\n\r\n", 1)
    request_line = headers.splitlines()[0]
    print(f"Received request: {request_line}")

    # Process headers to find Content-Length
    content_length = 0
    for header in headers.splitlines():
        if header.lower().startswith("content-length:"):
            content_length = int(header.split(":")[1].strip())

    # Read the request body if Content-Length is specified
    if content_length > 0:
        while len(body) < content_length:
            body += connection.recv(1024).decode()
    return body


def compress_body(data: str):

    return gzip.compress(data=data.encode())


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    try:
        while True:
            connection, address = server_socket.accept()
            print(f"connected address: {address}")
            print(connection)
            Thread(target=socket_last_mile, args=(connection,)).start()
        # socket_last_mile(connection=connection)  # wait for client
    except (KeyboardInterrupt, Exception) as e:

        server_socket.close()


def socket_last_mile(connection: socket.socket):
    while True:
        data = connection.recv(1024).decode()
        if data is None:
            break
        resp_data = "HTTP/1.1 400 Bad Request\r\n\r\n"
        if len(data.split(" ")) < 2:

            break

        method, url_path = (
            data.split(" ")[0],
            data.split(" ")[1],
        )
        print(method, url_path)

        allowed_compression = content_compression(data=data)

        if url_path == "/":
            resp_data = b"HTTP/1.1 200 OK\r\n\r\n"
        elif "/echo/" in url_path:
            res_body = url_path.split("/")[-1]

            resp_data = response_body_builder(
                res_body=res_body.strip(), is_encoded=allowed_compression
            )

        elif "/files/" in url_path:
            file_path = os.path.join(sys.argv[2], url_path.split("/")[-1])

            if method == "GET":

                if os.path.exists(file_path):
                    with open(file=file_path) as f:
                        body = f.read()

                        resp_data = response_body_builder(
                            res_body=body,
                            content_type="application/octet-stream",
                            is_encoded=allowed_compression,
                        )
                else:
                    resp_data = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
            elif method == "POST":
                file = open(file=file_path, mode="w+")
                file.write(body_builder(connection=connection, data=data))
                file.close()

                resp_data = "HTTP/1.1 201 Created\r\n\r\n".encode()

            ...

        elif url_path == "/user-agent":

            user_agent = data.split(" ")[-1]

            resp_data = response_body_builder(
                res_body=user_agent.strip(), is_encoded=allowed_compression
            )

        else:
            resp_data = "HTTP/1.1 404 Not Found\r\n\r\n".encode()

        connection.sendall(resp_data)
    connection.close()


if __name__ == "__main__":
    main()
