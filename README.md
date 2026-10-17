# VlogPilot
VlogPilot is an accessible camera mount for wheelchair users. Using a Raspberry Pi Pico 2W, it serves a simple webpage and uses web protocols to control two servos for two axes of rotation. 

Code is written in [MicroPython](https://micropython.org/).

# Physical Components
- Raspberry Pi Pico 2 W - [Datasheet](https://pip-assets.raspberrypi.com/categories/1088-raspberry-pi-pico-2-w/documents/RP-008304-DS-3-pico-2-w-datasheet.pdf)

# Installation
### Method 1: Thonny IDE
This code can be run using the [Thonny IDE](https://thonny.org/). Connect the microcontroller to a computer, select the RPI configuration in the bottom-right, and then press Run.

### Method 2 (Recommended): VSCode
First, connect the board to your computer.
Clone this project into VSCode and install the required extensions (especially MicroPico). 

You can then run the code on the board using MicroPico's functionality and view the logs in the Terminal.