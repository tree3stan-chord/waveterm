"""
Extreme visualization modes for Wave
Mind-bending audio-reactive visualizations ported from parallax
"""

import numpy as np
import random
import math
from typing import List, Dict, Tuple
try:
    from ..audio.processor import AudioData
except ImportError:
    # For testing without audio dependencies
    pass
from ..render.terminal import VisualizationData, TerminalRenderer

class ExtremeVisualizations:
    """Collection of extreme/experimental visualization modes"""
    
    def __init__(self):
        self.glitch_state: Dict = {'frame': 0, 'corruption': []}
        self.void_tentacles: List[Dict] = []
        self.hypercube_rotation = {'x': 0, 'y': 0, 'z': 0, 'w': 0}
        self.fractal_iterations = []
        self.portal_rings: List[Dict] = []
        self.datamosh_buffer: List[str] = []
        self.code_drops: List[Dict] = []
        
    def glitch_art(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Digital glitch art effect with corruption artifacts"""
        self.glitch_state['frame'] += 1
        
        # Base pattern
        for y in range(canvas.height):
            for x in range(canvas.width):
                # Create underlying pattern
                wave = math.sin(x * 0.1 + time) * math.sin(y * 0.1 + time * 0.7)
                if abs(wave) > 0.3:
                    canvas.set_char(x, y, '█', 'cyan')
        
        # Audio-reactive glitch intensity
        glitch_intensity = audio_data.overall_amplitude if audio_data else 0.3
        
        # Horizontal line corruption
        if random.random() < glitch_intensity * 0.3:
            corrupt_y = random.randint(0, canvas.height - 1)
            shift = random.randint(-10, 10)
            
            # Shift line content
            line_chars = [canvas.get_char(x, corrupt_y) for x in range(canvas.width)]
            for x in range(canvas.width):
                source_x = (x - shift) % canvas.width
                char = line_chars[source_x] if source_x < len(line_chars) else ' '
                
                # Corrupt characters
                if random.random() < 0.1:
                    char = random.choice('▓▒░█▄▀■□▪▫')
                    
                canvas.set_char(x, corrupt_y, char, 'bright_red')
        
        # Block corruption
        if random.random() < glitch_intensity * 0.2:
            block_x = random.randint(0, canvas.width - 5)
            block_y = random.randint(0, canvas.height - 3)
            
            for y in range(block_y, min(block_y + 3, canvas.height)):
                for x in range(block_x, min(block_x + 5, canvas.width)):
                    canvas.set_char(x, y, random.choice('▓▒░'), 'magenta')
        
        # Scan lines
        if self.glitch_state['frame'] % 3 == 0:
            scan_y = (self.glitch_state['frame'] // 3) % canvas.height
            for x in range(0, canvas.width, 2):
                canvas.set_char(x, scan_y, '─', 'bright_black')
    
    def void_tentacles(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Lovecraftian void tentacles emerging from darkness"""
        # Initialize tentacles
        max_tentacles = 8
        if len(self.void_tentacles) < max_tentacles:
            for _ in range(max_tentacles - len(self.void_tentacles)):
                self.void_tentacles.append({
                    'segments': [],
                    'anchor_x': random.randint(0, canvas.width - 1),
                    'anchor_y': canvas.height - 1,
                    'length': random.randint(15, 25),
                    'phase': random.uniform(0, 2 * math.pi),
                    'thickness': random.randint(1, 3)
                })
        
        # Fill with void
        for y in range(canvas.height):
            for x in range(canvas.width):
                # Void background with occasional void particles
                if random.random() < 0.001:
                    canvas.set_char(x, y, '·', 'bright_black')
        
        # Update and draw tentacles
        audio_intensity = audio_data.overall_amplitude if audio_data else 0.3
        
        for tentacle in self.void_tentacles:
            # Update tentacle segments
            segments = []
            current_x = tentacle['anchor_x']
            current_y = tentacle['anchor_y']
            
            for i in range(tentacle['length']):
                # Writhing motion
                angle = (tentacle['phase'] + i * 0.3 + time * 2 + 
                        audio_intensity * math.sin(i * 0.5))
                
                # Movement influenced by audio
                dx = math.cos(angle) * (1 + audio_intensity)
                dy = -1 - math.sin(angle + i * 0.1) * 0.5
                
                current_x += dx
                current_y += dy
                
                if 0 <= current_x < canvas.width and 0 <= current_y < canvas.height:
                    segments.append((int(current_x), int(current_y), i))
            
            # Draw tentacle
            for x, y, segment_idx in segments:
                # Tentacle gets thinner toward tip
                thickness_factor = 1 - (segment_idx / tentacle['length'])
                
                # Different characters based on thickness
                if thickness_factor > 0.7:
                    chars = ['█', '▓']
                    color = 'bright_magenta'
                elif thickness_factor > 0.4:
                    chars = ['▒', '▓'] 
                    color = 'magenta'
                else:
                    chars = ['░', '▒', '·']
                    color = 'red'
                
                # Pulsing based on audio
                if audio_intensity > 0.6 and segment_idx % 3 == 0:
                    color = 'bright_red'
                
                char = random.choice(chars)
                canvas.set_char(x, y, char, color)
                
                # Add wispy edges
                if random.random() < 0.3:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        edge_x, edge_y = x + dx, y + dy
                        if (0 <= edge_x < canvas.width and 
                            0 <= edge_y < canvas.height and
                            canvas.get_char(edge_x, edge_y) == ' '):
                            canvas.set_char(edge_x, edge_y, '·', 'black')
    
    def hypercube_4d(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """4D hypercube projection with rotating tesseract"""
        # Update rotation based on audio
        rotation_speed = 0.02 + (audio_data.overall_amplitude * 0.05 if audio_data else 0)
        self.hypercube_rotation['x'] += rotation_speed
        self.hypercube_rotation['y'] += rotation_speed * 0.7
        self.hypercube_rotation['z'] += rotation_speed * 0.5
        self.hypercube_rotation['w'] += rotation_speed * 1.3
        
        # 4D hypercube vertices (tesseract)
        vertices_4d = []
        for i in range(16):  # 2^4 vertices
            x = 1 if i & 1 else -1
            y = 1 if i & 2 else -1  
            z = 1 if i & 4 else -1
            w = 1 if i & 8 else -1
            vertices_4d.append([x, y, z, w])
        
        # 4D rotation matrices
        rx = self.hypercube_rotation['x']
        ry = self.hypercube_rotation['y']
        rz = self.hypercube_rotation['z']
        rw = self.hypercube_rotation['w']
        
        # Apply 4D rotations and project to 3D, then to 2D
        projected_vertices = []
        
        for vertex in vertices_4d:
            x, y, z, w = vertex
            
            # 4D to 3D projection (drop W dimension with perspective)
            distance_4d = 4  # Distance from 4D object
            scale = distance_4d / (distance_4d + w)
            
            x3d = x * scale
            y3d = y * scale  
            z3d = z * scale
            
            # 3D rotation
            # Rotate around X
            y_rot = y3d * math.cos(rx) - z3d * math.sin(rx)
            z_rot = y3d * math.sin(rx) + z3d * math.cos(rx)
            y3d, z3d = y_rot, z_rot
            
            # Rotate around Y
            x_rot = x3d * math.cos(ry) + z3d * math.sin(ry)
            z_rot = -x3d * math.sin(ry) + z3d * math.cos(ry)
            x3d, z3d = x_rot, z_rot
            
            # 3D to 2D projection
            distance_3d = 5  # Distance from 3D object
            if distance_3d + z3d != 0:
                scale_2d = distance_3d / (distance_3d + z3d)
                
                screen_x = canvas.width // 2 + int(x3d * scale_2d * 8)
                screen_y = canvas.height // 2 + int(y3d * scale_2d * 4)
                
                # Color based on depth
                depth = (z3d + 2) / 4  # Normalize depth
                if depth > 0.7:
                    color = 'bright_cyan'
                elif depth > 0.4:
                    color = 'cyan'
                elif depth > 0.2:
                    color = 'blue'
                else:
                    color = 'bright_black'
                
                projected_vertices.append((screen_x, screen_y, depth, color))
        
        # Draw vertices
        for x, y, depth, color in projected_vertices:
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Different characters based on depth
                if depth > 0.8:
                    char = '●'
                elif depth > 0.5:
                    char = '•'
                else:
                    char = '·'
                    
                canvas.set_char(x, y, char, color)
        
        # Draw edges (simplified - connect nearby vertices)
        for i, (x1, y1, d1, c1) in enumerate(projected_vertices):
            for j, (x2, y2, d2, c2) in enumerate(projected_vertices[i+1:], i+1):
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                # Only draw edges for nearby vertices
                if distance < 20 and abs(d1 - d2) < 0.5:
                    # Simple line drawing
                    steps = int(distance)
                    for step in range(steps):
                        if steps > 0:
                            t = step / steps
                            x = int(x1 + t * (x2 - x1))
                            y = int(y1 + t * (y2 - y1))
                            
                            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                                canvas.set_char(x, y, '─', 'white')
    
    def ascii_fractal(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """ASCII-based fractal tree generation"""
        # Clear canvas
        canvas.clear()
        
        # Fractal parameters influenced by audio
        max_depth = 8
        if audio_data:
            angle_variation = audio_data.treble * 45  # High freq affects branching angle
            length_factor = 0.7 + audio_data.mid * 0.2  # Mid freq affects branch length
            thickness_factor = audio_data.bass  # Bass affects trunk thickness
        else:
            angle_variation = 20
            length_factor = 0.8
            thickness_factor = 0.3
        
        def draw_branch(x: float, y: float, angle: float, length: float, depth: int):
            """Recursively draw fractal branch"""
            if depth <= 0 or length < 2:
                return
                
            # Calculate end point
            end_x = x + length * math.cos(math.radians(angle))
            end_y = y - length * math.sin(math.radians(angle))  # Y is inverted
            
            # Draw branch line
            steps = int(length)
            for i in range(steps):
                if steps > 0:
                    t = i / steps
                    draw_x = int(x + t * (end_x - x))
                    draw_y = int(y + t * (end_y - y))
                    
                    if 0 <= draw_x < canvas.width and 0 <= draw_y < canvas.height:
                        # Character and color based on depth
                        if depth > 6:
                            char, color = '█', 'yellow'  # Trunk
                        elif depth > 4:
                            char, color = '▓', 'green'   # Major branches  
                        elif depth > 2:
                            char, color = '▒', 'bright_green'  # Small branches
                        else:
                            char, color = '·', 'bright_yellow'  # Leaves
                            
                        # Add some thickness for trunk
                        if depth > 5 and thickness_factor > 0.5:
                            for dx in [-1, 0, 1]:
                                thick_x = draw_x + dx
                                if 0 <= thick_x < canvas.width:
                                    canvas.set_char(thick_x, draw_y, char, color)
                        else:
                            canvas.set_char(draw_x, draw_y, char, color)
            
            # Recursive branches
            if depth > 1:
                new_length = length * length_factor
                
                # Left branch
                left_angle = angle + angle_variation + random.uniform(-10, 10)
                draw_branch(end_x, end_y, left_angle, new_length, depth - 1)
                
                # Right branch  
                right_angle = angle - angle_variation + random.uniform(-10, 10)
                draw_branch(end_x, end_y, right_angle, new_length, depth - 1)
                
                # Occasional middle branch for complexity
                if random.random() < 0.3:
                    mid_angle = angle + random.uniform(-15, 15)
                    draw_branch(end_x, end_y, mid_angle, new_length * 0.7, depth - 1)
        
        # Start fractal from bottom center
        start_x = canvas.width // 2
        start_y = canvas.height - 1
        start_angle = 90  # Straight up
        start_length = canvas.height // 3
        
        draw_branch(start_x, start_y, start_angle, start_length, max_depth)
        
        # Add ground line
        for x in range(canvas.width):
            canvas.set_char(x, canvas.height - 1, '▀', 'yellow')
    
    def dimensional_portal(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Swirling dimensional portal with energy rings"""
        center_x = canvas.width // 2
        center_y = canvas.height // 2
        
        # Initialize portal rings
        max_rings = 15
        if len(self.portal_rings) < max_rings:
            for i in range(max_rings):
                self.portal_rings.append({
                    'radius': i * 2 + 5,
                    'phase': random.uniform(0, 2 * math.pi),
                    'speed': random.uniform(0.1, 0.3),
                    'intensity': random.uniform(0.5, 1.0)
                })
        
        # Audio reactive portal energy
        portal_energy = audio_data.overall_amplitude if audio_data else 0.4
        
        # Draw swirling portal
        for ring in self.portal_rings:
            ring['phase'] += ring['speed'] * (1 + portal_energy)
            
            # Calculate ring points
            num_points = int(ring['radius'] * 2)
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi + ring['phase']
                
                # Spiral effect
                spiral_radius = ring['radius'] + 2 * math.sin(angle * 3 + time)
                
                x = center_x + int(spiral_radius * math.cos(angle))
                y = center_y + int(spiral_radius * math.sin(angle) * 0.5)  # Squish Y
                
                if 0 <= x < canvas.width and 0 <= y < canvas.height:
                    # Color based on distance from center and energy
                    distance_norm = spiral_radius / (max_rings * 2)
                    
                    if distance_norm < 0.3:
                        # Core
                        char = '█' if portal_energy > 0.7 else '▓'
                        color = 'bright_white'
                    elif distance_norm < 0.6:
                        # Energy ring
                        char = '▒' if portal_energy > 0.5 else '░'
                        color = 'bright_cyan'
                    else:
                        # Outer glow
                        char = '·' if portal_energy > 0.3 else ' '
                        color = 'blue'
                    
                    # Pulsing effect
                    if (int(time * 10) + i) % 5 == 0:
                        color = 'bright_magenta'
                        
                    canvas.set_char(x, y, char, color)
        
        # Portal center void
        for y in range(center_y - 2, center_y + 3):
            for x in range(center_x - 4, center_x + 5):
                if 0 <= x < canvas.width and 0 <= y < canvas.height:
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance < 3:
                        canvas.set_char(x, y, ' ', 'black')
        
        # Energy particles escaping portal
        if random.random() < portal_energy * 0.5:
            escape_x = center_x + random.randint(-3, 3)
            escape_y = center_y + random.randint(-2, 2)
            
            if 0 <= escape_x < canvas.width and 0 <= escape_y < canvas.height:
                canvas.set_char(escape_x, escape_y, '*', 'bright_yellow')