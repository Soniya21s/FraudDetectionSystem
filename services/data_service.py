import pandas as pd
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "transactions.csv"


def save_transaction(input_data: dict, prediction: dict):
    """
    Save user input + prediction result to CSV.
    """

    # Combine input + prediction
    row = input_data.copy()

    row["fraud_probability"] = prediction["fraud_probability"]
    row["fraud_flag"] = prediction["fraud_flag"]
    row["decision"] = prediction["decision"]
    row["timestamp"] = datetime.now().isoformat()

    df_row = pd.DataFrame([row])

    # If CSV exists, append; else create
    if DATA_PATH.exists():
        df_row.to_csv(DATA_PATH, mode="a", header=False, index=False)
    else:
        df_row.to_csv(DATA_PATH, index=False)