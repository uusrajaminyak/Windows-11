from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

KEY = b'ThisIsTheBestKeyInTheWholeWorld!'

def encrypt_data(plain_text):
    try:
        data = plain_text.encode('utf-8')
        cipher = AES.new(KEY, AES.MODE_GCM)
        cipher_text, tag = cipher.encrypt_and_digest(data)
        encrypted_blob = cipher.nonce + tag + cipher_text
        return base64.b64encode(encrypted_blob).decode('utf-8')
    except Exception as e:
        print(f"[-] Encryption error: {e}")
        return None
    
def decrypt_data(encrypted_text):
    try:
        data = base64.b64decode(encrypted_text)
        nonce = data[:16]
        tag = data[16:32]
        cipher_text = data[32:]
        cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(cipher_text, tag)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"[-] Decryption error: {e}")
        return None