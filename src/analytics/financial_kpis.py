import pandas as pd

from src.database import engine


# --------------------------------------------------
# Overall portfolio KPIs
# --------------------------------------------------

def overall_kpis():

    query = """
        SELECT
            COUNT(*) AS total_transactions,

            SUM(transaction_value)
                AS total_transaction_value,

            AVG(transaction_value)
                AS average_transaction_value,

            COUNT(DISTINCT client_key)
                AS active_clients,

            COUNT(DISTINCT asset_key)
                AS active_assets

        FROM warehouse.fact_transaction;
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Buy vs Sell KPIs
# --------------------------------------------------

def buy_sell_kpis():

    query = """
        SELECT

            SUM(
                CASE
                    WHEN transaction_type = 'BUY'
                    THEN transaction_value
                    ELSE 0
                END
            ) AS buy_value,

            SUM(
                CASE
                    WHEN transaction_type = 'SELL'
                    THEN transaction_value
                    ELSE 0
                END
            ) AS sell_value,

            COUNT(
                CASE
                    WHEN transaction_type = 'BUY'
                    THEN 1
                END
            ) AS buy_transactions,

            COUNT(
                CASE
                    WHEN transaction_type = 'SELL'
                    THEN 1
                END
            ) AS sell_transactions

        FROM warehouse.fact_transaction;
    """

    df = pd.read_sql(
        query,
        engine
    )

    # Calculate buy/sell ratio
    df["buy_sell_value_ratio"] = (
        df["buy_value"]
        / df["sell_value"]
    )

    return df


# --------------------------------------------------
# Data quality KPIs
# --------------------------------------------------

def data_quality_kpis():

    query = """
        SELECT

            (
                SELECT COUNT(*)
                FROM warehouse.fact_transaction
            ) AS valid_transactions,

            (
                SELECT COUNT(*)
                FROM audit.data_quality_log
            ) AS rejected_transactions,

            (
                SELECT COUNT(*)
                FROM warehouse.fact_transaction
            )
            +
            (
                SELECT COUNT(*)
                FROM audit.data_quality_log
            )
            AS total_processed_records;
    """

    df = pd.read_sql(
        query,
        engine
    )

    # Calculate rejection rate
    df["rejection_rate_percent"] = (
        df["rejected_transactions"]
        / df["total_processed_records"]
        * 100
    )

    return df


# --------------------------------------------------
# Asset class KPIs
# --------------------------------------------------

def asset_class_kpis():

    query = """
        SELECT

            a.asset_class,

            COUNT(*) AS transaction_count,

            SUM(f.transaction_value)
                AS transaction_value,

            AVG(f.transaction_value)
                AS average_transaction_value

        FROM warehouse.fact_transaction f

        JOIN warehouse.dim_asset a
            ON f.asset_key = a.asset_key

        GROUP BY
            a.asset_class

        ORDER BY
            transaction_value DESC;
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Top clients
# --------------------------------------------------

def top_clients(limit=10):

    query = f"""
        SELECT

            c.client_id,

            c.client_name,

            c.segment,

            COUNT(*) AS transaction_count,

            SUM(f.transaction_value)
                AS transaction_value

        FROM warehouse.fact_transaction f

        JOIN warehouse.dim_client c
            ON f.client_key = c.client_key

        GROUP BY

            c.client_id,
            c.client_name,
            c.segment

        ORDER BY
            transaction_value DESC

        LIMIT {limit};
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# Monthly performance
# --------------------------------------------------

def monthly_performance():

    query = """
        WITH monthly_data AS (

            SELECT

                d.year,

                d.month,

                d.month_name,

                COUNT(*) AS transaction_count,

                SUM(f.transaction_value)
                    AS transaction_value

            FROM warehouse.fact_transaction f

            JOIN warehouse.dim_date d
                ON f.date_key = d.date_key

            GROUP BY

                d.year,
                d.month,
                d.month_name
        )

        SELECT

            year,

            month,

            month_name,

            transaction_count,

            transaction_value,

            LAG(transaction_value)
                OVER (
                    ORDER BY year, month
                ) AS previous_month_value

        FROM monthly_data

        ORDER BY
            year,
            month;
    """

    df = pd.read_sql(
        query,
        engine
    )

    # Month-over-month growth
    df["mom_growth_percent"] = (
        (
            df["transaction_value"]
            - df["previous_month_value"]
        )
        /
        df["previous_month_value"]
        * 100
    )

    return df


# --------------------------------------------------
# Executive KPI report
# --------------------------------------------------

def main():

    print("=" * 70)
    print("FINANCIAL INTELLIGENCE — KPI REPORT")
    print("=" * 70)

    # --------------------------------------------------
    # Overall KPIs
    # --------------------------------------------------

    print("\nOVERALL KPIs")
    print("-" * 70)

    print(
        overall_kpis()
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Buy vs Sell
    # --------------------------------------------------

    print("\nBUY vs SELL")
    print("-" * 70)

    print(
        buy_sell_kpis()
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Data Quality
    # --------------------------------------------------

    print("\nDATA QUALITY")
    print("-" * 70)

    print(
        data_quality_kpis()
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Asset Classes
    # --------------------------------------------------

    print("\nASSET CLASS PERFORMANCE")
    print("-" * 70)

    print(
        asset_class_kpis()
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Top Clients
    # --------------------------------------------------

    print("\nTOP 10 CLIENTS")
    print("-" * 70)

    print(
        top_clients()
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Monthly Performance
    # --------------------------------------------------

    print("\nMONTHLY PERFORMANCE")
    print("-" * 70)

    print(
        monthly_performance()
        .to_string(index=False)
    )

    print("\n")
    print("=" * 70)
    print("KPI REPORT COMPLETED")
    print("=" * 70)


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":

    main()