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
#csv_paths = [
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180541_220\offset_log.csv",
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180719_220\offset_log.csv",
#    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180749_220\offset_log.csv", 
#]

# --- Lista de CSVs 200 ---
csv_paths = [
    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180916_200\offset_log.csv",
    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-181000_200\offset_log.csv",
    r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-181035_200\offset_log.csv", 
]

# --- Modelo ---
K = 1.011
duty = 200
delay = 0.5  # atraso de inferência em segundos

n = len(csv_paths)
fig, axes = plt.subplots(1, n, figsize=(4*n, 4), sharex=False)

# Garante que axes seja iterável quando n = 1
if n == 1:
    axes = [axes]

for idx, csv_path in enumerate(csv_paths):
    timestamps = []
    offsets = []

    # --- Leitura do CSV ---
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            timestamps.append(
                datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
            )
            offsets.append(float(row['offset']))

    timestamps = np.array(timestamps)
    offsets = np.array(offsets)

    # --- Tempo relativo ---
    t0 = timestamps[0]
    t_exp = np.array([(ts - t0).total_seconds() for ts in timestamps])

    # --- Condição inicial ---
    offset_0 = offsets[0]

    # --- Resposta do modelo ---
    #y_model = offset_0 + K * duty * t_exp

    y_model = np.full_like(t_exp, offset_0)

    mask = t_exp >= delay
    y_model[mask] = offset_0 + K * duty * (t_exp[mask] - delay)

    ax = axes[idx]
    ax.plot(t_exp, offsets, 'o-', label='Experimental')
    ax.plot(t_exp, y_model, '-', linewidth=2, label='Modelo')
    ax.grid(True)
    ax.set_title(f'Ensaio {idx+1}')
    ax.set_xlabel('Tempo (s)')
    ax.set_ylabel('Offset')
    ax.legend()

plt.tight_layout()
plt.show()