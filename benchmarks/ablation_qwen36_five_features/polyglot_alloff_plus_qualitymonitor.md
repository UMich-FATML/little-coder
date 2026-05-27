# Aider Polyglot: All-Off + quality-monitor

## Setup

Extension setting: all-off (14 extensions) plus quality-monitor.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 138 (98.6%)
- Fail: 2 (1.4%)

## Failed Exercises

- camicia, sgf-parsing

## Analysis

Pass rate jumped from 91.4% (all-off) to 98.6% (+7.2%) — the largest single-feature improvement observed. quality-monitor is by far the most impactful of the 6 ablation features. Pass rate even exceeds all-on (96.4%).

Long-runtime anomalies present (react 165.5s, alphametics 108.8s, ledger 96.3s) — quality-monitor enables persistent retry behavior similar to checkpoint/shell-session.

## Raw Result

```text
benchmarks/results_full_polyglot_alloff_plus_qualitymonitor.json
```
