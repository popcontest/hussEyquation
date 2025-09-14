#!/usr/bin/env python3
import pandas as pd

csv_path = "Z:/Downloads/NBA hussEyquation - 2024-2025 - 2022 FINAL.csv"
df = pd.read_csv(csv_path)

print("Columns:")
for i, col in enumerate(df.columns):
    print(f"  {i}: '{col}'")

print(f"\nTotal rows: {len(df)}")
print(f"\nFirst 3 rows:")
print(df.head(3).to_string())