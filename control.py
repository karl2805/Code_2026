from typing import dataclass_transform

import serial
import numpy as np
import csv
import time
import re

ser = serial.Serial("/dev/ttyACM0", 115200, timeout = 4, write_timeout = 0.5, stopbits=serial.STOPBITS_ONE)

ser.reset_input_buffer()

command = "Read3:10\r\n"
print(f"Sending command: {command}")
ser.write(str.encode(command))


while True:
    data_recieved = ser.read_until(size=command.__sizeof__())
    data_recieved = ser.read_until(b'\n', size=None)

    # data_recieved = ser.read_until(b'\n').decode().strip()

    #print(f"Recieved {str(data_recieved.decode().strip())}")

    if data_recieved.decode().startswith("Output"):
        vals_str = re.findall(r'[-+]?\d+[\.]?\d*', str(data_recieved) )
        vals = [float(x) for x in vals_str]  # Convert strings to actual numbers
        print(vals)



        

# list_recieved = [float(x) for x in line.decode().strip().split(",")]

# numpy_array = np.array(list_recieved)

# print(f"Converted Numpy Array {numpy_array}")


# def ReadMultipleVoltage(channel, num_reads):
#     command = f"ReadMultipleVoltage_{channel}_{num_reads}"
#     print(f"Sending command: {command}")
#     ser.write(command.encode("utf-8"))

#     time.sleep(0.5)

#     line = ser.readline()
#     print(line.decode().strip())
#     # list_recieved = [float(x) for x in line.decode().strip().split(",")]
#     # np_array = np.column_stack([np.arange(len(list_recieved)), list_recieved])
#     # return np

# ReadMultipleVoltage('A0', 10)

# # header = ['index', 'voltage']

# # with open('voltages.csv', mode='w', newline="", encoding="utf-8") as file:
# #     writer = csv.writer(file)
# #     writer.writerow(header)
# #     writer.writerows(voltages)
