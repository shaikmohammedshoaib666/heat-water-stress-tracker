import json
from weather_service import WeatherDataService
from s3_service import S3DataService

def calculate_heat_stress(temperature, humidity):
    """Calculate heat stress index based on temperature and humidity"""
    # Simplified heat index calculation
    if temperature < 27:
        return "Low"
    elif temperature < 32:
        if humidity > 60:
            return "High"
        return "Moderate"
    else:
        if humidity > 50:
            return "Critical"
        return "High"

def calculate_water_stress(precipitation, water_usage):
    """Calculate water stress based on precipitation and usage"""
    # Water stress ratio
    stress_ratio = water_usage / (precipitation + 1)
    if stress_ratio < 0.5:
        return "Low"
    elif stress_ratio < 1.0:
        return "Moderate"
    elif stress_ratio < 2.0:
        return "High"
    return "Critical"

def calculate_overall_risk(heat_stress, water_stress):
    """Calculate overall environmental risk score (0-100)"""
    stress_levels = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}
    heat_score = stress_levels.get(heat_stress, 2) * 25
    water_score = stress_levels.get(water_stress, 2) * 25
    return min(heat_score + water_score, 100)

def generate_recommendations(heat_stress, water_stress, overall_risk):
    """Generate actionable recommendations based on stress levels"""
    recommendations = []

    if heat_stress in ["High", "Critical"]:
        recommendations.extend([
            "Implement heat warning systems",
            "Increase green spaces and shade",
            "Establish cooling centers"
        ])

    if water_stress in ["High", "Critical"]:
        recommendations.extend([
            "Implement water conservation measures",
            "Invest in water recycling systems",
            "Monitor groundwater levels regularly"
        ])

    if overall_risk >= 75:
        recommendations.append("Urgent: Declare environmental emergency protocol")

    if not recommendations:
        recommendations.append("Continue monitoring environmental conditions")

    return recommendations

def lambda_handler(event, context):
    """AWS Lambda handler for heat and water stress calculation"""
    try:
        # Parse input data
        body = event if isinstance(event, dict) else json.loads(event)

        # Check if location data provided (for real weather API)
        lat = body.get('lat')
        lon = body.get('lon')
        api_key = body.get('api_key', 'demo')

        if lat and lon:
            # Fetch real weather data
            weather_service = WeatherDataService(api_key)
            weather_data = weather_service.get_current_weather(lat, lon)
            risk_data = weather_service.extract_risk_data(weather_data)

            if risk_data:
                temperature = risk_data['temperature']
                humidity = risk_data['humidity']
                precipitation = body.get('precipitation', risk_data['precipitation'])
                water_usage = body.get('water_usage', risk_data['water_usage'])
            else:
                # Fallback to manual input
                temperature = body.get('temperature', 30)
                humidity = body.get('humidity', 60)
                precipitation = body.get('precipitation', 100)
                water_usage = body.get('water_usage', 150)
        else:
            # Manual input mode
            temperature = body.get('temperature', 30)
            humidity = body.get('humidity', 60)
            precipitation = body.get('precipitation', 100)
            water_usage = body.get('water_usage', 150)

        # Calculate stress levels
        heat_stress = calculate_heat_stress(temperature, humidity)
        water_stress = calculate_water_stress(precipitation, water_usage)
        overall_risk = calculate_overall_risk(heat_stress, water_stress)
        recommendations = generate_recommendations(heat_stress, water_stress, overall_risk)

        # Return results
        result_data = {
            'heat_stress': heat_stress,
            'water_stress': water_stress,
            'overall_risk_score': overall_risk,
            'risk_level': 'Critical' if overall_risk >= 75 else 'High' if overall_risk >= 50 else 'Moderate' if overall_risk >= 25 else 'Low',
            'recommendations': recommendations,
            'input_data': {
                'temperature': temperature,
                'humidity': humidity,
                'precipitation': precipitation,
                'water_usage': water_usage
            }
        }

        # Add forecast data if location provided
        if lat and lon:
            forecast_data = weather_service.get_forecast(lat, lon)
            time_series = weather_service.extract_forecast_data(forecast_data)
            result_data['forecast'] = time_series[:24]  # Next 3 days (8 points per day)

            # Save to S3 for historical tracking
            location_id = f"{lat}_{lon}"
            s3_service = S3DataService()
            save_result = s3_service.save_risk_data(result_data, location_id)
            result_data['storage_info'] = save_result

        response = {
            'statusCode': 200,
            'body': json.dumps(result_data)
        }

        return response

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
