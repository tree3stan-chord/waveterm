"""
Enhanced and new visualization modes inspired by the web implementation
Adds missing visualizations and improves existing ones with better effects
"""

import numpy as np
import random
import math
import time
from typing import List, Dict, Tuple, Optional

try:
    from ..audio.processor import AudioData
except ImportError:
    pass

from ..render.terminal import VisualizationData
from .colors import get_color_manager, ASCIISet, ColorPalette, get_chars, get_chars_reversed, get_char_for_intensity
from ..core.logger import get_logger

logger = get_logger('visualizations.enhanced')


class ParticleSystem:
    """Enhanced particle system for multiple visualization modes"""
    
    def __init__(self, max_particles: int = 500):
        self.particles: List[Dict] = []
        self.max_particles = max_particles
        
    def add_particle(self, x: float, y: float, vx: float, vy: float, 
                    life: float = 1.0, char: str = '*', particle_type: str = 'default'):
        """Add a new particle to the system"""
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'life': life, 'char': char, 'type': particle_type,
                'age': 0.0, 'trail': []
            })
    
    def update_particles(self, dt: float = 0.033):
        """Update all particles"""
        active_particles = []
        
        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx'] * dt * 30  # Scale for terminal coordinates
            particle['y'] += particle['vy'] * dt * 30
            
            # Update life and age
            particle['life'] -= dt
            particle['age'] += dt
            
            # Apply physics based on type
            if particle['type'] == 'explosion':
                particle['vx'] *= 0.95  # Friction
                particle['vy'] *= 0.95
                particle['vy'] += 0.1   # Gravity
            elif particle['type'] == 'fire':
                particle['vy'] -= 0.2   # Upward force
                particle['vx'] += (random.random() - 0.5) * 0.1  # Turbulence
            elif particle['type'] == 'spark':
                particle['vy'] += 0.2   # Gravity
                particle['vx'] *= 0.98  # Air resistance
            
            # Keep particle if still alive
            if particle['life'] > 0:
                active_particles.append(particle)
        
        self.particles = active_particles
    
    def draw_particles(self, canvas: VisualizationData):
        """Draw all particles to canvas"""
        color_manager = get_color_manager()
        
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Get intensity based on life
                intensity = particle['life']
                char = get_char_for_intensity(intensity, ASCIISet.EXPLOSION)
                color = color_manager.get_color_for_intensity(intensity)
                
                canvas.set_char(x, y, char, color)
                
                # Draw trail for certain particle types
                if particle['type'] in ['explosion', 'spark'] and len(particle.get('trail', [])) > 0:
                    for i, (tx, ty) in enumerate(particle['trail'][-3:]):  # Last 3 trail points
                        trail_x, trail_y = int(tx), int(ty)
                        if 0 <= trail_x < canvas.width and 0 <= trail_y < canvas.height:
                            trail_intensity = intensity * (0.3 + 0.7 * (i / 3))
                            trail_char = get_char_for_intensity(trail_intensity, ASCIISet.DOTS)
                            canvas.set_char(trail_x, trail_y, trail_char, 'dim white')


class EnhancedVisualizations:
    """Enhanced visualization modes with improved effects"""
    
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.matrix_drops: List[int] = []
        self.stars: List[Dict] = []
        self.explosion_particles: List[Dict] = []
        self.spiral_arms: List[Dict] = []
        self.fractal_branches: List[Dict] = []
        
    def explosion(self, canvas: VisualizationData, audio_data: AudioData, elapsed_time: float):
        """Explosive particle visualization with audio reactive bursts"""
        color_manager = get_color_manager()
        color_manager.set_palette(ColorPalette.FIRE)
        color_manager.set_ascii_set(ASCIISet.EXPLOSION)
        
        canvas.clear()
        
        if audio_data is None:
            return
            
        # Analyze audio for explosion triggers
        max_intensity = 0
        avg_intensity = 0
        for amplitude in audio_data.amplitudes:
            intensity = amplitude
            max_intensity = max(max_intensity, intensity)
            avg_intensity += intensity
        
        if len(audio_data.amplitudes) > 0:
            avg_intensity /= len(audio_data.amplitudes)
        
        # Create explosions on strong beats
        if max_intensity > 0.6 and len(self.explosion_particles) < 200:
            # Multiple explosion centers
            num_explosions = min(3, int(max_intensity * 5))
            
            for _ in range(num_explosions):
                cx = random.randint(canvas.width // 4, 3 * canvas.width // 4)
                cy = random.randint(canvas.height // 4, 3 * canvas.height // 4)
                power = max_intensity * 30
                
                # Create explosion particles
                for i in range(int(power)):
                    angle = (i / power) * math.pi * 2 + random.random() * 0.5
                    speed = 2 + random.random() * 6 * max_intensity
                    
                    self.particle_system.add_particle(
                        cx, cy,
                        math.cos(angle) * speed, 
                        math.sin(angle) * speed * 0.7,
                        life=1.0 + random.random(),
                        particle_type='explosion'
                    )
        
        # Add continuous small explosions from frequency bars
        bar_count = min(16, len(audio_data.amplitudes))
        for i in range(0, len(audio_data.amplitudes), len(audio_data.amplitudes) // bar_count):
            intensity = audio_data.amplitudes[i]
            if intensity > 0.4:
                x = int((i / len(audio_data.amplitudes)) * canvas.width)
                y = int(canvas.height - intensity * canvas.height)
                
                # Small explosion
                for _ in range(int(intensity * 5)):
                    self.particle_system.add_particle(
                        x + random.randint(-2, 2),
                        y + random.randint(-2, 2),
                        (random.random() - 0.5) * 2,
                        -random.random() * 3,
                        life=0.5,
                        particle_type='spark'
                    )
        
        # Update and draw particles
        self.particle_system.update_particles()
        self.particle_system.draw_particles(canvas)
    
    def spiral(self, canvas: VisualizationData, audio_data: AudioData, elapsed_time: float):
        """Multi-armed spiral visualization with audio reactive effects"""
        color_manager = get_color_manager()
        color_manager.set_palette(ColorPalette.NEON)
        color_manager.set_ascii_set(ASCIISet.GEOMETRIC)
        
        canvas.clear()
        
        if audio_data is None:
            return
        
        # Calculate center and audio metrics
        center_x = canvas.width / 2
        center_y = canvas.height / 2
        
        avg_intensity = np.mean(audio_data.amplitudes) if len(audio_data.amplitudes) > 0 else 0
        
        # Spiral parameters
        num_arms = 5
        points_per_arm = 200
        
        for arm in range(num_arms):
            arm_offset = (arm / num_arms) * math.pi * 2
            
            for i in range(points_per_arm):
                t = i / points_per_arm
                data_index = int(t * (len(audio_data.amplitudes) - 1))
                intensity = audio_data.amplitudes[data_index] if data_index < len(audio_data.amplitudes) else 0
                
                # Spiral calculation
                angle = t * math.pi * 6 + arm_offset + elapsed_time
                radius = t * min(canvas.width, canvas.height) * 0.4 * (0.5 + intensity)
                
                # Position calculation  
                x = int(center_x + math.cos(angle) * radius)
                y = int(center_y + math.sin(angle) * radius * 0.6)
                
                if 0 <= x < canvas.width and 0 <= y < canvas.height:
                    # Main spiral line with thickness
                    char = get_char_for_intensity(intensity)
                    color = color_manager.get_color_for_intensity(intensity)
                    
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < canvas.width and 0 <= ny < canvas.height:
                                canvas.set_char(nx, ny, char, color)
                    
                    # Particle spray from intense points
                    if intensity > 0.8 and random.random() < 0.3:
                        spray_angle = angle + (random.random() - 0.5)
                        spray_radius = radius + random.random() * 10
                        sx = int(center_x + math.cos(spray_angle) * spray_radius)
                        sy = int(center_y + math.sin(spray_angle) * spray_radius * 0.6)
                        
                        if 0 <= sx < canvas.width and 0 <= sy < canvas.height:
                            spray_char = get_char_for_intensity(1.0, ASCIISet.EXPLOSION)
                            canvas.set_char(sx, sy, spray_char, 'bright_yellow')
        
        # Central explosion for strong bass
        bass_intensity = np.mean(audio_data.amplitudes[:len(audio_data.amplitudes)//8]) if len(audio_data.amplitudes) > 0 else 0
        if bass_intensity > 0.7:
            explosion_size = int(bass_intensity * 8)
            for ex in range(-explosion_size, explosion_size + 1):
                for ey in range(-explosion_size, explosion_size + 1):
                    dist = math.sqrt(ex * ex + ey * ey)
                    if dist <= explosion_size:
                        px = int(center_x + ex)
                        py = int(center_y + ey)
                        if 0 <= px < canvas.width and 0 <= py < canvas.height:
                            fade = 1 - (dist / explosion_size)
                            char = get_char_for_intensity(fade, ASCIISet.EXPLOSION)
                            canvas.set_char(px, py, char, 'bright_red')
    
    def fractal_tree(self, canvas: VisualizationData, audio_data: AudioData, elapsed_time: float):
        """Enhanced fractal tree with audio-reactive growth and effects"""
        color_manager = get_color_manager()
        color_manager.set_palette(ColorPalette.ORGANIC if elapsed_time % 10 < 5 else ColorPalette.RETRO)
        color_manager.set_ascii_set(ASCIISet.ORGANIC)
        
        canvas.clear()
        
        if audio_data is None:
            return
        
        # Audio analysis
        avg_intensity = np.mean(audio_data.amplitudes) if len(audio_data.amplitudes) > 0 else 0
        bass_intensity = np.mean(audio_data.amplitudes[:len(audio_data.amplitudes)//4]) if len(audio_data.amplitudes) > 0 else 0
        
        # Tree parameters affected by audio
        trunk_height = canvas.height * 0.3
        max_depth = min(7, 3 + int(avg_intensity * 6))
        angle_spread = 0.4 + avg_intensity * 0.6
        branch_shrink = 0.65 + bass_intensity * 0.2
        sway = math.sin(elapsed_time * 2) * bass_intensity * 0.3
        
        def draw_branch(x: float, y: float, length: float, angle: float, depth: int, thickness: int):
            """Recursively draw tree branches"""
            if depth <= 0 or length < 2 or y < 0:
                return
                
            # Calculate end point
            end_x = x + math.cos(angle) * length
            end_y = y - math.sin(angle) * length
            
            # Draw branch line
            steps = max(1, int(length))
            for i in range(steps):
                t = i / steps
                bx = int(x + (end_x - x) * t)
                by = int(y + (end_y - y) * t)
                
                if 0 <= bx < canvas.width and 0 <= by < canvas.height:
                    # Branch thickness
                    for w in range(-thickness, thickness + 1):
                        wx = bx + w
                        if 0 <= wx < canvas.width:
                            # Character based on depth and thickness
                            if depth > max_depth // 2:
                                char = '|' if w == 0 else '/'
                            else:
                                char = get_char_for_intensity(depth / max_depth, ASCIISet.ORGANIC)
                            
                            color = color_manager.get_color_for_intensity(depth / max_depth)
                            canvas.set_char(wx, by, char, color)
            
            # Add leaves at branch endpoints
            if depth <= 2 and random.random() < 0.7 + avg_intensity * 0.3:
                leaf_x, leaf_y = int(end_x), int(end_y)
                if 0 <= leaf_x < canvas.width and 0 <= leaf_y < canvas.height:
                    leaf_chars = ['*', '✿', '●', '◉', '◦'] 
                    leaf_char = random.choice(leaf_chars)
                    canvas.set_char(leaf_x, leaf_y, leaf_char, 'bright_green')
                    
                    # Falling leaves on strong beats
                    if bass_intensity > 0.6 and random.random() < 0.4:
                        fall_distance = random.randint(3, 15)
                        fall_x = leaf_x + random.randint(-3, 3)
                        fall_y = min(canvas.height - 1, leaf_y + fall_distance)
                        
                        for fy in range(leaf_y + 1, fall_y + 1, 2):
                            if 0 <= fall_x < canvas.width and 0 <= fy < canvas.height:
                                canvas.set_char(fall_x, fy, '·', 'dim green')
            
            # Create child branches
            num_branches = 2 + (1 if random.random() < avg_intensity else 0)
            for i in range(num_branches):
                new_angle = angle + (i - (num_branches - 1) / 2) * angle_spread + sway
                new_length = length * branch_shrink * (0.8 + random.random() * 0.4)
                new_thickness = max(0, thickness - 1)
                
                draw_branch(end_x, end_y, new_length, new_angle, depth - 1, new_thickness)
        
        # Draw the main tree
        start_x = canvas.width / 2
        start_y = canvas.height - 3
        draw_branch(start_x, start_y, trunk_height, math.pi / 2 + sway, max_depth, 2)
        
        # Add ground
        ground_y = canvas.height - 2
        for x in range(canvas.width):
            if ground_y >= 0:
                canvas.set_char(x, ground_y, '─', 'dim white')
                # Add grass
                if random.random() < 0.2:
                    grass_y = ground_y - 1
                    if grass_y >= 0:
                        canvas.set_char(x, grass_y, random.choice([',', "'", '`']), 'green')
    
    def enhanced_matrix(self, canvas: VisualizationData, audio_data: AudioData, elapsed_time: float):
        """Enhanced Matrix rain with better effects and audio reactivity"""
        color_manager = get_color_manager()
        color_manager.set_palette(ColorPalette.MATRIX)
        
        canvas.clear()
        
        # Initialize matrix drops if needed
        if len(self.matrix_drops) != canvas.width:
            self.matrix_drops = [random.randint(0, canvas.height) for _ in range(canvas.width)]
        
        if audio_data is None:
            return
            
        # Audio analysis
        avg_intensity = np.mean(audio_data.amplitudes) if len(audio_data.amplitudes) > 0 else 0
        max_intensity = np.max(audio_data.amplitudes) if len(audio_data.amplitudes) > 0 else 0
        
        # Matrix characters (mix of numbers, letters, and katakana)
        matrix_chars = "0123456789ABCDEFアイウエオカキクケコサシスセソタチツテト"
        
        # Update drops with audio-reactive speed
        for i in range(len(self.matrix_drops)):
            if i < len(audio_data.amplitudes):
                frequency_intensity = audio_data.amplitudes[i]
            else:
                frequency_intensity = avg_intensity
                
            # Speed varies with audio
            base_speed = 1
            audio_speed = frequency_intensity * 4
            explosion_speed = 8 if max_intensity > 0.8 else 0
            
            total_speed = base_speed + audio_speed + explosion_speed
            
            if random.random() < 0.1 + frequency_intensity * 0.4:
                self.matrix_drops[i] += int(total_speed)
                if self.matrix_drops[i] > canvas.height + 20:
                    self.matrix_drops[i] = -random.randint(0, 20)
        
        # Draw matrix rain
        for x in range(len(self.matrix_drops)):
            drop_y = self.matrix_drops[x]
            
            # Get frequency intensity for this column
            if x < len(audio_data.amplitudes):
                intensity = audio_data.amplitudes[x]
            else:
                intensity = avg_intensity
            
            # Trail length based on intensity
            trail_length = 8 + int(intensity * 20)
            
            for t in range(trail_length):
                y = drop_y - t
                if 0 <= y < canvas.height:
                    fade = 1 - (t / trail_length)
                    char_intensity = fade * (0.5 + intensity * 0.5)
                    
                    if t == 0:
                        # Head of the drop - bright character
                        char = random.choice(['◉', '●', '◎', '○'])
                        color = 'bright_white'
                    else:
                        # Body of the drop
                        char = random.choice(matrix_chars)
                        if char_intensity > 0.7:
                            color = 'bright_green'
                        elif char_intensity > 0.4:
                            color = 'green'
                        else:
                            color = 'dim green'
                    
                    canvas.set_char(x, y, char, color)
                    
                    # Side effects for high intensity
                    if intensity > 0.7 and random.random() < 0.3:
                        side_x = x + random.randint(-1, 1)
                        if 0 <= side_x < canvas.width:
                            side_char = random.choice(['*', '+', '×'])
                            canvas.set_char(side_x, y, side_char, 'bright_cyan')
    
    def glitch_art(self, canvas: VisualizationData, audio_data: AudioData, elapsed_time: float):
        """Glitch art visualization with digital corruption effects"""
        color_manager = get_color_manager()
        color_manager.set_palette(ColorPalette.CYBERPUNK)
        color_manager.set_ascii_set(ASCIISet.DENSE)
        
        canvas.clear()
        
        if audio_data is None:
            return
        
        # Audio analysis for glitch intensity
        max_intensity = np.max(audio_data.amplitudes) if len(audio_data.amplitudes) > 0 else 0
        avg_intensity = np.mean(audio_data.amplitudes) if len(audio_data.amplitudes) > 0 else 0
        
        # Glitch parameters
        glitch_probability = avg_intensity * 0.5
        corruption_level = max_intensity
        
        # Draw base frequency bars with glitch effects
        bar_count = min(canvas.width // 2, len(audio_data.amplitudes))
        for i in range(bar_count):
            x = i * 2
            intensity = audio_data.amplitudes[i * len(audio_data.amplitudes) // bar_count]
            bar_height = int(intensity * canvas.height)
            
            # Draw normal bar
            for y in range(canvas.height - bar_height, canvas.height):
                if random.random() > glitch_probability:
                    char = get_char_for_intensity(intensity)
                    color = color_manager.get_color_for_intensity(intensity)
                else:
                    # Glitch character
                    glitch_chars = "█▓▒░!@#$%^&*()_+-=[]{}|;:,.<>?"
                    char = random.choice(glitch_chars)
                    color = random.choice(['bright_red', 'bright_cyan', 'bright_magenta', 'bright_yellow'])
                
                canvas.set_char(x, y, char, color)
                
                # Digital corruption - spread glitches
                if corruption_level > 0.8 and random.random() < 0.2:
                    for dx in [-1, 1]:
                        for dy in [-1, 0, 1]:
                            gx, gy = x + dx, y + dy
                            if 0 <= gx < canvas.width and 0 <= gy < canvas.height:
                                corrupt_char = random.choice("▓▒░▀▄█▌▐")
                                canvas.set_char(gx, gy, corrupt_char, 'bright_red')
        
        # Add scan lines and digital noise
        if random.random() < avg_intensity * 0.8:
            scan_line_y = random.randint(0, canvas.height - 1)
            for x in range(canvas.width):
                if random.random() < 0.7:
                    canvas.set_char(x, scan_line_y, '─', 'dim cyan')
        
        # Data corruption blocks
        if corruption_level > 0.6:
            num_blocks = int(corruption_level * 8)
            for _ in range(num_blocks):
                bx = random.randint(0, canvas.width - 5)
                by = random.randint(0, canvas.height - 3)
                block_chars = "████▓▓▓▓▒▒▒▒░░░░"
                
                for dx in range(4):
                    for dy in range(2):
                        if bx + dx < canvas.width and by + dy < canvas.height:
                            char = random.choice(block_chars)
                            color = random.choice(['red', 'bright_red', 'dim red'])
                            canvas.set_char(bx + dx, by + dy, char, color)