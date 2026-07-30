import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def prefixed_json(lines, prefix):
    return json.loads(next(line[len(prefix) :] for line in lines if line.startswith(prefix)))


def standalone_json(text):
    decoder = json.JSONDecoder()
    values = []
    for offset, character in enumerate(text):
        if character != "{" or (offset and text[offset - 1] != "\n"):
            continue
        try:
            value, _ = decoder.raw_decode(text[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            values.append(value)
    return values


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    args = parser.parse_args()
    destination = Path(args.destination)
    destination.mkdir(parents=True, exist_ok=True)
    text = sys.stdin.read()
    lines = text.splitlines()
    values = standalone_json(text)

    claim_1_2 = next(value for value in values if "claim_1" in value)
    claim_3 = next(value for value in values if "certificate" in value)
    claim_5 = next(value for value in values if "comparisons" in value)
    claim_4 = prefixed_json(lines, "CLAIM4_RAW ")
    claim_6 = prefixed_json(lines, "CLAIM6_RAW ")
    runtime = prefixed_json(lines, "REPRODUCTION_SUMMARY ")

    for name, value in [
        ("claim_1_2.json", claim_1_2),
        ("claim_3.json", claim_3),
        ("claim_4.json", claim_4),
        ("claim_5.json", claim_5),
        ("claim_6.json", claim_6),
        ("runtime.json", runtime),
    ]:
        write_json(destination / name, value)

    raw_directory = destination / "claim_6_raw"
    raw_directory.mkdir(exist_ok=True)
    for row in claim_6["runs"]:
        raw = dict(row)
        for key in ["execution_order_position", "raw_path", "raw_sha256"]:
            raw.pop(key)
        target = raw_directory / Path(row["raw_path"]).name
        write_json(target, raw)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == row["raw_sha256"]

    checker_lines = [
        line
        for line in lines
        if line.startswith(("CLAIM4_CHECK PASS ", "CLAIM6_CHECK PASS "))
    ]
    control_lines = [
        line
        for line in lines
        if line.startswith(("CLAIM4_CHECK FAIL:", "CLAIM6_CHECK FAIL:"))
    ]
    (destination / "checker_output.txt").write_text("\n".join(dict.fromkeys(checker_lines)) + "\n")
    (destination / "negative_control_output.txt").write_text(
        "\n".join(dict.fromkeys(control_lines))
        + "\n"
        + json.dumps(runtime["negative_controls"], sort_keys=True)
        + "\n"
    )

    contracts = destination / "contracts"
    for claim in range(1, 7):
        shutil.copytree(
            Path(".openresearch/artifacts") / f"claim_{claim}",
            contracts / f"claim_{claim}",
            dirs_exist_ok=True,
        )
    code = destination / "code"
    code.mkdir(exist_ok=True)
    for source in sorted(Path("reproduction").glob("*.py")):
        shutil.copy2(source, code / source.name)
    for source in [Path("pyproject.toml"), Path("uv.lock")]:
        shutil.copy2(source, destination / source.name)


if __name__ == "__main__":
    main()
