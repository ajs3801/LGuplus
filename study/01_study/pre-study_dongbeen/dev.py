import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

#yolo v4
CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0,255,255), (255,255,0), (0,255,0), (255,0,0)]

class_name = []
with open("classes.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
#net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416,416), scale=1/255, swapRB=True)

#캠열기
cap = cv2.VideoCapture(0)

#전경 검출
ret, back = cap.read()
back = cv2.cvtColor(back, cv2.COLOR_BGR2GRAY)
back = cv2.GaussianBlur(back, (0,0),1)
back = cv2.resize(back, (250, 250))

#배경 검출
bs = cv2.createBackgroundSubtractorMOG2()
bs.setDetectShadows(False)

while True:
    ret, cam = cap.read()
    cam = cv2.resize(cam, (250, 250))
    #cam1 = cv2.resize(cam, (250, 250))
    cam2 = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)

    #threshold 처리
    #ret, cam2 = cv2.threshold(cam2, 50, 255, cv2.THRESH_BINARY) #THRESH_BINARY 적용

    #ret, cam3 = cv2.threshold(cam2, 50, 255, cv2.THRESH_BINARY_INV) #THRESH_BINARY_INV 적용

    #ret, cam3 = cv2.threshold(cam2, 50, 255, cv2.THRESH_TRUNC) #THRESH_TRUNC 적용

    ret, cam3 = cv2.threshold(cam2, 50, 255, cv2.THRESH_TOZERO) #THRESH_TOZERO 적용

    #ret, cam3 = cv2.threshold(cam2, 50, 255, cv2.THRESH_TOZERO_INV)

    cam3 = cv2.cvtColor(cam3, cv2.COLOR_GRAY2BGR)

    #blur 처리
    #cam_blur = cv2.blur(cam,(5,5))
    cam_blur_gaussian = cv2.GaussianBlur(cam,(5,5),0)
    #cam_blur_median = cv2.medianBlur(cam, 5)
    #cam_blur_bilateral = cv2.bilateralFilter(cam,9,75,75)

    #Canny edge detection
    edge = cv2.Canny(cam, 50, 150)
    edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    #edge2 = cv2.Canny(cam, 100, 200)
    #edge2 = cv2.cvtColor(edge2, cv2.COLOR_GRAY2BGR)
    
    #전경 검출
    cam4 = cv2.resize(cam, (250, 250))
    gray = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (0,0),1)

    diff = cv2.absdiff(gray, back)
    _, diff = cv2.threshold(diff, 30, 1, cv2.THRESH_BINARY)

    #cnt, _, stats, _ = cv2.connectedComponentsWithStats(diff)
    '''
    for i in range(1, cnt):
        x, y, w, h, s = stats[i]

        if s < 100:
            continue

        cv2.rectangle(cam4, (x,y,w,h), (0,0,255),2)
    '''
    diff = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)

    #배경 검출
    fgmask = bs.apply(gray)
    back2 = bs.getBackgroundImage()
    fgmask = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
    back2 = cv2.cvtColor(back2, cv2.COLOR_GRAY2BGR)

    #face detect
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    #face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt_tree.xml")

    faces = face_cascade.detectMultiScale(cam2, 1.3, 5)

    detectImage = cv2.resize(cam, (250, 250))
    src = cv2.resize(cam, (250,250))

    ratio = 0.05

    for (x,y,w,h) in faces:
        cv2.rectangle(detectImage, (x,y), (x+w, y+h), (255,0,0),2)
        roi_gray = cam2[y:y+h, x:x+w]
        roi_color = detectImage[y:y+h, x:x+w]

        small = cv2.resize(src[y: y + h, x: x + w], None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
        src[y: y + h, x: x + w] = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    #yolov4
    start = time.time()
    classes, scores, boxes = model.detect(cam, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    end = time.time()

    start_drawing = time.time()
    for (classid, score, box) in zip(classes, scores, boxes):
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %f" % (class_names[classid], score)
        cv2.rectangle(cam, box, color, 2)
        cv2.putText(cam, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    end_drawing = time.time()

    fps_label = "FPS: %.2f (excluding drawing time of %.2fms)" % (1/(end-start), (end_drawing - start_drawing) * 1000)
    cv2.putText(cam, fps_label, (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0),2)

    #detectImage = cv2.cvtColor(detectImage, cv2.COLOR_GRAY2BGR)

    #캠 합치기
    numpy_horizontal1 = np.hstack((cam, cam3))
    numpy_horizontal2 = np.hstack((fgmask, back2))
    numpy_horizontal12 = np.hstack((numpy_horizontal1, numpy_horizontal2))
    numpy_horizontal12 = np.hstack((numpy_horizontal12, cam_blur_gaussian))

    numpy_horizontal5 = np.hstack((detectImage, src))
    numpy_horizontal6 = np.hstack((diff, diff*cam4))
    numpy_horizontal56 = np.hstack((numpy_horizontal5, numpy_horizontal6))
    numpy_horizontal56 = np.hstack((numpy_horizontal56, edge))

    numpy_final = np.vstack((numpy_horizontal12, numpy_horizontal56))

    #numpy_final = np.vstack((numpy_vertical, numpy_horizontal56))


    if ret:
        #cv2.imshow('cam', cam)
        cv2.imshow('cam', numpy_final)

        if cv2.waitKey(1) &  0xFF == 27:
            break
        
cap.release()
cv2.destroyAllWindows()
