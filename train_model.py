import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, confusion_matrix, accuracy_score
import joblib
import os
import json
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)

# --- CONFIGURATION ---
DATA_PATH = 'data/loan_data.csv'
MODEL_DIR = 'models'
MODEL_FILENAME = 'ews_model.json' # Single model file
FEATURE_LIST_FILENAME = 'feature_list.pkl'
EVALUATION_FILENAME = 'evaluation_report.json'

# Ensure the models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data_robustly(path: str) -> pd.DataFrame | None:
    print(f"   Attempting to load data from {path}...")
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            df = pd.read_csv(path, encoding=encoding)
            print(f"   Successfully loaded data with {encoding} encoding.")
            return df
        except UnicodeDecodeError: continue
        except FileNotFoundError:
            print(f"FATAL ERROR: Data file not found at {path}.")
            return None
    return None

def train_and_save_model():
    # 1. Load Data
    df = load_data_robustly(DATA_PATH)
    if df is None: return

    # --- 2. Feature Selection and Preprocessing ---
    print("\n2. Preprocessing and Feature Engineering...")
    
    FEATURES = [
        'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'DAYS_BIRTH', 'DAYS_EMPLOYED',
        'NAME_EDUCATION_TYPE', 'EXT_SOURCE_2', 'EXT_SOURCE_3',
        'REGION_POPULATION_RELATIVE', 'DAYS_ID_PUBLISH',
    ]
    TARGET = 'TARGET'

    if TARGET not in df.columns:
        print("FATAL ERROR: TARGET column missing.")
        return

    for col in [f for f in FEATURES if f != 'NAME_EDUCATION_TYPE']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    df = pd.get_dummies(df, columns=['NAME_EDUCATION_TYPE'], dummy_na=False)

    X_final_features = [f for f in FEATURES if f != 'NAME_EDUCATION_TYPE']
    encoded_cols = [col for col in df.columns if 'NAME_EDUCATION_TYPE_' in col]
    X_final_features.extend(encoded_cols)
    X_final_features = [f for f in X_final_features if f in df.columns]

    X = df[X_final_features]
    y = df[TARGET]

    # --- 3. Split Data ---
    print("3. Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # --- 4. Train XGBoost ---
    print("4. Training XGBoost Classifier...")
    scale_pos_weight = y_train.value_counts()[0] / y_train.value_counts()[1]
    
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        n_estimators=300, 
        learning_rate=0.05, 
        max_depth=5,
        scale_pos_weight=scale_pos_weight, 
        random_state=42, 
        use_label_encoder=False, 
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)

    # --- 5. Evaluation ---
    print("5. Evaluating performance...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    y_pred = (y_pred_proba > 0.5).astype(int)
    cm = confusion_matrix(y_test, y_pred).tolist()
    acc = accuracy_score(y_test, y_pred)

    evaluation = {
        'roc_auc': roc_auc,
        'accuracy': acc,
        'confusion_matrix': cm,
        'final_features': X_final_features,
        'model_type': 'XGBoost (Single)'
    }

    print(f"   ROC AUC Score: {roc_auc:.4f}")
    
    # --- 6. Saving Artifacts ---
    print("6. Saving artifacts...")
    
    model.save_model(os.path.join(MODEL_DIR, MODEL_FILENAME))
    joblib.dump(X_final_features, os.path.join(MODEL_DIR, FEATURE_LIST_FILENAME))

    with open(os.path.join(MODEL_DIR, EVALUATION_FILENAME), 'w') as f:
        json.dump(evaluation, f, indent=4)
        
    print("Training complete. XGBoost artifacts saved.")

if __name__ == "__main__":
    train_and_save_model()