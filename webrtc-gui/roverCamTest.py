import cv2

for i in [0, 1]:
    cap = cv2.VideoCapture(i)
    if not cap.isOpened():
        print(f"Camera {i} not available")
        continue
    ret, frame = cap.read()
    if ret:
        print(f"Camera {i} works, frame size: {frame.shape}")
        cv2.imwrite(f"frame_{i}.jpg", frame)
    cap.release()
