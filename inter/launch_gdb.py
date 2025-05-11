import subprocess
import time
import sys
import re
import os
import socket
import select

GDB_PATH = "/opt/devkitpro/devkitARM/bin/arm-none-eabi-gdb"
ELF_PATH = "../pokeemerald_modern.elf"
MAKE_PATH = "../"
GDB_PORT = 2345

class GDBSession:
    def __init__(self, gdb_path, elf_path, port):
        self.gdb = subprocess.Popen(
            [gdb_path, elf_path, '--interpreter=mi2'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # self.stdout_queue = queue.Queue()
        # self._start_reader_thread()
        print("[GDB] Process started")
        self.port = port
        self._wait_for_prompt()
    
    def _wait_for_prompt(self):
        response = ''
        while True:
            line = self.gdb.stdout.readline()
            response += line
            if line == "":
                raise RuntimeError("[ERROR] GDB stdout closed.")
            print("[GDB OUTPUT]", line.strip())
            if line.startswith(("^done", "^connected", "^error")) or line.strip() == "(gdb)":
                break
        return response
    
    def wait_for_port(port, host="localhost", timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((host, port), timeout=1):
                    print(f"GDB port {port} is now open.")
                    return True
            except OSError:
                time.sleep(0.5)
        raise TimeoutError(f"Timeout: GDB server not available on port {port}")
       

    def send_mi_cmd(self, cmd, wait_for="^done"):
        self.gdb.stdin.write(cmd + '\n')
        self.gdb.stdin.flush()
        self._wait_for_prompt()

    def close(self):
        self.send_mi_cmd("quit")
        self.gdb.terminate()

def make_mgba_gdb(make_path):
    print("Making gba project...")
    return subprocess.run(
        ['make', 'modern', 'DINFO=1', '-j6'],
        cwd=make_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def launch_mgba(rom_path, port):
    print("Launching mGBA...")
    
    return subprocess.Popen(
        ['mgba-qt', '-g', '-C', f'gdb.port={port}', rom_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
# def wait_for_mgba_ready(proc, timeout=10):
#     start = time.time()
#     while time.time() - start < timeout:
#         line = proc.stderr.readline()
#         if not line:
#             break
#         print("[mGBA]", line.strip())
#         if "GDB stub listening on" in line:
#             return True
#     raise TimeoutError("mGBA did not start the GDB stub.")

def wait_for_mgba_ready(port, max_retries=20, initial_delay=0.5, max_delay=5):
    """
    Wait for mGBA to be ready by checking the connection at the given port.
    
    Parameters:
    - port: The port to connect to.
    - max_retries: The maximum number of retries before raising a TimeoutError.
    - initial_delay: The initial delay between connection attempts in seconds.
    - max_delay: The maximum delay between retries to avoid excessive waiting.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                print(f"mGBA is listening on port {port} (attempt {attempt}/{max_retries})")
                return
        except OSError:
            print(f"Attempt {attempt}/{max_retries} failed. Retrying in {delay}s...")
            time.sleep(delay)
            delay = min(delay * 2, max_delay)  # Exponential backoff with a cap

    raise TimeoutError(f"mGBA GDB stub is not ready after {max_retries} attempts.")

def main(make_project=False):
    if make_project:
        make_result = make_mgba_gdb(MAKE_PATH)
        print(make_result.stdout)
        if make_result.returncode != 0:
            print("Make failed:", make_result.stderr)
            return

    print("[main] Launching mGBA...")
    mgba_proc = launch_mgba(ELF_PATH, GDB_PORT)
    print("[main] Waiting for mGBA to be ready...")
    wait_for_mgba_ready(GDB_PORT)
    print("[main] GDB stub is ready")

    print("[main] Starting GDB session...")
    gdb = GDBSession(GDB_PATH, ELF_PATH, GDB_PORT)

    # Make sure we connect to the target before anything else
    print("[main] Connecting to remote GDB target...")
    gdb.send_mi_cmd("set remote X-packet off")
    gdb.send_mi_cmd("set remote hardware-watchpoint-limit 0")
    gdb.send_mi_cmd("set remote Z-packet off")
    gdb.send_mi_cmd("set remote noack-packet off")
    start = time.time()
    
    gdb.send_mi_cmd(f"-target-select remote localhost:{GDB_PORT}")
    print(f"[DEBUG] target-select took {time.time() - start:.2f} seconds")
    # Load ELF after connecting to the target
    print("[main] Executing -file-exec-and-symbols to load ELF...")
    gdb.send_mi_cmd(f"-file-exec-and-symbols {ELF_PATH}")
    print("[main] Executable loaded")

    # Disable packets if needed

    print("[main] Remote GDB configurations set")

    # Send an interrupt to pause execution
    print("[main] Sending interrupt to pause execution...")
    gdb.send_mi_cmd("-exec-interrupt")
    time.sleep(0.5)  # Wait a little for the game to pause
    print("[main] GDB paused")

    # Set breakpoints and continue
    print("[main] Setting breakpoint at HandleTurnActionSelectionState...")
    gdb.send_mi_cmd("break-insert HandleTurnActionSelectionState")
    
    
    # Evaluate expression
    print("[main] Evaluating expression 'isActionWritten'...")
    gdb.send_mi_cmd("-data-evaluate-expression isActionWritten")

    print("[main] Breakpoint set and execution continued")
    gdb.send_mi_cmd("-exec-continue")


    # print("Waiting for breakpoint...")
    # wait_for_breakpoint(gdb)
    # print("Setting variable...")
    # gdb.send_mi_cmd("-gdb-set var=action=1")
    # print(gdb.send_mi_cmd("-data-evaluate-expression action"))

    # print("Reading gPlayerParty[0]...")
    # mon_data = get_gplayerparty_mon_data(gdb, 0)
    # for k, v in mon_data.items():
    #     print(f"{k}: {v}")

    # print("Dumping struct...")
    # debug_dump = get_struct_dump(gdb, "gBattleMonsDebug[0]")
    # for k, v in debug_dump.items():
    #     print(f"{k}: {v}")

    # gdb.close()

if __name__ == "__main__":
    make = len(sys.argv) > 1 and sys.argv[1].lower() == "make"
    main(make)
