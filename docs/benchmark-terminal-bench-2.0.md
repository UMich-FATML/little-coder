# little-coder on Terminal-Bench 2.0

This document is the reproduction path for the Terminal-Bench 2.0 leaderboard runs using little-coder through Harbor, with Qwen3.6-35B-A3B served by vLLM's OpenAI-compatible API.

## Result To Reproduce

| | |
|---|---|
| Agent | `little-coder` |
| Dataset | `terminal-bench@2.0` |
| Harness | Harbor |
| Trials | 89 tasks x 5 attempts = 445 trials |
| Published 35B result | 106 / 445 = 23.82 % |
| Model | `Qwen/Qwen3.6-35B-A3B` served by vLLM |
| little-coder model id | `llamacpp/qwen/qwen3.6-35b-a3b` |
| Adapter | `benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent` |
| Concurrency | `--n-concurrent 10` |

The `llamacpp/qwen/qwen3.6-35b-a3b` id is registered in `models.json` as the vLLM-backed Qwen3.6 MoE entry. It still lives under the `llamacpp` provider key so it can reuse the existing OpenAI-compatible local-provider path; point that provider at vLLM with `LLAMACPP_BASE_URL`.

## Setup

Use Pixi for Python-side benchmark dependencies:

```bash
cd /home/yuekai/little-coder

pixi install
pixi run npm ci

export LLAMACPP_API_KEY=noop
export OLLAMA_API_KEY=noop
```

If Harbor is not already in the Pixi environment:

```bash
pixi add python pip nodejs
pixi add --pypi harbor
```

Then point little-coder's local OpenAI-compatible provider at vLLM:

```bash
export LLAMACPP_BASE_URL=http://127.0.0.1:8000/v1
```

Sanity-check the model listing before launching Harbor:

```bash
curl http://127.0.0.1:8000/v1/models
pixi run npm run pi -- --list-models | grep 'qwen3.6-35b-a3b'
```

## Full Leaderboard Run

Run the 89-task TB 2.0 set with 5 attempts per task:

```bash
pixi run harbor run \
  --job-name tb2-leaderboard-k5-vllm-qwen36-moe \
  --dataset terminal-bench@2.0 \
  --agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent \
  --model llamacpp/qwen/qwen3.6-35b-a3b \
  --jobs-dir benchmarks/harbor_runs \
  --n-attempts 5 \
  --n-concurrent 10 \
  --force-build \
  --yes
```

`--force-build` is required on arm64 hosts. The Terminal-Bench 2.0 task metadata points at prebuilt `alexgshaw/<task>:20251031` images, which are currently amd64 images. Forcing a build makes Harbor build each task image locally from its `environment/Dockerfile`, so Docker selects native arm64 base images where available.

Harbor writes the job under:

```text
benchmarks/harbor_runs/tb2-leaderboard-k5-vllm-qwen36-moe/
```

## Monitor Or Resume

Status:

```bash
bash benchmarks/harbor_status.sh tb2-leaderboard-k5-vllm-qwen36-moe
```

Resume an interrupted run:

```bash
pixi run harbor job resume \
  --job-path benchmarks/harbor_runs/tb2-leaderboard-k5-vllm-qwen36-moe
```

Resume uses the saved job config, so an arm64 job must have been created with `--force-build` in the original `harbor run` command.

To retry only selected infrastructure errors before resuming, use Harbor's `--filter-error-type` flag. Do not filter normal failed trials for a leaderboard-comparable result.

## Pilot Run

For a quick end-to-end check before spending the full run:

```bash
pixi run harbor run \
  --job-name tb2-pilot-vllm-qwen36-moe-fix-git \
  --dataset terminal-bench@2.0 \
  --include-task-name fix-git \
  --agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent \
  --model llamacpp/qwen/qwen3.6-35b-a3b \
  --jobs-dir benchmarks/harbor_runs \
  --n-attempts 1 \
  --n-concurrent 1 \
  --force-build \
  --yes
```

## Notes

- Keep one consistent little-coder checkout, prompt, model id, vLLM serving config, and Harbor config across all 445 trials. Mixing partial runs with different prompts or backends is not leaderboard-comparable.
- On arm64, keep `--force-build` enabled for every run so Harbor does not pull the amd64 prebuilt task images.
- The first local build for each task can be slow. Later runs on the same machine should reuse Docker/BuildKit layers unless Docker cache is pruned or the task image inputs change.
- Harbor's default cleanup may remove final trial containers/images, but it does not normally remove Docker's build cache. Use `--no-delete` only for debugging because long runs can consume substantial disk.
- If local builds fail with Docker Hub `429 Too Many Requests`, authenticate with `docker login` or pre-pull common base images such as `python:*`, `ubuntu:*`, and `debian:*` after the rate limit resets.
- Some tasks may still contain architecture-specific assumptions even when their images build on arm64. Treat those as task-level compatibility issues rather than Harbor adapter failures.
- Harbor stores each trial reward at `verifier_result.rewards.reward` in the trial `result.json`; `benchmarks/harbor_status.sh` reads that field.
- The TB 2.0 adapter exposes only `ShellSession`, `ShellSessionCwd`, and `ShellSessionReset` to the agent. File edits inside the task container happen through shell commands proxied to Harbor's environment.
- vLLM's default OpenAI-compatible port is 8000. The `LLAMACPP_BASE_URL` override is what makes the existing little-coder provider talk to that endpoint instead of a llama.cpp server on port 8888.
- Tool calls are required for this adapter. vLLM must be started with `--enable-auto-tool-choice` and a Qwen-compatible `--tool-call-parser`; otherwise the agent may produce plain text instead of callable `ShellSession` requests.
