"""
COM (Center of Mass) Analysis Page
Displays all 7 COM visualizations with metrics dashboard.
"""
import streamlit as st
import os
from utils.data_loader import load_com_data, load_pose_data, load_metadata

# Constants
VIDEO_PATH = "data/video_preview_h264.mp4"
JSON_PATH = "data/analysis_output.json"

def render_metrics_dashboard(com_data, metadata):
    """Render metrics dashboard with key COM statistics."""
    fps = metadata.get("fps", 24.0)
    
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    com_shift_norm = com_data.get("com_shift_norm", 0.0)
    com_shift_percent = com_data.get("com_shift_percent_width", 0.0)
    stance_width = com_data.get("stance_width_norm", 0.0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "COM Shift",
            f"{com_shift_norm:.3f}",
            delta=f"{com_shift_percent:.1f}% of width",
            help="Lateral shift of center of mass from stance to impact"
        )
    
    with col2:
        st.metric(
            "Stance Frame",
            f"{stance_frame}",
            delta=f"{stance_frame/fps:.2f}s",
            help="Frame where bowler is in stable stance position"
        )
    
    with col3:
        st.metric(
            "Impact Frame",
            f"{impact_frame}",
            delta=f"{impact_frame/fps:.2f}s",
            help="Frame with maximum hip movement (ball release)"
        )
    
    with col4:
        st.metric(
            "Stance Width",
            f"{stance_width:.3f}",
            help="Distance between ankles at stance (normalized)"
        )

def render():
    """Main render function for COM analysis page."""
    st.title("📊 Center of Mass (COM) Analysis")
    st.markdown("Analyze lateral weight transfer during bowling delivery")
    
    # Check if files exist
    if not os.path.exists(JSON_PATH):
        st.error(f"Data file not found: `{JSON_PATH}`")
        return
    
    if not os.path.exists(VIDEO_PATH):
        st.error(f"Video file not found: `{VIDEO_PATH}`")
        return
    
    # Load data
    com_data = load_com_data(JSON_PATH)
    pose_data = load_pose_data(JSON_PATH)
    metadata = load_metadata(JSON_PATH)
    
    if not com_data:
        st.warning("No COM analysis data found in JSON file")
        return
    
    # Metrics Dashboard
    st.markdown("### Key Metrics")
    render_metrics_dashboard(com_data, metadata)
    
    st.markdown("---")
    
    # AI Assessment Section
    st.markdown("### 🤖 AI Coaching Assessment")
    from utils.assessment import assess_com_performance, get_com_interpretation, get_benchmark_comparison
    
    assessment = assess_com_performance(com_data, metadata)
    
    # Overall rating
    col1, col2 = st.columns([1, 3])
    with col1:
        rating_emoji = {
            "Excellent": "🌟",
            "Good": "👍",
            "Developing": "📈",
            "Needs Work": "⚠️"
        }
        st.markdown(f"## {rating_emoji.get(assessment['overall_rating'], '📊')} {assessment['overall_rating']}")
    
    with col2:
        com_shift_percent = com_data.get("com_shift_percent_width", 0.0)
        interpretation = get_com_interpretation(com_shift_percent)
        st.info(f"**Interpretation:** {interpretation}")
        
        benchmark = get_benchmark_comparison(com_shift_percent)
        st.caption(f"📊 {benchmark}")
    
    # Strengths and improvements in columns
    col1, col2 = st.columns(2)
    
    with col1:
        if assessment["strengths"]:
            st.markdown("**✅ Strengths:**")
            for strength in assessment["strengths"]:
                st.success(strength, icon="✅")
    
    with col2:
        if assessment["areas_for_improvement"]:
            st.markdown("**🎯 Areas for Improvement:**")
            for area in assessment["areas_for_improvement"]:
                st.warning(area, icon="🎯")
    
    # Recommendations
    if assessment["recommendations"]:
        with st.expander("💡 **Coaching Recommendations**", expanded=True):
            for i, rec in enumerate(assessment["recommendations"], 1):
                st.markdown(f"{i}. {rec}")
    
    # Technical notes
    if assessment["technical_notes"]:
        with st.expander("📝 Technical Notes"):
            for note in assessment["technical_notes"]:
                st.markdown(f"- {note}")
    
    st.markdown("---")
    
    # Video Section with COM Overlay
    st.markdown("### Video with COM Overlay")
    
    with st.spinner("Processing video with COM annotations..."):
        from utils.video_processor import process_video_with_com_overlay
        import tempfile
        
        # Use temp file that will be auto-deleted
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            output_path = tmp.name
        
        result = process_video_with_com_overlay(
            VIDEO_PATH, pose_data, com_data, metadata, output_path
        )
        
        if result:
            st.video(result)
            # Note: File will be cleaned up by OS temp directory cleanup
        else:
            st.error("Failed to process video")
    
    st.markdown("---")
    
    # Analysis Tabs
    st.markdown("### Detailed Analysis")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🗺️ COM Trajectory",
        "📊 Movement Scores",
        "🔍 COM Components",
        "🔥 Heatmap",
        "⚡ Velocity Analysis",
        "🔄 Phase Diagram",
        "📈 Stability Index",
        "💎 Movement Efficiency",
        "🌐 3D Trajectory",
        "🏆 Benchmarks"
    ])
    
    with tab1:
        from visualizations.com_viz import plot_com_trajectory
        fig = plot_com_trajectory(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Shows lateral COM movement across delivery phases with stance and impact markers")
    
    with tab2:
        from visualizations.com_viz import plot_movement_scores
        fig = plot_movement_scores(pose_data, com_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Hip movement scores help validate stance (minimum) and impact (maximum) frame detection")
    
    with tab3:
        from visualizations.com_viz import plot_com_components
        fig = plot_com_components(pose_data, com_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("COM is calculated as 60% hip midpoint + 40% shoulder midpoint")
    
    with tab4:
        from visualizations.com_viz import create_heatmap
        fig = create_heatmap(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Density distribution showing where COM is concentrated during delivery")
    
    with tab5:
        from visualizations.com_viz_advanced import plot_com_velocity_analysis
        fig = plot_com_velocity_analysis(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Position, velocity, and acceleration analysis of COM movement")
    
    with tab6:
        from visualizations.com_viz_advanced import plot_com_phase_diagram
        fig = plot_com_phase_diagram(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Phase space diagram showing position vs velocity relationship")
    
    with tab7:
        from visualizations.com_viz_advanced import plot_com_stability_index
        fig = plot_com_stability_index(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Rolling stability score over time - higher is more stable")
    
    with tab8:
        from visualizations.com_viz_advanced import plot_com_movement_efficiency
        fig = plot_com_movement_efficiency(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Efficiency of COM movement - direct path vs total path")
    
    with tab9:
        from visualizations.com_viz_advanced import plot_com_3d_trajectory
        fig = plot_com_3d_trajectory(com_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("3D visualization of COM trajectory with time dimension")
    
    with tab10:
        from visualizations.com_viz_advanced import plot_com_benchmark_comparison
        fig = plot_com_benchmark_comparison(com_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Compare your lateral COM movement against benchmarks")

