# 📡 Churn Intelligence Dashboard

> **A machine learning-powered telecom customer churn prediction dashboard built with Streamlit, Random Forest, and Plotly — featuring SHAP explainability, batch scoring, retention ROI estimation, prediction history logging, and a fully responsive dark/light UI.**

<br>

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-0F828C?style=for-the-badge)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Churn Prediction** | Predict individual customer churn risk with a 3-tier scoring system (Low / Medium / High) |
| 🧠 **SHAP Explainability** | Visualize exactly which features drive each prediction up or down |
| 💰 **Cost Estimator** | Calculate revenue at risk, campaign ROI, and break-even probability |
| 📂 **Batch Analysis** | Upload a CSV to score thousands of customers at once and download results |
| 📋 **Prediction History** | Every prediction is auto-saved to SQLite with trend charts and export |
| 📊 **KPI Banner** | Live dashboard metrics — total predictions, avg risk, high/low risk counts |
| 📄 **PDF Export** | One-click downloadable prediction report per customer |
| 🌙 **Dark / Light Theme** | Toggle between themes with a single button click |
| 📱 **Fully Responsive** | Optimized for desktop, tablet, and mobile screens |

---

## 🖥️ Dashboard Preview

```
📡 Churn Intelligence
─────────────────────────────────────────────────────
  Total Predictions  |  Avg Risk  |  High Risk  |  Low Risk
─────────────────────────────────────────────────────
  🔍 Predict  |  🧠 SHAP  |  💰 Cost  |  📂 Batch  |  📋 History
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/churn-intelligence.git
cd churn-intelligence
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the model
```bash
python train_model.py
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

The app will open at **`http://localhost:8501`**

---

## 📦 Requirements

```txt
streamlit
pandas
numpy
joblib
plotly
scikit-learn
shap
fpdf2
```

> Install all at once: `pip install -r requirements.txt`

---

## 📁 Project Structure

```
churn-intelligence/
│
├── app.py                          # Main Streamlit dashboard
├── train_model.py                  # Model training script
├── requirements.txt                # Python dependencies
│
├── churn_model.pkl                 # Trained Random Forest model (auto-generated)
├── scaler.pkl                      # Feature scaler (auto-generated)
├── columns.pkl                     # Feature column names (auto-generated)
├── churn_history.db                # SQLite prediction log (auto-generated)
│
└── WA_Fn-UseC_-Telco-Customer-Churn.csv   # Dataset (required for training)
```

---

## 🧠 Model Details

| Property | Value |
|---|---|
| **Algorithm** | Random Forest Classifier |
| **Dataset** | IBM Telco Customer Churn |
| **Features** | 24 behavioral & contractual features |
| **Class Balancing** | `class_weight="balanced"` |
| **Explainability** | SHAP TreeExplainer |

### Key Churn Predictors

| Feature | Churn Signal | Why It Matters |
|---|---|---|
| Contract Type | 🔴 Very High | Month-to-month customers churn at ~42% vs ~3% for 2-year |
| Tenure | 🔴 High | Customers < 12 months are 3–5× more likely to churn |
| Monthly Charges | 🟡 Medium | High bills drive price sensitivity, especially on Fiber |
| Tech Support | 🟡 Medium | No support = customers feel abandoned |
| Payment Method | 🟡 Medium | Electronic check users have ~45% higher churn rate |
| Add-on Services | 🔵 Inverse | More add-ons = higher switching costs = lower churn |

---

## 📊 Dashboard Tabs

### 🔍 Predict
Run a prediction for a single customer using sidebar inputs. Displays a risk badge, churn probability gauge, retention recommendations, feature importance chart, and correlation heatmap. Includes one-click PDF export.

### 🧠 SHAP Explainer
Click **Explain This Prediction** to generate a SHAP waterfall chart showing which features increased or decreased churn risk for the current customer profile. Highlights top 3 churn drivers and top 3 retention signals.

### 💰 Cost Estimator
Enter Customer LTV, campaign cost, expected churn reduction %, and discount rate. Outputs revenue at risk, revenue saved, net ROI, and a waterfall chart. Auto-recommends whether the campaign is financially justified.

### 📂 Batch Analysis
Upload a customer CSV. The model scores every row, assigns risk tiers, and displays a risk distribution pie chart and probability histogram. Download the scored file with one click.

### 📋 History
All predictions are auto-logged to a local SQLite database. View a risk trend line over time, risk tier distribution bar chart, full prediction table, and clear/download history.

---

## 🎨 Tech Stack

- **Frontend** — Streamlit + custom CSS (DM Sans font, glassmorphism cards, gradient sidebar)
- **ML Model** — Scikit-Learn Random Forest with balanced class weights
- **Explainability** — SHAP TreeExplainer
- **Charts** — Plotly Express & Graph Objects
- **Storage** — SQLite (prediction history), Pickle (model artifacts)
- **PDF Export** — fpdf2
- **Responsive** — CSS media queries for desktop / tablet / mobile / small phone

---

## 👩‍💻 Author

**Mahreen Begum**

---

## 📄 License

This project is licensed under the MIT License.
