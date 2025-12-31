"""
Head Stability visualization functions.
Creates interactive charts and overlays for head movement analysis.
"""
import plotly.graph_objects as go
import numpy as np
import cv2
from plotly.subplots import make_subplots

def plot_head_trajectory_2d(head_data):
    """
    Plot 2D trajectory of head movement (X vs Y).
    
    Args:
        head_data: Head stability data dict
    
    Returns:
        Plotly figure
    """
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    
    # Safety check for empty data
    if not head_x or not head_y or len(head_x) == 0 or len(head_y) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No head position data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Head Position Trajectory (2D Path)", height=500)
        return fig
    
    fig = go.Figure()
    
    # Pre-stance
    fig.add_trace(go.Scatter(
        x=head_x[:stance_frame+1],
        y=head_y[:stance_frame+1],
        mode='lines+markers',
        name='Pre-Stance',
        line=dict(color='blue', width=2),
        marker=dict(size=4)
    ))
    
    # Delivery (stance to impact)
    if impact_frame > stance_frame:
        fig.add_trace(go.Scatter(
            x=head_x[stance_frame:impact_frame+1],
            y=head_y[stance_frame:impact_frame+1],
            mode='lines+markers',
            name='Delivery',
            line=dict(color='green', width=3),
            marker=dict(size=5)
        ))
    
    # Post-impact
    if impact_frame < len(head_x) - 1:
        fig.add_trace(go.Scatter(
            x=head_x[impact_frame:],
            y=head_y[impact_frame:],
            mode='lines+markers',
            name='Post-Impact',
            line=dict(color='orange', width=2),
            marker=dict(size=4)
        ))
    
    # Mark stance and impact positions
    if stance_frame < len(head_x):
        fig.add_trace(go.Scatter(
            x=[head_x[stance_frame]],
            y=[head_y[stance_frame]],
            mode='markers',
            name='Stance',
            marker=dict(size=15, color='red', symbol='star')
        ))
    
    if impact_frame < len(head_x):
        fig.add_trace(go.Scatter(
            x=[head_x[impact_frame]],
            y=[head_y[impact_frame]],
            mode='markers',
            name='Impact',
            marker=dict(size=15, color='purple', symbol='star')
        ))
    
    fig.update_layout(
        title="Head Position Trajectory (2D Path)",
        xaxis_title="Horizontal Position (normalized)",
        yaxis_title="Vertical Position (normalized)",
        yaxis=dict(autorange='reversed'),  # Flip Y axis (0 is top in images)
        height=500,
        hovermode='closest'
    )
    
    return fig

def plot_head_position_over_time(head_data, metadata):
    """
    Plot head X and Y positions over time.
    
    Args:
        head_data: Head stability data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure with subplots
    """
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    # Safety check
    if not head_x or not head_y or len(head_x) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No head position data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Head Position Over Time", height=600)
        return fig
    
    frames = list(range(len(head_x)))
    time_sec = [f / fps for f in frames]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Horizontal Movement (X)", "Vertical Movement (Y)"),
        vertical_spacing=0.12
    )
    
    # X position
    fig.add_trace(
        go.Scatter(x=time_sec, y=head_x, mode='lines', name='X Position',
                   line=dict(color='steelblue', width=2)),
        row=1, col=1
    )
    
    # Y position
    fig.add_trace(
        go.Scatter(x=time_sec, y=head_y, mode='lines', name='Y Position',
                   line=dict(color='coral', width=2)),
        row=2, col=1
    )
    
    # Add stance markers
    for row in [1, 2]:
        fig.add_vline(
            x=stance_frame/fps, line_dash="dash", line_color="red",
            annotation_text="Stance" if row == 1 else "",
            row=row, col=1
        )
        fig.add_vline(
            x=impact_frame/fps, line_dash="dash", line_color="purple",
            annotation_text="Impact" if row == 1 else "",
            row=row, col=1
        )
    
    fig.update_xaxes(title_text="Time (seconds)", row=2, col=1)
    fig.update_yaxes(title_text="Position", row=1, col=1)
    fig.update_yaxes(title_text="Position", row=2, col=1)
    
    fig.update_layout(height=600, showlegend=False, hovermode='x unified')
    
    return fig

def plot_head_displacement(head_data, metadata):
    """
    Plot frame-to-frame displacement (jitter).
    
    Args:
        head_data: Head stability data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    
    # Safety check
    if not head_x or not head_y or len(head_x) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No head position data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Head Displacement", height=400)
        return fig
    
    head_x = np.array(head_x)
    head_y = np.array(head_y)
    
    # Calculate displacement
    disp = np.sqrt(np.diff(head_x, prepend=head_x[0])**2 + 
                   np.diff(head_y, prepend=head_y[0])**2)
    
    frames = list(range(len(disp)))
    
    fig = go.Figure()
    
    # Add displacement line
    fig.add_trace(go.Scatter(
        x=frames,
        y=disp,
        mode='lines',
        name='Displacement',
        line=dict(color='darkgreen', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 128, 0, 0.2)'
    ))
    
    # Add stance marker
    fig.add_vline(
        x=stance_frame,
        line_dash="dash",
        line_color="red",
        annotation_text="Stance",
        annotation_position="top"
    )
    
    # Add impact marker
    fig.add_vline(
        x=impact_frame,
        line_dash="dash",
        line_color="purple",
        annotation_text="Impact",
        annotation_position="top"
    )
    
    fig.update_layout(
        title="Head Displacement (Frame-to-Frame Movement)",
        xaxis_title="Frame",
        yaxis_title="Displacement (normalized units)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_head_heatmap(head_data):
    """
    Create density heatmap of head positions.
    
    Args:
        head_data: Head stability data dict
    
    Returns:
        Plotly figure
    """
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    
    # Safety check
    if not head_x or not head_y or len(head_x) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Head Position Density Heatmap", height=500)
        return fig
    
    # Create 2D histogram
    hist, xedges, yedges = np.histogram2d(head_x, head_y, bins=30)
    
    fig = go.Figure(data=go.Heatmap(
        z=hist.T,
        x=xedges[:-1],
        y=yedges[:-1],
        colorscale='Hot',
        colorbar=dict(title="Density")
    ))
    
    fig.update_layout(
        title="Head Position Density Heatmap",
        xaxis_title="Horizontal Position",
        yaxis_title="Vertical Position",
        yaxis=dict(autorange='reversed'),
        height=500
    )
    
    return fig

def draw_head_on_frame(frame, head_x, head_y, frame_idx, stance_frame, impact_frame,
                       head_trail=None, width=None, height=None, heatmap_overlay=None):
    """
    Draw head position visualization on frame.
    
    Args:
        frame: Video frame
        head_x: Head x-position (normalized 0-1)
        head_y: Head y-position (normalized 0-1)
        frame_idx: Current frame index
        stance_frame: Stance frame index
        impact_frame: Impact frame index
        head_trail: List of recent head positions for trail
        width: Frame width
        height: Frame height
        heatmap_overlay: Optional heatmap image to overlay
    
    Returns:
        Modified frame
    """
    if width is None:
        height, width = frame.shape[:2]
    
    # Determine phase color
    if frame_idx < stance_frame:
        color = (255, 100, 0)  # Blue
    elif frame_idx <= impact_frame:
        color = (0, 255, 0)    # Green
    else:
        color = (0, 165, 255)  # Orange
    
    # Draw head position
    head_pixel_x = int(head_x * width)
    head_pixel_y = int(head_y * height)
    
    # Draw crosshair
    cv2.line(frame, (head_pixel_x - 15, head_pixel_y), (head_pixel_x + 15, head_pixel_y), color, 2)
    cv2.line(frame, (head_pixel_x, head_pixel_y - 15), (head_pixel_x, head_pixel_y + 15), color, 2)
    
    # Draw circle
    cv2.circle(frame, (head_pixel_x, head_pixel_y), 8, color, -1)
    cv2.circle(frame, (head_pixel_x, head_pixel_y), 10, (255, 255, 255), 2)
    
    # Draw trail
    if head_trail and len(head_trail) > 1:
        for i in range(len(head_trail) - 1):
            pt1 = (int(head_trail[i][0] * width), int(head_trail[i][1] * height))
            pt2 = (int(head_trail[i+1][0] * width), int(head_trail[i+1][1] * height))
            alpha = (i + 1) / len(head_trail)
            thickness = max(1, int(2 * alpha))
            cv2.line(frame, pt1, pt2, color, thickness)
    
    # Overlay heatmap if provided
    if heatmap_overlay is not None:
        # Blend heatmap with frame
        frame = cv2.addWeighted(frame, 0.7, heatmap_overlay, 0.3, 0)
    
    # Add label
    label = f"Head: ({head_x:.3f}, {head_y:.3f})"
    cv2.putText(frame, label, (head_pixel_x - 80, head_pixel_y - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return frame
