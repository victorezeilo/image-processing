# TC-US2-01 Resize Image to Specified Width and Height – Successful Execution
# TC-US2-02 Resize Image With Aspect Ratio Preservation
# TC-US2-03 Resize Image Using Minimum Valid Dimensions
# TC-US2-04 Resize Image Exceeding Maximum Supported Resolution – Error Handling
# TC-US2-05 Resize Image With Invalid Dimensions (Zero, Negative, Non-Numeric)
# TC-US2-06 Missing Required Resize Parameters – User Input Validation
# TC-US2-07 Resize Images of Different Supported Formats
# TC-US2-08 Resize Image With Unwritable Output Path – Error Handling
# TC-US2-09 Image Resizing Performance Within Time Limit


import os
import time
import pytest
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np

from src.image_processing import resize

# create a temporary image for testing
def _write_temp_image(path: Path, w: int = 200, h: int = 100) -> None:
    img = np.zeros((h, w, 3), dtype=np.uint8)
    ok = cv2.imwrite(str(path), img)
    assert ok, f"Failed to write temporary image to {path}"
    
# read image dimensions
def _read_image_dim(path: Path) -> tuple[int, int]:
    img = cv2.imread(str(path))
    assert img is not None, f"Failed to read image from {path}"
    h, w = img.shape[:2] # height, width
    return w, h

# 1. resize image to specified w and h
def test_resize_success(tmp_path: Path):
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    _write_temp_image(input_path, w=200, h=100)
    
    args = SimpleNamespace(
        source=str(input_path),
        destination=str(output_path),
        width=800,
        height=600,
        force=True
    )
    
    resize.validate_resize_arguments(args)
    resize.resize_image(args)
    
    assert output_path.exists(), "Output image was not created"
    w, h = _read_image_dim(output_path)
    assert (w, h) == (800, 600), f"Expected dimensions (800, 600), got ({w}, {h})"
    
# 2. not possibe
@pytest.mark.xfail(reason="We are not implementing Aspect ratio preservation in the resize command.")
def test_aspect_ratio():
    pass

# 3. test minimum dimensions
def test_min_dimensions(tmp_path: Path):
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    _write_temp_image(input_path, w=50, h=50)
    
    args = SimpleNamespace(
        source=str(input_path),
        destination=str(output_path),
        width=1,
        height=1,
        force=True
    )
    resize.validate_resize_arguments(args)
    resize.resize_image(args)
    
    assert output_path.exists(), "Output image was not created"
    w, h = _read_image_dim(output_path)
    assert (w, h) == (1, 1), f"Expected dimensions (1, 1), got ({w}, {h})"

# 4. test exceeding max dimensions
def test_exceed_max_dimension(tmp_path: Path):
    input_path = tmp_path / "input.jpg"
    _write_temp_image(input_path)

    max_dim = getattr(resize, "MAX_DIM", 4096)

    args = SimpleNamespace(
        source=str(input_path),
        destination=None,
        width=max_dim + 1,
        height=max_dim + 1,
        force=True,
    )

    with pytest.raises(ValueError):
        resize.validate_resize_arguments(args)
        
# 5. test invalid dimensions
@pytest.mark.parametrize("width, height", [
    (0, 100),   # zero width
    (100, 0),   # zero height
    (-100, 100), # negative width
    (100, -100), # negative height
    ("abc", 100), # non-numeric width
    (100, "abc"), # non-numeric height
])
def test_invalid_dimensions(tmp_path: Path, width, height):
    input_path = tmp_path / "input.jpg"
    _write_temp_image(input_path)

    args = SimpleNamespace(
        source=str(input_path),
        destination=None,
        width=width,
        height=height,
        force=True,
    )

    with pytest.raises((ValueError, TypeError)):
        resize.validate_resize_arguments(args)

# 6. Test missing required parameters
def test_missing_parameters(tmp_path: Path):
    input_path = tmp_path / "input.jpg"
    _write_temp_image(input_path)

    # missing width
    args = SimpleNamespace(
        source=str(input_path),
        destination=None,
        width=None,  # missing width
        height=100, # missing height
        force=True,
    )

    with pytest.raises(ValueError):
        resize.validate_resize_arguments(args)
    
    # missing height
    args = SimpleNamespace(
        source=str(input_path),
        destination=None,
        width=100,  
        height=None, 
        force=True,
    )

    with pytest.raises(ValueError):
        resize.validate_resize_arguments(args)

#  7. Test resizing different formats
@pytest.mark.parametrize("ext", ["jpg", "png", "tiff"])
def test_resize_different_formats(tmp_path: Path, ext: str):
    input_path = tmp_path / f"input.{ext}"
    output_path = tmp_path / f"output.{ext}"
    _write_temp_image(input_path)

    args = SimpleNamespace(
        source=str(input_path),
        destination=str(output_path),
        width=100,
        height=100,
        force=True,
    )

    resize.validate_resize_arguments(args)
    resize.resize_image(args)

    assert output_path.exists()
    w, h = _read_image_dim(output_path)
    assert (w, h) == (100, 100)
    
# 8. test time limit
def test_resize_performance(tmp_path: Path):
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    _write_temp_image(input_path, w=3840, h=2160) # 4K image

    args = SimpleNamespace(
        source=str(input_path),
        destination=str(output_path),
        width=1920,
        height=1080,
        force=True,
    )

    start_time = time.time()
    resize.validate_resize_arguments(args)
    resize.resize_image(args)
    end_time = time.time()

    assert output_path.exists()
    w, h = _read_image_dim(output_path)
    assert (w, h) == (1920, 1080)

    elapsed_time = end_time - start_time
    assert elapsed_time < 3.0, f"Resizing took too long: {elapsed_time:.2f} seconds"