import socket

def client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 3343))

        print(client_socket.recv(1024).decode(), end="")
        opcion = input().strip()
        client_socket.sendall(opcion.encode() + b'\n')

        print(client_socket.recv(1024).decode(), end="")
        username = input().strip()
        client_socket.sendall(username.encode() + b'\n')

        print(client_socket.recv(1024).decode(), end="")
        password = input().strip()

        # Enviar la contraseña sin hashear, el servidor lo manejará
        client_socket.sendall(password.encode() + b'\n')  

        response = client_socket.recv(1024).decode()
        print(response)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()



if __name__ == "__main__":
    client()
