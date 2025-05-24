import random
import numpy as np
from OpenGL.GL import *

Open_challenge = False

class Field:
    Randomization = True  # If False, do not randomize obstacles or robot initial position
    def __init__(self):
        self.field_size = 4.0  # 4x4 meter field
        self.block_size = 0.05  # 50mm blocks
        self.block_height = 0.1  # 100mm height
        self.blocks = []  # List of (position, color) tuples
        # Define the bounds between the two red rectangles
        self.rect_bounds = {
            'min_x': -1.2,  # Left boundary (adjusted to be inside outer red rectangle)
            'max_x': 1.2,   # Right boundary
            'min_z': -1.2,  # Bottom boundary
            'max_z': 1.2    # Top boundary
        }
        # Define wall dimensions
        self.wall_height = 0.1  # 10cm high walls
        self.inner_wall_size = 0.8  # 0.8x0.8m inner walls
        self.outer_wall_size = 3.0  # 3x3m outer walls
        self.generate_random_blocks()
        
        # Reference to robot for trajectory rendering
        self.robot = None
    
    def set_robot(self, robot):
        """Set the robot reference for trajectory rendering"""
        self.robot = robot
    
    def generate_random_blocks(self):
        """Randomly place 3 red and 3 green blocks on the 16 user-specified positions (left, right, up, down) around the white square."""
        if Open_challenge:
            self.blocks = []
            return
        if not Field.Randomization:
            # If randomization is off, place blocks in a fixed configuration (example: corners)
            self.blocks = [
                ((-1.1, 0.5), 'red'),
                ((1.1, 0.5), 'green'),
                ((-1.1, -0.5), 'red'),
                ((1.1, -0.5), 'green'),
                ((-0.5, 1.1), 'red'),
                ((0.5, 1.1), 'green'),
            ]
            return
        self.blocks = []
        num_blocks = 6  # 3 red and 3 green blocks
        colors = ['red', 'green'] * (num_blocks // 2)
        random.shuffle(colors)

        # Define positions for each side, separated into outer and inner positions
        side_positions = {
            'left': {
                'outer': [(-1.1, 0.5), (-1.1, -0.5)],  # Far positions
                'inner': [(-0.9, 0.5), (-0.9, 0), (-0.9, -0.5)]  # Middle positions
            },
            'right': {
                'outer': [(1.1, 0.5), (1.1, -0.5)],  # Far positions
                'inner': [(0.9, 0.5), (0.9, 0), (0.9, -0.5)]  # Middle positions
            },
            'up': {
                'outer': [(-0.5, 1.1), (0.5, 1.1)],  # Far positions
                'inner': [(-0.5, 0.9), (0, 0.9), (0.5, 0.9)]  # Middle positions
            },
            'down': {
                'outer': [(-0.5, -1.1), (0.5, -1.1)],  # Far positions
                'inner': [(-0.5, -0.9), (0, -0.9), (0.5, -0.9)]  # Middle positions
            }
        }

        # Randomly select sides to place blocks
        sides = ['left', 'right', 'up', 'down']
        random.shuffle(sides)
        
        # Place blocks ensuring the rule is followed
        remaining_blocks = num_blocks
        for side in sides:
            if remaining_blocks == 0:
                break
                
            # Decide how many blocks to place on this side (1 or 2)
            blocks_on_side = min(2, remaining_blocks)
            
            if blocks_on_side == 2:
                # If placing 2 blocks, use only outer positions
                positions = random.sample(side_positions[side]['outer'], 2)
            else:
                # If placing 1 block, can use any position
                all_positions = side_positions[side]['outer'] + side_positions[side]['inner']
                positions = random.sample(all_positions, 1)
            
            # Add blocks to the list
            for pos in positions:
                self.blocks.append((pos, colors[len(self.blocks)]))
                remaining_blocks -= 1
    
    def render_walls(self):
        """Render the black walls for both inner (0.8x0.8m) and outer (3x3m) areas as solid cuboids."""
        glColor3f(0.0, 0.0, 0.0)  # Black color
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 10.0)

        def draw_box(center_x, center_z, width, depth, height):
            x1 = center_x - width / 2
            x2 = center_x + width / 2
            z1 = center_z - depth / 2
            z2 = center_z + depth / 2
            y1 = 0.0
            y2 = height
            glBegin(GL_QUADS)
            # Bottom face
            glNormal3f(0.0, -1.0, 0.0)
            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y1, z1)
            glVertex3f(x2, y1, z2)
            glVertex3f(x1, y1, z2)
            # Top face
            glNormal3f(0.0, 1.0, 0.0)
            glVertex3f(x1, y2, z1)
            glVertex3f(x1, y2, z2)
            glVertex3f(x2, y2, z2)
            glVertex3f(x2, y2, z1)
            # Front face
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(x1, y1, z2)
            glVertex3f(x2, y1, z2)
            glVertex3f(x2, y2, z2)
            glVertex3f(x1, y2, z2)
            # Back face
            glNormal3f(0.0, 0.0, -1.0)
            glVertex3f(x1, y1, z1)
            glVertex3f(x1, y2, z1)
            glVertex3f(x2, y2, z1)
            glVertex3f(x2, y1, z1)
            # Left face
            glNormal3f(-1.0, 0.0, 0.0)
            glVertex3f(x1, y1, z1)
            glVertex3f(x1, y1, z2)
            glVertex3f(x1, y2, z2)
            glVertex3f(x1, y2, z1)
            # Right face
            glNormal3f(1.0, 0.0, 0.0)
            glVertex3f(x2, y1, z1)
            glVertex3f(x2, y2, z1)
            glVertex3f(x2, y2, z2)
            glVertex3f(x2, y1, z2)
            glEnd()

        wall_thickness = 0.01  # 10mm thick walls
        height = self.wall_height

        # Inner square (0.8x0.8m)
        inner_half = self.inner_wall_size / 2
        # Top wall
        draw_box(0, inner_half + wall_thickness/2, self.inner_wall_size + wall_thickness, wall_thickness, height)
        # Bottom wall
        draw_box(0, -inner_half - wall_thickness/2, self.inner_wall_size + wall_thickness, wall_thickness, height)
        # Left wall
        draw_box(-inner_half - wall_thickness/2, 0, wall_thickness, self.inner_wall_size + wall_thickness, height)
        # Right wall
        draw_box(inner_half + wall_thickness/2, 0, wall_thickness, self.inner_wall_size + wall_thickness, height)

        # Outer square (3x3m)
        outer_half = 1.5  # 3.0m / 2
        # Top wall
        draw_box(0, outer_half + wall_thickness/2, self.outer_wall_size + wall_thickness, wall_thickness, height)
        # Bottom wall
        draw_box(0, -outer_half - wall_thickness/2, self.outer_wall_size + wall_thickness, wall_thickness, height)
        # Left wall
        draw_box(-outer_half - wall_thickness/2, 0, wall_thickness, self.outer_wall_size + wall_thickness, height)
        # Right wall
        draw_box(outer_half + wall_thickness/2, 0, wall_thickness, self.outer_wall_size + wall_thickness, height)

    def render_parking_space(self):
        """Render the magenta parking space walls as two vertical cuboids, spaced by 2.4x robot length."""
        if not self.robot:
            return  # Need robot reference for length
        robot_length = self.robot.get_length_x()
        gap = 2.4 * robot_length  # 60% more than 1.5x
        wall_width = 0.02  # 2 cm thick
        wall_height = 0.10  # 10 cm high
        wall_length = 0.20  # 20 cm long
        z_center = -1.5 + wall_length / 2 + 0.02  # 2cm offset from field edge
        x_offset = gap / 2
        # Left wall
        glPushMatrix()
        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.0, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        self._draw_box(-x_offset, z_center, wall_width, wall_length, wall_height)
        glPopMatrix()
        # Right wall
        glPushMatrix()
        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.0, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        self._draw_box(x_offset, z_center, wall_width, wall_length, wall_height)
        glPopMatrix()

    def _draw_box(self, center_x, center_z, width, depth, height):
        """Draw a box centered at (center_x, center_z) with given dimensions."""
        x1 = center_x - width / 2
        x2 = center_x + width / 2
        z1 = center_z - depth / 2
        z2 = center_z + depth / 2
        y1 = 0.0
        y2 = height
        glBegin(GL_QUADS)
        # Bottom face
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y1, z1)
        glVertex3f(x2, y1, z2)
        glVertex3f(x1, y1, z2)
        # Top face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(x1, y2, z1)
        glVertex3f(x1, y2, z2)
        glVertex3f(x2, y2, z2)
        glVertex3f(x2, y2, z1)
        # Front face
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(x1, y1, z2)
        glVertex3f(x2, y1, z2)
        glVertex3f(x2, y2, z2)
        glVertex3f(x1, y2, z2)
        # Back face
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(x1, y1, z1)
        glVertex3f(x1, y2, z1)
        glVertex3f(x2, y2, z1)
        glVertex3f(x2, y1, z1)
        # Left face
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(x1, y1, z1)
        glVertex3f(x1, y1, z2)
        glVertex3f(x1, y2, z2)
        glVertex3f(x1, y2, z1)
        # Right face
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(x2, y1, z1)
        glVertex3f(x2, y2, z1)
        glVertex3f(x2, y2, z2)
        glVertex3f(x2, y1, z2)
        glEnd()

    def get_parking_space_options(self):
        """Return two possible robot positions and rotations (facing each magenta block, spaced by 2.4x robot length)."""
        if not self.robot:
            return []
        robot_length = self.robot.get_length_x()
        gap = 2.4 * robot_length  # 60% more than 1.5x
        z_center = -1.5 + 0.20 / 2 + 0.02
        x_offset = gap / 2
        y = 0.01
        # Facing right block (yaw=90), centered just left of center
        pos1 = [-x_offset + 0.0, y, z_center]
        rot1 = [0.0, 90.0, 0.0]
        # Facing left block (yaw=-90), centered just right of center
        pos2 = [x_offset - 0.0, y, z_center]
        rot2 = [0.0, -90.0, 0.0]
        return [(pos1, rot1), (pos2, rot2)]

    def render(self, draw_trajectory=True):
        """Render all blocks in the field and mark the origin (0,0) with a yellow circle for reference."""
        # Draw walls first
        self.render_walls()
        
        # Draw yellow circle at the origin
        glPushMatrix()
        glTranslatef(0.0, 0.01, 0.0)  # Slightly above ground to avoid z-fighting
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_LINE_LOOP)
        num_segments = 64
        radius = 0.12
        for i in range(num_segments):
            theta = 2.0 * np.pi * i / num_segments
            x = radius * np.cos(theta)
            z = radius * np.sin(theta)
            glVertex3f(x, 0, z)
        glEnd()
        glPopMatrix()

        # Render robot trajectory if available and allowed
        if draw_trajectory and self.robot and self.robot.trajectory:
            glPushAttrib(GL_LINE_BIT | GL_ENABLE_BIT)
            glDisable(GL_LIGHTING)
            glLineWidth(4.0)  # Thicker line
            glColor3f(0.0, 0.8, 0.0)  # Green color
            glBegin(GL_LINE_STRIP)
            for x, z in self.robot.trajectory:
                glVertex3f(x, 0.02, z)  # Slightly above ground to avoid z-fighting
            glEnd()
            glPopAttrib()

        for (x, z), color in self.blocks:
            glPushMatrix()
            glTranslatef(x, 0.0, z)  # Place blocks directly on ground (removed elevation)
            
            # Set color
            if color == 'red':
                glColor3f(238/255, 39/255, 55/255)  # RGB (238, 39, 55)
                glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.0, 0.0, 1.0])
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [238/255, 39/255, 55/255, 1.0])
            else:  # green
                glColor3f(68/255, 214/255, 44/255)  # RGB (68, 214, 44)
                glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.2, 0.0, 1.0])
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [68/255, 214/255, 44/255, 1.0])
            
            glMaterialfv(GL_FRONT, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
            glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
            
            # Draw block as a cube
            glBegin(GL_QUADS)
            # Top face
            glNormal3f(0.0, 1.0, 0.0)
            glVertex3f(-self.block_size/2, self.block_height, -self.block_size/2)
            glVertex3f(-self.block_size/2, self.block_height, self.block_size/2)
            glVertex3f(self.block_size/2, self.block_height, self.block_size/2)
            glVertex3f(self.block_size/2, self.block_height, -self.block_size/2)
            
            # Bottom face
            glNormal3f(0.0, -1.0, 0.0)
            glVertex3f(-self.block_size/2, 0, -self.block_size/2)
            glVertex3f(self.block_size/2, 0, -self.block_size/2)
            glVertex3f(self.block_size/2, 0, self.block_size/2)
            glVertex3f(-self.block_size/2, 0, self.block_size/2)
            
            # Front face
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(-self.block_size/2, 0, self.block_size/2)
            glVertex3f(self.block_size/2, 0, self.block_size/2)
            glVertex3f(self.block_size/2, self.block_height, self.block_size/2)
            glVertex3f(-self.block_size/2, self.block_height, self.block_size/2)
            
            # Back face
            glNormal3f(0.0, 0.0, -1.0)
            glVertex3f(-self.block_size/2, 0, -self.block_size/2)
            glVertex3f(-self.block_size/2, self.block_height, -self.block_size/2)
            glVertex3f(self.block_size/2, self.block_height, -self.block_size/2)
            glVertex3f(self.block_size/2, 0, -self.block_size/2)
            
            # Right face
            glNormal3f(1.0, 0.0, 0.0)
            glVertex3f(self.block_size/2, 0, -self.block_size/2)
            glVertex3f(self.block_size/2, self.block_height, -self.block_size/2)
            glVertex3f(self.block_size/2, self.block_height, self.block_size/2)
            glVertex3f(self.block_size/2, 0, self.block_size/2)
            
            # Left face
            glNormal3f(-1.0, 0.0, 0.0)
            glVertex3f(-self.block_size/2, 0, -self.block_size/2)
            glVertex3f(-self.block_size/2, 0, self.block_size/2)
            glVertex3f(-self.block_size/2, self.block_height, self.block_size/2)
            glVertex3f(-self.block_size/2, self.block_height, -self.block_size/2)
            glEnd()
            
            glPopMatrix()

        self.render_parking_space()
    
    def get_block_positions(self):
        """Return list of block positions and colors"""
        return self.blocks 

    def get_randomization(self):
        return Field.Randomization 