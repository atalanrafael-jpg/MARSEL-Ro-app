# MARSEL ROAPP — Apple Core AI Torch integration

Status: **CONFIGURED / NOT HARDWARE-VERIFIED**

## Purpose

Add an optional Apple Silicon AI conversion path without changing the MARSEL ROAPP production server dependency set.

`coreai-torch` converts PyTorch `ExportedProgram` graphs to Core AI IR. Apple's current repository documents installation with `pip install coreai-torch` and uses `torch.export` plus `get_decomp_table()` before `TorchConverter.to_coreai()`. The current upstream release is `0.4.2`, and its package metadata requires Python `>=3.11` and `coreai-core==1.0.0b2`.

## Repository integration

- Optional dependency file: `requirements-coreai.txt`
- Conversion smoke test: `scripts/marsel_coreai_torch_smoke.py`
- Production runtime dependencies in `requirements.txt` are intentionally unchanged.

## Install on Apple Silicon

```bash
python3.12 -m venv .venv-coreai
source .venv-coreai/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-coreai.txt
python scripts/marsel_coreai_torch_smoke.py
```

The smoke test is deliberately read-only. It converts a tiny local PyTorch model and does not access RO App, modify production data, or run graph optimization.

## Safety decision

Do **not** add Core AI packages to the production Docker image or server requirements merely to enable the feature. Core AI is an Apple-hardware deployment path, while the canonical MARSEL ROAPP server remains platform-neutral.

Do not treat successful conversion as proof of on-device execution. A separate Apple Silicon runtime test is required for that claim.

The smoke test also intentionally avoids `program.optimize()` until the current upstream optimization behavior is separately validated. Upstream issue reports document correctness problems in optimization for some graphs, so optimization must not be assumed safe for arbitrary MARSEL models.

## Verification state

Current repository inspection confirms:

- canonical repository: `atalanrafael-jpg/MARSEL-Ro-app`;
- canonical branch: `main`;
- Core AI integration is isolated from production dependencies;
- no existing `coreai` integration was found in the repository before this change.

Not yet verified in this environment:

- installation on a real Apple Silicon host;
- Core AI conversion smoke test execution;
- `.aimodel` generation and loading;
- Neural Engine/GPU runtime execution;
- performance or memory characteristics for any MARSEL model.

Therefore this integration remains **NOT HARDWARE-VERIFIED** until those tests produce fresh evidence.

## Upstream references

- Apple `coreai-torch`: https://github.com/apple/coreai-torch
- Apple Core AI documentation: https://apple.github.io/coreai-torch/main/
- Current release: `v0.4.2`
