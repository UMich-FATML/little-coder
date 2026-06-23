# Aider Polyglot: checkpoint + shell-session + benchmark-profiles + turn-cap (+ llama-cpp-provider)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, benchmark-profiles, turn-cap.
Environment: `LITTLE_CODER_BENCHMARK=terminal_bench` to activate max_turns=40 from settings.json.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 132 (94.3%)
- Fail: 8 (5.7%)

## Failed Exercises

- bowling, camicia, connect, forth, pov, react, rest-api, sgf-parsing, zipper

## Analysis

No extreme long-runtime anomalies observed (all exercises under 90s). This confirms that `benchmark-profiles` + `turn-cap` + `LITTLE_CODER_BENCHMARK=terminal_bench` is sufficient to suppress long-runtime behavior.

**This directly answers Yuekai's original question:** In Terminal-Bench, `benchmark-profiles` reads `max_turns=40` from settings.json's `benchmark_overrides.terminal_bench` and passes it to `turn-cap`, which enforces a hard stop at 40 turns. This is why all-off has very few AgentTimeoutErrors while zero-extensions has 436/445.

The earlier turn-cap-only test failed because without `benchmark-profiles`, turn-cap had no max_turns value to enforce.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_benchprofiles_turncap.json
```
