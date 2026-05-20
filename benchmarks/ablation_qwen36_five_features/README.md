# Qwen3.6 Terminal-Bench 2.0 Scaffold Ablation

This folder records the harness setup for comparing three extension settings:

1. `all_on`: full little-coder extension set
2. `all_off`: full extension set minus the five target adaptations:
   - write-guard
   - skill-inject + knowledge-inject
   - thinking-budget
   - output-parser
   - quality-monitor
3. `zero_extensions`: empty `.pi/extensions/`

Model:
- `umich/qwen/qwen3.6-35b-a3b`

Dataset:
- `terminal-bench@2.0`

Agent:
- `benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent`

Timeouts:
- Harbor default timeout settings are used.
- Timeouts count as errors.

Raw `benchmarks/harbor_runs` artifacts are not committed because verifier logs may contain secrets.
