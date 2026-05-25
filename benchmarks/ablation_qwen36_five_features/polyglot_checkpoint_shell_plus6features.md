# Aider Polyglot: checkpoint + shell-session + 6 features (+ llama-cpp-provider)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, plus the 6 ablation features (write-guard, skill-inject, knowledge-inject, output-parser, quality-monitor, thinking-budget).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

This condition could not be reliably completed due to frequent race condition crashes.

## Analysis

This specific combination triggers checkpoint's race condition far more frequently than any other condition tested. The likely reason is that quality-monitor and/or output-parser cause the agent to trigger retry more aggressively, while the absence of permission-gate and tool-gating means there is no buffering between tool calls. The combination of frequent retry triggering + fast execution pace + no buffering creates the worst-case scenario for checkpoint's race condition.

In contrast:
- all-off (which includes permission-gate and tool-gating) does not crash
- all-on (which includes all extensions) does not crash
- checkpoint + shell-session alone crashes occasionally but is recoverable

**Recommendation:** Fix checkpoint's retry mechanism to wait for pi to finish processing before sending the retry prompt. Until then, this condition cannot be reliably benchmarked.
