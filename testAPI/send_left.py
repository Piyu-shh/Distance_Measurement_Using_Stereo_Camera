import requests
import time

left_image_path = "left30.jpg"
url = "http://localhost:8000/upload"

while True:
    with open(left_image_path, "rb") as f:
        files = {"file": ("left30.jpg", f, "image/jpeg")}
        try:
            response = requests.post(url, files=files)
            print("[LEFT] Image sent successfully.")
        except Exception as e:
            print(f"[LEFT] Error: {e}")
    
    time.sleep(1)  # Send every 1 second (adjust if needed)
