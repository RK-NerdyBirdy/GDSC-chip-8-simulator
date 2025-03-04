# CHIP-8 Emulator in Python

This is a simple CHIP-8 emulator written in Python using the `pygame` library. CHIP-8 is an interpreted programming language that was initially used on the COSMAC VIP and Telmac 1800 8-bit microcomputers in the mid-1970s. It is a great starting point for learning how to write emulators.

## Features

- **CHIP-8 CPU Emulation**: Supports the majority of the CHIP-8 instruction set, including graphics, input, and sound.
- **Graphics**: Renders a 64x32 pixel display, which can be scaled up using the `pxl_size` variable.
- **Input**: Supports a 16-key keypad, mapped to the keyboard.
- **ROM Loading**: Loads CHIP-8 ROMs from a file and executes them.

## Requirements

- Python 3.x
- `pygame` library
- `numpy` library

You can install the required libraries using:

```bash
pip install pygame numpy
```

## Usage

To run the emulator, use the following command:

```bash
python chip8_emulator.py <rom_path>
```

Replace `<rom_path>` with the path to your CHIP-8 ROM file.

### Example

```bash
python chip8_emulator.py roms/PONG
```

## Key Mapping

The CHIP-8 keypad is mapped to the following keys on your keyboard:

```
1 2 3 C    ->   1 2 3 4
4 5 6 D    ->   Q W E R
7 8 9 E    ->   A S D F
A 0 B F    ->   Z X C V
```

## Code Overview

### Memory
- **Memory (`mem`)**: 4KB of memory represented as a `bytearray` of size 4096.
- **Registers (`V`)**: 16 8-bit registers (V0 to VF), where VF is used as a flag register.
- **Index Register (`I`)**: 16-bit register used for memory addresses.
- **Program Counter (`pc`)**: Tracks the current instruction in memory.
- **Stack**: Stores return addresses during subroutine calls.
- **Timers**: Delay and sound timers for timing events.

### Graphics
- **Display**: 64x32 pixel monochrome screen represented by a 2D numpy array.
- **Draw Flag (`d_flag`)**: Indicates whether the screen needs to be redrawn.

### Input
- **Keypad**: A list representing the state of the 16-key keypad.

### Execution
- **`emulate_cycle`**: Fetches, decodes, and executes one CPU cycle.
- **`execute_opcode`**: Handles the execution of individual CHIP-8 opcodes.

### Pygame Integration
- **Display Update**: `update_display` renders the current state of the CHIP-8 display using `pygame`.
- **Event Handling**: The main loop handles keyboard events and updates the emulator state accordingly.

## Limitations

- **Sound**: Currently not implemented.
- **Performance**: May not run at full speed on all systems, depending on the performance of the Python interpreter and the complexity of the ROM.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CHIP-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) by Thomas P. Greene.
- [Pygame Documentation](https://www.pygame.org/docs/).

Enjoy exploring the world of CHIP-8 emulation!

