from pathlib import Path
import duckdb

PROCESSED_PATH = Path("data/lake/processed")
WAREHOUSE_PATH = Path("data/warehouse")

WAREHOUSE_PATH.mkdir(parents=True, exist_ok=True)

DATABASE_FILE = WAREHOUSE_PATH / "ecommerce.duckdb"
SALES_FILE = PROCESSED_PATH / "fact_sales.parquet"


def load_sales_data():
    print("Connecting to DuckDB warehouse...")

    connection = duckdb.connect(str(DATABASE_FILE))

    print("Creating fact_sales table...")

    connection.execute("""
        CREATE OR REPLACE TABLE fact_sales AS
        SELECT *
        FROM read_parquet(?)
    """, [str(SALES_FILE)])

    row_count = connection.execute(
        "SELECT COUNT(*) FROM fact_sales"
    ).fetchone()[0]

    print("\nData warehouse load completed successfully!")
    print(f"Rows loaded into fact_sales: {row_count:,}")

    print("\nWarehouse table preview:")

    preview = connection.execute("""
        SELECT
            order_id,
            product_category_name_english,
            price,
            freight_value,
            total_item_value,
            order_year_month
        FROM fact_sales
        LIMIT 5
    """).fetchdf()

    print(preview.to_string(index=False, col_space=15))

    connection.close()

    print(f"\nWarehouse created at: {DATABASE_FILE}")


if __name__ == "__main__":
    load_sales_data()