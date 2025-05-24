# Raspberry Pi Robot Simulator

A comprehensive simulation environment for testing and developing Raspberry Pi robot control systems. This simulator provides a 3D visualization of the robot's environment, camera simulation, and control system testing capabilities.

## 🚀 Features

- **3D Visualization**: OpenGL-based visualization of the robot and environment
- **Camera Simulation**: Simulated camera view with color detection and path following
- **Physics Simulation**: Realistic movement and collision detection
- **Control System Testing**: Test control algorithms without physical hardware
- **Path Planning**: Visualize and test navigation paths
- **Block Detection**: Simulate detection of colored blocks and obstacles
- **Wall Following**: Test wall detection and following algorithms

## 📋 Requirements

```bash
numpy>=1.19.0
opencv-python>=4.5.0
PyOpenGL>=3.1.0
pygame>=2.0.0
numpy-stl>=2.16.0
pillow>=8.0.0
```

## 🏗️ Project Structure

- `main.py`: Main simulation loop and control logic
- `camera_sim.py`: Camera simulation and image processing
- `field.py`: Environment and obstacle generation
- `robot.py`: Robot model and movement simulation
- `viewer.py`: 3D visualization and OpenGL rendering
- `vision.py`: Computer vision algorithms and color detection
- `logic.py`: Control system logic and decision making

## 🎮 Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulator:
```bash
python main.py
```

## 🎯 Key Components

### Camera Simulation (`camera_sim.py`)
- Simulates robot's camera view
- Processes images for block detection
- Handles path detection and wall following
- Provides color-based object detection

### Field Environment (`field.py`)
- Generates the simulation environment
- Manages obstacles and blocks
- Handles wall generation and placement
- Controls randomization of elements

### Robot Control (`robot.py`)
- Simulates robot movement and physics
- Handles trajectory tracking
- Manages robot state and parameters
- Provides visualization of robot model

### Visualization (`viewer.py`)
- Renders 3D environment using OpenGL
- Handles camera view and perspective
- Manages textures and lighting
- Provides debug visualization

### Vision Processing (`vision.py`)
- Implements color detection algorithms
- Handles block and line detection
- Processes camera images
- Provides steering suggestions

## 🛠️ Control System

The simulator includes a sophisticated control system with multiple priority levels:

1. Wall Angle Override
2. Strict Wall Rectangle
3. Obstacle Avoidance
4. Corner Steering
5. Wall Following
6. Strategic Object Bias
7. Safety Rules

## 📊 Visualization Features

- Real-time camera view
- Block detection visualization
- Path following indicators
- Wall detection overlays
- Steering decision visualization
- Debug information display

## 🔧 Configuration

The simulator can be configured through various parameters:

- Camera resolution and FOV
- Robot movement parameters
- Field dimensions and layout
- Color detection thresholds
- Control system priorities

## 🎨 Color Detection

The simulator supports detection of:
- Red and green blocks
- Orange and blue lines
- Black walls
- Magenta parking indicators

## ⚠️ Notes

- The simulator is designed for testing control algorithms
- All measurements are in meters
- Camera simulation includes realistic perspective
- Physics simulation includes acceleration and turning constraints

## 🔍 Troubleshooting

Common issues and solutions:

1. **OpenGL Errors**
   - Ensure graphics drivers are up to date
   - Check OpenGL version compatibility

2. **Performance Issues**
   - Reduce camera resolution
   - Disable debug visualization
   - Adjust simulation update rate

3. **Color Detection Issues**
   - Adjust HSV thresholds in vision.py
   - Check lighting conditions in simulation
   - Verify camera parameters

## 📝 License

This project is licensed under the same terms as the main Raspberry Pi Robot Control System.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
