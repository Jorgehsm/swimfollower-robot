import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Define the file paths and their respective labels
#paths = [
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-174435_255\offset_log.csv", "100%"),
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180335_255\offset_log.csv", "100%"),
#]

paths = [
    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180541_220\offset_log.csv", "86%"),
    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180719_220\offset_log.csv", "86%"),
    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180749_220\offset_log.csv", "86%"),
]

#paths = [
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180916_200\offset_log.csv", "78%"),
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-181000_200\offset_log.csv", "78%"),
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-181035_200\offset_log.csv", "78%"),
#]

def read_csv_basic(filename):
    timestamp = []
    offset = []
    initial_timestamp = None

    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if row[0] == 'timestamp':
                continue

            current_ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            if initial_timestamp is None:
                initial_timestamp = current_ts

            t = (current_ts - initial_timestamp).total_seconds()
            timestamp.append(t)
            offset.append(float(row[1]))

    return np.array(timestamp), np.array(offset)

# Plot configuration
plt.figure(figsize=(10, 6))
colors = ['blue', 'green', 'red']
slopes = []
intercepts = []
max_time = 0

# 1. Process data and plot individual scatter points
for i, (path_csv, duty) in enumerate(paths, start=1):
    t, y = read_csv_basic(path_csv)
    color = colors[(i-1) % len(colors)]
    
    # Store the maximum time to define the length of the average line later
    if t.max() > max_time:
        max_time = t.max()

    # Linear fit for the current trial
    a, b = np.polyfit(t, y, 1)
    slopes.append(a)
    intercepts.append(b)

    # Plot scatter points for each trial
    plt.scatter(t, y, s=20, color=color, alpha=0.4, label=f'Ensaio {i} ({duty})')

# 2. Calculate the average linearization
avg_slope = np.mean(slopes)
avg_intercept = np.mean(intercepts)

# Create a time array for the average line
t_avg = np.linspace(0, max_time, 100)
y_avg = avg_slope * t_avg + avg_intercept

# 3. Plot the single average trend line
plt.plot(t_avg, y_avg, color='black', linestyle='--', linewidth=2, 
         label=f'Linearização média: $y = {avg_slope:.2f}t + {avg_intercept:.2f}$')

# Aesthetic configurations
plt.title(f'Resposta ao degrau – - Duty Cycle {paths[0][1]} (Linearização média)')
plt.xlabel('Tempo (s)')
plt.ylabel('Offset (pixels)')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

plt.show()