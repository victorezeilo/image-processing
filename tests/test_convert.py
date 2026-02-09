# Agile/tests/test_convert_us1.py
import os
import sys
import time
import hashlib
import subprocess
from pathlib import Path

import pytest

try:
    import numpy as np
    import cv2
except Exception as e:  # pragma: no cover
    raise RuntimeError("Tests require numpy + opencv-python (cv2). Install them first.") from e


# -----------------------
# Paths / CLI runner
# -----------------------

REPO_ROOT = Path(__file__).resolve().parents[1]  # Agile/
CLI_MAIN = REPO_ROOT / "src" / "image_processing" / "main.py"


def run_convert(args, timeout=10):
    """
    Run: python main.py convert <args>
    Returns CompletedProcess with stdout/stderr as text.
    """
    cmd = [sys.executable, str(CLI_MAIN), "convert"] + list(args)
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# -----------------------
# Helpers
# -----------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_test_png(path: Path, w=128, h=96):
    img = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.putText(img, "TEST", (5, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    ok = cv2.imwrite(str(path), img)
    assert ok, f"Failed to write test image: {path}"


def is_jpeg(path: Path) -> bool:
    b = path.read_bytes()
    return len(b) >= 2 and b[0] == 0xFF and b[1] == 0xD8


def is_png(path: Path) -> bool:
    b = path.read_bytes()
    return len(b) >= 8 and b[:8] == b"\x89PNG\r\n\x1a\n"


# -----------------------
# US1 / DoD-aligned tests (Convert)
# -----------------------

def test_convert_png_to_jpg_success(tmp_path):
    src = tmp_path / "input.png"
    dst = tmp_path / "output.jpg"
    write_test_png(src)

    cp = run_convert(["-s", str(src), "-d", str(dst), "-f", "jpg"])
    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert dst.exists(), "Output file not created"
    assert is_jpeg(dst), "Output is not a valid JPEG signature"
    # "Success" message (your DoD wording). Accept either exact or partial.
    combined = (cp.stdout + "\n" + cp.stderr).lower()
    assert "success" in combined, f"Expected success message, got:\n{combined}"


def test_convert_jpg_to_png_success(tmp_path):
    # Create a jpg via OpenCV first
    src_png = tmp_path / "seed.png"
    src_jpg = tmp_path / "input.jpg"
    out_png = tmp_path / "output.png"

    write_test_png(src_png)
    ok = cv2.imwrite(str(src_jpg), cv2.imread(str(src_png)))
    assert ok, "Failed to write seed jpg"

    cp = run_convert(["-s", str(src_jpg), "-d", str(out_png), "-f", "png"])
    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert out_png.exists()
    assert is_png(out_png), "Output is not a valid PNG signature"


def test_convert_tiff_to_png_success(tmp_path):
    src_png = tmp_path / "seed.png"
    src_tiff = tmp_path / "input.tiff"
    out_png = tmp_path / "output.png"

    write_test_png(src_png)
    img = cv2.imread(str(src_png))
    assert img is not None
    assert cv2.imwrite(str(src_tiff), img), "Failed to write seed tiff (check OpenCV build supports TIFF)"

    cp = run_convert(["-s", str(src_tiff), "-d", str(out_png), "-f", "png"])
    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert out_png.exists()
    assert is_png(out_png)


def test_convert_tiff_to_jpg_success(tmp_path):
    src_png = tmp_path / "seed.png"
    src_tiff = tmp_path / "input.tiff"
    out_jpg = tmp_path / "output.jpg"

    write_test_png(src_png)
    img = cv2.imread(str(src_png))
    assert img is not None

    # write tiff
    assert cv2.imwrite(str(src_tiff), img), "Failed to write TIFF (check OpenCV TIFF support)"

    cp = run_convert(["-s", str(src_tiff), "-d", str(out_jpg), "-f", "jpg"])
    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert out_jpg.exists()
    assert is_jpeg(out_jpg)

def test_convert_default_destination_does_not_overwrite_input(tmp_path):
    """
    DoD/goal: must not overwrite the original input file.
    Your code now appends '_converted' by default; this test enforces that.
    """
    src = tmp_path / "input.png"
    write_test_png(src)

    before_hash = sha256(src)
    before_mtime = src.stat().st_mtime

    cp = run_convert(["-s", str(src)])  # no -d, no -f
    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"

    after_hash = sha256(src)
    after_mtime = src.stat().st_mtime
    assert after_hash == before_hash and after_mtime == before_mtime, "Input file was modified/overwritten"

    # Verify default output exists: input_converted.png
    expected = src.with_name(src.stem + "_converted" + src.suffix)
    assert expected.exists(), f"Expected default output '{expected.name}' to be created"

def test_convert_unsupported_format_argument(tmp_path):
    src = tmp_path / "input.png"
    write_test_png(src)

    cp = run_convert(["-s", str(src), "-f", "bmp"])  # bmp 不在 choices 中
    assert cp.returncode != 0
    combined = (cp.stdout + "\n" + cp.stderr).lower()
    assert "invalid choice" in combined or "error" in combined



def test_convert_existing_destination_without_force_creates_unique_path(tmp_path):
    """
    Your code uses givecorrectdestination() + unique_path() when not forcing overwrite.
    This test verifies it does NOT overwrite existing destination.
    """
    src = tmp_path / "input.png"
    dst = tmp_path / "output.jpg"
    write_test_png(src)

    # Create an existing output file
    dst.write_bytes(b"existing file contents")
    existing_hash = sha256(dst)

    cp = run_convert(["-s", str(src), "-d", str(dst), "-f", "jpg"])  # no --force
    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"

    # Destination should NOT be overwritten
    assert sha256(dst) == existing_hash, "Destination was overwritten despite no --force"

    # A unique file should exist (e.g., output_1.jpg)
    candidates = list(tmp_path.glob("output_*.jpg"))
    assert len(candidates) >= 1, "Expected a unique output file (output_*.jpg) to be created"


def test_convert_missing_source_file_shows_error_and_nonzero_exit():
    cp = run_convert(["-s", "no_such_file.png", "-f", "jpg"])
    assert cp.returncode != 0, "Expected non-zero exit for missing file"
    combined = (cp.stdout + "\n" + cp.stderr).lower()
    assert "not a valid file" in combined or "error" in combined, (
        f"Expected descriptive error message.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    )


def test_convert_corrupted_input_shows_error_and_nonzero_exit(tmp_path):
    bad = tmp_path / "bad.png"
    bad.write_text("this is not a real image")
    out = tmp_path / "out.jpg"

    cp = run_convert(["-s", str(bad), "-d", str(out), "-f", "jpg"])
    assert cp.returncode != 0, "Corrupted input should fail with non-zero exit"
    combined = (cp.stdout + "\n" + cp.stderr).lower()
    assert "could not read" in combined or "error" in combined or "invalid" in combined, (
        f"Expected descriptive error message.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    )
    assert not out.exists(), "Should not produce output for corrupted input"

# Note: This test may be skipped on Windows because directory permission
# modifications are unreliable across operating systems.
@pytest.mark.skipif(os.name == "nt", reason="Permission-based test is unreliable on Windows")
def test_convert_unwritable_output_path_fails_gracefully(tmp_path):
    """
    DoD: show error message for invalid output path + no crash.
    Make a read-only directory and attempt to write inside it.
    """
    src = tmp_path / "input.png"
    write_test_png(src)

    ro_dir = tmp_path / "readonly"
    ro_dir.mkdir()
    os.chmod(ro_dir, 0o555)  # r-xr-xr-x

    out = ro_dir / "out.jpg"
    cp = run_convert(["-s", str(src), "-d", str(out), "-f", "jpg"])

    assert cp.returncode != 0, "Expected non-zero exit when output is unwritable"
    combined = (cp.stdout + "\n" + cp.stderr).lower()
    assert "failed to write" in combined or "permission" in combined or "error" in combined, (
        f"Expected descriptive error message.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    )
    assert not out.exists(), "Output should not be created in unwritable directory"

#Note: This performance test runs only when the environment variable
#RUN_SLOW=1 is set, to ensure stable execution across different hardware.

@pytest.mark.skipif(os.environ.get("RUN_SLOW") != "1", reason="Set RUN_SLOW=1 to enable performance test")
def test_convert_performance_under_7_seconds(tmp_path):
    """
    Optional: performance requirement check.
    Environment-dependent -> only runs if RUN_SLOW=1.
    """
    src = tmp_path / "big.png"
    img = np.zeros((4096, 4096, 3), dtype=np.uint8)
    assert cv2.imwrite(str(src), img)

    dst = tmp_path / "big.jpg"
    t0 = time.time()
    cp = run_convert(["-s", str(src), "-d", str(dst), "-f", "jpg"], timeout=30)
    t1 = time.time()

    assert cp.returncode == 0, f"Convert failed.\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
    assert dst.exists()
    assert (t1 - t0) <= 7.0, f"Performance requirement violated: {t1 - t0:.2f}s (>7s)"
