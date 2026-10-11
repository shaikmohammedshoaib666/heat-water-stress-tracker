# 🌍 Heat & Water Stress Risk Tracker

**Environmental Hacks Hackathon Submission**

A web application that calculates environmental risk scores based on heat and water stress data, helping communities identify and respond to environmental threats.

## 🎯 Problem Solved

Climate change is increasing the frequency and severity of heat waves and water stress events worldwide. This tool provides:

- **Real-time risk assessment** based on temperature, humidity, precipitation, and water usage data
- **Actionable recommendations** for mitigating environmental risks
- **Early warning system** for critical environmental conditions

## 🏗️ Architecture

Built with AWS Serverless Application Model (SAM) for scalable, cost-effective deployment:

```
Streamlit Frontend → AWS Lambda (Risk Calculation) → Risk Score & Recommendations
                          ↓
                    Local Development (SAM CLI)
```

## 🔧 AWS Services Used

### 1. **AWS Lambda** (Serverless Compute)
- **Purpose**: Core risk calculation logic
- **Location**: `lambda/app.py`
- **Features**:
  - Heat stress index calculation
  - Water stress ratio analysis
  - Overall risk scoring (0-100)
  - Actionable recommendation generation

### 2. **AWS SAM CLI** (Local Development)
- **Purpose**: Local development and testing without AWS account
- **Configuration**: `template.yaml`
- **Benefits**:
  - Develop Lambda functions locally
  - Test serverless applications before deployment
  - Simulates AWS Lambda environment

### 3. **Environment Variables**
- Configurable environment settings
- Easy deployment between dev/prod

## 📦 Project Structure

```
.
├── app.py                 # Streamlit frontend application
├── lambda/
│   ├── app.py            # AWS Lambda function
│   └── requirements.txt  # Lambda dependencies
├── template.yaml         # AWS SAM template
├── events/
│   └── test-event.json   # Sample Lambda event
├── requirements.txt      # Python dependencies
└── README.md            # This file
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
   - Explain the need for risk assessment tools

2. **Application Demo** (90 seconds)
   - Open Streamlit app
   - Input sample environmental data
   - Show risk calculation in real-time
   - Display recommendations

3. **AWS Integration** (60 seconds)
   - Show SAM CLI terminal running `sam build`
   - Demonstrate `sam local invoke` with test event
   - Show Lambda function code
   - Explain AWS Lambda benefits (serverless, scalable, cost-effective)

## 🌱 Future Enhancements

- Integration with real-time weather APIs
- Geographic data visualization
- Historical trend analysis
- Multi-region support
- Alert notification system
- Mobile application

## 📝 Submission Requirements

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
