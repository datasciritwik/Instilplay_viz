"""
Hip-Shoulder Separation Analysis Page
Displays hip-shoulder angle analysis with separation metrics and AI assessment.
"""
import streamlit as st
import os
from utils.data_loader import load_hip_shoulder_data, load_metadata

# Constants
VIDEO_PATH = "data/video_preview_h264.mp4"
JSON_PATH = "data/analysis_output.json"

def render_metrics_dashboard(hs_data, metadata):
    """Render metrics dashboard with key hip-shoulder statistics."""
    fps = metadata.get("fps", 24.0)
    
    peak_sep = hs_data.get("peak_separation_deg", 0.0)
    rate_of_sep = hs_data.get("rate_of_separation_deg_per_sec", 0.0)
    key_frames = hs_data.get("key_frames", {})
    downswing_start = key_frames.get("downswing_start", 0)
    peak_frame = key_frames.get("peak_frame", 0)
    downswing_end = key_frames.get("downswing_end", 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Peak Separation",
            f"{peak_sep:.1f}°",
            help="Maximum angle between hip and shoulder lines during delivery"
        )
    
    with col2:
        st.metric(
            "Separation Rate",
            f"{rate_of_sep:.0f}°/s",
            help="Speed of hip-shoulder separation (higher = more explosive)"
        )
    
    with col3:
        st.metric(
            "Downswing Start",
            f"{downswing_start}",
            delta=f"{downswing_start/fps:.2f}s",
            help="Frame where downswing begins"
        )
    
    with col4:
        st.metric(
            "Peak Frame",
            f"{peak_frame}",
            delta=f"{peak_frame/fps:.2f}s",
            help="Frame with maximum separation"
        )

def render():
    """Main render function for hip-shoulder analysis page."""
    st.title("💪 Hip-Shoulder Separation Analysis")
    st.markdown("Analyze the 'X-factor' - hip rotation ahead of shoulders for power generation")
    
    # Load data
    hs_data = load_hip_shoulder_data(JSON_PATH)
    metadata = load_metadata(JSON_PATH)
    
    # Handle nested structure
    if "hip_shoulder_separation" in hs_data:
        hs_data = hs_data.get("hip_shoulder_separation", {})
    
    if not hs_data:
        st.warning("No hip-shoulder separation data found in JSON file")
        return
    
    # Metrics Dashboard
    st.markdown("### Key Metrics")
    render_metrics_dashboard(hs_data, metadata)
    
    st.markdown("---")
    
    # AI Assessment Section
    st.markdown("### 🤖 AI Coaching Assessment")
    from utils.assessment import assess_hip_shoulder, get_hip_shoulder_interpretation
    
    assessment = assess_hip_shoulder(hs_data, metadata)
    
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
        peak_sep = hs_data.get("peak_separation_deg", 0.0)
        interpretation = get_hip_shoulder_interpretation(peak_sep)
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
    
    # Video Section with Hip-Shoulder Overlay
    st.markdown("### Video with Hip-Shoulder Separation")
    
    with st.spinner("Processing video with hip-shoulder annotations..."):
        from utils.hip_shoulder_video_processor import process_video_with_hip_shoulder
        from utils.data_loader import load_pose_data
        import tempfile
        
        pose_data = load_pose_data(JSON_PATH)
        
        # Use temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            output_path = tmp.name
        
        result = process_video_with_hip_shoulder(
            VIDEO_PATH, pose_data, hs_data, metadata, output_path
        )
        
        if result:
            try:
                if isinstance(result, str) and os.path.exists(result):
                    with open(result, "rb") as vf:
                        video_bytes = vf.read()
                    st.video(video_bytes)
                    st.download_button("Download processed video", data=video_bytes, file_name=os.path.basename(result), mime="video/mp4")
                else:
                    st.video(result)
            except Exception as e:
                st.warning(f"Could not load processed video as bytes: {e}; falling back to path.")
                st.video(result)
        else:
            st.error("Failed to process video")
    
    st.markdown("---")
    
    # Analysis Tabs
    st.markdown("### Detailed Analysis")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📈 Separation Angle",
        "⚡ Separation Rate",
        "📊 Phase Breakdown",
        "🎯 Separation Zones",
        "⚙️ Power Generation",
        "⏱️ Timing Analysis",
        "🔄 Hip vs Shoulder",
        "🏆 Benchmarks",
        "📉 Frame-by-Frame"
    ])
    
    with tab1:
        from visualizations.hip_shoulder_viz import plot_separation_angle
        fig = plot_separation_angle(hs_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Hip-shoulder separation angle throughout delivery - peak indicates maximum 'X-factor'")
    
    with tab2:
        from visualizations.hip_shoulder_viz import plot_separation_rate
        fig = plot_separation_rate(hs_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Angular velocity of separation - higher values indicate more explosive hip rotation")
    
    with tab3:
        from visualizations.hip_shoulder_viz import plot_separation_phases
        fig = plot_separation_phases(hs_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Average separation in different phases of delivery")
    
    with tab4:
        from visualizations.hip_shoulder_viz_enhanced import plot_separation_zones
        fig = plot_separation_zones(hs_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Color-coded zones: Elite (>45°), Good (35-45°), Developing (25-35°), Poor (<25°)")
    
    with tab5:
        from visualizations.hip_shoulder_viz_enhanced import plot_power_generation
        fig = plot_power_generation(hs_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Power generation index and estimated ball speed potential based on separation")
    
    with tab6:
        from visualizations.hip_shoulder_viz_enhanced import plot_timing_analysis
        fig = plot_timing_analysis(hs_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Timing of separation events - time to peak and peak duration")
    
    with tab7:
        from visualizations.hip_shoulder_viz_enhanced import plot_hip_vs_shoulder_rotation
        fig = plot_hip_vs_shoulder_rotation(hs_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Separate tracking of hip and shoulder rotation - shows the 'lag' effect")
    
    with tab8:
        from visualizations.hip_shoulder_viz_enhanced import plot_benchmark_comparison_hs
        fig = plot_benchmark_comparison_hs(hs_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Compare your separation against different bowling types")
    
    with tab9:
        from visualizations.hip_shoulder_viz_enhanced import plot_frame_by_frame_rate
        fig = plot_frame_by_frame_rate(hs_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Angular velocity and acceleration - identifies explosive moments")


