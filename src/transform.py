from pathlib import Path
import pandas as pd

# Paths
RAW_LAKE_PATH = Path("data/lake/raw")
PROCESSED_LAKE_PATH = Path("data/lake/processed")

PROCESSED_LAKE_PATH.mkdir(parents=True, exist_ok=True)


def transform_sales_data():
    print("Reading raw Parquet files...")

    orders = pd.read_parquet(
        RAW_LAKE_PATH / "olist_orders_dataset.parquet"
    )

    order_items = pd.read_parquet(
        RAW_LAKE_PATH / "olist_order_items_dataset.parquet"
    )

    products = pd.read_parquet(
        RAW_LAKE_PATH / "olist_products_dataset.parquet"
    )

    category_translation = pd.read_parquet(
        RAW_LAKE_PATH / "product_category_name_translation.parquet"
    )

    print("Filtering delivered orders...")

    # Keep only completed deliveries for sales analysis
    orders = orders[
        orders["order_status"] == "delivered"
    ].copy()

    # Convert timestamp
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    )

    # Join orders with order items
    sales = orders.merge(
        order_items,
        on="order_id",
        how="inner"
    )

    # Join sales with product information
    sales = sales.merge(
        products[
            ["product_id", "product_category_name"]
        ],
        on="product_id",
        how="left"
    )

    # Translate category names into English
    sales = sales.merge(
        category_translation,
        on="product_category_name",
        how="left"
    )

    # Calculate revenue
    sales["total_item_value"] = (
        sales["price"] + sales["freight_value"]
    )

    # Create analytical date fields
    sales["order_date"] = (
        sales["order_purchase_timestamp"].dt.date
    )

    sales["order_year"] = (
        sales["order_purchase_timestamp"].dt.year
    )

    sales["order_month"] = (
        sales["order_purchase_timestamp"].dt.month
    )

    sales["order_year_month"] = (
        sales["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )

    # Select useful analytical columns
    sales = sales[
        [
            "order_id",
            "customer_id",
            "product_id",
            "seller_id",
            "order_status",
            "order_purchase_timestamp",
            "order_date",
            "order_year",
            "order_month",
            "order_year_month",
            "product_category_name",
            "product_category_name_english",
            "price",
            "freight_value",
            "total_item_value",
        ]
    ]

    # Remove duplicate records
    sales = sales.drop_duplicates()

    # Save the processed dataset
    output_file = PROCESSED_LAKE_PATH / "fact_sales.parquet"

    sales.to_parquet(
        output_file,
        index=False
    )

    print("\nTransformation completed successfully!")
    print(f"Rows generated: {len(sales):,}")
    print(f"Columns generated: {len(sales.columns)}")
    print(f"Saved to: {output_file}")

    print("\nSample transformed data:")
    print(sales.head(5).to_string(index=False))


if __name__ == "__main__":
    transform_sales_data()