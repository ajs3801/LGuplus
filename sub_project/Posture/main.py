import utils.Engine as Engine
import cv2 # Import opencv

if __name__ == "__main__":
  MODEL = "model/ActionV7_rf.pkl"
  VIDEO_PATH = "RandomVideo/JS_SPPSLSPLSS.mov"

  # TESTCAM
  cap = cv2.VideoCapture(VIDEO_PATH)

  # REALTIME CAM
  # cap = cv2.VideoCapture(0)

  # Engine.StartEngine(cap)
  Engine.InferenceEngine(cap,MODEL)