from flask import Flask, render_template, Response, request
import cv2
import threading
import time
import os
import serial
import json
import datetime
from ultralytics import YOLO

#use firmware WebServerControl

# ------------------ CONFIGURAÇÕES ------------------
serial_port = '/dev/ttyUSB0'
baud_rate = 115200
video_source = '/dev/video0'
capture_interval = 0.2  # intervalo entre registros de offset
MODEL_PATH = 'yolov8n-face_ncnn_model'
CONF_THRESHOLD = 0.4

# ------------------ SERIAL ------------------
ser = None
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"[INFO] Conectado ao microcontrolador em {serial_port}")
except Exception as e:
    print(f"[ERRO] Falha ao abrir porta serial: {e}")

# ------------------ CÂMERA ------------------
print("[INFO] Aguardando câmera conectar...")
while not os.path.exists(video_source):
    time.sleep(0.2)

camera = cv2.VideoCapture(video_source)
if not camera.isOpened():
    raise RuntimeError("Falha ao abrir câmera.")

# ------------------ VARIÁVEIS GLOBAIS ------------------
app = Flask(__name__)
is_capturing = False
capture_thread = None
inference_thread_obj = None
latest_frame = None
latest_offset = 0.0
latest_inference_time = 0.0
speed_value = 0
frame_lock = threading.Lock()
running = True

# ------------------ MODELO ------------------
print("[INFO] Carregando modelo YOLO...")
model = YOLO(MODEL_PATH)
print("[INFO] Modelo carregado com sucesso.")

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ------------------ STREAM ------------------
def generate_frames():
    """Gera frames para o stream e atualiza o frame mais recente."""
    global camera, latest_frame
    while True:
        success, frame = camera.read()
        if not success:
            continue

        with frame_lock:
            latest_frame = frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ------------------ INFERÊNCIA ------------------
def inference_thread():
    """Faz inferência no frame mais recente, calcula offset e envia por serial."""
    global latest_frame, latest_offset, ser, running, is_capturing, speed_value, latest_inference_time

    while running:
        with frame_lock:
            frame = None if latest_frame is None else latest_frame.copy()

        if frame is None:
            time.sleep(0.02)
            continue

        try:
            start_time = time.time()
            results = model(frame, conf=CONF_THRESHOLD, verbose=False, device='cpu')
            

            boxes = results[0].boxes
            h, w = frame.shape[:2]
            center_x = w // 2
            offset = 0.0

            if boxes and len(boxes) > 0:
                # pega a primeira detecção
                x1, y1, x2, y2 = boxes[0].xyxy[0].tolist()
                box_center_x = int((x1 + x2) / 2)
                offset = float(box_center_x - center_x)

            latest_offset = offset

            # envia apenas quando está capturando
            if ser is not None and ser.is_open:
                try:
                    value_to_send = speed_value if is_capturing else 0
                    ser.write(f"{value_to_send}\n".encode('utf-8'))
                except Exception:
                    pass

        except Exception as e:
            print(f"[WARN] Erro na inferência: {e}")

        time.sleep(0.01)
        end_time = time.time()
        latest_inference_time = (end_time - start_time) * 1000

# ------------------ CAPTURA ------------------
def capture_data():
    """Salva apenas timestamp e offset enquanto a gravação está ativa."""
    global is_capturing, latest_offset, latest_inference_time, speed_value

    folder_name = f"dataset_{time.strftime('%Y%m%d-%H%M%S')}_{speed_value}"
    os.makedirs(folder_name, exist_ok=True)
    csv_path = os.path.join(folder_name, "offset_log.csv")

    with open(csv_path, 'w') as f:
            f.write("timestamp,offset,inference_time_ms\n")

            while is_capturing:
                now = time.time()
                milliseconds = int((now - int(now)) * 1000)
                timestamp_ms = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)) + f".{milliseconds:03d}"

                f.write(f"{timestamp_ms},{latest_offset:.2f},{latest_inference_time:.2f}\n")
                f.flush()

                print(f"[INFO] {timestamp_ms} | offset={latest_offset:.2f} | inf={latest_inference_time:.2f}ms")
                time.sleep(capture_interval)

    print("[INFO] Captura de dados finalizada.")

# ------------------ ROTAS ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_capture', methods=['POST'])
def toggle_capture():
    global is_capturing, capture_thread, ser
    if not is_capturing:
        is_capturing = True
        capture_thread = threading.Thread(target=capture_data)
        capture_thread.start()
        return "Captura iniciada", 200
    else:
        is_capturing = False
        if capture_thread is not None:
            capture_thread.join()

        # envia 0 quando a gravação parar
        if ser is not None and ser.is_open:
            try:
                ser.write(b"0\n")
            except Exception:
                pass

        return "Captura parada", 200

@app.route('/set_speed', methods=['POST'])
def set_speed():
    global speed_value
    try:
        data = request.get_json()
        new_speed = data.get('speed')
        if new_speed is not None and 0 <= new_speed <= 255:
            speed_value = int(new_speed)
            print(f"[INFO] Velocidade definida: {speed_value}")
            return "Velocidade atualizada com sucesso", 200
        else:
            return "Valor inválido. Use entre 0 e 255.", 400
    except Exception as e:
        return f"Erro: {str(e)}", 500

# ------------------ MAIN ------------------
if __name__ == '__main__':
    inference_thread_obj = threading.Thread(target=inference_thread, daemon=True)
    inference_thread_obj.start()

    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        running = False
        if inference_thread_obj.is_alive():
            inference_thread_obj.join()
        if camera.isOpened():
            camera.release()
        if ser is not None and ser.is_open:
            ser.close()