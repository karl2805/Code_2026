import time, gc, os
import neopixel
import board, digitalio
import pwmio
import supervisor
from analogio import AnalogIn
from analogio import AnalogOut
import usb_cdc

data_stream = usb_cdc.data

pwm5 = pwmio.PWMOut(board.D20, duty_cycle=2 ** 15)

# Define names for In and Out pins
Vout0 = AnalogOut(board.A0)
Vout1 = AnalogOut(board.A1)
Vin2 = AnalogIn(board.A2)
Vin3 = AnalogIn(board.A4)
Vin4 = AnalogIn(board.A5)
Vin5 = AnalogIn(board.A8)
Vin6 = AnalogIn(board.A9)
NRdChLim = 5 # Upper limit for no of channels that can read, previously NRdChLim = 4


B2U_Cal = 14/3

# Define the constants
# For notes on the following see
# https://learn.adafruit.com/circuitpython-basics-analog-inputs-and-outputs/analog-to-digital-converter-inputs
# ADC values in circuit python are all put in the range of 16-bit unsigned values so 0 - 65535 (-1+2**16)
Vmax = Vin2.reference_voltage # max AO/AI value
bit_scale = (-1+(2**16) )#(-1+(64*1024)) # 64 bits

# Functions to convert from 12-bit to Volt.
def dac_value(volts):
    return int(volts / 3.3 * 65535)
    #return int((volts / Vmax)*bit_scale)

# def get_voltage(pin):
#     return (pin.value * 3.3) / 65535
#     #return ((pin.value*Vmax)/bit_scale)

def get_voltage(value):
    return (value * 3.3) / 65535

def get_PWM(percentage):
    return (int(percentage/100.0*0xffff+0.5))

# Create a NeoPixel instance
# Brightness of 0.3 is ample for the 1515 sized LED
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=True, pixel_order=neopixel.RGB)

# Say hello
print("\nHello from TinyS2!")
print("------------------\n")

# Show available memory
print("Memory Info - gc.mem_free()")
print("---------------------------")
print("{} Bytes\n".format(gc.mem_free()))

flash = os.statvfs('/')
flash_size = flash[0] * flash[2]
flash_free = flash[0] * flash[3]
# Show flash size
print("Flash - os.statvfs('/')")
print("---------------------------")
print("Size: {} Bytes\nFree: {} Bytes\n".format(flash_size, flash_free))

print("Pixel Time!\n")

while True:
    if data_stream.in_waiting > 0:   # Listens for a serial command
        command = data_stream.readline().decode().strip()
        if command.startswith("*IDN"):
            print('ISBY-UCC-RevA.1')
        elif command.startswith("Mode"):
            TheMode = int(command[4:])
            print(TheMode)
        elif command.startswith("Write"):
            try:
                Tokens = command[5:].split(":")
                Chan = int(Tokens[0])
                SetVoltage = float(Tokens[1])
                if SetVoltage >= 0 and SetVoltage < 3.31:
                    # Sets limits on the Output voltage to board specs
                    if Chan == 0:
                        Vout0.value = dac_value(SetVoltage)  # Set the voltage
                    elif Chan == 1:
                        Vout1.value = dac_value(SetVoltage)  # Set the voltage
                    else:
                        print('Channel out of range: 0 - 1')
                else:
                    print('Vset out of range: 0 - 3.3V')
            except ValueError as ex:
                print('Vset must be a float')
                print(ex)
            except:
                print('Unknown problem')
            else:
                print("Vset", Chan, "=", str(SetVoltage), end=' ')
                print()
        elif command.startswith("Read"):
            try:
                Tokens = command[4:].split(":")
                Chan = int(Tokens[0])
                N = int(Tokens[1])
                if Chan == 0:
                    Pin = Vin2
                elif Chan == 1:
                    Pin = Vin3
                elif Chan == 2:
                    Pin = Vin4
                elif Chan == 3:
                    Pin = Vin5
                elif Chan == 4:
                    Pin = Vin6
                else:
                    print('Channel out of range: 0 - 4')
                if N < 1:
                    print('Must read at least one value')
            except ValueError as ex:
                print('Channel must be an integer')
                print(ex)
            except:
                print('Unknown problem')
            else:
                if Chan in range(0, NRdChLim) and N > 0:
                    Ref = 0.0
                    Mult = 1
                    TheMode = 1
                    if TheMode == 1:
                        for i in range(100):
                            Ref += get_voltage(Vin6.value)
                        Ref /= 100
                        Mult = B2U_Cal
                    Values = [0] * N

                    for i in range(N):
                        Values[i] = Pin.value

                    data_string = f"Output {Chan} = {str((get_voltage(Values[0])-Ref)*Mult)}"
                    data_stream.write(data_string.encode('utf-8'))

                    for i in range(1, N):
                        data_string = f", {str((get_voltage(Values[i])-Ref)*Mult)}"
                        data_stream.write(data_string.encode('utf-8'))
                    data_stream.write(b"\r\n")
