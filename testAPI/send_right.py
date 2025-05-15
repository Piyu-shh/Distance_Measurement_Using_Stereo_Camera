import requests
import time

right_image_path = "right30.jpg"
url = "http://localhost:8000/upload"

while True:
    with open(right_image_path, "rb") as f:
        files = {"file": ("right30.jpg", f, "image/jpeg")}
        try:
            response = requests.post(url, files=files)
            print("[RIGHT] Image sent successfully.")
        except Exception as e:
            print(f"[RIGHT] Error: {e}")
    
    time.sleep(1)  # Send every 1 second (adjust if needed)
