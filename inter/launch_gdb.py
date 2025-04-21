import time
import subprocess
from pygdbmi.gdbcontroller import GdbController
from pygdbmi.constants import GdbTimeoutError
import sys
import re
GDB_PATH = "/opt/devkitpro/devkitARM/bin/arm-none-eabi-gdb"
ELF_PATH = "../pokeemerald_modern.elf"
MAKE_PATH = "../"
GDB_PORT = 2345

def make_mgba_gdb(make_path):
    print("Make gba gdb...")
    return subprocess.run(
        ['make', 'modern','DINFO=1','-j6'],
        cwd=make_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def launch_mgba(rom_path, port):
    print("Launching mGBA...")
    return subprocess.Popen(
        ['mgba-qt', '-g', f'-C', f'gdb.port={port}', rom_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def wait_for_breakpoint(gdbmi):
    print("Waiting for breakpoint to be hit...")
    break_hit = False
    while not break_hit:
        try:
            responses = gdbmi.get_gdb_response(timeout_sec=1)
            for resp in responses:
                if resp.get('type') == 'notify' and resp.get('message') == 'stopped':
                    break_hit = True
                    print("Breakpoint hit!")
                    break
        except GdbTimeoutError:
            pass
        if not break_hit:
            time.sleep(0.5)

def get_gplayerparty_mon_data(gdbmi, index=0):
    fields = [
        'hp', 'maxHP', 'level', 'status', 'attack', 'defense', 'speed', 'spAttack', 'spDefense'
    ]
    data = {}
    prefix = f"gPlayerParty[{index}]"
    for field in fields:
        cmd = f"p {prefix}.{field}"
        response = gdbmi.write(cmd, timeout_sec=5)
        for msg in response:
            if msg.get('type') == 'console' and '$' in msg.get('payload', ''):
                value = msg['payload'].split('=')[-1].strip()
                data[field] = value
                break
    
    return data

def parse_c_string_bytes(s):
    # s is a C string like "\031\024(\n"
    # Remove quotes if present
    s = s.strip('"')
    # Decode C escape sequences and get bytes
    bytestr = s.encode('latin1').decode('unicode_escape').encode('latin1')
    return [b for b in bytestr]

def get_gplayerparty_mon_dump(gdbmi, index=0):
    cmd = f"p DumpPartyMonData(&gPlayerParty[{index}])"
    response = gdbmi.write(cmd, timeout_sec=5)
    for msg in response:
        if msg.get('type') == 'console' and '$' in msg.get('payload', ''):
            payload = msg['payload']
            print("Raw DumpPartyMonData output:", payload)
            struct_str = payload.split('=', 1)[-1].strip().lstrip('{').rstrip('}\n')
            result = {}

            array_pattern = re.compile(r'(\w+)\s*=\s*\{([^\}]*)\}')
            for arr_match in array_pattern.finditer(struct_str):
                key = arr_match.group(1)
                values = [int(x.strip()) for x in arr_match.group(2).split(',')]
                result[key] = values
                struct_str = struct_str.replace(arr_match.group(0), '')  # Remove parsed array

            string_pattern = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
            for str_match in string_pattern.finditer(struct_str):
                key = str_match.group(1)
                value = str_match.group(2)
                result[key] = parse_c_string_bytes('"' + value + '"')
                struct_str = struct_str.replace(str_match.group(0), '')

            for part in struct_str.split(','):
                if '=' in part:
                    key, value = part.split('=', 1)
                    try:
                        result[key.strip()] = int(value.strip())
                    except ValueError:
                        result[key.strip()] = value.strip()
            return result
    return None

def main(make_project=False):
    mgba_make = make_mgba_gdb(MAKE_PATH) 
    mgba_proc = launch_mgba(ELF_PATH, GDB_PORT)
    print("Waiting for mGBA to start...")
    time.sleep(2)  # Wait for mGBA to be ready

    gdbmi = GdbController(command=[GDB_PATH, '--interpreter=mi2'])
    print("Loading ELF...")
    print(gdbmi.write(f'file {ELF_PATH}', timeout_sec=5))
    print("Connecting to GDB server...")
    print(gdbmi.write(f'-target-select remote localhost:{GDB_PORT}', timeout_sec=5))

    print("Setting breakpoints...")
    print(gdbmi.write('break SetWildMonHeldItem', timeout_sec=5))

    input("Press Enter to continue execution...")
    gdbmi.write('continue')

    wait_for_breakpoint(gdbmi)

    print("Inspecting gPlayerParty[0] data...")
    mon_data = get_gplayerparty_mon_data(gdbmi, 0)
    print("gPlayerParty[0]:", mon_data)
    mon_data = get_gplayerparty_mon_dump(gdbmi, 0)
    print("gPlayerParty[0]:", mon_data)


if __name__ == "__main__":
    make = False
    if len(sys.argv) > 1 and sys.argv[1].lower() == "make":
        make = True
    main(make)