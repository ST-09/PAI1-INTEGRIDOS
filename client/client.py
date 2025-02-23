import socket
import getpass


def client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 3343))

        while True:
            print(client_socket.recv(1024).decode(), end="")
            opcion = input().strip()
            client_socket.sendall(opcion.encode() + b'\n')

            if opcion == "2":
                print(client_socket.recv(1024).decode(), end="")
                username = input().strip()
                client_socket.sendall(username.encode() + b'\n')

                print(client_socket.recv(1024).decode(), end="")
                password = getpass.getpass("Ingrese su contraseña: ")
                client_socket.sendall(password.encode() + b'\n')

                response = client_socket.recv(1024).decode()
                print(response)

            elif opcion == "4":
                print(client_socket.recv(1024).decode(), end="")
                username = input().strip()
                client_socket.sendall(username.encode() + b'\n')

                response = client_socket.recv(1024).decode()
                print(response)

                if "Introduzca la transacción" in response:
                    transaccion = input("Cuenta origen, Cuenta destino, Cantidad transferida: ")
                    client_socket.sendall(transaccion.encode() + b'\n')
                    print(client_socket.recv(1024).decode())

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    client()
