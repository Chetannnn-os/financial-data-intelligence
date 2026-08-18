import os
import random
import numpy as np
import pandas as pd
from faker import Faker


# --------------------------------------------------
# Configuration
# --------------------------------------------------

fake = Faker()
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "data/raw"

NUM_CLIENTS = 500
NUM_ASSETS = 200
NUM_TRANSACTIONS = 100_000


# --------------------------------------------------
# Setup
# --------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------
# 1. Generate Clients
# --------------------------------------------------

def generate_clients():

    clients = []

    segments = [
        "Retail",
        "High Net Worth",
        "Institutional",
        "Corporate"
    ]

    countries = [
        "USA",
        "UK",
        "India",
        "Singapore",
        "Germany",
        "Canada",
        "Australia"
    ]

    for i in range(1, NUM_CLIENTS + 1):

        clients.append({
            "client_id": f"C{i:04d}",
            "client_name": fake.name(),
            "country": random.choice(countries),
            "segment": random.choice(segments),
            "onboarding_date": fake.date_between(
                start_date="-8y",
                end_date="today"
            )
        })

    df = pd.DataFrame(clients)

    df.to_csv(
        f"{OUTPUT_DIR}/clients.csv",
        index=False
    )

    return df


# --------------------------------------------------
# 2. Generate Assets
# --------------------------------------------------

def generate_assets():

    asset_classes = [
        "Equity",
        "ETF",
        "Bond",
        "Commodity",
        "REIT"
    ]

    sectors = [
        "Technology",
        "Healthcare",
        "Financials",
        "Energy",
        "Consumer",
        "Industrials",
        "Telecommunications"
    ]

    countries = [
        "USA",
        "UK",
        "India",
        "Germany",
        "Japan",
        "Canada"
    ]

    assets = []

    for i in range(1, NUM_ASSETS + 1):

        assets.append({
            "asset_id": f"A{i:04d}",
            "ticker": f"AST{i:03d}",
            "asset_name": fake.company(),
            "asset_class": random.choice(asset_classes),
            "sector": random.choice(sectors),
            "country": random.choice(countries)
        })

    df = pd.DataFrame(assets)

    df.to_csv(
        f"{OUTPUT_DIR}/assets.csv",
        index=False
    )

    return df


# --------------------------------------------------
# 3. Generate Transactions
# --------------------------------------------------

def generate_transactions(clients, assets):

    transactions = []

    client_ids = clients["client_id"].tolist()
    asset_ids = assets["asset_id"].tolist()

    transaction_types = [
        "BUY",
        "SELL"
    ]

    currencies = [
        "USD",
        "EUR",
        "GBP",
        "INR",
        "SGD"
    ]

    for i in range(1, NUM_TRANSACTIONS + 1):

        quantity = round(
            np.random.lognormal(
                mean=3,
                sigma=1
            ),
            2
        )

        price = round(
            np.random.lognormal(
                mean=4,
                sigma=0.8
            ),
            2
        )

        transactions.append({
            "transaction_id": f"TX{i:07d}",
            "client_id": random.choice(client_ids),
            "asset_id": random.choice(asset_ids),
            "transaction_date": fake.date_between(
                start_date="-3y",
                end_date="today"
            ),
            "transaction_type": random.choice(transaction_types),
            "quantity": quantity,
            "price": price,
            "currency": random.choice(currencies)
        })

    df = pd.DataFrame(transactions)

    df.to_csv(
        f"{OUTPUT_DIR}/transactions.csv",
        index=False
    )

    return df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Generating clients...")
    clients = generate_clients()

    print("Generating assets...")
    assets = generate_assets()

    print("Generating transactions...")
    transactions = generate_transactions(
        clients,
        assets
    )

    print("\nData generation completed!")
    print(f"Clients:      {len(clients):,}")
    print(f"Assets:       {len(assets):,}")
    print(f"Transactions: {len(transactions):,}")


if __name__ == "__main__":
    main()