"""
Kinematics Analysis Page
Displays kinematic sequencing analysis with hip-torso-shoulder coordination.
"""
import streamlit as st
import os
from utils.data_loader import load_kinematics_data, load_metadata

# Constants
VIDEO_PATH = "data/video_preview_h264.mp4"
JSON_PATH = "data/analysis_output.json"

def render_metrics_dashboard(kin_data, metadata):
    """Render metrics dashboard with key kinematics statistics."""
    fps = metadata.get("fps", 24.0)
    
    score = kin_data.get("score", 0.0)
    error = kin_data.get("error_sec", 0.0)
    peaks = kin_data.get("peaks", {})
    
    hip_frame = peaks.get("hip_frame", 0)
    torso_frame = peaks.get("torso_frame", 0)
    shoulder_frame = peaks.get("shoulder_frame", 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Sequencing Score",
            f"{score:.1f}/100",
            delta="Excellent" if score >= 80 else "Good" if score >= 70 else "Needs Work",
            help="Overall kinematic sequencing quality (higher is better)"
        )
    
    with col2:
        st.metric(
            "Timing Error",
            f"{error*1000:.1f}ms",
            delta="Low" if error < 0.02 else "High",
            delta_color="inverse",
            help="Deviation from ideal 30ms delays"
        )
    
    with col3:
        delay1 = (torso_frame - hip_frame) / fps * 1000
        st.metric(
            "Hip → Torso",
            f"{delay1:.1f}ms",
            delta=f"Ideal: 30ms",
            help="Delay between hip and torso peaks"
        )
    
    with col4:
        delay2 = (shoulder_frame - torso_frame) / fps * 1000
        st.metric(
            "Torso → Shoulder",
            f"{delay2:.1f}ms",
            delta=f"Ideal: 30ms",
            help="Delay between torso and shoulder peaks"
        )

def render():
    """Main render function for kinematics analysis page."""
    st.title("🔄 Kinematic Sequencing Analysis")
    st.markdown("Analyze hip → torso → shoulder rotation coordination")
    
    # Load data
    kin_data = load_kinematics_data(JSON_PATH)
    metadata = load_metadata(JSON_PATH)
    
    # Handle nested structure
    if "kinematic_sequencing" in kin_data:
        kin_data = kin_data.get("kinematic_sequencing", {})
    
    if not kin_data:
        st.warning("No kinematics data found in JSON file")
        return
    
    # Metrics Dashboard
    st.markdown("### Key Metrics")
    render_metrics_dashboard(kin_data, metadata)
    
    st.markdown("---")
    
    # AI Assessment Section
    st.markdown("### 🤖 AI Coaching Assessment")
    from utils.assessment import assess_kinematics, get_kinematics_interpretation
    
    assessment = assess_kinematics(kin_data, metadata)
    
    # Overall rating
    col1, col2 = st.columns([1, 3])
    with col1:
        rating_emoji = {
            "Elite": "👑",
            "Excellent": "🌟",
            "Good": "👍",
            "Developing": "📈",
            "Needs Work": "⚠️"
        }
        st.markdown(f"## {rating_emoji.get(assessment['overall_rating'], '📊')} {assessment['overall_rating']}")
    
    with col2:
        score = kin_data.get("score", 0.0)
        interpretation = get_kinematics_interpretation(score)
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
    
    # Video Section with Kinematics Overlay
    st.markdown("### Video with Kinematic Sequencing")
    
    with st.spinner("Processing video with kinematics annotations..."):
        from utils.kinematics_video_processor import process_video_with_kinematics
        from utils.data_loader import load_pose_data
        import tempfile
        
        pose_data = load_pose_data(JSON_PATH)
        
        # Use temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            output_path = tmp.name
        
        result = process_video_with_kinematics(
            VIDEO_PATH, pose_data, kin_data, metadata, output_path
        )
        
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16 = st.tabs([
        "📈 Velocity Timeline",
        "💧 Waterfall",
        "⏱️ Timing Diagram",
        "🎯 Score Gauge",
        "📊 Velocity Comparison",
        "🎨 Sequencing Zones",
        "⚡ Energy Transfer",
        "📉 Timing Deviation",
        "🏆 Benchmarks",
        "🎯 Coordination Index",
        "🔍 Segment Comparison",
        "🌐 3D Rotation",
        "🔄 Phase Portrait",
        "⚙️ Power Flow",
        "🔥 Timing Heatmap",
        "💎 Efficiency Breakdown"
    ])
    
    with tab1:
        from visualizations.kinematics_viz import plot_angular_velocity_timeline
        fig = plot_angular_velocity_timeline(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Angular velocities of hip, torso, and shoulder - shows sequencing pattern")
    
    with tab2:
        from visualizations.kinematics_viz import plot_sequencing_waterfall
        fig = plot_sequencing_waterfall(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Cascade showing hip → torso → shoulder peak progression")
    
    with tab3:
        from visualizations.kinematics_viz import plot_timing_diagram
        fig = plot_timing_diagram(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Delays between segment peaks (ideal: 30ms each)")
    
    with tab4:
        from visualizations.kinematics_viz import plot_sequencing_score_gauge
        fig = plot_sequencing_score_gauge(kin_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Overall sequencing quality score")
    
    with tab5:
        from visualizations.kinematics_viz import plot_velocity_comparison
        fig = plot_velocity_comparison(kin_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Peak velocities by body segment")
    
    with tab6:
        from visualizations.kinematics_viz_enhanced import plot_sequencing_zones
        fig = plot_sequencing_zones(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Color-coded zones showing dominant segment by phase")
    
    with tab7:
        from visualizations.kinematics_viz_enhanced import plot_energy_transfer_efficiency
        fig = plot_energy_transfer_efficiency(kin_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Energy distribution across segments")
    
    with tab8:
        from visualizations.kinematics_viz_enhanced import plot_timing_deviation
        fig = plot_timing_deviation(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Deviation from ideal 30ms delays")
    
    with tab9:
        from visualizations.kinematics_viz_enhanced import plot_benchmark_comparison_kin
        fig = plot_benchmark_comparison_kin(kin_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Compare your sequencing score against benchmarks")
    
    with tab10:
        from visualizations.kinematics_viz_enhanced import plot_coordination_index
        fig = plot_coordination_index(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Overall coordination quality metrics")
    
    with tab11:
        from visualizations.kinematics_viz_enhanced import plot_segment_comparison
        fig = plot_segment_comparison(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Detailed comparison of all three segments")
    
    with tab12:
        from visualizations.kinematics_viz_ultra import plot_3d_rotation_animation
        fig = plot_3d_rotation_animation(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("3D visualization of rotation trajectories through time")
    
    with tab13:
        from visualizations.kinematics_viz_ultra import plot_phase_portrait
        fig = plot_phase_portrait(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Phase space analysis - velocity vs acceleration for each segment")
    
    with tab14:
        from visualizations.kinematics_viz_ultra import plot_power_flow_diagram
        fig = plot_power_flow_diagram(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Sankey diagram showing energy flow through kinematic chain")
    
    with tab15:
        from visualizations.kinematics_viz_ultra import plot_comparative_timing_heatmap
        fig = plot_comparative_timing_heatmap(kin_data, metadata)
        st.plotly_chart(fig, width='stretch')
        st.caption("Heatmap comparing actual vs ideal timing patterns")
    
    with tab16:
        from visualizations.kinematics_viz_ultra import plot_efficiency_score_breakdown
        fig = plot_efficiency_score_breakdown(kin_data)
        st.plotly_chart(fig, width='stretch')
        st.caption("Polar chart breaking down efficiency score components")



