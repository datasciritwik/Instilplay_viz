"""
COM (Center of Mass) visualization functions.
Creates interactive charts using Plotly for COM analysis.
"""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots

def plot_com_trajectory(com_data, metadata):
    """
    Plot COM trajectory over time with stance/impact markers.
    
    Args:
        com_data: COM analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    # Create time axis
    frames = list(range(len(com_x_series)))
    time_sec = [f / fps for f in frames]
    
    # Create figure
    fig = go.Figure()
    
    # Add COM trajectory line with phase coloring
    # Pre-stance
    fig.add_trace(go.Scatter(
        x=time_sec[:stance_frame+1],
        y=com_x_series[:stance_frame+1],
        mode='lines',
        name='Pre-Stance',
        line=dict(color='blue', width=3)
    ))
    
    # Stance to impact
    if impact_frame > stance_frame:
        fig.add_trace(go.Scatter(
            x=time_sec[stance_frame:impact_frame+1],
            y=com_x_series[stance_frame:impact_frame+1],
            mode='lines',
            name='Stance to Impact',
            line=dict(color='green', width=3)
        ))
    
    # Post-impact
    if impact_frame < len(com_x_series) - 1:
        fig.add_trace(go.Scatter(
            x=time_sec[impact_frame:],
            y=com_x_series[impact_frame:],
            mode='lines',
            name='Post-Impact',
            line=dict(color='orange', width=3)
        ))
    
    # Add stance marker
    fig.add_vline(
        x=stance_frame/fps,
        line_dash="dash",
        line_color="red",
        annotation_text="Stance",
        annotation_position="top"
    )
    
    # Add impact marker
    fig.add_vline(
        x=impact_frame/fps,
        line_dash="dash",
        line_color="purple",
        annotation_text="Impact",
        annotation_position="top"
    )
    
    fig.update_layout(
        title="COM Lateral Position Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="COM Position (normalized)",
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_movement_scores(pose_data, com_data):
    """
    Plot hip movement scores showing acceleration/deceleration.
    
    Args:
        pose_data: List of pose data dicts
        com_data: COM analysis data dict
    
    Returns:
        Plotly figure
    """
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    
    # Calculate movement scores
    movement_scores = [0.0]
    for i in range(1, len(pose_data)):
        curr = pose_data[i]
        prev = pose_data[i-1]
        
        if not curr.get('landmarks') or not prev.get('landmarks'):
            movement_scores.append(0.0)
            continue
        
        curr_lm = curr['landmarks']
        prev_lm = prev['landmarks']
        
        # Hip movement (indices 23, 24)
        if len(curr_lm) > 24 and len(prev_lm) > 24:
            diff = (abs(curr_lm[23]['x'] - prev_lm[23]['x']) + 
                   abs(curr_lm[24]['x'] - prev_lm[24]['x']))
            movement_scores.append(diff)
        else:
            movement_scores.append(0.0)
    
    frames = list(range(len(movement_scores)))
    
    fig = go.Figure()
    
    # Add movement score line
    fig.add_trace(go.Scatter(
        x=frames,
        y=movement_scores,
        mode='lines',
        name='Hip Movement',
        line=dict(color='steelblue', width=2),
        fill='tozeroy',
        fillcolor='rgba(70, 130, 180, 0.3)'
    ))
    
    # Add stance marker
    fig.add_vline(
        x=stance_frame,
        line_dash="dash",
        line_color="red",
        annotation_text="Stance (Min Movement)",
        annotation_position="top"
    )
    
    # Add impact marker
    fig.add_vline(
        x=impact_frame,
        line_dash="dash",
        line_color="purple",
        annotation_text="Impact (Max Movement)",
        annotation_position="top"
    )
    
    fig.update_layout(
        title="Hip Movement Scores (Frame-to-Frame Change)",
        xaxis_title="Frame",
        yaxis_title="Movement Score",
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_com_components(pose_data, com_data):
    """
    Plot COM components breakdown (hip vs shoulder contribution).
    
    Args:
        pose_data: List of pose data dicts
        com_data: COM analysis data dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    
    # Calculate hip and shoulder midpoints
    hip_mid = []
    shoulder_mid = []
    
    for frame in pose_data:
        if frame.get('landmarks'):
            lm = frame['landmarks']
            if len(lm) > 24:
                # Hip midpoint (indices 23, 24)
                hip_mid.append((lm[23]['x'] + lm[24]['x']) / 2)
                # Shoulder midpoint (indices 11, 12)
                shoulder_mid.append((lm[11]['x'] + lm[12]['x']) / 2)
            else:
                hip_mid.append(None)
                shoulder_mid.append(None)
        else:
            hip_mid.append(None)
            shoulder_mid.append(None)
    
    frames = list(range(len(com_x_series)))
    
    fig = go.Figure()
    
    # Add hip midpoint (60% contribution)
    fig.add_trace(go.Scatter(
        x=frames,
        y=hip_mid,
        mode='lines',
        name='Hip Midpoint (60%)',
        line=dict(color='blue', width=2, dash='dot')
    ))
    
    # Add shoulder midpoint (40% contribution)
    fig.add_trace(go.Scatter(
        x=frames,
        y=shoulder_mid,
        mode='lines',
        name='Shoulder Midpoint (40%)',
        line=dict(color='orange', width=2, dash='dot')
    ))
    
    # Add combined COM (thicker line)
    fig.add_trace(go.Scatter(
        x=frames,
        y=com_x_series,
        mode='lines',
        name='Combined COM',
        line=dict(color='green', width=4)
    ))
    
    fig.update_layout(
        title="COM Components Breakdown",
        xaxis_title="Frame",
        yaxis_title="Position (normalized)",
        hovermode='x unified',
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def create_heatmap(com_data, metadata):
    """
    Create COM density heatmap showing concentration zones.
    
    Args:
        com_data: COM analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    
    # Create histogram of COM positions
    bins = 50
    hist, bin_edges = np.histogram(com_x_series, bins=bins, range=(0, 1))
    
    # Create heatmap-style visualization
    fig = go.Figure()
    
    # Add bar chart styled as heatmap
    fig.add_trace(go.Bar(
        x=bin_edges[:-1],
        y=hist,
        marker=dict(
            color=hist,
            colorscale='Hot',
            showscale=True,
            colorbar=dict(title="Density")
        ),
        name='COM Density'
    ))
    
    # Add stance position marker
    if stance_frame < len(com_x_series):
        stance_com = com_x_series[stance_frame]
        fig.add_vline(
            x=stance_com,
            line_dash="dash",
            line_color="blue",
            annotation_text="Stance",
            annotation_position="top"
        )
    
    # Add impact position marker
    if impact_frame < len(com_x_series):
        impact_com = com_x_series[impact_frame]
        fig.add_vline(
            x=impact_com,
            line_dash="dash",
            line_color="green",
            annotation_text="Impact",
            annotation_position="top"
        )
    
    fig.update_layout(
        title="COM Position Density Heatmap",
        xaxis_title="COM Position (normalized)",
        yaxis_title="Frequency (frames)",
        height=500,
        showlegend=False
    )
    
    return fig
