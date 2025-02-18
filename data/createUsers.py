import psycopg2


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
    # Conexión a la base de datos
    conn = psycopg2.connect(
        dbname="insegus",
        user="st09",
        password="paulaylucia",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # Lista de usuarios pre-registrados
    users = [
        ("alice", "password123"),
        ("bob", "securepass"),
        ("charlie", "mypassword"),
        ("juan", "12345678"),
    ]

    # Insertar usuarios en la tabla
    for username, password in users:
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (username, password))

    # Confirmar cambios y cerrar conexión
    conn.commit()
    cursor.close()
    conn.close()
    print("Usuarios pre-registrados insertados con éxito ✅")


# Crear la tabla antes de insertar los usuarios
create_table()

# Ejecutar la función
insert_users()
