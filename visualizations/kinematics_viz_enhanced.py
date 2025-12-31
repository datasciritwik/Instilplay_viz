"""
Enhanced kinematics visualizations.
Advanced analysis functions for kinematic sequencing.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_sequencing_zones(kin_data, metadata):
    """
    Plot velocity timeline with color-coded sequencing zones.
    
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
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Sequencing Zones", height=500)
        return fig
    
    frames = list(range(len(hip_vel)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Add zone backgrounds
    fig.add_vrect(x0=0, x1=hip_frame/fps, fillcolor="rgba(255, 165, 0, 0.1)",
                  layer="below", line_width=0,
                  annotation_text="Hip Dominant", annotation_position="top left")
    fig.add_vrect(x0=hip_frame/fps, x1=torso_frame/fps, fillcolor="rgba(0, 0, 255, 0.1)",
                  layer="below", line_width=0,
                  annotation_text="Torso Dominant", annotation_position="top left")
    fig.add_vrect(x0=torso_frame/fps, x1=shoulder_frame/fps, fillcolor="rgba(0, 255, 0, 0.1)",
                  layer="below", line_width=0,
                  annotation_text="Shoulder Dominant", annotation_position="top left")
    
    # Plot velocities
    fig.add_trace(go.Scatter(x=time_sec, y=hip_vel, mode='lines',
                             name='Hip', line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=time_sec, y=torso_vel, mode='lines',
                             name='Torso', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=time_sec, y=shoulder_vel, mode='lines',
                             name='Shoulder', line=dict(color='green', width=2)))
    
    fig.update_layout(
        title="Sequencing Zones - Dominant Segment by Phase",
        xaxis_title="Time (seconds)",
        yaxis_title="Angular Velocity (rad/s)",
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_energy_transfer_efficiency(kin_data):
    """
    Visualize energy transfer efficiency through segments.
    
    Args:
        kin_data: Kinematics analysis data dict
    
    Returns:
        Plotly figure
    """
    velocities = kin_data.get("velocities", {})
    hip_vel = velocities.get("hip", [])
    torso_vel = velocities.get("torso", [])
    shoulder_vel = velocities.get("shoulder", [])
    
    # Calculate energy (proportional to velocity squared)
    hip_energy = sum([v**2 for v in hip_vel]) if hip_vel else 0
    torso_energy = sum([v**2 for v in torso_vel]) if torso_vel else 0
    shoulder_energy = sum([v**2 for v in shoulder_vel]) if shoulder_vel else 0
    
    # Normalize
    total = hip_energy + torso_energy + shoulder_energy
    if total > 0:
        hip_pct = (hip_energy / total) * 100
        torso_pct = (torso_energy / total) * 100
        shoulder_pct = (shoulder_energy / total) * 100
    else:
        hip_pct = torso_pct = shoulder_pct = 0
    
    fig = go.Figure()
    
    # Sankey-style flow diagram
    fig.add_trace(go.Funnel(
        y=['Hip', 'Torso', 'Shoulder'],
        x=[hip_pct, torso_pct, shoulder_pct],
        textinfo="value+percent initial",
        marker=dict(color=['orange', 'blue', 'green'])
    ))
    
    fig.update_layout(
        title="Energy Distribution Across Segments",
        height=400
    )
    
    return fig

def plot_timing_deviation(kin_data, metadata):
    """
    Analyze deviation from ideal timing.
    
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
    
    ideal_delay = 0.03  # 30ms
    
    # Calculate actual delays
    delay1 = torso_time - hip_time
    delay2 = shoulder_time - torso_time
    
    # Calculate deviations
    dev1 = (delay1 - ideal_delay) * 1000  # ms
    dev2 = (delay2 - ideal_delay) * 1000
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Hip → Torso', 'Torso → Shoulder'],
        y=[dev1, dev2],
        marker=dict(
            color=['green' if abs(dev1) < 10 else 'orange' if abs(dev1) < 20 else 'red',
                   'green' if abs(dev2) < 10 else 'orange' if abs(dev2) < 20 else 'red']
        ),
        text=[f'{dev1:+.1f}ms', f'{dev2:+.1f}ms'],
        textposition='outside'
    ))
    
    # Add acceptable range
    fig.add_hrect(y0=-10, y1=10, fillcolor="green", opacity=0.1,
                  annotation_text="Excellent (±10ms)", annotation_position="right")
    fig.add_hrect(y0=-20, y1=-10, fillcolor="yellow", opacity=0.1)
    fig.add_hrect(y0=10, y1=20, fillcolor="yellow", opacity=0.1)
    
    fig.update_layout(
        title="Timing Deviation from Ideal (30ms)",
        xaxis_title="Segment Transition",
        yaxis_title="Deviation (milliseconds)",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_benchmark_comparison_kin(kin_data):
    """
    Compare sequencing score against benchmarks.
    
    Args:
        kin_data: Kinematics analysis data dict
    
    Returns:
        Plotly figure
    """
    score = kin_data.get("score", 0.0)
    
    benchmarks = {
        'Elite': (90, 100),
        'Excellent': (80, 90),
        'Good': (70, 80),
        'Developing': (60, 70),
        'Poor': (0, 60)
    }
    
    fig = go.Figure()
    
    categories = list(benchmarks.keys())
    ranges = [v[1] - v[0] for v in benchmarks.values()]
    colors = ['gold', 'lightgreen', 'lightblue', 'lightyellow', 'lightcoral']
    
    fig.add_trace(go.Bar(
        y=categories,
        x=ranges,
        base=[v[0] for v in benchmarks.values()],
        orientation='h',
        marker=dict(color=colors),
        name='Benchmark Ranges'
    ))
    
    fig.add_vline(x=score, line_color="red", line_width=3,
                  annotation_text=f"Your Score: {score:.1f}",
                  annotation_position="top")
    
    fig.update_layout(
        title="Sequencing Score vs Benchmarks",
        xaxis_title="Score (0-100)",
        yaxis_title="Category",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_coordination_index(kin_data, metadata):
    """
    Overall coordination quality metric.
    
    Args:
        kin_data: Kinematics analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    score = kin_data.get("score", 0.0)
    error = kin_data.get("error_sec", 0.0)
    
    peaks = kin_data.get("peaks", {})
    hip_time = peaks.get("hip_time_sec", 0)
    torso_time = peaks.get("torso_time_sec", 0)
    shoulder_time = peaks.get("shoulder_time_sec", 0)
    
    # Calculate coordination metrics
    delay1 = (torso_time - hip_time) * 1000
    delay2 = (shoulder_time - torso_time) * 1000
    
    consistency = 100 - abs(delay1 - delay2)  # How consistent are the delays
    timing_accuracy = 100 - (error * 1000)  # Overall timing accuracy
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[score, consistency, timing_accuracy],
        theta=['Overall Score', 'Consistency', 'Timing Accuracy'],
        fill='toself',
        fillcolor='rgba(0, 100, 200, 0.3)',
        line=dict(color='darkblue', width=2),
        name='Coordination'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        title="Coordination Index",
        height=450,
        showlegend=False
    )
    
    return fig

def plot_segment_comparison(kin_data, metadata):
    """
    Detailed comparison of all three segments.
    
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
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Hip Angular Velocity", "Torso Angular Velocity", "Shoulder Angular Velocity"),
        vertical_spacing=0.1
    )
    
    frames = list(range(len(hip_vel)))
    fps = metadata.get("fps", 24.0)
    time_sec = [f / fps for f in frames]
    
    # Hip
    fig.add_trace(
        go.Scatter(x=time_sec, y=hip_vel, mode='lines', name='Hip',
                   line=dict(color='orange', width=2),
                   fill='tozeroy', fillcolor='rgba(255, 165, 0, 0.2)'),
        row=1, col=1
    )
    
    # Torso
    fig.add_trace(
        go.Scatter(x=time_sec, y=torso_vel, mode='lines', name='Torso',
                   line=dict(color='blue', width=2),
                   fill='tozeroy', fillcolor='rgba(0, 0, 255, 0.2)'),
        row=2, col=1
    )
    
    # Shoulder
    fig.add_trace(
        go.Scatter(x=time_sec, y=shoulder_vel, mode='lines', name='Shoulder',
                   line=dict(color='green', width=2),
                   fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.2)'),
        row=3, col=1
    )
    
    fig.update_xaxes(title_text="Time (seconds)", row=3, col=1)
    fig.update_yaxes(title_text="Velocity", row=1, col=1)
    fig.update_yaxes(title_text="Velocity", row=2, col=1)
    fig.update_yaxes(title_text="Velocity", row=3, col=1)
    
    fig.update_layout(height=700, showlegend=False, hovermode='x unified')
    
    return fig
