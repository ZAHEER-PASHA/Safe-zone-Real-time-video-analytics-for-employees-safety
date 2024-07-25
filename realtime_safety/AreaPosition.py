import cv2
import pickle
import numpy as np

# Load the existing area positions or initialize an empty list if the file is not found
try:
    with open('AreaPositions.pkl', 'rb') as f:
        posList = pickle.load(f)
except (FileNotFoundError, EOFError):
    posList = []

# Variables to keep track of the drawing state and selected point for moving
selected_point = None
polygon_index = -1
point_index = -1
current_polygon = []

def mouseClick(event, x, y, flags, param):
    global selected_point, polygon_index, point_index, current_polygon

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(current_polygon) < 1 or np.linalg.norm(np.array(current_polygon[-1]) - np.array([x, y])) > 10:
            current_polygon.append((x, y))
        else:
            current_polygon[-1] = (x, y)

        if len(current_polygon) > 2 and np.linalg.norm(np.array(current_polygon[0]) - np.array([x, y])) < 10:
            posList.append(current_polygon)
            current_polygon = []
            with open('AreaPositions.pkl', 'wb') as f:
                pickle.dump(posList, f)

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Check if the click is near any polygon point
        for i, pos in enumerate(posList):
            for j, point in enumerate(pos):
                if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                    selected_point = (x, y)
                    polygon_index = i
                    point_index = j
                    return

        # Check if the click is inside any polygon
        for i, pos in enumerate(posList):
            if cv2.pointPolygonTest(np.array(pos), (x, y), False) >= 0:
                posList.pop(i)
                with open('AreaPositions.pkl', 'wb') as f:
                    pickle.dump(posList, f)
                return

    elif event == cv2.EVENT_MOUSEMOVE:
        if selected_point:
            posList[polygon_index][point_index] = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        selected_point = None

# Main loop
while True:
    img = cv2.imread("E:/projects/realtime_safety/sample.jpg")
    if img is None:
        print("Error: Image file not found. Please check the path.")
        break

    # Draw the current polygon being created
    if current_polygon:
        cv2.polylines(img, [np.array(current_polygon)], False, (0, 255, 255), 2)
        for point in current_polygon:
            cv2.circle(img, point, 5, (0, 255, 0), cv2.FILLED)

    # Draw all polygons
    for pos in posList:
        cv2.polylines(img, [np.array(pos)], True, (255, 0, 255), 2)
        for point in pos:
            cv2.circle(img, point, 5, (0, 255, 0), cv2.FILLED)

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    
    key = cv2.waitKey(1)
    if key == 27:  # Exit on 'Esc' key
        break

# Save the final positions
with open('AreaPositions.pkl', 'wb') as f:
    pickle.dump(posList, f)

cv2.destroyAllWindows()
