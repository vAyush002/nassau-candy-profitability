# Nassau Candy Distributor — Product Profitability Analysis

This project demonstrates a data analytics workflow for a Machine Learning Intern role focused on product line profitability and margin performance.

## Project Summary
- Cleaned and prepared raw order data with invalid rows removed, missing values handled, and product labels standardized.
- Built business KPIs such as Gross Margin %, Profit per Unit, Revenue Contribution, and Profit Contribution.
- Identified which products were truly profitable versus those with high sales but low profit margins.
- Compared performance across divisions: Chocolate, Sugar, and Other.
- Conducted an 80/20 Pareto analysis to identify the products driving 80% of profit.
- Highlighted low-margin, cost-heavy products for repricing or discontinuation.
- Created an interactive Streamlit dashboard to filter data by date, division, and margin thresholds.

## Files
- `data_cleaning.py`: Clean raw dataset and derive profit metrics.
- `candy_profit_analysis.py`: Produce product- and division-level profitability summaries and Pareto analysis.
- `streamlit_app.py`: Interactive dashboard for exploring financial insights.
- `download_dataset.py`: Optional script to download the raw dataset from Google Drive.
- `requirements.txt`: Required Python packages.

## Run the project
1. Activate the virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Clean the data and compute KPI columns:
   ```bash
   python data_cleaning.py
   ```
4. Run the profitability analysis:
   ```bash
   python candy_profit_analysis.py
   ```
5. Start the dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```

## GitHub and Streamlit deployment
1. Initialize the local repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Nassau Candy profitability dashboard"
   ```
2. Create a GitHub repository and add it as remote, for example:
   ```bash
   git remote add origin https://github.com/<your-username>/nassau-candy-profitability.git
   git push -u origin main
   ```
3. Deploy on Streamlit Community Cloud:
   - Connect your GitHub account.
   - Select this repository.
   - Use `streamlit run streamlit_app.py` as the start command if prompted, or leave default.

## Notes
- If you want the dataset to be downloaded dynamically instead of included, run:
  ```bash
  python download_dataset.py
  ```

## Resume-ready contributions
- Cleaned and validated sales and profitability data for Nassau Candy Distributor.
- Computed business metrics and product-level profitability to surface the most valuable product lines.
- Performed division performance comparison and Pareto analysis to guide pricing and product rationalization.
- Delivered an interactive dashboard for the team to explore insights and make data-driven decisions.

## Outcome
The project turned raw order data into actionable business intelligence, helping identify high-profit products, weak margin SKUs, and division-level opportunities for promotion or repricing.
