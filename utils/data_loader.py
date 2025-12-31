"""
Data loading utilities with caching for cricket kinematics analysis.
"""
import streamlit as st
import json

@st.cache_data
def load_analysis_data(json_path):
    """Load all analysis data from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)

@st.cache_data
def load_com_data(json_path):
    """Load COM (Center of Mass) analysis data."""
    data = load_analysis_data(json_path)
    return data.get("center_of_mass", {}).get("com_analysis", {})

@st.cache_data
def load_pose_data(json_path):
    """Load pose landmarks data for all frames."""
    data = load_analysis_data(json_path)
    return data.get("pose_data", [])

@st.cache_data
def load_metadata(json_path):
    """Load video metadata (fps, dimensions, etc.)."""
    data = load_analysis_data(json_path)
    return data.get("metadata", {})

@st.cache_data
def load_kinematics_data(json_path):
    """Load kinematics analysis data."""
    data = load_analysis_data(json_path)
    return data.get("kinematics", {})

@st.cache_data
def load_hip_shoulder_data(json_path):
    """Load hip-shoulder analysis data."""
    data = load_analysis_data(json_path)
    return data.get("hip_shoulder", {})

@st.cache_data
def load_head_stability_data(json_path):
    """Load head stability analysis data."""
    data = load_analysis_data(json_path)
    head_data = data.get("head_stability", {})
    # Handle nested structure
    if "head_stability" in head_data:
        return head_data.get("head_stability", {})
    return head_data

@st.cache_data
def load_fbr_data(json_path):
    """Load FBR (Front-Back-Release) analysis data."""
    data = load_analysis_data(json_path)
    return data.get("foot_plant_fbr", {})
