# How we work

## Git in one line each
- Repository (repo): the project folder on GitHub.
- Branch: your own copy of the code to work on safely.
- Commit: a saved snapshot with a message.
- Pull request (PR): a request to merge your branch into main, so a teammate can review it first.

## Rules
1. main is protected: nobody pushes directly.
2. One task = one Issue = one branch = one PR.
3. Branch name: yourname/task, for example sara/eda-sales
4. Commit message: short and clear, for example "Add sales EDA notebook".
5. One teammate reviews each PR. Merge only after approval.
6. After a merge, pull main before starting the next task.

## Code
- Reusable code goes in src/ as .py files. Notebooks are for exploration.
- Add a short "why" comment above non-obvious lines.
- Time-based splits only, never random splits.

## Data
- Never commit data, models or keys. Data lives in Google Drive (see DATA.md).
- One writer per shared file. Version files in the name: sales_clean_v1.parquet.
- Log every new shared file in DATA.md.

## Getting stuck
Check the error message and that cells ran in order. Still stuck after 1 hour: message the leader.
