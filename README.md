# ReStock AI

Demand forecasting and order recommendations for shops. Team Forecast Crew, Samsung Innovation Campus AI capstone (2026).

Problem: shops lose money by over-ordering (waste) or under-ordering (stockouts).
Idea: predict demand ranges per product and recommend tomorrow's order quantities.

## Status
Phase 1: data (EDA, cleaning, features, time split, naive baseline). See PROGRESS.md for the latest.

## Team
Forecast Crew: Raghad (leader) and 5 teammates (names added by each member in TEAM.md).

## Repo layout
- src/        reusable code (.py files)
- notebooks/  exploration only, one owner per notebook, outputs cleared before commit
- data/       local only, never committed (data lives in Google Drive)
- PROGRESS.md running log: done, decisions, open issues

## How we work
- main is protected: no direct pushes
- one task = one Issue = one short branch (member/task) = one pull request
- one teammate reviews each pull request, then it is merged
- work runs on Google Colab with files in Google Drive

## Data
Dataset to be locked in task T3 (candidate: Corporacion Favorita, Kaggle). Not stored in this repo.
