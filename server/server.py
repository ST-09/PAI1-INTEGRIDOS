import socket
import threading
import hashlib
import psycopg2

# Conexión a PostgreSQL
DB_CONFIG = {
    "dbname": "insegus",
    "user": "st09",
    "password": "paulaylucia",
    "host": "localhost",
    "port": "5432"
}


def conectar_db():
    """Conecta a PostgreSQL y retorna el cursor y la conexión"""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn, conn.cursor()


def hash_password(password):
    """Genera un hash SHA-512 de la contraseña"""
    return hashlib.sha512(password.encode()).hexdigest()


def registrar_usuario(username, password_hash):
    """Registra un usuario en la base de datos"""
    try:
        conn, cursor = conectar_db()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False  # Usuario ya existe
    finally:
        cursor.close()
        conn.close()


def handle_client(client_socket):
    try:
        client_socket.sendall(b"Ingrese nombre de usuario: ")
        username = client_socket.recv(1024).decode().strip()

        client_socket.sendall("Ingrese contraseña: ".encode("utf-8"))
        password = client_socket.recv(1024).decode().strip()
        password_hash = hash_password(password)

        if registrar_usuario(username, password_hash):
            client_socket.sendall(b"Registro exitoso.\n")
        else:
            client_socket.sendall(b"Usuario ya existe. Registro fallido.\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 3343))
    server.listen(5)
    print("Servidor escuchando en el puerto 3343...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexion aceptada de {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    main()
