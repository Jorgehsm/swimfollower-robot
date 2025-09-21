from flask import Flask, render_template, Response, request
import cv2
import queue
import threading
import time
import serial
import os

# ---------------- CONFIGURAÇÃO ----------------
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
timeout = time.time() + 10  # 10s de timeout
while not os.path.exists(video_source):
    if time.time() > timeout:
        raise RuntimeError("Não foi possível localizar a câmera.")
    time.sleep(0.2)

app = Flask(__name__)

# ---------------- VARIÁVEIS GLOBAIS ----------------
camera = cv2.VideoCapture(video_source)
if not camera.isOpened():
    raise RuntimeError("Não foi possível abrir a câmera.")

is_recording = False
recording_thread = None
video_writer = None
speed_value = 0

# Frame mais recente para streaming
latest_frame = None
frame_lock = threading.Lock()

# Fila para gravação de frames
frame_queue = queue.Queue(maxsize=50)

# ---------------- THREAD DE CAPTURA ----------------
def capture_frames():
    global latest_frame, frame_queue, camera, is_recording
    while True:
        success, frame = camera.read()
        if not success:
            time.sleep(0.01)
            continue

        # Atualiza frame mais recente para streaming
        with frame_lock:
            latest_frame = frame

        # Coloca frame na fila de gravação
        if is_recording:
            try:
                frame_queue.put_nowait(frame.copy())
            except queue.Full:
                _ = frame_queue.get_nowait()  # descarta frame antigo
                frame_queue.put_nowait(frame.copy())

        time.sleep(1.0 / recording_fps)  # limita FPS da captura

# ---------------- STREAM ----------------
def generate_frames():
    global latest_frame
    while True:
        with frame_lock:
            frame = latest_frame

        if frame is None:
            time.sleep(0.01)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1/15)  # envia ~15 fps para o navegador

# ---------------- GRAVAÇÃO ----------------
def record_video():
    global is_recording, video_writer, frame_queue, latest_frame

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    filename = f"dataset_{time.strftime('%Y%m%d-%H%M%S')}.mp4"

    # Pega dimensões do primeiro frame
    while latest_frame is None:
        time.sleep(0.01)
    with frame_lock:
        height, width, _ = latest_frame.shape

    video_writer = cv2.VideoWriter(filename, fourcc, recording_fps, (width, height))
    print("Iniciando gravação...")

    while is_recording or not frame_queue.empty():
        try:
            frame = frame_queue.get(timeout=0.1)
            video_writer.write(frame)
        except queue.Empty:
            continue

    if video_writer is not None:
        video_writer.release()
        print(f"Gravação finalizada. Arquivo salvo como '{filename}'")

# ---------------- ROTAS ----------------
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
        recording_thread = threading.Thread(target=record_video, daemon=True)
        recording_thread.start()
        return "Gravação iniciada", 200
    else:
        is_recording = False
        # NÃO bloqueia o Flask; gravação termina sozinha
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
                ser.write(bytes([speed_value]))

            return "Velocidade atualizada com sucesso", 200
        else:
            return "Valor inválido. Use entre 0 e 255.", 400
    except Exception as e:
        return f"Erro: {str(e)}", 500

# ---------------- MAIN ----------------
if __name__ == '__main__':
    # Inicia a thread de captura
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()

    app.run(host='0.0.0.0', port=5000, threaded=True)
