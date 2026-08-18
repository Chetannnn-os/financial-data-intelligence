import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRANSACTIONS_FILE = "data/raw/transactions_messy.csv"
CLIENTS_FILE = "data/raw/clients.csv"
ASSETS_FILE = "data/raw/assets.csv"


# --------------------------------------------------
# Load reference data
# --------------------------------------------------

transactions = pd.read_csv(TRANSACTIONS_FILE)
clients = pd.read_csv(CLIENTS_FILE)
assets = pd.read_csv(ASSETS_FILE)


# --------------------------------------------------
# Validation functions
# --------------------------------------------------

def check_missing_values(df):

    return {
        "missing_client_id": df["client_id"].isna().sum(),
        "missing_price": df["price"].isna().sum(),
        "missing_quantity": df["quantity"].isna().sum(),
        "missing_asset_id": df["asset_id"].isna().sum()
    }


def check_negative_quantity(df):

    return (
        df["quantity"].fillna(0) < 0
    ).sum()


def check_zero_price(df):

    return (
        (df["price"] == 0)
        & df["price"].notna()
    ).sum()


def check_invalid_clients(df, clients):

    valid_clients = set(
        clients["client_id"]
    )

    return (
        ~df["client_id"].isin(valid_clients)
        & df["client_id"].notna()
    ).sum()


def check_invalid_assets(df, assets):

    valid_assets = set(
        assets["asset_id"]
    )

    return (
        ~df["asset_id"].isin(valid_assets)
        & df["asset_id"].notna()
    ).sum()


def check_duplicates(df):

    return df["transaction_id"].duplicated().sum()


def check_currency(df):

    valid_currencies = {
        "USD",
        "EUR",
        "GBP",
        "INR",
        "SGD"
    }

    return (
        ~df["currency"].isin(valid_currencies)
    ).sum()


# --------------------------------------------------
# Generate report
# --------------------------------------------------

def generate_report():

    missing = check_missing_values(transactions)

    negative_quantity = check_negative_quantity(
        transactions
    )

    zero_price = check_zero_price(
        transactions
    )

    invalid_clients = check_invalid_clients(
        transactions,
        clients
    )

    invalid_assets = check_invalid_assets(
        transactions,
        assets
    )

    duplicates = check_duplicates(
        transactions
    )

    invalid_currency = check_currency(
        transactions
    )

    print("\n")
    print("=" * 55)
    print("           FINANCIAL DATA QUALITY REPORT")
    print("=" * 55)

    print(f"\nTotal records: {len(transactions):,}")

    print("\nCompleteness")
    print("-" * 30)

    for key, value in missing.items():
        print(f"{key:<25} {value:>8,}")

    print("\nValidity")
    print("-" * 30)

    print(
        f"{'Negative quantities':<25}"
        f"{negative_quantity:>8,}"
    )

    print(
        f"{'Zero prices':<25}"
        f"{zero_price:>8,}"
    )

    print(
        f"{'Invalid client IDs':<25}"
        f"{invalid_clients:>8,}"
    )

    print(
        f"{'Invalid asset IDs':<25}"
        f"{invalid_assets:>8,}"
    )

    print(
        f"{'Invalid currencies':<25}"
        f"{invalid_currency:>8,}"
    )

    print("\nUniqueness")
    print("-" * 30)

    print(
        f"{'Duplicate transactions':<25}"
        f"{duplicates:>8,}"
    )

    print("\nOverall Status")
    print("-" * 30)

    total_issues = (
        sum(missing.values())
        + negative_quantity
        + zero_price
        + invalid_clients
        + invalid_assets
        + invalid_currency
        + duplicates
    )

    if total_issues == 0:
        print("PASSED")
    else:
        print("FAILED")

    print("=" * 55)


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    generate_report()