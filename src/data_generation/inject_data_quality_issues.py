import random
import pandas as pd
import numpy as np


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = "data/raw/transactions.csv"
OUTPUT_FILE = "data/raw/transactions_messy.csv"

random.seed(42)
np.random.seed(42)


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"Original records: {len(df):,}")


# --------------------------------------------------
# 1. Missing client IDs
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    300
)

df.loc[indices, "client_id"] = np.nan


# --------------------------------------------------
# 2. Missing prices
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    250
)

df.loc[indices, "price"] = np.nan


# --------------------------------------------------
# 3. Negative quantities
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    100
)

df.loc[indices, "quantity"] *= -1


# --------------------------------------------------
# 4. Zero prices
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    50
)

df.loc[indices, "price"] = 0


# --------------------------------------------------
# 5. Invalid client IDs
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    100
)

df.loc[indices, "client_id"] = "C9999"


# --------------------------------------------------
# 6. Invalid asset IDs
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    100
)

df.loc[indices, "asset_id"] = "A9999"


# --------------------------------------------------
# 7. Currency inconsistencies
# --------------------------------------------------

indices = random.sample(
    list(df.index),
    300
)

for index in indices:

    currency = df.loc[index, "currency"]

    if currency == "USD":
        df.loc[index, "currency"] = "usd"

    elif currency == "EUR":
        df.loc[index, "currency"] = "eur"

    elif currency == "GBP":
        df.loc[index, "currency"] = "gbp"


# --------------------------------------------------
# 8. Duplicate transactions
# --------------------------------------------------

duplicates = df.sample(
    n=200,
    random_state=42
)

df = pd.concat(
    [df, duplicates],
    ignore_index=True
)


# --------------------------------------------------
# Shuffle data
# --------------------------------------------------

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# --------------------------------------------------
# Save
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\nData quality issues injected:")
print("Missing client IDs : 300")
print("Missing prices     : 250")
print("Negative quantities: 100")
print("Zero prices        : 50")
print("Invalid clients    : 100")
print("Invalid assets     : 100")
print("Currency issues    : 300")
print("Duplicate records  : 200")

print(f"\nFinal records: {len(df):,}")
print(f"Saved to: {OUTPUT_FILE}")