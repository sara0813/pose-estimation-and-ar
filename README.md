# Pose Estimation and AR
A simple project that estimates camera pose using calibration results and renders an AR object (a 3D pyramid) onto a chessboard pattern in a video.

---

## Description

This project demonstrates basic augmented reality using OpenCV.

- **Camera pose estimation** is performed with a previously calibrated camera.
- A **3D virtual pyramid** is rendered and aligned with a chessboard pattern.
- The result is shown in real-time and saved as an output video.
- A screenshot of the AR overlay is also saved automatically.

---

## How to Run

1. Place your input video (e.g., `recorded_video.avi`) containing a visible chessboard pattern in the same folder  
2. Make sure `calibration_data.npz` exists (from Homework #3)  
3. Run the Python script:

```bash
python pose_estimation_ar.py
