"""
Nassau Candy Distributor - Profitability Analysis
This module builds on cleaned sales data to produce business KPIs,
product-level profitability rankings, division performance summaries,
and an 80/20 Pareto analysis.
"""

import pandas as pd
from pathlib import Path


def load_dataset(clean_path: str = "cleaned_nassau_candy.csv", raw_path: str = "nassau_candy_data.csv") -> pd.DataFrame:
    if Path(clean_path).exists():
        return pd.read_csv(clean_path, parse_dates=["Order Date", "Ship Date"], dayfirst=False)
    if not Path(raw_path).exists():
        raise FileNotFoundError(f"Dataset not found: {raw_path}")
    from data_cleaning import CandyDataCleaner  # noqa: E402

    cleaner = CandyDataCleaner(raw_path)
    cleaner.clean_data()
    cleaner.save_data(clean_path)
    return cleaner.df


def create_product_profit_summary(df: pd.DataFrame) -> pd.DataFrame:
    products = (
        df.groupby(["Division", "Product ID", "Product Name"], dropna=False)
        .agg(
            Total_Sales=("Sales", "sum"),
            Total_Units=("Units", "sum"),
            Total_Profit=("Gross Profit", "sum"),
            Total_Cost=("Cost", "sum"),
        )
        .reset_index()
    )
    products["Avg_Margin"] = products.apply(
        lambda row: row["Total_Profit"] / row["Total_Sales"] * 100 if row["Total_Sales"] > 0 else 0,
        axis=1,
    )
    products["Avg_Profit_per_Unit"] = products.apply(
        lambda row: row["Total_Profit"] / row["Total_Units"] if row["Total_Units"] > 0 else 0,
        axis=1,
    )
    products["Profitability_Rank"] = products["Total_Profit"].rank(method="dense", ascending=False).astype(int)
    products = products.sort_values(by="Total_Profit", ascending=False)
    total_sales = products["Total_Sales"].sum()
    total_profit = products["Total_Profit"].sum()
    products["Revenue_Contribution_%"] = products["Total_Sales"] / total_sales * 100
    products["Profit_Contribution_%"] = products["Total_Profit"] / total_profit * 100
    return products


def create_division_summary(df: pd.DataFrame) -> pd.DataFrame:
    division = (
        df.groupby("Division", dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Cost=("Cost", "sum"),
        )
        .reset_index()
    )
    division["Avg_Margin"] = division.apply(
        lambda row: row["Profit"] / row["Sales"] * 100 if row["Sales"] > 0 else 0,
        axis=1,
    )
    total_sales = division["Sales"].sum()
    total_profit = division["Profit"].sum()
    division["Sales_Share_%"] = division["Sales"] / total_sales * 100
    division["Profit_Share_%"] = division["Profit"] / total_profit * 100
    division = division.sort_values(by="Profit", ascending=False)
    return division


def create_pareto_table(product_summary: pd.DataFrame) -> pd.DataFrame:
    pareto = product_summary.copy()
    pareto = pareto.sort_values(by="Total_Profit", ascending=False)
    pareto["Cum_Profit"] = pareto["Total_Profit"].cumsum()
    pareto["Cum_Profit_%"] = pareto["Cum_Profit"] / pareto["Total_Profit"].sum() * 100
    pareto["Pareto_80"] = pareto["Cum_Profit_%"] <= 80
    return pareto


def low_margin_products(product_summary: pd.DataFrame, threshold: float = 25.0) -> pd.DataFrame:
    low_margin = product_summary[product_summary["Avg_Margin"] < threshold].copy()
    low_margin = low_margin.sort_values(by="Avg_Margin")
    return low_margin


def save_summary(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(filename, index=False)
    print(f"Saved: {filename}")


def main() -> None:
    print("📌 Nassau Candy Distributor - Profitability Analysis")
    df = load_dataset()

    product_summary = create_product_profit_summary(df)
    division_summary = create_division_summary(df)
    pareto = create_pareto_table(product_summary)
    low_margin = low_margin_products(product_summary, threshold=25.0)

    save_summary(product_summary, "product_profit_summary.csv")
    save_summary(division_summary, "division_profit_summary.csv")
    save_summary(pareto, "pareto_profit_summary.csv")
    save_summary(low_margin.head(50), "low_margin_products.csv")

    print("\nTop 5 products by profit:")
    print(product_summary[["Division", "Product Name", "Total_Sales", "Total_Profit", "Avg_Margin"]].head(5).to_string(index=False))

    print("\nDivision performance:")
    print(division_summary.to_string(index=False))

    print("\nTop low-margin products (Avg Margin < 25%):")
    print(low_margin[["Division", "Product Name", "Avg_Margin", "Total_Profit"]].head(10).to_string(index=False))

    print("\n✅ Analysis completed. Summary files generated.")


if __name__ == "__main__":
    main()
