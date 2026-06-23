# Aider Polyglot: All-Off minus checkpoint

## Setup

Extension setting: all-off (14 extensions) minus checkpoint (13 extensions total).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 132 (94.3%)
- Fail: 8 (5.7%)

## Failed Exercises

- bowling, camicia, connect, forth, paasio, pov, rest-api, sgf-parsing

## Analysis

This is the key experiment to isolate shell-session's role in preventing timeouts.

**Long-runtime anomalies reappeared:**
- `bowling`: 100.2s
- `connect`: 93.2s

This confirms that **shell-session alone is responsible for the long-runtime behavior** in all-off. When checkpoint is removed but shell-session remains, the agent keeps retrying on difficult problems, causing long runtimes — consistent with what we see in Terminal-Bench as AgentTimeoutError prevention.

**Pass rate increased from 91.4% to 94.3%** when checkpoint was removed, suggesting checkpoint actually hurts performance in the all-off context, possibly because its file-snapshotting overhead interferes with the agent's workflow.

**Conclusion:** In the all-off extension set, shell-session is the extension responsible for preventing AgentTimeoutErrors in Terminal-Bench by keeping the agent actively retrying rather than giving up early.
