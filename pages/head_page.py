"""
Head Stability Analysis Page
Displays head movement analysis with trajectory, displacement, and stability metrics.
"""
import streamlit as st
import os
from utils.data_loader import load_head_stability_data, load_pose_data, load_metadata

# Constants
VIDEO_PATH = "data/video_preview_h264.mp4"
JSON_PATH = "data/analysis_output.json"

def render_metrics_dashboard(head_data, metadata):
    """Render metrics dashboard with key head stability statistics."""
    fps = metadata.get("fps", 24.0)
    
    score = head_data.get("score_0_100", 0.0)
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Color code the score
        if score >= 80:
            delta_color = "normal"
        elif score >= 60:
            delta_color = "off"
        else:
            delta_color = "inverse"
            
        st.metric(
            "Stability Score",
            f"{score:.1f}/100",
            delta="Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work",
            help="Higher score = more stable head position (less jitter)"
        )
    
    with col2:
        st.metric(
            "Stance Frame",
            f"{stance_frame}",
            delta=f"{stance_frame/fps:.2f}s",
            help="Frame where head position stabilizes before delivery"
        )
    
    with col3:
        st.metric(
            "Impact Frame",
            f"{impact_frame}",
            delta=f"{impact_frame/fps:.2f}s",
            help="Frame with maximum head movement (ball release)"
        )

def render():
    """Main render function for head stability analysis page."""
    st.title("🎯 Head Stability Analysis")
    st.markdown("Analyze head position control and stability during bowling delivery")
    
    # Check if files exist
    if not os.path.exists(JSON_PATH):
        st.error(f"Data file not found: `{JSON_PATH}`")
        return
    
    if not os.path.exists(VIDEO_PATH):
        st.error(f"Video file not found: `{VIDEO_PATH}`")
        return
    
    # Load data
    head_data = load_head_stability_data(JSON_PATH)
    pose_data = load_pose_data(JSON_PATH)
    metadata = load_metadata(JSON_PATH)
    
    if not head_data:
        st.warning("No head stability data found in JSON file")
        return
    
    # Metrics Dashboard
    st.markdown("### Key Metrics")
    render_metrics_dashboard(head_data, metadata)
    
    st.markdown("---")
    
    # AI Assessment Section
    st.markdown("### 🤖 AI Coaching Assessment")
    from utils.assessment import assess_head_stability, get_head_stability_interpretation
    
    assessment = assess_head_stability(head_data, metadata)
    
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
        score = head_data.get("score_0_100", 0.0)
        interpretation = get_head_stability_interpretation(score)
        st.info(f"**Interpretation:** {interpretation}")
    
    # Strengths and improvements
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
    
    # Video Section with Head Tracking
    st.markdown("### Video with Head Tracking")
    
    with st.spinner("Processing video with head tracking overlay..."):
        from utils.head_video_processor import process_video_with_head_tracking
        import tempfile
        
        # Use temp file that will be auto-deleted
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            output_path = tmp.name
        
        result = process_video_with_head_tracking(
            VIDEO_PATH, pose_data, head_data, metadata, output_path
        )
        
        if result:
            st.video(result)
            # Note: File will be cleaned up by OS temp directory cleanup
        else:
            st.error("Failed to process video")
    
    st.markdown("---")
    
    # Analysis Tabs
    st.markdown("### Detailed Analysis")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🗺️ 2D Trajectory",
        "📈 Position Over Time",
        "📉 Displacement",
        "🔥 Heatmap",
        "🎯 Stability Zones",
        "📊 Rolling Score",
        "⬇️ Head Dip",
        "🏆 Benchmarks"
    ])
    
    with tab1:
        from visualizations.head_viz import plot_head_trajectory_2d
        fig = plot_head_trajectory_2d(head_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Shows the path of head movement during delivery - ideally should be minimal")
    
    with tab2:
        from visualizations.head_viz import plot_head_position_over_time
        fig = plot_head_position_over_time(head_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Horizontal and vertical head position changes over time")
    
    with tab3:
        from visualizations.head_viz import plot_head_displacement
        fig = plot_head_displacement(head_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Frame-to-frame head movement (jitter) - lower is better for consistency")
    
    with tab4:
        from visualizations.head_viz import create_head_heatmap
        fig = create_head_heatmap(head_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Density map showing where head position is concentrated during delivery")
    
    with tab5:
        from visualizations.head_viz_enhanced import plot_stability_zones
        fig = plot_stability_zones(head_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Color-coded zones showing stability - green (stable), yellow (acceptable), red (unstable)")
    
    with tab6:
        from visualizations.head_viz_enhanced import plot_rolling_stability
        fig = plot_rolling_stability(head_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Frame-by-frame stability score - identifies specific unstable periods")
    
    with tab7:
        from visualizations.head_viz_enhanced import plot_head_dip_analysis
        fig = plot_head_dip_analysis(head_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Vertical head movement analysis - excessive dip affects line and length")
    
    with tab8:
        from visualizations.head_viz_enhanced import plot_benchmark_comparison
        fig = plot_benchmark_comparison(head_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Compare your stability score against professional benchmarks")
