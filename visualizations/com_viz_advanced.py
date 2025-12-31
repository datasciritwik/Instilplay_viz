"""
Advanced COM (Center of Mass) visualizations.
Professional-grade analysis tools for COM movement patterns.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_com_velocity_analysis(com_data, metadata):
    """
    Analyze COM velocity and acceleration.
    
    Args:
        com_data: COM analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    fps = metadata.get("fps", 24.0)
    dt = 1.0 / fps
    
    if not com_x_series or len(com_x_series) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="COM Velocity Analysis", height=600)
        return fig
    
    # x_positions are already in com_x_series
    x_positions = com_x_series
    
    # Calculate velocity and acceleration
    velocity = np.gradient(x_positions, dt)
    acceleration = np.gradient(velocity, dt)
    
    frames = list(range(len(x_positions)))
    time_sec = [f / fps for f in frames]
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Position", "Velocity", "Acceleration"),
        vertical_spacing=0.1
    )
    
    # Position
    fig.add_trace(
        go.Scatter(x=time_sec, y=x_positions, mode='lines', name='Position',
                   line=dict(color='steelblue', width=2),
                   fill='tozeroy', fillcolor='rgba(70, 130, 180, 0.2)'),
        row=1, col=1
    )
    
    # Velocity
    fig.add_trace(
        go.Scatter(x=time_sec, y=velocity, mode='lines', name='Velocity',
                   line=dict(color='orange', width=2),
                   fill='tozeroy', fillcolor='rgba(255, 165, 0, 0.2)'),
        row=2, col=1
    )
    
    # Acceleration
    fig.add_trace(
        go.Scatter(x=time_sec, y=acceleration, mode='lines', name='Acceleration',
                   line=dict(color='red', width=2),
                   fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)'),
        row=3, col=1
    )
    
    fig.update_xaxes(title_text="Time (seconds)", row=3, col=1)
    fig.update_yaxes(title_text="Position", row=1, col=1)
    fig.update_yaxes(title_text="Velocity", row=2, col=1)
    fig.update_yaxes(title_text="Acceleration", row=3, col=1)
    
    fig.update_layout(height=700, showlegend=False, hovermode='x unified',
                      title="COM Kinematics: Position, Velocity, Acceleration")
    
    return fig

def plot_com_phase_diagram(com_data, metadata):
    """
    Phase space diagram showing position vs velocity.
    
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
    dt = 1.0 / fps
    
    if not com_x_series or len(com_x_series) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="COM Phase Diagram", height=500)
        return fig
    
    x_positions = com_x_series
    velocity = np.gradient(x_positions, dt)
    
    # Color by time
    frames = list(range(len(x_positions)))
    
    fig = go.Figure()
    
    # Main trajectory
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=velocity,
        mode='lines+markers',
        marker=dict(size=4, color=frames, colorscale='Viridis', showscale=True,
                    colorbar=dict(title="Frame")),
        line=dict(color='gray', width=1),
        name='Trajectory'
    ))
    
    # Mark stance
    if stance_frame < len(x_positions):
        fig.add_trace(go.Scatter(
            x=[x_positions[stance_frame]],
            y=[velocity[stance_frame]],
            mode='markers',
            marker=dict(size=15, color='green', symbol='star'),
            name='Stance'
        ))
    
    # Mark impact
    if impact_frame < len(x_positions):
        fig.add_trace(go.Scatter(
            x=[x_positions[impact_frame]],
            y=[velocity[impact_frame]],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='Impact'
        ))
    
    fig.update_layout(
        title="COM Phase Space - Position vs Velocity",
        xaxis_title="Position (normalized)",
        yaxis_title="Velocity (units/s)",
        height=500,
        hovermode='closest'
    )
    
    return fig

def plot_com_stability_index(com_data, metadata):
    """
    Calculate and visualize COM stability over time.
    
    Args:
        com_data: COM analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    fps = metadata.get("fps", 24.0)
    
    if not com_x_series or len(com_x_series) < 10:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="COM Stability Index", height=400)
        return fig
    
    x_positions = com_x_series
    
    # Calculate rolling stability (inverse of rolling std deviation)
    window = 10
    stability_scores = []
    
    for i in range(len(x_positions)):
        start = max(0, i - window // 2)
        end = min(len(x_positions), i + window // 2)
        window_data = x_positions[start:end]
        
        if len(window_data) > 1:
            std = np.std(window_data)
            # Stability = 100 / (1 + std)
            stability = 100 / (1 + std * 100)
        else:
            stability = 50
        
        stability_scores.append(stability)
    
    frames = list(range(len(stability_scores)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Stability score
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=stability_scores,
        mode='lines',
        line=dict(color='purple', width=3),
        fill='tozeroy',
        fillcolor='rgba(128, 0, 128, 0.2)',
        name='Stability Index'
    ))
    
    # Add threshold lines
    fig.add_hline(y=80, line_dash="dash", line_color="green",
                  annotation_text="Excellent (>80)")
    fig.add_hline(y=60, line_dash="dash", line_color="orange",
                  annotation_text="Good (>60)")
    
    fig.update_layout(
        title="COM Stability Index Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Stability Score (0-100)",
        yaxis=dict(range=[0, 100]),
        height=400,
        hovermode='x unified'
    )
    
    return fig

def plot_com_movement_efficiency(com_data, metadata):
    """
    Analyze efficiency of COM movement.
    
    Args:
        com_data: COM analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    
    if not com_x_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Movement Efficiency", height=400)
        return fig
    
    x_positions = com_x_series
    
    # Calculate total path length
    total_distance = sum(abs(x_positions[i+1] - x_positions[i]) 
                        for i in range(len(x_positions)-1))
    
    # Calculate direct distance (stance to impact)
    if stance_frame < len(x_positions) and impact_frame < len(x_positions):
        direct_distance = abs(x_positions[impact_frame] - x_positions[stance_frame])
        efficiency = (direct_distance / total_distance * 100) if total_distance > 0 else 0
    else:
        efficiency = 0
        direct_distance = 0
    
    # Metrics
    metrics = {
        'Total Path': total_distance,
        'Direct Path': direct_distance,
        'Efficiency %': efficiency,
        'Wasted Movement': total_distance - direct_distance
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker=dict(
            color=['steelblue', 'green', 'gold', 'red'],
            line=dict(color='black', width=2)
        ),
        text=[f'{v:.3f}' for v in metrics.values()],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f"COM Movement Efficiency: {efficiency:.1f}%",
        yaxis_title="Value",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_com_3d_trajectory(com_data, metadata):
    """
    3D visualization of COM movement with time dimension.
    
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
    
    if not com_x_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="3D COM Trajectory", height=600)
        return fig
    
    x_positions = com_x_series
    # Create synthetic y-axis based on velocity for 3D effect
    dt = 1.0 / fps
    velocity = np.gradient(x_positions, dt)
    frames_list = list(range(len(com_x_series)))
    time_sec = [f / fps for f in frames_list]
    
    fig = go.Figure()
    
    # Main trajectory
    fig.add_trace(go.Scatter3d(
        x=x_positions,
        y=velocity,  # Use velocity as y-axis
        z=time_sec,
        mode='lines+markers',
        marker=dict(size=3, color=time_sec, colorscale='Plasma', showscale=True,
                    colorbar=dict(title="Time (s)")),
        line=dict(color='steelblue', width=3),
        name='COM Path'
    ))
    
    # Mark stance
    if stance_frame < len(com_x_series):
        fig.add_trace(go.Scatter3d(
            x=[x_positions[stance_frame]],
            y=[velocity[stance_frame]],
            z=[time_sec[stance_frame]],
            mode='markers',
            marker=dict(size=10, color='green', symbol='diamond'),
            name='Stance'
        ))
    
    # Mark impact
    if impact_frame < len(com_x_series):
        fig.add_trace(go.Scatter3d(
            x=[x_positions[impact_frame]],
            y=[velocity[impact_frame]],
            z=[time_sec[impact_frame]],
            mode='markers',
            marker=dict(size=10, color='red', symbol='diamond'),
            name='Impact'
        ))
    
    fig.update_layout(
        title="3D COM Trajectory - Position, Velocity, Time",
        scene=dict(
            xaxis_title="X Position",
            yaxis_title="Velocity",
            zaxis_title="Time (seconds)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        height=600
    )
    
    return fig

def plot_com_benchmark_comparison(com_data):
    """
    Compare COM movement against benchmarks.
    
    Args:
        com_data: COM analysis data dict
    
    Returns:
        Plotly figure
    """
    com_x_series = com_data.get("com_x_series", [])
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    
    if not com_x_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="COM Benchmarks", height=400)
        return fig
    
    x_positions = com_x_series
    
    # Calculate lateral movement
    if stance_frame < len(x_positions) and impact_frame < len(x_positions):
        lateral_movement = abs(x_positions[impact_frame] - x_positions[stance_frame])
    else:
        lateral_movement = 0
    
    # Benchmarks (normalized units)
    benchmarks = {
        'Elite': (0.15, 0.25),
        'Professional': (0.25, 0.35),
        'Good': (0.35, 0.45),
        'Developing': (0.45, 0.60),
        'Needs Work': (0.60, 1.0)
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
    
    fig.add_vline(x=lateral_movement, line_color="red", line_width=3,
                  annotation_text=f"Your Movement: {lateral_movement:.3f}",
                  annotation_position="top")
    
    fig.update_layout(
        title="Lateral COM Movement vs Benchmarks",
        xaxis_title="Lateral Movement (normalized)",
        yaxis_title="Category",
        height=400,
        showlegend=False
    )
    
    return fig

