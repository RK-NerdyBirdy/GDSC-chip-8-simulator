import random 
import time 
import sys
import numpy as np 
import pygame
w = 64
h = 32

mem = bytearray(4096) # 4kb byts 
V = bytearray(16) # 16 8-bit registers 
I = 0 #index register
pc = 0x200
stack =[]
delay_timer = 0
sound_timer = 0
display = np.zeros((h,w),dtype = np.uint8) #64 x 32 pixels (0 or 1 )

keypad = [0]*16 #16 keys 
fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]

for i,font_byte in enumerate(fontset):
    mem[i] = font_byte

d_flag = False #draw flag is set to false

wait_for_key = False
key_register =0

def load_rom(rompath:str):
    try:
        with open(rompath,'rb') as f:
            romdata = f.read()
        if len(romdata)>4096 - 0x200:
            raise ValueError(f"Rom too large: {len(romdata)} bytes")
        for i,byte in enumerate(romdata):
            mem[0x200+i] = byte
        print(f"Loaded Rom: {rompath} ({len(romdata)}) bytes")

    
            
    except Exception as e:
        print(f"error loading rom due to {e}")
        sys.exit(1)


def emulate_cycle():
    #execute one cpu cycle (fetch,decode,execute)
    global pc, sound_timer,delay_timer
    opcode = (mem[pc]<<8) | mem[pc+1]
    pc +=2
    execute_opcode(opcode)

    if delay_timer>0:
        delay_timer -= 1
    if sound_timer>0:
        sound_timer -=1

def execute_opcode(opcode:int):
    global pc,I, delay_timer,sound_timer,w,h,wait_for_key,display,keypad,d_flag
    #execute given code
    x = (opcode & 0x0F00)>>8 #second nibble
    y = (opcode & 0x00F0) >>4 #third nibble
    n = opcode &0x000F #fourth nibble
    nn = opcode & 0x00FF # second byte
    nnn = opcode & 0x0FFF #last 12 bytes

    l = opcode&0xF000

    if l == 0x0000:

        if opcode == 0x00E0: #clear screen
            display.fill(0)
            d_flag = True

        elif opcode == 0x00EE:
            pc = stack.pop() #Return from function call

        else:
            print(f"Unknown opcode: {opcode:04X}")


    elif l == 0x1000:
        pc = nnn #jum to address nnn

    elif l == 0x2000:
        stack.append(pc) #add stackframe
        pc = nnn
    
    elif l == 0x3000:
        if V[x] == nn:
            pc +=2 # SE VC, byte: skip if vc ==n

    elif l == 0x4000:
        if V[x] != nn:
            pc +=2  # SNE Vx, byte: Skip if Vx != nn

    elif l == 0x5000:
        if V[x] == V[y]:
                    # SNE VX, VY: skp if VX = VY
            pc+=2

    elif l == 0x6000:
        V[x] = nn

    elif l == 0x7000:
        V[x] = (V[x]+nn) &0xFF #ensuring 8bit result
    
    elif l == 0x8000:
        if n == 0x0:
            V[x] = V[y]
        
        elif n == 0x1:
            V[x] |= V[y]
        
        elif n == 0x2:
            V[x] &= V[y]
        
        elif n == 0x3:
            V[x] ^= V[y]
        
        elif n == 0x4:
            res = V[x] + V[y]
            V[0xF] = 1 if res >0xFF else 0 
            V[x] = res &0xFF #lowest 8 bits only
        elif n == 0x5:
            V[0xF] = 1 if V[x] > V[y] else 0
            V[x] = (V[x] - V[y]) &0xFF
        
        elif n == 0x6:
            V[0xF] = V[x] &0x1
            V[x] >>=1
        elif n ==0x7:
            V[0xF] = 1 if V[y] > V[x] else 0
            V[x] = (V[y] - V[x]) &0xFF
        elif n == 0xE:
            V[0xF] = (V[x]& 0x80)>>7 
            V[x] = (V[x] <<1) &0xFF
        
        else:
            print(f"Unknown opcode: {opcode:04X}")

    elif l == 0x9000:
        if V[x] != V[y]: 
            pc+=2
    elif l == 0xA000:
        I = nnn
    elif l == 0xB000:
        pc += nnn+ V[0]
    
    elif l == 0xC000:
        V[x] = random.randint(0,255)&nn
    elif l == 0xD000:
        xcoord = V[x] % w
        ycoord = V[y] % h
        V[0xF] = 0

        for row in range(n):
            if ycoord+row >= h:
                break
            spbyte = mem[I+row]

            for col in range(8):
                if xcoord+col >= w:
                    break
                if(spbyte &(0x80>>col)) !=0:
                    if display[ycoord+row][xcoord+col] == 1:
                        V[0xF] = 1
                    display[ycoord+row][xcoord+col] ^=1
        
        d_flag =True

    elif l == 0xE000:
        if nn == 0x9E:
            if keypad[V[x] & 0xF] !=0:
                pc +=2
        elif nn == 0xA1:
            if keypad[V[x] & 0xF] ==0:
                pc +=2
    
    elif l == 0XF000:
        if nn == 0x07:
            V[x] = delay_timer
        
        elif nn == 0x0A:
            wait_for_key =True
            key_register = x 
            pc -=2
        
        elif nn == 0x15:
            delay_timer=V[x]
        
        elif nn == 0x18:
            sound_timer = V[x]
        
        elif nn == 0x1E:
            I = (I + V[x]) &0xFFF
        
        elif nn == 0x29:
            I = V[x] *5
        
        elif nn == 0x33:
            mem[I] = V[x]//100
            mem[I+1] = (V[x]//10)%10
            mem[I+2] = V[x]%10
        
        elif nn == 0x55:
            for i in range(x+1):
                mem[I+i] = V[i]
        
        elif nn == 0x65:
            for i in range(x+1):
                V[i] = mem[I+i]
        
        else:
            print(f"Unkown opcode: {opcode:04X}")

    else:
        print(f"Unkown opcode: {opcode:04X}")

            
def handle_key_d(key:int):
    global wait_for_key, key_register,keypad
    keypad[key] = 1
    if wait_for_key:
        V[key_register] = key
        wait_for_key = False
        pc +=2

def handle_key_up(key:int):
    global keypad
    keypad[key] = 0


pxl_size = 10
cspeed = 500

dw = w*pxl_size
dh = h *pxl_size

if len(sys.argv) < 2:
    print("Usage: python chip8_emulator.py <rom_path>")
    sys.exit(1)

rompath = sys.argv[1]
    
load_rom(rompath)

pygame.init()
screen = pygame.display.set_mode((dw,dh))
pygame.display.set_caption(f"CHIP-8 Emulator - {rompath}")

keymapping = {
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
        }

clock = pygame.time.Clock()

def update_display():
    screen.fill((0,0,0)) #cls
    global pxl_size 
    for y in range(h):
        for x in range(w):
            if display[y][x]==1:
                pygame.draw.rect(screen, (255,255,255), (x* pxl_size, y* pxl_size, pxl_size,pxl_size))

    pygame.display.flip()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in keymapping:
                handle_key_d(keymapping[event.key])
        elif event.type == pygame.KEYUP:
            if event.key in keymapping:
                handle_key_up(keymapping[event.key])
    
    if not wait_for_key:
        emulate_cycle()
    
    if d_flag:
        update_display()
        d_flag=False
    
    clock.tick(cspeed)
pygame.quit()
    


         

