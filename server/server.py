import socket
import threading
import psycopg2
import bcrypt
from datetime import datetime, timedelta
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


MAX_ATTEMPTS = 5
LOCK_TIME = timedelta(minutes=5)

DB_CONFIG = {
    "dbname": "insegus",
    "user": "st09",
    "password": "paulaylucia",
    "host": "localhost",
    "port": "5432"
}

active_sessions = {}
failed_attempts = {}
locked_users = {}
locked_nonces = set() #NONCES usados


def conectar_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn, conn.cursor()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None, None


def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def registrar_usuario(username, password_hash):
    try:
        conn, cursor = conectar_db()
        if not conn or not cursor:
            return "Error de conexión a la base de datos."

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                       (username, password_hash.decode('utf-8')))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    finally:
        cursor.close()
        conn.close()


def create_users_table():
    conn, cursor = conectar_db()
    if not conn or not cursor:
        return
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


def verificar_credenciales(username, password):
    global failed_attempts, locked_users

    if username in locked_users:
        if datetime.now() < locked_users[username]:
            return "Usuario bloqueado temporalmente. Inténtelo más tarde."
        else:
            del locked_users[username]

    try:
        conn, cursor = conectar_db()
        if not conn or not cursor:
            return "Error de conexión a la base de datos."

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return "Acceso denegado: credenciales incorrectas."

        stored_password = user[0]
        if isinstance(stored_password, memoryview):
            stored_password = stored_password.tobytes().decode('utf-8')

        if not bcrypt.checkpw(password.encode(), stored_password.encode()):
            failed_attempts[username] = failed_attempts.get(username, 0) + 1
            if failed_attempts[username] >= MAX_ATTEMPTS:
                locked_users[username] = datetime.now() + LOCK_TIME
                failed_attempts.pop(username, None)
                return "Usuario bloqueado temporalmente. Inténtelo más tarde."
            return "Acceso denegado: credenciales incorrectas."

        failed_attempts.pop(username, None)
        return "Inicio de sesión exitoso."

    finally:
        cursor.close()
        conn.close()


def handle_client(client_socket):
    try:
        client_socket.sendall("Seleccione una opción:\n1. Registrarse\n2. Iniciar sesión\n3. Cerrar sesión\n4. Realizar transacción\n".encode("utf-8"))
        opcion = client_socket.recv(1024).decode().strip()

        if opcion == "1":
            client_socket.sendall("Ingrese nombre de usuario: ".encode("utf-8"))
            username = client_socket.recv(1024).decode().strip()
            client_socket.sendall("Ingrese contraseña: ".encode("utf-8"))
            password = client_socket.recv(1024).decode().strip()
            password_hash = hash_password(password)

            if registrar_usuario(username, password_hash):
                client_socket.sendall("Registro exitoso.\n".encode("utf-8"))
            else:
                client_socket.sendall("Usuario ya existe. Registro fallido.\n".encode("utf-8"))

        if opcion == "2":
            client_socket.sendall("Ingrese nombre de usuario: ".encode("utf-8"))
            username = client_socket.recv(1024).decode().strip()
            client_socket.sendall("Ingrese contraseña: ".encode("utf-8"))
            password = client_socket.recv(1024).decode().strip()

            resultado = verificar_credenciales(username, password)
            if resultado == "Inicio de sesión exitoso.":
                active_sessions[username] = client_socket

                # Generar y enviar NONCE
                nonce = generate_nonce()
                locked_nonces.add(nonce)

                # Generar y enviar HMAC
                hmac_value = generate_hmac(resultado, nonce)
                client_socket.sendall(f"{resultado}\nNONCE:{nonce}\nHMAC:{hmac_value}\n".encode("utf-8"))
            else:
                client_socket.sendall(f"{resultado}\n".encode("utf-8"))

        elif opcion == "4":
            client_socket.sendall("Ingrese su nombre de usuario: ".encode("utf-8"))
            username = client_socket.recv(1024).decode().strip()

            if username in active_sessions:
                client_socket.sendall("Introduzca la transacción: ".encode("utf-8"))
                transaccion = client_socket.recv(1024).decode().strip()

                # Generar NONCE para la transacción
                nonce = generate_nonce()
                locked_nonces.add(nonce)

                # Generar y enviar HMAC
                hmac_value = generate_hmac(transaccion, nonce)
                client_socket.sendall(f"Transacción completada.\nNONCE:{nonce}\nHMAC:{hmac_value}\n".encode("utf-8"))
            else:
                client_socket.sendall("Usuario no tiene sesión activa.\n".encode("utf-8"))

        else:
            client_socket.sendall("Opción inválida.\n".encode("utf-8"))

    finally:
        client_socket.close()


def main():
    create_users_table()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 3343))
    server.listen(5)
    print("Servidor escuchando en el puerto 3343...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexión aceptada de {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
