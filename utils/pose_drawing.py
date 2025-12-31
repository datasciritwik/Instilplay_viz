"""
Pose drawing utilities for cricket kinematics visualization.
Moved from st_app.py for modularity.
"""
import cv2

# MediaPipe Pose landmark indices
# Head/Face: 0-10
# Arms: 11-16 (shoulders, elbows, wrists)
# Torso: 11, 12, 23, 24 (shoulders and hips)
# Legs: 23-32 (hips, knees, ankles, feet)

# Color scheme (BGR format)
COLORS = {
    'head': (255, 200, 0),      # Cyan - head/face
    'torso': (0, 255, 0),       # Green - torso/core
    'arms': (0, 165, 255),      # Orange - both arms
    'legs': (255, 0, 255),      # Magenta - both legs
}

# MediaPipe Pose Connections with body part labels
POSE_CONNECTIONS = [
    # Torso
    ((11, 12), 'torso'),  # shoulders
    ((11, 23), 'torso'),  # left shoulder to hip
    ((12, 24), 'torso'),  # right shoulder to hip
    ((23, 24), 'torso'),  # hips
    
    # Arms
    ((11, 13), 'arms'),   # left shoulder to elbow
    ((13, 15), 'arms'),   # left elbow to wrist
    ((12, 14), 'arms'),   # right shoulder to elbow
    ((14, 16), 'arms'),   # right elbow to wrist
    
    # Legs
    ((23, 25), 'legs'),   # left hip to knee
    ((25, 27), 'legs'),   # left knee to ankle
    ((24, 26), 'legs'),   # right hip to knee
    ((26, 28), 'legs'),   # right knee to ankle
    ((27, 29), 'legs'),   # left ankle to heel
    ((29, 31), 'legs'),   # left heel to toe
    ((28, 30), 'legs'),   # right ankle to heel
    ((30, 32), 'legs'),   # right heel to toe
    ((27, 31), 'legs'),   # left foot
    ((28, 32), 'legs'),   # right foot
]

def get_landmark_color(idx):
    """Get color for a landmark based on its index."""
    if idx <= 10:
        return COLORS['head']
    elif idx in [11, 12, 23, 24]:
        return COLORS['torso']
    elif idx in [13, 14, 15, 16]:
        return COLORS['arms']
    else:
        return COLORS['legs']

def draw_pose_on_frame(frame, landmarks, width, height):
    """
    Draws pose landmarks and connections on the frame with color-coded body parts.
    
    Args:
        frame: Video frame (numpy array)
        landmarks: List of landmark dicts with 'x', 'y', 'z', 'visibility'
        width: Frame width in pixels
        height: Frame height in pixels
    
    Returns:
        Modified frame with pose overlay
    """
    # Convert to pixel coordinates
    points = {}
    for idx, lm in enumerate(landmarks):
        cx, cy = int(lm['x'] * width), int(lm['y'] * height)
        points[idx] = (cx, cy)
        # Draw landmarks with color based on body part
        color = get_landmark_color(idx)
        cv2.circle(frame, (cx, cy), 5, color, -1)
            
    # Draw connections with color based on body part
    for (start_idx, end_idx), body_part in POSE_CONNECTIONS:
        if start_idx in points and end_idx in points:
            color = COLORS[body_part]
            cv2.line(frame, points[start_idx], points[end_idx], color, 3)

    return frame
