import cv2
for idx in [22, 21, 15, 14]:
    cap = cv2.VideoCapture(idx)
    print(f"Camera {idx} opened:", cap.isOpened())
    ret, frame = cap.read()
    print(f"Camera {idx} frame:", ret)
    if ret:
        cv2.imshow(f"Camera {idx}", frame)
        cv2.waitKey(0)
    cap.release()