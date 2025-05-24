import time
import cv2
import numpy as np
import control
from vision import detect_blocks, detect_corners, detect_wall_and_angle
from picamera2 import Picamera2

# --- Parameters ---
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DT = 1/30.0  # 30 FPS
SHOW_CAMERA_FEED = False  # Set to True to display camera feed window

# --- WALL ANGLE OVERRIDE RULE CONFIGURATION ---
# Options: 'wall', 'time', 'none'
WALL_ANGLE_OVERRIDE_RULE = 'none'  # Change to 'time' or 'none' as needed

# --- Helper functions from main.py (parabola, etc.) ---
def is_inside_parabola(x, y, h, k, a, threshold=0):
    parabola_y = a * (x - h) ** 2 + k
    return y > parabola_y + threshold

def any_thick_line_point_inside_parabola(pt1, pt2, h, k, a, threshold=2, thickness=8, num_samples=20):
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    length = np.hypot(dx, dy)
    if length == 0:
        return is_inside_parabola(pt1[0], pt1[1], h, k, a, threshold)
    perp_dx = -dy / length
    perp_dy = dx / length
    for i in range(num_samples + 1):
        t = i / num_samples
        x = pt1[0] * (1 - t) + pt2[0] * t
        y = pt1[1] * (1 - t) + pt2[1] * t
        for offset in np.linspace(-thickness/2, thickness/2, int(thickness)+1):
            px = x + perp_dx * offset
            py = y + perp_dy * offset
            if is_inside_parabola(px, py, h, k, a, threshold):
                return True
    return False

def control_logic(wall_info, green_blocks, red_blocks, orange_angle, blue_angle, image_width, image_height, orange_pts=None, blue_pts=None, h_parab=None, k_parab=None, a_parab=None):
    # 1. Wall avoidance (highest priority)
    if wall_info.get('wall_y') is not None and wall_info['wall_y'] < image_height * 0.4:
        wall_angle = wall_info.get('wall_angle')
        if wall_angle is not None:
            if wall_angle > 0:
                return 1.0, f'Wall close, wall_angle={wall_angle:.2f} > 0, steer right to increase angle'
            elif wall_angle < 0:
                return -1.0, f'Wall close, wall_angle={wall_angle:.2f} < 0, steer left to decrease angle'
            else:
                return -1.0, 'Wall close, wall_angle=0, steer left for safety'
        return -1.0, 'Wall close, always steer left for safety'
    # 2. Obstacle avoidance (gentler turns)
    closest_green = max(green_blocks, key=lambda b: b['y'], default=None)
    closest_red = max(red_blocks, key=lambda b: b['y'], default=None)
    if closest_green and closest_green['y'] > image_height * 0.5:
        steer = max(-0.4, -0.5 * ((closest_green['y'] - image_height * 0.5) / (image_height * 0.5)))
        return steer, 'Avoid green: steer left (gentle, capped)'
    if closest_red and closest_red['y'] > image_height * 0.6:
        steer = min(0.4, 0.5 * ((closest_red['y'] - image_height * 0.6) / (image_height * 0.4)))
        return steer, 'Avoid red: steer right (gentle, capped)'
    # 3. Corner handling: react if EITHER line is inside the parabola
    if orange_angle is not None and blue_angle is not None and orange_pts and blue_pts and h_parab is not None and k_parab is not None and a_parab is not None:
        orange_in = False
        blue_in = False
        if orange_pts and all(pt is not None for pt in orange_pts):
            orange_in = any_thick_line_point_inside_parabola(orange_pts[0], orange_pts[1], h_parab, k_parab, a_parab, threshold=2, thickness=8, num_samples=20)
        if blue_pts and all(pt is not None for pt in blue_pts):
            blue_in = any_thick_line_point_inside_parabola(blue_pts[0], blue_pts[1], h_parab, k_parab, a_parab, threshold=2, thickness=8, num_samples=20)
        # Prioritize orange if both are inside
        if orange_in:
            if orange_angle < 0:
                return -1.0, 'Corner: any orange line point (thick) inside parabola with negative angle, turn left (CCW)'
            elif orange_angle > 0:
                return 1.0, 'Corner: any orange line point (thick) inside parabola with positive angle, turn right (CW)'
        elif blue_in:
            if blue_angle < 0:
                return -1.0, 'Corner: any blue line point (thick) inside parabola with negative angle, turn left (CCW)'
            elif blue_angle > 0:
                return 1.0, 'Corner: any blue line point (thick) inside parabola with positive angle, turn right (CW)'
    # 4. Default: go straight
    return 0.0, 'Default: go straight'

def draw_parabola(image, h, k, a, color=(255,0,255), thickness=2, num_points=200):
    height, width = image.shape[:2]
    pts = []
    for x in np.linspace(0, width-1, num_points):
        y = a * (x - h) ** 2 + k
        if 0 <= y < height:
            pts.append((int(x), int(y)))
    if len(pts) > 1:
        for i in range(len(pts)-1):
            cv2.line(image, pts[i], pts[i+1], color, thickness)
    return image

def main():
    print("[INFO] Starting Raspberry Pi robot main loop...")
    try:
        control.setup_gpio()
        print("[INFO] GPIO initialized.")
    except Exception as e:
        print(f"Warning: Failed to initialize GPIO: {e}")
        print("Running in simulation mode (no actual motor control)")

    # Initialize PiCamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (FRAME_WIDTH, FRAME_HEIGHT)}))
    picam2.start()
    time.sleep(2)  # Let camera warm up

    h_parab = FRAME_WIDTH // 2
    k_parab = int(FRAME_HEIGHT * 0.55)
    a_parab = 0.0011

    print("[INFO] Main loop running. Press Ctrl+C to quit.")
    try:
        while True:
            start_time = time.time()
            frame = picam2.capture_array()
            # Convert from RGB to BGR for OpenCV/vision
            # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # TEST: Remove this conversion
            frame_bgr = frame # TEST: Assume frame is already BGR or test direct usage

            # --- Vision processing ---
            wall_info = detect_wall_and_angle(frame_bgr, visualize=False)
            corner_info = detect_corners(frame_bgr, draw_overlay=False)
            blocks = detect_blocks(frame_bgr)

            # Debug: Print detected blocks
            # print("Detected blocks:", blocks)

            # --- Draw bounding boxes for detected blocks (green/red) ---
            # MODIFIED FOR DEBUGGING - DRAW ALL BLOCKS WITH LABELS
            for b in blocks:
                # Determine color for bounding box based on detected block name
                box_color_bgr = (255, 255, 255) # Default to white for unrecognized blocks
                label_text = b['color']

                if b['color'] == 'red_block':      # Real BLUE object
                    box_color_bgr = (255, 0, 0)    # Blue box
                elif b['color'] == 'green_block':  # Real GREEN object
                    box_color_bgr = (0, 255, 0)    # Green box
                elif b['color'] == 'orange_block': # Real YELLOW object
                    box_color_bgr = (0, 255, 255)  # Yellow box
                elif b['color'] == 'blue_block':   # Real RED object
                    box_color_bgr = (0, 0, 255)    # Red box

                x, y = b['position']
                w, h_ = b['size']
                top_left = (x - w//2, y - h_//2)
                bottom_right = (x + w//2, y + h_//2)
                cv2.rectangle(frame_bgr, top_left, bottom_right, box_color_bgr, 2)
                cv2.putText(frame_bgr, label_text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color_bgr, 1)

            # --- Use the same exclusion rectangle as simulation (main.py) ---
            rect_width = 520
            rect_height = 120
            center_x_img = FRAME_WIDTH // 2
            rect_center_x = center_x_img
            rect_center_y = FRAME_HEIGHT - 1 - (rect_height // 2) - 10
            rect_left = rect_center_x - rect_width // 2
            rect_top = rect_center_y - rect_height // 2
            rect_right = rect_center_x + rect_width // 2
            rect_bottom = rect_center_y + rect_height // 2
            cv2.rectangle(frame_bgr, (rect_left, rect_top), (rect_right, rect_bottom), (0, 255, 255), 2)

            # --- Draw parabola overlay (same as simulation) ---
            frame_bgr = draw_parabola(frame_bgr, h_parab, k_parab, a_parab, color=(255,0,255), thickness=2)

            # Prepare block lists for control logic
            green_blocks = [{'x': b['position'][0], 'y': b['position'][1]} for b in blocks if b['color'] == 'green_block']
            red_blocks = [{'x': b['position'][0], 'y': b['position'][1]} for b in blocks if b['color'] == 'red_block']

            orange_angle = corner_info.get('orange_angle')
            blue_angle = corner_info.get('blue_angle')
            orange_pts = corner_info.get('orange_pts')
            blue_pts = corner_info.get('blue_pts')

            # --- WALL ANGLE OVERRIDE RULE (HIGHEST PRIORITY, FIRST CHECK, CONFIGURABLE) ---
            if not hasattr(main, 'wall_override_direction'):
                main.wall_override_direction = 0
            if not hasattr(main, 'wall_override_timer'):
                main.wall_override_timer = 0
            if not hasattr(main, 'wall_override_phase'):
                main.wall_override_phase = None
            wall_override_triggered = False
            wall_angle = wall_info.get('wall_angle', 0)
            if WALL_ANGLE_OVERRIDE_RULE == 'wall':
                # Angle-based override (as before)
                if main.wall_override_direction != 0:
                    if main.wall_override_direction == -1 and wall_angle >= 5:
                        print(f"[DEBUG] WALL ANGLE OVERRIDE END: wall_angle={wall_angle:.2f} >= 5, stop steering left")
                        main.wall_override_direction = 0
                    elif main.wall_override_direction == 1 and wall_angle <= -5:
                        print(f"[DEBUG] WALL ANGLE OVERRIDE END: wall_angle={wall_angle:.2f} <= -5, stop steering right")
                        main.wall_override_direction = 0
                if main.wall_override_direction == 0:
                    if wall_angle < 0:
                        main.wall_override_direction = -1
                        print(f"[DEBUG] WALL ANGLE OVERRIDE TRIGGERED: wall_angle={wall_angle:.2f} < 0, steer left until >= 5")
                    elif wall_angle > 0:
                        main.wall_override_direction = 1
                        print(f"[DEBUG] WALL ANGLE OVERRIDE TRIGGERED: wall_angle={wall_angle:.2f} > 0, steer right until <= -5")
                if main.wall_override_direction != 0:
                    steer = main.wall_override_direction
                    print(f"[DEBUG] WALL ANGLE OVERRIDE ACTIVE: steer {'right' if steer > 0 else 'left'} (wall_angle={wall_angle:.2f})")
                    # Actuate robot for override
                    if steer < 0:
                        control.steer_left()
                        control.move_forward(40)
                        print("[ACTION] OVERRIDE: Steer LEFT")
                    else:
                        control.steer_right()
                        control.move_forward(40)
                        print("[ACTION] OVERRIDE: Steer RIGHT")
                    # Show camera frame with overlays (for debugging)
                    if SHOW_CAMERA_FEED:
                        cv2.imshow('Pi Camera View', frame_bgr)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    # Maintain loop timing
                    elapsed = time.time() - start_time
                    if elapsed < DT:
                        time.sleep(DT - elapsed)
                    continue
            elif WALL_ANGLE_OVERRIDE_RULE == 'time':
                # Time-based override: steer left/right for 2s, then opposite for 1s
                if main.wall_override_timer > 0:
                    steer = main.wall_override_direction
                    print(f"[DEBUG] WALL ANGLE TIME OVERRIDE ACTIVE: steer {'right' if steer > 0 else 'left'} (timer {main.wall_override_timer:.2f}s left, phase={main.wall_override_phase})")
                    if steer < 0:
                        control.steer_left()
                        control.move_forward(40)
                        print("[ACTION] TIME OVERRIDE: Steer LEFT")
                    else:
                        control.steer_right()
                        control.move_forward(40)
                        print("[ACTION] TIME OVERRIDE: Steer RIGHT")
                    main.wall_override_timer -= DT
                    if main.wall_override_timer <= 0 and main.wall_override_phase == 'first':
                        # Switch to opposite direction for 1s
                        main.wall_override_direction *= -1
                        main.wall_override_timer = 1.0
                        main.wall_override_phase = 'second'
                        print(f"[DEBUG] WALL ANGLE TIME OVERRIDE PHASE 2: steer {'right' if main.wall_override_direction > 0 else 'left'} for 1s")
                    elif main.wall_override_timer <= 0 and main.wall_override_phase == 'second':
                        print(f"[DEBUG] WALL ANGLE TIME OVERRIDE END")
                        main.wall_override_direction = 0
                        main.wall_override_phase = None
                    # Show camera frame with overlays (for debugging)
                    if SHOW_CAMERA_FEED:
                        cv2.imshow('Pi Camera View', frame_bgr)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    elapsed = time.time() - start_time
                    if elapsed < DT:
                        time.sleep(DT - elapsed)
                    continue
                if main.wall_override_direction == 0:
                    if wall_angle < 0:
                        main.wall_override_direction = -1
                        main.wall_override_timer = 2.0
                        main.wall_override_phase = 'first'
                        print(f"[DEBUG] WALL ANGLE TIME OVERRIDE TRIGGERED: wall_angle={wall_angle:.2f} < 0, steer left for 2s then right for 1s")
                    elif wall_angle > 0:
                        main.wall_override_direction = 1
                        main.wall_override_timer = 2.0
                        main.wall_override_phase = 'first'
                        print(f"[DEBUG] WALL ANGLE TIME OVERRIDE TRIGGERED: wall_angle={wall_angle:.2f} > 0, steer right for 2s then left for 1s")
            # If 'none', do nothing (no override)

            # --- Advanced control logic (priority system) ---
            steer, steer_reason = control_logic(
                wall_info, green_blocks, red_blocks, orange_angle, blue_angle,
                FRAME_WIDTH, FRAME_HEIGHT, orange_pts, blue_pts, h_parab, k_parab, a_parab
            )

            # --- Actuate robot ---
            if wall_info.get('wall_y') is not None and wall_info['wall_y'] > FRAME_HEIGHT * 0.9:
                control.stop_drive_motor()
                control.center_steering()
                print("[ACTION] STOP: Wall too close")
            else:
                if steer < -0.2:
                    control.steer_left()
                    control.move_forward(40)
                    print("[ACTION] Steer LEFT")
                elif steer > 0.2:
                    control.steer_right()
                    control.move_forward(40)
                    print("[ACTION] Steer RIGHT")
                else:
                    control.center_steering()
                    control.move_forward(50)
                    print("[ACTION] FORWARD")

            # --- Show camera frame with overlays (for debugging) ---
            if SHOW_CAMERA_FEED:
                cv2.imshow('Pi Camera View', frame_bgr)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # --- Maintain loop timing ---
            elapsed = time.time() - start_time
            if elapsed < DT:
                time.sleep(DT - elapsed)
    except KeyboardInterrupt:
        print("Loop interrupted by user.")
    finally:
        print("Cleaning up...")
        picam2.stop()
        if SHOW_CAMERA_FEED:
            cv2.destroyAllWindows()
        control.cleanup_gpio()

if __name__ == "__main__":
    main() 