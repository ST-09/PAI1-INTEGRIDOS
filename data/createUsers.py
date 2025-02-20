import psycopg2
import bcrypt  # Necesitas instalarlo con `pip install bcrypt`

def hash_password(password):
    """Genera un hash seguro con bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


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

def insert_users():
    conn = psycopg2.connect(
        dbname="insegus",
        user="st09",
        password="paulaylucia",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    users = [
        ("alice", "password123"),
        ("bob", "securepass"),
        ("charlie", "mypassword"),
        ("juan", "12345678"),
    ]

    for username, password in users:
        hashed_password = hash_password(password)  # Encriptamos la contraseña
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (username, hashed_password))

    conn.commit()
    cursor.close()
    conn.close()
    print("Usuarios pre-registrados insertados con éxito ✅")



def check_password(stored_password, provided_password):
    """Verifica si la contraseña proporcionada coincide con la almacenada"""
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())


# Crear la tabla antes de insertar los usuarios
create_table()
insert_users()
