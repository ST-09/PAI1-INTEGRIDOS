import socket
import getpass  # Para ocultar la contraseña al escribir


def client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 3343))

        while True:
            # Mostrar el menú principal
            print(client_socket.recv(1024).decode(), end="")
            opcion = input().strip()
            client_socket.sendall(opcion.encode() + b'\n')

            if opcion == "1":  # Registro
                print(client_socket.recv(1024).decode(), end="")
                username = input().strip()
                client_socket.sendall(username.encode() + b'\n')

                print(client_socket.recv(1024).decode(), end="")
                password = getpass.getpass("Ingrese su contraseña: ")
                client_socket.sendall(password.encode() + b'\n')

                response = client_socket.recv(1024).decode()
                print(response)

            elif opcion == "2":  # Iniciar sesión
                while True:  # Permitir reintentos en el login sin cerrar el socket
                    print(client_socket.recv(1024).decode(), end="")
                    username = input().strip()
                    client_socket.sendall(username.encode() + b'\n')

                    print(client_socket.recv(1024).decode(), end="")
                    password = getpass.getpass("Ingrese su contraseña: ")
                    client_socket.sendall(password.encode() + b'\n')

                    response = client_socket.recv(1024).decode()
                    print(response)

                    if "Inicio de sesión exitoso" in response:
                        break  # Salir del bucle de reintento si el login es correcto
                    elif "bloqueada" in response:
                        print("Cuenta bloqueada temporalmente. Intente más tarde.")
                        break

            elif opcion == "3":  # Cerrar sesión
                print(client_socket.recv(1024).decode(), end="")
                username = input().strip()
                client_socket.sendall(username.encode() + b'\n')

                response = client_socket.recv(1024).decode()
                print(response)
            
            else:
                print("Opción inválida.")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    client()
