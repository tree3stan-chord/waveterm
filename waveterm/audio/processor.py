"""
Audio processing engine for Wave
Handles audio input, FFT analysis, and frequency data extraction
"""

import numpy as np
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except (ImportError, OSError) as e:
    AUDIO_AVAILABLE = False
    print(f"Warning: sounddevice not available - audio input disabled ({e})")
    sd = None
    
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available - file input disabled")
import threading
import queue
from typing import Optional, Tuple, Dict, Any
import time

class AudioData:
    """Container for processed audio data"""
    def __init__(self, frequencies: np.ndarray, amplitudes: np.ndarray, 
                 waveform: np.ndarray, sample_rate: int):
        self.frequencies = frequencies
        self.amplitudes = amplitudes  
        self.waveform = waveform
        self.sample_rate = sample_rate
        self.timestamp = time.time()
        
        # Derived data
        self.bass = np.mean(amplitudes[:len(amplitudes)//8])  # Low frequencies
        self.mid = np.mean(amplitudes[len(amplitudes)//8:len(amplitudes)//2])  # Mid frequencies  
        self.treble = np.mean(amplitudes[len(amplitudes)//2:])  # High frequencies
        self.overall_amplitude = np.mean(amplitudes)

class AudioProcessor:
    def __init__(self, source: str = "mic", file_path: Optional[str] = None, 
                 sensitivity: float = 1.0):
        self.source = source
        self.file_path = file_path
        self.sensitivity = sensitivity
        
        # Audio parameters
        self.sample_rate = 44100
        self.buffer_size = 2048
        self.hop_length = 512
        
        # Processing state
        self.running = False
        self.audio_buffer = queue.Queue(maxsize=10)
        self.current_data: Optional[AudioData] = None
        self.lock = threading.Lock()
        
        # For file playback
        self.audio_file_data: Optional[np.ndarray] = None
        self.file_position = 0
        
        # For microphone input
        self.stream: Optional[sd.InputStream] = None
        
    def initialize(self):
        """Initialize audio input source"""
        if self.source == "file":
            if not self.file_path:
                raise ValueError("File path required for file input")
            self._load_audio_file()
        elif self.source == "mic":
            self._setup_microphone()
        else:
            raise ValueError(f"Unknown audio source: {self.source}")
            
    def _load_audio_file(self):
        """Load audio file for playback"""
        try:
            self.audio_file_data, self.sample_rate = librosa.load(
                self.file_path, sr=self.sample_rate, mono=True
            )
            print(f"Loaded audio file: {self.file_path} ({len(self.audio_file_data)/self.sample_rate:.1f}s)")
        except Exception as e:
            raise RuntimeError(f"Failed to load audio file: {e}")
    
    def _setup_microphone(self):
        """Setup microphone input stream"""
        try:
            # Check available devices
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            print(f"Using microphone: {default_input['name']}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup microphone: {e}")
    
    def _microphone_callback(self, indata, frames, time, status):
        """Callback for microphone audio stream"""
        if status:
            print(f"Audio input status: {status}")
            
        # Convert to mono if stereo
        if indata.shape[1] > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata[:, 0]
            
        # Add to processing queue
        if not self.audio_buffer.full():
            self.audio_buffer.put(audio_data.copy())
    
    def start_processing(self):
        """Start audio processing thread"""
        self.running = True
        
        if self.source == "mic":
            # Start microphone stream
            self.stream = sd.InputStream(
                callback=self._microphone_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size
            )
            self.stream.start()
            
        # Processing loop
        while self.running:
            try:
                if self.source == "mic":
                    self._process_microphone_data()
                elif self.source == "file":
                    self._process_file_data()
                    
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                print(f"Error in audio processing: {e}")
                break
    
    def _process_microphone_data(self):
        """Process microphone input data"""
        try:
            # Get audio data from queue
            audio_chunk = self.audio_buffer.get(timeout=0.1)
            self._analyze_audio(audio_chunk)
        except queue.Empty:
            pass
    
    def _process_file_data(self):
        """Process audio file data"""
        if self.audio_file_data is None:
            return
            
        # Get chunk from file
        chunk_size = self.buffer_size
        if self.file_position + chunk_size >= len(self.audio_file_data):
            # Loop back to beginning
            self.file_position = 0
            
        audio_chunk = self.audio_file_data[self.file_position:self.file_position + chunk_size]
        self.file_position += self.hop_length
        
        self._analyze_audio(audio_chunk)
        
        # Control playback speed (roughly real-time)
        time.sleep(self.hop_length / self.sample_rate)
    
    def _analyze_audio(self, audio_chunk: np.ndarray):
        """Perform FFT analysis on audio chunk"""
        if len(audio_chunk) < self.buffer_size:
            # Pad with zeros if chunk is too small
            padded = np.zeros(self.buffer_size)
            padded[:len(audio_chunk)] = audio_chunk
            audio_chunk = padded
            
        # Apply window function to reduce spectral leakage
        windowed = audio_chunk * np.hanning(len(audio_chunk))
        
        # Perform FFT
        fft = np.fft.rfft(windowed)
        amplitudes = np.abs(fft)
        
        # Apply sensitivity scaling
        amplitudes *= self.sensitivity
        
        # Generate frequency bins
        frequencies = np.fft.rfftfreq(len(windowed), 1/self.sample_rate)
        
        # Normalize amplitudes (0-1 range)
        if np.max(amplitudes) > 0:
            amplitudes = amplitudes / np.max(amplitudes)
        
        # Create AudioData object
        audio_data = AudioData(
            frequencies=frequencies,
            amplitudes=amplitudes,
            waveform=audio_chunk,
            sample_rate=self.sample_rate
        )
        
        # Thread-safe update
        with self.lock:
            self.current_data = audio_data
    
    def get_current_data(self) -> Optional[AudioData]:
        """Get the most recent audio analysis data"""
        with self.lock:
            return self.current_data
    
    def stop(self):
        """Stop audio processing"""
        self.running = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
    
    def get_frequency_bands(self, num_bands: int = 32) -> Optional[np.ndarray]:
        """Get frequency data divided into bands for visualization"""
        data = self.get_current_data()
        if data is None:
            return None
            
        # Divide frequency spectrum into bands
        band_size = len(data.amplitudes) // num_bands
        bands = []
        
        for i in range(num_bands):
            start_idx = i * band_size
            end_idx = min((i + 1) * band_size, len(data.amplitudes))
            band_amplitude = np.mean(data.amplitudes[start_idx:end_idx])
            bands.append(band_amplitude)
            
        return np.array(bands)