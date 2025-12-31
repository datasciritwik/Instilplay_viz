"""
Video processing utilities for cricket kinematics visualization.
"""
import cv2
import numpy as np
import logging
import subprocess
import tempfile
import os
from utils.pose_drawing import draw_pose_on_frame

logger = logging.getLogger(__name__)

def _ensure_faststart(output_path):
    """Try to remux MP4 with ffmpeg -movflags +faststart to make it streamable.
    If ffmpeg is not available or fails, this silently logs a warning and continues.
    """
    try:
        fd, tmp = tempfile.mkstemp(suffix=".mp4", dir=os.path.dirname(output_path) or None)
        os.close(fd)
        cmd = ["ffmpeg", "-y", "-i", output_path, "-c", "copy", "-movflags", "+faststart", tmp]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(tmp, output_path)
        logger.info("Remuxed video with faststart: %s", output_path)
    except Exception as e:
        logger.warning("ffmpeg remux failed (ffmpeg may be missing) for %s: %s", output_path, e)


def create_video_writer(output_path, width, height, fps):
    """
    Create video writer with mp4v codec for MP4 format.
    
    Args:
        output_path: Path to save output video
        width: Video width
        height: Video height
        fps: Frames per second
    
    Returns:
        cv2.VideoWriter object
    """
    # Use mp4v codec for MP4 container
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    return out

def draw_com_on_frame(frame, com_x, frame_idx, stance_frame, impact_frame, 
                      com_trail=None, width=None, height=None):
    """
    Draw COM (Center of Mass) visualization on frame.
    
    Args:
        frame: Video frame
        com_x: COM x-position (normalized 0-1)
        frame_idx: Current frame index
        stance_frame: Stance frame index
        impact_frame: Impact frame index
        com_trail: List of recent COM positions for trail effect
        width: Frame width (if None, use frame.shape)
        height: Frame height (if None, use frame.shape)
    
    Returns:
        Modified frame with COM overlay
    """
    if width is None:
        height, width = frame.shape[:2]
    
    # Determine phase color
    if frame_idx < stance_frame:
        color = (255, 100, 0)  # Blue - pre-stance
    elif frame_idx <= impact_frame:
        color = (0, 255, 0)    # Green - stance to impact
    else:
        color = (0, 165, 255)  # Orange - post-impact
    
    # Draw COM dot at mid-height
    com_pixel_x = int(com_x * width)
    com_pixel_y = int(height * 0.5)
    cv2.circle(frame, (com_pixel_x, com_pixel_y), 10, color, -1)
    cv2.circle(frame, (com_pixel_x, com_pixel_y), 12, (255, 255, 255), 2)  # White outline
    
    # Draw trail
    if com_trail and len(com_trail) > 1:
        for i in range(len(com_trail) - 1):
            pt1 = (int(com_trail[i] * width), int(height * 0.5))
            pt2 = (int(com_trail[i+1] * width), int(height * 0.5))
            # Fade trail
            alpha = (i + 1) / len(com_trail)
            thickness = max(1, int(3 * alpha))
            cv2.line(frame, pt1, pt2, color, thickness)
    
    # Add text label
    label = f"COM: {com_x:.3f}"
    cv2.putText(frame, label, (com_pixel_x - 50, com_pixel_y - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return frame

def process_video_with_com_overlay(video_path, pose_data, com_data, metadata, output_path):
    """
    Process video with pose annotations and COM overlay.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        com_data: COM analysis data
        metadata: Video metadata
        output_path: Output video path
    
    Returns:
        Output video path or None if failed
    """
    cap = None
    out = None
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("Failed to open input video: %s", video_path)
            return None
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        out = create_video_writer(output_path, width, height, fps)
        if not out.isOpened():
            logger.error("Failed to open VideoWriter for %s", output_path)
            return None
        
        # Extract COM data
        com_x_series = com_data.get("com_x_series", [])
        stance_frame = com_data.get("stance_frame", 0)
        impact_frame = com_data.get("impact_frame", 0)
        
        # Create pose map for quick lookup
        pose_map = {item['frame_idx']: item['landmarks'] for item in pose_data if item.get('landmarks')}
        
        frame_idx = 0
        com_trail = []
        trail_length = 15  # Number of frames to show in trail
        
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
                
                # Update trail
                com_trail.append(com_x)
                if len(com_trail) > trail_length:
                    com_trail.pop(0)
                
                frame = draw_com_on_frame(frame, com_x, frame_idx, stance_frame, 
                                         impact_frame, com_trail, width, height)
            
            out.write(frame)
            frame_idx += 1
        
        # Try to make file streamable
        try:
            _ensure_faststart(output_path)
        except Exception:
            pass
        
        return output_path
    except Exception as e:
        logger.exception("Error while processing COM overlay: %s", e)
        return None
    finally:
        try:
            if cap is not None:
                cap.release()
        except Exception:
            pass
        try:
            if out is not None:
                out.release()
        except Exception:
            pass
