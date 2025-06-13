import pandas as pd
import re
from typing import Optional, Dict, Any

DATA_PATH = "/workspaces/agent-development-kit-crash-course/beebi/data/growthdata.csv"

def extract_number(value: str) -> Optional[float]:
    if pd.isna(value) or value == 0.0:
        return None
    try:
        return float(re.sub(r"[^\d.]+", "", str(value)))
    except:
        return None

def preprocess_growth_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["RecordDate"] = pd.to_datetime(df["RecordDate"])
    df["Weight"] = df["Weight"].apply(extract_number)
    df["Height"] = df["Height"].apply(extract_number)
    df["Head"] = df["Head"].apply(extract_number)
    df = df.sort_values("RecordDate")
    return df


