import pandas as pd
import matplotlib.pyplot as plt

# Lê o arquivo (ajuste o nome conforme o teu)
df = pd.read_csv('offset_log.csv', names=['timestamp', 'offset'], header=0)

# Converte timestamps para tipo datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Garante que o offset é numérico
df['offset'] = pd.to_numeric(df['offset'], errors='coerce')

# Plota
plt.figure(figsize=(10,5))
plt.plot(df['timestamp'], df['offset'], linewidth=1)
plt.xlabel('Tempo')
plt.ylabel('Offset (pixels)')
plt.title('Variação do Offset ao longo do tempo')
plt.grid(True)
plt.tight_layout()
plt.show()
