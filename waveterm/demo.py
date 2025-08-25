"""
Enhanced demo system for WaveTerm
Shows off all visualizations with simulated audio patterns
"""

import time
import random
from typing import List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

from .audio.simulator import AudioSimulator
from .render.terminal import TerminalRenderer
from .visualizations.registry import get_all_modes

console = Console()

class DemoRunner:
    """Advanced demo runner with multiple patterns and smooth transitions"""
    
    def __init__(self, duration: int = 30, cycle_time: int = 5):
        self.duration = duration
        self.cycle_time = cycle_time
        self.renderer = TerminalRenderer()
        
        # Get all available modes
        self.modes = list(get_all_modes().keys())
        self.mode_info = get_all_modes()
        
        # Audio simulators for different patterns  
        self.simulators = {
            'electronic': AudioSimulator('electronic'),
            'rock': AudioSimulator('rock'),
            'ambient': AudioSimulator('ambient'),
            'dubstep': AudioSimulator('dubstep'),
            'classical': AudioSimulator('classical'),
            'techno': AudioSimulator('techno'),
            'chill': AudioSimulator('chill')
        }
        
        # Demo sequence
        self.demo_sequence = self._create_demo_sequence()
        
    def _create_demo_sequence(self) -> List[Tuple[str, str, str]]:
        """Create an interesting sequence of mode/pattern combinations"""
        sequence = [
            # (mode, pattern, description)
            ('bars', 'electronic', 'Classic frequency bars with electronic beats'),
            ('matrix', 'techno', 'Matrix rain synchronized to techno rhythms'),
            ('fire', 'rock', 'ASCII flames dancing to rock music'),
            ('starfield', 'ambient', 'Peaceful starfield journey'),
            ('neural', 'dubstep', 'Neural network reacting to dubstep drops'),
            ('glitch', 'electronic', 'Digital corruption and glitch effects'),
            ('void', 'ambient', 'Lovecraftian tentacles in the void'),
            ('hypercube', 'classical', '4D geometry meets classical harmonies'),
            ('portal', 'dubstep', 'Interdimensional portal with bass wobbles'),
            ('fractal', 'chill', 'Growing fractal trees in lo-fi atmosphere'),
            ('ocean', 'ambient', 'Ocean wave interference patterns'),
            ('dna', 'electronic', 'DNA helix spinning to electronic music'),
            ('circle', 'jazz', 'Circular frequency display'),  
            ('particles', 'techno', 'Particle field mayhem'),
            ('wave', 'classical', 'Pure waveform visualization')
        ]
        
        # Shuffle for variety, but keep some structure
        random.shuffle(sequence)
        return sequence
    
    def run(self):
        """Run the complete demo experience"""
        try:
            self.renderer.initialize()
            
            # Demo intro
            self._show_intro()
            
            # Main demo loop
            start_time = time.time()
            sequence_index = 0
            last_switch = start_time
            
            while time.time() - start_time < self.duration:
                current_time = time.time()
                
                # Switch modes
                if current_time - last_switch >= self.cycle_time:
                    sequence_index = (sequence_index + 1) % len(self.demo_sequence)
                    last_switch = current_time
                
                # Get current demo step
                mode, pattern, description = self.demo_sequence[sequence_index]
                
                # Show visualization
                self._render_frame(mode, pattern, description)
                
                # Frame rate control
                time.sleep(1/30)  # 30 FPS
                
        except KeyboardInterrupt:
            pass
        finally:
            self.renderer.cleanup()
            self._show_outro()
    
    def _show_intro(self):
        """Show demo introduction"""
        intro_text = """
[bold cyan]🌊 WaveTerm Terminal Music Visualizer[/bold cyan]
[bold]Enhanced Demo Mode[/bold]

Featuring [green]{num_modes}[/green] visualization modes:
• [yellow]{basic}[/yellow] basic visualizations  
• [orange1]{advanced}[/orange1] advanced effects
• [red]{extreme}[/red] extreme/experimental modes

[dim]Each visualization runs for {cycle_time} seconds
Audio patterns: {patterns}
Total demo time: {duration} seconds

Press Ctrl+C to exit anytime[/dim]
        """.format(
            num_modes=len(self.modes),
            basic=len([m for m in self.mode_info.values() if m['category'] == 'basic']),
            advanced=len([m for m in self.mode_info.values() if m['category'] == 'advanced']), 
            extreme=len([m for m in self.mode_info.values() if m['category'] == 'extreme']),
            cycle_time=self.cycle_time,
            patterns=', '.join(self.simulators.keys()),
            duration=self.duration
        )
        
        console.print(Panel(intro_text, border_style="cyan"))
        time.sleep(3)
    
    def _render_frame(self, mode: str, pattern: str, description: str):
        """Render a single frame of the demo"""
        # Get simulator and generate audio data
        simulator = self.simulators[pattern]
        audio_data = simulator.generate_audio_data()
        
        # Get visualization function
        from .visualizations.registry import get_mode
        viz_func = get_mode(mode)
        
        if viz_func is None:
            return
            
        # Create and populate canvas
        canvas = self.renderer.create_canvas()
        
        try:
            viz_func(canvas, audio_data, time.time())
        except Exception as e:
            # Show error info instead of crashing
            error_text = f"Error in {mode}: {str(e)[:50]}..."
            for i, char in enumerate(error_text[:canvas.width]):
                canvas.set_char(i, 0, char, 'red')
        
        # Add info overlay
        self._add_info_overlay(canvas, mode, pattern, description, audio_data)
        
        # Render to terminal
        self.renderer.render(canvas)
    
    def _add_info_overlay(self, canvas, mode: str, pattern: str, description: str, audio_data):
        """Add informational overlay to the visualization"""
        # Mode info (top line)
        mode_info = self.mode_info.get(mode, {})
        mode_text = f"{mode_info.get('name', mode)} | {pattern.title()} | {mode_info.get('category', '').title()}"
        
        for i, char in enumerate(mode_text[:canvas.width]):
            canvas.set_char(i, 0, char, 'white')
        
        # Audio info (bottom line) 
        audio_text = f"Bass:{audio_data.bass:.2f} Mid:{audio_data.mid:.2f} Treble:{audio_data.treble:.2f} | {description[:30]}..."
        
        for i, char in enumerate(audio_text[:canvas.width]):
            canvas.set_char(i, canvas.height - 1, char, 'bright_black')
        
        # Progress indicator (right side)
        progress_chars = "▁▂▃▄▅▆▇█"
        bass_bar_height = min(8, int(audio_data.bass * 8))
        mid_bar_height = min(8, int(audio_data.mid * 8))
        treble_bar_height = min(8, int(audio_data.treble * 8))
        
        if canvas.width >= 3:
            # Bass indicator
            if bass_bar_height > 0:
                canvas.set_char(canvas.width - 3, canvas.height - 2, progress_chars[bass_bar_height - 1], 'red')
                
            # Mid indicator  
            if mid_bar_height > 0:
                canvas.set_char(canvas.width - 2, canvas.height - 2, progress_chars[mid_bar_height - 1], 'green')
                
            # Treble indicator
            if treble_bar_height > 0:
                canvas.set_char(canvas.width - 1, canvas.height - 2, progress_chars[treble_bar_height - 1], 'blue')
    
    def _show_outro(self):
        """Show demo conclusion"""
        outro_text = """
[bold green]🎵 WaveTerm Demo Complete![/bold green]

[bold]What's Next?[/bold]
• Try different modes: [cyan]waveterm run --mode glitch[/cyan]
• Check available modes: [cyan]waveterm modes[/cyan]  
• Configure settings: [cyan]waveterm config[/cyan]
• Install audio support: [cyan]pip install waveterm[audio][/cyan]
• Export visualizations: [cyan]waveterm export output.gif --mode fire[/cyan]

[dim]Thanks for exploring WaveTerm!
Visit the project page for more information and updates.[/dim]
        """
        
        console.print(Panel(outro_text, border_style="green"))

# Compatibility function for old demo script
def run_demo():
    """Run demo with default settings"""
    runner = DemoRunner()
    runner.run()