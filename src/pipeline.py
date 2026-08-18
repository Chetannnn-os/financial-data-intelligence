import subprocess
import sys
import time


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def run_step(description, command):

    print("\n" + "=" * 70)
    print(description)
    print("=" * 70)

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"\n❌ FAILED: {description}")
        sys.exit(result.returncode)

    print(f"\n✅ COMPLETED: {description}")


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def main():

    start_time = time.time()

    print("=" * 70)
    print("FINANCIAL DATA INTELLIGENCE PIPELINE")
    print("=" * 70)

    # --------------------------------------------------
    # STEP 1 — ETL preprocessing
    # --------------------------------------------------

    run_step(
        "STEP 1 — ETL PREPROCESSING",
        [
            sys.executable,
            "-m",
            "src.etl.transaction_etl"
        ]
    )

    # --------------------------------------------------
    # STEP 2 — Reset PostgreSQL warehouse
    # --------------------------------------------------

    run_step(
        "STEP 2 — RESET POSTGRESQL WAREHOUSE",
        [
            "sudo",
            "-u",
            "postgres",
            "psql",
            "-d",
            "financial_intelligence",
            "-c",
            """
            TRUNCATE TABLE
                warehouse.fact_transaction,
                warehouse.dim_date,
                warehouse.dim_asset,
                warehouse.dim_client
            RESTART IDENTITY CASCADE;

            TRUNCATE TABLE
                audit.data_quality_log
            RESTART IDENTITY;
            """
        ]
    )

    # --------------------------------------------------
    # STEP 3 — Load PostgreSQL warehouse
    # --------------------------------------------------

    run_step(
        "STEP 3 — LOAD POSTGRESQL DATA WAREHOUSE",
        [
            sys.executable,
            "-m",
            "src.etl.database_loader"
        ]
    )

    # --------------------------------------------------
    # STEP 4 — Portfolio analytics
    # --------------------------------------------------

    run_step(
        "STEP 4 — RUN PORTFOLIO ANALYTICS",
        [
            sys.executable,
            "-m",
            "src.analytics.portfolio_analysis"
        ]
    )

    # --------------------------------------------------
    # STEP 5 — Financial KPIs
    # --------------------------------------------------

    run_step(
        "STEP 5 — GENERATE FINANCIAL KPIs",
        [
            sys.executable,
            "-m",
            "src.analytics.financial_kpis"
        ]
    )

    # --------------------------------------------------
    # STEP 6 — Completion
    # --------------------------------------------------

    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(f"\nExecution time: {elapsed:.2f} seconds")

    print("\nData flow:")
    print("CSV → Python ETL → PostgreSQL → SQL Analytics → Metabase")

    # --------------------------------------------------
    # STEP 7 — Open Metabase dashboard
    # --------------------------------------------------

    dashboard_url = (
        "http://localhost:3000/dashboard/"
        "2-financial-intelligence-dashboard"
    )

    print("\nOpening Financial Intelligence Dashboard...")

    subprocess.Popen(
        [
            "xdg-open",
            dashboard_url
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Dashboard opened successfully.")

    print("\n" + "=" * 70)
    print("FINANCIAL INTELLIGENCE PIPELINE FINISHED")
    print("=" * 70)


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()
