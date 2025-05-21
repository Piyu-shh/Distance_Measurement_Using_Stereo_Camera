# IoT-Based Real-Time Stereo Vision System with YOLOv8 and LLM Integration


## Introduction

This project proposes a real-time IoT-based stereo vision system that integrates computer vision and deep learning with a Raspberry Pi 3 unit and two Raspberry Pi Camera Modules. Addressing the growing demand for accurate object detection and distance measurement in intelligent, autonomous systems (e.g., smart surveillance, robotic navigation, assistive devices), this system offers a cost-effective alternative to traditional LiDAR or ultrasonic sensors.

By leveraging stereo vision, inspired by human binocular perception, the system captures simultaneous views of a scene to calculate disparity and estimate object distances with high accuracy. Coupled with the YOLOv8 deep learning model, it detects and localizes objects in real-time, extracting both spatial and semantic information from the environment.
Features

## The system encompasses the following key functionalities:

  ### Object Detection:
  -Utilizes the YOLO (You Only Look Once) deep learning model on Raspberry Pi for real-time detection of multiple objects from live camera feeds.
  -Ensures fast and accurate identification of objects such as people, vehicles, and obstacles, enabling efficient scene processing with minimal delay.

  ### Stereo Vision Setup:

  -Two Raspberry Pi cameras are mounted with a fixed baseline distance to replicate human binocular vision for depth perception.
  -Cameras are synchronized to capture images simultaneously from slightly different angles, crucial for calculating object depth via disparity mapping.

  ### Distance Measurement:

  -Employs triangulation and stereo disparity calculations to estimate the precise distance between the camera and each detected object.
  -Depth information helps determine object proximity, vital for applications in robotics, security, and automation.

  ### Direction Estimation:

  -Calculates the relative horizontal position of each object to estimate its angle or bearing from the center axis of the camera setup.
  -Provides spatial awareness for directional tracking (left/right/center) of moving objects, aiding navigation and decision-making.

  ### Query Integration using Open Router LLM:
  -The server interfaces with Open Router, a powerful natural language model, to interpret user queries and return intelligent, contextual responses.
  -Users can ask flexible questions like "What’s the closest object to the camera right now?" or "Where was the car detected in the last 5 minutes?" and receive human-like answers.

## System Architecture

![iotArc](https://github.com/user-attachments/assets/cb63c435-baf3-4298-8a4c-615a71811b01)

## Setup and Installation

### Hardware Requirements:

        Raspberry Pi 3 (or newer)

        2 x Raspberry Pi Camera Modules

        Power supply for Raspberry Pi

        SD card (minimum 16GB recommended)

        Fixed mount for stereo camera setup (with known baseline)

### Software Requirements:

        Raspberry Pi OS - 32 bit (Note: I could not get the Raspberry Pi Camera Modules to run on 64 bit version of the OS)

        Python 3.x

        OpenCV library (cv2)

        YOLOv8 model and associated dependencies (e.g., ultralytics)

        FastAPI framework for uiserver.py

        Open Router API key for LLM integration

## Working

![sw](https://github.com/user-attachments/assets/0ae3de70-e31f-4aef-b41e-6e5d34dabb11)

##TODO

1. Integrate Database
2. Integrate Face Regonization
3. Improve Calibration Method
