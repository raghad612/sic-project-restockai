# How we work

## Git in one line each
- Repository (repo): the project folder on GitHub.
- Branch: your own copy of the code to work on safely.
- Commit: a saved snapshot with a message.
- Pull request (PR): a request to merge your branch into main, so a teammate can review it first.

## Rules
1. main is protected: nobody pushes directly.
2. One task = one Issue = one branch = one PR. The PR description says "Closes #N" (the Issue number).
3. Branch name: yourname/task, for example nour/t09-baseline
4. Commit message: short and clear, for example "Add sales EDA notebook".
5. One teammate reviews each PR. You cannot approve your own PR. Merge only after approval. The bypass option is for the leader only, and only on her own PRs.
6. After a merge, pull main before starting the next task.
7. Move your own card on the board: In progress when you start, Review when your PR is open, and comment "PR ready" on the Issue.
8. Every PR adds an entry at the top of PROGRESS.md (done, decisions, open issues).
9. Check README.md and CONTRIBUTING.md. If your task changes a fact or a rule they state, update them in your PR. Otherwise write "README/CONTRIBUTING: no change" in the PR description.

## Code
- Reusable code goes in src/ as .py files. Notebooks are for exploration.
- Notebooks are numbered, have the owner name in the file name, and their outputs are cleared before commit.
- Add a short "why" comment above non-obvious lines.
- Time-based splits only, never random. Use src/split.py and the dates in src/config.py: fit up to 2017-03-05, validation 2017-03-06 to 2017-04-30, test 2017-05-01 to 2017-07-31.
- Tune models on the validation period only. Use the test period once, for the final comparison.
- Rows flagged fill_after_last_train are never used for fitting.
- Score every model with src/metrics.py. Save predictions in the same table format as the baseline (date, store_nbr, item_nbr, prediction, target).

## Data
- Never commit data, models or keys. Data lives in Google Drive (see DATA.md). No Drive links in the repo.
- One writer per shared file. Version files in the name: sales_clean_v1.parquet.
- Log every new shared file in DATA.md.

## Communication
- After your PR is merged, post one line in the team Slack channel.
- The weekly status update also goes to Slack.

## Merge conflicts
In the PR click "Resolve conflicts", keep both versions, delete the marker lines (<<<<<<<, =======, >>>>>>>), click "Mark as resolved", then "Commit merge". If you are not sure, ask the leader.

## Getting stuck
Check the error message and that cells ran in order. Still stuck after 1 hour: message the leader.
