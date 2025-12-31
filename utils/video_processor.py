"""
Video processing utilities with smart codec detection and fallback.
Handles both local (H.264) and cloud (WebM/VP8) environments.
"""
import cv2
import numpy as np
import subprocess
import os
import tempfile
from utils.pose_drawing import draw_pose_on_frame

def detect_available_codec():
    """
    Detect which video codec is available in the current environment.
    
    Returns:
        tuple: (fourcc, extension, codec_name)
    """
    test_width, test_height = 640, 480
    test_fps = 24
    
    # Try codecs in order of preference for web compatibility
    codecs_to_try = [
        (cv2.VideoWriter_fourcc(*'VP80'), '.webm', 'VP8'),  # VP8 - better compatibility
        (cv2.VideoWriter_fourcc(*'VP90'), '.webm', 'VP9'),  # VP9 - better quality
        (cv2.VideoWriter_fourcc(*'MJPG'), '.avi', 'MJPEG'), # MJPEG - fallback
        (cv2.VideoWriter_fourcc(*'mp4v'), '.mp4', 'MPEG4'), # MPEG4
        (cv2.VideoWriter_fourcc(*'avc1'), '.mp4', 'H264'),  # H.264 - local only
    ]
    
    for fourcc, ext, name in codecs_to_try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            test_path = tmp.name
        
        try:
            writer = cv2.VideoWriter(test_path, fourcc, test_fps, (test_width, test_height))
            if writer.isOpened():
                # Test if we can actually write a frame
                test_frame = np.zeros((test_height, test_width, 3), dtype=np.uint8)
                writer.write(test_frame)
                writer.release()
                
                # Check if file was created and has content
                if os.path.exists(test_path) and os.path.getsize(test_path) > 0:
                    os.remove(test_path)
                    return fourcc, ext, name
            
            if os.path.exists(test_path):
                os.remove(test_path)
        except Exception:
            if os.path.exists(test_path):
                os.remove(test_path)
            continue
    
    # If nothing works, return None
    return None, None, None

def create_video_writer(output_path, width, height, fps):
    """
    Create video writer with automatic codec detection.
    
    Args:
        output_path: Path to save output video
        width: Video width
        height: Video height
        fps: Frames per second
    
    Returns:
        tuple: (cv2.VideoWriter, final_output_path) or (None, None) if failed
    """
    # Detect available codec
    fourcc, ext, codec_name = detect_available_codec()
    
    if fourcc is None:
        print("ERROR: No compatible video codec found!")
        return None, None
    
    print(f"Using codec: {codec_name} with extension {ext}")
    
    # Update output path with correct extension
    base_path = output_path.rsplit('.', 1)[0]
    final_output_path = base_path + ext
    
    # Create writer
    out = cv2.VideoWriter(final_output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print(f"ERROR: Failed to open video writer with {codec_name}")
        return None, None
    
    return out, final_output_path

def convert_to_web_format(input_path, output_path=None):
    """
    Convert video to web-compatible format using ffmpeg if available.
    
    Args:
        input_path: Input video path
        output_path: Output path (optional, will auto-generate)
    
    Returns:
        str: Path to converted video or None if failed
    """
    if output_path is None:
        output_path = input_path.rsplit('.', 1)[0] + '_web.mp4'
    
    try:
        # Try to use ffmpeg to convert
        result = subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx264',  # H.264 is widely supported
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-movflags', '+faststart',  # Enable streaming
            output_path
        ], capture_output=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"FFmpeg conversion failed: {e}")
    
    # If conversion failed, return original
    return input_path

def draw_com_on_frame(frame, com_x, frame_idx, stance_frame, impact_frame, 
                      com_trail=None, width=None, height=None):
    """Draw COM visualization on frame."""
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
    cv2.circle(frame, (com_pixel_x, com_pixel_y), 12, (255, 255, 255), 2)
    
    # Draw trail
    if com_trail and len(com_trail) > 1:
        for i in range(len(com_trail) - 1):
            pt1 = (int(com_trail[i] * width), int(height * 0.5))
            pt2 = (int(com_trail[i+1] * width), int(height * 0.5))
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
    Uses automatic codec detection for maximum compatibility.
    
    Args:
        video_path: Input video path
        pose_data: List of pose data for each frame
        com_data: COM analysis data
        metadata: Video metadata
        output_path: Output video path
    
    Returns:
        Output video path or None if failed
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("ERROR: Cannot open input video")
        return None
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Create video writer with automatic codec detection
    out, final_output_path = create_video_writer(output_path, width, height, fps)
    
    if out is None:
        cap.release()
        print("ERROR: Cannot create video writer")
        return None
    
    # Extract COM data
    com_x_series = com_data.get("com_x_series", [])
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    
    # Create pose map for quick lookup
    pose_map = {item['frame_idx']: item['landmarks'] for item in pose_data if item.get('landmarks')}
    
    frame_idx = 0
    com_trail = []
    trail_length = 15
    
    print(f"Processing {len(pose_data)} frames...")
    
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
        
        out.write(frame)
        frame_idx += 1
        
        # Progress indicator every 50 frames
        if frame_idx % 50 == 0:
            print(f"Processed {frame_idx} frames...")
    
    cap.release()
    out.release()
    
    print(f"Video saved to: {final_output_path}")
    
    # Try to convert to web-compatible format if not already
    if not final_output_path.endswith(('.mp4', '.webm')):
        print("Converting to web-compatible format...")
        converted_path = convert_to_web_format(final_output_path, output_path)
        if converted_path != final_output_path:
            # Remove temp file
            try:
                os.remove(final_output_path)
            except:
                pass
            return converted_path
    
    return final_output_path