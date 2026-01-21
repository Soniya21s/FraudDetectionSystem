import pandas as pd
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "transactions.csv"
PRED_DATA_PATH = BASE_DIR / "data" / "transactions.csv"



def load_and_combine_data() -> pd.DataFrame:
    """
    Load historical + prediction data and combine into a unified dataframe.
    """

    dfs = []

    # 1️⃣ Load historical data
    if RAW_DATA_PATH.exists():
        df_raw = pd.read_csv(RAW_DATA_PATH)

        # Normalize column names: strip, replace spaces with underscores, remove parentheses, lowercase
        df_raw.columns = (
            df_raw.columns
            .str.strip()
            .str.replace(" ", "_", regex=False)
            .str.replace(r"[()]", "", regex=True)
            .str.lower()
        )

        # Normalize schema for dashboard
        df_raw["fraud_probability"] = None
        df_raw["decision"] = df_raw["fraud_flag"].map(
            lambda x: "FLAGGED" if x == 1 else "SAFE"
        )
        df_raw["source"] = "historical"

        dfs.append(df_raw)

    # 2️⃣ Load prediction data
    if PRED_DATA_PATH.exists():
        df_pred = pd.read_csv(PRED_DATA_PATH)

        df_pred.columns = (
            df_pred.columns
            .str.strip()
            .str.replace(" ", "_", regex=False)
            .str.replace(r"[()]", "", regex=True)
            .str.lower()
        )

        df_pred["source"] = "predicted"
        dfs.append(df_pred)

    # 3️⃣ Combine
    if not dfs:
        return pd.DataFrame()

    combined_df = pd.concat(dfs, ignore_index=True)

    return combined_df



def get_kpis():
    """
    High-level KPI metrics.
    """
    df = load_and_combine_data()
    if df.empty:
        return {
            "total_transactions": 0,
            "fraud_transactions": 0,
            "fraud_rate": 0.0,
        }

    total = len(df)
    fraud = int(df["fraud_flag"].sum())
    fraud_rate = round((fraud / total) * 100, 2)

    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": fraud_rate,
    }


def fraud_vs_non_fraud():
    """
    Counts for pie/donut chart.
    """
    df = load_and_combine_data()
    if df.empty:
        return {"fraud": 0, "non_fraud": 0}

    fraud = int(df["fraud_flag"].sum())
    non_fraud = len(df) - fraud

    return {
        "fraud": fraud,
        "non_fraud": non_fraud,
    }


def fraud_by_network():
    """
    Fraud count by network type.
    """
    df = load_and_combine_data()
    if df.empty:
        return {}

    result = (
        df[df["fraud_flag"] == 1]
        .groupby("network_type")
        .size()
        .sort_values(ascending=False)
    )

    return result.to_dict()


def fraud_by_transaction_type():
    """
    Fraud count by transaction type.
    """
    df = load_and_combine_data()
    if df.empty:
        return {}

    result = (
        df[df["fraud_flag"] == 1]
        .groupby("transaction_type")
        .size()
        .sort_values(ascending=False)
    )

    return result.to_dict()


def transactions_over_time(freq="D"):
    """
    Transactions count over time.
    freq: 'D' (daily), 'H' (hourly)
    """
    df = load_and_combine_data()
    if df.empty:
        return {}

    # Parse timestamps (source CSV uses day-month-year format)
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    result = (
        df.set_index("timestamp")
        .resample(freq)
        .size()
    )

    # Convert index to string for JSON
    return {
        str(k): int(v)
        for k, v in result.items()
    }