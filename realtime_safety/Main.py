import cv2
import pickle
import numpy as np
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()

# Load predefined area positions
try:
    with open('AreaPositions.pkl', 'rb') as f:
        areaPosList = pickle.load(f)
except (FileNotFoundError, EOFError):
    print("Error: Area positions file not found or empty.")
    areaPosList = []

print(f"Loaded area positions: {areaPosList}")

sound_file = "E:/projects/realtime_safety/warning.wav"

# Check if the sound file exists
if not os.path.isfile(sound_file):
    print(f"Error: The sound file at '{sound_file}' does not exist. Please check the path.")
else:
    # Load the sound file into pygame
    sound = pygame.mixer.Sound(sound_file)

    def checkAreaIntrusion(frame, gray_frame):
        for polygon in areaPosList:
            mask = np.zeros_like(gray_frame)
            polygon_np = np.array(polygon, np.int32)
            cv2.fillPoly(mask, [polygon_np], 255)

            area_frame = cv2.bitwise_and(gray_frame, mask)
            count = cv2.countNonZero(area_frame)
            print(f"Count in area: {count}")

            if count > 50:
                color = (0, 0, 255)  # Red
                thickness = 5
                try:
                    sound.play()
                except Exception as e:
                    print(f"Error playing sound: {e}")
            else:
                color = (0, 255, 0)  # Green
                thickness = 2

            cv2.polylines(frame, [polygon_np], True, color, thickness)

    # Initialize video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Unable to capture frame.")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 1)
        _, threshold_frame = cv2.threshold(blurred_frame, 200, 255, cv2.THRESH_BINARY_INV)

        checkAreaIntrusion(frame, threshold_frame)

        cv2.imshow("Intrusion Detection", frame)
        key = cv2.waitKey(1)
        if key == 27:  # Exit on 'Esc' key
            break

    cap.release()
    cv2.destroyAllWindows()
