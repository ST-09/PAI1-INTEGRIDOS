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


create_table()
