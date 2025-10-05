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
recording_fps = 30.0

# Conexão serial com o microcontrolador
ser = None
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Conectado ao microcontrolador em {serial_port}")
except Exception as e:
    print(f"Erro ao abrir porta serial: {e}")

# Espera pela câmera
print("Aguardando câmera conectar...")
while not os.path.exists(video_source):
    time.sleep(0.2)

app = Flask(__name__)

camera = cv2.VideoCapture(video_source)
is_recording = False
recording_thread = None
video_writer = None
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

# ------------------ RECORDING ------------------
def record_video():
    global camera, is_recording, video_writer

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    filename = f"dataset_{time.strftime('%Y%m%d-%H%M%S')}.mp4"
    width  = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_writer = cv2.VideoWriter(filename, fourcc, recording_fps, (width, height))

    while is_recording:
        success, frame = camera.read()
        if success:
            video_writer.write(frame)
        time.sleep(1.0 / recording_fps)

    if video_writer is not None:
        video_writer.release()
        print(f"Gravação finalizada. Arquivo salvo como '{filename}'")

# ------------------ ROUTES ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    global is_recording, recording_thread
    if not is_recording:
        is_recording = True
        recording_thread = threading.Thread(target=record_video)
        recording_thread.start()
        return "Gravação iniciada", 200
    else:
        is_recording = False
        if recording_thread is not None:
            recording_thread.join()
        return "Gravação parada", 200

@app.route('/set_speed', methods=['POST'])
def set_speed():
    global speed_value, ser
    try:
        data = request.get_json()
        new_speed = data.get('speed')
        if new_speed is not None and 0 <= new_speed <= 255:
            speed_value = int(new_speed)
            print(f"Velocidade do motor definida para: {speed_value}")

            if ser is not None and ser.is_open:
                ser.write(f"{speed_value}\n".encode())

            return "Velocidade atualizada com sucesso", 200
        else:
            return "Valor inválido. Use entre 0 e 255.", 400
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
