from ultralytics import YOLO
import cv2
import serial
import time
import threading
import queue
import os

# ------------------ CONFIGURATION ------------------
model_path = 'yolov8n-face.pt'
serial_port = '/dev/ttyUSB0'
baud_rate = 115200
video_source = '/dev/video1'
confidence_threshold = 0.4
output_video_path = "output.mp4"
recording_fps = 30.0

stop_flag = threading.Event()

# Waits for camera connection
print("Waiting for camera to connect...")
while not os.path.exists(video_source):
    time.sleep(0.2)

# Buffers de frames
latest_frame_lock = threading.Lock()
latest_frame = None
recording_queue = queue.Queue(maxsize=50)  # buffer para frames anotados para gravação

# ------------------ INITIALIZATION ------------------
model = YOLO(model_path)

# Serial connection
try:
    serial_connection = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Serial connection opened on {serial_port} at {baud_rate} baud.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    exit()

# ------------------ THREADS ------------------

def capture_thread():
    global latest_frame
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: cannot open camera.")
        stop_flag.set()
        return

    print("Camera connected.")
    while not stop_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            continue
        with latest_frame_lock:
            latest_frame = frame.copy()
    cap.release()

def inference_thread():
    global latest_frame
    width, height = 640, 480  # ajusta se necessário

    # Inicializa o VideoWriter para gravação
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, recording_fps, (width, height))
    if not out.isOpened():
        print("Error: Could not create video writer.")
        stop_flag.set()
        return

    while not stop_flag.is_set():
        frame = None
        with latest_frame_lock:
            if latest_frame is not None:
                frame = latest_frame.copy()
        if frame is None:
            time.sleep(0.001)
            continue

        # ---- Read speed from serial ----
        speed_text = "Speed: ---"
        try:
            if serial_connection.in_waiting > 0:
                line = serial_connection.readline().decode('utf-8').strip()
                try:
                    speed = float(line)
                    speed_text = f"Speed: {speed:.2f} m/s"
                except ValueError:
                    pass
        except Exception as e:
            print(f"Serial read error: {e}")

        # ---- YOLO inference ----
        start_time = time.time()
        results = model.predict(source=frame, conf=confidence_threshold, save=False, device="cpu")
        end_time = time.time()
        fps = 1 / (end_time - start_time)

        frame_height, frame_width = frame.shape[:2]
        image_center_x = frame_width // 2
        horizontal_offset = None

        boxes = results[0].boxes
        if boxes and len(boxes) > 0:
            box = boxes[0]
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_center_x = int((x1 + x2) / 2)
            horizontal_offset = float(box_center_x - image_center_x)

            # Draw bounding box and offset
            cv2.line(frame, (box_center_x, 0), (box_center_x, frame_height), (255, 0, 0), 2)
            cv2.line(frame, (image_center_x, 0), (image_center_x, frame_height), (0, 0, 255), 1)
            cv2.putText(frame, f"Offset X: {horizontal_offset:.2f}px", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

            # Envia offset para microcontrolador
            try:
                serial_connection.write(f"{horizontal_offset:.2f}\n".encode('utf-8'))
            except Exception as e:
                print(f"Serial write error: {e}")

        # Desenha velocidade e FPS
        cv2.putText(frame, speed_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Coloca frame anotado na fila de gravação
        if not recording_queue.full():
            recording_queue.put(frame.copy())

        # Mostra feed em tempo real
        cv2.imshow("YOLO Inference", frame)
        cv2.waitKey(1)

    # Gravação final
    while not recording_queue.empty():
        out.write(recording_queue.get())
    out.release()

def recording_thread():
    """Grava frames anotados da fila no arquivo de vídeo no FPS da câmera"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 640, 480
    out = cv2.VideoWriter(output_video_path, fourcc, recording_fps, (width, height))
    while not stop_flag.is_set() or not recording_queue.empty():
        try:
            frame = recording_queue.get(timeout=0.1)
            out.write(frame)
        except queue.Empty:
            continue
    out.release()


# ------------------ START THREADS ------------------
t_capture = threading.Thread(target=capture_thread)
t_infer = threading.Thread(target=inference_thread)
t_record = threading.Thread(target=recording_thread)

t_capture.start()
t_infer.start()
t_record.start()

# ------------------ MAIN LOOP ------------------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Termination requested.")
finally:
    stop_flag.set()
    t_capture.join()
    t_infer.join()
    t_record.join()
    serial_connection.close()
    cv2.destroyAllWindows()
    print("Program terminated gracefully.")
