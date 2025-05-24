import numpy as np
from OpenGL.GL import *
import stl
from stl import mesh
import math

class Robot:
    def __init__(self):
        # Load the STL file
        self.mesh = mesh.Mesh.from_file('car.stl')
        
        # Robot state
        self.position = [1.0, 0.01, 0.0]  # x, y (1cm above ground), z - Start on the right
        self.rotation = [0.0, -90.0, 0.0]  # pitch, yaw, roll - Start facing towards negative Z
        self.velocity = [0.0, 0.0, 0.0]   # velocity vector
        self.current_speed = 0.0
        
        # Robot parameters
        self.max_speed = 1.0  # meters per second
        self.max_turn_angle = 45.0  # degrees
        self.acceleration = 2.0  # meters per second squared
        self.turn_rate = 90.0  # degrees per second
        
        # Trajectory tracking
        self.trajectory = []  # List to store position history
        self.trajectory_spacing = 0.1  # Minimum distance between trajectory points
        self.last_trajectory_point = None  # Last recorded position
        
    def set_parameters(self, max_speed=None, max_turn_angle=None, 
                      acceleration=None, turn_rate=None):
        """Update robot parameters"""
        if max_speed is not None:
            self.max_speed = max_speed
        if max_turn_angle is not None:
            self.max_turn_angle = max_turn_angle
        if acceleration is not None:
            self.acceleration = acceleration
        if turn_rate is not None:
            self.turn_rate = turn_rate
            
    def update(self, dt, forward_input, turn_input):
        """Update robot state based on inputs"""
        # Update speed based on forward input
        target_speed = forward_input * self.max_speed
        speed_diff = target_speed - self.current_speed
        if abs(speed_diff) > self.acceleration * dt:
            self.current_speed += self.acceleration * dt * (1 if speed_diff > 0 else -1)
        else:
            self.current_speed = target_speed
            
        # Update turn angle based on turn input - No longer needed
        # target_angle = turn_input * self.max_turn_angle
        # angle_diff = target_angle - self.turn_angle
        # max_angle_change = self.turn_rate * dt
        # if abs(angle_diff) > max_angle_change:
        #     self.turn_angle += max_angle_change * (1 if angle_diff > 0 else -1)
        # else:
        #     self.turn_angle = target_angle
            
        # Convert turn angle to radians for calculations - No longer needed
        # turn_rad = math.radians(self.turn_angle)
        heading_rad = math.radians(self.rotation[1])
        
        # Update position based on current speed and heading
        self.position[0] += self.current_speed * math.sin(heading_rad) * dt
        self.position[2] += self.current_speed * math.cos(heading_rad) * dt
        
        # Update heading based on turn input (interpreted as turn rate)
        # turn_input range is -1.0 to 1.0, scale by turn_rate
        # Invert turn_input so that negative values turn clockwise (right)
        actual_turn_rate = -turn_input * self.turn_rate # Degrees per second
        self.rotation[1] += actual_turn_rate * dt
        
        # Update trajectory
        self._update_trajectory()
        
    def _update_trajectory(self):
        """Update the robot's trajectory by adding new points when needed"""
        current_pos = (self.position[0], self.position[2])
        
        # Add first point or if we've moved far enough from last point
        if (self.last_trajectory_point is None or 
            self._distance(current_pos, self.last_trajectory_point) >= self.trajectory_spacing):
            self.trajectory.append(current_pos)
            self.last_trajectory_point = current_pos
            
    def _distance(self, pos1, pos2):
        """Calculate distance between two 2D points"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
    def clear_trajectory(self):
        """Clear the robot's trajectory history"""
        self.trajectory = []
        self.last_trajectory_point = None
        
    def get_trajectory(self):
        """Return the robot's trajectory"""
        return self.trajectory
        
    def render(self):
        """Render the robot model"""
        # Set material properties for blue color
        glColor3f(0.0, 0.0, 1.0)  # Pure blue color
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.0, 0.0, 0.4, 1.0])  # Dark blue ambient
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.0, 0.0, 0.8, 1.0])  # Medium blue diffuse
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.4, 0.4, 1.0, 1.0])  # Light blue specular
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)  # Slightly more shiny
        
        # --- Draw Robot Local Axes (before model transformations) ---
        # Small axes (length 0.1) to show robot orientation
        self.draw_axes(length=0.1)
        # --- End Robot Axes ---

        # --- Render the Mesh (with isolated transformations) ---
        glPushMatrix() # Isolate model transformations
        try:
            # Apply initial rotation to lay the model flat
            glRotatef(-90, 1, 0, 0)  # Rotate -90 degrees around X axis to lay flat
            
            # Scale the model to appropriate size (assuming STL is in mm)
            glScalef(0.002, 0.002, 0.002)  # Doubled from original 0.001
            
            # Render the mesh
            glBegin(GL_TRIANGLES)
            if hasattr(self.mesh, 'vectors'): # Check if mesh loaded correctly
                for triangle in self.mesh.vectors:
                    # Calculate normal for the triangle
                    v1 = triangle[1] - triangle[0]
                    v2 = triangle[2] - triangle[0]
                    # Ensure normal calculation is robust against zero vectors
                    norm = np.linalg.norm(np.cross(v1, v2))
                    if norm > 1e-6:
                         normal = np.cross(v1, v2) / norm
                         glNormal3fv(normal)
                    else: # Use a default normal if triangle is degenerate
                         glNormal3f(0.0, 1.0, 0.0) 
                         
                    for vertex in triangle:
                        glVertex3fv(vertex)
            glEnd()
        finally:
             glPopMatrix() # Restore state after model transformations
        # --- End Mesh Rendering ---
        
        # Render camera visualization (now in correct robot local frame)
        self.render_camera_visualization()
        
    def render_camera_visualization(self):
        """Render camera direction arrow and field of view to match CameraSim"""
        # --- Match CameraSim parameters ---
        camera_height = 0.05  # Lowered height from 0.3 for visualization
        camera_forward = 0.0 # Use the same forward offset as in CameraSim (0)
        camera_tilt = -45    # Use the same tilt as in CameraSim (but tilt is ignored below for visualization)
        
        # FOV parameters 
        fov = 60  
        view_distance = 0.8 
        arrow_length = 0.15
        # --- End Parameters ---
        
        glPushAttrib(GL_LIGHTING_BIT | GL_LINE_BIT | GL_ENABLE_BIT)
        glDisable(GL_LIGHTING) # Disable lighting for visualization primitives
        glPushMatrix()

        # 1. Translate to the camera's position relative to the robot origin.
        #    Robot model Z points forward, Y points up. Camera is 0.3 up.
        glTranslatef(0.0, camera_height, 0.0)

        # 2. Apply the camera tilt rotation around the robot's X-axis.
        # --- REMOVED this line to make visualization point horizontally forward ---
        # glRotatef(camera_tilt, 1, 0, 0) 
        # --- 
        
        # --- Draw Camera Local Axes --- 
        # Draw axes here to show the camera's coordinate system (now horizontal)
        self.draw_axes(length=0.05) # Smaller axes for camera
        # --- End Camera Axes ---

        # The current local +Z axis now represents the camera's viewing direction.
        # We will draw the arrow and FOV cone along this axis.

        # --- Draw Red Direction Arrow --- 
        glColor3f(1.0, 0.0, 0.0) # Red
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0) # Start at camera position (after translation & rotation)
        glVertex3f(0, 0, arrow_length) # Extend along the local Z-axis (viewing direction)
        glEnd()
        
        # Arrow head (simple triangle pointing along +Z)
        head_length = 0.05
        head_width = 0.02
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, arrow_length) # Tip
        glVertex3f(-head_width, 0, arrow_length - head_length) # Base left
        glVertex3f(head_width, 0, arrow_length - head_length) # Base right
        glEnd()
        # --- End Arrow ---
        
        # --- Draw FOV Visualization (Yellow, Semi-transparent) ---
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Calculate FOV corners at view_distance along the local Z axis
        half_fov_rad = math.radians(fov / 2)
        corner_x = view_distance * math.tan(half_fov_rad)
        corner_z = view_distance
        
        glColor4f(1.0, 1.0, 0.0, 0.3)  # Yellow with alpha
        glLineWidth(1.0) 
        
        # Draw FOV polygon representing the base of the pyramid
        glBegin(GL_TRIANGLE_FAN) 
        glVertex3f(0, 0, 0) # Apex (camera position)
        glVertex3f(-corner_x, 0, corner_z) # Far left 
        glVertex3f(corner_x, 0, corner_z)  # Far right
        # Add intermediate points for a smoother cone base if desired
        # For simplicity, a triangle fan base is used here
        glEnd()

        # Draw lines outlining the FOV pyramid
        glLineWidth(1.5) 
        glColor4f(1.0, 1.0, 0.0, 0.5) # Slightly less transparent outline
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(-corner_x, 0, corner_z)
        
        glVertex3f(0, 0, 0)
        glVertex3f(corner_x, 0, corner_z)

        # Line connecting the base corners
        glVertex3f(-corner_x, 0, corner_z)
        glVertex3f(corner_x, 0, corner_z)
        glEnd()
        # --- End FOV ---
        
        glPopMatrix()
        glPopAttrib() # Restores lighting state etc.
        
    def get_state(self):
        """Return current robot state"""
        return {
            'position': self.position,
            'rotation': self.rotation,
            'speed': self.current_speed,
            # 'turn_angle': self.turn_angle # Removed
        } 

    # Helper method to draw axes (copied from Viewer)
    def draw_axes(self, length=1.0):
        """Draw X (red), Y (green), Z (blue) axes"""
        glPushAttrib(GL_LINE_BIT | GL_ENABLE_BIT)
        # Assuming lighting is already disabled by caller if needed
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # X Axis (Red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(length, 0.0, 0.0)
        # Y Axis (Green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, length, 0.0)
        # Z Axis (Blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, length)
        glEnd()
        glPopAttrib() 

    def get_length_x(self):
        """Return the robot's x-dimension (length) in meters, accounting for STL scaling."""
        # STL is in mm, scaled by 0.002 in render()
        min_x = np.min(self.mesh.vectors[:,:,0])
        max_x = np.max(self.mesh.vectors[:,:,0])
        length_mm = max_x - min_x
        length_m = length_mm * 0.002  # Apply scale
        return length_m 