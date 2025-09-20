import cv2
import asyncio
import os
import time
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from aiohttp import web
import json
import numpy as np
from ultralytics import YOLO
import serial

# ------------------ CONFIGURATION ------------------

model_path = 'yolov8n-face.pt'             # Path to your trained YOLO model
serial_port = '/dev/ttyUSB0'       # Serial port used (adjust as needed)
baud_rate = 115200                 # Baud rate for serial communication
video_source = '/dev/video1'                   # Camera index or path to video file
confidence_threshold = 0.4         # YOLO confidence threshold

# ------------------ INITIALIZATION ------------------

# Load the trained YOLOv8 model
model = YOLO(model_path)

# Open serial communication with the microcontroller
try:
    serial_connection = serial.Serial(serial_port, baud_rate, timeout=0.01)
    print(f"Serial connection opened on {serial_port} at {baud_rate} baud.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}. Running without serial.")
    serial_connection = None

# Waits for camera connection
print("Waiting for camera connection...")
while not os.path.exists(video_source):
    time.sleep(0.1)

# Opens camera with OpenCV
cap = cv2.VideoCapture(video_source)
if not cap.isOpened():
    raise RuntimeError("Could not open camera")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Use MediaRelay to manage the video source
relay = MediaRelay()

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.serial_connection = serial_connection
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.start_time = time.time()
        self.frame_count = 0

    async def recv(self):
        # Await the next frame from the stream
        frame = await self.track.recv()
        
        # Read image from frame
        img = frame.to_ndarray(format="bgr24")
        
        # --- YOLO INFERENCE AND ANNOTATION ---
        
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            fps = self.frame_count / elapsed_time
            self.start_time = time.time()
            self.frame_count = 0
        else:
            fps = 0 # Avoid division by zero initially

        # Run YOLO inference
        results = self.model.predict(source=img, conf=self.confidence_threshold, save=False, show=False)
        annotated_frame = results[0].plot()

        # Get image dimensions
        frame_height, frame_width = img.shape[:2]
        image_center_x = frame_width // 2
        horizontal_offset = None

        # Extract detection results
        boxes = results[0].boxes

        if boxes and len(boxes) > 0:
            box = boxes[0]
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_center_x = int((x1 + x2) / 2)
            horizontal_offset = float(box_center_x - image_center_x)

            # Draw center lines and offset if detection exists
            cv2.line(annotated_frame, (int(box_center_x), 0), (int(box_center_x), frame_height), (255, 0, 0), 2)
            cv2.line(annotated_frame, (image_center_x, 0), (image_center_x, frame_height), (0, 0, 255), 1)

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
            if self.serial_connection:
                try:
                    self.serial_connection.write(f"{horizontal_offset:.2f}\n".encode('utf-8'))
                except Exception as e:
                    print(f"Serial write error: {e}")

        # Draw FPS
        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.2f}",
            org=(10, 60),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.6,
            color=(255, 255, 255),
            thickness=1
        )
        
        # --- END OF YOLO INFERENCE AND ANNOTATION ---

        # Re-convert the numpy array back to a video frame object
        new_frame = frame.from_ndarray(annotated_frame, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        return new_frame

# ----------- WEB SERVER -----------

pcs = set()

async def index(request):
    content = open("index.html", "r").read()
    return web.Response(content_type="text/html", text=content)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            asyncio.create_task(pc.close())
            pcs.discard(pc)
    
    # 1. Set the remote description (offer) first
    await pc.setRemoteDescription(offer)

    # 2. Add the video track using MediaRelay after setting the remote description
    pc.addTrack(
        VideoTransformTrack(relay.subscribe(cap))
    )

    # 3. Create the answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # 4. Return the answer
    return web.Response(
        content_type="application/json",
        text=json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}),
    )

async def cleanup():
    # Clean up all open connections on shutdown
    for pc in list(pcs):
        await pc.close()

app = web.Application()
app.router.add_get("/", index)
app.router.add_post("/offer", offer)

if __name__ == "__main__":
    try:
        web.run_app(app, port=8080)
    finally:
        # Ensure camera and serial connections are closed
        if cap.isOpened():
            cap.release()
        if serial_connection:
            serial_connection.close()