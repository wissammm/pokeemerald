import time
import subprocess
from pygdbmi.gdbcontroller import GdbController
from pygdbmi.constants import GdbTimeoutError

GDB_PATH = "/opt/devkitpro/devkitARM/bin/arm-none-eabi-gdb"
ELF_PATH = "../pokeemerald_modern.elf"
GDB_PORT = 2345

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

def main():
    mgba_proc = launch_mgba(ELF_PATH, GDB_PORT)
    print("Waiting for mGBA to start...")
    time.sleep(2)  # Wait for mGBA to be ready

    gdbmi = GdbController(command=[GDB_PATH, '--interpreter=mi2'])
    print("Loading ELF...")
    print(gdbmi.write(f'file {ELF_PATH}', timeout_sec=5))
    print("Connecting to GDB server...")
    print(gdbmi.write(f'-target-select remote localhost:{GDB_PORT}', timeout_sec=5))

    print("Setting breakpoints...")
    print(gdbmi.write('break BattleMainCB2', timeout_sec=5))
    print(gdbmi.write('break HandleAction_UseMove', timeout_sec=5))
    print(gdbmi.write('break *0x0807570c', timeout_sec=5))

    input("Press Enter to continue execution...")
    gdbmi.write('continue')

    wait_for_breakpoint(gdbmi)

    print("Inspecting gPlayerParty[0] data...")
    mon_data = get_gplayerparty_mon_data(gdbmi, 0)
    print("gPlayerParty[0]:", mon_data)

if __name__ == "__main__":
    main()