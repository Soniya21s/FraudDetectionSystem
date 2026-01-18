import numpy as np
import pandas as pd
from joblib import load
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "fraud_xgb_model.joblib"
THRESHOLD_PATH = BASE_DIR / "models" / "fraud_threshold.joblib"
FEATURE_NAMES_PATH = BASE_DIR / "models" / "feature_names.joblib"
OHE_PATH = BASE_DIR / "models" / "ohe_encoder.joblib"

# Load artifacts once (important for performance)
model = load(MODEL_PATH)
threshold = load(THRESHOLD_PATH)
feature_names = load(FEATURE_NAMES_PATH)
ohe = load(OHE_PATH)



AGE_MAP = {
    "18-25": 1,
    "26-35": 2,
    "36-45": 3,
    "46-55": 4,
    "56+": 5
}

DEVICE_RISK_MAP = {
    "Web": "High",
    "Android": "Medium",
    "iOS": "Low"
}

NETWORK_RISK_MAP = {
    "WiFi": "High",
    "3G": "Medium",
    "4G": "Low",
    "5G": "Low"
}

# ===============================
# 3️⃣ Feature Engineering
# ===============================


def age_to_group(age: int) -> str:
    if age < 18:
        raise ValueError("Age must be >= 18")
    elif age <= 25:
        return "18-25"
    elif age <= 35:
        return "26-35"
    elif age <= 45:
        return "36-45"
    elif age <= 55:
        return "46-55"
    else:
        return "56+"


def build_features(input_data: dict) -> pd.DataFrame:
    """
    Convert raw input dict into a single-row DataFrame
    with engineered features (before encoding).
    """

    COLUMN_RENAME_MAP = {
    "transaction type": "transaction type",
    "merchant_category": "merchant_category",
    "amount": "amount",
    "sender_age": "sender_age",
    "receiver_age": "receiver_age",
    "sender_state": "sender_state",
    "sender_bank": "sender_bank",
    "receiver_bank": "receiver_bank",
    "device_type": "device_type",
    "network_type": "network_type",
    "transaction_status": "transaction_status",
    "hour_of_day": "hour_of_day",
    "day_of_week": "day_of_week",
    "is_weekend": "is_weekend"
    }

    df = pd.DataFrame([input_data])
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)

    # 🔹 Convert exact age to age group
    df["sender_age_group"] = df["sender_age"].apply(age_to_group)
    df["receiver_age_group"] = df["receiver_age"].apply(age_to_group)

    # Drop raw age columns (not used in training)
    df.drop(columns=["sender_age", "receiver_age"], inplace=True)

    # Amount features
    df["log_amount"] = np.log1p(df["amount"])
    df["is_high_amount"] = (df["amount"] >= 10000).astype(int)

    # Time features
    df["is_night"] = df["hour_of_day"].between(0, 5).astype(int)
    df["is_office_hours"] = df["hour_of_day"].between(9, 18).astype(int)

    # Bank relationship
    df["same_bank"] = (df["sender_bank"] == df["receiver_bank"]).astype(int)

    # Age features
    df["sender_age_ord"] = df["sender_age_group"].map(AGE_MAP)
    df["receiver_age_ord"] = df["receiver_age_group"].map(AGE_MAP)
    df["age_gap"] = abs(df["sender_age_ord"] - df["receiver_age_ord"])

    # Device & network risk
    df["device_risk"] = df["device_type"].map(DEVICE_RISK_MAP)
    df["network_risk"] = df["network_type"].map(NETWORK_RISK_MAP)
    df["device_network_risk"] = df["device_risk"] + "_" + df["network_risk"]

    # Frequency encode categorical columns (use LabelEncoder as fallback for unseen categories)
    from sklearn.preprocessing import LabelEncoder
    freq_cols = ['merchant_category', 'sender_bank', 'receiver_bank', 'sender_state']
    
    for col in freq_cols:
        if col in df.columns:
            # Convert to string and use a hash-based encoding to handle unseen values
            df[col] = hash(str(df[col].iloc[0])) % 1000 / 1000  # Normalize to [0, 1]

    return df

# ===============================
# 4️⃣ Encoding & Alignment
# ===============================

def encode_and_align(df: pd.DataFrame) -> np.ndarray:
    """
    One-hot encode categorical columns and
    align final features to training order.
    """

    ohe_cols = [
        "transaction type",
        "transaction_status",
        "device_type",
        "network_type",
        "day_of_week",
        "device_risk",
        "network_risk",
        "device_network_risk",
    ]

    # Numeric features (drop OHE cols and categorical cols that were frequency encoded)
    cols_to_drop = ohe_cols + ['sender_age_group', 'receiver_age_group']
    num_df = df.drop(columns=cols_to_drop, errors="ignore")

    # One-hot encoding
    ohe_array = ohe.transform(df[ohe_cols])
    ohe_feature_names = ohe.get_feature_names_out(ohe_cols)

    # Combine
    final_df = pd.concat(
        [
            num_df.reset_index(drop=True),
            pd.DataFrame(ohe_array, columns=ohe_feature_names),
        ],
        axis=1,
    )

    # Align with training features
    final_df = final_df.reindex(columns=feature_names, fill_value=0)

    return final_df.values

# ===============================
# 5️⃣ PUBLIC FUNCTION (FLASK USES THIS)
# ===============================

def predict_transaction(input_data: dict) -> dict:
    """
    Main prediction function.
    Flask will call ONLY this.
    """

    # Build features
    feature_df = build_features(input_data)

    # Encode & align
    X = encode_and_align(feature_df)

    # Predict probability
    fraud_proba = float(model.predict_proba(X)[0, 1])

    # Apply threshold
    fraud_flag = int(fraud_proba >= threshold)

    print("fraud_probability:",round(fraud_proba, 4),
        "fraud_flag:",fraud_flag,
        "threshold:",threshold,
        "decision:","FLAGGED" if fraud_flag else "SAFE",)

    return {
        "fraud_probability": round(fraud_proba, 4),
        "fraud_flag": fraud_flag,
        "threshold": threshold,
        "decision": "FLAGGED" if fraud_flag else "SAFE",
    }






