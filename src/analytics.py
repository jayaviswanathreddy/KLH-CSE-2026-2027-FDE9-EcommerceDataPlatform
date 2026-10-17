from pathlib import Path
import duckdb

# Path to the DuckDB warehouse
DATABASE_FILE = Path("data/warehouse/ecommerce.duckdb")


def get_connection():
    """Create a connection to the DuckDB warehouse."""
    return duckdb.connect(str(DATABASE_FILE), read_only=True)


def get_total_metrics():
    """Return total revenue, sales records, and average item value."""
    connection = get_connection()

    result = connection.execute("""
        SELECT
            COUNT(*) AS total_sales_records,
            ROUND(SUM(total_item_value), 2) AS total_revenue,
            ROUND(AVG(total_item_value), 2) AS average_item_value
        FROM fact_sales
    """).fetchone()

    connection.close()

    return {
        "total_sales_records": result[0],
        "total_revenue": result[1],
        "average_item_value": result[2]
    }


def get_monthly_revenue():
    """Return revenue grouped by month."""
    connection = get_connection()

    result = connection.execute("""
        SELECT
            order_year_month,
            ROUND(SUM(total_item_value), 2) AS revenue
        FROM fact_sales
        GROUP BY order_year_month
        ORDER BY order_year_month
    """).fetchdf()

    connection.close()

    return result


def get_top_categories(limit=10):
    """Return the highest-revenue product categories."""
    connection = get_connection()

    result = connection.execute("""
        SELECT
            COALESCE(
                product_category_name_english,
                'Unknown'
            ) AS category,
            ROUND(SUM(total_item_value), 2) AS revenue
        FROM fact_sales
        GROUP BY product_category_name_english
        ORDER BY revenue DESC
        LIMIT ?
    """, [limit]).fetchdf()

    connection.close()

    return result


def get_yearly_revenue():
    """Return revenue grouped by year."""
    connection = get_connection()

    result = connection.execute("""
        SELECT
            order_year,
            ROUND(SUM(total_item_value), 2) AS revenue
        FROM fact_sales
        GROUP BY order_year
        ORDER BY order_year
    """).fetchdf()

    connection.close()

    return result


def get_top_products(limit=10):
    """Return the highest-revenue products."""
    connection = get_connection()

    result = connection.execute("""
        SELECT
            product_id,
            ROUND(SUM(total_item_value), 2) AS revenue,
            COUNT(*) AS items_sold
        FROM fact_sales
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT ?
    """, [limit]).fetchdf()

    connection.close()

    return result


if __name__ == "__main__":
    print("\nTesting Analytics Layer...")

    metrics = get_total_metrics()

    print("\nOverall Metrics:")
    print(f"Total sales records: {metrics['total_sales_records']:,}")
    print(f"Total revenue: {metrics['total_revenue']:,.2f}")
    print(f"Average item value: {metrics['average_item_value']:,.2f}")

    print("\nTop Product Categories:")
    print(get_top_categories().to_string(index=False))

    print("\nYearly Revenue:")
    print(get_yearly_revenue().to_string(index=False))

    print("\nTop Products:")
    print(get_top_products().to_string(index=False))

    print("\nAnalytics layer tested successfully!")