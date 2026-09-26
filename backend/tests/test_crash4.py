import json
import subprocess
import sys
import os
from pathlib import Path
ORPHEUS_DIR = Path("backend").resolve() / "orpheusdl"
download_dir = Path("backend").resolve() / "downloads_test4"
download_dir.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
result = subprocess.run(
    [sys.executable, "orpheus.py", "https://tidal.com/browse/album/189843871", "-o", str(download_dir.absolute())],
    cwd=str(ORPHEUS_DIR),
    capture_output=True,
    text=True,
    env=env,
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("RETURN_CODE:", result.returncode)
