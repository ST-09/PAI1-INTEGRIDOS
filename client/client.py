import socket
import hashlib


def hash_password(password):
    """Genera un hash SHA-512 de la contraseña"""
    return hashlib.sha512(password.encode()).hexdigest()


def client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 3343))

        # Recibir el mensaje de solicitud de opción
        print(client_socket.recv(1024).decode(), end="")  
        opcion = input().strip()  # Leer la opción del cliente
        client_socket.sendall(opcion.encode() + b'\n')

        # Recibir el mensaje de solicitud de nombre de usuario
        print(client_socket.recv(1024).decode(), end="")  
        username = input().strip()
        client_socket.sendall(username.encode() + b'\n')

        # Recibir el mensaje de solicitud de contraseña
        print(client_socket.recv(1024).decode(), end="")  
        password = input().strip()
        client_socket.sendall(password.encode() + b'\n')  # Envía la contraseña en texto plano

        # Recibir respuesta del servidor
        response = client_socket.recv(1024).decode()
        print(response)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    client()
