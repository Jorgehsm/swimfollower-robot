from ultralytics import YOLO
import cv2
import serial
import time
import os

# ------------------ CONFIGURATION ------------------

model_path = 'yolov8n-face.pt'             # Path to your trained YOLO model
serial_port = '/dev/ttyUSB0'       # Serial port used (adjust as needed)
baud_rate = 115200                 # Baud rate for serial communication
video_source = '/dev/video1'                   # Camera index or path to video file
confidence_threshold = 0.4         # YOLO confidence threshold
discard_old_frames = 5  # How many frames to discard

# ------------------ INITIALIZATION ------------------

# Load the trained YOLOv8 model
model = YOLO(model_path)

# Waits for camera connection
print("Esperando a câmera conectar...")
while not os.path.exists(video_source):
    time.sleep(0.2)

# Opens camera with OpenCV
video_capture = cv2.VideoCapture(video_source)
if not video_capture.isOpened():
    print("Erro: não foi possível abrir a câmera.")
    exit()
else:
    print("Câmera conectada com sucesso.")

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Open serial communication with the microcontroller
try:
    serial_connection = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Serial connection opened on {serial_port} at {baud_rate} baud.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    exit()

# ------------------ INFERENCE LOOP ------------------

while True:

    for _ in range(discard_old_frames):  # Ajuste conforme necessário (2~5 geralmente já ajuda)
        video_capture.read()

    # Read video frame
    success, frame = video_capture.read()
    if not success:
        print("Warning: Failed to read frame.")
        break

    # Read speed from serial (non-blocking)
    speed_text = ""
    try:
        if serial_connection.in_waiting > 0:
            line = serial_connection.readline().decode('utf-8').strip()
            try:
                speed = float(line)
                speed_text = f"Speed: {speed:.2f} m/s"
            except ValueError:
                speed_text = "Speed: ---"
    except Exception as e:
        print(f"Serial read error: {e}")

    # Run YOLO inference
    start_time = time.time()
    results = model.predict(source=frame, conf=confidence_threshold, save=False, device="cpu")
    end_time = time.time()

    # Get image dimensions
    frame_height, frame_width = frame.shape[:2]
    image_center_x = frame_width // 2

    # Initialize variable to store the horizontal distance
    horizontal_offset = None

    # Extract detection results
    boxes = results[0].boxes

    if boxes and len(boxes) > 0:
        # Get the first detection
        box = boxes[0]

        # Get box coordinates: (x1, y1, x2, y2)
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        # Calculate centroid of the bounding box
        box_center_x = int((x1 + x2) / 2)

        # Calculate horizontal distance to image center
        horizontal_offset = float(box_center_x - image_center_x)

    # Plot annotated frame
    annotated_frame = results[0].plot()

    # Draw center lines and offset if detection exists
    if horizontal_offset is not None:
        # Draw bounding box center line (blue)
        cv2.line(annotated_frame, (int(box_center_x), 0), (int(box_center_x), frame_height), (255, 0, 0), 2)

        # Draw image center line (red)
        cv2.line(annotated_frame, (image_center_x, 0), (image_center_x, frame_height), (0, 0, 255), 1)

        # Draw offset text
        cv2.putText(
            annotated_frame,
            f"Offset X: {horizontal_offset:.2f}px",
            org=(10, 90),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.6,
            color=(0, 255, 255),
            thickness=1
        )

        # Send offset to microcontroller
        try:
            serial_connection.write(f"{horizontal_offset:.2f}\n".encode('utf-8'))
        except Exception as e:
            print(f"Serial write error: {e}")

    # Draw speed text
    if speed_text:
        cv2.putText(
            annotated_frame,
            speed_text,
            org=(10, 30),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 255, 0),
            thickness=2
        )

    # Show FPS
    fps = 1 / (end_time - start_time)
    cv2.putText(
        annotated_frame,
        f"FPS: {fps:.2f}",
        org=(10, 60),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.6,
        color=(255, 255, 255),
        thickness=1
    )

    # Display result
    cv2.imshow("YOLOv8 Inference", annotated_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.01)  # Small delay to avoid overloading serial

# ------------------ CLEANUP ------------------

video_capture.release()
serial_connection.close()
cv2.destroyAllWindows()
