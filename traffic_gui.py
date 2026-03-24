BG_COLOR = "#0f172a"
CARD_COLOR = "#1e293b"
ACCENT = "#38bdf8"
TEXT = "white"
import tkinter as tk
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

def run_detection():

    cap = cv2.VideoCapture("traffic.mp4")
    ret, frame = cap.read()

    results = model(frame)

    vehicle_count = 0

    for box in results[0].boxes:
        cls = int(box.cls)

        if cls in [2,3,5,7]:
            vehicle_count += 1

    if vehicle_count < 10:
        density = "Low"
        green_time = 10

    elif vehicle_count < 30:
        density = "Medium"
        green_time = 20

    else:
        density = "High"
        green_time = 30

    result_label.config(
        text=f"Vehicles: {vehicle_count}\nDensity: {density}\nGreen Time: {green_time}s"
    )

root = tk.Tk()
root.title("Traffic Control System")
root.geometry("400x300")

title = tk.Label(root,text="Density Based Traffic Control System",font=("Arial",14))
title.pack(pady=10)

btn = tk.Button(root,text="Run Detection",command=run_detection)
btn.pack(pady=20)

result_label = tk.Label(root,text="",font=("Arial",12))
result_label.pack()

root.mainloop()
