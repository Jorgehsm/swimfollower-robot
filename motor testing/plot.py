import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import os

dir_script = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(dir_script, "results.txt")
with open(path, "r") as results_file:
    results = results_file.readlines() 

print(results)

#plt.figure()
#plt.plot(duties, rpms, 'b.-')
#plt.title('Velocidade do motor em função do Duty Cycle')
#plt.xlabel('Duty Cycle')
#plt.ylabel('Velocidade (RPM)')
#plt.grid(True)
#plt.tight_layout()
#
#image_name = "speedPerDuty.png"
#image_path = os.path.join(dir_script, image_name)
#plt.savefig(image_path, dpi=300)