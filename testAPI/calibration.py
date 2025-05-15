import cv2
import numpy as np

left_img_path = "left15.jpg"   
right_img_path = "right15.jpg" 
baseline = 12.0  

left_img = cv2.imread(left_img_path)
right_img = cv2.imread(right_img_path)

if left_img is None or right_img is None:
    print("Error: Could not load the images. Check the paths.")
    exit()

left_img_display = left_img.copy()
right_img_display = right_img.copy()

points = {"left": None, "right": None}

def click_event_left(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points["left"] = (x, y)
        cv2.circle(left_img_display, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Left Image", left_img_display)
        print(f"Left point selected at: {(x, y)}")

def click_event_right(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points["right"] = (x, y)
        cv2.circle(right_img_display, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Right Image", right_img_display)
        print(f"Right point selected at: {(x, y)}")

cv2.namedWindow("Left Image", cv2.WINDOW_NORMAL)
cv2.namedWindow("Right Image", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Left Image", 600, 400)
cv2.resizeWindow("Right Image", 600, 400)

cv2.imshow("Left Image", left_img_display)
cv2.imshow("Right Image", right_img_display)
cv2.setMouseCallback("Left Image", click_event_left)
cv2.setMouseCallback("Right Image", click_event_right)

print("Click on the corresponding point in the LEFT image, then in the RIGHT image.")
print("Press 'q' to continue after selecting both points.")

while True:
    if points["left"] is not None and points["right"] is not None:
        break
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

if points["left"] is None or points["right"] is None:
    print("Both corresponding points were not selected properly. Exiting.")
    exit()

disparity = abs(points["left"][0] - points["right"][0])
print(f"Measured disparity (in pixels): {disparity}")

try:
    known_distance = float(input("Enter the known distance to the selected point (in cm): "))
except ValueError:
    print("Invalid input for distance. Exiting.")
    exit()

f_eff = (known_distance * disparity) / baseline
print(f"Calibrated effective focal length (in pixels): {f_eff:.2f}")

def measure_distance(disparity, baseline, f_eff):
    if disparity == 0:
        return float('inf')
    return (f_eff * baseline) / disparity

estimated_distance = measure_distance(disparity, baseline, f_eff)
print(f"With the measured disparity, the computed distance is: {estimated_distance:.2f} cm")
