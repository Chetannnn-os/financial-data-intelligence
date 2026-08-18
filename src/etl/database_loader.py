import pandas as pd

from src.database import engine


# --------------------------------------------------
# File locations
# --------------------------------------------------

CLIENTS_FILE = "data/raw/clients.csv"

ASSETS_FILE = "data/raw/assets.csv"

TRANSACTIONS_FILE = (
    "data/processed/transactions_clean.csv"
)

REJECTED_FILE = (
    "data/processed/transactions_rejected.csv"
)


# --------------------------------------------------
# Load clients
# --------------------------------------------------

def load_clients():

    print("\nLoading clients...")

    df = pd.read_csv(
        CLIENTS_FILE
    )

    df.to_sql(
        "dim_client",
        engine,
        schema="warehouse",
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Clients loaded: {len(df):,}"
    )


# --------------------------------------------------
# Load assets
# --------------------------------------------------

def load_assets():

    print("\nLoading assets...")

    df = pd.read_csv(
        ASSETS_FILE
    )

    df.to_sql(
        "dim_asset",
        engine,
        schema="warehouse",
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Assets loaded: {len(df):,}"
    )


# --------------------------------------------------
# Load date dimension
# --------------------------------------------------

def load_dates():

    print("\nGenerating date dimension...")

    transactions = pd.read_csv(
        TRANSACTIONS_FILE
    )

    # Convert transaction dates to datetime
    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"]
    )

    # Get unique transaction dates
    dates = (
        transactions["transaction_date"]
        .drop_duplicates()
        .sort_values()
    )

    date_df = pd.DataFrame({
        "full_date": dates
    })

    # Date surrogate key: YYYYMMDD
    date_df["date_key"] = (
        date_df["full_date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    date_df["year"] = (
        date_df["full_date"]
        .dt.year
    )

    date_df["quarter"] = (
        date_df["full_date"]
        .dt.quarter
    )

    date_df["month"] = (
        date_df["full_date"]
        .dt.month
    )

    date_df["month_name"] = (
        date_df["full_date"]
        .dt.month_name()
    )

    date_df["week"] = (
        date_df["full_date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    date_df["day"] = (
        date_df["full_date"]
        .dt.day
    )

    date_df["day_name"] = (
        date_df["full_date"]
        .dt.day_name()
    )

    # Reorder columns to match PostgreSQL table
    date_df = date_df[
        [
            "date_key",
            "full_date",
            "year",
            "quarter",
            "month",
            "month_name",
            "week",
            "day",
            "day_name"
        ]
    ]

    date_df.to_sql(
        "dim_date",
        engine,
        schema="warehouse",
        if_exists="append",
        index=False,
        method="multi"
    )

    print(
        f"Dates loaded: {len(date_df):,}"
    )


# --------------------------------------------------
# Load transactions
# --------------------------------------------------

def load_transactions():

    print("\nLoading transactions...")

    transactions = pd.read_csv(
        TRANSACTIONS_FILE
    )

    # --------------------------------------------------
    # Normalize transaction date
    # --------------------------------------------------

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"]
    )

    # --------------------------------------------------
    # Retrieve dimension keys
    # --------------------------------------------------

    clients = pd.read_sql(
        """
        SELECT
            client_key,
            client_id
        FROM warehouse.dim_client
        """,
        engine
    )

    assets = pd.read_sql(
        """
        SELECT
            asset_key,
            asset_id
        FROM warehouse.dim_asset
        """,
        engine
    )

    dates = pd.read_sql(
        """
        SELECT
            date_key,
            full_date
        FROM warehouse.dim_date
        """,
        engine
    )

    # --------------------------------------------------
    # Normalize PostgreSQL date column
    #
    # PostgreSQL returns DATE as object/string in pandas.
    # Convert it to datetime so both merge columns
    # have the same datatype.
    # --------------------------------------------------

    dates["full_date"] = pd.to_datetime(
        dates["full_date"]
    )

    # --------------------------------------------------
    # Join client surrogate key
    # --------------------------------------------------

    transactions = transactions.merge(
        clients,
        on="client_id",
        how="left"
    )

    # --------------------------------------------------
    # Join asset surrogate key
    # --------------------------------------------------

    transactions = transactions.merge(
        assets,
        on="asset_id",
        how="left"
    )

    # --------------------------------------------------
    # Join date surrogate key
    # --------------------------------------------------

    transactions = transactions.merge(
        dates,
        left_on="transaction_date",
        right_on="full_date",
        how="left"
    )

    # --------------------------------------------------
    # Verify all dimension keys were resolved
    # --------------------------------------------------

    missing_client_keys = (
        transactions["client_key"]
        .isna()
        .sum()
    )

    missing_asset_keys = (
        transactions["asset_key"]
        .isna()
        .sum()
    )

    missing_date_keys = (
        transactions["date_key"]
        .isna()
        .sum()
    )

    if (
        missing_client_keys > 0
        or missing_asset_keys > 0
        or missing_date_keys > 0
    ):

        raise ValueError(
            "Dimension lookup failed:\n"
            f"Missing client keys: {missing_client_keys}\n"
            f"Missing asset keys: {missing_asset_keys}\n"
            f"Missing date keys: {missing_date_keys}"
        )

    # --------------------------------------------------
    # Calculate transaction value
    # --------------------------------------------------

    transactions["transaction_value"] = (
        transactions["quantity"]
        * transactions["price"]
    )

    # --------------------------------------------------
    # Select warehouse columns
    # --------------------------------------------------

    fact = transactions[
        [
            "transaction_id",
            "client_key",
            "asset_key",
            "date_key",
            "transaction_type",
            "quantity",
            "price",
            "currency",
            "transaction_value"
        ]
    ].copy()

    # --------------------------------------------------
    # Load fact table
    # --------------------------------------------------

    fact.to_sql(
        "fact_transaction",
        engine,
        schema="warehouse",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(
        f"Transactions loaded: {len(fact):,}"
    )


# --------------------------------------------------
# Load rejected records
# --------------------------------------------------

def load_rejections():

    print(
        "\nLoading data-quality audit records..."
    )

    df = pd.read_csv(
        REJECTED_FILE
    )

    audit = df[
        [
            "transaction_id",
            "validation_status",
            "rejection_reason"
        ]
    ].copy()

    audit.to_sql(
        "data_quality_log",
        engine,
        schema="audit",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(
        f"Rejected records logged: {len(audit):,}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 60)
    print("FINANCIAL DATA WAREHOUSE LOAD")
    print("=" * 60)

    load_clients()

    load_assets()

    load_dates()

    load_transactions()

    load_rejections()

    print("\n")
    print("=" * 60)
    print("DATABASE LOAD COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":

    main()