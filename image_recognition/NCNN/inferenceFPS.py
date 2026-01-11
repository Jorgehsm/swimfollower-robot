from ultralytics import YOLO
import cv2
import time
import os

# ------------------ CONFIGURATION ------------------

# Path to the exported NCNN folder
model_path = 'yolov8n-face_ncnn_model' 
video_source = '/dev/video0'
confidence_threshold = 0.4
# Using 320 for faster inference on Raspberry Pi
inference_size = 320 

# ------------------ INITIALIZATION ------------------

# Load the NCNN model
# The library automatically recognizes the folder as an NCNN model
model = YOLO(model_path)

print("Waiting for camera to connect...")
while not os.path.exists(video_source):
    time.sleep(0.2)

video_capture = cv2.VideoCapture(video_source)
if not video_capture.isOpened():
    print("Error: Could not open camera.")
    exit()
else:
    print("Camera connected successfully.")

# Set resolution
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ------------------ INFERENCE LOOP ------------------

print(f"\nStarting inference with {model_path}...")
print("Press 'q' to quit.\n")

while True:
    success, frame = video_capture.read()
    if not success:
        break

    # Record start time for inference only
    inference_start = time.time()
    
    # Run YOLO inference using NCNN
    # imgsz=320 and half=True are keys for RPi performance
    results = model.predict(
        source=frame, 
        imgsz=inference_size, 
        conf=confidence_threshold, 
        verbose=True, # Keeps console clean
        device="cpu"   # NCNN runs on CPU/ARM
    )
    
    inference_end = time.time()
    
    # Calculate and print inference time
    #duration_ms = (inference_end - inference_start) * 1000
    #fps = 1 / (inference_end - inference_start)
    #print(f"Inference Time: {duration_ms:.2f}ms | Est. FPS: {fps:.1f}")

    # Plot results on frame
    #annotated_frame = results[0].plot()

    # Display result
    #cv2.imshow("YOLOv8 NCNN - Raspberry Pi", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ------------------ CLEANUP ------------------
video_capture.release()
cv2.destroyAllWindows()