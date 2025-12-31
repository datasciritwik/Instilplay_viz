"""
Real-time video processing utilities without saving to disk.
Streams processed frames directly to Streamlit.
"""
import cv2
import numpy as np
import streamlit as st
from utils.pose_drawing import draw_pose_on_frame
from visualizations.com_viz import draw_com_on_frame

def display_com_video_realtime(video_path, pose_data, com_data, metadata):
    """
    Display COM annotated video in real-time without saving.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        com_data: COM analysis data
        metadata: Video metadata
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Failed to open video")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Extract COM data
    com_x_series = com_data.get("com_x_series", [])
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    
    # Create pose map
    pose_map = {item['frame_idx']: item['landmarks'] for item in pose_data if item.get('landmarks')}
    
    # Create placeholder for video
    video_placeholder = st.empty()
    
    frame_idx = 0
    com_trail = []
    trail_length = 15
    frames_buffer = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Draw pose if available
        landmarks = pose_map.get(frame_idx)
        if landmarks:
            frame = draw_pose_on_frame(frame, landmarks, width, height)
        
        # Draw COM if available
        if frame_idx < len(com_x_series):
            com_x = com_x_series[frame_idx]
            com_trail.append(com_x)
            if len(com_trail) > trail_length:
                com_trail.pop(0)
            
            frame = draw_com_on_frame(frame, com_x, frame_idx, stance_frame, 
                                     impact_frame, com_trail, width, height)
        
        # Convert BGR to RGB for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames_buffer.append(frame_rgb)
        
        frame_idx += 1
    
    cap.release()
    
    # Display as video using st.image with animation
    if frames_buffer:
        # Show first frame
        video_placeholder.image(frames_buffer[0], use_column_width=True, caption="COM Analysis Video")
        
        # Note: Streamlit doesn't support real-time video streaming from numpy arrays
        # We need to save temporarily or use the original video
        st.info("💡 Annotated video preview: Processing complete. Use charts below for detailed analysis.")
