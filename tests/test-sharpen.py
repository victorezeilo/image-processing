import cv2
import numpy as np
from pathlib import Path
import subprocess
import sys


def write_text_image(path: Path):
    img = np.zeros((200, 600, 3), dtype=np.uint8)
    cv2.putText(img, "TEST TEXT", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    assert cv2.imwrite(str(path), img)


def sharpness_score(gray: np.ndarray) -> float:
    # Higher = sharper
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def run_cli(args, cwd: Path):
    # run the same way your tests run other commands: python main.py ...
    main_py = cwd / "src" / "image_processing" / "main.py"
    cmd = [sys.executable, str(main_py), *args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))


def test_sharpen_increases_sharpness(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    src = tmp_path / "input.png"
    write_text_image(src)

    # blur first to create a "needs sharpening" input
    img = cv2.imread(str(src))
    blurred = cv2.GaussianBlur(img, (9, 9), 0)
    assert cv2.imwrite(str(src), blurred)

    dst = tmp_path / "out.png"
    cp = run_cli(["sharpen", "-s", str(src), "-d", str(dst), "--level", "1.5", "--radius", "3", "--force"], repo)
    assert cp.returncode == 0, f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert dst.exists()

    before = cv2.imread(str(src))
    after = cv2.imread(str(dst))
    b = sharpness_score(cv2.cvtColor(before, cv2.COLOR_BGR2GRAY))
    a = sharpness_score(cv2.cvtColor(after, cv2.COLOR_BGR2GRAY))

    assert a > b * 1.2, f"Expected sharper output. Before={b}, After={a}"


def test_sharpen_invalid_level_fails(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]

    src = tmp_path / "input.png"
    write_text_image(src)

    dst = tmp_path / "out.png"
    cp = run_cli(["sharpen", "-s", str(src), "-d", str(dst), "--level", "-1"], repo)
    assert cp.returncode != 0