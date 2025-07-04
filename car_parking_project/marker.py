import cv2
import pickle


width = 400
height = 200

try:
    with open("CarParkPos", "rb") as f:
        posList = pickle.load(f)
except:
    posList = []


def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for index, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(index)

    with open("CarParkPos", "wb") as f:
        pickle.dump(posList, f)


while True:
    img = cv2.imread("simulated.png")
    # cv2.rectangle(img,(50,192),(157,240),(255,0,255),2)
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    cv2.waitKey(1)
