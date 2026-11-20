# Progress log

Newest first. Each entry: done, decisions, open issues.

## 2026-11-18

### T5 (PR #26, Closes #21)

**Done:** T5 EDA notebook notebooks/01_eda_sales_fatima.ipynb (Fatima, Zahraa).

Findings:
- Sunday is the busiest weekday (27.6% above the weekly average) and Thursday the quietest (20.4% below); Sunday averages 1.6x Thursday's daily units (train part). Saturday is 15.3% above the weekly average, so weekends (Sat + Sun) are clearly higher.
- BEVERAGES is the top family with 30.2% of all units (train part) (units mix counts and kg; sample, not the real family mix).
- The biggest store sells 3.92x the smallest store.
- Sales are very skewed: median positive unit_sales is 17.0 per row, but the 99.9th percentile is 597.6.
- 20.3% of store-item-days have no row (per calendar day, 639 days in the training part), and there are 0 explicit zeros: a day with no sale is probably a missing row. Store 33 has the most gaps (26.4%), store 39 the fewest (15.9%).
- Share of non-whole rows by family: POULTRY 99.6%, MEATS 98.7%, PRODUCE 60.3%. Probably sold by weight. Overall, 18.2% of positive rows are not whole numbers.
- After the Apr 16 2016 earthquake, units per day were 19.3% higher (Apr 16-30 vs Apr 1-15), matching T4.
- Average daily units were 4.2% lower in Aug16-Apr17 than in Aug15-Apr16, in this sample only.

Decisions: all numbers use the training part only; missing share uses calendar days, same as T4. No data changed.

Open:
- Missing store-item-days (zeros): 20.3% have no row (per calendar day) and there are no explicit zeros. T7 decides whether to fill them with 0 (some may be "not stocked yet", not "no sale"). 4 calendar dates have no sales in any store (likely closures): 2015-12-25, 2016-01-01, 2016-12-25, 2017-01-01.
- Negative values: 45 rows in the training part (sum -3791.24; 55 in the full file, as T4 said), 19 of them BEVERAGES. Possibly returns; one very large negative value (-1806), cause unknown. T7 decides: clip to 0, drop, or keep.
- kg vs counts: POULTRY, MEATS, PRODUCE (and partly PREPARED FOODS, FROZEN FOODS) are sold by weight. Do not mix with count families without care (e.g. in totals or scaling).
- Capped families / DAIRY only 6 items: GROCERY I, BEVERAGES, PRODUCE are at the 62-item cap; DAIRY has 6, LIQUOR,WINE,BEER only 2. Family-level totals reflect the sample, not real store mix.
- April 2016: +19.3% after the earthquake. T8 may need a flag/feature for this period, or T7 may treat it as unusual.
- New: store 33 has 26.4% missing days (highest); sales are heavily skewed (99.9th pct 597.6 vs median 17), so outliers need a rule.

## 2026-11-15

T6 (PR #24) and T6b (PR #25)
Done: T6 EDA of promotions and holidays merged (PR #24, Closes #22), plus T6b follow-up (PR #25, Refs #22): notebooks/02_eda_promo_holidays_raghad.ipynb. Owner: Raghad. Reviewed by Nour.

Findings:
- Promoted share: 12.83% (ranging from 10.57% to 14.78% by store).
- Average unit sales for promoted vs. non-promoted observations: 41.13 vs. 28.02 on the training split (correlation only, not causation).
- Sanity check only (last 3 months, test period): promoted 46.02 vs not promoted 25.93. Not used for any decision or rule.
- Holidays affect relatively few store-days: national 5.32%, local 0.29%, regional 0% (none of the 4 provinces with regional holidays is among our 6 states).
- Holiday vs. regular days (same weekday):
  - Days off: approximately +10% (1.098).
  - Shopping days (Additional/Bridge): approximately +38% (1.384).
  - Local holidays: no clear effect (0.955, based on 21 store-days).
- 45 negative rows = training part only; T4 and T5 count 55 on the full file.
- Local shows 21 store-days here vs 22 in the matching step: store 36 (Libertad) on 2017-04-14 is also a national holiday, so the comparison counts it as national. No store-day was dropped.
- T8 encoding list (11 points) is included in the notebook and updated with two national flags.

Decisions:
- T6 reassigned to Raghad on November 15.
- Reviewer changed from Zahraa to Nour.
- Promotions analysed before holidays.
- Sales-around-holidays chart completed (Navidad and Fundacion de Quito).
- No regional holiday flag in v1.
- The Transfer row represents the actual celebration day.
- Events kept out of holiday flags.
- Holiday flags are built from date, locale, and place so the methodology can transfer to another country.

Open:
- Promotions by product family left for later.
- Rule for no-record days (Dec 25, Jan 1; closure not verified).
- Investigate the 20.6% of store-item-days with no row (T7's job).
- Deduplicate holiday flags before merging (24 matched local rows = 22 distinct store-days).
- Finalize T8 encoding priorities and test "days to/since holiday" on the time split.

## 2026-11-15
Done: T4 sample built by src/subsample.py (Ali) and small tables by src/small_tables.py (Leen), all in restockai-work/interim, paths from src/config.py. sales_sample_v1.parquet: 1,741,225 rows, 2015-08-01 to 2017-07-31, 12 stores, 250 items, 105 perishable (42.0%), 15 families, 0.00% empty onpromotion, 55 negative unit_sales rows, 5.6 MB. stores_v1 (54 rows), items_v1 (4,100 rows), holidays_events_v1 (350 rows). First pass 189 s, whole script 317 s on free Colab. notes/dataset-check.md updated with the measured facts (Leen). DATA.md has the 4 files. PR for #17 opened, reviewer Raghad.
Decisions (confirmed by Raghad): stores = rows in all 24 months (50 of 54 eligible; 52, 18, 22, 25 excluded), then round-robin over types A-E by training-part sales, max 2 per city (5 types, 10 cities). Week = 7-day block from 2015-08-01, 91 full weeks in the training part; "sold" = unit_sales > 0 in any chosen store. Items filled in 3 phases: best perishables to 84, missing families to 8, then best remaining to 250, max 62 per family. Family cap 62 and ranking by unit_sales kept for v1.
Open: Notes for T5 to T8: GROCERY I, BEVERAGES and PRODUCE are at the 62 cap (186 of 250 items); ranking by unit_sales mixes counts and kg, so DAIRY has only 6 items; 20.6% of store-item-days have no row (zero-sales question for T7/T8); Apr 16-30 2016 is +19.3% units per day versus Apr 1-15 (earthquake period, kept).

## 2026-11-14
Done: T4 Issue #17 is on the board for Ali and Leen. T4 paths (ZIP_PATH, LOCAL, SALES_SAMPLE, STORES_OUT, ITEMS_OUT, HOLIDAYS_OUT) added to src/config.py on main (branch raghad/config-t4, merged by Raghad with the bypass). Kaggle rules message sent to Fatima, Nour and Zahraa.
Decisions: Phase 1 gate moved from Nov 15 to Nov 22, because T4 started on Nov 13 and T5 to T9 need about 7-8 working days after it. ML gate moved from Nov 24 to Nov 28. DL phase stays Nov 25 to Dec 1 and overlaps the ML phase (a different pair, comparison after the Nov 28 ML gate). T5, T6 and T7 run in parallel after T4 merges. Dec 1, Dec 5 and Dec 15 are unchanged. T8 and T9 stay single tasks, with no extra prep tasks.
Open: T4 in progress. Kaggle confirmations pending from Fatima, Nour and Zahraa. T5, T6 and T7 Issues and pairs to be written when T4 merges. Official guidelines and pitch date not received.

## 2026-11-13
Done: Raw zip checked: 8 .csv.7z files, train is 474 MB. Unzip method (zipfile + py7zr, Colab local disk) tested and works. Full train.csv measured: 125,497,040 rows, 2013-01-01 to 2017-08-15, 54 stores, 4,036 items, 5.0 GB extracted, 7,795 negative unit_sales rows, 17.3% empty onpromotion. Ali and Leen accepted the Kaggle rules. T4 Issue and teammate message written.
Decisions: T4 window 2015-08-01 to 2017-07-31; about 12 stores; about 250 items chosen on the training part only (up to 2017-04-30); Ali drives with Leen as associate; extracted data stays on Colab local disk, never in Drive or GitHub.
Open: T4 in progress (Ali and Leen); notes/dataset-check.md still has unconfirmed lines (Leen updates them in T4); Phase 1 gate (Nov 15) will slip, new date to decide; T5/T6 pairs not decided; official guidelines not received; pitch date not confirmed.

## 2026-11-12
Done: T3 merged. Favorita locked, M5 runner-up. Raw data downloaded to restockai-raw. PLAYBOOK T4 steps 1-2 updated. Ali.md and nour.md moved into team/.
Decisions: every teammate accepts the Kaggle competition rules on their own account; data stays in the private Drive, never in GitHub. Store, item and row counts are not confirmed yet and will be confirmed in T4. The report says the method transfers, not the numbers.
Open: T4 (subsample) goes to Ali and Leen; unzip method still to verify.

## 2026-11-10
Done: T3 dataset comparison completed. Compared Corporación Favorita, Rossmann, and M5 Forecasting against the project requirements. Created notes/dataset-check.md, committed the changes, and pushed branch nour/T3-dataset-check.
Decisions: Corporación Favorita selected as the recommended dataset; M5 Forecasting selected as the runner-up. Rossmann does not meet the product-level sales requirement.
Open: resolved, see 2026-11-12.

## 2026-11-08
Done: T1 complete. Repo renamed to sic-project-restockai; README, .gitignore, folder skeleton, working rules; board with To do, In progress, Review, Done; main protected with one approval. Leen and Nour joined and merged their practice PRs (#6, #7).
Decisions: code in GitHub, data in shared Drive; one Issue per task; no Issue template file; final deadline Dec 15, feature freeze Dec 8 (provisional); LLM explanation layer is cut first if time runs short.
Open: 3 teammates (invited and accepted) still need their T2 practice cards; T3 dataset check to assign to Leen and Nour; Drive folders to create and share; official guidelines not received.

## 2026-11-07
Done: repo renamed, README and .gitignore written, working rules and shared paths added.
Decisions: code in GitHub, data in shared Google Drive; GitHub Issues and board for tracking.
Open: dataset not locked yet (task T3); teammates not invited yet.

