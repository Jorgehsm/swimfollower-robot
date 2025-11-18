import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import os

PORT = '/dev/ttyUSB0'  # '/dev/ttyUSB0' ou 'COM'
BAUDRATE = 115200  # Baudrate for serial communication

TIMEOUT = 20 #seconds

ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2) #Waits connection to be established

data = []
print("Waiting data...")

last_data = time.time()
first_data_received = False

while True:
    raw = ser.readline()
    if raw != b'':
        print("First data detected. Starting read...")
        time.sleep(3)
        last_data = time.time()
        break

print("Reading...")

try:
    while True:
        line = ser.readline().decode().strip()
        print(line)
        if line:
            try:
                duty, rpm = map(float, line.split(','))
                data.append((int(duty), rpm))
                last_data = time.time()  # reset silence timer
            except ValueError:
                continue  # ignore invalid lines
        else:
            # if too much time has passed without receiving anything, end
            if time.time() - last_data > TIMEOUT:
                print("Timeout without data reached. Ending read.")
                break
finally:
    ser.close()

print("Reading ended.")

dir_script = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(dir_script, "results.txt")
with open(path, "w") as results_file:
    for duty, rpm in data:
        results_file.write(f"{duty},{rpm}\n")

duties, rpms = zip(*data)
plt.figure()
plt.plot(duties, rpms, 'b.-')
plt.title('Velocidade do motor em função do Duty Cycle')
plt.xlabel('Duty Cycle')
plt.ylabel('Velocidade (RPM)')
plt.grid(True)
plt.tight_layout()

image_name = "speedPerDuty.png"
image_path = os.path.join(dir_script, image_name)
plt.savefig(image_path, dpi=300)