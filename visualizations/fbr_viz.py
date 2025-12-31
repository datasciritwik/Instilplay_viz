"""
FBR (Front-Back-Release) visualization functions.
Creates interactive charts for foot plant biomechanics analysis.
"""
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def plot_com_vertical_movement(fbr_data, metadata):
    """
    Plot COM vertical position over time.
    
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
            text="No COM data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="COM Vertical Movement", height=500)
        return fig
    
    frames = list(range(len(com_y_series)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Add COM line
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=com_y_series,
        mode='lines',
        name='COM Vertical Position',
        line=dict(color='steelblue', width=3)
    ))
    
    # Mark foot plant
    fig.add_vline(
        x=plant_frame/fps,
        line_dash="dash",
        line_color="red",
        annotation_text="Foot Plant",
        annotation_position="top"
    )
    
    # Mark lowest point
    fig.add_vline(
        x=lowest_frame/fps,
        line_dash="dash",
        line_color="purple",
        annotation_text="Lowest COM",
        annotation_position="top"
    )
    
    # Highlight descent region
    fig.add_vrect(
        x0=plant_frame/fps,
        x1=lowest_frame/fps,
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0,
        annotation_text="Descent Phase"
    )
    
    fig.update_layout(
        title="Center of Mass Vertical Movement",
        xaxis_title="Time (seconds)",
        yaxis_title="Vertical Position (normalized, inverted)",
        yaxis=dict(autorange='reversed'),  # Flip so down is positive
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_deceleration_profile(fbr_data, metadata):
    """
    Plot deceleration over time.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Plotly figure
    """
    decel_series = fbr_data.get("decel_series", [])
    plant_frame = fbr_data.get("plant_frame", 0)
    peak_decel = fbr_data.get("peak_deceleration", 0.0)
    fps = metadata.get("fps", 24.0)
    
    if not decel_series:
        fig = go.Figure()
        fig.add_annotation(
            text="No deceleration data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(title="Deceleration Profile", height=400)
        return fig
    
    frames = list(range(len(decel_series)))
    time_sec = [f / fps for f in frames]
    
    fig = go.Figure()
    
    # Add deceleration line
    fig.add_trace(go.Scatter(
        x=time_sec,
        y=decel_series,
        mode='lines',
        name='Deceleration',
        line=dict(color='darkgreen', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 128, 0, 0.2)'
    ))
    
    # Mark foot plant
    fig.add_vline(
        x=plant_frame/fps,
        line_dash="dash",
        line_color="red",
        annotation_text="Foot Plant"
    )
    
    # Mark peak deceleration
    peak_frame = plant_frame + np.argmax(decel_series[plant_frame:plant_frame+30])
    fig.add_vline(
        x=peak_frame/fps,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Peak: {peak_decel:.3f}"
    )
    
    fig.update_layout(
        title="Vertical Deceleration Profile",
        xaxis_title="Time (seconds)",
        yaxis_title="Deceleration (normalized units/s²)",
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_fbr_score_gauge(fbr_data):
    """
    Display FBR score as a gauge.
    
    Args:
        fbr_data: FBR analysis data dict
    
    Returns:
        Plotly figure
    """
    fbr_score = fbr_data.get("fbr_score", 0.0)
    
    # Interpret FBR score (lower is better - efficient braking)
    if fbr_score < 0.01:
        rating = "Excellent"
        color = "green"
    elif fbr_score < 0.02:
        rating = "Good"
        color = "lightgreen"
    elif fbr_score < 0.03:
        rating = "Moderate"
        color = "yellow"
    else:
        rating = "Needs Work"
        color = "red"
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=fbr_score * 1000,  # Scale for display
        title={'text': f"FBR Score<br><sub>{rating}</sub>"},
        delta={'reference': 20, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 50]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 10], 'color': "lightgreen"},
                {'range': [10, 20], 'color': "lightyellow"},
                {'range': [20, 30], 'color': "orange"},
                {'range': [30, 50], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 30
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        annotations=[
            dict(
                text="Lower score = Better braking efficiency",
                xref="paper", yref="paper",
                x=0.5, y=-0.1,
                showarrow=False,
                font=dict(size=12)
            )
        ]
    )
    
    return fig

def plot_descent_vs_deceleration(fbr_data):
    """
    Plot descent vs deceleration relationship.
    
    Args:
        fbr_data: FBR analysis data dict
    
    Returns:
        Plotly figure
    """
    max_descent = fbr_data.get("max_vertical_descent", 0.0)
    peak_decel = fbr_data.get("peak_deceleration", 0.0)
    fbr_score = fbr_data.get("fbr_score", 0.0)
    
    fig = go.Figure()
    
    # Create bar chart
    fig.add_trace(go.Bar(
        x=['Max Descent', 'Peak Deceleration', 'FBR Score (×1000)'],
        y=[max_descent, peak_decel, fbr_score * 1000],
        marker=dict(
            color=['steelblue', 'darkgreen', 'coral'],
            line=dict(color='black', width=2)
        ),
        text=[f'{max_descent:.4f}', f'{peak_decel:.4f}', f'{fbr_score*1000:.2f}'],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="FBR Components",
        yaxis_title="Value (normalized units)",
        height=400,
        showlegend=False
    )
    
    return fig

def plot_combined_analysis(fbr_data, metadata):
    """
    Combined plot showing COM and deceleration together.
    
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
        fig.update_layout(title="Combined Analysis", height=600)
        return fig
    
    frames = list(range(len(com_y_series)))
    time_sec = [f / fps for f in frames]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("COM Vertical Position", "Deceleration"),
        vertical_spacing=0.12
    )
    
    # COM position
    fig.add_trace(
        go.Scatter(x=time_sec, y=com_y_series, mode='lines', name='COM Y',
                   line=dict(color='steelblue', width=2)),
        row=1, col=1
    )
    
    # Deceleration
    fig.add_trace(
        go.Scatter(x=time_sec, y=decel_series, mode='lines', name='Deceleration',
                   line=dict(color='darkgreen', width=2),
                   fill='tozeroy', fillcolor='rgba(0, 128, 0, 0.2)'),
        row=2, col=1
    )
    
    # Add foot plant markers on both
    for row in [1, 2]:
        fig.add_vline(
            x=plant_frame/fps,
            line_dash="dash",
            line_color="red",
            annotation_text="Foot Plant" if row == 1 else "",
            row=row, col=1
        )
    
    fig.update_xaxes(title_text="Time (seconds)", row=2, col=1)
    fig.update_yaxes(title_text="Position", row=1, col=1, autorange='reversed')
    fig.update_yaxes(title_text="Deceleration", row=2, col=1)
    
    fig.update_layout(height=600, showlegend=False, hovermode='x unified')
    
    return fig
