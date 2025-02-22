import socket
import threading
import psycopg2
import bcrypt
from datetime import timedelta
import signal

MAX_ATTEMPTS = 5
LOCK_TIME = timedelta(minutes=5)

# Conexión a PostgreSQL
DB_CONFIG = {
    "dbname": "insegus",
    "user": "st09",
    "password": "paulaylucia",
    "host": "localhost",
    "port": "5432"
}

# Diccionario para manejar las sesiones de usuarios
active_sessions = {}


def conectar_db():
    """Conecta a PostgreSQL y retorna el cursor y la conexión"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn, conn.cursor()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None, None


def hash_password(password):
    """Genera un hash seguro con bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def registrar_usuario(username, password_hash):
    """Registra un usuario en la base de datos"""
    try:
        conn, cursor = conectar_db()
        if not conn or not cursor:
            return "Error de conexión a la base de datos."

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                       (username, password_hash.decode('utf-8')))  # Guardar como string
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False  # Usuario ya existe
    finally:
        cursor.close()
        conn.close()


def create_users_table():
    """Crea la tabla 'users' si no existe"""
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
    """Verifica credenciales"""
    try:
        conn, cursor = conectar_db()
        if not conn or not cursor:
            return "Error de conexión a la base de datos."
        
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return "Acceso denegado: credenciales incorrectas."

        stored_password = user[0]

        # 🔹 Convertir el hash de BYTEA a string UTF-8 si es necesario
        if isinstance(stored_password, memoryview):  
            stored_password = stored_password.tobytes().decode('utf-8')

        if not bcrypt.checkpw(password.encode(), stored_password.encode()):
            return "Acceso denegado: credenciales incorrectas."

        return "Inicio de sesión exitoso."

    finally:
        cursor.close()
        conn.close()


def handle_client(client_socket):
    try:
        client_socket.sendall("Seleccione una opción:\n1. Registrarse\n2. Iniciar sesión\n3. Cerrar sesión\n".encode("utf-8"))
        opcion = client_socket.recv(1024).decode().strip()

        if opcion == "1":  # Registro
            client_socket.sendall("Ingrese nombre de usuario: ".encode("utf-8"))
            username = client_socket.recv(1024).decode().strip()
            client_socket.sendall("Ingrese contraseña: ".encode("utf-8"))
            password = client_socket.recv(1024).decode().strip()
            password_hash = hash_password(password)

            if registrar_usuario(username, password_hash):
                client_socket.sendall("Registro exitoso.\n".encode("utf-8"))
            else:
                client_socket.sendall("Usuario ya existe. Registro fallido.\n".encode("utf-8"))

        elif opcion == "2":  # Iniciar sesión
            client_socket.sendall("Ingrese nombre de usuario: ".encode("utf-8"))
            username = client_socket.recv(1024).decode().strip()
            client_socket.sendall("Ingrese contraseña: ".encode("utf-8"))
            password = client_socket.recv(1024).decode().strip()

            resultado = verificar_credenciales(username, password)
            if resultado == "Inicio de sesión exitoso.":
                active_sessions[username] = client_socket  # Guardar sesión activa
            client_socket.sendall(f"{resultado}\n".encode("utf-8"))

        elif opcion == "3":  # Cerrar sesión
            client_socket.sendall("Ingrese nombre de usuario para cerrar sesión: ".encode("utf-8"))
            username = client_socket.recv(1024).decode().strip()

            if username in active_sessions:
                del active_sessions[username]  # Eliminar sesión activa
                client_socket.sendall(f"Sesión cerrada para {username}\n".encode("utf-8"))
            else:
                client_socket.sendall(f"No hay sesión activa para {username}\n".encode("utf-8"))

        else:
            client_socket.sendall("Opción inválida.\n".encode("utf-8"))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


def main():
    create_users_table()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 3343))
    server.listen(5)
    print("Servidor escuchando en el puerto 3343...")

    # Manejo de interrupción con Ctrl+C
    def cerrar_servidor(sig, frame):
        print("\nCerrando servidor...")
        server.close()
        exit(0)

    signal.signal(signal.SIGINT, cerrar_servidor)

    while True:
        client_socket, addr = server.accept()
        print(f"Conexión aceptada de {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.daemon = True  # Cierra hilos cuando termina el script
        thread.start()


if __name__ == "__main__":
    main()
