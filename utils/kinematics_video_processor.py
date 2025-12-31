"""
Video processing for kinematics visualization.
Shows hip, torso, and shoulder lines with rotation indicators.
"""
import cv2
import numpy as np
from utils.pose_drawing import draw_pose_on_frame

def draw_kinematics_overlay(frame, landmarks, width, height, frame_idx, 
                            hip_frame, torso_frame, shoulder_frame):
    """
    Draw kinematics overlay showing hip, torso, and shoulder lines.
    
    Args:
        frame: Video frame
        landmarks: Pose landmarks
        width: Frame width
        height: Frame height
        frame_idx: Current frame index
        hip_frame: Hip peak frame
        torso_frame: Torso peak frame
        shoulder_frame: Shoulder peak frame
    
    Returns:
        Modified frame
    """
    # MediaPipe indices
    L_HIP = 23
    R_HIP = 24
    L_SHOULDER = 11
    R_SHOULDER = 12
    
    if len(landmarks) <= max(L_HIP, R_HIP, L_SHOULDER, R_SHOULDER):
        return frame
    
    # Get positions
    l_hip = (int(landmarks[L_HIP]['x'] * width), int(landmarks[L_HIP]['y'] * height))
    r_hip = (int(landmarks[R_HIP]['x'] * width), int(landmarks[R_HIP]['y'] * height))
    l_sh = (int(landmarks[L_SHOULDER]['x'] * width), int(landmarks[L_SHOULDER]['y'] * height))
    r_sh = (int(landmarks[R_SHOULDER]['x'] * width), int(landmarks[R_SHOULDER]['y'] * height))
    
    # Calculate midpoints
    hip_mid = ((l_hip[0] + r_hip[0]) // 2, (l_hip[1] + r_hip[1]) // 2)
    sh_mid = ((l_sh[0] + r_sh[0]) // 2, (l_sh[1] + r_sh[1]) // 2)
    
    # Determine active segment and colors
    if frame_idx <= hip_frame:
        hip_color = (0, 255, 255)  # Yellow - active
        torso_color = (128, 128, 128)  # Gray
        shoulder_color = (128, 128, 128)
        phase = "HIP DOMINANT"
        phase_color = (0, 255, 255)
    elif frame_idx <= torso_frame:
        hip_color = (0, 165, 255)  # Orange - completed
        torso_color = (0, 255, 255)  # Yellow - active
        shoulder_color = (128, 128, 128)
        phase = "TORSO DOMINANT"
        phase_color = (0, 255, 255)
    elif frame_idx <= shoulder_frame:
        hip_color = (0, 165, 255)  # Orange
        torso_color = (0, 165, 255)  # Orange
        shoulder_color = (0, 255, 255)  # Yellow - active
        phase = "SHOULDER DOMINANT"
        phase_color = (0, 255, 255)
    else:
        hip_color = (0, 255, 0)  # Green - all completed
        torso_color = (0, 255, 0)
        shoulder_color = (0, 255, 0)
        phase = "SEQUENCE COMPLETE"
        phase_color = (0, 255, 0)
    
    # Draw hip line
    cv2.line(frame, l_hip, r_hip, hip_color, 4)
    cv2.circle(frame, l_hip, 8, hip_color, -1)
    cv2.circle(frame, r_hip, 8, hip_color, -1)
    cv2.putText(frame, "HIP", (l_hip[0] - 40, l_hip[1] + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, hip_color, 2)
    
    # Draw shoulder line
    cv2.line(frame, l_sh, r_sh, shoulder_color, 4)
    cv2.circle(frame, l_sh, 8, shoulder_color, -1)
    cv2.circle(frame, r_sh, 8, shoulder_color, -1)
    cv2.putText(frame, "SHOULDER", (l_sh[0] - 60, l_sh[1] - 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, shoulder_color, 2)
    
    # Draw torso line (connecting midpoints)
    cv2.line(frame, hip_mid, sh_mid, torso_color, 3)
    torso_mid = ((hip_mid[0] + sh_mid[0]) // 2, (hip_mid[1] + sh_mid[1]) // 2)
    cv2.putText(frame, "TORSO", (torso_mid[0] + 10, torso_mid[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, torso_color, 2)
    
    # Draw phase indicator
    cv2.putText(frame, phase, (10, height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, phase_color, 2)
    
    # Draw peak markers
    if frame_idx == hip_frame:
        cv2.putText(frame, "HIP PEAK!", (width - 200, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    elif frame_idx == torso_frame:
        cv2.putText(frame, "TORSO PEAK!", (width - 200, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    elif frame_idx == shoulder_frame:
        cv2.putText(frame, "SHOULDER PEAK!", (width - 250, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    return frame

def process_video_with_kinematics(video_path, pose_data, kin_data, metadata, output_path):
    """
    Process video with kinematics overlay.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        kin_data: Kinematics analysis data
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
    
    # Video writer - use mp4v for better compatibility on Streamlit Cloud
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        return None
    
    # Extract kinematics data
    peaks = kin_data.get("peaks", {})
    hip_frame = peaks.get("hip_frame", 0)
    torso_frame = peaks.get("torso_frame", 0)
    shoulder_frame = peaks.get("shoulder_frame", 0)
    
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
            
            # Draw kinematics overlay
            frame = draw_kinematics_overlay(frame, landmarks, width, height, 
                                           frame_idx, hip_frame, torso_frame, shoulder_frame)
        
        out.write(frame)
        frame_idx += 1
    
    cap.release()
    out.release()
    
    return output_path
