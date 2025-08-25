"""
Basic visualization modes for Wave
Simple but effective audio-reactive visualizations
"""

import numpy as np
import random
import math
from typing import List, Tuple
try:
    from ..audio.processor import AudioData
except ImportError:
    # For testing without audio dependencies
    pass
from ..render.terminal import VisualizationData, TerminalRenderer

class BasicVisualizations:
    """Collection of basic visualization modes"""
    
    def __init__(self):
        self.matrix_drops: List[int] = []
        self.particles: List[Dict] = []
        self.matrix_chars = "0123456789ABCDEFアイウエオカキクケコサシスセソタチツテト"
        
    def frequency_bars(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Classic frequency spectrum bars visualization"""
        if audio_data is None:
            return
            
        # Get frequency bands for bars
        num_bars = min(canvas.width - 2, 64)
        bands = np.zeros(num_bars)
        
        if len(audio_data.amplitudes) > 0:
            # Divide frequency spectrum into bands
            band_size = len(audio_data.amplitudes) // num_bars
            
            for i in range(num_bars):
                start_idx = i * band_size
                end_idx = min((i + 1) * band_size, len(audio_data.amplitudes))
                if end_idx > start_idx:
                    bands[i] = np.mean(audio_data.amplitudes[start_idx:end_idx])
        
        # Draw bars
        bar_width = canvas.width / num_bars
        max_height = canvas.height - 4
        
        for i, amplitude in enumerate(bands):
            bar_height = int(amplitude * max_height)
            x = int(i * bar_width) + 1
            
            # Choose color based on frequency range
            if i < num_bars * 0.3:  # Bass
                color = 'red'
                char = '█'
            elif i < num_bars * 0.7:  # Mid
                color = 'green' 
                char = '▓'
            else:  # Treble
                color = 'blue'
                char = '▒'
                
            # Draw bar from bottom up
            for y in range(max_height - bar_height, max_height):
                if y >= 0 and x < canvas.width:
                    # Use different characters for different intensities
                    intensity = (max_height - y) / max_height
                    if intensity > 0.8:
                        canvas.set_char(x, y, '█', color)
                    elif intensity > 0.6:
                        canvas.set_char(x, y, '▓', color)
                    elif intensity > 0.4:
                        canvas.set_char(x, y, '▒', color)
                    else:
                        canvas.set_char(x, y, '░', color)
        
        # Add info text
        info = f"BARS | Bass: {audio_data.bass:.2f} | Mid: {audio_data.mid:.2f} | Treble: {audio_data.treble:.2f}"
        for i, char in enumerate(info[:canvas.width]):
            canvas.set_char(i, canvas.height - 1, char, 'white')
    
    def waveform(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Oscilloscope-style waveform display"""
        if audio_data is None or len(audio_data.waveform) == 0:
            return
            
        # Sample waveform data to fit canvas width
        waveform = audio_data.waveform
        samples_per_pixel = max(1, len(waveform) // (canvas.width - 2))
        
        center_y = canvas.height // 2
        scale = (canvas.height - 4) // 2
        
        prev_y = center_y
        
        for x in range(1, canvas.width - 1):
            # Get sample index
            sample_idx = x * samples_per_pixel
            if sample_idx < len(waveform):
                # Calculate y position
                sample = waveform[sample_idx] 
                y = center_y + int(sample * scale)
                y = max(1, min(canvas.height - 2, y))
                
                # Draw line from previous point
                if abs(y - prev_y) <= 1:
                    canvas.set_char(x, y, '█', 'cyan')
                else:
                    # Draw connecting line for large jumps
                    steps = abs(y - prev_y)
                    for step in range(steps + 1):
                        interp_y = prev_y + ((y - prev_y) * step // steps)
                        if 0 <= interp_y < canvas.height:
                            canvas.set_char(x, interp_y, '▒', 'cyan')
                
                prev_y = y
        
        # Draw center line
        for x in range(canvas.width):
            canvas.set_char(x, center_y, '·', 'white')
            
        # Add amplitude indicator
        amplitude_bar_height = int(audio_data.overall_amplitude * 10)
        for y in range(amplitude_bar_height):
            canvas.set_char(0, canvas.height - 1 - y, '|', 'bright_yellow')
    
    def matrix_rain(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Matrix-style falling character rain"""
        # Initialize drops for each column
        if len(self.matrix_drops) != canvas.width:
            self.matrix_drops = [random.randint(-50, 0) for _ in range(canvas.width)]
        
        # Clear canvas with fading effect
        for y in range(canvas.height):
            for x in range(canvas.width):
                current = canvas.get_char(x, y)
                if current != ' ':
                    # Fade characters over time
                    fade_chars = ['█', '▓', '▒', '░', ' ']
                    try:
                        current_idx = fade_chars.index(current)
                        if current_idx < len(fade_chars) - 1:
                            canvas.set_char(x, y, fade_chars[current_idx + 1], 'green')
                    except ValueError:
                        canvas.set_char(x, y, '░', 'green')
        
        # Update drops based on audio
        bass_boost = int(audio_data.bass * 5) if audio_data else 0
        drop_speed = 1 + bass_boost
        
        for col in range(canvas.width):
            # Move drop down
            self.matrix_drops[col] += drop_speed
            
            # Draw characters for this drop
            if self.matrix_drops[col] > 0:
                drop_pos = self.matrix_drops[col]
                
                # Draw falling characters
                for i in range(min(8, canvas.height)):
                    y = drop_pos - i
                    if 0 <= y < canvas.height:
                        char = random.choice(self.matrix_chars)
                        
                        # Brighten characters based on audio intensity
                        if audio_data and audio_data.overall_amplitude > 0.7:
                            color = 'bright_green'
                        elif i == 0:  # Leading character
                            color = 'white'
                        else:
                            color = 'green'
                            
                        canvas.set_char(col, y, char, color)
            
            # Reset drop when it goes off screen
            if self.matrix_drops[col] > canvas.height + 10:
                self.matrix_drops[col] = random.randint(-20, -1)
                
    def particle_field(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """ASCII particle field that reacts to audio"""
        # Initialize particles
        max_particles = 100
        if len(self.particles) < max_particles:
            for _ in range(max_particles - len(self.particles)):
                self.particles.append({
                    'x': random.uniform(0, canvas.width - 1),
                    'y': random.uniform(0, canvas.height - 1),
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'life': random.uniform(50, 100),
                    'char': random.choice('·•*★✦✧⋆'),
                    'size': random.choice([1, 2])
                })
        
        # Update particles
        audio_intensity = audio_data.overall_amplitude if audio_data else 0
        
        for particle in self.particles[:]:
            # Move particle
            particle['x'] += particle['vx'] * (1 + audio_intensity)
            particle['y'] += particle['vy'] * (1 + audio_intensity)
            
            # Add audio-reactive turbulence
            if audio_data:
                particle['vx'] += (random.random() - 0.5) * audio_data.bass * 0.5
                particle['vy'] += (random.random() - 0.5) * audio_data.treble * 0.5
            
            # Boundary conditions
            if particle['x'] < 0 or particle['x'] >= canvas.width:
                particle['vx'] *= -0.8
                particle['x'] = max(0, min(canvas.width - 1, particle['x']))
                
            if particle['y'] < 0 or particle['y'] >= canvas.height:
                particle['vy'] *= -0.8  
                particle['y'] = max(0, min(canvas.height - 1, particle['y']))
            
            # Update life
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
                
            # Draw particle
            x, y = int(particle['x']), int(particle['y'])
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                # Color based on velocity and audio
                speed = math.sqrt(particle['vx']**2 + particle['vy']**2)
                if speed > 3:
                    color = 'bright_yellow'
                elif speed > 2:
                    color = 'yellow'
                elif audio_intensity > 0.6:
                    color = 'cyan'
                else:
                    color = 'white'
                    
                canvas.set_char(x, y, particle['char'], color)
    
    def circular_wave(self, canvas: VisualizationData, audio_data: AudioData, time: float):
        """Circular frequency display radiating from center"""
        if audio_data is None:
            return
            
        center_x = canvas.width // 2
        center_y = canvas.height // 2
        max_radius = min(center_x, center_y) - 2
        
        # Get frequency bands
        num_bands = 36  # 10 degree increments
        bands = np.zeros(num_bands)
        
        if len(audio_data.amplitudes) > 0:
            band_size = len(audio_data.amplitudes) // num_bands
            for i in range(num_bands):
                start_idx = i * band_size
                end_idx = min((i + 1) * band_size, len(audio_data.amplitudes))
                if end_idx > start_idx:
                    bands[i] = np.mean(audio_data.amplitudes[start_idx:end_idx])
        
        # Draw circular waves
        for i, amplitude in enumerate(bands):
            angle = (i / num_bands) * 2 * math.pi + time * 0.5
            
            # Multiple rings at different radii
            for ring in range(3):
                base_radius = (ring + 1) * max_radius // 4
                radius = base_radius + int(amplitude * max_radius // 4)
                
                # Calculate position
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle) * 0.5)  # Squish vertically
                
                if 0 <= x < canvas.width and 0 <= y < canvas.height:
                    # Character and color based on frequency and ring
                    if i < num_bands * 0.3:  # Bass
                        char = '█' if ring == 0 else '▓'
                        color = 'red'
                    elif i < num_bands * 0.7:  # Mid
                        char = '▒' if ring == 0 else '░'
                        color = 'green'
                    else:  # Treble
                        char = '·' if ring == 0 else '•'
                        color = 'blue'
                        
                    canvas.set_char(x, y, char, color)
        
        # Draw center dot
        canvas.set_char(center_x, center_y, '●', 'white')