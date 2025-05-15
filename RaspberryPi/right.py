import cv2
import numpy as np
import subprocess
import requests
import time


NGROK_URL = "https://768d-157-49-105-103.ngrok-free.app/upload"

# Start libcamera-vid process to capture raw video
process = subprocess.Popen([
    'libcamera-vid', '-t', '0', '--width', '640', '--height', '480', '--codec', 'yuv420', '-o', '-'
], stdout=subprocess.PIPE)

def yuv_to_bgr(frame, width, height):
    yuv_frame = np.frombuffer(frame, dtype=np.uint8).reshape((height * 3 // 2, width))
    return cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR_I420)

while True:
    frame_size = 640 * 480 * 3 // 2
    frame = process.stdout.read(frame_size)

    if len(frame) != frame_size:
        print("❌ Frame read error!")
        break

    # Convert to BGR and display locally for debugging
    bgr_frame = yuv_to_bgr(frame, 640, 480)
    cv2.imshow('Right Camera', bgr_frame)

    # Save frame as image
    image_path = "/tmp/right_frame.jpg"
    cv2.imwrite(image_path, bgr_frame)

    # Send image to FastAPI server with device identifier
    with open(image_path, 'rb') as image_file:
        try:
            response = requests.post(NGROK_URL, files={"file": image_file}, data={"device": "right"})
            print(f"✅ Right image sent. Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending image: {e}")

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

process.terminate()
cv2.destroyAllWindows()
