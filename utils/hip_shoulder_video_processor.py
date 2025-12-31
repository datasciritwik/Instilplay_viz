"""
Video processing for hip-shoulder separation visualization.
"""
import cv2
import numpy as np
from utils.pose_drawing import draw_pose_on_frame

def draw_hip_shoulder_lines(frame, landmarks, width, height, angle, is_peak=False):
    """
    Draw hip and shoulder lines with separation angle.
    
    Args:
        frame: Video frame
        landmarks: Pose landmarks
        width: Frame width
        height: Frame height
        angle: Current separation angle
        is_peak: Whether this is the peak separation frame
    
    Returns:
        Modified frame
    """
    # Get landmark positions
    L_SHOULDER = 11
    R_SHOULDER = 12
    L_HIP = 23
    R_HIP = 24
    
    if len(landmarks) <= max(L_SHOULDER, R_SHOULDER, L_HIP, R_HIP):
        return frame
    
    # Convert to pixel coordinates
    l_sh = (int(landmarks[L_SHOULDER]['x'] * width), int(landmarks[L_SHOULDER]['y'] * height))
    r_sh = (int(landmarks[R_SHOULDER]['x'] * width), int(landmarks[R_SHOULDER]['y'] * height))
    l_hp = (int(landmarks[L_HIP]['x'] * width), int(landmarks[L_HIP]['y'] * height))
    r_hp = (int(landmarks[R_HIP]['x'] * width), int(landmarks[R_HIP]['y'] * height))
    
    # Color based on whether it's peak frame
    hip_color = (0, 255, 0) if is_peak else (255, 165, 0)  # Green at peak, orange otherwise
    shoulder_color = (0, 0, 255) if is_peak else (255, 0, 255)  # Red at peak, magenta otherwise
    thickness = 4 if is_peak else 3
    
    # Draw hip line
    cv2.line(frame, l_hp, r_hp, hip_color, thickness)
    cv2.putText(frame, "HIPS", (l_hp[0] - 50, l_hp[1] + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, hip_color, 2)
    
    # Draw shoulder line
    cv2.line(frame, l_sh, r_sh, shoulder_color, thickness)
    cv2.putText(frame, "SHOULDERS", (l_sh[0] - 80, l_sh[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, shoulder_color, 2)
    
    # Draw angle arc and text
    # Calculate midpoints
    hip_mid = ((l_hp[0] + r_hp[0]) // 2, (l_hp[1] + r_hp[1]) // 2)
    shoulder_mid = ((l_sh[0] + r_sh[0]) // 2, (l_sh[1] + r_sh[1]) // 2)
    
    # Draw connecting line between midpoints
    cv2.line(frame, hip_mid, shoulder_mid, (255, 255, 255), 1, cv2.LINE_AA)
    
    # Display angle
    text_pos = (width - 250, 50)
    bg_color = (0, 255, 0) if is_peak else (50, 50, 50)
    
    # Draw background rectangle for text
    cv2.rectangle(frame, (text_pos[0] - 10, text_pos[1] - 30), 
                  (text_pos[0] + 230, text_pos[1] + 10), bg_color, -1)
    
    # Draw text
    text = f"Separation: {angle:.1f}" if not is_peak else f"PEAK: {angle:.1f}"
    cv2.putText(frame, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, (255, 255, 255), 2)
    
    return frame

def process_video_with_hip_shoulder(video_path, pose_data, hs_data, metadata, output_path):
    """
    Process video with hip-shoulder separation overlay.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        hs_data: Hip-shoulder analysis data
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
    
    # Video writer - use mp4v codec for MP4 container
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        return None
    
    # Extract hip-shoulder data
    angle_series = hs_data.get("angle_series", [])
    key_frames = hs_data.get("key_frames", {})
    peak_frame = key_frames.get("peak_frame", 0)
    downswing_start = key_frames.get("downswing_start", 0)
    downswing_end = key_frames.get("downswing_end", 0)
    
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
            
            # Draw hip-shoulder lines if we have angle data
            if frame_idx < len(angle_series):
                angle = angle_series[frame_idx]
                is_peak = (frame_idx == peak_frame)
                frame = draw_hip_shoulder_lines(frame, landmarks, width, height, angle, is_peak)
        
        # Add phase indicator
        if downswing_start <= frame_idx <= downswing_end:
            cv2.putText(frame, "DOWNSWING", (10, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        out.write(frame)
        frame_idx += 1
    
    cap.release()
    out.release()
    
    return output_path
