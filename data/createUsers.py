import psycopg2
import bcrypt
import secrets
import string
from cryptography.fernet import Fernet


# Generar y guardar una clave de cifrado
def generate_encryption_key():
    key = Fernet.generate_key()
    with open("encryption_key.key", "wb") as key_file:
        key_file.write(key)
    return key


# Cargar la clave de cifrado
def load_encryption_key():
    return open("encryption_key.key", "rb").read()


# Cifrar texto con la clave proporcionada
def encrypt_text(text, key):
    fernet = Fernet(key)
    return fernet.encrypt(text.encode())


# Generar contraseñas seguras aleatorias
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))


# Hashear la contraseña para almacenarla en la base de datos
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


# Crear la tabla de usuarios
def create_table():
    conn = psycopg2.connect(
        dbname="insegus",
        user="st09",
        password="paulaylucia",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

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
    print("Tabla 'users' creada con éxito ✅")


# Insertar usuarios con contraseñas aleatorias y guardar las contraseñas en un archivo cifrado
def insert_users():
    conn = psycopg2.connect(
        dbname="insegus",
        user="st09",
        password="paulaylucia",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # Usuarios a crear (nombres sin contraseñas)
    usernames = ["admin1", "admin2", "user1", "user2"]
    passwords = {}

    # Cargar o generar la clave de cifrado
    try:
        key = load_encryption_key()
        print("Clave de cifrado cargada 🔑")
    except FileNotFoundError:
        key = generate_encryption_key()
        print("Nueva clave de cifrado generada 🔐")

    # Crear contraseñas aleatorias, guardarlas en la base de datos y en el diccionario
    for username in usernames:
        password = generate_password()
        passwords[username] = password
        hashed_password = hash_password(password)

        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (username, hashed_password))

    conn.commit()
    cursor.close()
    conn.close()
    print("Usuarios pre-registrados insertados con éxito ✅")

    # Guardar las contraseñas en un archivo cifrado
    with open("passwords_encrypted.txt", "wb") as f:
        for username, password in passwords.items():
            encrypted_password = encrypt_text(f"{username}:{password}", key)
            f.write(encrypted_password + b'\n')

    print("Contraseñas guardadas en 'passwords_encrypted.txt' 🔒")


create_table()
insert_users()
