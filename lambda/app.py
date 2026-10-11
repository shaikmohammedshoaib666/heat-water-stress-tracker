import json
from weather_service import WeatherDataService
from s3_service import S3DataService
from risk_calculator import calculate_risk

def generate_recommendations(heat_stress, water_stress, overall_risk):
    """Generate actionable recommendations based on stress levels"""
    recommendations = []

    if heat_stress in ["Medium", "Critical"]:
        recommendations.extend([
            "Implement heat warning systems",
            "Increase green spaces and shade",
            "Establish cooling centers"
        ])

    if water_stress in ["Medium", "Critical"]:
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

        # Calculate stress levels and scores
        risk = calculate_risk(temperature, humidity, precipitation, water_usage)
        recommendations = generate_recommendations(
            risk['heat_stress'], risk['water_stress'], risk['overall_risk_score']
        )

        # Return results
        result_data = {
            **risk,
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
