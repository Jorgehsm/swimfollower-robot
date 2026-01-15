import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

paths = [
    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-174435_255\offset_log.csv", "100%"),
    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180335_255\offset_log.csv", "100%"),
]

#paths = [
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180541_220\offset_log.csv", "86%"),
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180719_220\offset_log.csv", "86%"),
#    (r"C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\acquiring_model\treated_data\dataset_20260111-180749_220\offset_log.csv", "86%"),
#]

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


# ===== Loop sobre todos os CSVs =====
for path_csv, duty in paths:

    t, y = read_csv_basic(path_csv)

    # Ajuste linear
    a, b = np.polyfit(t, y, 1)
    y_fit = a * t + b

    # R²
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean) ** 2)
    ss_res = np.sum((y - y_fit) ** 2)
    r2 = 1 - ss_res / ss_tot

    eq_text = (
        f"y = {a:.4f} t + {b:.2f}\n"
        f"$R^2$ = {r2:.4f}"
    )

    # Plot
    plt.figure(figsize=(10, 5))
    plt.scatter(t, y, s=20, label='Dados experimentais')
    plt.plot(t, y_fit, 'r-', linewidth=2, label='Ajuste linear')

    plt.xlabel('Tempo (s)')
    plt.ylabel('Offset (pixels)')
    plt.title(f'Resposta ao degrau – Duty Cycle = {duty}')
    plt.grid(True)
    plt.legend()

    plt.text(
        0.05, 0.95, eq_text,
        transform=plt.gca().transAxes,
        fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )

    plt.tight_layout()

    # Salva no mesmo diretório do CSV
    output_path = path_csv.replace('.csv', '_offset_linear_fit.png')
    plt.savefig(output_path)
    plt.close()

    print(f"Imagem salva em: {output_path}")
