from flask import Flask, render_template, Response, jsonify, request
import cv2
from ultralytics import YOLO
import time

app = Flask(__name__)

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("traffic.mp4")

vehicle_count = 0
density = "LOW"
lane_counts = [0,0,0,0]
priority_lane = 1

signal_timer = 20
last_switch = time.time()


# -------------------------
# FRAME PROCESSING
# -------------------------

def process_frame(frame):

    global vehicle_count, density, lane_counts
    global priority_lane, signal_timer, last_switch

    results = model(frame)

    h,w,_ = frame.shape
    lane_width = w // 4

    lane_counts = [0,0,0,0]
    vehicle_count = 0

    overlay = frame.copy()

    # lane lines
    for i in range(1,4):
        cv2.line(frame,(i*lane_width,0),(i*lane_width,h),(0,255,255),2)

    # vehicle detection
    for box in results[0].boxes:

        cls = int(box.cls)

        if cls in [2,3,5,7]:   # car, motorcycle, bus, truck

            vehicle_count += 1

            x1,y1,x2,y2 = map(int,box.xyxy[0])
            center_x = int((x1+x2)/2)

            lane = center_x // lane_width

            if lane < 4:
                lane_counts[lane] += 1

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,255),2)

    # density calculation
    if vehicle_count < 10:
        density = "LOW"
    elif vehicle_count < 30:
        density = "MEDIUM"
    else:
        density = "HIGH"

    # heatmap
    for i,count in enumerate(lane_counts):

        x1 = i*lane_width
        x2 = (i+1)*lane_width

        if count > 12:
            color = (0,0,255)
        elif count > 6:
            color = (0,165,255)
        else:
            color = (0,255,0)

        cv2.rectangle(overlay,(x1,0),(x2,h),color,-1)

    frame = cv2.addWeighted(overlay,0.15,frame,0.85,0)

    # lane counters on video
    for i,count in enumerate(lane_counts):

        text = f"Lane {i+1}: {count}"

        cv2.putText(frame,text,
                    (i*lane_width+20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,255,0),
                    2)

    # signal switching
    if time.time() - last_switch >= 1:

        signal_timer -= 1
        last_switch = time.time()

        if signal_timer <= 0:

            priority_lane = lane_counts.index(max(lane_counts)) + 1
            signal_timer = 20

    # display signal info
    cv2.putText(frame,
                f"Green Lane: {priority_lane}",
                (20,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                3)

    cv2.putText(frame,
                f"Timer: {signal_timer}s",
                (20,120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,255,0),
                3)

    return frame


# -------------------------
# VIDEO STREAM
# -------------------------

def generate():

    while True:

        success, frame = cap.read()

        if not success:
            break

        processed = process_frame(frame)

        ret, buffer = cv2.imencode('.jpg', processed)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# -------------------------
# DATA API
# -------------------------

@app.route("/data")

def data():

    return jsonify({

        "vehicles": vehicle_count,
        "density": density,
        "lane1": lane_counts[0],
        "lane2": lane_counts[1],
        "lane3": lane_counts[2],
        "lane4": lane_counts[3],
        "priority": priority_lane,
        "timer": signal_timer

    })


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/upload', methods=['POST'])

def upload():

    global cap

    file = request.files['video']

    file.save("uploaded.mp4")

    cap = cv2.VideoCapture("uploaded.mp4")

    return render_template("index.html")


# -------------------------
# START SERVER
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)