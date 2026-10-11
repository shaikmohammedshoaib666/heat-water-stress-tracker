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
from weather_service import WeatherDataService

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

def get_browser_geolocation():
    """Get user's location using browser GPS (accurate)"""
    # This is handled via JavaScript in the UI
    # Streamlit doesn't support two-way binding, so we use session state
    if 'browser_location' in st.session_state:
        return st.session_state['browser_location']
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

    # Auto-detect and fill button
    col_auto, col_info = st.columns([2, 1])

    with col_auto:
        auto_fill_manual = st.button("🎯 Auto-detect & Fill with Real Weather Data", type="primary")

    with col_info:
        st.info("💡 Click to auto-fill")

    # Initialize defaults
    if 'manual_defaults' not in st.session_state:
        st.session_state['manual_defaults'] = {
            'temperature': 30,
            'humidity': 60,
            'precipitation': 100,
            'water_usage': 150
        }

    if auto_fill_manual:
        with st.spinner("Fetching your location and weather data..."):
            # Try to get location via GPS
            location_script = """
            <div id="manual-location-result"></div>
            <script>
            function getManualLocation() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            const lat = position.coords.latitude;
                            const lon = position.coords.longitude;
                            document.getElementById("manual-location-result").innerHTML =
                                '<input type="hidden" id="manual-lat" value="' + lat + '">' +
                                '<input type="hidden" id="manual-lon" value="' + lon + '">';
                        },
                        function(error) {
                            document.getElementById("manual-location-result").innerHTML =
                                '<input type="hidden" id="manual-lat" value="">' +
                                '<input type="hidden" id="manual-lon" value="">';
                        }
                    );
                }
            }
            getManualLocation();
            </script>
            """
            st.components.v1.html(location_script, height=0)

            # Use default location (Vijayawada) for demo
            lat = 16.5062
            lon = 80.6480

            # Fetch weather data
            weather_service = WeatherDataService(api_key if api_key else 'demo')
            weather_data = weather_service.get_current_weather(lat, lon)
            risk_data = weather_service.extract_risk_data(weather_data)

            if risk_data:
                st.session_state['manual_defaults'] = {
                    'temperature': risk_data['temperature'],
                    'humidity': risk_data['humidity'],
                    'precipitation': 100,  # Default for demo
                    'water_usage': 150   # Default for demo
                }
                st.success("✅ Weather data auto-filled! You can adjust values below.")

    col1, col2 = st.columns(2)

    with col1:
        temperature = st.slider(
            "Temperature (°C)",
            0, 50,
            int(st.session_state['manual_defaults']['temperature']),
            help="Current air temperature in your area"
        )
        humidity = st.slider(
            "Humidity (%)",
            0, 100,
            int(st.session_state['manual_defaults']['humidity']),
            help="Amount of moisture in the air (higher = more humid)"
        )

    with col2:
        precipitation = st.slider(
            "Precipitation (mm)",
            0, 500,
            int(st.session_state['manual_defaults']['precipitation']),
            help="Rainfall in millimeters (0 = no rain, 100+ = heavy rain)"
        )
        water_usage = st.slider(
            "Water Usage (units)",
            0, 500,
            int(st.session_state['manual_defaults']['water_usage']),
            help="Daily water consumption (100-200 = average household)"
        )

    event_data = {
        'temperature': temperature,
        'humidity': humidity,
        'precipitation': precipitation,
        'water_usage': water_usage
    }

# Location-based Input Section
else:
    st.header("📍 Location-based Weather Data")

    # Browser GPS location detection
    st.subheader("🎯 Get Your Current Location")

    # JavaScript for browser geolocation
    location_script = """
    <div id="location-result"></div>
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else {
            document.getElementById("location-result").innerHTML = "Geolocation is not supported by this browser.";
        }
    }

    function showPosition(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        document.getElementById("location-result").innerHTML =
            '<div style="color: green; padding: 10px; background: #e8f5e9; border-radius: 5px; margin: 10px 0;">' +
            '✅ Location detected: ' + lat.toFixed(4) + ', ' + lon.toFixed(4) + '<br>' +
            '<small>Copy these coordinates to the fields below</small></div>';

        // Auto-fill the input fields
        const latInput = document.querySelector('input[aria-label="Latitude"]');
        const lonInput = document.querySelector('input[aria-label="Longitude"]');
        if (latInput) latInput.value = lat.toFixed(4);
        if (lonInput) lonInput.value = lon.toFixed(4);

        // Trigger change events
        if (latInput) latInput.dispatchEvent(new Event('input', { bubbles: true }));
        if (lonInput) lonInput.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function showError(error) {
        let message = "";
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = "User denied the request for Geolocation.";
                break;
            case error.POSITION_UNAVAILABLE:
                message = "Location information is unavailable.";
                break;
            case error.TIMEOUT:
                message = "The request to get user location timed out.";
                break;
            default:
                message = "An unknown error occurred.";
        }
        document.getElementById("location-result").innerHTML =
            '<div style="color: red; padding: 10px; background: #ffebee; border-radius: 5px; margin: 10px 0;">' +
            '❌ ' + message + '</div>';
    }

    // Auto-get location on load
    setTimeout(getLocation, 1000);
    </script>
    """

    st.components.v1.html(location_script, height=100)

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

    selected_city = st.selectbox("🏙️ Or Select Popular City", ["-- Select a city --"] + list(popular_cities.keys()))

    if selected_city != "-- Select a city --":
        default_lat, default_lon = popular_cities[selected_city]
    else:
        default_lat = 28.6139
        default_lon = 77.2090

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
