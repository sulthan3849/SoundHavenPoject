import json
import subprocess
import sys
from pathlib import Path
ORPHEUS_DIR = Path("backend").resolve() / "orpheusdl"
download_dir = Path("backend").resolve() / "downloads_test3"
download_dir.mkdir(parents=True, exist_ok=True)
result = subprocess.run(
    [sys.executable, "orpheus.py", "https://tidal.com/browse/album/189843871", "-o", str(download_dir.absolute())],
    cwd=str(ORPHEUS_DIR),
    capture_output=True,
    text=True,
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
