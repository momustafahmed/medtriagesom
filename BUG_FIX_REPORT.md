# Critical Bug Fix Report - Medical Triage App

## Date: December 9, 2025

## Summary
Fixed a **critical data type mismatch** between the app and the ML model that was causing prediction errors.

---

## Problem Identified

### The Bug
The app was sending **text values** (`"haa"`/`"maya"`) for the `Has_*` symptom flags, but the model expects **numeric values** (`1`/`0`).

### Affected Features
- `Has_Fever`
- `Has_Cough`
- `Has_Headache`
- `Has_Abdominal_Pain`
- `Has_Fatigue`
- `Has_Vomiting`

### Error Message
```
ValueError: could not convert string to float: 'haa'
```

---

## Root Cause Analysis

### Model Schema (from `ui_assets/feature_schema.json`)
```json
{
  "num_cols": [
    "Has_Fever",
    "Has_Cough",
    "Has_Headache",
    "Has_Abdominal_Pain",
    "Has_Fatigue",
    "Has_Vomiting"
  ]
}
```

The schema clearly defines `Has_*` flags as **numeric columns**, not categorical.

### Incorrect Implementation (BEFORE)
```python
# Setting default values
payload.setdefault(flag, "maya")  # ❌ WRONG - text value

# When symptom selected
payload[cfg["flag"]] = "haa"  # ❌ WRONG - text value

# Checking fever + fatigue
if (payload.get("Has_Fever") == "haa") and ...  # ❌ WRONG
```

---

## Solution Applied

### Correct Implementation (AFTER)
```python
# Setting default values
payload.setdefault(flag, 0)  # ✅ CORRECT - numeric 0 for "no"

# When symptom selected
payload[cfg["flag"]] = 1  # ✅ CORRECT - numeric 1 for "yes"

# Checking fever + fatigue
if (payload.get("Has_Fever") == 1) and ...  # ✅ CORRECT
```

### Changes Made
1. **Default values**: Changed from `"maya"` → `0`
2. **Selected symptoms**: Changed from `"haa"` → `1`
3. **Conditional checks**: Updated to compare with `1` instead of `"haa"`
4. **Code comments**: Added clarifications about numeric values

---

## Testing

### Test Results
```
Test 1: Using text 'haa'/'maya' (BEFORE FIX)
❌ Error: could not convert string to float: 'haa'

Test 2: Using numeric 1/0 (AFTER FIX)
✅ Prediction: Xaalad dhax dhaxaad eh (Bukaan socod)
```

---

## Impact

### Before Fix
- App would crash with ValueError when making predictions
- Model could not process user input
- Triage results were unavailable

### After Fix
- App works correctly with proper numeric input
- Model processes data as expected
- Users receive accurate triage predictions

---

## Data Flow Diagram

```
User Selection
     ↓
Symptom Selected (UI)
     ↓
Has_* flag = 1 (numeric) ← FIXED
     ↓
payload dictionary
     ↓
make_input_df() → DataFrame
     ↓
Model Prediction
     ↓
Triage Result
```

---

## Recommendations

1. **Add input validation** to catch data type mismatches early
2. **Update unit tests** to verify correct data types
3. **Consider retraining model** with current scikit-learn version (1.6.1 vs 1.4.2)
4. **Add logging** to track data transformations

---

## Files Modified
- `app.py` (lines 450-495)

## Test File Created
- `test_model.py` (validation script)

---

## Conclusion
The bug has been successfully fixed. The app now correctly sends numeric values (`1`/`0`) for symptom flags, matching the model's expected input format. The app is running properly at http://localhost:8501.
