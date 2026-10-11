import streamlit as st
import json
import sys
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add lambda directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda'))
from app import lambda_handler

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

    col1, col2 = st.columns(2)

    with col1:
        lat = st.number_input("Latitude", value=28.6139, format="%.4f", help="Example: 28.6139 for New Delhi")
        lon = st.number_input("Longitude", value=77.2090, format="%.4f", help="Example: 77.2090 for New Delhi")

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
