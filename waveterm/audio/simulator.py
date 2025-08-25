"""
Audio simulation system for headless environments
Generates realistic audio data without requiring actual audio input
"""

import numpy as np
import math
import random
import time
from typing import Optional, List
from .processor import AudioData

class AudioPattern:
    """Represents a musical pattern for simulation"""
    
    def __init__(self, name: str, bpm: int = 120):
        self.name = name
        self.bpm = bpm
        self.beat_duration = 60.0 / bpm
        self.start_time = time.time()
    
    def get_beat_phase(self) -> float:
        """Get current beat phase (0-1)"""
        elapsed = time.time() - self.start_time
        return (elapsed / self.beat_duration) % 1.0
    
    def get_measure_phase(self) -> float:
        """Get current measure phase (4 beats)"""
        elapsed = time.time() - self.start_time
        return (elapsed / (self.beat_duration * 4)) % 1.0

class AudioSimulator:
    """Simulates realistic audio data for visualization testing"""
    
    def __init__(self, pattern: str = "electronic", sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.buffer_size = 2048
        self.pattern_name = pattern
        self.pattern = self._create_pattern(pattern)
        self.time_offset = 0.0
        
        # Frequency bins for FFT simulation
        self.frequencies = np.fft.rfftfreq(self.buffer_size, 1/sample_rate)
        self.num_bins = len(self.frequencies)
        
        # Pattern variations
        self.variation_timer = 0.0
        self.current_variation = 0
        
    def _create_pattern(self, pattern_type: str) -> AudioPattern:
        """Create audio pattern based on type"""
        patterns = {
            "electronic": AudioPattern("Electronic", 128),
            "rock": AudioPattern("Rock", 120), 
            "ambient": AudioPattern("Ambient", 60),
            "jazz": AudioPattern("Jazz", 140),
            "dubstep": AudioPattern("Dubstep", 140),
            "classical": AudioPattern("Classical", 100),
            "techno": AudioPattern("Techno", 130),
            "chill": AudioPattern("Chill", 90)
        }
        return patterns.get(pattern_type, patterns["electronic"])
    
    def generate_audio_data(self) -> AudioData:
        """Generate realistic audio data based on current pattern"""
        # Update time
        self.time_offset += 1/30  # ~30 FPS update rate
        
        # Get pattern timing
        beat_phase = self.pattern.get_beat_phase()
        measure_phase = self.pattern.get_measure_phase()
        
        # Generate frequency spectrum based on pattern
        amplitudes = self._generate_frequency_spectrum(beat_phase, measure_phase)
        
        # Generate waveform
        waveform = self._generate_waveform(beat_phase, measure_phase)
        
        # Create AudioData object
        audio_data = AudioData(
            frequencies=self.frequencies,
            amplitudes=amplitudes,
            waveform=waveform,
            sample_rate=self.sample_rate
        )
        
        return audio_data
    
    def _generate_frequency_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Generate realistic frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        if self.pattern_name == "electronic":
            return self._electronic_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "rock":
            return self._rock_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "ambient":
            return self._ambient_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "jazz":
            return self._jazz_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "dubstep":
            return self._dubstep_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "classical":
            return self._classical_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "techno":
            return self._techno_spectrum(beat_phase, measure_phase)
        elif self.pattern_name == "chill":
            return self._chill_spectrum(beat_phase, measure_phase)
        else:
            return self._electronic_spectrum(beat_phase, measure_phase)
    
    def _electronic_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Electronic music frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        # Kick drum on beats
        if beat_phase < 0.1:
            # Strong bass for kick
            bass_range = self.num_bins // 8
            for i in range(bass_range):
                amplitudes[i] = 0.8 * (1 - beat_phase * 10) * (1 - i / bass_range)
        
        # Hi-hats
        if beat_phase > 0.5 and beat_phase < 0.6:
            treble_start = self.num_bins * 3 // 4
            for i in range(treble_start, self.num_bins):
                amplitudes[i] = 0.4 * random.uniform(0.7, 1.0)
        
        # Synth lead
        lead_freq_idx = int(self.num_bins * (0.3 + 0.2 * math.sin(measure_phase * 4 * math.pi)))
        for i in range(max(0, lead_freq_idx - 20), min(self.num_bins, lead_freq_idx + 20)):
            distance = abs(i - lead_freq_idx)
            amplitudes[i] = max(amplitudes[i], 0.6 * math.exp(-distance / 10))
        
        # Background texture
        for i in range(self.num_bins):
            amplitudes[i] += random.uniform(0, 0.1) * (0.5 + 0.5 * math.sin(self.time_offset))
        
        return np.clip(amplitudes, 0, 1)
    
    def _rock_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Rock music frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        # Drums
        if beat_phase < 0.15:
            # Kick + snare
            bass_range = self.num_bins // 6
            mid_range = self.num_bins // 3
            
            for i in range(bass_range):
                amplitudes[i] = 0.9 * (1 - beat_phase * 6)
            for i in range(bass_range, mid_range):
                amplitudes[i] = 0.7 * (1 - beat_phase * 6)
        
        # Guitar power chords
        chord_fundamentals = [150, 200, 250, 300]  # Hz roughly
        for freq_hz in chord_fundamentals:
            freq_idx = int(freq_hz * self.num_bins / (self.sample_rate / 2))
            if freq_idx < self.num_bins:
                # Add harmonics
                for harmonic in range(1, 4):
                    harm_idx = freq_idx * harmonic
                    if harm_idx < self.num_bins:
                        intensity = 0.6 / harmonic * (0.7 + 0.3 * math.sin(measure_phase * 2 * math.pi))
                        amplitudes[harm_idx] = max(amplitudes[harm_idx], intensity)
        
        # Cymbals
        if random.random() < 0.1:
            treble_start = self.num_bins * 2 // 3
            for i in range(treble_start, self.num_bins):
                amplitudes[i] = random.uniform(0.3, 0.7)
        
        return np.clip(amplitudes, 0, 1)
    
    def _ambient_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Ambient music frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        # Slow evolving pads
        for i in range(self.num_bins):
            freq_norm = i / self.num_bins
            
            # Multiple slow-moving sine waves
            wave1 = 0.3 * (0.5 + 0.5 * math.sin(self.time_offset * 0.7 + freq_norm * 8))
            wave2 = 0.2 * (0.5 + 0.5 * math.sin(self.time_offset * 0.5 + freq_norm * 12))
            wave3 = 0.1 * (0.5 + 0.5 * math.sin(self.time_offset * 0.3 + freq_norm * 6))
            
            # Emphasize lower frequencies
            freq_falloff = math.exp(-freq_norm * 3)
            
            amplitudes[i] = (wave1 + wave2 + wave3) * freq_falloff
        
        return np.clip(amplitudes, 0, 1)
    
    def _dubstep_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Dubstep frequency spectrum with wobbles and drops"""
        amplitudes = np.zeros(self.num_bins)
        
        # Drop every 4 beats
        is_drop = measure_phase > 0.5
        
        if is_drop:
            # Wobble bass
            wobble_freq = 20 * (1 + math.sin(self.time_offset * 8))  # Hz
            wobble_idx = int(wobble_freq * self.num_bins / (self.sample_rate / 2))
            
            for i in range(max(0, wobble_idx - 50), min(self.num_bins // 4, wobble_idx + 50)):
                distance = abs(i - wobble_idx)
                amplitudes[i] = 0.9 * math.exp(-distance / 20)
            
            # Snare hits
            if beat_phase < 0.05:
                mid_start = self.num_bins // 4
                mid_end = self.num_bins // 2
                for i in range(mid_start, mid_end):
                    amplitudes[i] = max(amplitudes[i], 0.8 * (1 - beat_phase * 20))
        else:
            # Build-up
            buildup_intensity = measure_phase * 2  # 0 to 1 over half measure
            
            # Rising sweep
            sweep_idx = int(self.num_bins * buildup_intensity * 0.8)
            for i in range(sweep_idx):
                amplitudes[i] = 0.5 * buildup_intensity
        
        return np.clip(amplitudes, 0, 1)
    
    def _classical_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Classical music frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        # Orchestra instruments - multiple harmonic series
        fundamental_freqs = [110, 147, 196, 262, 330, 392, 523]  # Musical notes
        
        for freq_hz in fundamental_freqs:
            freq_idx = int(freq_hz * self.num_bins / (self.sample_rate / 2))
            if freq_idx < self.num_bins:
                # Add harmonic series
                for harmonic in range(1, 8):
                    harm_idx = freq_idx * harmonic
                    if harm_idx < self.num_bins:
                        # Natural harmonic decay
                        intensity = (0.7 / harmonic) * (0.8 + 0.2 * math.sin(measure_phase * math.pi))
                        amplitudes[harm_idx] = max(amplitudes[harm_idx], intensity)
        
        # Strings texture
        for i in range(self.num_bins // 4, self.num_bins // 2):
            amplitudes[i] += 0.1 * random.uniform(0.5, 1.0)
        
        return np.clip(amplitudes, 0, 1)
    
    def _techno_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Techno music frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        # Four-on-the-floor kick
        if beat_phase < 0.08:
            bass_range = self.num_bins // 10
            for i in range(bass_range):
                amplitudes[i] = 0.95 * (1 - beat_phase * 12)
        
        # Constant hi-hat
        treble_start = self.num_bins * 3 // 4
        for i in range(treble_start, self.num_bins):
            amplitudes[i] = 0.3 * (0.8 + 0.2 * math.sin(beat_phase * 8 * math.pi))
        
        # Acid bassline
        bassline_freq = 80 + 40 * math.sin(measure_phase * 8 * math.pi)  # Hz
        bassline_idx = int(bassline_freq * self.num_bins / (self.sample_rate / 2))
        
        for i in range(max(0, bassline_idx - 15), min(self.num_bins // 4, bassline_idx + 15)):
            distance = abs(i - bassline_idx)
            amplitudes[i] = max(amplitudes[i], 0.7 * math.exp(-distance / 8))
        
        return np.clip(amplitudes, 0, 1)
    
    def _chill_spectrum(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Chill/Lo-fi music frequency spectrum"""
        amplitudes = np.zeros(self.num_bins)
        
        # Soft drums
        if beat_phase < 0.2:
            # Muffled kick
            for i in range(self.num_bins // 8):
                amplitudes[i] = 0.5 * (1 - beat_phase * 5) * math.exp(-i / 20)
        
        # Vinyl crackle
        for i in range(self.num_bins // 2, self.num_bins):
            if random.random() < 0.1:
                amplitudes[i] = random.uniform(0.1, 0.3)
        
        # Warm pad chords
        chord_freqs = [200, 250, 315, 400]  # Hz
        for freq_hz in chord_freqs:
            freq_idx = int(freq_hz * self.num_bins / (self.sample_rate / 2))
            if freq_idx < self.num_bins:
                for i in range(max(0, freq_idx - 10), min(self.num_bins, freq_idx + 10)):
                    distance = abs(i - freq_idx)
                    intensity = 0.4 * math.exp(-distance / 5) * (0.9 + 0.1 * math.sin(self.time_offset))
                    amplitudes[i] = max(amplitudes[i], intensity)
        
        return np.clip(amplitudes, 0, 1)
    
    def _generate_waveform(self, beat_phase: float, measure_phase: float) -> np.ndarray:
        """Generate realistic waveform data"""
        waveform = np.zeros(self.buffer_size)
        
        # Generate waveform based on pattern
        for i in range(self.buffer_size):
            t = i / self.sample_rate
            
            # Mix of different frequencies based on pattern
            signal = 0
            
            if self.pattern_name in ["electronic", "techno"]:
                # Sharp electronic sounds
                signal += 0.4 * np.sign(math.sin(2 * math.pi * 440 * t))  # Square wave
                signal += 0.3 * math.sin(2 * math.pi * 220 * t)  # Sine wave
            elif self.pattern_name == "rock":
                # Distorted guitar-like
                base = math.sin(2 * math.pi * 220 * t)
                signal += 0.5 * np.tanh(base * 3)  # Soft distortion
            else:
                # Smooth waves
                signal += 0.4 * math.sin(2 * math.pi * 440 * t)
                signal += 0.3 * math.sin(2 * math.pi * 660 * t)
            
            # Add beat-synchronized elements
            if beat_phase < 0.1:
                signal += 0.6 * math.exp(-beat_phase * 50) * math.sin(2 * math.pi * 60 * t)
            
            waveform[i] = signal * (0.7 + 0.3 * math.sin(measure_phase * 2 * math.pi))
        
        return np.clip(waveform, -1, 1)
    
    def set_pattern(self, pattern_name: str) -> bool:
        """Change the audio pattern"""
        available_patterns = {
            "electronic", "rock", "ambient", "jazz", 
            "dubstep", "classical", "techno", "chill"
        }
        
        if pattern_name in available_patterns:
            self.pattern = self._create_pattern(pattern_name)
            self.pattern_name = pattern_name
            return True
        else:
            return False
    
    def get_available_patterns(self) -> List[str]:
        """Get list of available patterns"""
        return ["electronic", "rock", "ambient", "jazz", "dubstep", "classical", "techno", "chill"]