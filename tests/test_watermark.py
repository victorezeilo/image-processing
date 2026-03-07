import sys
import subprocess
from pathlib import Path

import cv2
import numpy as np


def write_test_image(path: Path) -> None:
    img = np.random.randint(0, 256, (200, 300, 3), dtype=np.uint8)
    assert cv2.imwrite(str(path), img)


def run_cli(args: list[str], repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "src.image_processing.main"] + args,
        cwd=str(repo),
        capture_output=True,
        text=True,
    )


def test_watermark_creates_output(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    write_test_image(src)

    cp = run_cli(["watermark", "-s", str(src), "-d", str(dst), "--text", "TEST", "--force"], repo)

    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert dst.exists()


def test_watermark_changes_pixels(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    write_test_image(src)

    cp = run_cli(["watermark", "-s", str(src), "-d", str(dst), "--text", "TEST", "--force"], repo)
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"

    img1 = cv2.imread(str(src))
    img2 = cv2.imread(str(dst))
    assert img1 is not None and img2 is not None

    # Watermark should modify at least some pixels
    assert not np.array_equal(img1, img2)


def test_watermark_requires_text(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    src = tmp_path / "input.png"
    write_test_image(src)

    cp = run_cli(["watermark", "-s", str(src)], repo)
    assert cp.returncode != 0