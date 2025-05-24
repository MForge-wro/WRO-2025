import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
import math

class Viewer:
    def __init__(self, width=800, height=600):
        pygame.init()
        pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
        
        # Basic OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.8, 0.8, 0.8, 1.0)  # Set background color to light gray
        
        # Set up lighting for top view
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 0.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        
        # Initialize view parameters
        self.width = width
        self.height = height
        
        # Camera parameters
        self.camera_distance = 5.0
        self.camera_rotation_x = 30.0  # Pitch angle in degrees
        self.camera_rotation_y = 180.0   # Yaw angle in degrees (reversed)
        self.camera_position = [0.0, 0.0, 0.0]  # Camera target (for panning)
        
        # Mouse control parameters
        self.mouse_pressed = False
        self.right_pressed = False
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.3
        self.pan_sensitivity = 0.01
        self.zoom_sensitivity = 0.2
        
        self.setup_camera()
        
        # Load ground texture
        self.ground_texture = self.load_texture("Screenshot_1.jpg")
        
    def setup_camera(self):
        """Set up the camera projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width/self.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        
    def load_texture(self, image_path):
        img = Image.open(image_path)
        img = img.convert('RGB')
        img_width = img.size[0]
        img_height = img.size[1]
        img_data = np.array(img.getdata(), np.uint8)
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        # Specify the texture
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            img_width,
            img_height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            img_data
        )
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        
        return texture
        
    def handle_mouse_input(self, event):
        """Handle mouse input for camera control"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [1, 3]:  # Left or right click
                self.last_mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    self.mouse_pressed = True
                else:
                    self.right_pressed = True
            elif event.button == 4:  # Mouse wheel up
                self.camera_distance = max(2.0, self.camera_distance - self.zoom_sensitivity)
            elif event.button == 5:  # Mouse wheel down
                self.camera_distance = min(10.0, self.camera_distance + self.zoom_sensitivity)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_pressed = False
            elif event.button == 3:
                self.right_pressed = False
            self.last_mouse_pos = None
            
        elif event.type == pygame.MOUSEMOTION:
            if self.last_mouse_pos is not None:
                x, y = event.pos
                last_x, last_y = self.last_mouse_pos
                dx = x - last_x
                dy = y - last_y
                
                if self.mouse_pressed:  # Rotation
                    self.camera_rotation_y -= dx * self.mouse_sensitivity  # Reversed rotation direction
                    self.camera_rotation_x = max(-89, min(89, self.camera_rotation_x + dy * self.mouse_sensitivity))
                elif self.right_pressed:  # Panning
                    # Convert dx and dy to world space movement
                    cos_y = math.cos(math.radians(self.camera_rotation_y))
                    sin_y = math.sin(math.radians(self.camera_rotation_y))
                    self.camera_position[0] -= (dx * cos_y + dy * sin_y) * self.pan_sensitivity  # Inverted pan direction
                    self.camera_position[2] -= (-dx * sin_y + dy * cos_y) * self.pan_sensitivity
                
                self.last_mouse_pos = (x, y)
        
    def draw_ground(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.ground_texture)
        
        # Set material properties for the ground
        glColor3f(1.0, 1.0, 1.0)  # Set color to white to show texture properly
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
        
        # Draw 3.2x3.2 meter ground plane
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)  # Normal pointing up
        glTexCoord2f(0.0, 0.0); glVertex3f(-1.6, 0.0, -1.6)  # Bottom-left
        glTexCoord2f(1.0, 0.0); glVertex3f(1.6, 0.0, -1.6)   # Bottom-right
        glTexCoord2f(1.0, 1.0); glVertex3f(1.6, 0.0, 1.6)    # Top-right
        glTexCoord2f(0.0, 1.0); glVertex3f(-1.6, 0.0, 1.6)   # Top-left
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
    def update(self, robot_position, robot_rotation, robot, field=None, events=None):
        glViewport(0, 0, self.width, self.height)  # Ensure OpenGL viewport matches window size every frame
        for event in (events or []):
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
            elif event.type == VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL | RESIZABLE)
                glClearColor(0.8, 0.8, 0.8, 1.0)  # Re-set background color to light gray after resize
                glViewport(0, 0, self.width, self.height)  # Ensure OpenGL viewport matches window size
                self.setup_camera()
            # Handle mouse input
            self.handle_mouse_input(event)
                
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up camera position
        glLoadIdentity()
        
        # Calculate camera position in spherical coordinates
        camera_x = self.camera_distance * math.cos(math.radians(self.camera_rotation_x)) * math.sin(math.radians(self.camera_rotation_y))
        camera_y = self.camera_distance * math.sin(math.radians(self.camera_rotation_x))
        camera_z = self.camera_distance * math.cos(math.radians(self.camera_rotation_x)) * math.cos(math.radians(self.camera_rotation_y))
        
        # Set up the camera
        gluLookAt(
            camera_x + self.camera_position[0], camera_y, camera_z + self.camera_position[2],  # Camera position
            self.camera_position[0], 0, self.camera_position[2],  # Look at point
            0, 1, 0  # Up vector
        )
        
        # Draw World Coordinate Axes
        self.draw_axes(length=0.5)

        # Draw the ground
        self.draw_ground()
        
        # Render the field and blocks if available
        if field is not None:
            field.render()
        
        # Update robot position and rotation
        glPushMatrix()
        glTranslatef(robot_position[0], robot_position[1], robot_position[2])
        glRotatef(robot_rotation[1], 0, 1, 0)  # Yaw
        glRotatef(robot_rotation[0], 1, 0, 0)  # Pitch
        glRotatef(robot_rotation[2], 0, 0, 1)  # Roll
        
        # Render the robot
        robot.render()
        
        glPopMatrix()
        
        pygame.display.flip()
        return True 

    def draw_axes(self, length=1.0):
        """Draw X (red), Y (green), Z (blue) axes"""
        glPushAttrib(GL_LINE_BIT | GL_ENABLE_BIT)
        glDisable(GL_LIGHTING)
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

    def draw_debug_skybox(self, size=10.0):
        """Draw a large cube with differently colored faces."""
        s = size / 2.0
        glPushAttrib(GL_ENABLE_BIT | GL_POLYGON_BIT | GL_LIGHTING_BIT)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST) # Draw behind everything
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        glBegin(GL_QUADS)
        # Front face (Z+) - Blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(-s, -s,  s)
        glVertex3f( s, -s,  s)
        glVertex3f( s,  s,  s)
        glVertex3f(-s,  s,  s)
        
        # Back face (Z-) - Cyan
        glColor3f(0.0, 1.0, 1.0)
        glVertex3f(-s, -s, -s)
        glVertex3f(-s,  s, -s)
        glVertex3f( s,  s, -s)
        glVertex3f( s, -s, -s)
        
        # Top face (Y+) - Green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(-s,  s, -s)
        glVertex3f(-s,  s,  s)
        glVertex3f( s,  s,  s)
        glVertex3f( s,  s, -s)
        
        # Bottom face (Y-) - Magenta
        glColor3f(1.0, 0.0, 1.0)
        glVertex3f(-s, -s, -s)
        glVertex3f( s, -s, -s)
        glVertex3f( s, -s,  s)
        glVertex3f(-s, -s,  s)
        
        # Right face (X+) - Red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f( s, -s, -s)
        glVertex3f( s,  s, -s)
        glVertex3f( s,  s,  s)
        glVertex3f( s, -s,  s)
        
        # Left face (X-) - Yellow
        glColor3f(1.0, 1.0, 0.0)
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s,  s)
        glVertex3f(-s,  s,  s)
        glVertex3f(-s,  s, -s)
        glEnd()
        
        glPopAttrib() 