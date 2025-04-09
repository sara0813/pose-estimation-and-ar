import cv2
import numpy as np

# 캘리브레이션 결과 로드
with np.load('calibration_data.npz') as X:
    camera_matrix, dist_coeffs = [X[i] for i in ('camera_matrix', 'dist_coeffs')]

# 체스보드 설정
pattern_size = (7, 10)   # 내부 코너 수 (가로 x 세로)
square_size = 1.0        # 한 칸의 실제 크기 (단위는 일관성만 있으면 됨)

# 체스보드 3D 좌표 생성
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
objp *= square_size

# 피라미드 3D 좌표 설정 (체스보드 중앙 근처에 위치)
pyramid_points = np.array([
    [2, 2, 0],
    [3, 2, 0],
    [3, 3, 0],
    [2, 3, 0],
    [2.5, 2.5, -1]  # 꼭짓점 (위쪽으로 솟게)
], dtype=np.float32) * square_size

# 비디오 열기
cap = cv2.VideoCapture('recorded_video.avi')  # 또는 0: 웹캠

# 저장용 비디오 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter('ar_output.avi', fourcc, fps, (width, height))

screenshot_saved = False  # 첫 스크린샷 저장 여부

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 체스보드 코너 찾기
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    if ret:
        print("체스보드 인식 성공")

        # 코너 정제
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

        # 포즈 추정
        ret_pnp, rvecs, tvecs = cv2.solvePnP(objp, corners2, camera_matrix, dist_coeffs)

        # 코너 시각화
        cv2.drawChessboardCorners(frame, pattern_size, corners2, ret)

        if ret_pnp:
            # 피라미드 점들을 이미지 좌표로 투영
            imgpts, _ = cv2.projectPoints(pyramid_points, rvecs, tvecs, camera_matrix, dist_coeffs)
            imgpts = np.int32(imgpts).reshape(-1, 2)

            # 밑면 사각형 그리기
            frame = cv2.drawContours(frame, [imgpts[:4]], -1, (0, 255, 0), -3)

            # 꼭짓점과 밑면을 연결하는 선 그리기
            for i in range(4):
                frame = cv2.line(frame, tuple(imgpts[i]), tuple(imgpts[4]), (0, 0, 255), 2)

            # 스크린샷 저장 (첫 성공 프레임)
            if not screenshot_saved:
                cv2.imwrite("screenshot.png", frame)
                print("스크린샷 저장 완료: screenshot.png")
                screenshot_saved = True
        else:
            print("PnP 실패: 포즈를 추정할 수 없습니다.")
    else:
        print("체스보드 인식 실패")

    # 화면 출력 및 저장
    cv2.imshow('AR Pyramid', frame)
    out.write(frame)

    if cv2.waitKey(1) == 27:  # ESC 키로 종료
        break

# 정리
cap.release()
out.release()
cv2.destroyAllWindows()
