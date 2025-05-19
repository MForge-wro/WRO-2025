# 🛠️ Robot Schematic Diagram

This repository contains the schematic diagram and system overview for a simple Raspberry Pi 4-powered robot. The design features two DC motors, camera input, and remote power management, making it ideal for basic robotics experiments and computer vision applications.

## 🔧 Hardware Components

- **2× DC Motors**
  - One motor for **steering**
  - One motor for **driving**

- **Motor Driver: L298N Dual H-Bridge**
  - Handles both motors
  - Controlled via GPIO pins from the Raspberry Pi

- **Power Supply**
  - **9V Battery** powers the motors through the L298N
  - An **On/Off toggle switch** is placed between the battery and L298N for motor control
  - **Raspberry Pi 4** is powered separately using a **USB-A to USB-C cable** connected to a power bank

- **Controller: Raspberry Pi 4**
  - Runs the robot's control logic
  - **Pi Camera** connected via the flat ribbon cable for vision tasks

## ⚡ Power Architecture

\`\`\`
[ 9V Battery ] 
     |
 [ ON/OFF Switch ]
     |
 [  L298N H-Bridge  ]
    /        \\
[DC Motor]  [DC Motor]

[Raspberry Pi 4] <-- [Power Bank via USB-A to USB-C]
       |
  [Pi Camera via CSI Port]
\`\`\`

## 🖼️ Circuit Diagram

You can find the full schematic/circuit diagram here:

👉 [**View Circuit Diagram**](#) *[HERE](https://app.cirkitdesigner.com/project/81746f89-3439-4385-bd1d-2ebd57a1eb00)*

