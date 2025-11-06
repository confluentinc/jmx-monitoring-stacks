import hashlib

def hash_password(password, salt, iterations=210000, dklen=128):
    key = hashlib.pbkdf2_hmac(
        'sha512', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        iterations, 
        dklen
    )
    return key.hex()

def verify_password(password, salt, expected_hash, iterations=210000, dklen=128):
    return hash_password(password, salt, iterations, dklen) == expected_hash

if __name__ == "__main__":
    salt = "98LeBWIjca"
    password = "MySecretPassword"
    hashed = hash_password(password, salt)
    print("Hash:", hashed)

    print("Valid?", verify_password(password, salt, hashed))