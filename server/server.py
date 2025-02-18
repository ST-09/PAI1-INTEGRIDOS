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

def verificar_credenciales(username, password):
    """Verifica si las credenciales proporcionadas son correctas y devuelve un mensaje apropiado"""
    try:
        conn, cursor = conectar_db()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return "Acceso denegado: usuario no encontrado."

        stored_password = user[0]
        if stored_password != hash_password(password):
            return "Acceso denegado: contraseña incorrecta."

        return "Inicio de sesión exitoso."

    except Exception as e:
        return f"Error en la autenticación: {e}"

    finally:
        cursor.close()
        conn.close()




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

        for username, password in usuarios_iniciales:
            # Revisar si el usuario ya existe
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():  # Si no existe, lo insertamos
                password_hash = hash_password(password)
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))

        conn.commit()
        print("Usuarios preexistentes cargados correctamente.")

    except Exception as e:
        print(f"Error al insertar usuarios preexistentes: {e}")

    finally:
        cursor.close()
        conn.close()


def main():
    insertar_usuarios_preexistentes() #Cargar usuarios preexistentes
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
