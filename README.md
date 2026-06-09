# 🖱️ Virtual Mouse using OpenCV and MediaPipe

Control your computer mouse using hand gestures via webcam — no physical mouse needed!

## ✋ Gestures
| Gesture | Action |
|---|---|
| Index finger up | Move cursor |
| Index + Middle pinch | Left click |
| Index + Thumb pinch | Right click |
| Middle + Ring pinch | Scroll up/down |

## 🛠️ Tech Stack
- Python 3.11
- OpenCV
- MediaPipe
- PyAutoGUI

## ▶️ How to Run
```bash
pip install opencv-python mediapipe==0.10.9 pyautogui numpy
python virtual_mouse.py
```

## 📁 Project Structure
```
VirtualMouse/
├── hand_detector.py   # Hand tracking module
├── virtual_mouse.py   # Main file
└── README.md
```