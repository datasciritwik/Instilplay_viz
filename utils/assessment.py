"""
Assessment and coaching insights for cricket kinematics analysis.
Provides interpretations and recommendations based on biomechanical data.
"""

def assess_com_performance(com_data, metadata):
    """
    Generate coaching assessment based on COM analysis data.
    
    Args:
        com_data: COM analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Dict with assessment results and recommendations
    """
    com_shift_norm = com_data.get("com_shift_norm", 0.0)
    com_shift_percent = com_data.get("com_shift_percent_width", 0.0)
    stance_width = com_data.get("stance_width_norm", 0.0)
    stance_frame = com_data.get("stance_frame", 0)
    impact_frame = com_data.get("impact_frame", 0)
    fps = metadata.get("fps", 24.0)
    
    # Calculate timing
    delivery_duration = (impact_frame - stance_frame) / fps
    
    assessment = {
        "overall_rating": "",
        "rating_color": "",
        "strengths": [],
        "areas_for_improvement": [],
        "recommendations": [],
        "technical_notes": []
    }
    
    # Assess COM shift magnitude
    if abs(com_shift_percent) < 20:
        assessment["areas_for_improvement"].append(
            "Limited lateral weight transfer - COM shift is less than 20% of stance width"
        )
        assessment["recommendations"].append(
            "Work on driving through the crease with more lateral momentum to generate power"
        )
    elif abs(com_shift_percent) < 40:
        assessment["strengths"].append(
            "Moderate lateral weight transfer - good foundation for power generation"
        )
    else:
        assessment["strengths"].append(
            "Strong lateral weight transfer - excellent use of body momentum"
        )
    
    # Assess stance width
    if stance_width < 0.15:
        assessment["areas_for_improvement"].append(
            "Narrow stance width may limit stability and power generation"
        )
        assessment["recommendations"].append(
            "Consider widening your stance at delivery to create a more stable base"
        )
    elif stance_width > 0.35:
        assessment["areas_for_improvement"].append(
            "Very wide stance may restrict hip rotation and weight transfer"
        )
        assessment["recommendations"].append(
            "Try narrowing your stance slightly to allow better hip drive"
        )
    else:
        assessment["strengths"].append(
            "Good stance width - provides stable base for delivery"
        )
    
    # Assess delivery timing
    if delivery_duration < 0.3:
        assessment["technical_notes"].append(
            "Very quick delivery stride - ensure you're not rushing the action"
        )
    elif delivery_duration > 0.8:
        assessment["technical_notes"].append(
            "Longer delivery stride - may benefit from slightly quicker weight transfer"
        )
    else:
        assessment["strengths"].append(
            "Good delivery timing - balanced weight transfer duration"
        )
    
    # Assess direction of shift
    if com_shift_norm > 0:
        direction = "towards off-side"
    else:
        direction = "towards leg-side"
    
    assessment["technical_notes"].append(
        f"COM shifts {direction} during delivery (typical for most bowlers)"
    )
    
    # Overall rating
    strength_count = len(assessment["strengths"])
    improvement_count = len(assessment["areas_for_improvement"])
    
    if strength_count >= 3 and improvement_count == 0:
        assessment["overall_rating"] = "Excellent"
        assessment["rating_color"] = "green"
    elif strength_count >= 2 and improvement_count <= 1:
        assessment["overall_rating"] = "Good"
        assessment["rating_color"] = "blue"
    elif strength_count >= 1:
        assessment["overall_rating"] = "Developing"
        assessment["rating_color"] = "orange"
    else:
        assessment["overall_rating"] = "Needs Work"
        assessment["rating_color"] = "red"
    
    return assessment

def get_com_interpretation(com_shift_percent):
    """
    Get interpretation of COM shift percentage.
    
    Args:
        com_shift_percent: COM shift as percentage of stance width
    
    Returns:
        String interpretation
    """
    abs_shift = abs(com_shift_percent)
    
    if abs_shift < 15:
        return "Minimal lateral movement - may indicate upright bowling or limited power generation"
    elif abs_shift < 30:
        return "Moderate lateral movement - typical for medium-pace bowlers"
    elif abs_shift < 50:
        return "Strong lateral movement - characteristic of fast bowlers with good momentum"
    else:
        return "Very strong lateral movement - aggressive weight transfer, ensure control is maintained"

def get_benchmark_comparison(com_shift_percent):
    """
    Compare against typical benchmarks for different bowling types.
    
    Args:
        com_shift_percent: COM shift as percentage of stance width
    
    Returns:
        Dict with benchmark comparisons
    """
    abs_shift = abs(com_shift_percent)
    
    benchmarks = {
        "spin_bowler": {"range": (10, 25), "label": "Spin Bowler"},
        "medium_pace": {"range": (25, 40), "label": "Medium Pace"},
        "fast_bowler": {"range": (35, 60), "label": "Fast Bowler"},
    }
    
    matches = []
    for key, data in benchmarks.items():
        if data["range"][0] <= abs_shift <= data["range"][1]:
            matches.append(data["label"])
    
    if not matches:
        if abs_shift < 10:
            return "Below typical ranges - consider increasing lateral drive"
        else:
            return "Above typical ranges - very aggressive weight transfer"
    
    return f"Typical for: {', '.join(matches)}"

def assess_head_stability(head_data, metadata):
    """
    Generate coaching assessment based on head stability analysis.
    
    Args:
        head_data: Head stability data dict
        metadata: Video metadata dict
    
    Returns:
        Dict with assessment results and recommendations
    """
    score = head_data.get("score_0_100", 0.0)
    stance_frame = head_data.get("stance_frame", 0)
    impact_frame = head_data.get("impact_frame", 0)
    head_x = head_data.get("head_x_smooth", [])
    head_y = head_data.get("head_y_smooth", [])
    
    assessment = {
        "overall_rating": "",
        "rating_color": "",
        "strengths": [],
        "areas_for_improvement": [],
        "recommendations": [],
        "technical_notes": []
    }
    
    # Assess stability score
    if score >= 85:
        assessment["overall_rating"] = "Excellent"
        assessment["rating_color"] = "green"
        assessment["strengths"].append(
            f"Exceptional head stability (score: {score:.1f}/100) - minimal unwanted movement"
        )
    elif score >= 70:
        assessment["overall_rating"] = "Good"
        assessment["rating_color"] = "blue"
        assessment["strengths"].append(
            f"Good head stability (score: {score:.1f}/100) - well-controlled movement"
        )
    elif score >= 50:
        assessment["overall_rating"] = "Developing"
        assessment["rating_color"] = "orange"
        assessment["areas_for_improvement"].append(
            f"Moderate head stability (score: {score:.1f}/100) - some unwanted movement detected"
        )
        assessment["recommendations"].append(
            "Focus on keeping your eyes level and head still during delivery stride"
        )
    else:
        assessment["overall_rating"] = "Needs Work"
        assessment["rating_color"] = "red"
        assessment["areas_for_improvement"].append(
            f"Low head stability (score: {score:.1f}/100) - significant head movement affecting accuracy"
        )
        assessment["recommendations"].append(
            "Practice drills focusing on head position - try bowling with a book balanced on your head"
        )
        assessment["recommendations"].append(
            "Work with a coach on maintaining a stable head position through delivery"
        )
    
    # Analyze vertical movement (head dip)
    if len(head_y) > impact_frame:
        delivery_y = head_y[stance_frame:impact_frame+1]
        y_range = max(delivery_y) - min(delivery_y)
        
        if y_range > 0.05:  # Significant vertical movement
            assessment["areas_for_improvement"].append(
                "Noticeable head dip during delivery - may affect line and length consistency"
            )
            assessment["recommendations"].append(
                "Keep your head level throughout the delivery - imagine a string pulling your head up"
            )
        else:
            assessment["strengths"].append(
                "Good vertical head control - minimal dipping during delivery"
            )
    
    # Analyze lateral movement
    if len(head_x) > impact_frame:
        delivery_x = head_x[stance_frame:impact_frame+1]
        x_range = max(delivery_x) - min(delivery_x)
        
        if x_range > 0.04:  # Significant lateral movement
            assessment["technical_notes"].append(
                "Lateral head movement detected - may indicate body alignment issues"
            )
        else:
            assessment["strengths"].append(
                "Minimal lateral head drift - good alignment maintained"
            )
    
    # General coaching notes
    assessment["technical_notes"].append(
        "Head stability is crucial for accuracy - a stable head helps maintain consistent release point"
    )
    
    if score < 70:
        assessment["recommendations"].append(
            "Film yourself from the side and front to identify specific head movement patterns"
        )
    
    return assessment

def get_head_stability_interpretation(score):
    """
    Get interpretation of head stability score.
    
    Args:
        score: Stability score (0-100)
    
    Returns:
        String interpretation
    """
    if score >= 90:
        return "Elite level head stability - comparable to professional fast bowlers"
    elif score >= 80:
        return "Excellent stability - head remains very still through delivery"
    elif score >= 70:
        return "Good stability - minor movements that don't significantly affect accuracy"
    elif score >= 60:
        return "Moderate stability - some head movement that may affect consistency"
    elif score >= 50:
        return "Below average stability - noticeable head movement affecting control"
    else:
        return "Poor stability - significant head movement compromising accuracy and consistency"

def assess_hip_shoulder(hs_data, metadata):
    """
    Generate coaching assessment based on hip-shoulder separation analysis.
    
    Args:
        hs_data: Hip-shoulder analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Dict with assessment results and recommendations
    """
    peak_sep = hs_data.get("peak_separation_deg", 0.0)
    rate_of_sep = hs_data.get("rate_of_separation_deg_per_sec", 0.0)
    
    assessment = {
        "overall_rating": "",
        "rating_color": "",
        "strengths": [],
        "areas_for_improvement": [],
        "recommendations": [],
        "technical_notes": []
    }
    
    # Assess peak separation
    if peak_sep >= 45:
        assessment["strengths"].append(
            f"Excellent hip-shoulder separation ({peak_sep:.1f}°) - generates significant power"
        )
        assessment["overall_rating"] = "Excellent"
        assessment["rating_color"] = "green"
    elif peak_sep >= 35:
        assessment["strengths"].append(
            f"Good hip-shoulder separation ({peak_sep:.1f}°) - solid power generation"
        )
        assessment["overall_rating"] = "Good"
        assessment["rating_color"] = "blue"
    elif peak_sep >= 25:
        assessment["areas_for_improvement"].append(
            f"Moderate hip-shoulder separation ({peak_sep:.1f}°) - room for improvement"
        )
        assessment["recommendations"].append(
            "Work on creating more separation between hips and shoulders during delivery"
        )
        assessment["overall_rating"] = "Developing"
        assessment["rating_color"] = "orange"
    else:
        assessment["areas_for_improvement"].append(
            f"Limited hip-shoulder separation ({peak_sep:.1f}°) - restricting power generation"
        )
        assessment["recommendations"].append(
            "Focus on rotating hips ahead of shoulders - this is crucial for generating pace"
        )
        assessment["recommendations"].append(
            "Practice drills that emphasize hip drive and delayed shoulder rotation"
        )
        assessment["overall_rating"] = "Needs Work"
        assessment["rating_color"] = "red"
    
    # Assess rate of separation
    if rate_of_sep >= 400:
        assessment["strengths"].append(
            f"Explosive separation rate ({rate_of_sep:.0f}°/s) - very dynamic action"
        )
    elif rate_of_sep >= 250:
        assessment["strengths"].append(
            f"Good separation rate ({rate_of_sep:.0f}°/s) - efficient power transfer"
        )
    elif rate_of_sep >= 150:
        assessment["technical_notes"].append(
            f"Moderate separation rate ({rate_of_sep:.0f}°/s) - could be more explosive"
        )
    else:
        assessment["areas_for_improvement"].append(
            f"Slow separation rate ({rate_of_sep:.0f}°/s) - limiting power generation"
        )
        assessment["recommendations"].append(
            "Work on explosive hip rotation to increase separation rate"
        )
    
    # General coaching notes
    assessment["technical_notes"].append(
        "Hip-shoulder separation is the 'X-factor' in fast bowling - hips rotate before shoulders"
    )
    assessment["technical_notes"].append(
        "Greater separation = more elastic energy stored = more ball speed"
    )
    
    return assessment

def get_hip_shoulder_interpretation(peak_sep):
    """
    Get interpretation of hip-shoulder separation angle.
    
    Args:
        peak_sep: Peak separation angle in degrees
    
    Returns:
        String interpretation
    """
    if peak_sep >= 50:
        return "Elite separation - comparable to international fast bowlers"
    elif peak_sep >= 40:
        return "Excellent separation - strong power generation mechanism"
    elif peak_sep >= 30:
        return "Good separation - effective but room for improvement"
    elif peak_sep >= 20:
        return "Moderate separation - limiting potential ball speed"
    else:
        return "Poor separation - significantly restricting power generation"


def assess_fbr(fbr_data, metadata):
    """
    Generate coaching assessment based on FBR analysis.
    
    Args:
        fbr_data: FBR analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Dict with assessment results and recommendations
    """
    fbr_score = fbr_data.get("fbr_score", 0.0)
    peak_decel = fbr_data.get("peak_deceleration", 0.0)
    max_descent = fbr_data.get("max_vertical_descent", 0.0)
    
    assessment = {
        "overall_rating": "",
        "rating_color": "",
        "strengths": [],
        "areas_for_improvement": [],
        "recommendations": [],
        "technical_notes": []
    }
    
    # Assess FBR score (lower is better)
    if fbr_score < 0.01:
        assessment["overall_rating"] = "Excellent"
        assessment["rating_color"] = "green"
        assessment["strengths"].append(
            f"Excellent braking efficiency (FBR: {fbr_score:.4f}) - very controlled foot plant"
        )
    elif fbr_score < 0.02:
        assessment["overall_rating"] = "Good"
        assessment["rating_color"] = "blue"
        assessment["strengths"].append(
            f"Good braking efficiency (FBR: {fbr_score:.4f}) - solid foot plant control"
        )
    elif fbr_score < 0.03:
        assessment["overall_rating"] = "Developing"
        assessment["rating_color"] = "orange"
        assessment["areas_for_improvement"].append(
            f"Moderate braking efficiency (FBR: {fbr_score:.4f}) - room for improvement"
        )
        assessment["recommendations"].append(
            "Work on more explosive braking at foot plant to reduce COM descent"
        )
    else:
        assessment["overall_rating"] = "Needs Work"
        assessment["rating_color"] = "red"
        assessment["areas_for_improvement"].append(
            f"Poor braking efficiency (FBR: {fbr_score:.4f}) - excessive COM descent"
        )
        assessment["recommendations"].append(
            "Focus on stronger, more stable front foot plant"
        )
        assessment["recommendations"].append(
            "Practice drills emphasizing explosive braking and body control"
        )
    
    # Assess deceleration
    if peak_decel > 0.05:
        assessment["strengths"].append(
            f"Strong peak deceleration ({peak_decel:.4f}) - explosive braking action"
        )
    elif peak_decel > 0.03:
        assessment["technical_notes"].append(
            f"Moderate peak deceleration ({peak_decel:.4f})"
        )
    else:
        assessment["areas_for_improvement"].append(
            f"Weak peak deceleration ({peak_decel:.4f}) - insufficient braking force"
        )
        assessment["recommendations"].append(
            "Strengthen leg muscles for more powerful braking at foot plant"
        )
    
    # Assess descent
    if max_descent < 0.01:
        assessment["strengths"].append(
            f"Minimal COM descent ({max_descent:.4f}) - excellent body control"
        )
    elif max_descent > 0.02:
        assessment["areas_for_improvement"].append(
            f"Excessive COM descent ({max_descent:.4f}) - losing height at delivery"
        )
        assessment["recommendations"].append(
            "Maintain upright posture through delivery to minimize COM drop"
        )
    
    # General coaching notes
    assessment["technical_notes"].append(
        "FBR measures braking efficiency - lower score indicates better control"
    )
    assessment["technical_notes"].append(
        "Strong front foot plant is crucial for transferring energy to the ball"
    )
    
    return assessment

def get_fbr_interpretation(fbr_score):
    """
    Get interpretation of FBR score.
    
    Args:
        fbr_score: FBR score value
    
    Returns:
        String interpretation
    """
    if fbr_score < 0.01:
        return "Elite braking efficiency - minimal COM descent with strong deceleration"
    elif fbr_score < 0.02:
        return "Good braking efficiency - well-controlled foot plant"
    elif fbr_score < 0.03:
        return "Moderate efficiency - some COM descent indicating room for improvement"
    else:
        return "Poor efficiency - excessive COM descent relative to braking force"



def assess_kinematics(kin_data, metadata):
    """
    Generate coaching assessment based on kinematics analysis.
    
    Args:
        kin_data: Kinematics analysis data dict
        metadata: Video metadata dict
    
    Returns:
        Dict with assessment results and recommendations
    """
    score = kin_data.get("score", 0.0)
    error = kin_data.get("error_sec", 0.0)
    peaks = kin_data.get("peaks", {})
    
    hip_time = peaks.get("hip_time_sec", 0)
    torso_time = peaks.get("torso_time_sec", 0)
    shoulder_time = peaks.get("shoulder_time_sec", 0)
    
    delay1 = (torso_time - hip_time) * 1000  # ms
    delay2 = (shoulder_time - torso_time) * 1000
    
    assessment = {
        "overall_rating": "",
        "rating_color": "",
        "strengths": [],
        "areas_for_improvement": [],
        "recommendations": [],
        "technical_notes": []
    }
    
    # Assess overall score
    if score >= 90:
        assessment["overall_rating"] = "Elite"
        assessment["rating_color"] = "gold"
        assessment["strengths"].append(
            f"Elite kinematic sequencing (Score: {score:.1f}) - perfect timing coordination"
        )
    elif score >= 80:
        assessment["overall_rating"] = "Excellent"
        assessment["rating_color"] = "green"
        assessment["strengths"].append(
            f"Excellent kinematic sequencing (Score: {score:.1f}) - very good coordination"
        )
    elif score >= 70:
        assessment["overall_rating"] = "Good"
        assessment["rating_color"] = "blue"
        assessment["strengths"].append(
            f"Good kinematic sequencing (Score: {score:.1f}) - effective coordination"
        )
    elif score >= 60:
        assessment["overall_rating"] = "Developing"
        assessment["rating_color"] = "orange"
        assessment["areas_for_improvement"].append(
            f"Developing sequencing (Score: {score:.1f}) - timing issues present"
        )
        assessment["recommendations"].append(
            "Work on coordinating hip, torso, and shoulder rotation timing"
        )
    else:
        assessment["overall_rating"] = "Needs Work"
        assessment["rating_color"] = "red"
        assessment["areas_for_improvement"].append(
            f"Poor sequencing (Score: {score:.1f}) - significant coordination problems"
        )
        assessment["recommendations"].append(
            "Focus on proximal-to-distal sequencing: hips → torso → shoulders"
        )
        assessment["recommendations"].append(
            "Practice drills emphasizing proper kinematic chain activation"
        )
    
    # Assess individual delays
    ideal_delay = 30  # ms
    
    if abs(delay1 - ideal_delay) < 10:
        assessment["strengths"].append(
            f"Excellent hip-torso timing ({delay1:.1f}ms) - near perfect"
        )
    elif abs(delay1 - ideal_delay) > 20:
        assessment["areas_for_improvement"].append(
            f"Hip-torso timing off ({delay1:.1f}ms vs ideal 30ms)"
        )
        assessment["recommendations"].append(
            "Work on delaying torso rotation slightly after hip initiation"
        )
    
    if abs(delay2 - ideal_delay) < 10:
        assessment["strengths"].append(
            f"Excellent torso-shoulder timing ({delay2:.1f}ms) - near perfect"
        )
    elif abs(delay2 - ideal_delay) > 20:
        assessment["areas_for_improvement"].append(
            f"Torso-shoulder timing off ({delay2:.1f}ms vs ideal 30ms)"
        )
        assessment["recommendations"].append(
            "Work on delaying shoulder rotation after torso peaks"
        )
    
    # General coaching notes
    assessment["technical_notes"].append(
        "Kinematic sequencing follows proximal-to-distal pattern: hips lead, shoulders follow"
    )
    assessment["technical_notes"].append(
        "Ideal delay between segments: 30ms (0.03 seconds)"
    )
    assessment["technical_notes"].append(
        "Proper sequencing maximizes energy transfer and ball speed"
    )
    
    return assessment

def get_kinematics_interpretation(score):
    """
    Get interpretation of kinematics score.
    
    Args:
        score: Kinematics sequencing score
    
    Returns:
        String interpretation
    """
    if score >= 90:
        return "Elite sequencing - perfect proximal-to-distal coordination"
    elif score >= 80:
        return "Excellent sequencing - very good timing between segments"
    elif score >= 70:
        return "Good sequencing - effective but room for refinement"
    elif score >= 60:
        return "Developing - timing issues affecting energy transfer"
    else:
        return "Poor sequencing - significant coordination problems limiting performance"




