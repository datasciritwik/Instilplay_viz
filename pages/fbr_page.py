"""
FBR (Front-Back-Release) Analysis Page
Displays foot plant biomechanics with COM descent and braking efficiency.
"""
import streamlit as st
import os
import cv2
import traceback
from utils.data_loader import load_fbr_data, load_metadata

# Constants
VIDEO_PATH = "data/video_preview_h264.mp4"
JSON_PATH = "data/analysis_output.json"

def render_metrics_dashboard(fbr_data, metadata):
    """Render metrics dashboard with key FBR statistics."""
    fps = metadata.get("fps", 24.0)
    
    fbr_score = fbr_data.get("fbr_score", 0.0)
    peak_decel = fbr_data.get("peak_deceleration", 0.0)
    max_descent = fbr_data.get("max_vertical_descent", 0.0)
    plant_frame = fbr_data.get("plant_frame", 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "FBR Score",
            f"{fbr_score:.4f}",
            delta="Lower is better",
            delta_color="inverse",
            help="Braking efficiency - descent/deceleration ratio"
        )
    
    with col2:
        st.metric(
            "Peak Deceleration",
            f"{peak_decel:.4f}",
            help="Maximum braking force at foot plant"
        )
    
    with col3:
        st.metric(
            "Max Descent",
            f"{max_descent:.4f}",
            help="Maximum vertical COM drop after foot plant"
        )
    
    with col4:
        st.metric(
            "Foot Plant Frame",
            f"{plant_frame}",
            delta=f"{plant_frame/fps:.2f}s",
            help="Frame where front foot plants"
        )

def render():
    """Main render function for FBR analysis page."""
    st.title("🦶 FBR (Front-Back-Release) Analysis")
    st.markdown("Analyze foot plant biomechanics and braking efficiency")
    
    # Load data
    fbr_data = load_fbr_data(JSON_PATH)
    metadata = load_metadata(JSON_PATH)
    
    # Handle nested structure
    if "fbr_analysis" in fbr_data:
        fbr_data = fbr_data.get("fbr_analysis", {})
    
    if not fbr_data:
        st.warning("No FBR data found in JSON file")
        return
    
    # Metrics Dashboard
    st.markdown("### Key Metrics")
    render_metrics_dashboard(fbr_data, metadata)
    
    st.markdown("---")
    
    # AI Assessment Section
    st.markdown("### 🤖 AI Coaching Assessment")
    from utils.assessment import assess_fbr, get_fbr_interpretation
    
    assessment = assess_fbr(fbr_data, metadata)
    
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
        fbr_score = fbr_data.get("fbr_score", 0.0)
        interpretation = get_fbr_interpretation(fbr_score)
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
    
    # Video Section with FBR Overlay
    st.markdown("### Video with FBR Analysis")
    disable_processing = st.checkbox("Disable processing and show original video (safe fallback)", value=False)
    if disable_processing:
        try:
            with open(VIDEO_PATH, "rb") as vf:
                st.video(vf.read())
        except Exception:
            st.video(VIDEO_PATH)
    else:
        with st.spinner("Processing video with FBR annotations..."): 
        from utils.fbr_video_processor import process_video_with_fbr
        from utils.data_loader import load_pose_data
        import tempfile
        
        pose_data = load_pose_data(JSON_PATH)
        
        # Quick OpenCV diagnostic
        try:
            cap_test = cv2.VideoCapture(VIDEO_PATH)
            if not cap_test.isOpened():
                st.warning(f"OpenCV cannot open input video: {VIDEO_PATH}")
            else:
                ret_test, frame_test = cap_test.read()
                st.write(f"OpenCV test read: ret={ret_test}, frame_shape={None if not ret_test else frame_test.shape}")
            cap_test.release()
        except Exception as e:
            st.error(f"OpenCV diagnostic failed: {e}")
            st.code(traceback.format_exc())
        
        # Use temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            output_path = tmp.name
        
        try:
            result = process_video_with_fbr(
                VIDEO_PATH, pose_data, fbr_data, metadata, output_path
            )
        except Exception as e:
            st.error("Processing raised an exception")
            st.code(traceback.format_exc())
            result = None
        
        if result:
            try:
                if isinstance(result, str) and os.path.exists(result):
                    with open(result, "rb") as vf:
                        video_bytes = vf.read()
                    st.video(video_bytes)
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📉 COM Vertical",
        "⚡ Deceleration",
        "🎯 FBR Score",
        "📊 Components",
        "🔄 Combined",
        "🎯 Efficiency Zones",
        "⚙️ Energy Absorption",
        "⏱️ Timing",
        "🏆 Benchmarks",
        "📈 Velocity",
        "💥 Impact Force"
    ])
    
    with tab1:
        from visualizations.fbr_viz import plot_com_vertical_movement
        fig = plot_com_vertical_movement(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Vertical COM position - shows descent after foot plant")
    
    with tab2:
        from visualizations.fbr_viz import plot_deceleration_profile
        fig = plot_deceleration_profile(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Deceleration profile - peak indicates braking force")
    
    with tab3:
        from visualizations.fbr_viz import plot_fbr_score_gauge
        fig = plot_fbr_score_gauge(fbr_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("FBR score gauge - lower is better (efficient braking)")
    
    with tab4:
        from visualizations.fbr_viz import plot_descent_vs_deceleration
        fig = plot_descent_vs_deceleration(fbr_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("FBR components breakdown")
    
    with tab5:
        from visualizations.fbr_viz import plot_combined_analysis
        fig = plot_combined_analysis(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Combined view of COM and deceleration")
    
    with tab6:
        from visualizations.fbr_viz_enhanced import plot_braking_efficiency_zones
        fig = plot_braking_efficiency_zones(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Color-coded efficiency zones based on COM descent")
    
    with tab7:
        from visualizations.fbr_viz_enhanced import plot_energy_absorption
        fig = plot_energy_absorption(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Kinetic energy absorption during braking phase")
    
    with tab8:
        from visualizations.fbr_viz_enhanced import plot_timing_metrics
        fig = plot_timing_metrics(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Timing analysis of braking events")
    
    with tab9:
        from visualizations.fbr_viz_enhanced import plot_benchmark_comparison_fbr
        fig = plot_benchmark_comparison_fbr(fbr_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Compare your FBR score against performance benchmarks")
    
    with tab10:
        from visualizations.fbr_viz_enhanced import plot_velocity_profile
        fig = plot_velocity_profile(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Vertical velocity profile - shows rate of descent")
    
    with tab11:
        from visualizations.fbr_viz_enhanced import plot_impact_force_estimate
        fig = plot_impact_force_estimate(fbr_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Estimated impact force at foot plant")


