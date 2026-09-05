"""Minimal, read-only Core AI Torch conversion smoke test.

This intentionally validates conversion only; it does not call production APIs,
write RO App data, or optimize the generated graph. Runtime/on-device validation
requires an Apple Silicon environment with the Core AI runtime available.
"""

from __future__ import annotations

import platform
import sys


def main() -> int:
    if sys.version_info < (3, 11):
        print("REVIEW_REQUIRED: Core AI Torch requires Python >= 3.11")
        return 2
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        print("REVIEW_REQUIRED: Core AI target environment is macOS arm64")
        return 2

    import torch
    import coreai
    from coreai_torch import TorchConverter, get_decomp_table

    class SmokeModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.linear = torch.nn.Linear(8, 4)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.linear(x)

    model = SmokeModel().eval()
    sample = (torch.randn(1, 8),)
    exported = torch.export.export(model, args=sample)
    exported = exported.run_decompositions(get_decomp_table())
    program = TorchConverter().add_exported_program(exported).to_coreai()

    print(f"OK: coreai={coreai.__version__}")
    print(f"OK: torch={torch.__version__}")
    print(f"OK: converted={type(program).__name__}")
    print("NOTE: optimize()/on-device runtime were not exercised by this smoke test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
