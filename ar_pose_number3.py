import numpy as np
import cv2 as cv

# 캘리브레이션 결과 불러오기
with np.load("calibration_data.npz") as data:
    K = data["camera_matrix"]
    dist_coeff = data["dist_coeffs"]

# 체스보드 설정
board_pattern = (10, 7)  # 내부 코너 수
board_cellsize = 0.025   # 체스보드 한 칸의 실제 크기
pattern_size = board_pattern

# 체스보드 3D 좌표 생성
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
objp *= board_cellsize

# 숫자 '3'의 3D 좌표 (AR 오브젝트)
number3_lower = board_cellsize * np.array([
    [1, 1, 0], [2, 1, 0], [2, 2, 0], [1.5, 2, 0], [2, 2, 0],
    [2, 3, 0], [1, 3, 0]
])
number3_upper = number3_lower.copy()
number3_upper[:, 2] = -1  # 위로 extrude

# 체스보드 영상 열기
video_file = 'recorded_video.avi'
cap = cv.VideoCapture(video_file)
assert cap.isOpened(), f"Can't open video: {video_file}"

# 영상 저장 설정
fourcc = cv.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv.CAP_PROP_FPS) or 30
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
out = cv.VideoWriter('ar_output.avi', fourcc, fps, (width, height))

screenshot_saved = False  # 스크린샷 저장 여부

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    found, corners = cv.findChessboardCorners(gray, pattern_size, None)

    if found:
        corners2 = cv.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            criteria=(cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        ret_pnp, rvec, tvec = cv.solvePnP(objp, corners2, K, dist_coeff)

        if ret_pnp:
            # 숫자 '3' 투영 및 입체 표시
            proj_lower, _ = cv.projectPoints(number3_lower, rvec, tvec, K, dist_coeff)
            proj_upper, _ = cv.projectPoints(number3_upper, rvec, tvec, K, dist_coeff)

            for i in range(len(number3_lower) - 1):
                pt1 = tuple(map(int, proj_lower[i][0]))
                pt2 = tuple(map(int, proj_lower[i+1][0]))
                cv.line(frame, pt1, pt2, (0, 0, 255), 2)

                pt1u = tuple(map(int, proj_upper[i][0]))
                pt2u = tuple(map(int, proj_upper[i+1][0]))
                cv.line(frame, pt1u, pt2u, (0, 255, 255), 2)

            for l, u in zip(proj_lower, proj_upper):
                pt_l = tuple(map(int, l[0]))
                pt_u = tuple(map(int, u[0]))
                cv.line(frame, pt_l, pt_u, (255, 255, 0), 2)

            # 카메라 위치 출력
            R, _ = cv.Rodrigues(rvec)
            pos = (-R.T @ tvec).flatten()
            info = f'XYZ: [{pos[0]:.3f} {pos[1]:.3f} {pos[2]:.3f}]'
            cv.putText(frame, info, (10, 25), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # 첫 프레임 스크린샷 저장
            if not screenshot_saved:
                cv.imwrite("screenshot.png", frame)
                print("스크린샷 저장 완료: screenshot.png")
                screenshot_saved = True

    # 결과 출력 및 저장
    cv.imshow("AR Pose with Number 3", frame)
    out.write(frame)

    if cv.waitKey(10) == 27:  # ESC
        break

# 정리
cap.release()
out.release()
cv.destroyAllWindows()
