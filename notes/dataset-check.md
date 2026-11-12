# Dataset Check – ReStock AI

## 1. Dataset Comparison

| Requirement | Corporación Favorita | Rossmann | M5 Forecasting |
|---|---|---|---|
| Daily sales per store | PASS | PASS | PASS |
| Daily sales per product/family | PASS – item_nbr | FAIL – store-level only | PASS – item_id |
| At least 1 year of dates | PASS – 2013–2017 | PASS – 2013–2015 | PASS – 2011–2016 |
| Promotion or price column | PASS – onpromotion | PASS – Promo | PASS – sell_price (weekly) |
| At least 10 stores | PASS – 54 | PASS – 1,115 | PASS – 10 |
| Holidays/events | PASS – holidays_events.csv | PASS – StateHoliday, SchoolHoliday | PASS – calendar.csv |
| Country | Ecuador | Germany | USA |
| Number of files | 8 | 4 | 5 |
| Dataset size | 479.88 MB compressed (8 .7z files, Data tab); about 5.83 GB after extraction (from a Kaggle notebook listing, to be confirmed in T4) | 39.85 MB | 450.47 MB |
| Rows / observations | Approximately 125 million training rows | Approximately 1 million training rows | 30,490 item-store series, with daily sales in separate columns |
| Free Colab after subsampling | PASS – subsampling required | PASS | PASS – subsampling recommended |
| Kaggle rules | Subject to competition rules; accept before downloading | Subject to competition rules; accept before downloading | Subject to competition rules; accept before downloading |

## 2. Dataset Details

### Corporación Favorita Grocery Sales Forecasting

Kaggle version checked: **Corporación Favorita Grocery Sales Forecasting**

Link: https://www.kaggle.com/competitions/favorita-grocery-sales-forecasting/data

- Country: Ecuador.
- Stores: 54.
- Products: Approximately 4,100 items and 33 families.
- Date range: January 1, 2013 – August 15, 2017.
- Target: unit_sales.
- Promotion: onpromotion.
- Perishable information: items.csv contains perishable.
- Holidays: holidays_events.csv.
- Main files: train.csv, test.csv, stores.csv, items.csv, transactions.csv, oil.csv, holidays_events.csv, sample_submission.csv.
- Training data: approximately 125 million rows.
- Dataset is large and requires subsampling for free Colab.
- Note: the store count, item and family counts, row count and date range above were not stated on the Kaggle Data tab. They are to be confirmed in T4.

Important limitation: The training data does not contain rows for items with zero recorded sales. Missing records should not automatically be treated as proof of zero demand or out-of-stock status.

Rules: Kaggle competition rules must be accepted. Rule 7A allows use for academic research, education and non-commercial purposes after acceptance. Rule 7B forbids making the data available to anyone who has not accepted the rules. So every teammate must accept the rules with their own Kaggle account, and the data stays in the private team Drive, never in GitHub.

### Rossmann Store Sales

Link: https://www.kaggle.com/competitions/rossmann-store-sales/data

- Country: Germany.
- Stores: 1,115.
- Date range: January 2013 – July 2015.
- Target: Sales.
- Promotion: Promo and Promo2.
- Holidays: StateHoliday and SchoolHoliday.
- Files: train.csv, test.csv, store.csv, sample_submission.csv.
- Total size: 39.85 MB.

Important limitation: Sales are recorded per store and date, without a product identifier. Therefore, it fails the mandatory product-level forecasting requirement.

Rules: Competition rules apply and must be accepted to access the data.

### M5 Forecasting – Accuracy

Link: https://www.kaggle.com/competitions/m5-forecasting-accuracy/data

- Country: USA.
- Stores: 10.
- Products: 3,049.
- Date range: January 2011 – May 2016.
- Target: Daily unit sales.
- Price: sell_price (weekly).
- Holidays/events: calendar.csv.
- Files: calendar.csv, sales_train_validation.csv, sales_train_evaluation.csv, sell_prices.csv, sample_submission.csv.
- Total size: 450.47 MB.

Important limitation: The sales data is stored in a wide format, with a separate column for each day. The calendar and weekly prices must be joined to the sales data.

Rules: Competition rules must be accepted. Historical rules restrict use of competition data to permitted non-commercial purposes.

## 3. Recommendation

### Tie-breaker comparison: Favorita vs M5

Both Corporación Favorita and M5 Forecasting satisfy the mandatory dataset requirements. Applying the tie-breakers in order:

1. **Fewer files to join:** Favorita needs `train.csv`, `items.csv` and `holidays_events.csv` (3 files, because we also want holiday features). M5 needs the sales file, `calendar.csv` and `sell_prices.csv` (3 files). About even, no clear advantage.
2. **Perishable flag:** Favorita provides an explicit `perishable` column in `items.csv`, while M5 does not provide an equivalent flag. Favorita has the advantage.
3. **Explicit promotion column:** Favorita includes `onpromotion` directly in `train.csv`. M5 provides selling prices but no equivalent explicit promotion flag. Favorita has the advantage.

**Final decision:** Select Corporación Favorita as the primary dataset and M5 Forecasting as the runner-up. Favorita is better suited to ReStock AI because it has a perishable flag and an explicit promotion column.

**Recommended dataset: Corporación Favorita Grocery Sales Forecasting.**

Three reasons:

1. It includes perishable products, making it particularly relevant to reducing food waste caused by over-ordering.
2. It provides an explicit daily promotion indicator (`onpromotion`) at the product/store level.
3. It contains real grocery sales for 54 stores, thousands of products, and more than four years of daily history.

It is the closest match to ReStock AI's goal of predicting product demand and recommending appropriate order quantities.

**Runner-up: M5 Forecasting – Accuracy.**

M5 is a strong alternative because it contains daily product-level sales across 10 stores and historical prices. However, prices are weekly, there is no explicit promotion indicator, and multiple files must be joined.

## 4. Final Decision

Choose Corporación Favorita, using a carefully selected subset of stores, products, and dates to keep the project manageable in free Google Colab.

Rossmann is excluded because it does not provide product-level sales.

M5 remains the runner-up.

**Final recommendation: Corporación Favorita Grocery Sales Forecasting.**
