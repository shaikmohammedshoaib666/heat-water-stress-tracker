def calculate_risk(temperature, humidity, precipitation, water_usage):
    """Calculate heat, water, and combined risk scores and levels."""
    if temperature > 35 or (temperature > 30 and humidity > 70):
        heat_score = 100
        heat_stress = "Critical"
    elif temperature > 30:
        heat_score = 50
        heat_stress = "Medium"
    else:
        heat_score = 20
        heat_stress = "Low"

    if precipitation < 10 and water_usage > 120:
        water_score = 100
        water_stress = "Critical"
    elif precipitation < 20 or water_usage > 100:
        water_score = 60
        water_stress = "Medium"
    else:
        water_score = 20
        water_stress = "Low"

    overall_risk_score = (heat_score + water_score) // 2
    if overall_risk_score >= 75:
        risk_level = "Critical"
    elif overall_risk_score >= 50:
        risk_level = "High"
    elif overall_risk_score >= 25:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return {
        "heat_stress": heat_stress,
        "heat_score": heat_score,
        "water_stress": water_stress,
        "water_score": water_score,
        "overall_risk_score": overall_risk_score,
        "risk_level": risk_level,
    }
