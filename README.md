# 🏎️ Gesture-Controlled Racing Game with Power-Ups & Day-Night Cycle

A unique racing game built with **Pygame**, **MediaPipe**, and **OpenCV**, where your **hand gestures** control the car. Collect coins, avoid obstacles, and enjoy a dynamic day-night cycle as you race!

## 🎮 Features

- 👋 **Hand Gesture Control** (via webcam using MediaPipe):
  - **Open Palm**: Start or speed up the car
  - **Thumbs Up**: Boost speed temporarily

- 🛣️ **Dynamic Road Design** with stripes and smooth lane-based movement

- 🌗 **Day-Night Cycle** that transitions every 30 seconds

- 🪙 **Coins and Power-Ups**:
  - Collect coins to increase score
  - Shield power-up activates after collecting a coin

- 🚧 **Obstacles** to dodge or crash into

- 🧠 **Difficulty Levels**: Easy, Medium, and Hard

- 🔊 **Realistic Sounds**:
  - Background engine sound
  - Crash and Boost sounds

- 📈 **Score Tracking** and Level Progression

## 🛠️ Tech Stack

- `Python`
- `Pygame`
- `MediaPipe` (for gesture recognition)
- `OpenCV` (for webcam input)

## 🖥️ How to Run

1. **Install dependencies**:
   ```bash
   pip install pygame opencv-python mediapipe
🎮 Controls
Gesture	Action
✋ Open Palm	Start & accelerate
👍 Thumbs Up	Boost speed (cooldown: 5s)
🕹️ Arrow Keys	Navigate menus
⌨️ Keyboard	Enter name, restart/quit
🧠 Game Flow
Enter your name

Choose difficulty (Easy / Medium / Hard)

Use gestures to control the car

Avoid obstacles, collect coins

Game ends on collision (unless shield is active)![image](https://github.com/user-attachments/assets/804d3310-5c1f-473b-a89d-ec48bb084733)
