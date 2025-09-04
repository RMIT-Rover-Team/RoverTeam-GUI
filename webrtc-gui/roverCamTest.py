import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    ret, frame = cap.read()
    print(f"Camera {i}: Opened={cap.isOpened()}, Frame={ret}")
    cap.release()