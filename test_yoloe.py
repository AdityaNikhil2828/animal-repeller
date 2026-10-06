import cv2
import serial
import time
from ultralytics import YOLOE

# =========================
# ESP32 SERIAL
# =========================
ESP32_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

print("Connecting to ESP32...")

esp32 = serial.Serial(
    ESP32_PORT,
    BAUD_RATE,
    timeout=1
)

# Give ESP32 time to reset
time.sleep(2)

print("ESP32 connected!")

# =========================
# YOLOE
# =========================
print("Loading YOLOE...")

model = YOLOE("yoloe-26s-seg.pt")
model.set_classes(["tiger"])

print("YOLOE loaded!")
print("Target: TIGER")
print("Press Q to quit.")

# =========================
# CAMERA
# =========================
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Webcam could not be opened.")
    esp32.close()
    exit()

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# =========================
# DETECTION SETTINGS
# =========================
last_trigger_time = 0
COOLDOWN = 7        # seconds
CONFIDENCE = 0.35

while True:

    ret, frame = camera.read()

    if not ret:
        print("Could not read webcam.")
        break

    results = model.predict(
        frame,
        conf=CONFIDENCE,
        verbose=False
    )

    detected = False
    best_confidence = 0

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name.lower() == "tiger":

                detected = True
                best_confidence = max(
                    best_confidence,
                    confidence
                )

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                # Red bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3
                )

                label = f"TIGER {confidence * 100:.1f}%"

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

    # =========================
    # TIGER DETECTED
    # =========================

    if detected:

        cv2.putText(
            frame,
            "!!! TIGER DETECTED !!!",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            3
        )

        current_time = time.time()

        # Check cooldown
        if current_time - last_trigger_time >= COOLDOWN:

            print(
                f"TIGER DETECTED - "
                f"{best_confidence * 100:.1f}%"
            )

            print("Sending TIGER command to ESP32...")

            esp32.write(b"TIGER\n")
            esp32.flush()

            print("BUZZER TRIGGERED!")

            last_trigger_time = current_time

        else:

            remaining = COOLDOWN - (
                current_time - last_trigger_time
            )

            cv2.putText(
                frame,
                f"Buzzer cooldown: {remaining:.1f}s",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

    else:

        cv2.putText(
            frame,
            "No tiger detected",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )

    # =========================
    # SHOW CAMERA
    # =========================

    cv2.imshow(
        "Animal Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =========================
# CLEANUP
# =========================

print("Stopping...")

# Make sure buzzer is stopped
try:
    esp32.write(b"STOP\n")
    esp32.flush()
except:
    pass

camera.release()
cv2.destroyAllWindows()
esp32.close()

print("Detection stopped.")
