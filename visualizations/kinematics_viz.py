"""
Kinematics visualization functions.
Creates interactive charts for kinematic sequencing analysis.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_angular_velocity_timeline(kin_data, metadata):
    """
    Plot angular velocities of all three segments.
    
    Args:
        kin_data: Kinematics analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    velocities = kin_data.get("velocities", {})
    hip_vel = velocities.get("hip", [])
    torso_vel = velocities.get("torso", [])
    shoulder_vel = velocities.get("shoulder", [])
    
    peaks = kin_data.get("peaks", {})
    hip_frame = peaks.get("hip_frame", 0)
    torso_frame = peaks.get("torso_frame", 0)
    shoulder_frame = peaks.get("shoulder_frame", 0)
    
    fps = metadata.get("fps", 24.0)
    
    if not hip_vel:
        fig = go.Figure()
        fig.add_annotation(
            text="No velocity data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Angular Velocity Timeline", height=500)
        return fig
    
    frames = list(range(len(hip_vel)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Hip velocity
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=hip_vel,
        mode='lines',
        name='Hip',
        line=dict(color='orange', width=3)
    ))
    
    # Torso velocity
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=torso_vel,
        mode='lines',
        name='Torso',
        line=dict(color='blue', width=3)
    ))
    
    # Shoulder velocity
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=shoulder_vel,
        mode='lines',
        name='Shoulder',
        line=dict(color='green', width=3)
    ))
    
    # Mark peaks
    fig.add_vline(x=hip_frame/fps, line_dash="dash", line_color="orange",
                  annotation_text="Hip Peak")
    fig.add_vline(x=torso_frame/fps, line_dash="dash", line_color="blue",
                  annotation_text="Torso Peak")
    fig.add_vline(x=shoulder_frame/fps, line_dash="dash", line_color="green",
                  annotation_text="Shoulder Peak")
    
    fig.update_layout(
        title="Angular Velocity Timeline - Kinematic Sequencing",
        xaxis_title="Time (seconds)",
        yaxis_title="Angular Velocity (rad/s)",
        hovermode='x unified',
        height=500,
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig

def plot_sequencing_waterfall(kin_data, metadata):
    """
    Waterfall chart showing cascade of peak velocities.
    
    Args:
        kin_data: Kinematics analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    peaks = kin_data.get("peaks", {})
    hip_time = peaks.get("hip_time_sec", 0)
    torso_time = peaks.get("torso_time_sec", 0)
    shoulder_time = peaks.get("shoulder_time_sec", 0)
    
    velocities = kin_data.get("velocities", {})
    hip_vel = velocities.get("hip", [])
    torso_vel = velocities.get("torso", [])
    shoulder_vel = velocities.get("shoulder", [])
    
    hip_peak = max(hip_vel) if hip_vel else 0
    torso_peak = max(torso_vel) if torso_vel else 0
    shoulder_peak = max(shoulder_vel) if shoulder_vel else 0
    
    fig = go.Figure()
    
    # Create waterfall effect
    fig.add_trace(go.Scatter(
        x=[hip_time, torso_time, shoulder_time],
        y=[hip_peak, torso_peak, shoulder_peak],
        mode='markers+lines',
        marker=dict(size=20, color=['orange', 'blue', 'green']),
        line=dict(color='gray', width=2, dash='dash'),
        name='Sequencing',
        text=['Hip', 'Torso', 'Shoulder'],
        textposition='top center'
    ))
    
    fig.update_layout(
        title="Kinematic Sequencing Waterfall",
        xaxis_title="Time (seconds)",
        yaxis_title="Peak Angular Velocity (rad/s)",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_timing_diagram(kin_data, metadata):
    """
    Bar chart showing delays between peaks.
    
    Args:
        kin_data: Kinematics analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    peaks = kin_data.get("peaks", {})
    hip_time = peaks.get("hip_time_sec", 0)
    torso_time = peaks.get("torso_time_sec", 0)
    shoulder_time = peaks.get("shoulder_time_sec", 0)
    
    # Calculate delays
    delay1 = (torso_time - hip_time) * 1000  # Convert to ms
    delay2 = (shoulder_time - torso_time) * 1000
    
    ideal_delay = 30  # ms
    
    fig = go.Figure()
    
    # Actual delays
    fig.add_trace(go.Bar(
        x=['Hip → Torso', 'Torso → Shoulder'],
        y=[delay1, delay2],
        marker=dict(
            color=['orange' if abs(delay1 - ideal_delay) < 10 else 'red',
                   'green' if abs(delay2 - ideal_delay) < 10 else 'red']
        ),
        text=[f'{delay1:.1f}ms', f'{delay2:.1f}ms'],
        textposition='outside',
        name='Actual Delay'
    ))
    
    # Ideal delay line
    fig.add_hline(y=ideal_delay, line_dash="dash", line_color="green",
                  annotation_text="Ideal (30ms)")
    
    fig.update_layout(
        title="Timing Between Segment Peaks",
        xaxis_title="Segment Transition",
        yaxis_title="Delay (milliseconds)",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_sequencing_score_gauge(kin_data):
    """
    Display sequencing score as a gauge.
    
    Args:
        kin_data: Kinematics analysis data dict
    
    Returns:
        Plotly figure
    """
    score = kin_data.get("score", 0.0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={'text': "Kinematic Sequencing Score"},
        delta={'reference': 80, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "lightcoral"},
                {'range': [60, 80], 'color': "lightyellow"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=400)
    
    return fig

def plot_velocity_comparison(kin_data):
    """
    Side-by-side comparison of peak velocities.
    
    Args:
        kin_data: Kinematics analysis data dict
    
    Returns:
        Plotly figure
    """
    velocities = kin_data.get("velocities", {})
    hip_vel = velocities.get("hip", [])
    torso_vel = velocities.get("torso", [])
    shoulder_vel = velocities.get("shoulder", [])
    
    hip_peak = max(hip_vel) if hip_vel else 0
    torso_peak = max(torso_vel) if torso_vel else 0
    shoulder_peak = max(shoulder_vel) if shoulder_vel else 0
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Hip', 'Torso', 'Shoulder'],
        y=[hip_peak, torso_peak, shoulder_peak],
        marker=dict(color=['orange', 'blue', 'green']),
        text=[f'{hip_peak:.3f}', f'{torso_peak:.3f}', f'{shoulder_peak:.3f}'],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Peak Angular Velocities by Segment",
        xaxis_title="Body Segment",
        yaxis_title="Peak Velocity (rad/s)",
        height=400,
        showlegend=False
    )
    
    return fig
