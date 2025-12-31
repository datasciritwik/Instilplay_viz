"""
Enhanced FBR visualizations.
Additional advanced analysis functions for foot plant biomechanics.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_braking_efficiency_zones(fbr_data, metadata):
    """
    Plot COM descent with braking efficiency zones.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_y_series = fbr_data.get("com_y_series", [])
    plant_frame = fbr_data.get("plant_frame", 0)
    lowest_frame = fbr_data.get("lowest_com_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    if not com_y_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Braking Efficiency Zones", height=500)
        return fig
    
    frames = list(range(len(com_y_series)))
    time_sec = [f / fps for f in frames]
    
    # Define efficiency zones based on COM change after plant
    plant_com = com_y_series[plant_frame] if plant_frame < len(com_y_series) else com_y_series[0]
    
    fig = go.Figure()
    
    # Add zone backgrounds
    fig.add_hrect(y0=plant_com, y1=plant_com + 0.01, fillcolor="rgba(0, 255, 0, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Excellent (<0.01)", annotation_position="right")
    fig.add_hrect(y0=plant_com + 0.01, y1=plant_com + 0.02, fillcolor="rgba(255, 255, 0, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Good (0.01-0.02)", annotation_position="right")
    fig.add_hrect(y0=plant_com + 0.02, y1=plant_com + 0.05, fillcolor="rgba(255, 0, 0, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Poor (>0.02)", annotation_position="right")
    
    # Plot COM line
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=com_y_series,
        mode='lines',
        name='COM Position',
        line=dict(color='steelblue', width=3)
    ))
    
    # Mark key events
    fig.add_vline(x=plant_frame/fps, line_dash="dash", line_color="red",
                  annotation_text="Foot Plant")
    fig.add_vline(x=lowest_frame/fps, line_dash="dash", line_color="purple",
                  annotation_text="Lowest Point")
    
    fig.update_layout(
        title="Braking Efficiency Zones",
        xaxis_title="Time (seconds)",
        yaxis_title="COM Vertical Position",
        yaxis=dict(autorange='reversed'),
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_energy_absorption(fbr_data, metadata):
    """
    Visualize energy absorption during braking.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_y_series = fbr_data.get("com_y_series", [])
    decel_series = fbr_data.get("decel_series", [])
    plant_frame = fbr_data.get("plant_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    if not com_y_series or not decel_series:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Energy Absorption", height=400)
        return fig
    
    # Calculate velocity (derivative of position)
    dt = 1.0 / fps
    velocity = np.gradient(com_y_series, dt)
    
    # Estimate kinetic energy (proportional to v²)
    kinetic_energy = velocity ** 2
    
    frames = list(range(len(kinetic_energy)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Plot kinetic energy
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=kinetic_energy,
        mode='lines',
        name='Kinetic Energy',
        line=dict(color='darkred', width=2),
        fill='tozeroy',
        fillcolor='rgba(139, 0, 0, 0.2)'
    ))
    
    # Mark foot plant
    fig.add_vline(x=plant_frame/fps, line_dash="dash", line_color="red",
                  annotation_text="Energy Absorption Begins")
    
    fig.update_layout(
        title="Energy Absorption Profile",
        xaxis_title="Time (seconds)",
        yaxis_title="Kinetic Energy (relative)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_timing_metrics(fbr_data, metadata):
    """
    Analyze timing of braking events.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    plant_frame = fbr_data.get("plant_frame", 0)
    lowest_frame = fbr_data.get("lowest_com_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    # Calculate durations
    descent_duration = (lowest_frame - plant_frame) / fps
    
    fig = go.Figure()
    
    # Create timeline
    fig.add_trace(go.Bar(
        x=[descent_duration],
        y=['Descent Duration'],
        orientation='h',
        marker=dict(color='steelblue'),
        text=[f'{descent_duration:.3f}s'],
        textposition='inside'
    ))
    
    # Add ideal range indicator
    fig.add_vrect(x0=0.05, x1=0.15, fillcolor="green", opacity=0.2,
                  annotation_text="Ideal Range", annotation_position="top")
    
    fig.update_layout(
        title=f"Braking Timing Analysis<br><sub>Foot Plant: Frame {plant_frame} | Lowest: Frame {lowest_frame}</sub>",
        xaxis_title="Time (seconds)",
        height=250,
        showlegend=False
    )
    
    return fig

def plot_benchmark_comparison_fbr(fbr_data):
    """
    Compare FBR score against benchmarks.
    
    Args:
        fbr_data: FBR analysis data dict
    
    Returns:
        Plotly figure
    """
    fbr_score = fbr_data.get("fbr_score", 0.0)
    
    # Benchmark ranges
    benchmarks = {
        'Elite': (0, 0.01),
        'Excellent': (0.01, 0.015),
        'Good': (0.015, 0.02),
        'Developing': (0.02, 0.03),
        'Needs Work': (0.03, 0.05)
    }
    
    fig = go.Figure()
    
    # Add benchmark bars
    categories = list(benchmarks.keys())
    ranges = [v[1] - v[0] for v in benchmarks.values()]
    colors = ['gold', 'lightgreen', 'lightblue', 'lightyellow', 'lightcoral']
    
    fig.add_trace(go.Bar(
        y=categories,
        x=ranges,
        base=[v[0] for v in benchmarks.values()],
        orientation='h',
        marker=dict(color=colors),
        name='Benchmark Ranges',
        hovertemplate='%{y}<br>Range: %{base:.3f} - %{x:.3f}<extra></extra>'
    ))
    
    # Add user's score
    fig.add_vline(x=fbr_score, line_color="red", line_width=3,
                  annotation_text=f"Your FBR: {fbr_score:.4f}",
                  annotation_position="top")
    
    fig.update_layout(
        title="FBR Score vs Benchmarks",
        xaxis_title="FBR Score (lower is better)",
        yaxis_title="Category",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_velocity_profile(fbr_data, metadata):
    """
    Plot vertical velocity profile.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    com_y_series = fbr_data.get("com_y_series", [])
    plant_frame = fbr_data.get("plant_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    if not com_y_series or len(com_y_series) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Velocity Profile", height=400)
        return fig
    
    # Calculate velocity
    dt = 1.0 / fps
    velocity = np.gradient(com_y_series, dt)
    
    frames = list(range(len(velocity)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Plot velocity
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=velocity,
        mode='lines',
        name='Vertical Velocity',
        line=dict(color='purple', width=2),
        fill='tozeroy',
        fillcolor='rgba(128, 0, 128, 0.2)'
    ))
    
    # Mark foot plant
    fig.add_vline(x=plant_frame/fps, line_dash="dash", line_color="red",
                  annotation_text="Foot Plant")
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    
    fig.update_layout(
        title="Vertical Velocity Profile",
        xaxis_title="Time (seconds)",
        yaxis_title="Velocity (normalized units/s)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_impact_force_estimate(fbr_data, metadata):
    """
    Estimate impact force based on deceleration.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    decel_series = fbr_data.get("decel_series", [])
    peak_decel = fbr_data.get("peak_deceleration", 0.0)
    plant_frame = fbr_data.get("plant_frame", 0)
    
    # Estimate relative force (F = ma, where a is deceleration)
    # This is a simplified model
    force_estimate = [abs(d) for d in decel_series]
    
    frames = list(range(len(force_estimate)))
    
    fig = go.Figure()
    
    # Plot force estimate
    fig.add_trace(go.Scatter(
        x=frames,
        y=force_estimate,
        mode='lines',
        name='Impact Force',
        line=dict(color='darkred', width=2),
        fill='tozeroy',
        fillcolor='rgba(139, 0, 0, 0.2)'
    ))
    
    # Mark foot plant
    fig.add_vline(x=plant_frame, line_dash="dash", line_color="red",
                  annotation_text="Foot Plant")
    
    # Mark peak force
    peak_frame = plant_frame + np.argmax(force_estimate[plant_frame:plant_frame+30])
    fig.add_vline(x=peak_frame, line_dash="dash", line_color="orange",
                  annotation_text=f"Peak Force")
    
    fig.update_layout(
        title=f"Estimated Impact Force<br><sub>Peak: {peak_decel:.4f} (relative units)</sub>",
        xaxis_title="Frame",
        yaxis_title="Force (relative)",
        hovermode='x unified',
        height=400
    )
    
    return fig
