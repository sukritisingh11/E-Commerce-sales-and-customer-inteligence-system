import streamlit as st
import pandas as pd
from pathlib import Path

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="E-Commerce Customer Intelligence",
    page_icon="🛒",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("🛒 E-Commerce Sales & Customer Intelligence System")

st.markdown(
    "### B.Tech Machine Learning & Data Analytics Project"
)

st.markdown(
    "Analyze sales performance, customers, products, "
    "customer segments, and sales predictions."
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    # Location of ml.py
    BASE_DIR = Path(__file__).resolve().parent

    # All CSV files are inside datasets
    DATA_DIR = BASE_DIR / "Datasets"

    # Check dataset folder
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATA_DIR}"
        )

    # Load datasets
    customers = pd.read_csv(
        DATA_DIR / "customers_dataset.csv"
    )

    orders = pd.read_csv(
        DATA_DIR / "Order_datasets.csv"
    )

    order_items = pd.read_csv(
        DATA_DIR / "Order_items_datasets.csv"
    )

    products = pd.read_csv(
        DATA_DIR / "Product_datasets.csv"
    )

    return customers, orders, order_items, products


# =========================================================
# LOAD DATA WITH ERROR HANDLING
# =========================================================

try:

    customers, orders, order_items, products = load_data()

except FileNotFoundError as e:

    st.error("❌ Dataset file not found.")

    st.write("Your project should have this structure:")

    st.code(
        """
ECSCIS/
│
├── ml.py
│
└── Datasets/
    ├── customers_dataset.csv
    ├── Orders_datasets.csv
    ├── Order_items_datasets.csv
    └── Product_datasets.csv
        """
    )

    st.error(str(e))

    st.stop()

except Exception as e:

    st.error(
        f"❌ Error while loading datasets: {e}"
    )

    st.stop()


# =========================================================
# DATASET INFORMATION
# =========================================================

st.success("✅ All datasets loaded successfully!")

with st.expander("📋 Dataset Information"):

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Customers",
        f"{len(customers):,}"
    )

    col2.metric(
        "Orders",
        f"{len(orders):,}"
    )

    col3.metric(
        "Order Items",
        f"{len(order_items):,}"
    )

    col4.metric(
        "Products",
        f"{len(products):,}"
    )


# =========================================================
# DATE CONVERSION
# =========================================================

if "order_purchase_timestamp" in orders.columns:

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce"
    )

else:

    st.error(
        "❌ The column 'order_purchase_timestamp' "
        "was not found in Orders_datasets.csv."
    )

    st.write(
        "Available columns:"
    )

    st.write(
        orders.columns.tolist()
    )

    st.stop()


# =========================================================
# CREATE SALES DATA
# =========================================================

if "order_id" not in orders.columns:

    st.error(
        "❌ 'order_id' column is missing from orders dataset."
    )

    st.stop()


if "order_id" not in order_items.columns:

    st.error(
        "❌ 'order_id' column is missing from order items dataset."
    )

    st.stop()


sales = orders.merge(
    order_items,
    on="order_id",
    how="inner"
)


# =========================================================
# MERGE PRODUCT INFORMATION
# =========================================================

if "product_id" in sales.columns and "product_id" in products.columns:

    product_columns = ["product_id"]

    if "product_category_name" in products.columns:

        product_columns.append(
            "product_category_name"
        )

    sales = sales.merge(
        products[product_columns],
        on="product_id",
        how="left"
    )


# =========================================================
# REVENUE CALCULATION
# =========================================================

if "price" in sales.columns:

    sales["revenue"] = pd.to_numeric(
        sales["price"],
        errors="coerce"
    ).fillna(0)

else:

    st.error(
        "❌ 'price' column was not found in "
        "Order_items_datasets.csv."
    )

    st.write(
        "Available columns:"
    )

    st.write(
        order_items.columns.tolist()
    )

    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

if "customer_unique_id" in customers.columns:

    total_customers = customers[
        "customer_unique_id"
    ].nunique()

elif "customer_id" in customers.columns:

    total_customers = customers[
        "customer_id"
    ].nunique()

else:

    total_customers = len(customers)


total_orders = orders[
    "order_id"
].nunique()


total_revenue = sales[
    "revenue"
].sum()


if total_orders > 0:

    average_order_value = (
        total_revenue / total_orders
    )

else:

    average_order_value = 0


# =========================================================
# MAIN KPI DASHBOARD
# =========================================================

st.divider()

st.subheader("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "👥 Total Customers",
        f"{total_customers:,}"
    )

with col2:

    st.metric(
        "📦 Total Orders",
        f"{total_orders:,}"
    )

with col3:

    st.metric(
        "💰 Total Revenue",
        f"R$ {total_revenue:,.2f}"
    )

with col4:

    st.metric(
        "🛍️ Average Order Value",
        f"R$ {average_order_value:,.2f}"
    )


# =========================================================
# MONTHLY SALES
# =========================================================

st.divider()

st.subheader("📈 Monthly Sales")

monthly_sales = (
    sales
    .dropna(
        subset=["order_purchase_timestamp"]
    )
    .set_index(
        "order_purchase_timestamp"
    )
    .resample("ME")["revenue"]
    .sum()
)

if len(monthly_sales) > 0:

    st.line_chart(
        monthly_sales,
        use_container_width=True
    )

else:

    st.warning(
        "No valid sales date information available."
    )


# =========================================================
# MONTHLY ORDER COUNT
# =========================================================

st.subheader("📦 Monthly Orders")

monthly_orders = (
    orders
    .dropna(
        subset=["order_purchase_timestamp"]
    )
    .set_index(
        "order_purchase_timestamp"
    )
    .resample("ME")["order_id"]
    .nunique()
)

st.line_chart(
    monthly_orders,
    use_container_width=True
)


# =========================================================
# ORDER STATUS
# =========================================================

st.divider()

st.subheader("📦 Order Status")

if "order_status" in orders.columns:

    status_count = (
        orders["order_status"]
        .value_counts()
    )

    st.bar_chart(
        status_count,
        use_container_width=True
    )

    status_table = (
        status_count
        .reset_index()
    )

    status_table.columns = [
        "Order Status",
        "Number of Orders"
    ]

    st.dataframe(
        status_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "The 'order_status' column was not found."
    )


# =========================================================
# TOP PRODUCT CATEGORIES
# =========================================================

st.divider()

st.subheader("🏆 Top 10 Product Categories")

if "product_category_name" in sales.columns:

    category_sales = (
        sales
        .dropna(
            subset=["product_category_name"]
        )
        .groupby(
            "product_category_name"
        )["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    if len(category_sales) > 0:

        st.bar_chart(
            category_sales,
            use_container_width=True
        )

        category_table = (
            category_sales
            .reset_index()
        )

        category_table.columns = [
            "Product Category",
            "Revenue"
        ]

        st.dataframe(
            category_table,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No product category information available."
        )

else:

    st.warning(
        "The 'product_category_name' column "
        "was not found in the product dataset."
    )


# =========================================================
# TOP PRODUCTS
# =========================================================

st.divider()

st.subheader("🥇 Top 10 Products by Revenue")

if "product_id" in sales.columns:

    top_products = (
        sales
        .groupby(
            "product_id"
        )["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    st.bar_chart(
        top_products,
        use_container_width=True
    )

    product_table = (
        top_products
        .reset_index()
    )

    product_table.columns = [
        "Product ID",
        "Revenue"
    ]

    st.dataframe(
        product_table,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# CUSTOMER SEGMENTATION
# =========================================================

st.divider()

st.subheader("👥 Customer Segmentation")

BASE_DIR = Path(__file__).resolve().parent

SEGMENT_FILE = (
    BASE_DIR /
    "customer_segmentation.csv"
)

if SEGMENT_FILE.exists():

    try:

        rfm = pd.read_csv(
            SEGMENT_FILE
        )

        st.success(
            "✅ Customer segmentation data loaded."
        )

        # ---------------------------------------------
        # CLUSTER DISTRIBUTION
        # ---------------------------------------------

        if "cluster" in rfm.columns:

            cluster_count = (
                rfm["cluster"]
                .value_counts()
                .sort_index()
            )

            st.write(
                "### Customer Cluster Distribution"
            )

            st.bar_chart(
                cluster_count,
                use_container_width=True
            )

            cluster_table = (
                cluster_count
                .reset_index()
            )

            cluster_table.columns = [
                "Cluster",
                "Number of Customers"
            ]

            st.dataframe(
                cluster_table,
                use_container_width=True,
                hide_index=True
            )

        # ---------------------------------------------
        # RFM DATA
        # ---------------------------------------------

        st.write(
            "### Customer RFM Data"
        )

        st.dataframe(
            rfm.head(20),
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:

        st.error(
            f"Error loading customer segmentation: {e}"
        )

else:

    st.info(
        "ℹ️ customer_segmentation.csv was not found."
    )

    st.write(
        "Run your customer segmentation model "
        "to generate this file."
    )


# =========================================================
# SALES PREDICTION
# =========================================================

st.divider()

st.subheader("🔮 Sales Prediction")

PREDICTION_FILE = (
    BASE_DIR /
    "sales_predictions.csv"
)

if PREDICTION_FILE.exists():

    try:

        predictions = pd.read_csv(
            PREDICTION_FILE
        )

        st.success(
            "✅ Sales prediction data loaded."
        )

        st.write(
            "### Recent Predictions"
        )

        st.dataframe(
            predictions.tail(10),
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------------------
        # FIND PREDICTION COLUMN
        # ---------------------------------------------

        prediction_columns = [
            column
            for column in predictions.columns
            if (
                "predict" in column.lower()
                or
                "forecast" in column.lower()
                or
                "sales" in column.lower()
            )
        ]

        if len(prediction_columns) > 0:

            prediction_column = (
                prediction_columns[0]
            )

            st.write(
                "### 📈 Prediction Trend"
            )

            st.line_chart(
                predictions[
                    prediction_column
                ],
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Error loading sales predictions: {e}"
        )

else:

    st.info(
        "ℹ️ sales_predictions.csv was not found."
    )

    st.write(
        "Run your sales prediction model "
        "to generate this file."
    )


# =========================================================
# DATASET PREVIEW
# =========================================================

st.divider()

st.subheader("🔍 Dataset Preview")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "👥 Customers",
        "📦 Orders",
        "🛒 Order Items",
        "🏷️ Products"
    ]
)


with tab1:

    st.write(
        f"Customer dataset: {len(customers):,} records"
    )

    st.dataframe(
        customers.head(10),
        use_container_width=True,
        hide_index=True
    )


with tab2:

    st.write(
        f"Order dataset: {len(orders):,} records"
    )

    st.dataframe(
        orders.head(10),
        use_container_width=True,
        hide_index=True
    )


with tab3:

    st.write(
        f"Order items dataset: {len(order_items):,} records"
    )

    st.dataframe(
        order_items.head(10),
        use_container_width=True,
        hide_index=True
    )


with tab4:

    st.write(
        f"Product dataset: {len(products):,} records"
    )

    st.dataframe(
        products.head(10),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🛒 E-Commerce Sales and Customer Intelligence System "
    "| B.Tech Machine Learning & Data Analytics Project"
)
