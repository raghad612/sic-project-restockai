# ReStock AI

Demand forecasting and order recommendations for shops.
Samsung Innovation Campus AI capstone, Team Forecast Crew (2026).

## The problem
Shops lose money in two ways: ordering too much (waste, especially for perishables) or too little (stockouts and lost sales). Store and purchasing managers usually decide by gut feeling or by repeating last week's order.

## Our solution
ReStock AI predicts a demand range (low, expected, high) for each product and recommends tomorrow's order quantity, with a plain-language explanation of why.

## How it works (planned)
1. Data: daily sales per store and product, with promotions and holidays.
2. Forecasting: one global model trained across many stores and products. We compare a naive baseline (last week's sales), gradient boosting (LightGBM) with quantile forecasts, and one simple deep learning model.
3. Evaluation: walk-forward backtest on the most recent months, always split by time. We report forecast error against the baselines.
4. Order recommendation: forecast ranges converted into order quantities (lower quantile for perishables, higher for costly stockouts).
5. Explanation: each recommendation comes with the main demand drivers, written in plain language by a GenAI layer that uses only numbers produced by the models.
6. App: a simple web app for the store manager.

## Data
Public retail sales data from Kaggle (Corporacion Favorita), subsampled to 12 stores, 250 items and 2015-08-01 to 2017-07-31 to run on free Google Colab. The data is not stored in this repo.

## Tech stack
Python, pandas, LightGBM, PyTorch or Keras, SHAP, FastAPI, Streamlit, Google Colab.

## Status
Work in progress. Phase 1 (exploration, cleaning, features, time split, naive baseline) is done. Naive baseline (same day last week): count-family WAPE about 59% on validation and test, see notes/results.md. Next: LightGBM with quantile forecasts, then one simple deep learning model.

## Team
Forecast Crew.
