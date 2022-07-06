import numpy as np
import cv2

MHI_DURATION = 50
DEFAULT_THRESHOLD = 32

def main():
    live_video = True
    video_src = 0
    if not live_video:
        video_src = "E:\Projects\computer-vision\computer-vision-python\opencv-starter\data/video/Sequence_6/visor_1246523090489_new_6_camera1.avi".replace('\\', '/')
        video_src = "E:\Projects\computer-vision\computer-vision-python\opencv-starter\data/video\AVSS/AVSS_AB_Easy.avi".replace('\\', '/')

    cv2.namedWindow('motion-history')
    cv2.namedWindow('raw')
    cv2.moveWindow('raw', 200, 0)

    cam = cv2.VideoCapture(video_src)
    ret, frame = cam.read()
    h, w = frame.shape[:2]
    prev_frame = frame.copy()
    motion_history = np.zeros((h, w), np.float32)
    timestamp = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        frame_diff = cv2.absdiff(frame, prev_frame)
        gray_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
        ret, fgmask = cv2.threshold(gray_diff, DEFAULT_THRESHOLD, 1, cv2.THRESH_BINARY)
        timestamp += 1

        # update motion history
        cv2.motempl.updateMotionHistory(fgmask, motion_history, timestamp, MHI_DURATION)

        # normalize motion history
        # np.clip -> array 값이 지정한 최솟값보다 작으면 그  최솟값으로 지정, 만약 지정한 최댓값보다 크면 최댓값으로 고정
        # np.uint8 -> 1byte 만큼의 정수표현
        mh = np.uint8(np.clip((motion_history - (timestamp - MHI_DURATION)) / MHI_DURATION, 0, 1) * 255)
        cv2.imshow('motion-history', mh)
        cv2.imshow('raw', frame)

        prev_frame = frame.copy()
        if 0xFF & cv2.waitKey(5) == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()