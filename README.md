# 🌍 Heat & Water Stress Risk Tracker

**Environmental Hacks Hackathon Submission**

A real-time environmental risk assessment platform that leverages AWS Lambda, weather APIs, and data visualization to help communities identify and respond to heat and water stress threats.

## 🎯 Problem Solved

Climate change is increasing the frequency and severity of heat waves and water stress events worldwide. This tool provides:

- **Real-time risk assessment** using live weather data from OpenWeatherMap API
- **Geographic-based analysis** with support for any global location
- **Time-series forecasting** with 3-day weather predictions
- **Actionable recommendations** for mitigating environmental risks
- **Historical data tracking** with AWS S3 storage
- **Interactive visualizations** using Plotly charts and risk gauges

## 🏗️ Architecture

Built with AWS Serverless Application Model (SAM) for scalable, cost-effective deployment:

```
User → Streamlit Frontend → AWS Lambda → OpenWeatherMap API
                              ↓
                         Risk Calculation
                              ↓
                         S3 Storage (Historical Data)
                              ↓
                         Real-time Visualization
```

### Key Components

1. **Streamlit Frontend**: Interactive web interface with real-time data visualization
2. **AWS Lambda**: Serverless compute for risk calculations and weather API integration
3. **OpenWeatherMap API**: Real-time weather data from any global location
4. **AWS S3**: Historical risk data storage and retrieval
5. **Plotly**: Interactive charts and risk gauge visualizations

## 🔧 AWS Services Used

### 1. **AWS Lambda** (Serverless Compute)
- **Purpose**: Core risk calculation logic and weather API integration
- **Location**: `lambda/app.py`
- **Features**:
  - Real-time weather data fetching from OpenWeatherMap API
  - Heat stress index calculation based on temperature & humidity
  - Water stress ratio analysis using precipitation & usage data
  - Overall risk scoring (0-100 scale)
  - Actionable recommendation generation
  - 3-day weather forecast processing
  - Historical data storage via S3 integration

### 2. **AWS S3** (Simple Storage Service)
- **Purpose**: Historical risk data storage and retrieval
- **Location**: `lambda/s3_service.py`
- **Features**:
  - Store risk assessment results with timestamps
  - Location-based data organization
  - Historical trend analysis capability
  - Local fallback mode for demo without AWS credentials

### 3. **AWS SAM CLI** (Local Development)
- **Purpose**: Local development and testing without AWS account
- **Configuration**: `template.yaml`
- **Benefits**:
  - Develop Lambda functions locally
  - Test serverless applications before deployment
  - Simulates AWS Lambda environment
  - Infrastructure as Code

### 4. **External API Integration**
- **OpenWeatherMap API**: Real-time weather data from any global location
- **Geographic coordinates support**: Input lat/lon for any city
- **Demo mode**: Simulated data when API key not provided

## 📦 Project Structure

```
.
├── app.py                    # Streamlit frontend application
├── lambda/
│   ├── app.py               # AWS Lambda function (main logic)
│   ├── weather_service.py   # OpenWeatherMap API integration
│   ├── s3_service.py        # AWS S3 data storage service
│   └── requirements.txt      # Lambda dependencies
├── template.yaml             # AWS SAM template
├── events/
│   └── test-event.json      # Sample Lambda event
├── requirements.txt          # Python dependencies
├── local_data/              # Local storage for demo mode
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip3
- AWS SAM CLI (optional, for full AWS simulation)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ENVIRONMENTAL-HACATHON
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

4. **Get OpenWeatherMap API Key (Optional)**
- Visit https://openweathermap.org/api
- Sign up for free account
- Get your API key
- Enter it in the app sidebar for real weather data
- Without API key, the app uses demo mode with simulated data

## 🌐 Streamlit Cloud Deployment

### Quick Deploy (5 minutes)

1. **Ensure code is on GitHub**
   - Repository: https://github.com/shaikmohammedshoaib666/heat-water-stress-tracker
   - Code is already pushed and ready!

2. **Deploy to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Click "New app"
   - Select your repository: `shaikmohammedshoaib666/heat-water-stress-tracker`
   - Main file: `app.py`
   - Click "Deploy"

3. **That's it!**
   - Streamlit Cloud will automatically:
     - Install dependencies from `requirements.txt`
     - Run the app
     - Provide a public URL
     - Handle HTTPS and scaling

### Your App URL

After deployment, your app will be available at:
`https://shaikmohammedshoaib666-heat-water-stress-tracker-app.streamlit.app`

### AWS Integration on Streamlit Cloud

The app works perfectly on Streamlit Cloud because:
- Lambda functions run locally (Python import)
- Weather API calls work from any environment
- S3 integration has local fallback mode
- No AWS credentials required for demo mode

### For Full AWS Integration (Optional)

If you want to use real AWS S3 on Streamlit Cloud:
1. Add AWS credentials as Streamlit Cloud secrets:
   - In Streamlit Cloud app settings → Secrets
   - Add:
     ```
     AWS_ACCESS_KEY_ID=your_key
     AWS_SECRET_ACCESS_KEY=your_secret
     AWS_REGION=us-east-1
     S3_BUCKET_NAME=your_bucket
     ```
2. The app will automatically use real S3 instead of local storage

## 🧪 Testing Lambda Function

### Direct Python Testing (Quick Start)

The Lambda function can be tested directly without SAM CLI:

```bash
cd /Users/sk.md.shoaib.raza/ENVIRONMENTAL\ HACATHON
python3 -c "import sys; sys.path.insert(0, 'lambda'); from app import lambda_handler; result = lambda_handler({'temperature': 35, 'humidity': 70, 'precipitation': 50, 'water_usage': 200}, None); print(result)"
```

### AWS SAM CLI (Optional Full AWS Simulation)

For complete AWS local simulation, install SAM CLI:

```bash
# macOS (requires Homebrew)
brew tap aws/tap
brew install aws-sam-cli

# Verify installation
sam --version
```

Then run:
```bash
sam build
sam local invoke HeatWaterStressFunction --event events/test-event.json
sam local start-api
```

**Note**: SAM CLI is optional for this submission. The Lambda function works directly and can be demonstrated without it.

## ✨ Key Features

### 1. **Smart Data Input Modes**
- **Manual Input with Auto-detect**: Click button to auto-fill real weather data, then adjust as needed
- **Location-based**: Enter coordinates or use browser GPS for automatic weather data fetching
- **Quick City Selection**: Choose from 10 popular cities worldwide for instant, accurate location
- **User-friendly descriptions**: Each slider explains what the metric means in plain language

### 2. **Real-time Weather Integration**
- Fetches current weather data from OpenWeatherMap API
- Supports any global location via coordinates
- Demo mode with simulated data when API key not provided

### 3. **3-Day Weather Forecast**
- Time-series data visualization
- Temperature and humidity trends
- Risk pattern prediction

### 4. **Interactive Visualizations**
- Risk gauge chart (0-100 scale)
- Temperature & humidity forecast line charts
- Color-coded risk level indicators
- Historical data tables

### 5. **Historical Data Tracking**
- Stores risk assessments in AWS S3
- Location-based data organization
- Enables trend analysis over time
- Local fallback mode for demo

### 6. **Actionable Recommendations**
- Context-aware suggestions based on risk levels
- Heat stress mitigation strategies
- Water conservation measures
- Emergency protocol triggers

### 7. **Popular Cities Quick Selection**
- Pre-loaded 10 major cities worldwide
- Includes major Indian cities (Vijayawada, Hyderabad, Chennai, etc.)
- One-click accurate location selection
- Instant coordinate population
- No manual input or inaccurate IP detection

### 8. **User-Friendly Manual Input** ⭐ NEW
- Auto-detect button fills real weather data automatically
- Plain language descriptions for each metric:
  - Temperature: "Current air temperature in your area"
  - Humidity: "Amount of moisture in the air (higher = more humid)"
  - Precipitation: "Rainfall in millimeters (0 = no rain, 100+ = heavy rain)"
  - Water Usage: "Daily water consumption (100-200 = average household)"
- Users can adjust values after auto-fill
- No technical knowledge required

## 📊 Risk Calculation Logic

### Heat Stress
- **Low**: Temperature < 27°C
- **Moderate**: Temperature 27-32°C, humidity < 60%
- **High**: Temperature 27-32°C, humidity > 60% OR Temperature > 32°C, humidity < 50%
- **Critical**: Temperature > 32°C, humidity > 50%

### Water Stress
Based on water usage to precipitation ratio:
- **Low**: Ratio < 0.5
- **Moderate**: Ratio 0.5-1.0
- **High**: Ratio 1.0-2.0
- **Critical**: Ratio > 2.0

### Overall Risk Score
- Combines heat and water stress (0-100 scale)
- Critical: ≥75
- High: 50-74
- Moderate: 25-49
- Low: <25

## 🎬 Demo Video Script

For the hackathon submission, demonstrate:

1. **Problem Statement** (30 seconds)
   - Show heat/water stress data from recent climate events
   - Explain the need for real-time risk assessment tools
   - Mention climate change impact on communities

2. **Application Demo** (90 seconds)
   - Open Streamlit app
   - **Manual Mode**: Click "Auto-detect & Fill" button
   - Show temperature and humidity auto-filled from real weather
   - Adjust values if needed (user-friendly descriptions shown)
   - **Location Mode**: Select "Vijayawada, India" from dropdown
   - Show coordinates auto-filled instantly
   - Click "Calculate Risk Score"
   - Show real-time weather data fetching
   - Display risk calculation with gauge chart
   - Show 3-day forecast visualization
   - Display actionable recommendations

3. **AWS Integration** (60 seconds)
   - Show Lambda function code with weather API integration
   - Demonstrate Lambda testing: `python3 -c "import sys; sys.path.insert(0, 'lambda'); from app import lambda_handler; result = lambda_handler({'lat': 28.6139, 'lon': 77.2090, 'precipitation': 50, 'water_usage': 200, 'api_key': 'demo'}, None); print(result)"`
   - Show S3 service code for historical data storage
   - Explain AWS Lambda benefits (serverless, scalable, cost-effective)
   - Mention SAM CLI for local development

## 🌱 Future Enhancements

- Integration with additional weather APIs (NOAA, Met Office)
- Geographic data visualization with interactive maps
- Machine learning for risk prediction
- Multi-region comparison dashboard
- Alert notification system via AWS SNS
- Mobile application (React Native)
- Integration with IoT sensors for real-time local data
- Social media sentiment analysis during heat waves

## � What Makes This Innovative

### 1. **Real-time Data Integration**
Unlike static calculators, this system fetches live weather data from OpenWeatherMap API, providing up-to-date risk assessments for any global location.

### 2. **Triple Operation Modes**
- **Demo Mode**: Works without any external dependencies or API keys
- **Production Mode**: Full AWS integration with real data and S3 storage
- **Quick City Mode**: One-click city selection for instant, accurate location

### 3. **Serverless Architecture**
AWS Lambda provides automatic scaling, zero maintenance, and pay-per-use pricing - perfect for hackathon demonstration and real-world deployment.

### 4. **Historical Tracking**
S3 integration enables long-term trend analysis, helping communities understand patterns and plan proactively.

### 5. **Actionable Intelligence**
Not just risk scores - provides specific, contextual recommendations based on the type and severity of environmental threat.

### 6. **Time-Series Forecasting**
3-day weather predictions help communities prepare for upcoming heat or water stress events.

## �📝 Submission Requirements

✅ **Public GitHub Repository** - Complete with README and commit history
✅ **Demo Video** - Under 3 minutes showing working product and AWS usage
✅ **Write-up** - Problem, solution, and AWS usage documentation

## 🤝 Contributing

This project was built for the Environmental Hacks hackathon. For questions or improvements, please open an issue.

## 📄 License

MIT License - Built for Environmental Hacks Hackathon

## 🏆 Hackathon Compliance

- ✅ Uses AWS open-source tools (SAM CLI)
- ✅ Addresses environmental problem (heat & water stress)
- ✅ Working demo with clear AWS integration
- ✅ Follows all hackathon guidelines and norms

---

**Built with ❤️ for Environmental Hacks Hackathon**
