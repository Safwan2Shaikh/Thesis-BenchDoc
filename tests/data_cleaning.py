"""
data_cleaning.py

Purpose:
- Load raw CSV from knowledgeBase/
- Clean dataset (remove spaces, NaN, duplicates)
- Select only required columns
- Create combined search column
- Save cleaned data to processed/
- Overwrite file if it already exists

Run:
    python src/data_cleaning.py
"""

import pandas as pd
import os

# =============================
# PATH CONFIG
# =============================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INPUT_FILE = os.path.join(BASE_DIR, "knowledgeBase", "Logged_Issues.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "processed", "cleaned_issues.csv")

# =============================
# REQUIRED COLUMNS (ALREADY FIXED IN CSV)
# =============================

REQUIRED_COLUMNS = [
    "Issue",
    "Symptoms_Observed",
    "Root_Cause_Problem",
    "Solution",
    "Category",
    "Device"
]

# =============================
# LOAD DATA
# =============================

print("📂 Loading raw dataset...")
df = pd.read_csv(INPUT_FILE)  # ✅ UTF-8 works now

print(f"✅ Loaded {len(df)} raw records")

# =============================
# SELECT REQUIRED COLUMNS
# =============================

print("🔍 Selecting relevant columns...")
df = df[REQUIRED_COLUMNS]

# =============================
# CLEAN TEXT DATA
# =============================

print("🧹 Cleaning text...")

# Fill missing values
df = df.fillna("")

# Remove leading/trailing spaces from all cells
for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

# =============================
# REMOVE EMPTY ENTRIES
# =============================

print("🚫 Removing empty issues...")
df = df[df["Issue"] != ""]

# =============================
# REMOVE DUPLICATES
# =============================

print("♻️ Removing duplicates...")
df = df.drop_duplicates()

# =============================
# CREATE COMBINED SEARCH COLUMN
# =============================

print("🔗 Creating search field...")

df["combined"] = (
    df["Issue"] + " " +
    df["Symptoms_Observed"] + " " +
    df["Root_Cause_Problem"]
)

# Normalize text for matching
df["combined"] = df["combined"].str.lower()

# =============================
# SAVE CLEANED DATA
# =============================

print("💾 Saving cleaned dataset...")

# Ensure processed folder exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# ✅ Overwrites automatically
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Saved cleaned data to: {OUTPUT_FILE}")
print(f"✅ Final number of records: {len(df)}")