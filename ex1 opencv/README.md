# Color Detector

## How to Use - exe
Download `coldetect.exe` and run it.

If white balance is desired (i.e., the environment is lit up with yellow light), run `coldetect -wb` from the command line.

---
## How to use - `coldetect.py`
### Requirements
- Python 3.9+ (tested on Python 3.14.8)
- OpenCV with contrib modules
- NumPy
Install dependencies:
```bash
pip install numpy opencv-contrib-python
```

### Run the program

From the project folder:

```bash
python coldetect.py
```

To enable white balance:

```bash
python coldetect.py -wb
```
---

## Additional Debug Info
**If objects are not detected:**
Red and blue masks are created using predefined HSV ranges. Try changing the HSV ranges in code (`red_lower`, `red_upper`, `red_lower_high`, `red_upper_high`, `blue_lower`, `blue_upper`) to better suit your environment.

**If camera is not detected:**
The camera index is set to `0` in the script, which usually works for the built-in webcam. Try changing `cv2.VideoCapture(0)` to another index, such as `1`.
