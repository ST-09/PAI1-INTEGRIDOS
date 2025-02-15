import psycopg2

# Configuración de la conexión
DB_NAME = "insegus"
DB_USER = "st09"
DB_PASSWORD = "paulaylucia"
DB_HOST = "localhost"  # Cambia si usas un servidor remoto
DB_PORT = "5432"  # Puerto por defecto de PostgreSQL

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Conexión exitosa a PostgreSQL 🚀")
except Exception as e:
    print(f"Error conectando a PostgreSQL: {e}")

# Cierra la conexión
conn.close()
