import cv2
from ultralytics import YOLO

# Load the trained YOLOv8 model from the best.pt file
model_path = '../training/best.pt'
model = YOLO(model_path)

# Video source (change to your video file path)
video_path = '../dataset/swimming_test.MP4'
cap = cv2.VideoCapture(video_path)

# Check if video was opened successfully
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 inference on the frame
        results = model(frame)

        # Get the annotated frame from the results
        # The 'show=True' parameter in the predict function can display a window directly,
        # but manual drawing provides more control. 'plot()' method simplifies this.
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and destroy all windows
cap.release()
cv2.destroyAllWindows()