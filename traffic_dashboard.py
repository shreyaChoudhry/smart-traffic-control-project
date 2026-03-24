import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO
import cv2
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

model = YOLO("yolov8n.pt")

video_cap = None
lane_counts = [0,0,0,0]

# -----------------------------
# Upload Video
# -----------------------------

def upload_video():
    global video_cap
    file_path = filedialog.askopenfilename()
    video_cap = cv2.VideoCapture(file_path)
    process_video()

# -----------------------------
# Density Calculation
# -----------------------------

def get_density(count):

    if count < 10:
        return "LOW"
    elif count < 30:
        return "MEDIUM"
    else:
        return "HIGH"

# -----------------------------
# Update Traffic Signals
# -----------------------------

def update_signals(priority):

    for i in range(4):
        lights[i].itemconfig(circles[i], fill="red")

    lights[priority-1].itemconfig(circles[priority-1], fill="green")

# -----------------------------
# Update Graph
# -----------------------------

def update_graph():

    ax.clear()

    lanes = ["Lane1","Lane2","Lane3","Lane4"]

    ax.bar(lanes, lane_counts, color="#38bdf8")

    ax.set_title("Traffic Per Lane", color="white")

    ax.set_facecolor("#1e293b")

    fig.patch.set_facecolor("#1e293b")

    canvas.draw()

# -----------------------------
# Video Processing
# -----------------------------

def process_video():

    global video_cap

    ret, frame = video_cap.read()

    if not ret:
        return

    results = model(frame)

    width = frame.shape[1]
    lane_width = width // 4

    lane_counts[:] = [0,0,0,0]
    vehicle_count = 0

    for box in results[0].boxes:

        cls = int(box.cls)

        if cls in [2,3,5,7]:

            vehicle_count += 1

            x1 = int(box.xyxy[0][0])
            lane = x1 // lane_width

            if lane < 4:
                lane_counts[lane] += 1

    density = get_density(vehicle_count)

    priority_lane = lane_counts.index(max(lane_counts)) + 1

    update_signals(priority_lane)

    update_graph()

    vehicles_label.config(text=str(vehicle_count))
    density_label.config(text=density)
    priority_label.config(text="Lane "+str(priority_lane))

    lane1_label.config(text=str(lane_counts[0]))
    lane2_label.config(text=str(lane_counts[1]))
    lane3_label.config(text=str(lane_counts[2]))
    lane4_label.config(text=str(lane_counts[3]))

    annotated = results[0].plot()

    img = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    img = Image.fromarray(img)

    img = img.resize((640,360))

    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(10, process_video)

# -----------------------------
# GUI Layout
# -----------------------------

root = tk.Tk()
root.title("Smart Traffic Control Dashboard")
root.geometry("1200x750")
root.configure(bg="#0f172a")

title = tk.Label(root,
                 text="SMART TRAFFIC CONTROL SYSTEM",
                 font=("Arial",24,"bold"),
                 fg="white",
                 bg="#0f172a")

title.pack(pady=10)

upload_btn = tk.Button(root,
                       text="Upload Traffic Video",
                       font=("Arial",12),
                       bg="#38bdf8",
                       command=upload_video)

upload_btn.pack(pady=10)

# -----------------------------
# Video Frame
# -----------------------------

video_label = tk.Label(root)
video_label.pack()

# -----------------------------
# Stats Dashboard
# -----------------------------

stats_frame = tk.Frame(root, bg="#0f172a")
stats_frame.pack(pady=15)

def create_card(title):

    frame = tk.Frame(stats_frame,
                     bg="#1e293b",
                     padx=30,
                     pady=20)

    label_title = tk.Label(frame,
                           text=title,
                           font=("Arial",12),
                           fg="#94a3b8",
                           bg="#1e293b")

    label_title.pack()

    label_value = tk.Label(frame,
                           text="0",
                           font=("Arial",18,"bold"),
                           fg="white",
                           bg="#1e293b")

    label_value.pack()

    frame.pack(side=tk.LEFT,padx=15)

    return label_value

vehicles_label = create_card("VEHICLES")
density_label = create_card("DENSITY")
priority_label = create_card("PRIORITY LANE")

# -----------------------------
# Lane Statistics
# -----------------------------

lane_frame = tk.Frame(root,bg="#0f172a")
lane_frame.pack(pady=10)

lane1_label = tk.Label(lane_frame,text="0",fg="white",bg="#0f172a")
lane2_label = tk.Label(lane_frame,text="0",fg="white",bg="#0f172a")
lane3_label = tk.Label(lane_frame,text="0",fg="white",bg="#0f172a")
lane4_label = tk.Label(lane_frame,text="0",fg="white",bg="#0f172a")

tk.Label(lane_frame,text="Lane1",fg="white",bg="#0f172a").grid(row=0,column=0,padx=15)
tk.Label(lane_frame,text="Lane2",fg="white",bg="#0f172a").grid(row=0,column=1,padx=15)
tk.Label(lane_frame,text="Lane3",fg="white",bg="#0f172a").grid(row=0,column=2,padx=15)
tk.Label(lane_frame,text="Lane4",fg="white",bg="#0f172a").grid(row=0,column=3,padx=15)

lane1_label.grid(row=1,column=0)
lane2_label.grid(row=1,column=1)
lane3_label.grid(row=1,column=2)
lane4_label.grid(row=1,column=3)

# -----------------------------
# Traffic Lights
# -----------------------------

signal_frame = tk.Frame(root,bg="#0f172a")
signal_frame.pack(pady=20)

lights = []
circles = []

for i in range(4):

    canvas_light = tk.Canvas(signal_frame,
                             width=60,
                             height=60,
                             bg="#0f172a",
                             highlightthickness=0)

    circle = canvas_light.create_oval(10,10,50,50,fill="red")

    canvas_light.grid(row=0,column=i,padx=25)

    lights.append(canvas_light)
    circles.append(circle)

# -----------------------------
# Graph
# -----------------------------

fig, ax = plt.subplots(figsize=(4,2))

fig.patch.set_facecolor("#1e293b")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()