from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
ENTRYPOINT = ROOT_DIR / "main.py"
DATA_FILE = ROOT_DIR / "src" / "territorios_espana.json"
PYINSTALLER_DIR = ROOT_DIR / ".pyinstaller"
CONFIG_DIR = PYINSTALLER_DIR / "config"
WORK_DIR = PYINSTALLER_DIR / "build"
SPEC_DIR = PYINSTALLER_DIR / "spec"
DIST_DIR = ROOT_DIR / "dist"


def build_add_data_arg(source: Path, destination: str) -> str:
    separator = ";" if os.name == "nt" else ":"
    return f"{source}{separator}{destination}"


def main() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYINSTALLER_CONFIG_DIR", str(CONFIG_DIR))

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        "extractor-pdf",
        "--windowed",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(WORK_DIR),
        "--specpath",
        str(SPEC_DIR),
        "--add-data",
        build_add_data_arg(DATA_FILE, "src"),
        str(ENTRYPOINT),
    ]

    subprocess.run(command, cwd=ROOT_DIR, check=True, env=env)


if __name__ == "__main__":
    main()
