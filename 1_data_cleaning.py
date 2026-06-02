"""
Nassau Candy Distributor - Data Cleaning Module
Author: Ayush Anand
Internship: Unified Mentor UMID31032686678
"""

import os
import pandas as pd
import numpy as np


class CandyDataCleaner:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = pd.read_csv(filepath)
        self.initial_shape = self.df.shape
        self.cleaning_log = {}

        print("=" * 60)
        print("🍬 NASSAU CANDY - DATA CLEANING PIPELINE")
        print("=" * 60)
        print(f"\n📊 Dataset Loaded")
        print(f"   Shape: {self.initial_shape}")
        print(f"   Columns: {list(self.df.columns)}")

    def explore_data(self):
        """Display high-level data exploration results."""
        print("\n" + "=" * 60)
        print("📋 DATA EXPLORATION")
        print("=" * 60)
        print("\n📌 First 5 rows:")
        print(self.df.head())
        print("\n📌 Data Types:")
        print(self.df.dtypes)
        print("\n📌 Missing Values:")
        missing = self.df.isnull().sum()
        print(missing[missing > 0])
        print("\n📌 Basic Statistics:")
        print(self.df.describe(include='all'))

    def clean_data(self):
        """Run the full cleaning pipeline and prepare KPI columns."""
        print("\n" + "=" * 60)
        print("🧹 STARTING DATA CLEANING")
        print("=" * 60)

        self._normalize_columns()
        self._remove_duplicates()
        self._convert_numeric_fields()
        self._clean_text_fields()
        self._standardize_dates()
        self._drop_invalid_rows()
        self._infer_profit_fields()
        self._compute_profit_metrics()

        print("\n" + "=" * 60)
        print("📊 CLEANING SUMMARY")
        print("=" * 60)
        print(f"Initial rows: {self.initial_shape[0]}")
        print(f"Final rows: {len(self.df)}")
        print(f"Rows removed: {self.initial_shape[0] - len(self.df)}")
        print(f"Data retention: {(len(self.df) / self.initial_shape[0] * 100):.2f}%")
        print("=" * 60)

        return self.df

    def _normalize_columns(self):
        self.df.columns = [col.strip() for col in self.df.columns]

    def _remove_duplicates(self):
        step = "Remove Duplicates"
        initial = len(self.df)
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        removed = initial - len(self.df)
        self.cleaning_log[step] = removed
        print(f"✅ Step 1 - {step}: Removed {removed} duplicate rows")

    def _convert_numeric_fields(self):
        numeric_fields = ["Sales", "Units", "Gross Profit", "Cost"]
        for field in numeric_fields:
            if field in self.df.columns:
                self.df[field] = pd.to_numeric(self.df[field], errors="coerce")

        step = "Handle Missing Numeric Values"
        missing_before = self.df[[col for col in numeric_fields if col in self.df.columns]].isna().sum().sum()
        for field in numeric_fields:
            if field in self.df.columns:
                self.df[field] = self.df[field].fillna(self.df[field].median())
        missing_after = self.df[[col for col in numeric_fields if col in self.df.columns]].isna().sum().sum()
        self.cleaning_log[step] = missing_before - missing_after
        print(f"✅ Step 2 - {step}: Filled {missing_before - missing_after} missing numeric values")

    def _clean_text_fields(self):
        text_columns = self.df.select_dtypes(include=[object]).columns.tolist()
        for col in text_columns:
            self.df[col] = self.df[col].astype(str).str.strip()
            if col.lower() in ["product name", "division", "ship mode", "region"]:
                self.df[col] = self.df[col].str.title().str.replace(r"\s+", " ", regex=True)

        step = "Standardize Text"
        self.cleaning_log[step] = len(text_columns)
        print(f"✅ Step 3 - {step}: Standardized {len(text_columns)} text columns")

    def _standardize_dates(self):
        date_cols = [col for col in self.df.columns if "date" in col.lower()]
        for col in date_cols:
            self.df[col] = pd.to_datetime(self.df[col], dayfirst=True, errors="coerce")

        step = "Convert Dates"
        self.cleaning_log[step] = len(date_cols)
        print(f"✅ Step 4 - {step}: Converted {len(date_cols)} date columns")

    def _drop_invalid_rows(self):
        step = "Drop Invalid Rows"
        required = ["Order ID", "Product Name", "Division", "Sales", "Units", "Gross Profit", "Cost"]
        required = [col for col in required if col in self.df.columns]
        initial = len(self.df)

        if required:
            self.df = self.df.dropna(subset=required)

        if "Sales" in self.df.columns:
            self.df = self.df[self.df["Sales"] > 0]
        if "Units" in self.df.columns:
            self.df = self.df[self.df["Units"] > 0]
        if "Gross Profit" in self.df.columns:
            self.df = self.df[self.df["Gross Profit"].notna()]

        self.df = self.df.reset_index(drop=True)
        removed = initial - len(self.df)
        self.cleaning_log[step] = removed
        print(f"✅ Step 5 - {step}: Removed {removed} invalid or empty rows")

    def _infer_profit_fields(self):
        if "Gross Profit" in self.df.columns and "Cost" in self.df.columns and "Sales" in self.df.columns:
            missing_profit = self.df["Gross Profit"].isna() & self.df[["Sales", "Cost"]].notna().all(axis=1)
            if missing_profit.any():
                self.df.loc[missing_profit, "Gross Profit"] = self.df.loc[missing_profit, "Sales"] - self.df.loc[missing_profit, "Cost"]

    def _compute_profit_metrics(self):
        self.df["Gross Margin %"] = np.where(
            self.df["Sales"] > 0,
            self.df["Gross Profit"] / self.df["Sales"] * 100,
            0,
        )
        self.df["Profit per Unit"] = np.where(
            self.df["Units"] > 0,
            self.df["Gross Profit"] / self.df["Units"],
            0,
        )
        self.df["Sales per Unit"] = np.where(
            self.df["Units"] > 0,
            self.df["Sales"] / self.df["Units"],
            0,
        )
        total_sales = self.df["Sales"].sum()
        total_profit = self.df["Gross Profit"].sum()
        self.df["Revenue Contribution %"] = np.where(
            total_sales > 0,
            self.df["Sales"] / total_sales * 100,
            0,
        )
        self.df["Profit Contribution %"] = np.where(
            total_profit > 0,
            self.df["Gross Profit"] / total_profit * 100,
            0,
        )

        step = "Compute Profit Metrics"
        self.cleaning_log[step] = 1
        print(f"✅ Step 6 - {step}: Added Gross Margin %, Profit per Unit, and contribution metrics")

    def save_data(self, output_path: str = "cleaned_nassau_candy.csv") -> str:
        self.df.to_csv(output_path, index=False)
        print(f"\n💾 Cleaned data saved to: {output_path}")
        print(f"   Size: {os.path.getsize(output_path) / 1024:.2f} KB")
        return output_path


if __name__ == "__main__":
    cleaner = CandyDataCleaner("nassau_candy_data.csv")
    cleaner.explore_data()
    cleaned_df = cleaner.clean_data()
    cleaner.save_data()
    print("\n🎉 Data cleaning completed successfully!")