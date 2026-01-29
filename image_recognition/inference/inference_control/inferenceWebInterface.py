from flask import Flask, render_template, Response, request, jsonify
import cv2
import threading
import time
import os
import serial
import csv
from ultralytics import YOLO

#use firmware control-firmware

# ------------------ CONFIG ------------------
#MODEL_PATH = 'yolov8n-face.pt'
MODEL_PATH = 'yolov8n-face_ncnn_model'
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
VIDEO_SOURCE = '/dev/video0'
RECORDING_FPS = 15.0
CONF_THRESHOLD = 0.4

csv_file = None
csv_writer = None
record_start_time = None

# ------------------ INIT ------------------
app = Flask(__name__)

# Conexão serial com o microcontrolador
ser = None
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[INFO] Conectado ao microcontrolador em {SERIAL_PORT}")
except Exception as e:
    print(f"[ERRO] Falha ao abrir porta serial: {e}")

# Espera pela câmera
print("[INFO] Aguardando câmera conectar...")
while not os.path.exists(VIDEO_SOURCE):
    time.sleep(0.2)

camera = cv2.VideoCapture(VIDEO_SOURCE)
if not camera.isOpened():
    raise RuntimeError(f"Falha ao abrir câmera {VIDEO_SOURCE}")

model = YOLO(MODEL_PATH)

# ------------------ SHARED STATE ------------------
latest_frame = None            # frame BGR em np.array (apenas 1)
frame_lock = threading.Lock()  # protege latest_frame
is_recording = False
record_writer = None
record_lock = threading.Lock() # protege writer e is_recording
latest_offset = 0.0
latest_speed = "0.0"
running = True                 # para desligar limpo se desejar

# ------------------ THREADS ------------------

def capture_thread():
    """Lê continuamente da câmera e atualiza latest_frame"""
    global latest_frame, running, camera
    while running:
        ret, frame = camera.read()
        if not ret:
            camera.release()
            time.sleep(0.5)
            camera = cv2.VideoCapture(VIDEO_SOURCE)
            time.sleep(0.5)
            continue
        with frame_lock:
            latest_frame = frame
        time.sleep(0.005)

def serial_read_thread():
    """Lê continuamente a velocidade retornada pelo microcontrolador."""
    global latest_speed, ser, running
    if ser is None:
        return
    while running:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    latest_speed = line
        except Exception:
            pass
        time.sleep(0.03)

def inference_thread():
    """Faz inferência no frame mais recente, calcula offset e envia por serial."""
    global latest_frame, latest_offset, ser, running, is_recording
    while running:
        with frame_lock:
            frame = None if latest_frame is None else latest_frame.copy()
        if frame is None:
            time.sleep(0.02)
            continue
        
        try:
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

            if ser is not None and ser.is_open:
                try:
                    value_to_send = latest_offset if is_recording else 999.0
                    ser.write(f"{value_to_send:.2f}\n".encode('utf-8'))
                except Exception:
                    pass
        except Exception as e:
            print(f"[WARN] inference error: {e}")

        time.sleep(0.1)
def recorder_thread():
    global is_recording, record_writer, latest_frame, running, csv_writer, record_start_time
    
    while running:
        loop_start = time.time()
        
        with record_lock:
            writer = record_writer
            active = is_recording

        if not active or writer is None or not writer.isOpened():
            time.sleep(0.05)
            continue

        # Captura e Gravação
        with frame_lock:
            frame_copy = latest_frame.copy() if latest_frame is not None else None

        if frame_copy is not None:
            try:
                write_start = time.time()
                writer.write(frame_copy)
                with record_lock:
                    if csv_writer is not None:
                        timestamp = time.time() - record_start_time
                        csv_writer.writerow([f"{timestamp:.6f}", f"{latest_offset:.2f}"])
                        csv_file.flush()
                write_end = time.time()

            except Exception as e:
                print(f"[WARN] erro ao escrever frame: {e}")

        # Controle de cadência (FPS)
        elapsed_in_loop = time.time() - loop_start
        sleep_time = (1.0 / RECORDING_FPS) - elapsed_in_loop
        elapsed_in_loop = (time.time() - loop_start)

        sleep_time = (1.0 / RECORDING_FPS) - elapsed_in_loop

        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            pass

# ------------------ STREAM ------------------
def generate_frames():
    """Gera stream MJPEG do frame mais recente sem bloquear."""
    global latest_frame
    print("[INFO] MJPEG streaming iniciado")
    while True:
        frame_copy = latest_frame
        if frame_copy is None:
            time.sleep(0.02)
            continue

        ret, buffer = cv2.imencode('.jpg', frame_copy, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.01) 

# ------------------ ROUTES ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    global is_recording, record_writer, csv_file, csv_writer, record_start_time

    with record_lock:
        if not is_recording:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            filename = f"record_{time.strftime('%Y%m%d-%H%M%S')}.avi"
            record_writer = cv2.VideoWriter(filename, fourcc, RECORDING_FPS, (1280, 720))

            if not record_writer.isOpened():
                print("[ERRO] Falha ao abrir VideoWriter.")
                record_writer.release()
                record_writer = None
                return jsonify({'status': 'fail', 'reason': 'Falha ao abrir VideoWriter'}), 500
            
            record_start_time = time.time()

            csv_filename = filename.replace('.avi', '.csv')
            csv_file = open(csv_filename, mode='w', newline='')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['timestamp_s', 'offset_px'])

            is_recording = True
            print(f"[INFO] Gravando em {filename}")
            return jsonify({'status': 'recording_started', 'file': filename}), 200

        else:
            print("[INFO] Parando gravação...")

            if record_writer is not None:
                try:
                    record_writer.release()
                    print("[DEBUG] VideoWriter liberado com sucesso")
                except Exception as e:
                    print(f"[WARN] Erro ao fechar VideoWriter: {e}")
                finally:
                    record_writer = None

            is_recording = False

            if csv_file is not None:
                try:
                    csv_file.flush()
                    csv_file.close()
                except Exception:
                    pass
                finally:
                    csv_file = None
                    csv_writer = None

            print("[INFO] Gravação parada")
            return jsonify({'status': 'recording_stopped'}), 200

@app.route('/status')
def status():
    """Retorna offset e velocidade para UI, se necessário."""
    return jsonify({
        'offset': latest_offset,
        'speed': latest_speed,
        'is_recording': is_recording
    })

@app.route('/set_gains', methods=['POST'])
def set_gains():
    """Recebe e envia os novos ganhos PID para o microcontrolador via Serial."""
    global ser

    try:
        data = request.get_json()
        kp = float(data.get('kp', 0.0))
        ki = float(data.get('ki', 0.0))
        kd = float(data.get('kd', 0.0))
    except Exception:
        return jsonify({'status': 'fail', 'reason': 'Dados JSON invalidos ou faltantes.'}), 400

    command = f"{kp:.4f},{ki:.4f},{kd:.4f}\n"

    if ser is not None and ser.is_open:
        try:
            ser.write(command.encode('utf-8'))
            print(f"[INFO] Ganhos enviados: {command.strip()}")
            return jsonify({
                'status': 'success', 
                'kp': kp, 
                'ki': ki, 
                'kd': kd,
                'sent_command': command.strip()
            }), 200
        except Exception as e:
            print(f"[ERRO] Falha ao enviar ganhos serialmente: {e}")
            return jsonify({'status': 'fail', 'reason': f'Falha Serial: {e}'}), 500
    else:
        return jsonify({'status': 'fail', 'reason': 'Conexao Serial nao esta ativa.'}), 503

# ------------------ START ------------------
if __name__ == '__main__':
    # threads
    threading.Thread(target=capture_thread, daemon=True).start()
    threading.Thread(target=inference_thread, daemon=True).start()
    threading.Thread(target=recorder_thread, daemon=True).start()
    threading.Thread(target=serial_read_thread, daemon=True).start()

    # liberação ao sair
    import atexit
    def cleanup():
        global running, camera, ser, record_writer
        running = False
        time.sleep(0.2)
        try:
            if camera and camera.isOpened():
                camera.release()
        except Exception:
            pass
        if ser is not None and ser.is_open:
            try:
                stop_command = "999.00\n" 
                ser.write(stop_command.encode('utf-8'))
                time.sleep(0.1)
            except Exception as e:
                print(f"[WARN] Falha ao enviar comando 999: {e}")
            
            try:
                ser.close()
            except Exception:
                pass
        with record_lock:
            if record_writer is not None:
                try:
                    record_writer.release()
                except Exception:
                    pass
    atexit.register(cleanup)

    # roda servidor
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)