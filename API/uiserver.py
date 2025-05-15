from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import torch
import asyncio
import threading
import time
import requests
import json
import speech_recognition as sr
import pyttsx3
from tkinter import Tk, Label, Frame, StringVar, Button
from PIL import Image, ImageTk
from ultralytics import YOLO
from dotenv import load_dotenv
import os

project_root = os.path.dirname(os.path.dirname(__file__))

dotenv_path = os.path.join(project_root, '.env')

load_dotenv(dotenv_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


app = FastAPI()

model = YOLO("yolov8x.pt")

detection_memory = {"Left Camera": {}, "Right Camera": {}}
detection_history = []  
left_image = None
right_image = None
distance_info = "Waiting for detections..."
llm_response_text = "LLM response will appear here."

def calculate_distance(object_name, left_center, right_center, focal_length=2800, baseline=12.0):

    disparity = abs(left_center[0] - right_center[0])
    if disparity == 0:
        return {"label": object_name, "distance": float('inf'), "direction": "N/A"}
    
    distance = (focal_length * baseline) / disparity

    dx = right_center[0] - left_center[0]
    dy = right_center[1] - left_center[1]

    if dy < -10:
        vertical = "Top"
    elif dy > 10:
        vertical = "Bottom"
    else:
        vertical = ""

    if dx > 10:
        horizontal = "Right"
    elif dx < -10:
        horizontal = "Left"
    else:
        horizontal = ""

    direction = f"{vertical}-{horizontal}".strip("-")
    print(f"📏 Distance to {object_name}: {distance:.2f} cm ({direction})")
    
    return {"label": object_name, "distance": round(distance, 2), "direction": direction}

def detect_objects(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model(image)
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = model.names[class_id]

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            detections.append({
                "label": label,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2],
                "center": (center_x, center_y)
            })
    # Optionally sort by x-coordinate of the center (or by label if preferred)
    detections.sort(key=lambda obj: obj["center"][0])
    return detections, image

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):

    global left_image, right_image, distance_info, detection_history

    try:
        image_bytes = await file.read()

        if "left" in file.filename.lower():
            camera_position = "Left Camera"
        elif "right" in file.filename.lower():
            camera_position = "Right Camera"
        else:
            print("Unknown camera position!")
            return {"error": "Unknown camera position"}

        detections, image = detect_objects(image_bytes)

        if camera_position == "Left Camera":
            left_image = image
        else:
            right_image = image

        detection_memory[camera_position] = {obj["label"]: obj for obj in detections}
        print(f"\n[{camera_position}] Detected Objects:")
        for obj in detections:
            print(f"{obj['label']}: Confidence={obj['confidence']:.2f}, Center={obj['center']}")

        if camera_position == "Right Camera":
            left_objects = detection_memory["Left Camera"]
            right_objects = detection_memory["Right Camera"]
            results = []
            for right_label, right_obj in right_objects.items():
                base_name = " ".join(right_label.split()[:-1]) if right_label[-1].isdigit() else right_label
                for left_label, left_obj in left_objects.items():
                    if base_name in left_label:
                        obj_info = calculate_distance(right_label, left_obj["center"], right_obj["center"])
                        results.append(obj_info)
                        detection_history.append({**obj_info, "timestamp": time.time()})
            
            detection_history = [entry for entry in detection_history if time.time() - entry["timestamp"] <= 5]
            
            if not results:
                distance_info = "No objects detected."
            else:

                distance_info = "\n".join([
                    f"{res['label']}: {res['distance']} cm ({res['direction']})" for res in results
                ])
    except Exception as e:
        print(f"Error processing image: {e}")
        return {"error": str(e)}

    return {"status": "ok"}

@app.get("/ping")
async def health_check():
    return {"status": "running"}

async def send_to_llm(query, objects):
  
    try:
        prompt = f"{query}\n\nAdditionally, consider the following recent object detections (last 5 seconds):\n"
        for obj in objects:
            prompt += f"- {obj['label']} at {obj['distance']} cm to the {obj['direction']}\n"
        print("LLM Prompt:", prompt)
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        llm_response = response.json()["choices"][0]["message"]["content"]
        print(f"LLM Response: {llm_response}")
        

        global llm_response_text
        llm_response_text = llm_response
        engine = pyttsx3.init()
        engine.say(llm_response)
        engine.runAndWait()
    except Exception as e:
        print(f"Error sending to LLM: {e}")

def run_send_to_llm(query, recent_objects):
    """Helper to run the async function from a new thread."""
    asyncio.run(send_to_llm(query, recent_objects))

def update_gui():
    """
    Tkinter GUI update loop. Displays left/right camera images,
    distance info, and the LLM response. Also creates a mic button for voice input.
    """
    def update():
        if left_image is not None:
            left_img = cv2.resize(left_image, (400, 300))
            left_img = cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)
            left_img = ImageTk.PhotoImage(Image.fromarray(left_img))
            left_label.config(image=left_img)
            left_label.image = left_img

        if right_image is not None:
            right_img = cv2.resize(right_image, (400, 300))
            right_img = cv2.cvtColor(right_img, cv2.COLOR_BGR2RGB)
            right_img = ImageTk.PhotoImage(Image.fromarray(right_img))
            right_label.config(image=right_img)
            right_label.image = right_img

        distance_text.set(distance_info)
        llm_text.set(llm_response_text)
        root.after(100, update)

    def record_query():
        """Record the user's voice query, recognize it, and call the LLM function."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for query (speak now)...")
            try:
                audio = recognizer.listen(source, phrase_time_limit=5)
                query = recognizer.recognize_google(audio)
                print("Recognized query:", query)
            except Exception as e:
                print("Error recognizing audio:", e)
                return

        current_time = time.time()
        recent_objects = [obj for obj in detection_history if current_time - obj["timestamp"] <= 5]
        
        threading.Thread(target=run_send_to_llm, args=(query, recent_objects)).start()

    root = Tk()
    root.title("Stereo Vision Object Detection")
    root.geometry("850x600")  

    frame = Frame(root)
    frame.pack()

    global left_label, right_label
    left_label = Label(frame)
    left_label.grid(row=0, column=0, padx=5, pady=5)
    right_label = Label(frame)
    right_label.grid(row=0, column=1, padx=5, pady=5)

    global distance_text
    distance_text = StringVar()
    distance_text.set("Waiting for detections...")
    distance_label = Label(root, textvariable=distance_text, font=("Arial", 12))
    distance_label.pack(pady=5)

    global llm_text
    llm_text = StringVar()
    llm_text.set("LLM response will appear here.")
    llm_response_label = Label(root, textvariable=llm_text, font=("Arial", 12), wraplength=800, justify="left")
    llm_response_label.pack(pady=5)

    mic_button = Button(root, text="🎤 Ask (Mic)", font=("Arial", 14), command=record_query)
    mic_button.pack(pady=10)

    root.after(100, update)
    root.mainloop()

def start_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    threading.Thread(target=start_fastapi, daemon=True).start()
    update_gui()
