from pathlib import Path
import duckdb

DATABASE_FILE = Path("data/warehouse/ecommerce.duckdb")

connection = duckdb.connect(str(DATABASE_FILE))

print("\n1. Total sales records:")
print(
    connection.execute(
        "SELECT COUNT(*) FROM fact_sales"
    ).fetchone()[0]
)

print("\n2. Total revenue:")
print(
    connection.execute(
        "SELECT ROUND(SUM(total_item_value), 2) FROM fact_sales"
    ).fetchone()[0]
)

print("\n3. Top 10 product categories:")
result = connection.execute("""
    SELECT
        product_category_name_english AS category,
        ROUND(SUM(total_item_value), 2) AS revenue
    FROM fact_sales
    GROUP BY product_category_name_english
    ORDER BY revenue DESC
    LIMIT 10
""").fetchdf()

print(result.to_string(index=False))

print("\n4. Monthly revenue:")
monthly_revenue = connection.execute("""
    SELECT
        order_year_month,
        ROUND(SUM(total_item_value), 2) AS revenue
    FROM fact_sales
    GROUP BY order_year_month
    ORDER BY order_year_month
""").fetchdf()

print(monthly_revenue.to_string(index=False))

connection.close()

print("\nWarehouse validation completed successfully!")