import streamlit as st
import json
import subprocess
import sys

st.set_page_config(
    page_title="Heat & Water Stress Tracker",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Heat & Water Stress Risk Tracker")
st.markdown("""
This application calculates environmental risk scores based on heat and water stress data.
Built with AWS SAM CLI for local Lambda simulation.
""")

# Input section
st.header("Environmental Data Input")

col1, col2 = st.columns(2)

with col1:
    temperature = st.slider("Temperature (°C)", 0, 50, 30)
    humidity = st.slider("Humidity (%)", 0, 100, 60)

with col2:
    precipitation = st.slider("Precipitation (mm)", 0, 500, 100)
    water_usage = st.slider("Water Usage (units)", 0, 500, 150)

# Calculate button
if st.button("Calculate Risk Score", type="primary"):
    # Prepare event data for Lambda
    event_data = {
        'temperature': temperature,
        'humidity': humidity,
        'precipitation': precipitation,
        'water_usage': water_usage
    }

    # Call Lambda function directly (for demo without SAM running)
    # In production, this would call the Lambda via boto3 or HTTP
    import sys
    sys.path.insert(0, 'lambda')
    from app import lambda_handler

    with st.spinner("Calculating risk scores..."):
        result = lambda_handler(event_data, None)

    if result['statusCode'] == 200:
        data = json.loads(result['body'])

        # Display results
        st.header("Risk Assessment Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Heat Stress", data['heat_stress'])
            st.caption(f"Temperature: {temperature}°C, Humidity: {humidity}%")

        with col2:
            st.metric("Water Stress", data['water_stress'])
            st.caption(f"Precipitation: {precipitation}mm, Usage: {water_usage}")

        with col3:
            st.metric("Overall Risk Score", f"{data['overall_risk_score']}/100")
            st.metric("Risk Level", data['risk_level'])

        # Risk level color coding
        risk_level = data['risk_level']
        if risk_level == "Critical":
            st.error(f"⚠️ CRITICAL RISK LEVEL: {data['overall_risk_score']}/100")
        elif risk_level == "High":
            st.warning(f"⚠️ HIGH RISK LEVEL: {data['overall_risk_score']}/100")
        elif risk_level == "Moderate":
            st.info(f"ℹ️ MODERATE RISK LEVEL: {data['overall_risk_score']}/100")
        else:
            st.success(f"✅ LOW RISK LEVEL: {data['overall_risk_score']}/100")

        # Recommendations
        st.header("📋 Recommended Actions")
        for i, rec in enumerate(data['recommendations'], 1):
            st.write(f"{i}. {rec}")

        # AWS Usage Section
        st.divider()
        st.subheader("🔧 AWS Integration")
        st.markdown("""
        **AWS SAM CLI Usage:**
        This application uses AWS Serverless Application Model (SAM) CLI to run Lambda functions locally.

        **To run with SAM CLI:**
        ```bash
        sam build
        sam local invoke HeatWaterStressFunction --event events/test-event.json
        ```

        **AWS Services Used:**
        - AWS Lambda (serverless compute)
        - SAM CLI (local development and testing)
        - Environment variables for configuration
        """)

    else:
        st.error("Error calculating risk scores")
        st.json(result)

# Footer
st.divider()
st.markdown("""
---
**Environmental Hacks Hackathon Submission**
Built with Streamlit + AWS SAM CLI
""")

# Demo mode info
st.info("""
💡 **Demo Mode**: Currently running with direct Lambda import for instant testing.
For full AWS demonstration, run `sam build && sam local start-api` and use the API endpoint.
""")
