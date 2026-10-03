import joblib
import os
import pandas as pd
import xgboost as xgb
import shap
from typing import List, Dict, Any, Optional

# --- CONFIGURATION ---
MODEL_DIR = 'models'
XGB_MODEL_FILENAME = 'ews_xgboost.json'
RF_MODEL_FILENAME = 'ews_rf.joblib'
FEATURE_LIST_FILENAME = 'feature_list.pkl'

# Global variables
_xgb_model: Optional[xgb.XGBClassifier] = None
_rf_model: Optional[Any] = None
_feature_list: Optional[List[str]] = None
_explainer: Optional[shap.TreeExplainer] = None

def load_model_artifacts():
    global _xgb_model, _rf_model, _feature_list, _explainer
    
    xgb_path = os.path.join(MODEL_DIR, XGB_MODEL_FILENAME)
    rf_path = os.path.join(MODEL_DIR, RF_MODEL_FILENAME)
    feat_path = os.path.join(MODEL_DIR, FEATURE_LIST_FILENAME)

    print("\n--- Loading Ensemble Models ---")

    if not os.path.exists(xgb_path) or not os.path.exists(rf_path):
        print("ERROR: Models not found. Run 'python train_model.py' first.")
        return

    try:
        # 1. Load XGBoost
        _xgb_model = xgb.XGBClassifier()
        _xgb_model.load_model(xgb_path)
        print("   [1/2] XGBoost loaded.")
        
        # 2. Load Random Forest
        _rf_model = joblib.load(rf_path)
        print("   [2/2] Random Forest loaded.")
        
        # 3. Load Features
        _feature_list = joblib.load(feat_path)
        print(f"   Feature list loaded ({len(_feature_list)} features).")

        # 4. Initialize SHAP (Using XGBoost for explanations as it's usually cleaner)
        _explainer = shap.TreeExplainer(_xgb_model)
        print("   SHAP Explainer initialized (via XGBoost).")
        print("----------------------------------\n")

    except Exception as e:
        print(f"FATAL ERROR during model loading: {e}")


def predict_risk_and_explain(feature_data: Dict[str, Any]) -> Dict[str, Any]:
    if _xgb_model is None or _rf_model is None:
        return {"error": "Models not loaded."}

    # Prepare Input
    input_df = pd.DataFrame([feature_data])
    for feature in _feature_list:
        if feature not in input_df.columns:
            input_df[feature] = 0.0 
    
    X_predict = input_df[_feature_list]

    # --- ENSEMBLE PREDICTION ---
    # 1. XGBoost Probability
    prob_xgb = _xgb_model.predict_proba(X_predict)[:, 1][0]
    
    # 2. Random Forest Probability
    prob_rf = _rf_model.predict_proba(X_predict)[:, 1][0]
    
    # 3. Average (Ensemble Score)
    # You can weight this! e.g., 0.7*XGB + 0.3*RF if XGB is better.
    # We'll use a simple 50/50 split for stability.
    final_risk_proba = (prob_xgb + prob_rf) / 2
    
    # ---------------------------

    # SHAP Explanations (from XGBoost)
    shap_values = _explainer.shap_values(X_predict)[0]
    
    explanation = []
    feature_shap_map = sorted(zip(_feature_list, shap_values), key=lambda x: abs(x[1]), reverse=True)
    
    for feature, shap_value in feature_shap_map[:5]:
        explanation.append({
            "feature": feature,
            "value": round(float(X_predict[feature].iloc[0]), 3),
            "impact": round(float(shap_value), 4),
            "direction": "Positive" if shap_value > 0 else "Negative" 
        })

    risk_level = "High" if final_risk_proba >= 0.7 else ("Medium" if final_risk_proba >= 0.4 else "Low")
    
    return {
        "risk_score": round(float(final_risk_proba), 4),
        "risk_level": risk_level,
        "explanation": explanation,
        "model_version": "2.0.0-Ensemble(XGB+RF)" # Updated Version!
    }

load_model_artifacts()