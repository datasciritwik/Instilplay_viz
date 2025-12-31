"""
Ultra-advanced kinematics visualizations.
Cutting-edge analysis tools for professional biomechanics analysis.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_3d_rotation_animation(kin_data, metadata):
    """
    3D animated visualization of body segment rotations.
    
    Args:
        kin_data: Kinematics analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure with animation
    """
    velocities = kin_data.get("velocities", {})
    hip_vel = velocities.get("hip", [])
    torso_vel = velocities.get("torso", [])
    shoulder_vel = velocities.get("shoulder", [])
    
    fps = metadata.get("fps", 24.0)
    
    if not hip_vel:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="3D Rotation Animation", height=600)
        return fig
    
    # Create 3D trajectory
    frames_data = []
    time_points = np.linspace(0, len(hip_vel)-1, len(hip_vel))
    
    # Normalize velocities for 3D coordinates
    max_vel = max(max(hip_vel), max(torso_vel), max(shoulder_vel))
    
    fig = go.Figure()
    
    # Add 3D scatter for each segment
    fig.add_trace(go.Scatter3d(
        x=time_points,
        y=[v/max_vel for v in hip_vel],
        z=[0]*len(hip_vel),
        mode='lines+markers',
        name='Hip',
        line=dict(color='orange', width=4),
        marker=dict(size=3)
    ))
    
    fig.add_trace(go.Scatter3d(
        x=time_points,
        y=[v/max_vel for v in torso_vel],
        z=[1]*len(torso_vel),
        mode='lines+markers',
        name='Torso',
        line=dict(color='blue', width=4),
        marker=dict(size=3)
    ))
    
    fig.add_trace(go.Scatter3d(
        x=time_points,
        y=[v/max_vel for v in shoulder_vel],
        z=[2]*len(shoulder_vel),
        mode='lines+markers',
        name='Shoulder',
        line=dict(color='green', width=4),
        marker=dict(size=3)
    ))
    
    fig.update_layout(
        title="3D Rotation Trajectory - Kinematic Chain",
        scene=dict(
            xaxis_title="Time (frames)",
            yaxis_title="Normalized Velocity",
            zaxis_title="Segment Level",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        height=600
    )
    
    return fig

def plot_phase_portrait(kin_data, metadata):
    """
    Phase portrait showing velocity vs acceleration for each segment.
    
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
    
    fps = metadata.get("fps", 24.0)
    dt = 1.0 / fps
    
    if not hip_vel or len(hip_vel) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Phase Portrait", height=600)
        return fig
    
    # Calculate accelerations
    hip_acc = np.gradient(hip_vel, dt)
    torso_acc = np.gradient(torso_vel, dt)
    shoulder_acc = np.gradient(shoulder_vel, dt)
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Hip Phase Space", "Torso Phase Space", "Shoulder Phase Space"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Hip phase portrait
    fig.add_trace(
        go.Scatter(x=hip_vel, y=hip_acc, mode='lines+markers',
                   marker=dict(size=4, color=hip_vel, colorscale='Hot', showscale=False),
                   line=dict(color='orange', width=2),
                   name='Hip'),
        row=1, col=1
    )
    
    # Torso phase portrait
    fig.add_trace(
        go.Scatter(x=torso_vel, y=torso_acc, mode='lines+markers',
                   marker=dict(size=4, color=torso_vel, colorscale='Blues', showscale=False),
                   line=dict(color='blue', width=2),
                   name='Torso'),
        row=1, col=2
    )
    
    # Shoulder phase portrait
    fig.add_trace(
        go.Scatter(x=shoulder_vel, y=shoulder_acc, mode='lines+markers',
                   marker=dict(size=4, color=shoulder_vel, colorscale='Greens', showscale=False),
                   line=dict(color='green', width=2),
                   name='Shoulder'),
        row=1, col=3
    )
    
    fig.update_xaxes(title_text="Velocity", row=1, col=1)
    fig.update_xaxes(title_text="Velocity", row=1, col=2)
    fig.update_xaxes(title_text="Velocity", row=1, col=3)
    fig.update_yaxes(title_text="Acceleration", row=1, col=1)
    
    fig.update_layout(
        title="Phase Portrait Analysis - Velocity vs Acceleration",
        height=500,
        showlegend=False
    )
    
    return fig

def plot_power_flow_diagram(kin_data, metadata):
    """
    Sankey diagram showing power flow through kinematic chain.
    
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
    
    # Calculate total energy (proportional to velocity squared integrated over time)
    hip_energy = sum([v**2 for v in hip_vel]) if hip_vel else 0
    torso_energy = sum([v**2 for v in torso_vel]) if torso_vel else 0
    shoulder_energy = sum([v**2 for v in shoulder_vel]) if shoulder_vel else 0
    
    # Estimate transfers (simplified model)
    hip_to_torso = min(hip_energy, torso_energy) * 0.8
    torso_to_shoulder = min(torso_energy, shoulder_energy) * 0.8
    
    # Energy loss
    hip_loss = hip_energy - hip_to_torso
    torso_loss = torso_energy - torso_to_shoulder
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=["Hip Rotation", "Torso Rotation", "Shoulder Rotation", 
                   "Energy Loss (Hip)", "Energy Loss (Torso)", "Final Output"],
            color=["orange", "blue", "green", "lightgray", "lightgray", "gold"]
        ),
        link=dict(
            source=[0, 0, 1, 1, 2],
            target=[1, 3, 2, 4, 5],
            value=[hip_to_torso, hip_loss, torso_to_shoulder, torso_loss, shoulder_energy],
            color=["rgba(255,165,0,0.4)", "rgba(200,200,200,0.2)", 
                   "rgba(0,0,255,0.4)", "rgba(200,200,200,0.2)", 
                   "rgba(0,255,0,0.4)"]
        )
    )])
    
    fig.update_layout(
        title="Power Flow Through Kinematic Chain",
        font=dict(size=12),
        height=500
    )
    
    return fig

def plot_comparative_timing_heatmap(kin_data, metadata):
    """
    Heatmap comparing actual vs ideal timing patterns.
    
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
    
    # Actual delays
    actual_delay1 = (torso_time - hip_time) * 1000
    actual_delay2 = (shoulder_time - torso_time) * 1000
    
    # Ideal pattern
    ideal_delay = 30  # ms
    
    # Create comparison matrix
    segments = ['Hip Peak', 'Torso Peak', 'Shoulder Peak']
    
    # Timing matrix (relative to hip peak)
    actual_times = [0, actual_delay1, actual_delay1 + actual_delay2]
    ideal_times = [0, ideal_delay, ideal_delay * 2]
    
    # Create heatmap data
    z_data = [
        [actual_times[0], ideal_times[0], abs(actual_times[0] - ideal_times[0])],
        [actual_times[1], ideal_times[1], abs(actual_times[1] - ideal_times[1])],
        [actual_times[2], ideal_times[2], abs(actual_times[2] - ideal_times[2])]
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=['Actual (ms)', 'Ideal (ms)', 'Deviation (ms)'],
        y=segments,
        colorscale='RdYlGn_r',
        text=[[f'{v:.1f}' for v in row] for row in z_data],
        texttemplate='%{text}',
        textfont={"size": 14},
        colorbar=dict(title="Time (ms)")
    ))
    
    fig.update_layout(
        title="Timing Comparison: Actual vs Ideal",
        height=400
    )
    
    return fig

def plot_efficiency_score_breakdown(kin_data):
    """
    Detailed breakdown of efficiency score components.
    
    Args:
        kin_data: Kinematics analysis data dict
    
    Returns:
        Plotly figure
    """
    score = kin_data.get("score", 0.0)
    error = kin_data.get("error_sec", 0.0)
    peaks = kin_data.get("peaks", {})
    
    hip_time = peaks.get("hip_time_sec", 0)
    torso_time = peaks.get("torso_time_sec", 0)
    shoulder_time = peaks.get("shoulder_time_sec", 0)
    
    # Calculate sub-scores
    delay1 = (torso_time - hip_time) * 1000
    delay2 = (shoulder_time - torso_time) * 1000
    
    ideal = 30
    timing_score1 = 100 - min(100, abs(delay1 - ideal) * 3)
    timing_score2 = 100 - min(100, abs(delay2 - ideal) * 3)
    consistency_score = 100 - abs(delay1 - delay2)
    
    categories = ['Overall Score', 'Hip→Torso Timing', 'Torso→Shoulder Timing', 
                  'Consistency', 'Sequencing Quality']
    values = [score, timing_score1, timing_score2, consistency_score, score]
    
    fig = go.Figure()
    
    fig.add_trace(go.Barpolar(
        r=values,
        theta=categories,
        marker=dict(
            color=values,
            colorscale='Viridis',
            showscale=True,
            cmin=0,
            cmax=100,
            colorbar=dict(title="Score")
        ),
        opacity=0.8
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        title="Efficiency Score Breakdown",
        height=500
    )
    
    return fig
