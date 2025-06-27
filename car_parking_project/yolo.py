from ultralytics import YOLO
import cv2
import pickle

# Load YOLO
model = YOLO("yolov8s.pt")  # More accurate than yolov8n.pt

# Load slot positions
with open("CarParkPos", "rb") as f:
    posList = pickle.load(f)

# Define slot size
width, height = 400, 200

# Minimum size of YOLO box to consider (tweak based on actual image)
MIN_BOX_WIDTH = 20
MIN_BOX_HEIGHT = 20

# Video loop
cap = cv2.VideoCapture("real_car.mp4")
while True:
    success, img = cap.read()
    if not success:
        break

    # Run detection on larger input size for small objects
    results = model(img, imgsz=720, verbose=False)[0]

    # Collect car-related detections
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        box_width = x2 - x1
        box_height = y2 - y1

        if cls in [2, 3, 5, 7] and box_width > MIN_BOX_WIDTH and box_height > MIN_BOX_HEIGHT:
            detections.append((x1, y1, x2, y2))

    # Check occupancy
    spaceCounter = 0
    for pos in posList:
        x, y = pos
        slot_rect = (x, y, x + width, y + height)
        occupied = False

        for x1, y1, x2, y2 in detections:
            if not (x2 < x or x1 > x + width or y2 < y or y1 > y + height):
                occupied = True
                break

        if occupied:
            color = (0, 0, 255)
            thickness = 2
        else:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1

        cv2.rectangle(img, pos, (x + width, y + height), color, thickness)

    cv2.putText(
        img,
        f"Free: {spaceCounter}/{len(posList)}",
        (100, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        2,
        (0, 200, 0),
        5
    )

    cv2.imshow("YOLO Smart Parking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break