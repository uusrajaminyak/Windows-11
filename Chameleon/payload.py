import ctypes
import sys

def run_malware():
    print("[!] MALWARE IS RUNNING")
    ctypes.windll.user32.MessageBoxW(0, "Your system has been infected!", "Malware Alert", 1)
    
if __name__ == "__main__":
    run_malware()