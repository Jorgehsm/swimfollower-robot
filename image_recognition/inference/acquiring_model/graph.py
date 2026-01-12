import csv
import matplotlib.pyplot as plt
from datetime import datetime

def read_csv_basic(filename):
    timestamp = []
    offset = []
    initial_timestamp = None
    with open(filename, mode='r', newline='', encoding='utf-8') as file: #
        reader = csv.reader(file, delimiter=',') # Default delimiter is ','
        for row in reader:
            if row[0] == 'timestamp':
                continue  # Pula o cabeçalho

            current_ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            if initial_timestamp is None:
                initial_timestamp = current_ts
            timestamp.append((current_ts - initial_timestamp).total_seconds() * 1000)
            offset.append(float(row[1]))
    return {'timestamp': timestamp, 'offset': offset}
            
# Lê o arquivo (ajuste o nome conforme o teu)
path_csv = '/home/user/swimfollower-robot/image_recognition/inference/acquiring_model/dataset_20260111-181035_200/offset_log.csv'
data = read_csv_basic(path_csv)
 
print(data)


# Plota
plt.figure(figsize=(10,5))
plt.plot(data['timestamp'], data['offset'], linewidth=1)
plt.xlabel('Tempo')
plt.ylabel('Offset (pixels)')
plt.title('Variação do Offset ao longo do tempo')
plt.grid(True)
plt.tight_layout()
plt.savefig(path_csv.replace('.csv', '_offset_plot.png'))
