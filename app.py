import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection

# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="Product Management System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------
# Custom CSS
# ---------------------------------------

st.markdown("""
<style>

.main{
    background-color:#F5F7FA;
}

h1{
    color:#1565C0;
    text-align:center;
}

.stButton>button{
    width:100%;
    height:45px;
    border-radius:8px;
    background:#1565C0;
    color:white;
    font-size:16px;
}

[data-testid="stMetric"]{
    background:white;
    padding:15px;
    border-radius:10px;
    box-shadow:0px 3px 8px rgba(0,0,0,.15);
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# Database Connection
# ---------------------------------------

conn = get_connection()

if conn is None:
    st.stop()

cursor = conn.cursor()

# ---------------------------------------
# Header
# ---------------------------------------

st.title("🛒 Product Management System")

st.write("Manage Products Using Python, Streamlit and MySQL")

st.divider()

# ---------------------------------------
# Sidebar Menu
# ---------------------------------------

menu = st.sidebar.selectbox(

    "Select Operation",

    (

        "🏠 Dashboard",

        "➕ Add Product",

        "📋 View Products",

        "🔍 Search Product",

        "✏️ Update Product",

        "🗑 Delete Product",

        "📊 Charts"

    )

)

# ---------------------------------------
# Dashboard
# ---------------------------------------

def dashboard():

    st.subheader("📊 Dashboard")

    cursor.execute("SELECT COUNT(*) FROM product_table")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity) FROM product_table")
    total_quantity = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(price) FROM product_table")
    total_price = cursor.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📦 Total Products",
        total_products
    )

    col2.metric(
        "📦 Total Quantity",
        total_quantity
    )

    col3.metric(
        "💰 Total Price",
        f"₹ {total_price:,.2f}"
    )

    st.divider()

    st.info("Select an option from the sidebar to continue.")
    # ---------------------------------------
# Add Product
# ---------------------------------------

def add_product():

    st.subheader("➕ Add New Product")

    col1, col2 = st.columns(2)

    with col1:

        product_id = st.number_input(
            "Product ID",
            min_value=1,
            step=1
        )

        product_name = st.text_input(
            "Product Name"
        )

        category = st.text_input(
            "Category"
        )

    with col2:

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

        price = st.number_input(
            "Price",
            min_value=0.0,
            step=1.0
        )

        feedback = st.text_area(
            "Feedback"
        )

    st.divider()

    if st.button("💾 Save Product"):

        if product_name.strip() == "" or category.strip() == "":

            st.warning("Please fill all required fields.")

        else:

            try:

                sql = """
                INSERT INTO product_table
                (
                    product_id,
                    product_name,
                    category,
                    quantity,
                    price,
                    feedback
                )
                VALUES
                (%s,%s,%s,%s,%s,%s)
                """

                values = (

                    product_id,

                    product_name,

                    category,

                    quantity,

                    price,

                    feedback

                )

                cursor.execute(sql, values)

                conn.commit()

                st.success("✅ Product Added Successfully")

            except Exception as e:

                st.error(f"Error : {e}")
# ---------------------------------------
# View Products
# ---------------------------------------

def view_products():

    st.subheader("📋 Product List")

    try:

        cursor.execute("""
            SELECT *
            FROM product_table
        """)

        records = cursor.fetchall()

        if len(records) == 0:

            st.warning("No Products Found")

            return

        columns = [

            "Product ID",

            "Product Name",

            "Category",

            "Quantity",

            "Price",

            "Feedback"

        ]

        df = pd.DataFrame(

            records,

            columns=columns

        )

        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True

        )

        st.divider()

        st.subheader("📊 Product Statistics")

        col1, col2, col3 = st.columns(3)

        col1.metric(

            "Total Products",

            len(df)

        )

        col2.metric(

            "Total Quantity",

            int(df["Quantity"].sum())

        )

        col3.metric(

            "Average Price",

            f"₹ {df['Price'].mean():,.2f}"

        )

        st.divider()

        csv = df.to_csv(index=False)

        st.download_button(

            label="📥 Download CSV",

            data=csv,

            file_name="products.csv",

            mime="text/csv",

            use_container_width=True

        )

    except Exception as e:

        st.error(f"Error : {e}")
# ---------------------------------------
# Search Product
# ---------------------------------------

def search_product():

    st.subheader("🔍 Search Product")

    product_id = st.number_input(

        "Enter Product ID",

        min_value=1,

        step=1,

        key="search_id"

    )

    st.divider()

    if st.button("🔍 Search"):

        try:

            sql = """
            SELECT *
            FROM product_table
            WHERE product_id=%s
            """

            cursor.execute(

                sql,

                (product_id,)

            )

            record = cursor.fetchone()

            if record:

                columns = [

                    "Product ID",

                    "Product Name",

                    "Category",

                    "Quantity",

                    "Price",

                    "Feedback"

                ]

                df = pd.DataFrame(

                    [record],

                    columns=columns

                )

                st.success("✅ Product Found")

                st.dataframe(

                    df,

                    use_container_width=True,

                    hide_index=True

                )

            else:

                st.error("❌ Product Not Found")

        except Exception as e:

            st.error(f"Error : {e}")
# ---------------------------------------
# Update Product
# ---------------------------------------

def update_product():

    st.subheader("✏️ Update Product")

    product_id = st.number_input(
        "Enter Product ID",
        min_value=1,
        step=1,
        key="update_id"
    )

    if st.button("Load Product"):

        try:

            sql = """
            SELECT *
            FROM product_table
            WHERE product_id = %s
            """

            cursor.execute(sql, (product_id,))

            record = cursor.fetchone()

            if record:

                st.session_state["record"] = record

            else:

                st.error("❌ Product Not Found")

        except Exception as e:

            st.error(f"Error : {e}")

    if "record" in st.session_state:

        record = st.session_state["record"]

        product_name = st.text_input(
            "Product Name",
            value=record[1]
        )

        category = st.text_input(
            "Category",
            value=record[2]
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=int(record[3])
        )

        price = st.number_input(
            "Price",
            min_value=0.0,
            value=float(record[4])
        )

        feedback = st.text_area(
            "Feedback",
            value=record[5]
        )

        if st.button("Update Product"):

            try:

                sql = """
                UPDATE product_table
                SET
                    product_name=%s,
                    category=%s,
                    quantity=%s,
                    price=%s,
                    feedback=%s
                WHERE product_id=%s
                """

                values = (

                    product_name,

                    category,

                    quantity,

                    price,

                    feedback,

                    product_id

                )

                cursor.execute(sql, values)

                conn.commit()

                st.success("✅ Product Updated Successfully")

                del st.session_state["record"]

            except Exception as e:

                st.error(f"Error : {e}")
# ---------------------------------------
# Delete Product
# ---------------------------------------

def delete_product():

    st.subheader("🗑 Delete Product")

    product_id = st.number_input(

        "Enter Product ID",

        min_value=1,

        step=1,

        key="delete_id"

    )

    st.divider()

    if st.button("🗑 Delete Product"):

        try:

            # Check whether product exists

            sql = """
            SELECT *
            FROM product_table
            WHERE product_id=%s
            """

            cursor.execute(

                sql,

                (product_id,)

            )

            record = cursor.fetchone()

            if record:

                delete_sql = """
                DELETE FROM product_table
                WHERE product_id=%s
                """

                cursor.execute(

                    delete_sql,

                    (product_id,)

                )

                conn.commit()

                st.success("✅ Product Deleted Successfully")

            else:

                st.error("❌ Product Not Found")

        except Exception as e:

            st.error(f"Error : {e}")
# ---------------------------------------
# Product Charts
# ---------------------------------------

def show_charts():

    st.subheader("📊 Product Analytics Dashboard")

    try:

        cursor.execute("""
            SELECT
                product_name,
                quantity,
                price
            FROM product_table
        """)

        records = cursor.fetchall()

        if len(records) == 0:

            st.warning("No Product Data Available")

            return

        df = pd.DataFrame(

            records,

            columns=[

                "Product",

                "Quantity",

                "Price"

            ]

        )

        # ---------------------------------------
        # Dashboard Metrics
        # ---------------------------------------

        total_products = len(df)

        total_quantity = df["Quantity"].sum()

        average_price = df["Price"].mean()

        inventory_value = (
            df["Quantity"] *
            df["Price"]
        ).sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📦 Products",
            total_products
        )

        c2.metric(
            "📦 Quantity",
            total_quantity
        )

        c3.metric(
            "💰 Average Price",
            f"₹ {average_price:,.2f}"
        )

        c4.metric(
            "💵 Inventory Value",
            f"₹ {inventory_value:,.2f}"
        )

        st.divider()

        # ---------------------------------------
        # Bar Chart
        # ---------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("📊 Product Quantity")

            fig, ax = plt.subplots(figsize=(7,4))

            ax.bar(

                df["Product"],

                df["Quantity"],

                color="steelblue"

            )

            ax.set_xlabel("Product")

            ax.set_ylabel("Quantity")

            ax.set_title("Quantity by Product")

            plt.xticks(rotation=30)

            st.pyplot(fig)

        # ---------------------------------------
        # Pie Chart
        # ---------------------------------------

        with col2:

            st.subheader("🥧 Quantity Distribution")

            fig2, ax2 = plt.subplots(figsize=(6,6))

            ax2.pie(

                df["Quantity"],

                labels=df["Product"],

                autopct="%1.1f%%",

                startangle=90

            )

            ax2.set_title("Product Quantity")

            st.pyplot(fig2)

        st.divider()

        # ---------------------------------------
        # Line Chart
        # ---------------------------------------

        st.subheader("📈 Product Price Analysis")

        fig3, ax3 = plt.subplots(figsize=(10,5))

        ax3.plot(

            df["Product"],

            df["Price"],

            marker="o",

            linewidth=3,

            color="green"

        )

        ax3.set_xlabel("Product")

        ax3.set_ylabel("Price")

        ax3.set_title("Product Price")

        plt.xticks(rotation=30)

        st.pyplot(fig3)

        st.divider()

        # ---------------------------------------
        # Statistics Table
        # ---------------------------------------

        st.subheader("📋 Product Data")

        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True

        )

        statistics = pd.DataFrame({

            "Metric":[

                "Total Products",

                "Total Quantity",

                "Average Price",

                "Inventory Value"

            ],

            "Value":[

                total_products,

                total_quantity,

                f"₹ {average_price:,.2f}",

                f"₹ {inventory_value:,.2f}"

            ]

        })

        st.subheader("📊 Statistics")

        st.table(statistics)

        st.divider()

        # ---------------------------------------
        # Download CSV
        # ---------------------------------------

        csv = df.to_csv(index=False)

        st.download_button(

            label="📥 Download CSV",

            data=csv,

            file_name="product_report.csv",

            mime="text/csv",

            use_container_width=True

        )

    except Exception as e:

        st.error(f"Error : {e}")
# ---------------------------------------
# Main Menu
# ---------------------------------------

if menu == "🏠 Dashboard":

    dashboard()

elif menu == "➕ Add Product":

    add_product()

elif menu == "📋 View Products":

    view_products()

elif menu == "🔍 Search Product":

    search_product()

elif menu == "✏️ Update Product":

    update_product()

elif menu == "🗑 Delete Product":

    delete_product()

elif menu == "📊 Charts":

    show_charts()