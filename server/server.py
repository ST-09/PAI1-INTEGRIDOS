import socket
import threading
import psycopg2
import bcrypt
from datetime import datetime, timedelta
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


def create_login_attempts_table():
    """Crea la tabla para registrar intentos de login"""
    conn, cursor = conectar_db()
    if not conn or not cursor:
        return "Error de conexión a la base de datos."
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            username VARCHAR(50) PRIMARY KEY,
            attempts INT DEFAULT 0,
            last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
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
    """Verifica credenciales con bloqueo tras varios intentos fallidos"""
    try:
        conn, cursor = conectar_db()
        if not conn or not cursor:
            return "Error de conexión a la base de datos."
        
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            actualizar_intentos(cursor, conn, username)
            return "Acceso denegado: credenciales incorrectas."

        stored_password = user[0]  

        # 🔹 Convertir el hash de BYTEA a string UTF-8 si es necesario
        if isinstance(stored_password, memoryview):  
            stored_password = stored_password.tobytes().decode('utf-8')

        if not bcrypt.checkpw(password.encode(), stored_password.encode()):
            actualizar_intentos(cursor, conn, username)
            return "Acceso denegado: credenciales incorrectas."

        # Restablecer intentos fallidos en caso de éxito
        cursor.execute("DELETE FROM login_attempts WHERE username = %s", (username,))
        conn.commit()

        return "Inicio de sesión exitoso."

    finally:
        cursor.close()
        conn.close()




def actualizar_intentos(cursor, conn, username):
    """Actualiza intentos fallidos y bloquea si es necesario"""
    cursor.execute("SELECT attempts FROM login_attempts WHERE username = %s", (username,))
    row = cursor.fetchone()

    if row:
        attempts = row[0] + 1
        cursor.execute("UPDATE login_attempts SET attempts = %s, last_attempt = CURRENT_TIMESTAMP WHERE username = %s", (attempts, username))
    else:
        cursor.execute("INSERT INTO login_attempts (username, attempts) VALUES (%s, 1)", (username,))

    conn.commit()




def handle_client(client_socket):
    try:
        client_socket.sendall("Seleccione una opción:\n1. Registrarse\n2. Iniciar sesión\n".encode("utf-8"))
        opcion = client_socket.recv(1024).decode().strip()

        client_socket.sendall("Ingrese nombre de usuario: ".encode("utf-8"))
        username = client_socket.recv(1024).decode().strip()

        client_socket.sendall("Ingrese contraseña: ".encode("utf-8"))
        password = client_socket.recv(1024).decode().strip()
        password_hash = hash_password(password)

        if opcion == "1":
            if registrar_usuario(username, password_hash):
                client_socket.sendall("Registro exitoso.\n".encode("utf-8"))
            else:
                client_socket.sendall("Usuario ya existe. Registro fallido.\n".encode("utf-8"))

        elif opcion == "2":
            resultado = verificar_credenciales(username, password)
            client_socket.sendall(f"{resultado}\n".encode("utf-8"))


        else:
            client_socket.sendall("Opción inválida.\n".encode("utf-8"))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


def insertar_usuarios_preexistentes():
    """Inserta un conjunto inicial de usuarios si no existen"""
    usuarios_iniciales = [
        ("admin", "admin123"),
        ("user1", "password1"),
        ("user2", "password2")
    ]
    
    try:
        conn, cursor = conectar_db()
        if not conn or not cursor:
            return "Error de conexión a la base de datos."

        for username, password in usuarios_iniciales:
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                password_hash = hash_password(password).decode('utf-8')  # Convertimos a string
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                               (username, password_hash))

        conn.commit()
        print("Usuarios preexistentes cargados correctamente.")

    except Exception as e:
        print(f"Error al insertar usuarios preexistentes: {e}")

    finally:
        cursor.close()
        conn.close()




def main():
    create_users_table()
    create_login_attempts_table()
    insertar_usuarios_preexistentes()

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
