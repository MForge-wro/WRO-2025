# Raspberry Pi Robot Control System

A sophisticated robot control system built with Raspberry Pi, featuring computer vision-based navigation, obstacle avoidance, and precise motor control.

## 🚀 Features

- **Computer Vision Navigation**
  - Real-time path detection using color-based segmentation
  - Wall detection and angle calculation
  - Corner detection for precise turning
  - Block detection and classification

- **Advanced Control System**
  - Priority-based decision making
  - Wall angle override system
  - Parabolic path planning
  - Smooth steering control

- **Hardware Integration**
  - Direct GPIO control for motors
  - PWM-based speed control
  - Simulation mode for testing without hardware

## 📋 Prerequisites

- Raspberry Pi (tested on Raspberry Pi 4)
- Python 3.x
- Required Python packages:
  ```bash
  pip install numpy opencv-python picamera2
  ```

## 🛠️ Hardware Setup

### Motor Connections
- **Drive Motor (L298N)**
  - IN1: GPIO 27
  - IN2: GPIO 17
  - ENA: GPIO 22 (PWM)

- **Steering Motor (L298N)**
  - IN1: GPIO 5
  - IN2: GPIO 6
  - ENB: GPIO 13 (PWM)

### Camera
- Raspberry Pi Camera Module 2
- Resolution: 640x480
- Frame Rate: 30 FPS

## 📁 Project Structure

```
├── rpi.py          # Main control loop and decision making
├── vision.py       # Computer vision processing
└── control.py      # Motor control and GPIO management
```

## 🔧 Configuration

### Vision Parameters
- HSV color ranges for path detection
- Block detection thresholds
- Wall detection parameters

### Control Parameters
- PWM frequency: 100 Hz
- Maximum steering angle: 30 degrees
- Frame processing rate: 30 FPS

## 🚀 Usage

1. Connect the hardware components as specified
2. Install required dependencies
3. Run the main program:
   ```bash
   python rpi.py
   ```

## 🎯 Features in Detail

### Vision System
- **Path Detection**: Uses HSV color segmentation to detect orange and blue lines
- **Wall Detection**: Identifies black walls and calculates their angle
- **Block Detection**: Recognizes colored blocks (red, green, blue, yellow)

### Control System
- **Priority-based Navigation**:
  1. Wall avoidance
  2. Obstacle avoidance
  3. Corner handling
  4. Default straight path

- **Wall Angle Override**:
  - Configurable override rules
  - Time-based or angle-based correction
  - Automatic recovery

## 🔍 Simulation Mode

The system includes a simulation mode that can be used for testing without actual hardware:
- Automatically activates when RPi.GPIO is not available
- Maintains motor state tracking
- Useful for development and testing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Safety Notes

- Always test in simulation mode first
- Ensure proper power supply for motors
- Keep clear of moving parts during operation
- Monitor system temperature during extended use
