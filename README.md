# Pose Estimation and AR
A simple project that estimates camera pose using calibration results and renders an AR object (a 3D pyramid) onto a chessboard pattern in a video.

## Description

This project performs:

- **Camera Pose Estimation** using a pre-calibrated camera and chessboard detection
- **AR Object Rendering** by overlaying a virtual 3D pyramid onto the video feed
- The camera calibration data is loaded from `calibration_data.npz`, created in a previous assignment

## ▶ How to Run
1. Place your input video (e.g., `recorded_video.avi`) containing a visible chessboard pattern in the same folder
2. Make sure `calibration_data.npz` exists (from Homework #3)
3. Run the Python script:

```bash
python pose_estimation_ar.py
