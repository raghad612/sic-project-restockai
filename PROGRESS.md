# Progress log

Newest first. Each entry: done, decisions, open issues.

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
