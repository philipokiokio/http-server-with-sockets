# Uncomment this to pass the first stage
import socket
from threading import Thread
import os
import sys


def response_body_builder(res_body: str, content_type: str = "text/plain"):
    return (
        "HTTP/1.1 200 OK\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(res_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{res_body}"
    )


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

        url_path = data.split(" ")[1]

        if url_path == "/":
            connection.send(b"HTTP/1.1 200 OK\r\n\r\n")
        elif "/echo/" in url_path:
            res_body = url_path.split("/")[-1]

            resp_data = response_body_builder(res_body=res_body)

        elif "/files/" in url_path:
            file_path = os.path.join(sys.argv[2], url_path.split("/")[-1])

            if os.path.exists(file_path):
                with open(file=file_path) as f:
                    body = f.read()

                    resp_data = response_body_builder(
                        res_body=body, content_type="application/octet-stream"
                    )
            else:
                resp_data = "HTTP/1.1 404 Not Found\r\n\r\n"

            ...

        elif url_path == "/user-agent":

            user_agent = data.split(" ")[-1]

            resp_data = response_body_builder(res_body=user_agent.strip())

        else:
            resp_data = "HTTP/1.1 404 Not Found\r\n\r\n"

        connection.sendall(resp_data.encode())
    connection.close()


if __name__ == "__main__":
    main()
