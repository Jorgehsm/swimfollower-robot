from flask import Flask, render_template, Response, request, jsonify
import cv2
import threading
import time
import os
import serial
import json

# --- CONFIGURATION CONSTANTS ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
VIDEO_SOURCE = 0 # Use 0 for the first connected camera, or '/dev/video0'
RECORDING_FPS = 30.0

# --- GLOBAL VARIABLES ---
# Serial connection with microcontroller
ser = None
try:
    # Attempt to establish serial connection
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to microcontroller on {SERIAL_PORT}")
except Exception as e:
    # Handle error if serial port is unavailable (e.g., during development)
    print(f"Warning: Error opening serial port: {e}. Motor control will be disabled.")
    print("If you are running this on a device with a microcontroller, check the port configuration.")

# Wait for the camera to be accessible. Use a loop if VIDEO_SOURCE is a path.
if isinstance(VIDEO_SOURCE, str):
    print("Waiting for camera to connect...")
    while not os.path.exists(VIDEO_SOURCE):
        time.sleep(0.2)

# Initialize Flask app and camera
app = Flask(__name__)
camera = cv2.VideoCapture(VIDEO_SOURCE)

# Check if the camera opened successfully
if not camera.isOpened():
    print(f"Error: Could not open video source {VIDEO_SOURCE}.")
    exit(1)

# Global state variables
is_recording = False
recording_thread = None
video_writer = None
motor_speed = 0 # Current motor speed value (0-255)
lock = threading.Lock() # Lock for thread-safe access to global variables

# ------------------ VIDEO STREAMING ------------------
def generate_frames():
    """Generates JPEG frames from the camera for the video stream."""
    global camera
    while True:
        # Acquire the frame
        success, frame = camera.read()
        if not success:
            # Reconnect camera if stream is lost (e.g., device unplugged/re-plugged)
            camera = cv2.VideoCapture(VIDEO_SOURCE)
            time.sleep(1)
            continue
        else:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            frame = buffer.tobytes()
            # Yield the frame in the multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ------------------ VIDEO RECORDING ------------------
def record_video():
    """Captures and saves video frames to a file in a separate thread."""
    global camera, is_recording, video_writer
    
    # Configure video file settings
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for MP4
    filename = f"dataset_{time.strftime('%Y%m%d-%H%M%S')}.mp4"
    
    # Get frame dimensions from the camera
    width  = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Initialize VideoWriter
    video_writer = cv2.VideoWriter(filename, fourcc, RECORDING_FPS, (width, height))
    
    print(f"Recording started. Output file: '{filename}'")

    while is_recording:
        # Must read from camera object used in the thread (or ensure thread-safe sharing)
        # For simplicity, we assume the camera can be read by both the streamer and recorder
        # The streamer will handle the primary camera access. This loop simply reads.
        success, frame = camera.read() 
        
        if success and video_writer.isOpened():
            video_writer.write(frame)
        
        # Maintain recording FPS
        time.sleep(1.0 / RECORDING_FPS)

    # Clean up when recording stops
    if video_writer is not None:
        video_writer.release()
        print(f"Recording finished. File saved as '{filename}'")

# ------------------ FLASK ROUTES ------------------

@app.route('/')
def index():
    """Main page route that serves the control panel HTML."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Route for the Motion JPEG video stream."""
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    """Starts or stops the video recording process."""
    global is_recording, recording_thread, lock
    
    with lock: # Use lock to safely modify shared state
        if not is_recording:
            # Start recording
            is_recording = True
            recording_thread = threading.Thread(target=record_video)
            recording_thread.start()
            return jsonify({'status': 'Recording started', 'is_recording': True}), 200
        else:
            # Stop recording
            is_recording = False
            if recording_thread is not None and recording_thread.is_alive():
                recording_thread.join(timeout=5) # Wait for thread to finish writing
            return jsonify({'status': 'Recording stopped', 'is_recording': False}), 200

@app.route('/set_speed', methods=['POST'])
def set_speed():
    """Receives and sets the motor speed via the serial connection."""
    global motor_speed, ser
    try:
        data = request.get_json()
        new_speed = data.get('speed')
        
        # Validation
        if new_speed is not None and 0 <= new_speed <= 255:
            motor_speed = int(new_speed)
            print(f"Motor speed set to: {motor_speed}")

            # Send command over serial if connected
            if ser is not None and ser.is_open:
                # The command format should match what the microcontroller expects (e.g., "150\n")
                command = f"{motor_speed}\n"
                ser.write(command.encode('utf-8'))
                print(f"Serial command sent: {command.strip()}")

            return jsonify({'status': 'Speed updated successfully', 'speed': motor_speed}), 200
        else:
            return jsonify({'status': 'Invalid value. Use between 0 and 255.'}), 400
    except Exception as e:
        print(f"Error in set_speed: {str(e)}")
        return jsonify({'status': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Ensure camera resource is released on exit
    def release_resources():
        global camera, ser
        print("Releasing camera and closing serial port...")
        if camera.isOpened():
            camera.release()
        if ser and ser.is_open:
            ser.close()

    import atexit
    atexit.register(release_resources)

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, threaded=True)
