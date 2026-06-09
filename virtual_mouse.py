import cv2
import numpy as np
import pyautogui
import time
from hand_detector import HandDetector

# ── Settings ──────────────────────────────────────────
CAM_W, CAM_H = 640, 480
FRAME_REDUCE = 100        # shrink active zone to reduce edge jitter
SMOOTHING = 7             # higher = smoother but slower cursor
CLICK_DISTANCE = 35       # pixels between fingers to trigger click
SCROLL_DISTANCE = 40      # pixels between fingers to trigger scroll

# ── Init ──────────────────────────────────────────────
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)
cap.set(3, CAM_W)
cap.set(4, CAM_H)

detector = HandDetector()

prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
last_click_time = 0

# ── Landmark IDs ──────────────────────────────────────
# 4=thumb, 8=index tip, 12=middle tip, 16=ring tip, 20=pinky tip

def distance(p1, p2):
    return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

# ── Main Loop ─────────────────────────────────────────
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)          # mirror so it feels natural
    frame = detector.find_hands(frame)
    landmarks = detector.get_positions(frame)

    if landmarks:
        # Key points
        ix, iy = landmarks[8][1], landmarks[8][2]   # index tip
        mx, my = landmarks[12][1], landmarks[12][2] # middle tip
        tx, ty = landmarks[4][1], landmarks[4][2]   # thumb tip
        rx, ry = landmarks[16][1], landmarks[16][2] # ring tip

        # ── MOVE: only index finger up ──
        # Map index finger position to screen (with reduced frame zone)
        screen_x = np.interp(ix, (FRAME_REDUCE, CAM_W - FRAME_REDUCE), (0, screen_w))
        screen_y = np.interp(iy, (FRAME_REDUCE, CAM_H - FRAME_REDUCE), (0, screen_h))

        # Smooth the movement
        curr_x = prev_x + (screen_x - prev_x) / SMOOTHING
        curr_y = prev_y + (screen_y - prev_y) / SMOOTHING
        pyautogui.moveTo(curr_x, curr_y)
        prev_x, prev_y = curr_x, curr_y

        cv2.circle(frame, (ix, iy), 10, (0, 255, 0), cv2.FILLED)

        # ── LEFT CLICK: index + middle close together ──
        click_dist = distance((ix, iy), (mx, my))
        if click_dist < CLICK_DISTANCE:
            now = time.time()
            if now - last_click_time > 0.4:   # prevent double-click spam
                pyautogui.click()
                last_click_time = now
                cv2.circle(frame, (ix, iy), 15, (0, 0, 255), cv2.FILLED)

        # ── RIGHT CLICK: index + thumb close together ──
        right_dist = distance((ix, iy), (tx, ty))
        if right_dist < CLICK_DISTANCE:
            now = time.time()
            if now - last_click_time > 0.6:
                pyautogui.rightClick()
                last_click_time = now
                cv2.circle(frame, (ix, iy), 15, (255, 0, 0), cv2.FILLED)

        # ── SCROLL: middle + ring fingers close together ──
        scroll_dist = distance((mx, my), (rx, ry))
        if scroll_dist < SCROLL_DISTANCE:
            if my < CAM_H // 2:
                pyautogui.scroll(3)    # scroll up
            else:
                pyautogui.scroll(-3)   # scroll down
            cv2.putText(frame, "SCROLL", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # ── UI Overlay ────────────────────────────────────
    cv2.rectangle(frame,
                  (FRAME_REDUCE, FRAME_REDUCE),
                  (CAM_W - FRAME_REDUCE, CAM_H - FRAME_REDUCE),
                  (255, 255, 0), 2)
    cv2.putText(frame, "Virtual Mouse | Q to quit", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()