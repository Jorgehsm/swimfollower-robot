import csv
import matplotlib.pyplot as plt

file_path = r'C:\Users\jhdac\Git\swimfollower-robot\image_recognition\inference\inference_control\results\record_20260115-174026.csv'

def plot_filtered_data(path):
    timestamps = []
    offsets = []

    try:
        with open(path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                timestamps.append(float(row['timestamp_s']))
                offsets.append(float(row['offset_px']))
        
        first_idx = 0
        for i, val in enumerate(offsets):
            if val != 0:
                first_idx = i - 1
                break
        
        last_idx = len(offsets) - 1
        for i in range(len(offsets) - 1, -1, -1):
            if offsets[i] != 0:
                last_idx = i + 1
                break

        filtered_timestamps = timestamps[first_idx : last_idx + 1]
        filtered_offsets = offsets[first_idx : last_idx + 1]

        
        start_time_ref = filtered_timestamps[0]
        
        # Subtract start_time_ref from every element to make the first one 0.0
        normalized_time = [(t - start_time_ref) for t in filtered_timestamps]
        offset_meters = [offset/183 for offset in filtered_offsets]

        # --- Plotting ---
        plt.figure(figsize=(12, 6))
        plt.plot(normalized_time, offset_meters, 
                 color='green', label='Erro')
        
        plt.axvline(x=4.5, color='green', linestyle='--', linewidth=2, label='Início do movimento para esquerda')
        plt.axvline(x=13, color='red', linestyle='--', linewidth=2, label='Primeira virada')
        plt.axvline(x=24, color='red', linestyle='--', linewidth=2, label='Segunda virada')
        plt.axvline(x=32, color='red', linestyle='--', linewidth=2, label='Parada')
        
        #Zero
        plt.axhline(0, color='red', linestyle='--', alpha=0.5)
        
        plt.title('Erro ao decorrer do tempo - Teste do controlador', fontsize=14)
        plt.xlabel('Tempo (s)', fontsize=12)
        plt.ylabel('Offset (metros)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    plot_filtered_data(file_path)