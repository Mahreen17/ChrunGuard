import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# ── Load dataset ──────────────────────────────────────────────────────────────
df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
df = df.drop("customerID", axis=1)

# ── Fix TotalCharges ──────────────────────────────────────────────────────────
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)

# ── Encode binary columns ─────────────────────────────────────────────────────
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
df["gender"] = df["gender"].map({"Male": 1, "Female": 0})

# ── One-hot encode remaining categoricals ─────────────────────────────────────
cat_cols = ["MultipleLines", "InternetService", "OnlineSecurity",
            "OnlineBackup", "DeviceProtection", "TechSupport",
            "StreamingTV", "StreamingMovies", "Contract", "PaymentMethod"]
df = pd.get_dummies(df, columns=cat_cols)

# ── Binary encode remaining yes/no cols ──────────────────────────────────────
yn_cols = ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]
for c in yn_cols:
    df[c] = df[c].map({"Yes": 1, "No": 0})

# ── Split features / target ───────────────────────────────────────────────────
X = df.drop("Churn", axis=1)
y = df["Churn"]

# Save column names for app.py to use
joblib.dump(X.columns.tolist(), "columns.pkl")
print(f"✅ Saved {len(X.columns)} feature columns")

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Scale ─────────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
joblib.dump(scaler, "scaler.pkl")

# ── Train model ───────────────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)
joblib.dump(model, "churn_model.pkl")

# ── Evaluate ──────────────────────────────────────────────────────────────────
print("\n📊 Test Set Performance:")
print(classification_report(y_test, model.predict(X_test_scaled),
                             target_names=["Stay", "Churn"]))

# ── Feature Importance Summary ────────────────────────────────────────────────
import numpy as np
feat_imp = sorted(zip(X.columns, model.feature_importances_),
                  key=lambda x: x[1], reverse=True)
print("\n🏆 Top 10 Feature Importances:")
for name, imp in feat_imp[:10]:
    print(f"  {name:<45} {imp:.5f}")

print("\n✅ Model, scaler, and columns saved successfully!")
