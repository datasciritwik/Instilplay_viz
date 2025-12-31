"""
Video processing utilities for head stability visualization.
"""
import cv2
import numpy as np
from utils.pose_drawing import draw_pose_on_frame
from visualizations.head_viz import draw_head_on_frame

def process_video_with_head_tracking(video_path, pose_data, head_data, metadata, output_path):
    """
    Process video with pose annotations and head tracking overlay.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        head_data: Head stability data
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
    
    # Video writer - use VP80 for browser compatibility, fallback to mp4v
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        return None
    
    # Extract head data
    head_x_series = head_data.get("head_x_smooth", [])
    head_y_series = head_data.get("head_y_smooth", [])
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    
    # Generate heatmap overlay
    heatmap_overlay = None
    if head_x_series and head_y_series and len(head_x_series) > 10:
        # Create 2D histogram
        hist, xedges, yedges = np.histogram2d(
            head_x_series, head_y_series, 
            bins=[width//20, height//20],  # Lower resolution for smoother look
            range=[[0, 1], [0, 1]]
        )
        
        # Normalize and create heatmap
        hist = hist.T
        hist = (hist / hist.max() * 255).astype(np.uint8) if hist.max() > 0 else hist.astype(np.uint8)
        
        # Resize to full frame size
        heatmap_resized = cv2.resize(hist, (width, height), interpolation=cv2.INTER_LINEAR)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
        
        # Make it semi-transparent by creating alpha channel
        heatmap_overlay = heatmap_colored.copy()
    
    # Create pose map
    pose_map = {item['frame_idx']: item['landmarks'] for item in pose_data if item.get('landmarks')}
    
    frame_idx = 0
    head_trail = []
    trail_length = 20
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Draw pose if available
        landmarks = pose_map.get(frame_idx)
        if landmarks:
            frame = draw_pose_on_frame(frame, landmarks, width, height)
        
        # Overlay heatmap with transparency
        if heatmap_overlay is not None:
            frame = cv2.addWeighted(frame, 0.7, heatmap_overlay, 0.3, 0)
        
        # Draw head tracking if available
        if frame_idx < len(head_x_series) and frame_idx < len(head_y_series):
            head_x = head_x_series[frame_idx]
            head_y = head_y_series[frame_idx]
            
            # Update trail
            head_trail.append((head_x, head_y))
            if len(head_trail) > trail_length:
                head_trail.pop(0)
            
            frame = draw_head_on_frame(
                frame, head_x, head_y, frame_idx, 
                stance_frame, impact_frame, 
                head_trail, width, height
            )
        
        out.write(frame)
        frame_idx += 1
    
    cap.release()
    out.release()
    
    return output_path
