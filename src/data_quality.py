from pathlib import Path
import duckdb

DATABASE_FILE = Path("data/warehouse/ecommerce.duckdb")


def run_data_quality_checks():
    print("\n" + "=" * 60)
    print("STARTING DATA QUALITY CHECKS")
    print("=" * 60)

    connection = duckdb.connect(str(DATABASE_FILE), read_only=True)

    # 1. Check whether the table exists and contains data
    total_rows = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
    """).fetchone()[0]

    print(f"\nTotal records: {total_rows:,}")

    if total_rows > 0:
        print("✅ Record count check passed")
    else:
        print("❌ Record count check failed")

    # 2. Check for missing order IDs
    missing_order_ids = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE order_id IS NULL
    """).fetchone()[0]

    print(f"\nMissing order IDs: {missing_order_ids}")

    if missing_order_ids == 0:
        print("✅ Order ID check passed")
    else:
        print("❌ Order ID check failed")

    # 3. Check for invalid prices
    invalid_prices = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE price < 0
    """).fetchone()[0]

    print(f"\nInvalid price records: {invalid_prices}")

    if invalid_prices == 0:
        print("✅ Price validation passed")
    else:
        print("❌ Price validation failed")

    # 4. Check for invalid total values
    invalid_totals = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE total_item_value < 0
    """).fetchone()[0]

    print(f"\nInvalid total values: {invalid_totals}")

    if invalid_totals == 0:
        print("✅ Total value validation passed")
    else:
        print("❌ Total value validation failed")

    # 5. Check for duplicate item records
    duplicate_records = connection.execute("""
        SELECT
            order_id,
            product_id,
            seller_id,
            COUNT(*) AS record_count
        FROM fact_sales
        GROUP BY order_id, product_id, seller_id
        HAVING COUNT(*) > 1
    """).fetchall()

    print(f"\nDuplicate record groups: {len(duplicate_records)}")

    if len(duplicate_records) == 0:
        print("✅ Duplicate check passed")
    else:
        print("⚠️ Duplicate groups detected")

    connection.close()

    print("\n" + "=" * 60)
    print("DATA QUALITY CHECKS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_data_quality_checks()