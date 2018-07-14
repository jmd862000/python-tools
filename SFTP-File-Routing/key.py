from cryptography.fernet import Fernet
from getpass import getpass

def GenerateKeyFile(filename):
    password = getpass("Enter the password to hash: ")
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    ciphered_text = cipher_suite.encrypt(password.encode('utf-8'))
    with open(filename,'wb') as file_object:
        file_object.write(ciphered_text)
    print("Password hashed with master key: %s" % key)

def RetrievePassword(filename,master_key):
    cipher_suite = Fernet(master_key.encode('utf-8'))
    with open(filename,'rb') as file_object:
        for line in file_object:
            ciphered_text = line
    unciphered_text = (cipher_suite.decrypt(ciphered_text))
    return bytes(unciphered_text).decode('utf-8')