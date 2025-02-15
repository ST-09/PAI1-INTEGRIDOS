import psycopg2


def create_transactions_table():
    # Conexión a la base de datos
    conn = psycopg2.connect(
        dbname="insegus",
        user="st09",
        password="paulaylucia",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # Crear la tabla de transacciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            origin_account_id INT NOT NULL,
            destination_account_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Confirmar los cambios y cerrar la conexión
    conn.commit()
    cursor.close()
    conn.close()

    print("Tabla 'transactions' creada con éxito ✅")


# Llamada a la función para crear la tabla
create_transactions_table()
