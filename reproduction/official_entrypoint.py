import argparse
import os
import runpy
import sys
import types
from pathlib import Path

import torch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--cores", type=int, required=True)
    parser.add_argument("entrypoint_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if hasattr(os, "sched_getaffinity"):
        available = sorted(os.sched_getaffinity(0))
    else:
        available = list(range(os.cpu_count() or 1))
    selected = available[: args.cores]
    if len(selected) != args.cores:
        raise RuntimeError(f"Requested {args.cores} cores from {len(available)} available")
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, selected)
    torch.set_num_threads(args.cores)
    torch.set_num_interop_threads(1)

    vendor = Path(__file__).resolve().parents[1] / "vendor" / "FFOLayer"
    script = vendor / args.script
    os.chdir(vendor)
    sys.path.insert(0, str(script.parent))
    sys.path.insert(1, str(vendor))
    sys.path.insert(2, str(vendor / "src"))
    sys.path.insert(3, str(vendor.parent / "cvxtorch"))
    try:
        from dqp import dQP as _unused_dqp
    except (ImportError, AttributeError):
        unavailable_dqp = types.ModuleType("dqp")

        def missing_dqp(*_args, **_kwargs):
            raise RuntimeError("The optional dQP baseline is not installed")

        unavailable_dqp.dQP = missing_dqp
        sys.modules["dqp"] = unavailable_dqp
        print("OPTIONAL_BASELINE dQP unavailable; selected method does not use it", flush=True)
    passthrough = args.entrypoint_args
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]
    sys.argv = [str(script), *passthrough]
    effective_cores = (
        len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else args.cores
    )
    print(
        f"OFFICIAL_ENTRYPOINT script={args.script} effective_cores={effective_cores}",
        flush=True,
    )
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
