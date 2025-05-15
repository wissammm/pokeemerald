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
        response_lines = []

        while True:
            line = self.gdb.stdout.readline()
            if line == "":
                raise RuntimeError("[ERROR] GDB stdout closed.")
            line = line.rstrip("\r\n")
            response_lines.append(line)
            print("[GDB OUTPUT]", line)

            # Always collect everything, but only stop when prompt appears
            if line.strip() == "(gdb)":
                print("[GDB] Prompt received")
                break

        return '\n'.join(response_lines)
       
    def parse_mi_output(self, raw_output):
        results = []
        for line in raw_output.strip().splitlines():
            if line.startswith('*stopped'):
                match = re.search(r'reason="([^"]+)"', line)
                reason = match.group(1) if match else None
                func_match = re.search(r'func="([^"]+)"', line)
                func = func_match.group(1) if func_match else None
                results.append({
                    "reason": reason,
                    "frame": {"func": func} if func else {}
                })
        return results
    
    def send_mi_cmd(self, cmd, wait_for="^done"):
        self.gdb.stdin.write(cmd + '\n')
        self.gdb.stdin.flush()
        return self._wait_for_prompt()

    def wait_for_async_event(self, event_type="breakpoint-hit", timeout=100):
        start = time.time()
        buffer = ""
        print(f"[DEBUG] Waiting for async event: {event_type} (timeout = {timeout}s)")
        
        while time.time() - start < timeout:
            line = self.gdb.stdout.readline()
            if not line:
                print("[DEBUG] GDB stdout closed or returned nothing.")
                break

            line = line.strip()
            buffer += line + "\n"
            print("[GDB ASYNC RAW]", repr(line))  # Show raw line including escapes

            if line.startswith("*stopped"):
                print("[DEBUG] Found *stopped message")
                if event_type in line:
                    print(f"[DEBUG] Matched event type '{event_type}' in line")
                    return True
                else:
                    print(f"[DEBUG] *stopped event found but no match for '{event_type}'")
        
        print(f"[DEBUG] Timeout reached or no matching event found. Collected buffer:\n{buffer}")
        return False
    
    def close(self):
        self.send_mi_cmd("quit")
        self.gdb.terminate()

def make_mgba_gdb(make_path):
    # print("Making gba project...")
    return subprocess.run(
        ['make', 'modern', 'DINFO=1', '-j6'],
        cwd=make_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def launch_mgba(rom_path, port):
    # print("Launching mGBA...")
    
    return subprocess.Popen(
        ['mgba-qt', '-g', '-C', f'gdb.port={port}', rom_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
def setup_gdb_session():
    print("[GDB] Starting session...")
    gdb = GDBSession(GDB_PATH, ELF_PATH, GDB_PORT)

    # GDB connection settings
    gdb.send_mi_cmd("set remote X-packet off")
    gdb.send_mi_cmd("set remote hardware-watchpoint-limit 0")
    gdb.send_mi_cmd("set remote Z-packet off")
    gdb.send_mi_cmd("set remote noack-packet off")

    # Connect to target
    start = time.time()
    gdb.send_mi_cmd(f"-target-select remote localhost:{GDB_PORT}")
    print(f"[DEBUG] target-select took {time.time() - start:.2f}s")

    # Load symbols
    gdb.send_mi_cmd(f"-file-exec-and-symbols {ELF_PATH}")
    print("[GDB] Executable loaded.")
    return gdb

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
    launch_mgba(ELF_PATH, GDB_PORT)
    print("[main] Waiting for mGBA to be ready...")
    wait_for_mgba_ready(GDB_PORT)
    print("[main] GDB stub is ready")

    print("[main] Starting GDB session...")
    gdb = setup_gdb_session()
    


    # Set breakpoints and continue
    print("[main] Setting breakpoint at HandleTurnActionSelectionState...")
    print(gdb.send_mi_cmd("-break-insert GetBattlerPosition"))
    
    print("[main] After BP set...")
    status = gdb.send_mi_cmd("-thread-info")
    if "state=\"stopped\"" in status:
        print("[DEBUG] Target is stopped, continuing execution")
        gdb.send_mi_cmd("-exec-continue")
    else:
        print("[DEBUG] Target already running")
    # Wait for the breakpoint to be hit
    break_hit = gdb.wait_for_async_event(event_type="breakpoint-hit")

    if break_hit:
        # Evaluate the expression after hitting the breakpoint
        response = gdb.send_mi_cmd("-data-evaluate-expression isActionWritten")
        print("[main] isActionWritten =", response)
    else:
        print("[main] Breakpoint was not hit.")


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
