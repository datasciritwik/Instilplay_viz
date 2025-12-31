import cv2
import json
import os

def map_first_frame():
    # Define paths relative to the notebook directory
    DATA_PATH = "../data"
    
    # Find files
    try:
        json_files = [f"{DATA_PATH}/{f}" for f in os.listdir(DATA_PATH) if f.endswith(".json")]
        video_files = [f"{DATA_PATH}/{f}" for f in os.listdir(DATA_PATH) if f.endswith(".mp4")]
    except FileNotFoundError:
        print(f"Error: Data directory '{DATA_PATH}' not found.")
        return

    if not json_files:
        print("Error: No JSON file found in data directory.")
        return
    if not video_files:
        print("Error: No MP4 video file found in data directory.")
        return

    print(f"Using JSON: {json_files[0]}")
    print(f"Using Video: {video_files[0]}")

    # Load annotations
    with open(json_files[0], "r") as f:
        annotations = json.load(f)

    # Load video
    video = cv2.VideoCapture(video_files[0])

    # Get first frame
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, frame = video.read()

    if ret:
        height, width, _ = frame.shape
        
        # Get frame 0 pose data
        if 'pose_data' in annotations and len(annotations['pose_data']) > 0:
            frame_data = annotations['pose_data'][0]
            landmarks = frame_data.get('landmarks', [])
            
            print(f"Mapping {len(landmarks)} landmarks for frame {frame_data.get('frame_idx', 0)}")

            # Draw landmarks
            for lm in landmarks:
                # Denormalize coordinates
                x = int(lm['x'] * width)
                y = int(lm['y'] * height)
                
                # Draw circle (green for visible, red for visibility logic?)
                # Just green for now
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            # Save output
            output_filename = "first_frame_mapped.png"
            cv2.imwrite(output_filename, frame)
            print(f"Successfully saved mapped annotation to: {os.path.abspath(output_filename)}")
        else:
            print("Error: No pose_data available in annotations.")
    else:
        print("Error: Could not read video frame.")
    
    video.release()

if __name__ == "__main__":
    map_first_frame()
