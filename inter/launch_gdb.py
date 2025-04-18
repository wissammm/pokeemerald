import pygdbmi 
import time
from pygdbmi.gdbcontroller import GdbController
from pygdbmi.constants import GdbTimeoutError
import subprocess
# Initialize GDB controller
gdbmi = GdbController()

class GDBMI:
    def __init__(self):
        self.gdbmi = GdbController()

    def write(self, command):
        response = self.gdbmi.write(command)
        return response

    def exit(self):
        self.gdbmi.exit()
    
    def getRegisters(self):
        response = self.gdbmi.write('info registers')
        return response
    
    def getVariable(self, variable_name):
        # Use GDB's `print` command to inspect the variable
        response = self.gdbmi.write(f'print {variable_name}')
        return response


GDB_PATH = "/opt/devkitpro/devkitARM/bin/arm-none-eabi-gdb"  # Update if needed

print("Launching mgba-qt...")
mgba_proc = subprocess.Popen(
    ['mgba-qt', '-g', '../pokeemerald_modern.elf'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(2)

# Use the correct GDB for ARM
gdbmi = GdbController(command=[GDB_PATH, '--interpreter=mi2'])

gdbmi.write('file ../pokeemerald_modern.elf')

gdbmi.write('-target-select remote localhost:2345', timeout_sec=5)

print("Setting breakpoints...")
print(gdbmi.write('break BattleMainCB2', timeout_sec=5))
print(gdbmi.write('break HandleAction_UseMove', timeout_sec=5))
print(gdbmi.write('break *0x0807570c', timeout_sec=5))

print(" Press Enter ")
input()
gdbmi.write('continue')

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

print("Inspecting gPlayerParty[0] species (raw offset)...")
response = gdbmi.write('p *(unsigned short *)((char *)&gPlayerParty[0] + 8)')
print("gPlayerParty[0] species:", response)

gdbmi.exit()