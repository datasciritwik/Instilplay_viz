"""
Cricket Kinematics Analysis - Streamlit App
Main entry point with sidebar navigation for 5 analysis features.
"""
import streamlit as st
import sys
import os

# Add notebook directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Cricket Kinematics Analysis",
    page_icon="🏏",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🏏 Cricket Kinematics")
st.sidebar.markdown("---")

feature = st.sidebar.radio(
    "Select Analysis Feature:",
    [
        "COM Analysis",
        "Kinematics",
        "Hip-Shoulder",
        "Head Stability",
        "FBR"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("**Data**: `data/analysis_output.json`")

# Route to appropriate page
if feature == "COM Analysis":
    from pages import com_page
    com_page.render()
elif feature == "Kinematics":
    from pages import kinematics_page
    kinematics_page.render()
elif feature == "Hip-Shoulder":
    from pages import hip_shoulder_page
    hip_shoulder_page.render()
elif feature == "Head Stability":
    from pages import head_page
    head_page.render()
elif feature == "FBR":
    from pages import fbr_page
    fbr_page.render()
