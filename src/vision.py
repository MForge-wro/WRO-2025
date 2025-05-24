import numpy as np
import cv2

# HSV Color Ranges for path and block detection
PATH_ROBOT_HSV_LOWER = np.array([50, 120, 120])
PATH_ROBOT_HSV_UPPER = np.array([70, 255, 255])
PATH_TARGET_HSV_LOWER1 = np.array([0, 120, 120])
PATH_TARGET_HSV_UPPER1 = np.array([10, 255, 255])
PATH_TARGET_HSV_LOWER2 = np.array([170, 120, 120])
PATH_TARGET_HSV_UPPER2 = np.array([180, 255, 255])
ORANGE_HSV_LOWER = np.array([8, 60, 60])
ORANGE_HSV_UPPER = np.array([25, 255, 255])
BLUE_HSV_LOWER = np.array([85, 40, 30])
BLUE_HSV_UPPER = np.array([130, 255, 255])
# For block detection:
# These constants define the HSV ranges for colors AS SEEN BY THE CAMERA.
# The 'detect_blocks' function then maps these to the REAL-WORLD block colors.

# Camera sees RED (used when a real BLUE object appears RED)
CAMERA_RED_LOWER1 = np.array([0, 120, 70])
CAMERA_RED_UPPER1 = np.array([10, 255, 255])
CAMERA_RED_LOWER2 = np.array([160, 120, 70])
CAMERA_RED_UPPER2 = np.array([180, 255, 255])

# Camera sees YELLOW (used when a real BLUE object appears YELLOW)
CAMERA_YELLOW_LOWER = np.array([20, 100, 100])
CAMERA_YELLOW_UPPER = np.array([40, 255, 255])

# Camera sees BLUE (used when a real RED object appears BLUE)
CAMERA_BLUE_LOWER = np.array([100, 150, 70]) # S min increased for robustness
CAMERA_BLUE_UPPER = np.array([140, 255, 255])

# Camera sees GREEN (used when a real GREEN object appears GREEN)
CAMERA_GREEN_LOWER = np.array([40, 80, 50])
CAMERA_GREEN_UPPER = np.array([80, 255, 255])

# For 'orange_block' (real LIGHT BLUE/CYAN object)
# User has not recently specified how this appears to the camera.
# Keeping previous values that detect light blue/cyan directly.
# If this block needs detection, specify its camera appearance.
LOWER_ORANGE_DIRECT = np.array([85, 100, 100]) # For real Light Blue/Cyan
UPPER_ORANGE_DIRECT = np.array([99, 255, 255]) # For real Light Blue/Cyan

# For block detection:
# Remap HSV ranges for real-world color perception
# 'red' now detects blue objects
lower_red1 = np.array([100, 100, 70])
upper_red1 = np.array([130, 255, 255])
lower_red2 = np.array([0, 0, 0])
upper_red2 = np.array([0, 0, 0])
# 'blue' now detects red objects
lower_blue1 = np.array([0, 90, 40])
upper_blue1 = np.array([10, 255, 255])
lower_blue2 = np.array([160, 90, 40])
upper_blue2 = np.array([180, 255, 255])
# 'orange' now detects light blue/cyan
lower_orange = np.array([85, 100, 100])
upper_orange = np.array([99, 255, 255])
# 'green' stays the same
lower_green = np.array([40, 80, 50])
upper_green = np.array([80, 255, 255])

# --- HSV Color Definitions for Block Detection (Colors as SEEN BY THE CAMERA) ---
# These ranges define what the camera perceives. The detect_blocks function
# then maps these perceived colors to the appropriate 'block_name' which
# corresponds to the REAL-WORLD color of the object.

# For objects that appear RED to the camera (real RED)
HSC_SEEN_RED_LOWER1 = np.array([0, 100, 100])
HSC_SEEN_RED_UPPER1 = np.array([10, 255, 255])
HSC_SEEN_RED_LOWER2 = np.array([160, 100, 100])
HSC_SEEN_RED_UPPER2 = np.array([180, 255, 255])

# For objects that appear GREEN to the camera (real GREEN)
HSC_SEEN_GREEN_LOWER = np.array([40, 70, 70])
HSC_SEEN_GREEN_UPPER = np.array([80, 255, 255])

# For objects that appear BLUE to the camera (real BLUE)
HSC_SEEN_BLUE_LOWER = np.array([100, 150, 70])
HSC_SEEN_BLUE_UPPER = np.array([130, 255, 255])

# For objects that appear YELLOW to the camera (real YELLOW)
HSC_SEEN_YELLOW_LOWER = np.array([20, 100, 100])
HSC_SEEN_YELLOW_UPPER = np.array([35, 255, 255])


def detect_blocks(image):
    """
    Detects red, green, blue, and yellow blocks in the image (expects BGR)
    Returns list of detected blocks with their positions in the image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Mask for RED objects
    red_mask1 = cv2.inRange(hsv, HSC_SEEN_RED_LOWER1, HSC_SEEN_RED_UPPER1)
    red_mask2 = cv2.inRange(hsv, HSC_SEEN_RED_LOWER2, HSC_SEEN_RED_UPPER2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    # Mask for GREEN objects
    green_mask = cv2.inRange(hsv, HSC_SEEN_GREEN_LOWER, HSC_SEEN_GREEN_UPPER)
    # Mask for BLUE objects
    blue_mask = cv2.inRange(hsv, HSC_SEEN_BLUE_LOWER, HSC_SEEN_BLUE_UPPER)
    # Mask for YELLOW objects
    yellow_mask = cv2.inRange(hsv, HSC_SEEN_YELLOW_LOWER, HSC_SEEN_YELLOW_UPPER)

    detected_blocks = []
    for mask, color_name in [
        (red_mask, 'red_block'),      # Real RED object
        (green_mask, 'green_block'),  # Real GREEN object
        (blue_mask, 'blue_block'),    # Real BLUE object
        (yellow_mask, 'orange_block') # Real YELLOW object
    ]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w//2
                center_y = y + h//2
                detected_blocks.append({
                    'color': color_name,
                    'position': (center_x, center_y),
                    'size': (w, h),
                    'area': cv2.contourArea(contour)
                })
    return detected_blocks


def detect_corners(image_bgr, draw_overlay=True):
    """
    Detect orange and blue lines and return their order for steering suggestion.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    orange_mask = cv2.inRange(hsv, ORANGE_HSV_LOWER, ORANGE_HSV_UPPER)
    blue_mask = cv2.inRange(hsv, BLUE_HSV_LOWER, BLUE_HSV_UPPER)
    h, w = image_bgr.shape[:2]
    bottom_y = h - 1
    def get_line_points(mask, color_bgr):
        points = []
        for x in range(w):
            if mask[bottom_y, x] > 0:
                points.append((x, bottom_y))
        if len(points) < 2:
            for y in range(h-2, h-10, -1):
                for x in range(w):
                    if mask[y, x] > 0:
                        points.append((x, y))
                if len(points) >= 2:
                    break
        if len(points) >= 2:
            points = sorted(points, key=lambda pt: pt[0])
            pt1, pt2 = points[0], points[-1]
            if draw_overlay:
                cv2.circle(image_bgr, pt1, 6, color_bgr, -1)
                cv2.circle(image_bgr, pt2, 6, color_bgr, -1)
                cv2.line(image_bgr, pt1, pt2, color_bgr, 2)
            return pt1, pt2
        return None, None
    orange_pt1, orange_pt2 = get_line_points(orange_mask, (0,140,255))
    blue_pt1, blue_pt2 = get_line_points(blue_mask, (255,0,0))
    def line_angle(pt1, pt2):
        if pt1 is None or pt2 is None:
            return None
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        angle = np.arctan2(dy, dx)
        angle_deg = np.degrees(angle)
        return abs(angle_deg)
    orange_angle = line_angle(orange_pt1, orange_pt2)
    blue_angle = line_angle(blue_pt1, blue_pt2)
    steer = None
    steer_reason = None
    if orange_angle is not None and blue_angle is not None:
        if blue_angle < orange_angle:
            steer = 'left'
            steer_reason = f'blue_angle({blue_angle:.1f}) < orange_angle({orange_angle:.1f})'
        elif orange_angle < blue_angle:
            steer = 'right'
            steer_reason = f'orange_angle({orange_angle:.1f}) < blue_angle({blue_angle:.1f})'
        else:
            steer = None
            steer_reason = 'angles equal'
    return {
        'image': image_bgr,
        'label': steer,
        'label_pos': (orange_pt1, orange_pt2, blue_pt1, blue_pt2),
        'steer': steer,
        'steer_reason': steer_reason,
        'orange_angle': orange_angle,
        'blue_angle': blue_angle,
        'orange_pts': (orange_pt1, orange_pt2),
        'blue_pts': (blue_pt1, blue_pt2)
    }


def detect_wall_and_angle(image_bgr, visualize=False):
    """
    Detects the proximity and angle of a black wall in the camera image.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, black_mask = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {'wall_y': None, 'wall_angle': None, 'steer': 'straight', 'viz': None} if visualize else {'wall_y': None, 'wall_angle': None, 'steer': 'straight'}
    largest = max(contours, key=cv2.contourArea)
    ys = largest[:,0,1]
    xs = largest[:,0,0]
    wall_points = {}
    for x, y in zip(xs, ys):
        if x not in wall_points or y < wall_points[x]:
            wall_points[x] = y
    if len(wall_points) < 2:
        return {'wall_y': None, 'wall_angle': None, 'steer': 'straight', 'viz': None} if visualize else {'wall_y': None, 'wall_angle': None, 'steer': 'straight'}
    edge_pts = np.array([[x, wall_points[x]] for x in sorted(wall_points.keys())])
    left_pt = edge_pts[0]
    right_pt = edge_pts[-1]
    if left_pt[1] < right_pt[1]:
        steer = 'right'
        steer_reason = 'left_pt lower than right_pt'
    elif right_pt[1] < left_pt[1]:
        steer = 'left'
        steer_reason = 'right_pt lower than left_pt'
    else:
        steer = 'straight'
        steer_reason = 'edge y equal'
    [vx, vy, x0, y0] = cv2.fitLine(edge_pts, cv2.DIST_L2, 0, 0.01, 0.01)
    angle_rad = np.arctan2(vy, vx)
    angle_deg = np.degrees(angle_rad)[0]
    wall_y = int(np.mean(edge_pts[:,1]))
    if visualize:
        viz = {
            'edge_pts': edge_pts,
            'line': ((int(x0 - vx * 200), int(y0 - vy * 200)), (int(x0 + vx * 200), int(y0 + vy * 200))),
            'steer': steer,
            'wall_y': wall_y,
            'angle_deg': angle_deg,
            'left_pt': left_pt,
            'right_pt': right_pt,
            'steer_reason': steer_reason
        }
        return {'wall_y': wall_y, 'wall_angle': angle_deg, 'steer': steer, 'viz': viz}
    else:
        return {'wall_y': wall_y, 'wall_angle': angle_deg, 'steer': steer, 'left_pt': left_pt, 'right_pt': right_pt, 'steer_reason': steer_reason} 