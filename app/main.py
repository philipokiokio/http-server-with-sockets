# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    print(f"connected address: {address}")
    print(connection)
    try:
        while True:
            data = connection.recv(1024).decode()
            if data is None:
                break
            url_path = data.split(" ")[1]

            if "/echo" in url_path:
                res_body = url_path.split("/")[-1]

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {len(res_body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    f"{res_body}"
                )
                connection.sendall(response.encode())
            elif url_path == "/":
                connection.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            else:
                connection.send(b"HTTP/1.1 200 OK\r\n\r\n")  # wait for client
    except (KeyboardInterrupt, Exception) as e:

        connection.close()


if __name__ == "__main__":
    main()
