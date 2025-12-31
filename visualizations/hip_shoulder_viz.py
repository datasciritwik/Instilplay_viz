"""
Hip-Shoulder Separation visualization functions.
Creates interactive charts for hip-shoulder angle analysis.
"""
import plotly.graph_objects as go
import numpy as np

def plot_separation_angle(hs_data, metadata):
    """
    Plot hip-shoulder separation angle over time.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    angle_series = hs_data.get("angle_series", [])
    key_frames = hs_data.get("key_frames", {})
    downswing_start = key_frames.get("downswing_start", 0)
    peak_frame = key_frames.get("peak_frame", 0)
    downswing_end = key_frames.get("downswing_end", 0)
    fps = metadata.get("fps", 24.0)
    
    if not angle_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No hip-shoulder data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Hip-Shoulder Separation Angle", height=500)
        return fig
    
    frames = list(range(len(angle_series)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Add angle line
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=angle_series,
        mode='lines',
        name='Separation Angle',
        line=dict(color='steelblue', width=3)
    ))
    
    # Mark downswing start
    fig.add_vline(
        x=downswing_start/fps,
        line_dash="dash",
        line_color="green",
        annotation_text="Downswing Start",
        annotation_position="top"
    )
    
    # Mark peak separation
    fig.add_vline(
        x=peak_frame/fps,
        line_dash="dash",
        line_color="red",
        annotation_text="Peak Separation",
        annotation_position="top"
    )
    
    # Mark downswing end
    fig.add_vline(
        x=downswing_end/fps,
        line_dash="dash",
        line_color="purple",
        annotation_text="Downswing End",
        annotation_position="top"
    )
    
    # Highlight downswing window
    fig.add_vrect(
        x0=downswing_start/fps,
        x1=downswing_end/fps,
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0,
        annotation_text="Downswing Window",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title="Hip-Shoulder Separation Angle Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Angle (degrees)",
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_separation_rate(hs_data, metadata):
    """
    Plot rate of separation (angular velocity).
    
    Args:
        hs_data: Hip-shoulder analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    angle_series = hs_data.get("angle_series", [])
    key_frames = hs_data.get("key_frames", {})
    downswing_start = key_frames.get("downswing_start", 0)
    downswing_end = key_frames.get("downswing_end", 0)
    fps = metadata.get("fps", 24.0)
    
    if not angle_series or len(angle_series) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for rate calculation",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Rate of Separation", height=400)
        return fig
    
    # Calculate angular velocity
    angle_arr = np.array(angle_series)
    angular_vel = np.gradient(angle_arr) * fps  # deg/sec
    
    frames = list(range(len(angular_vel)))
    
    fig = go.Figure()
    
    # Add rate line
    fig.add_trace(go.Scatter(
        x=frames,
        y=angular_vel,
        mode='lines',
        name='Angular Velocity',
        line=dict(color='darkgreen', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 128, 0, 0.2)'
    ))
    
    # Mark downswing window
    fig.add_vrect(
        x0=downswing_start,
        x1=downswing_end,
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0
    )
    
    fig.update_layout(
        title="Rate of Hip-Shoulder Separation",
        xaxis_title="Frame",
        yaxis_title="Angular Velocity (deg/sec)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_separation_phases(hs_data):
    """
    Plot separation in different phases as bar chart.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
    
    Returns:
        Plotly figure
    """
    angle_series = hs_data.get("angle_series", [])
    key_frames = hs_data.get("key_frames", {})
    downswing_start = key_frames.get("downswing_start", 0)
    peak_frame = key_frames.get("peak_frame", 0)
    downswing_end = key_frames.get("downswing_end", 0)
    
    if not angle_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Separation by Phase", height=400)
        return fig
    
    # Calculate average separation in each phase
    pre_downswing = np.mean(angle_series[:downswing_start]) if downswing_start > 0 else 0
    during_downswing = np.mean(angle_series[downswing_start:downswing_end+1])
    post_downswing = np.mean(angle_series[downswing_end:]) if downswing_end < len(angle_series)-1 else 0
    peak_sep = angle_series[peak_frame] if peak_frame < len(angle_series) else 0
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Pre-Downswing', 'During Downswing', 'Peak', 'Post-Downswing'],
        y=[pre_downswing, during_downswing, peak_sep, post_downswing],
        marker=dict(
            color=[pre_downswing, during_downswing, peak_sep, post_downswing],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Angle (deg)")
        ),
        text=[f'{v:.1f}°' for v in [pre_downswing, during_downswing, peak_sep, post_downswing]],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Average Separation Angle by Phase",
        xaxis_title="Phase",
        yaxis_title="Angle (degrees)",
        height=400,
        showlegend=False
    )
    
    return fig
