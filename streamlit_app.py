"""
Streamlit dashboard for Nassau Candy Distributor
Use: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


@st.cache_data
def load_data(clean_path: str = "cleaned_nassau_candy.csv", raw_path: str = "nassau_candy_data.csv") -> pd.DataFrame:
    if Path(clean_path).exists():
        return pd.read_csv(clean_path, parse_dates=["Order Date", "Ship Date"], dayfirst=False)
    from data_cleaning import CandyDataCleaner  # noqa: E402
    cleaner = CandyDataCleaner(raw_path)
    cleaner.clean_data()
    cleaner.save_data(clean_path)
    return cleaner.df


def filter_data(df: pd.DataFrame, divisions, start_date, end_date, min_margin=0.0):
    if divisions:
        df = df[df["Division"].isin(divisions)]
    df = df[(df["Order Date"] >= start_date) & (df["Order Date"] <= end_date)]
    if min_margin is not None and min_margin > 0:
        df = df[df["Gross Margin %"] >= min_margin]
    return df


def create_summary_cards(df: pd.DataFrame):
    total_sales = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()
    avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    product_profit = df.groupby("Product Name")["Gross Profit"].sum()
    if not product_profit.empty:
        top_product = product_profit.idxmax()
        top_profit = product_profit.max()
    else:
        top_product = "No product"
        top_profit = 0
    return total_sales, total_profit, avg_margin, top_product, top_profit


def create_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["Product ID", "Product Name"], dropna=False)
        .agg(
            Total_Sales=("Sales", "sum"),
            Total_Units=("Units", "sum"),
            Total_Profit=("Gross Profit", "sum"),
            Total_Cost=("Cost", "sum"),
        )
        .reset_index()
    )
    summary["Margin %"] = summary.apply(
        lambda row: row["Total_Profit"] / row["Total_Sales"] * 100 if row["Total_Sales"] > 0 else 0,
        axis=1,
    )
    summary["Profit per Unit"] = summary.apply(
        lambda row: row["Total_Profit"] / row["Total_Units"] if row["Total_Units"] > 0 else 0,
        axis=1,
    )
    summary = summary.sort_values(by="Total_Profit", ascending=False).reset_index(drop=True)
    summary["Cum_Profit"] = summary["Total_Profit"].cumsum()
    total_profit = summary["Total_Profit"].sum()
    summary["Cum_Profit_%"] = summary["Cum_Profit"] / total_profit * 100 if total_profit > 0 else 0
    return summary


def main():
    st.set_page_config(page_title="Nassau Candy Profitability", layout="wide")
    st.title("🍬 Nassau Candy Distributor — Profitability Dashboard")
    st.markdown(
        "Explore product profitability, division performance, and Pareto insights for better pricing and promotion decisions."
    )

    df = load_data()
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce", dayfirst=False)

    divisions = st.sidebar.multiselect(
        "Select divisions",
        options=sorted(df["Division"].unique()),
        default=sorted(df["Division"].unique()),
    )
    min_date = df["Order Date"].min()
    max_date = df["Order Date"].max()
    date_range = st.sidebar.date_input("Order date range", [min_date, max_date])
    margin_threshold = st.sidebar.slider("Minimum gross margin %", 0.0, 100.0, 20.0, 1.0)
    low_margin_threshold = st.sidebar.slider("Low-margin review threshold %", 0.0, 50.0, 25.0, 1.0)

    if len(date_range) != 2:
        st.sidebar.error("Please select a valid start and end date.")
        return

    scope_df = filter_data(df, divisions, pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]), min_margin=0.0)
    filtered = filter_data(df, divisions, pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]), min_margin=margin_threshold)

    if scope_df.empty:
        st.warning("No records match the selected division and date filters.")
        return

    if filtered.empty:
        st.warning("No records meet the selected minimum margin. Charts will not display until limits are relaxed.")

    total_sales, total_profit, avg_margin, top_product, top_profit = create_summary_cards(filtered)

    st.metric("Total Sales", f"${total_sales:,.0f}", help="Total revenue for selected filters")
    st.metric("Total Gross Profit", f"${total_profit:,.1f}")
    st.metric("Average Gross Margin", f"{avg_margin:.1f}%")
    st.metric("Top Product by Profit", f"{top_product}", delta=f"${top_profit:,.0f}")

    if not filtered.empty:
        col1, col2 = st.columns(2)
        with col1:
            product_profit = (
                filtered.groupby("Product Name")["Gross Profit"].sum().reset_index().sort_values(by="Gross Profit", ascending=False).head(12)
            )
            fig = px.bar(product_profit, x="Gross Profit", y="Product Name", orientation="h", title="Top Products by Profit")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            division_profit = (
                filtered.groupby("Division")["Gross Profit"].sum().reset_index().sort_values(by="Gross Profit", ascending=False)
            )
            fig2 = px.pie(division_profit, names="Division", values="Gross Profit", title="Profit Share by Division")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("Product Profitability and Pareto Analysis")

        product_summary = create_product_summary(filtered)
        st.dataframe(product_summary.head(15), use_container_width=True)

        fig3 = px.line(product_summary, x=product_summary.index + 1, y="Cum_Profit_%", title="Pareto Curve: Cumulative Profit Share")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Adjust the minimum gross margin filter to see top product and division charts.")

    st.markdown("---")
    st.subheader("Low-Margin Products to Review")
    product_summary = create_product_summary(scope_df)
    low_margin = product_summary[product_summary["Margin %"] < low_margin_threshold].sort_values(by="Margin %")
    st.dataframe(low_margin.head(20), use_container_width=True)

    st.markdown(
        "#### Notes\nUse this dashboard to identify products with high revenue but low margin, check division strength, and prioritize pricing or discontinuation decisions."
    )


if __name__ == "__main__":
    main()
