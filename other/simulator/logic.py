import cv2
import time

# --- Minimal test loop for robot movement ---
def main_test_loop():
    import control
    try:
        robot_controller = control
        robot_controller.setup_gpio()
    except Exception as e:
        print(f"CRITICAL: Failed to initialize control.py GPIO: {e}")
        print("Running in simulation mode (no actual motor control).")
        robot_controller = control

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        if hasattr(robot_controller, 'cleanup_gpio'):
            robot_controller.cleanup_gpio()
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Starting minimal test loop. Press 'q' to quit.")
    ACTIONS = [
        ("forward", 2.0),
        ("backward", 2.0),
        ("left", 2.0),
        ("right", 2.0),
    ]
    action_idx = 0
    action_start_time = time.time()
    last_action = None
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break
            action, duration = ACTIONS[action_idx]
            elapsed = time.time() - action_start_time
            if elapsed > duration:
                if last_action in ("left", "right"):
                    robot_controller.center_steering()
                    try:
                        import control as real_control
                        real_control.steer_left.last_direction = 'center'
                    except Exception:
                        pass
                action_idx = (action_idx + 1) % len(ACTIONS)
                action_start_time = time.time()
                action, duration = ACTIONS[action_idx]
            if action == "forward":
                robot_controller.center_steering()
                try:
                    import control as real_control
                    real_control.steer_left.last_direction = 'center'
                except Exception:
                    pass
                robot_controller.move_forward(50)
                last_action = "forward"
            elif action == "backward":
                robot_controller.center_steering()
                try:
                    import control as real_control
                    real_control.steer_left.last_direction = 'center'
                except Exception:
                    pass
                robot_controller.move_backward(50)
                last_action = "backward"
            elif action == "left":
                robot_controller.stop_drive_motor()
                robot_controller.steer_left()
                last_action = "left"
            elif action == "right":
                robot_controller.stop_drive_motor()
                robot_controller.steer_right()
                last_action = "right"
            cv2.putText(frame, f"TEST: {action}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('Robot View', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
                robot_controller.stop_drive_motor()
                robot_controller.center_steering()
    except KeyboardInterrupt:
        print("Loop interrupted by user.")
    finally:
        print("Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        if hasattr(robot_controller, 'cleanup_gpio'):
             robot_controller.cleanup_gpio()
        print("Exited.")

# Only keep the minimal test loop. Remove all other logic, classes, and computer vision code from this file.

if __name__ == '__main__':
    main_test_loop() 