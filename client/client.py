import socket
import getpass
import hmac
import hashlib
import os
import base64

SECRET_KEY = b"mi_clave_secreta"


# Generar un NONCE aleatorio
def generate_nonce(length=16):
    return base64.b64encode(os.urandom(length)).decode('utf-8')


# Crear un HMAC con el mensaje y el NONCE
def generate_hmac(message, nonce, secret_key=SECRET_KEY):
    hmac_obj = hmac.new(secret_key, f"{message}{nonce}".encode(), hashlib.sha256)
    return hmac_obj.hexdigest()


def client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 3343))

        while True:
            server_message = client_socket.recv(1024).decode()
            print(server_message, end="")
            opcion = input().strip()
            client_socket.sendall(opcion.encode() + b'\n')

            if opcion == "2":
                print(client_socket.recv(1024).decode(), end="")
                username = input().strip()
                client_socket.sendall(username.encode() + b'\n')

                print(client_socket.recv(1024).decode(), end="")
                password = getpass.getpass("Ingrese su contraseña: ")
                client_socket.sendall(password.encode() + b'\n')

                # Recibir el mensaje, NONCE y HMAC
                response = client_socket.recv(1024).decode()
                print(response)

                if "NONCE:" in response and "HMAC:" in response:
                    message, nonce, received_hmac = parse_server_response(response)

                    # Verificar HMAC
                    expected_hmac = generate_hmac(message, nonce)
                    if hmac.compare_digest(expected_hmac, received_hmac):
                        print("Integridad verificada: Mensaje auténtico.")
                    else:
                        print("Error: Integridad comprometida. Mensaje alterado.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()


# Parsear la respuesta del servidor para extraer el mensaje, NONCE y HMAC
def parse_server_response(response):
    parts = response.split("\n")
    message = parts[0]
    nonce = parts[1].split("NONCE:")[1].strip()
    received_hmac = parts[2].split("HMAC:")[1].strip()
    return message, nonce, received_hmac


if __name__ == "__main__":
    client()
