# The manual RPC step in the ablation workflow is vestigial

`results/scripts/run_ablation_interactive.sh` asks the operator to restart
`little-coder --model <MODEL> --mode rpc` in a separate terminal before each
coalition. **That process is never used by the benchmark.** (Verified
2026-07-06 while automating the gemma 11-player ablation.)

## Why

1. **The benchmark spawns its own RPC per exercise.**
   `benchmarks/aider_polyglot.py::_run_exercise` constructs a fresh
   `PiRpc(...)` for every exercise (`aider_polyglot.py` ~line 161).
   `PiRpc.__init__` (`benchmarks/rpc_client.py` ~line 104) launches
   `<repo>/node_modules/.bin/pi --mode rpc --no-session --model <model>`
   as a subprocess and speaks JSONL over its stdin/stdout. There is no
   socket, port, or shared session — nothing connects to an externally
   started RPC process.

2. **Extension toggling is picked up from disk at each spawn.**
   `rpc_client._extension_paths()` enumerates `<repo>/.pi/extensions/*/index.ts`
   at `PiRpc` construction time and passes each via `-e <path>`. So deleting
   player directories from `.pi/extensions` (the ablation's coalition toggle)
   takes effect on the very next exercise's subprocess — no restart of any
   long-lived process is required.

3. Confirmed empirically: `benchmarks/run_ablation_auto.sh` runs coalitions
   with `START_RPC=0` (no external RPC at all) and the benchmark behaves
   identically.

## Practical consequences

- The "restart RPC, press ENTER" step can be skipped entirely; the
  non-interactive driver `benchmarks/run_ablation_auto.sh` does so.
- An externally started RPC only wastes RAM (it idles with the extension
  set that happened to be on disk when it launched — which may not even
  match the coalition being run, another reason not to trust it).
- What *does* need cleanup between coalitions is leaked per-exercise child
  processes (chromium/playwright from the browser extension, tmux from
  shell-session) — the auto driver handles this.
