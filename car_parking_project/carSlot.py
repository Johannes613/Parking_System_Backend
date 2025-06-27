from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import pickle
import numpy as np
import cvzone

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

cap = cv2.VideoCapture("carPark.mp4")

with open("CarParkPos", "rb") as f:
    posList = pickle.load(f)
    # print(f"Loaded {len(posList)} parking positions.")
    # print("Parking positions:", posList)

width, height = 107, 48

def analyze_frame():
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        return []

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(
        imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16
    )
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    return get_parking_status(imgDilate)

def get_parking_status(imgPro):
    spaceCounter = 0
    status_list = []
    for index, pos in enumerate(posList):
        x, y = pos
        imgCrop = imgPro[y: y + height, x: x + width]
        count = cv2.countNonZero(imgCrop)
        
      

        status = "Available" if count < 900 else "Occupied"
        spaceCounter += 1 if status == "Available" else 0
        basement = f"Basement {index % 3 + 1}"  # Simulated basement assignment

        status_list.append({
            "id": index + 1,
            "status": status,
            "basement": basement
        })
        print("avilable count:", spaceCounter,"occupied count:", len(posList) - spaceCounter)
      
    return status_list

@app.route('/api/parking-slots', methods=['GET'])
def parking_slots():
    status_list = analyze_frame()
    return jsonify(status_list)


if __name__ == '__main__':
    app.run(debug=True)
