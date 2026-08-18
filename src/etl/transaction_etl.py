import os
import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = "data/raw/transactions_messy.csv"

PROCESSED_DIR = "data/processed"

CLEAN_FILE = (
    f"{PROCESSED_DIR}/transactions_clean.csv"
)

REJECTED_FILE = (
    f"{PROCESSED_DIR}/transactions_rejected.csv"
)


# --------------------------------------------------
# Setup
# --------------------------------------------------

os.makedirs(PROCESSED_DIR, exist_ok=True)


# --------------------------------------------------
# Extract
# --------------------------------------------------

def extract_data():

    print("Extracting transaction data...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Records extracted: {len(df):,}"
    )

    return df


# --------------------------------------------------
# Transform / Clean
# --------------------------------------------------

def clean_data(df):

    print("\nCleaning data...")

    df = df.copy()

    # Normalize currency
    df["currency"] = (
        df["currency"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # Convert numeric fields
    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    # Standardize dates
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    return df


# --------------------------------------------------
# Validation + Rejection
# --------------------------------------------------

def validate_data(df):

    print("\nValidating records...")

    valid_currencies = {
        "USD",
        "EUR",
        "GBP",
        "INR",
        "SGD"
    }

    clients = pd.read_csv(
        "data/raw/clients.csv"
    )

    assets = pd.read_csv(
        "data/raw/assets.csv"
    )

    valid_clients = set(
        clients["client_id"]
    )

    valid_assets = set(
        assets["asset_id"]
    )

    # --------------------------------------------------
    # Create a list of validation failures for each row
    # --------------------------------------------------

    df["validation_errors"] = [[] for _ in range(len(df))]

    def add_error(mask, message):

        for index in df.index[mask]:
            df.at[index, "validation_errors"].append(
                message
            )

    # --------------------------------------------------
    # Completeness checks
    # --------------------------------------------------

    add_error(
        df["client_id"].isna(),
        "Missing client ID"
    )

    add_error(
        df["asset_id"].isna(),
        "Missing asset ID"
    )

    add_error(
        df["price"].isna(),
        "Missing price"
    )

    add_error(
        df["quantity"].isna(),
        "Missing quantity"
    )

    # --------------------------------------------------
    # Referential integrity
    # --------------------------------------------------

    add_error(
        (
            ~df["client_id"].isin(valid_clients)
            & df["client_id"].notna()
        ),
        "Invalid client ID"
    )

    add_error(
        (
            ~df["asset_id"].isin(valid_assets)
            & df["asset_id"].notna()
        ),
        "Invalid asset ID"
    )

    # --------------------------------------------------
    # Business rules
    # --------------------------------------------------

    add_error(
        df["quantity"] <= 0,
        "Non-positive quantity"
    )

    add_error(
        df["price"] <= 0,
        "Non-positive price"
    )

    # --------------------------------------------------
    # Currency validation
    # --------------------------------------------------

    add_error(
        ~df["currency"].isin(valid_currencies),
        "Invalid currency"
    )

    # --------------------------------------------------
    # Date validation
    # --------------------------------------------------

    add_error(
        df["transaction_date"].isna(),
        "Invalid transaction date"
    )

    # --------------------------------------------------
    # Convert errors to readable text
    # --------------------------------------------------

    df["rejection_reason"] = df[
        "validation_errors"
    ].apply(
        lambda errors: "; ".join(errors)
    )

    # --------------------------------------------------
    # Separate initially valid/rejected records
    # --------------------------------------------------

    rejected = df[
        df["rejection_reason"] != ""
    ].copy()

    valid = df[
        df["rejection_reason"] == ""
    ].copy()

    # --------------------------------------------------
    # Duplicate detection
    # --------------------------------------------------

    duplicate_mask = valid.duplicated(
        subset=["transaction_id"],
        keep="first"
    )

    duplicate_records = valid[
        duplicate_mask
    ].copy()

    duplicate_records[
        "rejection_reason"
    ] = "Duplicate transaction ID"

    rejected = pd.concat(
        [
            rejected,
            duplicate_records
        ],
        ignore_index=True
    )

    valid = valid[
        ~duplicate_mask
    ].copy()

    # --------------------------------------------------
    # Validation status
    # --------------------------------------------------

    valid["validation_status"] = "VALID"

    rejected["validation_status"] = "REJECTED"

    # Remove internal validation column

    valid = valid.drop(
        columns=["validation_errors"]
    )

    rejected = rejected.drop(
        columns=["validation_errors"]
    )

    return valid, rejected


# --------------------------------------------------
# Load processed files
# --------------------------------------------------

def load_processed_data(valid, rejected):

    print("\nSaving processed data...")

    valid.to_csv(
        CLEAN_FILE,
        index=False
    )

    rejected.to_csv(
        REJECTED_FILE,
        index=False
    )

    print(
        f"Valid records:    {len(valid):,}"
    )

    print(
        f"Rejected records: {len(rejected):,}"
    )


# --------------------------------------------------
# Main ETL Pipeline
# --------------------------------------------------

def main():

    df = extract_data()

    df = clean_data(df)

    valid, rejected = validate_data(df)

    load_processed_data(
        valid,
        rejected
    )

    print("\nETL preprocessing completed!")


if __name__ == "__main__":
    main()