# 🔐 TOR Guard Node Predictor

**ML-based system to predict TOR guard nodes from exit node observations using XGBoost, LightGBM, and CatBoost ensemble with SHAP explainability.**

> **Built for:** Tamil Nadu Police Cyber Crime Wing Hackathon 2025  
> **Purpose:** Law enforcement tool for TOR network traffic analysis and cybercrime investigation

---

## 🎯 Overview

This system uses machine learning to predict which guard nodes were likely used in a TOR circuit when given exit node information. It helps law enforcement trace TOR network paths for cybercrime investigations by identifying entry points into the TOR network.

### Key Features

- ✅ **Multi-Model Ensemble:** Combines XGBoost, LightGBM, and CatBoost for 96% Top-10 accuracy
- ✅ **Explainable AI (XAI):** SHAP-based feature importance and prediction explanations
- ✅ **Counterfactual Analysis:** Interactive what-if scenario testing
- ✅ **Real-time Predictions:** FastAPI backend with React frontend
- ✅ **75 Engineered Features:** Advanced network traffic pattern analysis
- ✅ **Professional UI:** 4 comprehensive tabs for prediction, XAI, analysis, and metrics

---

## 📊 Model Performance

| Model | Top-1 Accuracy | Top-5 Accuracy | Top-10 Accuracy | Inference Time |
|-------|----------------|----------------|-----------------|----------------|
| XGBoost | ~70% | ~89% | ~94% | 25ms |
| LightGBM | ~72% | ~90% | ~95% | 18ms |
| CatBoost | ~73% | ~91% | ~96% | 35ms |
| **Ensemble** | **~75%** | **~92%** | **~96%** | **45ms** |

---

## 🚀 Quick Start

### Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 16.0 or higher
- **Git:** For version control
- **RAM:** Minimum 8GB (16GB recommended)
- **OS:** Windows 10/11, Linux, macOS

### Installation

**1. Clone the repository:**
``````bash
git clone https://github.com/YOUR_USERNAME/tor-guard-predictor.git
cd tor-guard-predictor
``````

**2. Setup Python environment:**
``````bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r backend/requirements.txt
``````

**3. Train models (or use pre-trained):**
``````bash
python scripts/01_analyze_data.py
python scripts/02_engineer_features.py
python scripts/03_train_xgboost.py
python scripts/04_train_lightgbm.py
python scripts/05_train_catboost.py
python scripts/06_create_ensemble.py
python scripts/07_generate_shap_values.py
``````

**4. Install frontend dependencies:**
``````bash
cd frontend
npm install
``````

### Running the Application

**Terminal 1 - Start Backend:**
``````bash
cd tor-guard-predictor
venv\Scripts\activate  # Windows
python -m backend.main
``````

**Terminal 2 - Start Frontend:**
``````bash
cd tor-guard-predictor/frontend
npm start
``````

**Access the application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🏗️ Architecture

``````
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React UI      │─────▶│  FastAPI Backend │─────▶│  ML Ensemble    │
│  (Port 3000)    │      │   (Port 8000)    │      │  XGBoost        │
│                 │      │                  │      │  LightGBM       │
│ • Prediction    │      │ • /predict       │      │  CatBoost       │
│ • XAI           │      │ • /explain       │      └─────────────────┘
│ • Counterfactual│      │ • /counterfactual│              │
│ • Analytics     │      │ • /models        │      ┌───────▼───────┐
└─────────────────┘      └──────────────────┘      │ SHAP Explainer│
                                                    │ Feature Eng.  │
                                                    └───────────────┘
``````

---

## 📁 Project Structure

``````
tor-guard-predictor/
├── backend/                 # FastAPI backend
│   ├── api/                 # REST API endpoints
│   │   ├── predict.py       # Prediction endpoint
│   │   ├── explain.py       # XAI explanations
│   │   ├── counterfactual.py
│   │   ├── models.py
│   │   └── health.py
│   ├── core/                # Business logic
│   │   ├── model_loader.py  # Model management
│   │   └── feature_engineering.py
│   ├── config.py            # Configuration
│   └── main.py              # Entry point
│
├── frontend/                # React frontend
│   ├── public/
│   └── src/
│       ├── components/      # UI components
│       ├── App.js           # Main application
│       └── App.css          # Styling
│
├── models/                  # Trained ML models
│   ├── xgboost/
│   │   └── model.json
│   ├── lightgbm/
│   │   └── model.pkl
│   ├── catboost/
│   │   └── model.cbm
│   ├── ensemble/
│   │   └── weights.pkl
│   └── shap/
│       └── explainer.pkl
│
├── data/                    # Training data
│   ├── raw/
│   │   └── circuit_data_raw.csv
│   └── processed/
│       └── circuit_data_processed.csv
│
├── scripts/                 # Training scripts
│   ├── 01_analyze_data.py
│   ├── 02_engineer_features.py
│   ├── 03_train_xgboost.py
│   ├── 04_train_lightgbm.py
│   ├── 05_train_catboost.py
│   ├── 06_create_ensemble.py
│   └── 07_generate_shap_values.py
│
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── .gitignore
└── README.md
``````

---

## 🎓 Use Cases

### 1. **Cybercrime Investigation**
Identify potential TOR guard nodes for ISP subpoena requests when investigating criminal activities conducted through TOR.

### 2. **Network Traffic Analysis**
Understand TOR circuit construction patterns for law enforcement traffic analysis and monitoring.

### 3. **Forensic Evidence**
Generate machine learning-backed predictions with explainability for use in legal proceedings.

### 4. **Pattern Detection**
Detect recurring guard-exit node pairings that might indicate specific threat actors or criminal networks.

---

## 🔬 Technical Details

### Feature Engineering (75 Features)

**Network Metrics:**
- Guard/Middle/Exit bandwidth
- Circuit setup duration
- Total bytes transferred
- Bandwidth ratios and products

**Geographic Features:**
- Country encodings
- Geographic distance calculations
- Regional patterns

**Temporal Features:**
- Time-based patterns
- Circuit lifetime
- Historical co-occurrence

**Statistical Features:**
- Log transformations
- Polynomial features
- Interaction terms

### Models

**XGBoost:**
- Tree-based gradient boosting
- Fast training and inference
- Handles missing values well

**LightGBM:**
- Leaf-wise tree growth
- Fastest inference speed
- Memory efficient

**CatBoost:**
- Categorical feature handling
- Highest single-model accuracy
- Built-in overfitting protection

**Ensemble:**
- Weighted average (XGBoost: 40%, LightGBM: 30%, CatBoost: 30%)
- Combines strengths of all models
- Best overall performance

---

## 📡 API Endpoints

### **POST /predict**
Predict guard nodes from exit node features
``````json
{
  "exit_ip": "45.33.32.156",
  "exit_country": "DE",
  "bandwidth": 7.5,
  "circuit_setup_duration": 2.0,
  "total_bytes": 500000,
  "model_id": "ensemble",
  "top_k": 10
}
``````

### **POST /explain**
Get SHAP explanation for prediction
``````json
{
  "input_features": {...},
  "guard_index": 42,
  "model_id": "xgboost"
}
``````

### **POST /counterfactual**
Analyze what-if scenarios
``````json
{
  "original_input": {...},
  "modified_features": {...},
  "model_id": "ensemble"
}
``````

### **GET /models**
List available models

---

## 🛡️ Legal & Ethical Considerations

**⚠️ IMPORTANT DISCLAIMER:**

This tool is designed **exclusively for law enforcement use** in authorized cybercrime investigations. Users must:

- ✅ Have legal authority to investigate TOR traffic
- ✅ Comply with local data protection and privacy laws
- ✅ Follow proper warrant and subpoena procedures
- ✅ Use predictions as investigative leads, not conclusive evidence
- ✅ Understand model limitations and accuracy bounds

**This tool should NOT be used for:**
- ❌ Unauthorized surveillance
- ❌ Privacy violations
- ❌ Targeting individuals without legal basis
- ❌ Circumventing legal protections

---

## 🔧 Configuration

Edit **backend/config.py** to customize:

``````python
# Model paths
XGBOOST_MODEL = Path("models/xgboost/model.json")
LIGHTGBM_MODEL = Path("models/lightgbm/model.pkl")
CATBOOST_MODEL = Path("models/catboost/model.cbm")

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Prediction settings
DEFAULT_TOP_K = 10
MAX_TOP_K = 20
``````

---

## 🧪 Testing

**Run backend tests:**
``````bash
pytest backend/tests/
``````

**Run frontend tests:**
``````bash
cd frontend
npm test
``````

**API testing:**
``````bash
# Using curl
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"exit_ip":"45.33.32.156","model_id":"ensemble"}'
``````

---

## 🤝 Contributing

This is a hackathon project for Tamil Nadu Police Cyber Crime Wing. For production deployment or collaboration:

1. Fork the repository
2. Create a feature branch (``git checkout -b feature/improvement``)
3. Commit changes (``git commit -m 'Add improvement'``)
4. Push to branch (``git push origin feature/improvement``)
5. Open a Pull Request

---

## 📜 License

**For Law Enforcement and Educational Use Only**

This project is provided for:
- ✅ Law enforcement agencies with proper authorization
- ✅ Academic research and education
- ✅ Cybersecurity training and awareness

Not licensed for commercial use or unauthorized surveillance.

---

## 🙏 Acknowledgments

- **Tamil Nadu Police Cyber Crime Wing** - For organizing the hackathon
- **TOR Project** - For network architecture understanding
- **SHAP Library** - For explainable AI capabilities
- **Scikit-learn, XGBoost, LightGBM, CatBoost** - Machine learning frameworks

---

## 👥 Team

**Built for Tamil Nadu Police Cyber Crime Wing Hackathon 2025**

For questions or collaboration: hamsavardan.m2023@vitstudent.ac.in

---

## 📈 Future Enhancements

- [ ] Real-time TOR network data integration
- [ ] Advanced visualization dashboards
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Integration with existing law enforcement systems
- [ ] Enhanced SHAP visualizations
- [ ] Automated report generation
- [ ] Historical pattern analysis

---

## 🐛 Known Issues

- Large dataset loading may take 30-60 seconds on first startup
- Model files require ~500MB disk space
- React dev server shows deprecation warnings (doesn't affect functionality)

---

## 📞 Support

For issues, questions, or feature requests:
- **GitHub Issues:** https://github.com/YOUR_USERNAME/tor-guard-predictor/issues
- **Email:** hamsavardan.m2023@vitstudent.ac.in

---

**⭐ If this project helps your investigation or research, please star the repository!**

---

*Last Updated: December 2025*
