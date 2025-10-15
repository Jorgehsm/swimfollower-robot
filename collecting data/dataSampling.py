from flask import Flask, render_template, Response, request
import cv2
import threading
import time
import os
import serial
import json

serial_port = '/dev/ttyUSB0'
baud_rate = 115200
video_source = '/dev/video0'
capture_interval = 0.2  # 10 imagens por segundo

# Conexão serial com o microcontrolador
ser = None
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"[INFO] Conectado ao microcontrolador em {serial_port}")
except Exception as e:
    print(f"[ERRO] Falha ao abrir porta serial: {e}")

# Espera pela câmera
print("[INFO] Aguardando câmera conectar...")
while not os.path.exists(video_source):
    time.sleep(0.2)

app = Flask(__name__)

camera = cv2.VideoCapture(video_source)
is_capturing = False
capture_thread = None
speed_value = 0

# ------------------ STREAM ------------------
def generate_frames():
    global camera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ------------------ CAPTURA DE IMAGENS ------------------
def capture_images():
    global camera, is_capturing

    folder_name = f"dataset_{time.strftime('%Y%m%d-%H%M%S')}"
    os.makedirs(folder_name, exist_ok=True)
    print(f"[INFO] Salvando imagens em: {folder_name}")

    frame_count = 0

    while is_capturing:
        success, frame = camera.read()
        if success:
            filename = os.path.join(folder_name, f"frame_{frame_count:05d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"[INFO] Imagem salva: {filename}")
            frame_count += 1
        time.sleep(capture_interval)

    print(f"[INFO] Captura finalizada. Total de imagens: {frame_count}")

# ------------------ ROUTES ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_capture', methods=['POST'])
def toggle_capture():
    global is_capturing, capture_thread
    if not is_capturing:
        is_capturing = True
        capture_thread = threading.Thread(target=capture_images)
        capture_thread.start()
        return "Captura iniciada", 200
    else:
        is_capturing = False
        if capture_thread is not None:
            capture_thread.join()
        return "Captura parada", 200

@app.route('/set_speed', methods=['POST'])
def set_speed():
    global speed_value, ser
    try:
        data = request.get_json()
        new_speed = data.get('speed')
        if new_speed is not None and 0 <= new_speed <= 255:
            speed_value = int(new_speed)
            print(f"[INFO] Velocidade do motor definida para: {speed_value}")

            if ser is not None and ser.is_open:
                ser.write(f"{speed_value}\n".encode())

            return "Velocidade atualizada com sucesso", 200
        else:
            return "Valor inválido. Use entre 0 e 255.", 400
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
