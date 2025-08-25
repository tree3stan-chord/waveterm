"""
Modern CLI interface for WaveTerm using Click
"""

import sys
import time
from pathlib import Path
from typing import Optional

import click
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import __version__
from .core.app import WaveApp
from .core.config import WaveConfig

console = Console()

@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx, version):
    """🌊 WaveTerm - Terminal Music Visualizer
    
    A modern terminal-based music visualizer with stunning ASCII art effects.
    Perfect for headless servers, development, and live performances.
    """
    if version:
        console.print(f"[bold cyan]WaveTerm[/bold cyan] version [bold]{__version__}[/bold]")
        sys.exit(0)
        
    if ctx.invoked_subcommand is None:
        # Default behavior - show help
        console.print(ctx.get_help())

@main.command()
@click.option("-m", "--mode", default="bars", 
              help="Visualization mode", 
              type=click.Choice([
                  'bars', 'wave', 'matrix', 'particles', 'circle',
                  'starfield', 'fire', 'ocean', 'dna', 'neural',
                  'glitch', 'void', 'hypercube', 'fractal', 'portal'
              ]))
@click.option("-i", "--input", default="sim", 
              type=click.Choice(['mic', 'file', 'sim']),
              help="Audio input source")
@click.option("-f", "--file", type=click.Path(exists=True),
              help="Audio file path (for file input)")
@click.option("--fps", default=30, help="Target FPS")
@click.option("--sensitivity", default=1.0, help="Audio sensitivity")
@click.option("--config", type=click.Path(), help="Config file path")
@click.option("--headless", is_flag=True, help="Run in headless mode")
@click.option("--export", help="Export frames to directory")
def run(mode, input, file, fps, sensitivity, config, headless, export):
    """Run WaveTerm visualizer"""
    
    if input == "file" and not file:
        console.print("[red]Error:[/red] --file required when using file input")
        sys.exit(1)
    
    # Load config
    config_obj = WaveConfig.load(config) if config else WaveConfig()
    
    try:
        app = WaveApp(
            mode=mode,
            input_source=input,
            file_path=file,
            fps=fps,
            sensitivity=sensitivity,
            config=config_obj,
            headless=headless,
            export_dir=export
        )
        
        console.print(f"[green]🎵 Starting WaveTerm[/green] - Mode: [bold]{mode}[/bold], Input: [bold]{input}[/bold]")
        if headless:
            console.print("[yellow]Running in headless mode - no audio required[/yellow]")
        console.print("Press [bold]Ctrl+C[/bold] to exit")
        
        app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 WaveTerm stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

@main.command()
@click.option("--duration", default=30, help="Demo duration in seconds")
@click.option("--cycle-time", default=5, help="Seconds per visualization")
def demo(duration, cycle_time):
    """Run WaveTerm demo (no audio required)"""
    from .demo import DemoRunner
    
    console.print("[bold cyan]🌊 WaveTerm Demo Mode[/bold cyan]")
    console.print("Showcasing visualizations without audio input\n")
    
    runner = DemoRunner(duration=duration, cycle_time=cycle_time)
    runner.run()

@main.command()
def modes():
    """List available visualization modes"""
    from .visualizations.registry import get_all_modes
    
    modes_data = get_all_modes()
    
    table = Table(title="🎨 Available Visualization Modes")
    table.add_column("Mode", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Description", style="white")
    
    for mode_id, info in modes_data.items():
        table.add_row(
            mode_id,
            info["name"],
            info["category"],
            info["description"]
        )
    
    console.print(table)

@main.command()  
@click.option("--check-audio", is_flag=True, help="Check audio system")
@click.option("--check-export", is_flag=True, help="Check export capabilities")
@click.option("--verbose", is_flag=True, help="Verbose output")
def doctor(check_audio, check_export, verbose):
    """Diagnose WaveTerm installation and capabilities"""
    from .core.diagnostics import WaveDiagnostics
    
    diag = WaveDiagnostics(verbose=verbose)
    
    console.print("[bold cyan]🔍 WaveTerm Diagnostics[/bold cyan]\n")
    
    # Basic system check
    diag.check_system()
    
    if check_audio:
        diag.check_audio()
        
    if check_export:
        diag.check_export()
        
    diag.print_summary()

@main.command()
@click.argument("output_file", type=click.Path())
@click.option("--mode", default="bars", help="Visualization mode")
@click.option("--duration", default=10, help="Export duration in seconds") 
@click.option("--format", default="gif", 
              type=click.Choice(['gif', 'mp4', 'images']),
              help="Export format")
@click.option("--fps", default=20, help="Export FPS")
def export(output_file, mode, duration, format, fps):
    """Export visualization to file/directory"""
    from .export.exporter import WaveExporter
    
    console.print(f"[green]📹 Exporting[/green] {mode} visualization to {output_file}")
    
    exporter = WaveExporter()
    exporter.export(
        output_path=output_file,
        mode=mode,
        duration=duration,
        format=format,
        fps=fps
    )
    
    console.print(f"[green]✅ Export complete![/green]")

@main.command()
def config():
    """Create/edit WaveTerm configuration"""
    config_file = Path.home() / ".waveterm" / "config.toml"
    
    if not config_file.exists():
        console.print("[yellow]Creating default configuration...[/yellow]")
        config_obj = WaveConfig()
        config_obj.save(config_file)
        console.print(f"[green]✅ Created[/green] {config_file}")
    else:
        console.print(f"[blue]Configuration file:[/blue] {config_file}")
    
    # Show current config
    try:
        config_obj = WaveConfig.load(config_file)
        console.print("\n[bold]Current Configuration:[/bold]")
        console.print(config_obj.to_table())
    except Exception as e:
        console.print(f"[red]Error loading config:[/red] {e}")

if __name__ == "__main__":
    main()