"""
Enhanced hip-shoulder separation visualizations.
Advanced analysis functions for power generation and timing.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_separation_zones(hs_data, metadata):
    """
    Plot separation angle with color-coded performance zones.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    angle_series = hs_data.get("angle_series", [])
    key_frames = hs_data.get("key_frames", {})
    peak_frame = key_frames.get("peak_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    if not angle_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Separation Zones", height=500)
        return fig
    
    frames = list(range(len(angle_series)))
    time_sec = [f / fps for f in frames]
    
    # Calculate zone percentages
    elite_pct = sum(1 for a in angle_series if a >= 45) / len(angle_series) * 100
    good_pct = sum(1 for a in angle_series if 35 <= a < 45) / len(angle_series) * 100
    developing_pct = sum(1 for a in angle_series if 25 <= a < 35) / len(angle_series) * 100
    poor_pct = sum(1 for a in angle_series if a < 25) / len(angle_series) * 100
    
    fig = go.Figure()
    
    # Add zone backgrounds
    fig.add_hrect(y0=45, y1=90, fillcolor="rgba(0, 255, 0, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Elite Zone", annotation_position="right")
    fig.add_hrect(y0=35, y1=45, fillcolor="rgba(173, 216, 230, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Good Zone", annotation_position="right")
    fig.add_hrect(y0=25, y1=35, fillcolor="rgba(255, 255, 0, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Developing Zone", annotation_position="right")
    fig.add_hrect(y0=0, y1=25, fillcolor="rgba(255, 0, 0, 0.1)", 
                  layer="below", line_width=0,
                  annotation_text="Poor Zone", annotation_position="right")
    
    # Color code the line based on zones
    colors = ['green' if a >= 45 else 'lightblue' if a >= 35 else 'yellow' if a >= 25 else 'red' 
              for a in angle_series]
    
    # Plot as scatter with color coding
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=angle_series,
        mode='lines+markers',
        marker=dict(size=4, color=colors),
        line=dict(color='steelblue', width=2),
        name='Separation Angle'
    ))
    
    # Mark peak
    fig.add_trace(go.Scatter(
        x=[peak_frame/fps],
        y=[angle_series[peak_frame]],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name='Peak Separation'
    ))
    
    fig.update_layout(
        title=f"Separation Zones<br><sub>Elite: {elite_pct:.1f}% | Good: {good_pct:.1f}% | Developing: {developing_pct:.1f}% | Poor: {poor_pct:.1f}%</sub>",
        xaxis_title="Time (seconds)",
        yaxis_title="Separation Angle (degrees)",
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_power_generation(hs_data):
    """
    Visualize power generation potential based on separation.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
    
    Returns:
        Plotly figure
    """
    peak_sep = hs_data.get("peak_separation_deg", 0.0)
    rate_of_sep = hs_data.get("rate_of_separation_deg_per_sec", 0.0)
    
    # Estimate relative power (simplified model)
    # Power ∝ separation angle × rate
    power_index = (peak_sep / 50) * (rate_of_sep / 400) * 100
    power_index = min(100, power_index)  # Cap at 100
    
    # Estimate ball speed potential (very rough approximation)
    # Elite bowlers: 45°+ separation, 140+ km/h
    # Good bowlers: 35-45°, 120-140 km/h
    estimated_speed_min = 90 + (peak_sep / 50) * 50
    estimated_speed_max = estimated_speed_min + 10
    
    fig = go.Figure()
    
    # Power gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=power_index,
        title={'text': "Power Generation Index"},
        delta={'reference': 70, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightcoral"},
                {'range': [40, 70], 'color': "lightyellow"},
                {'range': [70, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        },
        domain={'row': 0, 'column': 0}
    ))
    
    fig.update_layout(
        height=400,
        annotations=[
            dict(
                text=f"Estimated Ball Speed Potential: {estimated_speed_min:.0f}-{estimated_speed_max:.0f} km/h",
                xref="paper", yref="paper",
                x=0.5, y=-0.1,
                showarrow=False,
                font=dict(size=14)
            )
        ]
    )
    
    return fig

def plot_timing_analysis(hs_data, metadata):
    """
    Analyze timing of separation events.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    key_frames = hs_data.get("key_frames", {})
    downswing_start = key_frames.get("downswing_start", 0)
    peak_frame = key_frames.get("peak_frame", 0)
    downswing_end = key_frames.get("downswing_end", 0)
    fps = metadata.get("fps", 24.0)
    
    # Calculate durations
    time_to_peak = (peak_frame - downswing_start) / fps
    peak_duration = (downswing_end - peak_frame) / fps
    total_duration = (downswing_end - downswing_start) / fps
    
    fig = go.Figure()
    
    # Create timeline bars
    events = ['Downswing Start', 'Peak Separation', 'Downswing End']
    times = [downswing_start/fps, peak_frame/fps, downswing_end/fps]
    
    fig.add_trace(go.Bar(
        x=[time_to_peak, peak_duration],
        y=['Time to Peak', 'Peak Duration'],
        orientation='h',
        marker=dict(color=['steelblue', 'darkgreen']),
        text=[f'{time_to_peak:.3f}s', f'{peak_duration:.3f}s'],
        textposition='inside'
    ))
    
    fig.update_layout(
        title=f"Separation Timing Analysis<br><sub>Total Duration: {total_duration:.3f}s</sub>",
        xaxis_title="Time (seconds)",
        height=300,
        showlegend=False
    )
    
    return fig

def plot_hip_vs_shoulder_rotation(hs_data, metadata):
    """
    Compare hip and shoulder rotation separately.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    angle_series = hs_data.get("angle_series", [])
    fps = metadata.get("fps", 24.0)
    
    if not angle_series or len(angle_series) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Hip vs Shoulder Rotation", height=400)
        return fig
    
    # Simulate hip and shoulder angles (in real implementation, these would be tracked separately)
    # For now, we'll estimate based on separation angle
    # Assume hips rotate more, shoulders lag
    base_rotation = 45  # Base rotation angle
    hip_rotation = [base_rotation + a * 0.6 for a in angle_series]
    shoulder_rotation = [base_rotation + a * 0.4 for a in angle_series]
    
    frames = list(range(len(angle_series)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Hip rotation
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=hip_rotation,
        mode='lines',
        name='Hip Rotation',
        line=dict(color='orange', width=3)
    ))
    
    # Shoulder rotation
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=shoulder_rotation,
        mode='lines',
        name='Shoulder Rotation',
        line=dict(color='purple', width=3)
    ))
    
    # Separation (difference)
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=angle_series,
        mode='lines',
        name='Separation (Hip - Shoulder)',
        line=dict(color='green', width=2, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(0, 255, 0, 0.1)'
    ))
    
    fig.update_layout(
        title="Hip vs Shoulder Rotation",
        xaxis_title="Time (seconds)",
        yaxis_title="Rotation Angle (degrees)",
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_benchmark_comparison_hs(hs_data):
    """
    Compare separation against bowling type benchmarks.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
    
    Returns:
        Plotly figure
    """
    peak_sep = hs_data.get("peak_separation_deg", 0.0)
    
    # Benchmark ranges by bowling type
    benchmarks = {
        'Elite Fast Bowler': (50, 65),
        'Professional Fast': (45, 55),
        'Good Fast': (40, 50),
        'Medium Pace': (35, 45),
        'Spin Bowler': (25, 35)
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
        hovertemplate='%{y}<br>Range: %{base}° - %{x}°<extra></extra>'
    ))
    
    # Add user's score as a line
    fig.add_vline(x=peak_sep, line_color="red", line_width=3,
                  annotation_text=f"Your Peak: {peak_sep:.1f}°",
                  annotation_position="top")
    
    fig.update_layout(
        title="Peak Separation vs Bowling Type Benchmarks",
        xaxis_title="Separation Angle (degrees)",
        yaxis_title="Bowling Type",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_frame_by_frame_rate(hs_data, metadata):
    """
    Plot frame-by-frame separation rate with acceleration.
    
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
    
    if not angle_series or len(angle_series) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Frame-by-Frame Rate", height=500)
        return fig
    
    # Calculate velocity and acceleration
    angle_arr = np.array(angle_series)
    velocity = np.gradient(angle_arr) * fps  # deg/sec
    acceleration = np.gradient(velocity) * fps  # deg/sec²
    
    frames = list(range(len(angle_series)))
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Angular Velocity", "Angular Acceleration"),
        vertical_spacing=0.15
    )
    
    # Velocity
    fig.add_trace(
        go.Scatter(x=frames, y=velocity, mode='lines', name='Velocity',
                   line=dict(color='steelblue', width=2),
                   fill='tozeroy', fillcolor='rgba(70, 130, 180, 0.3)'),
        row=1, col=1
    )
    
    # Acceleration
    fig.add_trace(
        go.Scatter(x=frames, y=acceleration, mode='lines', name='Acceleration',
                   line=dict(color='darkgreen', width=2),
                   fill='tozeroy', fillcolor='rgba(0, 128, 0, 0.2)'),
        row=2, col=1
    )
    
    # Mark downswing window on both
    for row in [1, 2]:
        fig.add_vrect(
            x0=downswing_start, x1=downswing_end,
            fillcolor="yellow", opacity=0.2,
            layer="below", line_width=0,
            row=row, col=1
        )
    
    fig.update_xaxes(title_text="Frame", row=2, col=1)
    fig.update_yaxes(title_text="deg/sec", row=1, col=1)
    fig.update_yaxes(title_text="deg/sec²", row=2, col=1)
    
    fig.update_layout(height=600, showlegend=False, hovermode='x unified')
    
    return fig
