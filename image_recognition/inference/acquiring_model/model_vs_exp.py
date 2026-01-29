import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

## --- Lista de CSVs 255 ---
#csv_paths = [
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-174435_255\offset_log.csv",
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180335_255\offset_log.csv"
#]

## --- Lista de CSVs 220 ---
csv_paths = [
    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180541_220\offset_log.csv",
    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180719_220\offset_log.csv",
    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180749_220\offset_log.csv", 
]

## --- Lista de CSVs 200 ---
#csv_paths = [
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180916_200\offset_log.csv",
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-181000_200\offset_log.csv",
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-181035_200\offset_log.csv", 
#]

# --- Model Parameters ---
K = 1.011
duty = 220
delay = 1.25  # Inference delay in seconds

# Plotting setup: Single figure
plt.figure(figsize=(10, 6))

all_initial_offsets = []
max_time = 0
experimental_data = []

# 1. Read and store experimental data
for idx, csv_path in enumerate(csv_paths):
    timestamps = []
    offsets = []

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamps.append(
                datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
            )
            offsets.append(float(row['offset']))

    timestamps = np.array(timestamps)
    offsets = np.array(offsets)

    # Relative time calculation
    t0 = timestamps[0]
    t_exp = np.array([(ts - t0).total_seconds() for ts in timestamps])
    
    # Store data for plotting and calculation
    all_initial_offsets.append(offsets[0])
    experimental_data.append((t_exp, offsets))
    
    # Track max time for the model curve
    if t_exp.max() > max_time:
        max_time = t_exp.max()

# 2. Plot experimental trials
colors = ['blue', 'green', 'red']
for idx, (t_exp, offsets) in enumerate(experimental_data):
    plt.plot(t_exp, offsets, 'o', alpha=0.5, markersize=4, 
             color=colors[idx % len(colors)], label=f'Ensaio {idx+1}')

# 3. Calculate Model Responses
avg_offset_0 = np.mean(all_initial_offsets)
t_model = np.linspace(0, max_time, 200)

# delay
y_model_delay = np.full_like(t_model, avg_offset_0)
mask = t_model >= delay
y_model_delay[mask] = avg_offset_0 + K * duty * (t_model[mask] - delay)

# no delay
y_model_no_delay = avg_offset_0 + K * duty * t_model

# 4. Plot Model Curves
#plt.plot(t_model, y_model_delay, 'k--', linestyle='--', linewidth=2, label=f'Modelo com atraso ({delay}s)')
plt.plot(t_model, y_model_no_delay, 'k-', linestyle='--', linewidth=2, label='Modelo [G(s)]]')

plt.title(f'Comparativo entre modelo e exeprimental para degrau de {duty}')
plt.xlabel('Tempo (s)')
plt.ylabel('Offset (px)')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()

plt.show()