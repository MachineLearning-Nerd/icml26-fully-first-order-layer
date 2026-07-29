import hashlib
import json
import re
from pathlib import Path


ROOT = Path("candidate_space")
HISTORICAL = ROOT / "historical/judged_ff4102a"
RELEASE = ROOT / "release"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_links(path):
    for target in LINK.findall(path.read_text()):
        if target.startswith(("http://", "https://", "#")):
            continue
        yield (path.parent / target.split("#", 1)[0]).resolve()


def main():
    json.loads((ROOT / "logbook.json").read_text())
    required = [
        ROOT / "README.md",
        ROOT / "pages/current/page.md",
        *[
            ROOT / f"pages/claims/claim_{claim}/page.md"
            for claim in range(1, 7)
        ],
        ROOT / "pages/release/page.md",
        ROOT / "pages/overview/page.md",
    ]
    opened = []
    queue = [ROOT / "README.md"]
    seen = set()
    while queue:
        path = queue.pop(0).resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        opened.append(str(path.relative_to(ROOT.resolve())))
        if path.suffix == ".md":
            for target in markdown_links(path):
                if not target.exists():
                    raise RuntimeError(f"broken candidate link: {target}")
                if target.is_file() and ROOT.resolve() in target.parents:
                    queue.append(target)
    missing = [
        str(path.relative_to(ROOT))
        for path in required
        if path.resolve() not in seen
    ]
    if missing:
        raise RuntimeError(f"canonical traversal missed: {missing}")

    historical_files = sorted(
        path.relative_to(HISTORICAL) for path in HISTORICAL.rglob("*") if path.is_file()
    )
    missing_root_paths = [
        str(relative)
        for relative in historical_files
        if not (ROOT / relative).is_file()
    ]
    if missing_root_paths:
        raise RuntimeError(f"judged paths missing from candidate root: {missing_root_paths}")

    RELEASE.mkdir(exist_ok=True)
    subset = {
        "judged_revision": "ff4102a948f2bee686c6573820b6b1b4ce647869",
        "old_file_count": len(historical_files),
        "old_paths_present_at_candidate_root": True,
        "missing_paths": [],
        "immutable_historical_manifest": {
            str(relative): sha256(HISTORICAL / relative)
            for relative in historical_files
        },
    }
    (RELEASE / "subset_check.json").write_text(
        json.dumps(subset, indent=2, sort_keys=True) + "\n"
    )
    (RELEASE / "traversal.json").write_text(
        json.dumps(
            {
                "entrypoint": "README.md",
                "files_opened": opened,
                "missing_required_pages": [],
                "result": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    text_files = []
    for path in sorted(item for item in ROOT.rglob("*") if item.is_file()):
        if path == RELEASE / "upload_manifest.sha256":
            continue
        try:
            path.read_text()
        except UnicodeDecodeError:
            continue
        text_files.append(path)
    allowlist = [path.relative_to(ROOT).as_posix() for path in text_files]
    allowlist_path = "release/upload_allowlist.txt"
    if allowlist_path not in allowlist:
        allowlist.append(allowlist_path)
        allowlist.sort()
    (RELEASE / "upload_allowlist.txt").write_text("\n".join(allowlist) + "\n")
    manifest = [
        f"{sha256(ROOT / relative)}  {relative}"
        for relative in allowlist
    ]
    (RELEASE / "upload_manifest.sha256").write_text("\n".join(manifest) + "\n")
    print(
        json.dumps(
            {
                "status": "PASS",
                "reachable_files": len(opened),
                "old_paths": len(historical_files),
                "upload_text_paths": len(allowlist),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
