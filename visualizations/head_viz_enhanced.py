"""
Enhanced head stability visualizations.
Additional advanced analysis functions.
"""
import plotly.graph_objects as go
import numpy as np

def plot_stability_zones(head_data):
    """
    Plot 2D trajectory with stability zones.
    
    Args:
        head_data: Head stability data dict
    
    Returns:
        Plotly figure
    """
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    
    if not head_x or not head_y or len(head_x) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Stability Zones", height=500)
        return fig
    
    # Calculate center (mean position during delivery)
    delivery_x = head_x[stance_frame:impact_frame+1]
    delivery_y = head_y[stance_frame:impact_frame+1]
    center_x = np.mean(delivery_x) if delivery_x else np.mean(head_x)
    center_y = np.mean(delivery_y) if delivery_y else np.mean(head_y)
    
    # Define zones (radius from center)
    stable_radius = 0.02  # Very stable
    acceptable_radius = 0.04  # Acceptable
    
    fig = go.Figure()
    
    # Draw zones as circles
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Unstable zone (outer)
    fig.add_trace(go.Scatter(
        x=center_x + acceptable_radius * np.cos(theta),
        y=center_y + acceptable_radius * np.sin(theta),
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.1)',
        line=dict(color='red', dash='dash'),
        name='Unstable Zone',
        hoverinfo='skip'
    ))
    
    # Acceptable zone
    fig.add_trace(go.Scatter(
        x=center_x + stable_radius * np.cos(theta),
        y=center_y + stable_radius * np.sin(theta),
        fill='toself',
        fillcolor='rgba(255, 255, 0, 0.2)',
        line=dict(color='yellow', dash='dash'),
        name='Acceptable Zone',
        hoverinfo='skip'
    ))
    
    # Stable zone (inner)
    stable_inner = stable_radius * 0.5
    fig.add_trace(go.Scatter(
        x=center_x + stable_inner * np.cos(theta),
        y=center_y + stable_inner * np.sin(theta),
        fill='toself',
        fillcolor='rgba(0, 255, 0, 0.2)',
        line=dict(color='green', dash='dash'),
        name='Stable Zone',
        hoverinfo='skip'
    ))
    
    # Plot actual trajectory with color coding
    distances = [np.sqrt((x - center_x)**2 + (y - center_y)**2) for x, y in zip(head_x, head_y)]
    colors = ['green' if d < stable_radius else 'yellow' if d < acceptable_radius else 'red' 
              for d in distances]
    
    fig.add_trace(go.Scatter(
        x=head_x,
        y=head_y,
        mode='markers',
        marker=dict(size=4, color=colors),
        name='Head Position',
        text=[f'Frame {i}' for i in range(len(head_x))],
        hovertemplate='%{text}<br>X: %{x:.3f}<br>Y: %{y:.3f}'
    ))
    
    # Calculate zone percentages
    stable_pct = sum(1 for d in distances if d < stable_radius) / len(distances) * 100
    acceptable_pct = sum(1 for d in distances if stable_radius <= d < acceptable_radius) / len(distances) * 100
    unstable_pct = sum(1 for d in distances if d >= acceptable_radius) / len(distances) * 100
    
    fig.update_layout(
        title=f"Stability Zones<br><sub>Stable: {stable_pct:.1f}% | Acceptable: {acceptable_pct:.1f}% | Unstable: {unstable_pct:.1f}%</sub>",
        xaxis_title="Horizontal Position",
        yaxis_title="Vertical Position",
        yaxis=dict(autorange='reversed'),
        height=500,
        showlegend=True
    )
    
    return fig

def plot_rolling_stability(head_data, metadata):
    """
    Plot rolling stability score over time.
    
    Args:
        head_data: Head stability data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    fps = metadata.get("fps", 24.0)
    
    if not head_x or len(head_x) < 10:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Rolling Stability Score", height=400)
        return fig
    
    # Calculate rolling stability (inverse of rolling variance)
    window = min(int(fps * 0.5), len(head_x) // 4)  # 0.5 second window
    rolling_scores = []
    
    for i in range(len(head_x)):
        start = max(0, i - window // 2)
        end = min(len(head_x), i + window // 2)
        
        window_x = head_x[start:end]
        window_y = head_y[start:end]
        
        if len(window_x) > 1:
            variance = np.var(window_x) + np.var(window_y)
            score = 100 / (1 + variance * 1000)  # Scale to 0-100
            rolling_scores.append(score)
        else:
            rolling_scores.append(0)
    
    frames = list(range(len(rolling_scores)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Add rolling score line
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=rolling_scores,
        mode='lines',
        name='Stability Score',
        line=dict(color='steelblue', width=2),
        fill='tozeroy',
        fillcolor='rgba(70, 130, 180, 0.3)'
    ))
    
    # Add threshold lines
    fig.add_hline(y=80, line_dash="dash", line_color="green", 
                  annotation_text="Excellent (80+)")
    fig.add_hline(y=60, line_dash="dash", line_color="orange", 
                  annotation_text="Good (60+)")
    
    fig.update_layout(
        title="Rolling Stability Score (Frame-by-Frame)",
        xaxis_title="Time (seconds)",
        yaxis_title="Stability Score (0-100)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_head_dip_analysis(head_data, metadata):
    """
    Analyze and plot head dip (vertical movement).
    
    Args:
        head_data: Head stability data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    head_y = head_data.get("head_y_smooth", [])
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    if not head_y or len(head_y) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Head Dip Analysis", height=400)
        return fig
    
    frames = list(range(len(head_y)))
    time_sec = [f / fps for f in frames]
    
    # Calculate dip relative to stance position
    stance_y = head_y[stance_frame] if stance_frame < len(head_y) else head_y[0]
    dip_values = [(y - stance_y) for y in head_y]  # Positive = dip down
    
    fig = go.Figure()
    
    # Add dip line
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=dip_values,
        mode='lines',
        name='Head Dip',
        line=dict(color='darkred', width=2),
        fill='tozeroy',
        fillcolor='rgba(139, 0, 0, 0.2)'
    ))
    
    # Add ideal range
    fig.add_hrect(y0=-0.02, y1=0.02, fillcolor="green", opacity=0.1, 
                  layer="below", line_width=0,
                  annotation_text="Ideal Range", annotation_position="right")
    
    # Mark stance and impact
    fig.add_vline(x=stance_frame/fps, line_dash="dash", line_color="blue",
                  annotation_text="Stance")
    fig.add_vline(x=impact_frame/fps, line_dash="dash", line_color="purple",
                  annotation_text="Impact")
    
    # Calculate max dip
    max_dip = max(dip_values)
    max_dip_frame = dip_values.index(max_dip)
    
    fig.update_layout(
        title=f"Head Dip Analysis<br><sub>Max Dip: {max_dip:.3f} at frame {max_dip_frame}</sub>",
        xaxis_title="Time (seconds)",
        yaxis_title="Vertical Displacement (normalized)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_benchmark_comparison(head_data):
    """
    Compare stability score against benchmarks.
    
    Args:
        head_data: Head stability data dict
    
    Returns:
        Plotly figure
    """
    score = head_data.get("score_0_100", 0.0)
    
    # Benchmark ranges
    benchmarks = {
        'Elite (International)': (90, 100),
        'Excellent (Professional)': (80, 90),
        'Good (Club Level)': (70, 80),
        'Developing': (60, 70),
        'Needs Work': (0, 60)
    }
    
    fig = go.Figure()
    
    # Add benchmark bars
    categories = list(benchmarks.keys())
    ranges = [v[1] - v[0] for v in benchmarks.values()]
    
    colors = ['gold', 'lightgreen', 'lightblue', 'orange', 'lightcoral']
    
    fig.add_trace(go.Bar(
        y=categories,
        x=ranges,
        base=[v[0] for v in benchmarks.values()],
        orientation='h',
        marker=dict(color=colors),
        name='Benchmark Ranges',
        hovertemplate='%{y}<br>Range: %{base} - %{x}<extra></extra>'
    ))
    
    # Add user's score as a line
    fig.add_vline(x=score, line_color="red", line_width=3,
                  annotation_text=f"Your Score: {score:.1f}",
                  annotation_position="top")
    
    fig.update_layout(
        title="Stability Score vs Benchmarks",
        xaxis_title="Stability Score (0-100)",
        yaxis_title="Category",
        height=400,
        showlegend=False
    )
    
    return fig
