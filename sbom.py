from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import tomllib


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True
        )
    return result.stdout.strip()


def version_tuple(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in version.split("."))
    
    except ValueError as exc:
        raise RuntimeError(
            f"Unsupported version format: {version!r}; "
            "expected numeric dot-separated components."
            ) from exc


# The pyproject.toml version
def get_project_version(root: Path) -> tuple[int, ...]:
    with (root / "pyproject.toml").open("rb") as file:
        project = tomllib.load(file)["project"]
    
    version = project["version"]
    
    if not isinstance(version, str):
        raise RuntimeError("project.version must be a string.")
    
    return version_tuple(version)


# Highest published GitHub tag
def get_highest_release_version() -> tuple[int, ...]:
    tags = run_git(
        "tag",
        "--list",
        "v[0-9]*",
        "--sort=-version:refname",
        )
    if not tags:
        return (0,)
    
    return version_tuple(tags.splitlines()[0][1:])


def generate_sbom(
    root: Path,
    version: tuple[int, ...]
    ) -> None:
    version_string = ".".join(str(part) for part in version)
    sbom_dir = root / ".sbom"
    sbom_dir.mkdir(exist_ok=True)
    
    target = sbom_dir / f"sbom-finra-py-{version_string}.json"
    
    with tempfile.NamedTemporaryFile(
        dir=sbom_dir,
        suffix=".json",
        delete=False
        ) as file:
        temporary = Path(file.name)
    
    # Run syft to create the SBOM
    try:
        environment = os.environ.copy()
        environment.update({
            "SYFT_FILE_METADATA_SELECTION": "all",
            "SYFT_FILE_METADATA_DIGESTS": "sha256",
            })
        
        subprocess.run(
            [
                "syft",
                f"dir:{root / 'finra'}",
                "--base-path",
                str(root / "finra"),
                "--exclude",
                "**/__pycache__/**",
                "--source-name",
                "finra-py",
                "--source-version",
                version_string,
                "-o",
                f"cyclonedx-json={temporary}",
                ],
            cwd=root,
            env=environment,
            check=True
            )
        
        # Validate created file
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError(f"Syft produced an empty SBOM: {temporary}")
        
        try:
            with temporary.open(encoding="utf-8") as file:
                sbom = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Syft did not produce valid JSON: {temporary}"
                ) from exc
        
        if not isinstance(sbom, dict) or sbom.get("bomFormat") != "CycloneDX":
            raise RuntimeError(
                f"Syft output is not a CycloneDX JSON SBOM: {temporary}"
                )
        
        # Replace into ./sbom directory
        temporary.replace(target)
        
    finally:
        temporary.unlink(missing_ok=True)
    
    # Add to commit
    subprocess.run(
        ["git", "add", str(target)],
        cwd=root,
        check=True
        )
    
    print(f"Generated {target.relative_to(root)}")


def main() -> int:
    root = Path(run_git("rev-parse", "--show-toplevel"))
    
    # Only run SBOM routine if the pyproject.toml version is higher than the
    # highest published GitHub tag
    current_version = get_project_version(root)
    highest_release = get_highest_release_version()
    if current_version <= highest_release:
        return 0
    
    generate_sbom(root, current_version)
    return 0


if __name__ == "__main__": # pragma: no cover
    sys.exit(main())
