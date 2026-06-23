
# Aider Polyglot: All-Off + write-guard

## Setup

Extension setting: all-off (14 extensions) plus write-guard.

Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

- Total: 140

- Pass: 135 (96.4%)

- Fail: 5 (3.6%)

## Failed Exercises

- bowling, camicia, pov, scale-generator, sgf-parsing

## Analysis

Pass rate improved from 91.4% (all-off) to 96.4% (+5.0%) — second largest single-feature improvement after quality-monitor. Matches all-on (96.4%). write-guard is a highly impactful extension.

## Raw Result

```text

benchmarks/results_full_polyglot_alloff_plus_writeguard.json

```

