# ---------------- CONFIG ----------------
video_source = 0
serial_port = "/dev/ttyUSB0"
baud_rate = 115200
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# ---------------- THREADS ----------------
def capture_thread(cap, frame_queue, stop_event):
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            continue
        frame_queue.put(frame)

def writer_thread(frame_queue, writer, stop_event):
    while not stop_event.is_set() or not frame_queue.empty():
        try:
            frame = frame_queue.get(timeout=0.1)
            writer.write(frame)
        except queue.Empty:
            continue

# ---------------- MAIN ----------------
def main():
    # Serial
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"[INFO] Conectado ao microcontrolador em {serial_port}")
    except Exception as e:
        print(f"[ERRO] Falha ao abrir porta serial: {e}")
        ser = None

    # Camera
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("[ERRO] Não foi possível abrir a câmera")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Resolução da câmera: {width}x{height} @ {fps:.1f} fps")

    # Arquivo de saída
    filename = f"dataset_{time.strftime('%Y%m%d-%H%M%S')}.mp4"
    writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    # Controle
    frame_queue = queue.Queue(maxsize=100)
    stop_event = threading.Event()

    # Threads
    t_capture = threading.Thread(target=capture_thread, args=(cap, frame_queue, stop_event))
    t_writer = threading.Thread(target=writer_thread, args=(frame_queue, writer, stop_event))
    t_capture.start()
    t_writer.start()

    print("[INFO] Gravando... pressione CTRL+C para parar.")
    try:
        while True:
            time.sleep(1)  # mantém vivo, sem travar
    except KeyboardInterrupt:
        print("\n[INFO] Encerrando gravação...")

    # Finaliza
    stop_event.set()
    t_capture.join()
    t_writer.join()
    cap.release()
    writer.release()
    if ser:
        ser.close()
    print(f"[INFO] Gravação finalizada. Arquivo salvo como '{filename}'")

if __name__ == "__main__":
    main()