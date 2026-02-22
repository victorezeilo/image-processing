import cv2
import numpy as np
from pathlib import Path
import subprocess
import sys


def write_colourful_image(path: Path):
    # Create a simple colourful image (not grayscale) so hue shift definitely changes pixels
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    img[:, :100] = (0, 0, 255)     # red block (BGR)
    img[:, 100:200] = (0, 255, 0)  # green block
    img[:, 200:] = (255, 0, 0)     # blue block
    assert cv2.imwrite(str(path), img)


def run_cli(args, cwd: Path):
    main_py = cwd / "src" / "image_processing" / "main.py"
    cmd = [sys.executable, str(main_py), *args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))


def test_recolour_changes_pixels(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    src = tmp_path / "input.png"
    dst = tmp_path / "out.png"
    write_colourful_image(src)

    cp = run_cli(["recolour", "-s", str(src), "-d", str(dst), "--hue-shift", "120", "--sat-mult", "1.2", "--force"], repo)
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert dst.exists()

    before = cv2.imread(str(src))
    after = cv2.imread(str(dst))
    assert before is not None and after is not None

    # Visible change: mean absolute pixel diff should be significant
    diff = np.mean(np.abs(after.astype(np.int16) - before.astype(np.int16)))
    assert diff > 5.0, f"Expected visible recolour change, diff={diff}"


def test_recolour_invalid_hue_shift_fails(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    src = tmp_path / "input.png"
    dst = tmp_path / "out.png"
    write_colourful_image(src)

    cp = run_cli(["recolour", "-s", str(src), "-d", str(dst), "--hue-shift", "999"], repo)
    assert cp.returncode != 0