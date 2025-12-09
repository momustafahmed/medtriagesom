import pandas as pd
import numpy as np
from joblib import load
import json

# Load model and schema
pipe = load("models/best_pipe.joblib")
le = load("models/label_encoder.joblib")

with open("ui_assets/feature_schema.json", "r") as f:
    schema = json.load(f)

CAT_COLS = schema["cat_cols"]
NUM_COLS = schema["num_cols"]

print("=== MODEL SCHEMA ANALYSIS ===\n")
print(f"Categorical columns ({len(CAT_COLS)}):")
for col in CAT_COLS:
    print(f"  - {col}")

print(f"\nNumeric columns ({len(NUM_COLS)}):")
for col in NUM_COLS:
    print(f"  - {col}")

print("\n=== TESTING MODEL INPUT ===\n")

# Test case 1: Using text "haa"/"maya" (CURRENT IMPLEMENTATION - WRONG)
print("Test 1: Using text 'haa'/'maya' for Has_* flags (CURRENT - LIKELY WRONG)")
test_data_text = {col: np.nan for col in CAT_COLS + NUM_COLS}
test_data_text.update({
    "Age_Group": "qof weyn",
    "Has_Fever": "haa",  # Text
    "Has_Cough": "maya",
    "Has_Headache": "maya",
    "Has_Abdominal_Pain": "maya",
    "Has_Fatigue": "maya",
    "Has_Vomiting": "maya",
    "Fever_Level": "aad u daran",
    "Fever_Duration_Level": "dhexdhexaad",
    "Chills": "haa"
})

df_text = pd.DataFrame([test_data_text])
for col in CAT_COLS:
    df_text[col] = df_text[col].astype("object")

try:
    pred_text = pipe.predict(df_text)[0]
    label_text = le.inverse_transform([pred_text])[0]
    print(f"✓ Prediction: {label_text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test case 2: Using numeric 1/0 (CORRECT IMPLEMENTATION)
print("\nTest 2: Using numeric 1/0 for Has_* flags (CORRECT)")
test_data_num = {col: np.nan for col in CAT_COLS + NUM_COLS}
test_data_num.update({
    "Age_Group": "qof weyn",
    "Has_Fever": 1,  # Numeric
    "Has_Cough": 0,
    "Has_Headache": 0,
    "Has_Abdominal_Pain": 0,
    "Has_Fatigue": 0,
    "Has_Vomiting": 0,
    "Fever_Level": "aad u daran",
    "Fever_Duration_Level": "dhexdhexaad",
    "Chills": "haa"
})

df_num = pd.DataFrame([test_data_num])
for col in CAT_COLS:
    df_num[col] = df_num[col].astype("object")
for col in NUM_COLS:
    df_num[col] = pd.to_numeric(df_num[col], errors="coerce")

try:
    pred_num = pipe.predict(df_num)[0]
    label_num = le.inverse_transform([pred_num])[0]
    print(f"✓ Prediction: {label_num}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== CONCLUSION ===")
print("If both tests work but give different predictions, the app has a bug!")
print("The Has_* flags should be numeric (1/0), not text ('haa'/'maya')")
