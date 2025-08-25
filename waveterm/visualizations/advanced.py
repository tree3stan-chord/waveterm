"""
Advanced visualization modes for Wave
More complex audio-reactive visualizations
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

class AdvancedVisualizations:
    """Collection of advanced visualization modes"""
    
    def __init__(self):
        self.stars: List[Dict] = []
        self.fire_particles: List[Dict] = []
        self.ocean_wave_data: List[float] = []
        self.neural_nodes: List[Dict] = []
        self.dna_rotation = 0.0
        
    def starfield_warp(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Stars flying toward screen, faster with audio intensity"""
        # Initialize stars
        max_stars = 200
        if len(self.stars) < max_stars:
            for _ in range(max_stars - len(self.stars)):
                self.stars.append({
                    'x': random.uniform(-canvas.width, canvas.width),
                    'y': random.uniform(-canvas.height, canvas.height),
                    'z': random.uniform(1, 100),
                    'speed': random.uniform(0.5, 2.0)
                })
        
        center_x = canvas.width // 2
        center_y = canvas.height // 2
        
        # Audio reactive speed multiplier
        warp_factor = 1.0 + (audio_data.overall_amplitude * 3.0 if audio_data else 0)
        
        for star in self.stars[:]:
            # Move star toward viewer
            star['z'] -= star['speed'] * warp_factor
            
            if star['z'] <= 0:
                # Reset star to back
                star['z'] = 100
                star['x'] = random.uniform(-canvas.width, canvas.width)
                star['y'] = random.uniform(-canvas.height, canvas.height)
                continue
                
            # Project 3D to 2D
            screen_x = center_x + int(star['x'] / star['z'] * center_x)
            screen_y = center_y + int(star['y'] / star['z'] * center_y)
            
            if 0 <= screen_x < canvas.width and 0 <= screen_y < canvas.height:
                # Star appearance based on distance and audio
                if star['z'] < 10:
                    char = '█'
                    color = 'white'
                elif star['z'] < 30:
                    char = '●' if audio_data and audio_data.overall_amplitude > 0.5 else '•'
                    color = 'bright_cyan' if warp_factor > 2 else 'cyan'
                elif star['z'] < 60:
                    char = '•'
                    color = 'blue'
                else:
                    char = '·'
                    color = 'blue'
                    
                canvas.set_char(screen_x, screen_y, char, color)
    
    def fire_flames(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """ASCII fire effect that reacts to audio"""
        # Initialize fire particles
        max_particles = 150
        if len(self.fire_particles) < max_particles:
            for _ in range(max_particles - len(self.fire_particles)):
                self.fire_particles.append({
                    'x': random.uniform(0, canvas.width),
                    'y': canvas.height - 1,
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(-2, -0.5),
                    'life': random.randint(20, 60),
                    'intensity': random.uniform(0.3, 1.0)
                })
        
        # Add new particles based on audio intensity
        audio_intensity = audio_data.overall_amplitude if audio_data else 0.2
        new_particles = int(audio_intensity * 10)
        
        for _ in range(new_particles):
            if len(self.fire_particles) < max_particles:
                self.fire_particles.append({
                    'x': random.uniform(canvas.width * 0.2, canvas.width * 0.8),
                    'y': canvas.height - 1,
                    'vx': random.uniform(-1, 1) * audio_intensity,
                    'vy': random.uniform(-3, -1) * (1 + audio_intensity),
                    'life': random.randint(30, 80),
                    'intensity': audio_intensity
                })
        
        # Update particles
        for particle in self.fire_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['intensity'] *= 0.98
            
            # Add some turbulence
            particle['vx'] += random.uniform(-0.1, 0.1)
            particle['vy'] += random.uniform(-0.1, 0.1)
            
            if particle['life'] <= 0 or particle['y'] < 0:
                self.fire_particles.remove(particle)
                continue
                
            # Draw particle
            x, y = int(particle['x']), int(particle['y'])
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Color and character based on intensity and life
                life_ratio = particle['life'] / 60.0
                intensity = particle['intensity'] * life_ratio
                
                if intensity > 0.8:
                    char, color = '█', 'bright_yellow'
                elif intensity > 0.6:
                    char, color = '▓', 'yellow' 
                elif intensity > 0.4:
                    char, color = '▒', 'red'
                elif intensity > 0.2:
                    char, color = '░', 'red'
                else:
                    char, color = '·', 'red'
                    
                canvas.set_char(x, y, char, color)
    
    def ocean_waves(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Wave interference patterns"""
        if not self.ocean_wave_data:
            self.ocean_wave_data = [0.0] * canvas.width
        
        # Generate wave data
        wave_data = []
        for x in range(canvas.width):
            # Multiple sine waves with different frequencies
            wave = 0
            
            # Base wave
            wave += math.sin(x * 0.1 + time * 2) * 0.3
            
            # Audio-reactive waves
            if audio_data:
                # Bass wave (slow, big)
                wave += math.sin(x * 0.05 + time * 1.5) * audio_data.bass * 0.5
                
                # Mid wave (medium)
                wave += math.sin(x * 0.15 + time * 3) * audio_data.mid * 0.3
                
                # Treble wave (fast, small)
                wave += math.sin(x * 0.25 + time * 5) * audio_data.treble * 0.2
            
            wave_data.append(wave)
        
        # Draw waves
        center_y = canvas.height // 2
        amplitude = canvas.height // 4
        
        for x in range(canvas.width):
            wave_height = wave_data[x]
            y = center_y + int(wave_height * amplitude)
            y = max(0, min(canvas.height - 1, y))
            
            # Draw wave with varying intensity
            intensity = abs(wave_height)
            if intensity > 0.8:
                char, color = '█', 'bright_cyan'
            elif intensity > 0.6:
                char, color = '▓', 'cyan'
            elif intensity > 0.4:
                char, color = '▒', 'blue'
            elif intensity > 0.2:
                char, color = '░', 'blue'
            else:
                char, color = '·', 'blue'
                
            canvas.set_char(x, y, char, color)
            
            # Add foam effects for high intensity
            if audio_data and audio_data.overall_amplitude > 0.7:
                foam_y = y - 1 if wave_height < 0 else y + 1
                if 0 <= foam_y < canvas.height:
                    canvas.set_char(x, foam_y, '~', 'white')
    
    def dna_helix(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Rotating DNA double helix"""
        self.dna_rotation += 0.1 + (audio_data.overall_amplitude * 0.2 if audio_data else 0)
        
        center_x = canvas.width // 2
        height = canvas.height - 2
        
        # Draw DNA strands
        for y in range(height):
            # Two helices offset by pi
            angle1 = (y * 0.3 + self.dna_rotation)
            angle2 = angle1 + math.pi
            
            # Calculate positions
            radius = 8 + (audio_data.bass * 5 if audio_data else 0)
            
            x1 = center_x + int(radius * math.cos(angle1))
            x2 = center_x + int(radius * math.cos(angle2))
            
            # Draw strand points
            if 0 <= x1 < canvas.width:
                # Color based on audio frequency content
                if audio_data and audio_data.bass > 0.5:
                    color = 'red'
                elif audio_data and audio_data.mid > 0.5:
                    color = 'green'
                else:
                    color = 'blue'
                    
                canvas.set_char(x1, y, '●', color)
                
            if 0 <= x2 < canvas.width:
                canvas.set_char(x2, y, '●', 'cyan')
            
            # Draw connecting bonds every few units
            if y % 6 == 0 and 0 <= x1 < canvas.width and 0 <= x2 < canvas.width:
                # Draw line between strands
                start_x, end_x = (x1, x2) if x1 < x2 else (x2, x1)
                for x in range(start_x + 1, end_x):
                    if 0 <= x < canvas.width:
                        char = '-' if abs(x1 - x2) > 4 else '='
                        canvas.set_char(x, y, char, 'white')
    
    def neural_network(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Neural network visualization with pulsing connections"""
        # Initialize nodes
        if not self.neural_nodes:
            num_nodes = 15
            for _ in range(num_nodes):
                self.neural_nodes.append({
                    'x': random.randint(2, canvas.width - 2),
                    'y': random.randint(2, canvas.height - 2),
                    'activation': random.uniform(0, 1),
                    'pulse_phase': random.uniform(0, 2 * math.pi)
                })
        
        # Update node activations based on audio
        if audio_data:
            for i, node in enumerate(self.neural_nodes):
                # Different nodes respond to different frequency ranges
                if i % 3 == 0:
                    node['activation'] = audio_data.bass
                elif i % 3 == 1:
                    node['activation'] = audio_data.mid
                else:
                    node['activation'] = audio_data.treble
                    
                node['pulse_phase'] += 0.2
        
        # Draw connections between nearby nodes
        for i, node1 in enumerate(self.neural_nodes):
            for j, node2 in enumerate(self.neural_nodes[i+1:], i+1):
                distance = math.sqrt((node1['x'] - node2['x'])**2 + (node1['y'] - node2['y'])**2)
                
                if distance < 15:  # Only connect nearby nodes
                    # Connection strength based on activation and distance
                    strength = (node1['activation'] + node2['activation']) / 2
                    strength *= (1.0 - distance / 15)
                    
                    if strength > 0.3:
                        # Draw connection line
                        steps = int(distance)
                        for step in range(steps):
                            t = step / max(1, steps - 1)
                            x = int(node1['x'] + t * (node2['x'] - node1['x']))
                            y = int(node1['y'] + t * (node2['y'] - node1['y']))
                            
                            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                                # Pulsing connection
                                pulse = math.sin(time * 3 + step * 0.1) * 0.5 + 0.5
                                if pulse * strength > 0.4:
                                    char = '·' if strength < 0.6 else '-'
                                    color = 'cyan' if strength > 0.7 else 'blue'
                                    canvas.set_char(x, y, char, color)
        
        # Draw nodes
        for node in self.neural_nodes:
            x, y = int(node['x']), int(node['y'])
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Node appearance based on activation
                pulse = math.sin(node['pulse_phase']) * 0.5 + 0.5
                activation = node['activation'] * pulse
                
                if activation > 0.8:
                    char, color = '●', 'bright_yellow'
                elif activation > 0.6:
                    char, color = '●', 'yellow'
                elif activation > 0.4:
                    char, color = '•', 'green'
                elif activation > 0.2:
                    char, color = '•', 'blue'
                else:
                    char, color = '·', 'white'
                    
                canvas.set_char(x, y, char, color)