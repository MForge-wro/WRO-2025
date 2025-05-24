import time
import cv2
import control
from vision import detect_blocks, detect_corners, detect_wall_and_angle

# --- Main loop for Raspberry Pi robot ---
def main():
    # Initialize GPIO for robot control
    try:
        control.setup_gpio()
    except Exception as e:
        print(f"Warning: Failed to initialize GPIO: {e}")
        print("Running in simulation mode (no actual motor control)")

    # Open the Pi camera (or USB camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Starting main loop. Press 'q' to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break

            # --- Vision processing ---
            wall_info = detect_wall_and_angle(frame, visualize=True)
            corner_info = detect_corners(frame, draw_overlay=True)
            blocks = detect_blocks(frame)

            # --- Simple wall following logic ---
            steer = wall_info.get('steer', 'straight')
            wall_y = wall_info.get('wall_y', None)
            wall_y_threshold = 180  # Tune as needed (lower = wall closer)

            # Example: Stop if wall is too close, else steer
            if wall_y is not None and wall_y > wall_y_threshold:
                control.stop_drive_motor()
                control.center_steering()
                cv2.putText(frame, 'STOP: Wall too close', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            else:
                if steer == 'left':
                    control.steer_left()
                    control.move_forward(40)
                    cv2.putText(frame, 'Steer LEFT', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
                elif steer == 'right':
                    control.steer_right()
                    control.move_forward(40)
                    cv2.putText(frame, 'Steer RIGHT', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                else:
                    control.center_steering()
                    control.move_forward(50)
                    cv2.putText(frame, 'FORWARD', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            # --- Draw block detections ---
            for block in blocks:
                # Set box color based on real-world color mapping
                box_color_bgr = (255, 255, 255)  # default white
                if block['color'] == 'red_block':      # Real BLUE
                    box_color_bgr = (255, 0, 0)
                elif block['color'] == 'green_block':  # Real GREEN
                    box_color_bgr = (0, 255, 0)
                elif block['color'] == 'orange_block': # Real YELLOW
                    box_color_bgr = (0, 255, 255)
                elif block['color'] == 'blue_block':   # Real RED
                    box_color_bgr = (0, 0, 255)
                pos = block['position']
                size = block['size']
                cv2.rectangle(frame, (pos[0]-size[0]//2, pos[1]-size[1]//2), (pos[0]+size[0]//2, pos[1]+size[1]//2), box_color_bgr, 2)
                cv2.putText(frame, block['color'], (pos[0]-size[0]//2, pos[1]-size[1]//2-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color_bgr, 1)

            # --- Show camera frame with overlays ---
            cv2.imshow('Pi Camera View', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
    except KeyboardInterrupt:
        print("Loop interrupted by user.")
    finally:
        print("Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        control.cleanup_gpio()

if __name__ == "__main__":
    main() 