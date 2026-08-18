import pandas as pd

from src.database import engine


# --------------------------------------------------
# Asset class analysis
# --------------------------------------------------

def asset_class_analysis():

    query = """
        SELECT
            a.asset_class,
            COUNT(*) AS transaction_count,
            SUM(f.transaction_value)
                AS total_transaction_value,
            AVG(f.transaction_value)
                AS average_transaction_value
        FROM warehouse.fact_transaction f

        JOIN warehouse.dim_asset a
            ON f.asset_key = a.asset_key

        GROUP BY
            a.asset_class

        ORDER BY
            total_transaction_value DESC;
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Buy vs Sell analysis
# --------------------------------------------------

def transaction_type_analysis():

    query = """
        SELECT
            transaction_type,
            COUNT(*) AS transaction_count,
            SUM(transaction_value)
                AS total_transaction_value,
            AVG(transaction_value)
                AS average_transaction_value
        FROM warehouse.fact_transaction

        GROUP BY
            transaction_type

        ORDER BY
            total_transaction_value DESC;
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Client transaction analysis
# --------------------------------------------------

def top_clients(limit=10):

    query = f"""
        SELECT
            c.client_id,
            c.client_name,
            c.segment,

            COUNT(*) AS transaction_count,

            SUM(f.transaction_value)
                AS total_transaction_value

        FROM warehouse.fact_transaction f

        JOIN warehouse.dim_client c
            ON f.client_key = c.client_key

        GROUP BY
            c.client_id,
            c.client_name,
            c.segment

        ORDER BY
            total_transaction_value DESC

        LIMIT {limit};
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Monthly transaction analysis
# --------------------------------------------------

def monthly_analysis():

    query = """
        SELECT
            d.year,
            d.month,
            d.month_name,

            COUNT(*) AS transaction_count,

            SUM(f.transaction_value)
                AS total_transaction_value

        FROM warehouse.fact_transaction f

        JOIN warehouse.dim_date d
            ON f.date_key = d.date_key

        GROUP BY
            d.year,
            d.month,
            d.month_name

        ORDER BY
            d.year,
            d.month;
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 60)
    print("FINANCIAL ANALYTICS")
    print("=" * 60)

    print("\nAsset Class Analysis")
    print("-" * 60)

    print(
        asset_class_analysis()
        .to_string(index=False)
    )

    print("\nBuy vs Sell Analysis")
    print("-" * 60)

    print(
        transaction_type_analysis()
        .to_string(index=False)
    )

    print("\nTop Clients")
    print("-" * 60)

    print(
        top_clients()
        .to_string(index=False)
    )

    print("\nMonthly Analysis")
    print("-" * 60)

    print(
        monthly_analysis()
        .to_string(index=False)
    )


if __name__ == "__main__":

    main()