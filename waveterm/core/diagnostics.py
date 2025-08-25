"""
System diagnostics for Wave
"""

import sys
import platform
from pathlib import Path
from typing import List, Tuple, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class WaveDiagnostics:
    """System diagnostics and health checks"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[Tuple[str, bool, str]] = []
    
    def _check(self, name: str, success: bool, message: str) -> None:
        """Record a diagnostic check result"""
        self.results.append((name, success, message))
        
        if self.verbose:
            status = "[green]✅ PASS[/green]" if success else "[red]❌ FAIL[/red]"
            console.print(f"{status} {name}: {message}")
    
    def check_system(self) -> None:
        """Check basic system requirements"""
        console.print("[bold blue]System Information[/bold blue]")
        
        # Python version
        py_version = sys.version_info
        py_ok = py_version >= (3, 8)
        self._check(
            "Python Version", 
            py_ok, 
            f"{py_version.major}.{py_version.minor}.{py_version.micro} ({'✅ OK' if py_ok else '❌ Requires 3.8+'})"
        )
        
        # Platform info
        system_info = f"{platform.system()} {platform.release()}"
        self._check("Platform", True, system_info)
        
        # Terminal size
        try:
            import shutil
            size = shutil.get_terminal_size()
            term_ok = size.columns >= 40 and size.lines >= 10
            self._check(
                "Terminal Size",
                term_ok,
                f"{size.columns}x{size.lines} ({'✅ OK' if term_ok else '❌ Too small'})"
            )
        except Exception as e:
            self._check("Terminal Size", False, f"Cannot detect: {e}")
        
        # Core dependencies
        self._check_import("numpy", "NumPy")
        self._check_import("rich", "Rich")
        
    def check_audio(self) -> None:
        """Check audio system capabilities"""
        console.print("\n[bold blue]Audio System[/bold blue]")
        
        # Audio dependencies
        sd_available = self._check_import("sounddevice", "SoundDevice", required=False)
        librosa_available = self._check_import("librosa", "Librosa", required=False)
        
        if sd_available:
            try:
                import sounddevice as sd
                devices = sd.query_devices()
                input_devices = [d for d in devices if d['max_input_channels'] > 0]
                
                self._check(
                    "Audio Input Devices",
                    len(input_devices) > 0,
                    f"Found {len(input_devices)} input device(s)"
                )
                
                if self.verbose and input_devices:
                    console.print("[dim]Available input devices:[/dim]")
                    for i, device in enumerate(input_devices):
                        console.print(f"  {i}: {device['name']}")
                        
            except Exception as e:
                self._check("Audio Input Devices", False, f"Error: {e}")
        
        if librosa_available:
            self._check("File Audio Support", True, "Librosa available")
        else:
            self._check("File Audio Support", False, "Librosa not installed")
    
    def check_export(self) -> None:
        """Check export capabilities"""
        console.print("\n[bold blue]Export System[/bold blue]")
        
        # Export dependencies
        pil_available = self._check_import("PIL", "Pillow", required=False)
        imageio_available = self._check_import("imageio", "ImageIO", required=False)
        
        if pil_available:
            self._check("Image Export", True, "Pillow available")
        else:
            self._check("Image Export", False, "Pillow not installed")
            
        if imageio_available:
            self._check("GIF/Video Export", True, "ImageIO available") 
        else:
            self._check("GIF/Video Export", False, "ImageIO not installed")
    
    def _check_import(self, module_name: str, display_name: str, required: bool = True) -> bool:
        """Check if a module can be imported"""
        try:
            __import__(module_name)
            self._check(f"{display_name} Import", True, "Available")
            return True
        except ImportError as e:
            status = "Required" if required else "Optional"
            self._check(f"{display_name} Import", not required, f"Not available ({status}): {e}")
            return False
        except Exception as e:
            self._check(f"{display_name} Import", False, f"Error: {e}")
            return False
    
    def print_summary(self) -> None:
        """Print diagnostic summary"""
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        failed = total - passed
        
        if not self.verbose:
            # Show summary table
            table = Table(title="Diagnostic Results")
            table.add_column("Check", style="white")
            table.add_column("Status", style="white")
            table.add_column("Details", style="dim")
            
            for name, success, message in self.results:
                status = "[green]✅ PASS[/green]" if success else "[red]❌ FAIL[/red]"
                table.add_row(name, status, message)
                
            console.print(table)
        
        # Summary panel
        color = "green" if failed == 0 else "yellow" if failed < 3 else "red"
        summary_text = f"[{color}]{passed}/{total} checks passed[/{color}]"
        
        if failed > 0:
            summary_text += f"\n[red]{failed} checks failed[/red]"
            
        recommendations = self._get_recommendations()
        if recommendations:
            summary_text += f"\n\n[bold]Recommendations:[/bold]\n"
            for rec in recommendations:
                summary_text += f"• {rec}\n"
        
        console.print(Panel(summary_text, title="🏥 Diagnostic Summary"))
    
    def _get_recommendations(self) -> List[str]:
        """Generate recommendations based on failed checks"""
        recommendations = []
        
        # Check for common issues
        failed_checks = [name for name, success, _ in self.results if not success]
        
        if "Python Version" in failed_checks:
            recommendations.append("Upgrade to Python 3.8 or newer")
            
        if "SoundDevice Import" in failed_checks:
            recommendations.append("Install audio support: pip install 'wave-visualizer[audio]'")
            
        if "Pillow Import" in failed_checks or "ImageIO Import" in failed_checks:
            recommendations.append("Install export support: pip install 'wave-visualizer[export]'")
            
        if "Terminal Size" in failed_checks:
            recommendations.append("Increase terminal window size (minimum 40x10)")
            
        if "Audio Input Devices" in failed_checks:
            recommendations.append("Check audio system configuration and permissions")
            
        return recommendations