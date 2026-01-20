import subprocess
import time
import os
import requests
from fpdf import FPDF

GUEST_IP = "192.168.75.128"
GUEST_URL = f"http://{GUEST_IP}:5000"
VMX_PATH = r"E:\SandboxVM.vmx"
VMRUN_PATH = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
SNAPSHOT_NAME = "ReadyState"
MALWARE_SAMPLE = "putty.exe"
REPORT_DIR = "REPORTS"

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)
    
def run_vm_command(action, extra_args=""):
    if not os.path.exists(VMRUN_PATH):
        print(f"Error: vmrun.exe not found at {VMRUN_PATH}")
        return False
    command = f'"{VMRUN_PATH}" -T ws {action} "{VMX_PATH}" {extra_args}'
    subprocess.run(command, shell=True)
    return True

def revert_vm():
    print("Reverting VM to snapshot...")
    run_vm_command(f"revertToSnapshot {SNAPSHOT_NAME}")
    print(f"Starting VM")
    run_vm_command("start")
    print("Waiting Windows & agent startup...")
    time.sleep(15)
    
def wait_for_agent():
    print("Waiting for agent to be ready...")
    for i in range(10):
        try:
            r = requests.get(f"{GUEST_URL}/status", timeout=2)
            if r.status_code == 200:
                print("Agent is ready.")
                return True
        except:
            print(f"Attempt {i+1}/10: Agent not ready yet, retrying...")
            time.sleep(2)
    return False  

def analyze_malware(file_path):
    print(f"Starting analysis for {file_path}...")
    with open(file_path, 'rb') as f:
        print("Uploading malware sample to guest...")
        try:
            r = requests.post(f"{GUEST_URL}/upload", files={"file": f})
            if r.status_code != 200:
                print(f"Failed to upload file, status code: {r.status_code}")
                print(f"Response: {r.text}")
                return None
            remote_path  =r.json()['path']
            print(f"Executing malware sample at {remote_path}...")
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    print("Exploding Malware...")
    try:
        r = requests.post(f"{GUEST_URL}/execute", json={"path": remote_path})
        if r.status_code != 200:
            print(f"Failed to execute malware, status code: {r.status_code}")
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error executing malware: {e}")
    print("Examining virus's behavior...")
    time.sleep(5)
    print("Collecting forensic data...")
    try:    
        r_img = requests.get(f"{GUEST_URL}/screenshot")
        if r_img.status_code != 200:
            print(f"Failed to get screenshot, status code: {r_img.status_code}")
            return None
        screenshot_name = os.path.join(REPORT_DIR, "evidence.png")
        with open(screenshot_name, 'wb') as img_file:
            img_file.write(r_img.content)
        print("Screenshot saved")
        return screenshot_name
    except Exception as e:
        print(f"Error collecting forensic data: {e}")
        return None   
    
def generate_report(screenshot_path):
    if not screenshot_path: return
    print("Creating PDF report...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Automatic Malware Analysis Report", ln=1, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Target: {MALWARE_SAMPLE}", ln=2)
    pdf.cell(200, 10, txt=f"IP Sandbox: {GUEST_IP}", ln=3)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Visual Evidence (VM Screenshot):", ln=4)
    pdf.image(screenshot_path, x=10, y=60, w=180)
    
    filename = os.path.join(REPORT_DIR, "Final_Report.pdf")
    pdf.output(filename)
    print(f"\n[SUCCESS] REPORT GENERATED: {os.path.abspath(filename)}")
    
def main():
    if not os.path.exists(MALWARE_SAMPLE):
        with open(MALWARE_SAMPLE, "w") as f:
            f.write("This is a dummy malware sample.")
        print(f"File dummy '{MALWARE_SAMPLE}' created for testing.")
    revert_vm()
    if wait_for_agent():
        proof = analyze_malware(MALWARE_SAMPLE)
        generate_report(proof)
    else:
        print("Agent failed to respond. Exiting.")
        
if __name__ == "__main__":
    main()