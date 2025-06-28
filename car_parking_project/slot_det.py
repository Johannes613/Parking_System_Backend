from ultralytics import YOLO
import cv2
import pickle
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
model = YOLO("yolov8s.pt")

with open("CarParkPos", "rb") as f:
    posList = pickle.load(f)

width, height = 400, 200
slot_area = width * height
MIN_OVERLAP_RATIO = 0.45
MIN_BOX_WIDTH = 20
MIN_BOX_HEIGHT = 20

def intersection_area(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    return max(0, xB - xA) * max(0, yB - yA)

img = cv2.imread("simulated.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_height, img_width = gray.shape

results = model(img, imgsz=720, verbose=False)[0]

detections = []
for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cls = int(box.cls[0])
    w, h = x2 - x1, y2 - y1
    if cls in [2,3,5,7] and w > MIN_BOX_WIDTH and h > MIN_BOX_HEIGHT:
        detections.append((x1,y1,x2,y2))

spaceCounter = 0
for idx, (x,y) in enumerate(posList):
    x_end = min(x+width, img_width)
    y_end = min(y+height, img_height)

    slot_box = (x,y,x_end,y_end)
    occupied = False

    for det_box in detections:
        inter_area = intersection_area(slot_box, det_box)
        ratio = inter_area / slot_area

        if ratio > MIN_OVERLAP_RATIO:
            occupied = True
            break
    color = (0,0,255) if occupied else (0,255,0)
    thickness = 2 if occupied else 5
    if not occupied:
        spaceCounter += 1

    roi_x1 = x + int(width*0.2)
    roi_y1 = y + int(height*0.2)
    roi_x2 = x + int(width*0.8)
    roi_y2 = y + int(height*0.7)

    cv2.rectangle(img,(roi_x1,roi_y1),(roi_x2,roi_y2),(255,255,0),2)

    roi = gray[roi_y1:roi_y2, roi_x1:roi_x2]
    roi = cv2.resize(roi,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
    roi = cv2.GaussianBlur(roi,(3,3),0)

    _, roi = cv2.threshold(roi,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    config = r'--oem 3 --psm 7'
    text = pytesseract.image_to_string(roi, config=config).strip()
    match = re.search(r'B\d{4}', text)
    slot_number = match.group(0) if match else f"Slot {idx+1}"

    cv2.rectangle(img,(x,y),(x_end,y_end),color,thickness)
    cv2.putText(img, slot_number, (x+5,y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

cv2.putText(img, f"Free: {spaceCounter}/{len(posList)}", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,200,0), 5)
cv2.imshow("Static Image Parking Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
