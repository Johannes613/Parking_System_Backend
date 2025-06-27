from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import pickle
import numpy as np
import threading
import time

app = Flask(__name__)
CORS(app)

# Load parking positions
with open("CarParkPos", "rb") as f:
    posList = pickle.load(f)

# Video capture setup
cap = cv2.VideoCapture("carPark.mp4")
width, height = 107, 48

# Global variable to store latest status
latest_status = []

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

    print(f"Available: {spaceCounter}, Occupied: {len(posList) - spaceCounter}")
    return status_list

def video_processing_loop():
    global latest_status
    while True:
        latest_status = analyze_frame()


@app.route('/api/parking-slots', methods=['GET'])
def parking_slots():
    return jsonify(latest_status)

if __name__ == '__main__':
    thread = threading.Thread(target=video_processing_loop)
    thread.daemon = True  # Ensures thread exits with main program
    thread.start()

    app.run(debug=True)
