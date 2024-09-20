import secrets
secret_key = secrets.token_hex(32)  # Generates a 64-character (32 bytes) hex string
print(secret_key)
