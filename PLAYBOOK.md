# ReStock AI - Project Playbook

Team Forecast Crew, Samsung Innovation Campus (SIC) AI capstone, 2026.
Version 1 (Nov 10, 2026). This is a living document: the team always follows the latest version in the repo.

If you are new and confused, read sections 1, 3 and 7 first, then do your first PR (section 7).

---

## 1. One-page overview

**Problem.** Shops lose money in two ways: ordering too much (waste) or too little (stockouts).

**User.** A store or purchasing manager who decides what to order.

**Solution.** ReStock AI predicts a demand range (low, expected, high) for each product and recommends tomorrow's order quantity, with a plain-language explanation.

**What we build first.** Lock a public Kaggle retail dataset, then: data cleaning, EDA, features, a time-based split, a naive baseline, gradient boosting (LightGBM) with quantile forecasts, and one simple deep learning model. We compare them honestly.

**What we do later.** Only after the official guidelines arrive and the ML/DL baseline works: the order-decision layer, explanations, and a small app (see section 10).

**Instructor guidance (Mr. Mrad).** Data first (EDA, preprocessing, feature engineering), then ML, then DL.

---

## 2. Big-picture diagram

```text
Kaggle dataset (subsample: 10-15 stores, about 2 years)
        |
        v
Cleaning (fix dates, remove duplicates, quarantine impossible rows)
        |
        v
Features (lags 7/14/28 days, rolling means, calendar, promotion, holiday)
        |
        v
Time split (train on the past, test on the future, never random)
        |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
Naive baseline         LightGBM quantiles       Simple DL model
(last week's sales)    (q10, q50, q90)          (small MLP or LSTM)
        |                      |                      |
        +----------------------+----------------------+
        |
        v
Walk-forward backtest (last 3 months) and metrics
        |
        v
Honest comparison: baseline vs ML vs DL
```

---

## 3. Timeline and gates

All dates are 2026. Treat every date after Nov 24 as provisional until the official guidelines arrive.

| Phase / event | Dates | What happens | Gate |
|---|---|---|---|
| Phase 1: Data and baseline | Nov 6 - Nov 15 | Lock dataset, subsample, EDA, cleaning, features, time split, naive baseline | Nov 15: the naive baseline runs end to end |
| Phase 2: ML | Nov 16 - Nov 24 | LightGBM, then quantile forecasts, then walk-forward backtest | Nov 24: ML beats the baseline on the time split, or we know why not |
| Capstone intro session | Nov 25 | Official introduction | None |
| Phase 3: DL and comparison | Nov 25 - Dec 1 | One simple DL model with a fixed time budget, honest ML vs DL comparison | Dec 1: first Action Plan draft due |
| Mentoring session 1 | Dec 2 - Dec 4 | Feedback (exact slot to be confirmed) | Dec 5: final Action Plan due |
| Product layer (provisional) | Dec 6 - Dec 8 | Decision layer, template explanations, minimal app. To be confirmed once the official guidelines arrive | Dec 8: feature freeze |
| Deliverables (provisional) | Dec 9 - Dec 14 | Report, slides, README, code reference, rehearsals. Mentoring session 3 around Dec 13-15 | None |
| Final deadline | Dec 15 | Final deadline. Pitch date: to be confirmed | Dec 15 |

Rules:
- If a milestone slips by more than 2 days, tell Raghad immediately. We decide together what to cut.
- Nothing new is added after the Dec 8 feature freeze unless something else is cut.
- The Action Plan (first draft due Dec 1, final due Dec 5) is a course deliverable without a task card yet. Raghad creates its Issue after the Nov 25 intro session, when the format is known.

---

## 4. Phase-by-phase explanation

### Phase 1: Data and baseline (Nov 6 - Nov 15)

**Aim.** Lock the dataset, prepare clean data and features, and get a naive baseline running end to end.

**Why.** Everything else depends on clean data and a number to beat. This is also the instructor's required order.

**Outputs.** The subsample and cleaned file in `restockai-work/interim`, feature files in `restockai-work/processed`, two EDA notebooks, `src/clean.py`, `src/features.py`, `src/metrics.py`, and the baseline error saved in `notes/results.md`.

**Pitfalls and how we avoid them.**
- Data leakage: using information from the future to predict the past. We build every lag and rolling feature from past rows only.
- Random split: splitting rows randomly mixes future and past. We always split by date.

### Phase 2: Machine learning (Nov 16 - Nov 24)

**Aim.** Train one global LightGBM model (one model for all stores and items, with store, item family, promotion and holiday as features), then quantile models that give a low, middle and high forecast.

**Why.** Gradient boosting is usually very strong on tabular retail data and cheap to train on free Colab.

**Outputs.** Training scripts in `src/models/`, a clean quantile table (store, item, date, q10, q50, q90), and a 3-month walk-forward backtest compared with the baseline in `notes/results.md`.

**Pitfalls and how we avoid them.**
- Quantile crossing: the low forecast ends up higher than the middle one (q10 > q50). We check for it and fix it by sorting the three values per row.
- Cold start: a new store or item has no history. The global model handles it through store and item-family features, so we do not retrain per store.
- Overfitting: the model memorises the training period. We validate only on later dates and use early stopping.

### Phase 3: Deep learning and comparison (Nov 25 - Dec 1)

**Aim.** Train one small MLP or LSTM within a fixed time budget and compare it with the baseline and LightGBM using the same split and metrics.

**Why.** The course asks us to cover deep learning. A fair comparison counts, even if deep learning loses.

**Outputs.** One DL training script, and a comparison table with an honest conclusion in `notes/results.md`.

**Pitfalls and how we avoid them.**
- Deep learning often loses to gradient boosting on tabular data. We set a time budget first and report the result honestly. LightGBM stays the main model if DL is slower or worse.

---

## 5. Task cards

Each card is also a GitHub Issue. **If a card here differs from its Issue, the Issue wins.** Every task is 1-2 days. File names below are examples that the task team can adjust.

Proposed metrics (to be confirmed in T9): MAE (average absolute error), WAPE (total absolute error divided by total actual sales), and pinball loss (the error score for quantile forecasts).

### T1: Repo, board and skeleton (done)
- **Goal:** Set up the GitHub repo, folder layout and board.
- **Why:** One shared workspace from day one.
- **Done when:** The repo is live, the board "ReStock AI board" exists, the skeleton folders exist.

### T2: Practice pull request
- **Goal:** Every teammate completes one small PR.
- **Why:** Everyone must be able to branch, push and open a PR before the real tasks start.
- **Steps:**
  1. Follow "Your first pull request" in section 7 (Option A is the easiest).
  2. Add a file `team/yourfirstname.md` with a few lines about you.
  3. Open the PR with `Closes #N` in the description (N = your Issue number).
  4. Comment "PR ready" on your Issue.
- **Done when:** Each teammate has one merged PR that adds their own file in `team/`.
- **If stuck:** Re-read section 7, then message Raghad with a screenshot.

### T3: Dataset check and lock
- **Goal:** Choose the single dataset the project uses, and name a runner-up.
- **Why:** Everything after this task waits for it.
- **Steps:**
  1. For each candidate (Corporacion Favorita, Rossmann, M5 Forecasting), check these rules, all must pass: daily sales per store and per product or family; at least 1 year of dates; a promotion or price column; at least 10 stores; small enough for free Colab after subsampling; Kaggle rules allow use. Holidays are not required (they can be generated).
  2. If more than one passes, use these tie-breakers in order: fewer files to join, perishable flag or grocery items, explicit promotion column, more public Kaggle notebooks, smaller size.
  3. Write the pass/fail table in `notes/dataset-check.md`.
  4. Name the chosen dataset and one runner-up.
- **Done when:** `notes/dataset-check.md` has a pass/fail table for each candidate, one chosen dataset and one runner-up; the PR is reviewed and merged.
- **If stuck:** Read the dataset's Kaggle page for its columns. If a teammate finds another dataset, tell Raghad before checking it.

### T4: Subsample and save to Drive
- **Goal:** Make a small version of the locked dataset that runs on free Colab.
- **Why:** The full data may crash Colab and slows every experiment.
- **Steps:**
  1. Before you start: Raghad downloads the locked dataset from Kaggle into `restockai-raw` (only Raghad writes there) and tells the pair.
  2. Write a script in `src/` (for example `src/subsample.py`) that keeps about 10-15 stores and about 2 years of dates.
  3. Save the result in `restockai-work/interim` with a versioned name (for example `sales_sample_v1.parquet`). Use the paths in `src/config.py`.
  4. Add one row to `DATA.md`.
- **Done when:** The subsample is saved in `restockai-work/interim` with a versioned name, created by a script in `src/`, and logged in `DATA.md`.
- **If stuck:** Check that Drive is mounted in Colab and that you can see `restockai-raw`.

### T5: EDA of sales
- **Goal:** Understand how sales behave over time.
- **Why:** The patterns we find decide which features we build.
- **Steps:**
  1. Load the subsample in a notebook (one owner per notebook).
  2. Plot total sales over time and the weekly pattern.
  3. Compute the share of zero-sales days.
  4. List the top and bottom items.
  5. Write 5 findings in plain words.
- **Done when:** The EDA notebook shows the sales trend, weekly pattern, zero-sales share, top and bottom items, plus 5 written findings.
- **If stuck:** Start with `groupby('date')['sales'].sum()` and plot it.

### T6: EDA of promotions and holidays
- **Goal:** Measure how promotions and holidays change sales.
- **Why:** It tells us whether these columns are worth using as features.
- **Steps:**
  1. Compare average sales on promotion days vs non-promotion days.
  2. Compare holidays vs regular days.
  3. Check whether the effect differs by product family.
  4. Write 5 findings.
- **Done when:** The EDA notebook shows how promotions and holidays change sales, plus 5 written findings.
- **If stuck:** Join the holiday table to sales on the date column.

### T7: Cleaning step
- **Goal:** Build one small, repeatable cleaning step.
- **Why:** Bad rows silently ruin features and forecasts.
- **Steps:**
  1. Create `src/clean.py`.
  2. Fix date formats and remove duplicate store-item-date rows.
  3. Move impossible rows (for example negative sales) into a separate quarantine file instead of deleting them.
  4. Print and log row counts before and after.
  5. Save the cleaned file, versioned, in `restockai-work/interim`, and log it in `DATA.md`.
- **Done when:** `src/clean.py` fixes dates, removes duplicates, quarantines impossible rows and logs row counts before and after; the cleaned file is versioned and in `DATA.md`.
- **If stuck:** Use a boolean filter such as `df[df['sales'] < 0]` to find the rows to quarantine.

### T8: Features v1
- **Goal:** Build the input columns for the models.
- **Why:** Past sales are the strongest predictor of future sales.
- **Steps:**
  1. Create `src/features.py`.
  2. Add lag features (for example 7, 14 and 28 days).
  3. Add rolling means over past windows.
  4. Add calendar features (day of week, month), plus promotion and holiday flags.
  5. Save the feature table, versioned, in `restockai-work/processed`, and log it in `DATA.md`.
  6. The first rows of each series have empty lags because there is no history yet. Drop them from training.
- **Pitfall:** Leakage. A rolling mean must skip today's row, otherwise today's sales leak into the feature.
- **Done when:** `src/features.py` builds lags, rolling means and calendar features using only past data; the feature file is versioned and in `DATA.md`.
- **If stuck:** Use this pattern (column names depend on the chosen dataset):

```python
# why: shift(1) first, so today's sales are never inside the average
df["roll7"] = (
    df.groupby(["store", "item"])["sales"]
      .transform(lambda s: s.shift(1).rolling(7).mean())
)
```

### T9: Time split, metric and naive baseline (phase close)
- **Goal:** Fix the evaluation rules and get the first real number.
- **Why:** Every later model must beat this number.
- **Steps:**
  1. Write the metric functions in `src/metrics.py`.
  2. Choose fixed cutoff dates for train and test (never random). Keep the last 3 months of data as the test period, because T12 uses them for the walk-forward backtest.
  3. Build the naive baseline: tomorrow's forecast = sales 7 days earlier.
  4. Save the real error number and how it was computed in `notes/results.md`.
  5. Do the phase-close steps (section 7).
- **Done when:** The time split uses fixed dates, the metrics are in `src/metrics.py`, the naive baseline runs end to end, and its real error is saved in `notes/results.md`.
- **If stuck:** Check that the baseline compares day t with day t-7 for the same store and item.

### T10: LightGBM
- **Goal:** Train one global LightGBM model for point forecasts.
- **Why:** This is our main candidate model.
- **Steps:**
  1. Create a training script in `src/models/`.
  2. Load the T8 feature table and train on the training block only.
  3. Predict the later block and compute the same metrics as T9.
  4. Compare with the baseline.
- **Pitfall:** Leakage and random splits. Never let the model see rows after the cutoff date.
- **Done when:** LightGBM trains on the training block, is evaluated on the later block with the same metrics, and its error is compared with the baseline.
- **If stuck:** Start with default parameters. Tuning comes later.

### T11: Quantile models
- **Goal:** Produce a low, middle and high forecast.
- **Why:** A range lets a manager balance waste against stockouts.
- **Steps:**
  1. Train three LightGBM models with the quantile objective (alpha 0.1, 0.5, 0.9).
  2. Build a table with columns store, item, date, q10, q50, q90.
  3. Count rows where the order is wrong (q10 > q50 or q50 > q90).
  4. Fix them by sorting the three values per row, and report the count.
- **Pitfall:** Quantile crossing.
- **Done when:** The table is clean, and the number of crossings is checked and fixed.
- **If stuck:** `np.sort(df[["q10","q50","q90"]].values, axis=1)` puts each row in order.

### T12: Walk-forward backtest and comparison (phase close)
- **Goal:** Test the models over several future blocks, not just one.
- **Why:** One test block can be lucky or unlucky.
- **Steps:**
  1. Over the last 3 months, repeat: train on the past, predict the next block, move forward.
  2. Run the baseline and the ML models in the same loop.
  3. Average the metrics and save a comparison table in `notes/results.md`.
  4. Do the phase-close steps.
- **Done when:** A 3-month walk-forward backtest is run for baseline and ML, with the comparison table saved in `notes/results.md`.
- **If stuck:** Start with 3 monthly folds before trying weekly ones.

### T13: Deep learning model with a time budget
- **Goal:** Train one small MLP or LSTM within a fixed time.
- **Why:** The course asks for DL, and we must compare it fairly.
- **Steps:**
  1. Decide the time budget first (for example 30 minutes; the team sets it).
  2. Build a small MLP or LSTM in PyTorch or Keras.
  3. Use the same split and features as the ML models.
  4. Evaluate with the same metrics.
- **Pitfall:** Overfitting and wasted time. Stop at the budget and report what you have.
- **Done when:** One small MLP or LSTM is trained within the fixed budget, on the same split and metrics as ML.
- **If stuck:** If an LSTM is too slow, use a plain MLP on the T8 features.

### T14: ML vs DL comparison (phase close)
- **Goal:** Compare baseline, LightGBM and DL honestly.
- **Why:** This is the main result of the technical work.
- **Steps:**
  1. Collect the real numbers from `notes/results.md`.
  2. Build one comparison table (error, training time, complexity).
  3. Write a short honest conclusion. A fair loss for DL still counts.
  4. Do the phase-close steps.
- **Done when:** The comparison table and written conclusion are in `notes/results.md`; phase-close steps are done.
- **If stuck:** Describe trade-offs: accuracy vs speed vs complexity.

---

## 6. How tasks are assigned

- Raghad assigns each task by availability around partial exams and by learning goals.
- Work is done in pairs that rotate between phases, so everyone touches data, ML and DL.
- The owner of a task is the assignee on its GitHub Issue. The Issue is the source of truth; if a task card here differs from its Issue, the Issue wins.
- Every PR needs one approval from someone who is not the author. Raghad reviews unless she says otherwise. Raghad may merge her own docs-only PR with the bypass option when no reviewer is available, never on teammates' PRs.

---

## 7. GitHub guide and rules

CONTRIBUTING.md is the rule book. If this section ever differs from it, CONTRIBUTING.md wins.

### Words you need
- **Repository (repo):** the project folder on GitHub, with its full history.
- **Branch:** your own safe copy of the project where you make changes.
- **Commit:** a saved set of changes with a short message.
- **Pull request (PR):** a request to merge your branch into `main`, so someone can check it first.
- **Issue:** one task card on GitHub, with Goal, Steps and "Done when".
- **Board:** the "ReStock AI board" with columns To do, In progress, Review, Done.

### Rules
- `main` is protected: no direct pushes. Every change, including docs, goes through a branch and a PR.
- Branch name: `firstname/T5-short-name` (example: `zahraa/T5-eda-sales`). Your first name in lowercase, then the task number as written in the Issue title.
- One short branch and one PR per task.
- Every PR needs one approval from someone who is not the author. Raghad reviews unless she says otherwise.
- The PR description says `Closes #N` so the Issue closes when the PR is merged.
- The owner moves their own card: In progress when starting, Review when the PR is open. Then comment "PR ready" on the Issue.
- Shared data files: one writer per file, a version in the file name (for example `sales_clean_v1.parquet`), and one row in `DATA.md` (name, folder, owner, script, date).
- Notebooks: one owner per notebook, outputs cleared before commit. Reusable code goes in `src/*.py`.
- Never commit data, models or keys. Never put Drive links in the repo.

### Task life cycle

```text
Issue created -> To do -> In progress -> PR opened -> Review -> Merged -> Done
```

### Your first pull request

**Option A (easiest, no installs, in the browser)**
1. Open the repo on github.com.
2. Click Add file, then Create new file.
3. Name it `team/yourfirstname.md` and write a few lines.
4. Click Commit changes. Choose "Create a new branch for this commit and start a pull request".
5. In the branch-name box, replace the default name with `yourfirstname/T2-practice`.
6. Click Propose changes, then in the description write `Closes #N` (your Issue number) and click Create pull request.
7. Ask one teammate to review. After approval, click Merge pull request, then Delete branch.

**Option B (Git commands; needs Git installed, or a token in Colab)**

```bash
git clone https://github.com/raghad612/sic-project-restockai.git
cd sic-project-restockai
git checkout -b yourfirstname/T2-practice
# create team/yourfirstname.md
git add team/yourfirstname.md
git commit -m "Add team/yourfirstname.md"
git push -u origin yourfirstname/T2-practice
# then open the pull request on github.com
git checkout main && git pull
```

### Closing steps for every task
1. List the files you changed and write a clear commit message.
2. Open the PR with `Closes #N` and ask for one review.
3. Add a row to `DATA.md` if you created a shared data file.
4. Add an entry to `PROGRESS.md` (done, decisions, open issues).
5. After the merge, check that the Issue is closed and the card is in Done. If not, move it yourself.

### Extra steps for phase-close tasks (T9, T12, T14)
1. Update the Status line in `README.md`. Change "How it works" only if the scope changed.
2. Save the real numbers (metrics, comparison table, how they were computed) in `notes/results.md`. Never claim results that were not computed.
3. Check that every shared file from the phase is logged in `DATA.md`.
4. Close finished Issues and create the next phase's Issues.
5. Update `CONTRIBUTING.md` only if a team rule changed.
6. Re-check the phase gate and say whether it passed.

---

## 8. Repo and Drive structure

### GitHub repo

```text
sic-project-restockai/
  README.md          project description only
  PLAYBOOK.md        this file
  CONTRIBUTING.md    team rules
  PROGRESS.md        log of what is done
  DATA.md            log of shared data files
  TEAM.md            team list
  notes/             dataset-check.md, results.md
  team/              one practice file per teammate
  src/               reusable code: config.py, clean.py, features.py, metrics.py, models/
  notebooks/         exploration only, outputs cleared
```

### Shared Google Drive

```text
restockai-raw/       original Kaggle files (read-only for the team; only Raghad writes)
restockai-work/
  interim/           subsample (T4) and cleaned data (T7)
  processed/         feature tables and train/test splits (T8, T9)
  outputs/           predictions, metrics and trained models
```

Paths live in `src/config.py`. Never hardcode personal paths.

---

## 9. Team routine

- Weekly 20-minute sync: what is done, what is next, what is blocked.
- A short status message to the team after each sync.
- A card that stays In progress for more than 3 days gets flagged, and we help.
- Raghad resends GitHub invites that are older than 5 days.
- Keep every Issue current: assignee set, card in the right column, comments answered.

---

## 10. Parked items, and when the guidelines arrive

### Parked (no tasks yet)
Later, only after the official guidelines arrive and the ML/DL baseline works:
- Order-decision layer: turn quantiles into order quantities (perishables use a lower quantile).
- Waste and stockout simulation.
- SHAP explainability.
- Demand-shock detection.
- Explanation layer: templates first, then an optional small LLM, with a check that every number matches the model output.
- FastAPI and Streamlit app (Tomorrow's Orders, What-If).
- Report and slides.
- If time runs short, the LLM explanation upgrade is cut first.

Out of scope unless everything else works: Slack alerts, slow-mover detection, an ask-your-data chatbot, real-time ingestion.

### When the guidelines arrive
This Playbook is a living document. The plan, milestones, task cards and rules can all change.
1. Raghad shares the guidelines with the team.
2. Compare them with this Playbook, the README, the milestones and the board, and list the gaps.
3. Decide what to add, change or cut (nothing new after the feature freeze unless something else is cut).
4. Raghad updates the Playbook, edits the Issues, updates `CONTRIBUTING.md` only if a rule changed, and sends the team one short message.

The team always follows the latest version, and any change is announced by Raghad.

---

## 11. Known limitations

- The data comes from another country. The method transfers, but the numbers do not describe Lebanese shops.
- Sales is not demand: an empty shelf records zero sales, so true demand can be higher than what we see.
- Any later waste or stockout numbers come from a simulation under stated assumptions, not from real shops.

---

## 12. Glossary

- **EDA (exploratory data analysis):** looking at the data with summaries and plots to understand it.
- **Feature:** an input column the model uses.
- **Lag:** the value from an earlier day, for example sales 7 days ago.
- **Leakage:** accidentally using future information, which makes results look better than they are.
- **Time split:** train on earlier dates, test on later dates.
- **Baseline:** a very simple model we must beat (here: last week's sales).
- **Quantile:** a point in the forecast range, for example q10 is the low forecast and q90 the high one.
- **Walk-forward backtest:** train on the past, test on the next block, move forward, repeat.
- **PR (pull request):** a request to merge your branch after someone checks it.
- **Branch:** your own safe copy of the project.
- **Issue:** one task card on GitHub.

---

## 13. FAQ

**What do I do first?**
Do T2: add your file in `team/` through a pull request (section 7, Option A).

**What if I break something?**
You cannot break `main`. Direct pushes are blocked and your work lives on your own branch. Message Raghad with a screenshot.

**Where do data files go?**
In the shared Drive folders, never in GitHub. Paths are in `src/config.py`.

**Can I experiment in a notebook?**
Yes. But reusable code (cleaning, metrics, models) must move into `src/*.py`.

**What if my task is blocked by another task?**
Comment on your Issue and tell Raghad. She can re-pair or re-order tasks.

**What if LightGBM and deep learning disagree?**
We report both honestly in `notes/results.md`. If LightGBM is better or faster, it stays the main model.

**Who reviews my PR?**
Every PR needs one approval from someone who is not the author. Raghad reviews unless she says otherwise. Raghad may merge her own docs-only PR with the bypass option when no reviewer is available, never on teammates' PRs.

---

## 14. Version history

| Version | Date | What changed |
|---|---|---|
| v1 | Nov 10, 2026 | First release |
