import cv2
import os

def extract_frames(video_path, output_folder, frame_rate=1):
    """
    Extracts frames from a video and saves them as images.

    Args:
        video_path (str): The path to the video file.
        output_folder (str): The folder where the frames will be saved.
        frame_rate (int): The number of frames per second to save.
                          1 frame_rate = 1 frame per second.
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    video = cv2.VideoCapture(video_path)

    # Check if the video was opened correctly
    if not video.isOpened():
        print(f"Error: Could not open the video at {video_path}")
        return

    # Get the video's frames per second (FPS)
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video opened: {video_path} | FPS: {fps} | Total frames: {total_frames}")

    count = 0
    saved_frames = 0
    
    while True:
        # Read the next frame
        success, frame = video.read()
        
        # If there are no more frames, exit the loop
        if not success:
            break

        # Save the frame if it's within the desired interval (controlled by frame_rate)
        if count % (round(fps) // frame_rate) == 0:
            frame_name = f"frame_{saved_frames:06d}.jpg"
            frame_path = os.path.join(output_folder, frame_name)
            cv2.imwrite(frame_path, frame)
            saved_frames += 1

        count += 1
    
    # Release the video object
    video.release()
    print(f"Extraction complete. {saved_frames} frames saved to {output_folder}")


if __name__ == "__main__":
    # Change your video file path and output folder
    video_file = "swimming_test.MP4"
    output_dir = "test_frames"
    
    # Choose the frame rate you want to extract.
    # E.g., 1 frame/second, 2 frames/second, etc.
    extract_frames(video_file, output_dir, frame_rate=1)