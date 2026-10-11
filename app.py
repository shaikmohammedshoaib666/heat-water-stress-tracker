import streamlit as st
import json
import sys
import os
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add lambda directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda'))
from app import lambda_handler

def get_ip_geolocation():
    """Get user's location based on IP address (less accurate)"""
    try:
        # Try multiple free IP geolocation APIs
        apis = [
            'http://ip-api.com/json/',
            'https://ipapi.co/json/',
            'https://ipinfo.io/json'
        ]

        for api in apis:
            try:
                response = requests.get(api, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    # Handle different API response formats
                    if 'lat' in data and 'lon' in data:
                        # ip-api.com format
                        return {
                            'lat': data.get('lat'),
                            'lon': data.get('lon'),
                            'city': data.get('city'),
                            'country': data.get('country'),
                            'method': 'IP-based (approximate)'
                        }
                    elif 'latitude' in data:
                        # ipapi.co format
                        return {
                            'lat': data.get('latitude'),
                            'lon': data.get('longitude'),
                            'city': data.get('city'),
                            'country': data.get('country_name') or data.get('country'),
                            'method': 'IP-based (approximate)'
                        }
                    elif 'loc' in data:
                        # ipinfo.io format
                        lat, lon = data['loc'].split(',')
                        return {
                            'lat': float(lat),
                            'lon': float(lon),
                            'city': data.get('city'),
                            'country': data.get('country'),
                            'method': 'IP-based (approximate)'
                        }
            except:
                continue

    except Exception as e:
        st.warning(f"Could not auto-detect location: {e}")
    return None

st.set_page_config(
    page_title="Heat & Water Stress Tracker",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Heat & Water Stress Risk Tracker")
st.markdown("""
Real-time environmental risk assessment using AWS Lambda and weather data.
Built for Environmental Hacks Hackathon.
""")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# API Key input (optional)
api_key = st.sidebar.text_input("OpenWeatherMap API Key (optional)", type="password", help="Leave blank for demo mode with simulated data")

# Data source selection
data_source = st.sidebar.radio("Data Source", ["Manual Input", "Location-based (Real Weather)"])

# Manual Input Section
if data_source == "Manual Input":
    st.header("🌡️ Manual Environmental Data Input")

    col1, col2 = st.columns(2)

    with col1:
        temperature = st.slider("Temperature (°C)", 0, 50, 30)
        humidity = st.slider("Humidity (%)", 0, 100, 60)

    with col2:
        precipitation = st.slider("Precipitation (mm)", 0, 500, 100)
        water_usage = st.slider("Water Usage (units)", 0, 500, 150)

    event_data = {
        'temperature': temperature,
        'humidity': humidity,
        'precipitation': precipitation,
        'water_usage': water_usage
    }

# Location-based Input Section
else:
    st.header("📍 Location-based Weather Data")

    # Popular cities dropdown
    popular_cities = {
        "New Delhi, India": (28.6139, 77.2090),
        "Mumbai, India": (19.0760, 72.8777),
        "Vijayawada, India": (16.5062, 80.6480),
        "Hyderabad, India": (17.3850, 78.4867),
        "Chennai, India": (13.0827, 80.2707),
        "Bangalore, India": (12.9716, 77.5946),
        "New York, USA": (40.7128, -74.0060),
        "London, UK": (51.5074, -0.1278),
        "Tokyo, Japan": (35.6762, 139.6503),
        "Sydney, Australia": (-33.8688, 151.2093)
    }

    selected_city = st.selectbox("🏙️ Quick Select Popular City", ["-- Select a city --"] + list(popular_cities.keys()))

    if selected_city != "-- Select a city --":
        default_lat, default_lon = popular_cities[selected_city]
        st.info(f"✅ Selected: {selected_city}")
    else:
        default_lat = 28.6139
        default_lon = 77.2090

    # Auto-detect location button (with disclaimer)
    col_detect, col_info = st.columns([2, 1])

    with col_detect:
        auto_detect = st.button("🎯 Auto-detect via IP (Approximate)", type="secondary")

    with col_info:
        st.info("⚠️ May be inaccurate")

    location_data = None

    if auto_detect:
        with st.spinner("Detecting your location via IP..."):
            location_data = get_ip_geolocation()
            if location_data:
                method = location_data.get('method', 'IP-based')
                st.warning(f"⚠️ IP-based detection is approximate. Detected: {location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}")
                st.info("💡 For accurate location, use the popular cities dropdown or enter coordinates manually")
                default_lat = location_data['lat'] or 28.6139
                default_lon = location_data['lon'] or 77.2090
            else:
                st.warning("Could not auto-detect. Using default location.")

    col1, col2 = st.columns(2)

    with col1:
        lat = st.number_input("Latitude", value=default_lat, format="%.4f", help="Example: 28.6139 for New Delhi")
        lon = st.number_input("Longitude", value=default_lon, format="%.4f", help="Example: 77.2090 for New Delhi")

    with col2:
        st.info("💡 Get coordinates from Google Maps: Right-click location → Copy coordinates")
        precipitation = st.slider("Precipitation (mm)", 0, 500, 100, help="Manual input for water stress calculation")
        water_usage = st.slider("Water Usage (units)", 0, 500, 150, help="Manual input for water stress calculation")

    event_data = {
        'lat': lat,
        'lon': lon,
        'precipitation': precipitation,
        'water_usage': water_usage,
        'api_key': api_key if api_key else 'demo'
    }

    # Show location info
    if selected_city != "-- Select a city --":
        st.info(f"📍 Using selected city: {selected_city}")
    elif auto_detect and location_data:
        st.info(f"📍 Using IP-detected location: {location_data.get('city', 'Unknown')}, {location_data.get('country', 'Unknown')}")

# Calculate button
if st.button("🚀 Calculate Risk Score", type="primary", use_container_width=True):
    with st.spinner("Fetching weather data and calculating risk scores..."):
        result = lambda_handler(event_data, None)

    if result['statusCode'] == 200:
        data = json.loads(result['body'])

        # Display results
        st.header("📊 Risk Assessment Results")

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Heat Stress", data['heat_stress'],
                     help="Based on temperature and humidity")

        with col2:
            st.metric("Water Stress", data['water_stress'],
                     help="Based on precipitation and usage ratio")

        with col3:
            st.metric("Overall Risk Score", f"{data['overall_risk_score']}/100",
                     help="Combined environmental risk assessment")

        with col4:
            st.metric("Risk Level", data['risk_level'],
                     help="Overall environmental threat level")

        # Risk level banner
        risk_level = data['risk_level']
        if risk_level == "Critical":
            st.error(f"⚠️ CRITICAL RISK LEVEL: {data['overall_risk_score']}/100 - Immediate action required!")
        elif risk_level == "High":
            st.warning(f"⚠️ HIGH RISK LEVEL: {data['overall_risk_score']}/100 - Monitor closely")
        elif risk_level == "Moderate":
            st.info(f"ℹ️ MODERATE RISK LEVEL: {data['overall_risk_score']}/100 - Normal monitoring")
        else:
            st.success(f"✅ LOW RISK LEVEL: {data['overall_risk_score']}/100 - Conditions stable")

        # Input data summary
        st.subheader("📋 Input Data Summary")
        input_df = {
            'Parameter': ['Temperature', 'Humidity', 'Precipitation', 'Water Usage'],
            'Value': [
                f"{data['input_data']['temperature']}°C",
                f"{data['input_data']['humidity']}%",
                f"{data['input_data']['precipitation']}mm",
                f"{data['input_data']['water_usage']} units"
            ]
        }
        st.table(input_df)

        # Forecast visualization (if available)
        if 'forecast' in data and data['forecast']:
            st.subheader("� 3-Day Weather Forecast & Risk Trend")

            forecast_data = data['forecast']
            timestamps = [datetime.fromisoformat(f['timestamp']) for f in forecast_data]
            temperatures = [f['temperature'] for f in forecast_data]
            humidities = [f['humidity'] for f in forecast_data]

            # Create forecast chart
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=timestamps,
                y=temperatures,
                mode='lines+markers',
                name='Temperature (°C)',
                line=dict(color='red', width=2)
            ))

            fig.add_trace(go.Scatter(
                x=timestamps,
                y=humidities,
                mode='lines+markers',
                name='Humidity (%)',
                line=dict(color='blue', width=2),
                yaxis='y2'
            ))

            fig.update_layout(
                title='Temperature & Humidity Forecast',
                xaxis_title='Time',
                yaxis_title='Temperature (°C)',
                yaxis2=dict(
                    title='Humidity (%)',
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        # Risk gauge chart
        st.subheader("🎯 Risk Distribution")
        risk_score = data['overall_risk_score']

        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Risk Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgreen"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))

        st.plotly_chart(fig_gauge, use_container_width=True)

        # Recommendations
        st.header("📋 Recommended Actions")
        for i, rec in enumerate(data['recommendations'], 1):
            st.write(f"**{i}.** {rec}")

        # AWS Usage Section
        st.divider()
        st.subheader("🔧 AWS Integration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **AWS Lambda Function:**
            - Serverless compute for risk calculation
            - Real-time weather API integration
            - Auto-scaling architecture
            - Cost-effective (pay-per-use)
            """)

        with col2:
            st.markdown("""
            **AWS SAM CLI:**
            - Local development environment
            - Infrastructure as Code
            - Easy deployment to AWS
            - No AWS account required for demo
            """)

        st.code("""
# Run Lambda locally with SAM CLI
sam build
sam local invoke HeatWaterStressFunction --event events/test-event.json

# Or test directly with Python
python3 -c "import sys; sys.path.insert(0, 'lambda'); from app import lambda_handler; result = lambda_handler({...}, None); print(result)"
        """, language='bash')

    else:
        st.error("Error calculating risk scores")
        st.json(result)

# Footer
st.divider()
st.markdown("""
---
**🏆 Environmental Hacks Hackathon Submission**

Built with:
- 🌊 Streamlit (Frontend)
- ⚡ AWS Lambda (Serverless Compute)
- 🛠️ AWS SAM CLI (Infrastructure as Code)
- 🌤️ OpenWeatherMap API (Real Weather Data)
- 📊 Plotly (Data Visualization)

Repository: https://github.com/shaikmohammedshoaib666/heat-water-stress-tracker
""")

# Demo mode info
if data_source == "Location-based (Real Weather)" and not api_key:
    st.info("""
    💡 **Demo Mode Active**: Using simulated weather data.
    Add your free OpenWeatherMap API key in the sidebar for real-time weather data.
    Get your key at: https://openweathermap.org/api
    """)
