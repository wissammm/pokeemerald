import subprocess
import time
import sys
import re
import os
import socket
import threading
import queue

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

    def _wait_for_prompt(self):
        output = ""
        while True:
            line = self.gdb.stdout.readline()
            if line == "":
                print("[ERROR] GDB stdout closed unexpectedly.")
                break
            output += line
            if "(gdb)" in line:
                break
        return output

    def send_cli_cmd(self, cmd):
        print(f"Sending CLI: {cmd}")
        self.gdb.stdin.write(cmd + "\n")
        self.gdb.stdin.flush()
        return self._wait_for_prompt()
    
    def send_mi_cmd(self, cmd):
        print(f"Sending MI: {cmd}")
        self.gdb.stdin.write(cmd + "\n")
        self.gdb.stdin.flush()
        response = ""
        while True:
            line = self.gdb.stdout.readline()
            if line.strip() == "":
                continue
            response += line
            if line.startswith("^done") or line.startswith("^error"):
                break


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
        stderr=subprocess.PIPE
    )
    

def wait_for_breakpoint(gdb):
    print("Waiting for breakpoint...")
    while True:
        output = gdb._wait_for_prompt()
        if "Breakpoint" in output or "stopped" in output:
            print("Breakpoint hit!")
            break
        time.sleep(0.5)

def parse_c_struct_output(output):
    struct_str = output.split('=')[-1].strip().lstrip('{').rstrip('}')
    result = {}

    array_pattern = re.compile(r'(\w+)\s*=\s*\{([^\}]*)\}')
    for arr_match in array_pattern.finditer(struct_str):
        key = arr_match.group(1)
        values = [int(x.strip()) for x in arr_match.group(2).split(',') if x.strip()]
        result[key] = values
        struct_str = struct_str.replace(arr_match.group(0), '')

    string_pattern = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
    for str_match in string_pattern.finditer(struct_str):
        key = str_match.group(1)
        value = str_match.group(2)
        result[key] = value
        struct_str = struct_str.replace(str_match.group(0), '')

    for part in struct_str.split(','):
        if '=' in part:
            key, value = part.split('=', 1)
            try:
                result[key.strip()] = int(value.strip())
            except ValueError:
                result[key.strip()] = value.strip()

    return result

def get_gplayerparty_mon_data(gdb, index=0):
    fields = ['hp', 'maxHP', 'level', 'status', 'attack', 'defense', 'speed', 'spAttack', 'spDefense']
    data = {}
    prefix = f"gPlayerParty[{index}]"
    for field in fields:
        cmd = f"print {prefix}.{field}"
        output = gdb.send_mi_cmd(cmd)
        match = re.search(r'=\s*(\d+)', output)
        if match:
            data[field] = int(match.group(1))
    return data

def get_struct_dump(gdb, expr):
    output = gdb.send_mi_cmd(f"print {expr}")
    return parse_c_struct_output(output)

def main(make_project=False):
    if make_project:
        make_result = make_mgba_gdb(MAKE_PATH)
        print(make_result.stdout)
        if make_result.returncode != 0:
            print("Make failed:", make_result.stderr)
            return

    mgba_proc = launch_mgba(ELF_PATH, GDB_PORT)
    print("mgba created")
      # Give mGBA time to start
    
    GDBSession.wait_for_port(GDB_PORT)
    gdb = GDBSession(GDB_PATH, ELF_PATH, GDB_PORT)
    print(str(gdb))
    gdb.send_mi_cmd("set pagination off")
    gdb.send_mi_cmd("set confirm off")
    gdb.send_mi_cmd("set verbose off")
    gdb.send_cli_cmd(f"target remote localhost:{GDB_PORT}")

    print("Setting breakpoint...")
    gdb.send_mi_cmd("-break-insert GetBattlerPosition")



    wait_for_breakpoint(gdb)
    print("Setting variable...")
    gdb.send_mi_cmd("-gdb-set var=action=1")
    print(gdb.send_mi_cmd("-data-evaluate-expression action"))

    print("Reading gPlayerParty[0]...")
    mon_data = get_gplayerparty_mon_data(gdb, 0)
    for k, v in mon_data.items():
        print(f"{k}: {v}")

    print("Dumping struct...")
    debug_dump = get_struct_dump(gdb, "gBattleMonsDebug[0]")
    for k, v in debug_dump.items():
        print(f"{k}: {v}")

    gdb.close()

if __name__ == "__main__":
    make = len(sys.argv) > 1 and sys.argv[1].lower() == "make"
    main(make)
