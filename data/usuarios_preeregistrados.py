import os
from cryptography.fernet import Fernet


# Obtener la ruta del archivo de clave en la misma carpeta que el script
def load_encryption_key():
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    key_file_path = os.path.join(script_dir, "encryption_key.key")  
    return open(key_file_path, "rb").read()


# Desencriptar el texto
def decrypt_text(encrypted_text, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text).decode()


# Cargar las contraseñas cifradas
def load_encrypted_passwords():
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    passwords_file_path = os.path.join(script_dir, "passwords_encrypted.txt") 
    with open(passwords_file_path, "rb") as file:
        return file.readlines()


# Desencriptar y mostrar las contraseñas
def display_decrypted_passwords():
    # Cargar la clave de cifrado
    key = load_encryption_key()
    print("Asegurese de guardar estas contraseñas para los usuarios pre registrados en un lugar seguro:")

    # Cargar las contraseñas cifradas
    encrypted_passwords = load_encrypted_passwords()

    # Desencriptar y mostrar
    for encrypted_password in encrypted_passwords:
        decrypted_password = decrypt_text(encrypted_password.strip(), key)
        print(decrypted_password)


# Ejecutar la función para mostrar las contraseñas desencriptadas

display_decrypted_passwords()
