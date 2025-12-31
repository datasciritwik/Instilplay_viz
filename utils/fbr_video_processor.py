"""
Video processing for FBR visualization.
"""
import cv2
import numpy as np
from utils.pose_drawing import draw_pose_on_frame

def draw_fbr_overlay(frame, landmarks, width, height, frame_idx, plant_frame, lowest_frame, com_y):
    """
    Draw FBR overlay on frame.
    
    Args:
        frame: Video frame
        landmarks: Pose landmarks
        width: Frame width
        height: Frame height
        frame_idx: Current frame index
        plant_frame: Foot plant frame
        lowest_frame: Lowest COM frame
        com_y: Current COM y position
    
    Returns:
        Modified frame
    """
    # Get ankle positions
    L_ANKLE = 27
    R_ANKLE = 28
    
    if len(landmarks) <= max(L_ANKLE, R_ANKLE):
        return frame
    
    # Draw ankle markers
    l_ankle = (int(landmarks[L_ANKLE]['x'] * width), int(landmarks[L_ANKLE]['y'] * height))
    r_ankle = (int(landmarks[R_ANKLE]['x'] * width), int(landmarks[R_ANKLE]['y'] * height))
    
    # Color based on phase
    if frame_idx < plant_frame:
        ankle_color = (255, 165, 0)  # Orange - pre-plant
        phase_text = "PRE-PLANT"
    elif frame_idx == plant_frame:
        ankle_color = (0, 0, 255)    # Red - foot plant
        phase_text = "FOOT PLANT"
    elif frame_idx <= lowest_frame:
        ankle_color = (0, 255, 255)  # Yellow - descent
        phase_text = "DESCENT"
    else:
        ankle_color = (0, 255, 0)    # Green - recovery
        phase_text = "RECOVERY"
    
    # Draw ankle circles
    cv2.circle(frame, l_ankle, 12, ankle_color, -1)
    cv2.circle(frame, r_ankle, 12, ankle_color, -1)
    cv2.circle(frame, l_ankle, 14, (255, 255, 255), 2)
    cv2.circle(frame, r_ankle, 14, (255, 255, 255), 2)
    
    # Draw ankle line
    cv2.line(frame, l_ankle, r_ankle, ankle_color, 3)
    
    # Display phase
    cv2.putText(frame, phase_text, (10, height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, ankle_color, 2)
    
    # Display COM Y position
    com_text = f"COM Y: {com_y:.3f}"
    cv2.putText(frame, com_text, (width - 200, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw COM indicator (horizontal line showing height)
    com_pixel_y = int(com_y * height)
    cv2.line(frame, (10, com_pixel_y), (100, com_pixel_y), (0, 255, 255), 3)
    cv2.putText(frame, "COM", (105, com_pixel_y + 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    return frame

def process_video_with_fbr(video_path, pose_data, fbr_data, metadata, output_path):
    """
    Process video with FBR overlay.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        fbr_data: FBR analysis data
        metadata: Video metadata
        output_path: Output video path
    
    Returns:
        Output video path or None if failed
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    
    
    if not output_path.endswith('.avi'):
        output_path = output_path.rsplit('.', 1)[0] + '.avi'

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
    
    if not output_path.endswith('.avi'):
        cap.release()
        return None
    
    # Extract FBR data
    com_y_series = fbr_data.get("com_y_series", [])
    plant_frame = fbr_data.get("plant_frame", 0)
    lowest_frame = fbr_data.get("lowest_com_frame", 0)
    
    # Create pose map
    pose_map = {item['frame_idx']: item['landmarks'] for item in pose_data if item.get('landmarks')}
    
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Draw pose if available
        landmarks = pose_map.get(frame_idx)
        if landmarks:
            frame = draw_pose_on_frame(frame, landmarks, width, height)
            
            # Draw FBR overlay
            if frame_idx < len(com_y_series):
                com_y = com_y_series[frame_idx]
                frame = draw_fbr_overlay(frame, landmarks, width, height, 
                                        frame_idx, plant_frame, lowest_frame, com_y)
        
        out.write(frame)
        frame_idx += 1
    
    cap.release()
    out.release()
    
    return output_path
