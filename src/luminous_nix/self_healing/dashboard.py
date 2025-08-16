#!/usr/bin/env python3
"""
Real-time dashboard for monitoring self-healing system metrics.

This module provides a beautiful terminal-based dashboard using Rich
to visualize system health, healing actions, and performance metrics.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import psutil
import aiohttp

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.columns import Columns
from rich.align import Align
from rich import box

# Try to import plotext for better charts (optional)
try:
    import plotext as plt
    HAS_PLOTEXT = True
except ImportError:
    HAS_PLOTEXT = False


class MetricsDashboard:
    """
    Real-time dashboard for self-healing system metrics.
    """
    
    def __init__(self, metrics_url: str = "http://localhost:9090/metrics"):
        self.metrics_url = metrics_url
        self.console = Console()
        self.metrics_history = []
        self.healing_events = []
        self.system_status = {}
        self.start_time = time.time()
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_temp = self._get_cpu_temperature()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'temperature': cpu_temp,
                    'cores': psutil.cpu_count()
                },
                'memory': {
                    'percent': memory.percent,
                    'used_gb': memory.used / (1024**3),
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3)
                },
                'swap': {
                    'percent': swap.percent,
                    'used_gb': swap.used / (1024**3),
                    'total_gb': swap.total / (1024**3)
                },
                'disk': {
                    'percent': disk.percent,
                    'used_gb': disk.used / (1024**3),
                    'total_gb': disk.total / (1024**3),
                    'free_gb': disk.free / (1024**3)
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'processes': process_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if 'core' in entry.label.lower() or 'cpu' in entry.label.lower():
                            return entry.current
        except:
            pass
        return 0.0
    
    async def fetch_healing_metrics(self) -> Dict[str, Any]:
        """Fetch metrics from the self-healing engine"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.metrics_url) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Parse Prometheus format
                        metrics = {}
                        for line in text.split('\n'):
                            if line and not line.startswith('#'):
                                parts = line.split(' ')
                                if len(parts) == 2:
                                    metrics[parts[0]] = float(parts[1])
                        return metrics
        except:
            pass
        return {}
    
    def create_header_panel(self) -> Panel:
        """Create the header panel"""
        uptime = timedelta(seconds=int(time.time() - self.start_time))
        
        header = Table(box=None, expand=True)
        header.add_column("", justify="left")
        header.add_column("", justify="center")
        header.add_column("", justify="right")
        
        header.add_row(
            Text("🌟 Luminous Nix Self-Healing Dashboard", style="bold cyan"),
            Text(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="yellow"),
            Text(f"⬆️ Uptime: {uptime}", style="green")
        )
        
        return Panel(header, box=box.DOUBLE, style="bold blue")
    
    def create_system_panel(self, metrics: Dict[str, Any]) -> Panel:
        """Create system metrics panel"""
        table = Table(title="System Metrics", box=box.ROUNDED, expand=True)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green")
        table.add_column("Status", width=10)
        
        if 'error' not in metrics:
            # CPU
            cpu = metrics.get('cpu', {})
            cpu_status = "🔴" if cpu.get('percent', 0) > 80 else "🟡" if cpu.get('percent', 0) > 50 else "🟢"
            table.add_row(
                "CPU Usage",
                f"{cpu.get('percent', 0):.1f}% @ {cpu.get('frequency', 0):.0f}MHz",
                cpu_status
            )
            
            if cpu.get('temperature', 0) > 0:
                temp_status = "🔴" if cpu.get('temperature', 0) > 80 else "🟡" if cpu.get('temperature', 0) > 60 else "🟢"
                table.add_row(
                    "CPU Temperature",
                    f"{cpu.get('temperature', 0):.1f}°C",
                    temp_status
                )
            
            # Memory
            mem = metrics.get('memory', {})
            mem_status = "🔴" if mem.get('percent', 0) > 90 else "🟡" if mem.get('percent', 0) > 70 else "🟢"
            table.add_row(
                "Memory",
                f"{mem.get('used_gb', 0):.1f}/{mem.get('total_gb', 0):.1f}GB ({mem.get('percent', 0):.1f}%)",
                mem_status
            )
            
            # Swap
            swap = metrics.get('swap', {})
            if swap.get('total_gb', 0) > 0:
                swap_status = "🔴" if swap.get('percent', 0) > 50 else "🟡" if swap.get('percent', 0) > 25 else "🟢"
                table.add_row(
                    "Swap",
                    f"{swap.get('used_gb', 0):.1f}/{swap.get('total_gb', 0):.1f}GB ({swap.get('percent', 0):.1f}%)",
                    swap_status
                )
            
            # Disk
            disk = metrics.get('disk', {})
            disk_status = "🔴" if disk.get('percent', 0) > 90 else "🟡" if disk.get('percent', 0) > 70 else "🟢"
            table.add_row(
                "Disk",
                f"{disk.get('used_gb', 0):.1f}/{disk.get('total_gb', 0):.1f}GB ({disk.get('percent', 0):.1f}%)",
                disk_status
            )
            
            # Processes
            table.add_row(
                "Processes",
                f"{metrics.get('processes', 0)} running",
                "🟢"
            )
        else:
            table.add_row("Error", metrics['error'], "🔴")
        
        return Panel(table, title="📊 System Health", border_style="green")
    
    def create_healing_panel(self, healing_metrics: Dict[str, Any]) -> Panel:
        """Create healing metrics panel"""
        table = Table(title="Healing Metrics", box=box.ROUNDED, expand=True)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="yellow")
        
        # Add healing metrics
        if healing_metrics:
            issues_detected = healing_metrics.get('luminous_healing_issues_detected_total', 0)
            issues_resolved = healing_metrics.get('luminous_healing_issues_resolved_total', 0)
            plans_generated = healing_metrics.get('luminous_healing_plans_generated_total', 0)
            backups_created = healing_metrics.get('luminous_healing_backups_created_total', 0)
            
            table.add_row("Issues Detected", f"{int(issues_detected)}")
            table.add_row("Issues Resolved", f"{int(issues_resolved)}")
            table.add_row("Healing Plans Generated", f"{int(plans_generated)}")
            table.add_row("Backups Created", f"{int(backups_created)}")
            
            # Success rate
            if issues_detected > 0:
                success_rate = (issues_resolved / issues_detected) * 100
                table.add_row("Success Rate", f"{success_rate:.1f}%")
            
            # Add timing metrics
            monitor_time = healing_metrics.get('luminous_healing_monitor_duration_seconds_sum', 0)
            plan_time = healing_metrics.get('luminous_healing_plan_duration_seconds_sum', 0)
            execute_time = healing_metrics.get('luminous_healing_execute_duration_seconds_sum', 0)
            
            if monitor_time > 0:
                table.add_row("Avg Monitor Time", f"{monitor_time:.3f}s")
            if plan_time > 0:
                table.add_row("Avg Plan Time", f"{plan_time:.3f}s")
            if execute_time > 0:
                table.add_row("Avg Execute Time", f"{execute_time:.3f}s")
        else:
            table.add_row("Status", "No healing metrics available")
        
        return Panel(table, title="🔧 Healing Engine", border_style="yellow")
    
    def create_events_panel(self) -> Panel:
        """Create recent events panel"""
        table = Table(title="Recent Events", box=box.SIMPLE, expand=True)
        table.add_column("Time", style="dim", width=12)
        table.add_column("Type", width=15)
        table.add_column("Event", style="white")
        
        # Add recent healing events
        for event in self.healing_events[-10:]:  # Last 10 events
            time_str = event.get('time', '').split('T')[1][:8] if 'T' in event.get('time', '') else ''
            event_type = event.get('type', 'unknown')
            
            style = "green" if event_type == "resolved" else "yellow" if event_type == "detected" else "white"
            table.add_row(
                time_str,
                Text(event_type.capitalize(), style=style),
                event.get('description', '')
            )
        
        if not self.healing_events:
            table.add_row("", "", "No recent events")
        
        return Panel(table, title="📜 Event Log", border_style="blue")
    
    def create_performance_panel(self, metrics_history: List[Dict]) -> Panel:
        """Create performance graphs panel"""
        if HAS_PLOTEXT and len(metrics_history) > 1:
            # Create a simple ASCII chart
            cpu_history = [m.get('cpu', {}).get('percent', 0) for m in metrics_history[-20:]]
            mem_history = [m.get('memory', {}).get('percent', 0) for m in metrics_history[-20:]]
            
            # Create text representation
            chart_text = "CPU: " + self._create_sparkline(cpu_history) + f" {cpu_history[-1]:.1f}%\n"
            chart_text += "MEM: " + self._create_sparkline(mem_history) + f" {mem_history[-1]:.1f}%"
            
            return Panel(
                Align.center(Text(chart_text, style="cyan")),
                title="📈 Performance Trends",
                border_style="magenta"
            )
        else:
            return Panel(
                Align.center(Text("Collecting performance data...", style="dim")),
                title="📈 Performance Trends",
                border_style="magenta"
            )
    
    def _create_sparkline(self, data: List[float]) -> str:
        """Create a simple sparkline chart"""
        if not data:
            return ""
        
        blocks = "▁▂▃▄▅▆▇█"
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            return blocks[4] * len(data)
        
        sparkline = ""
        for value in data:
            normalized = (value - min_val) / (max_val - min_val)
            index = int(normalized * (len(blocks) - 1))
            sparkline += blocks[index]
        
        return sparkline
    
    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="system", ratio=2),
            Layout(name="performance", ratio=1)
        )
        
        layout["right"].split_column(
            Layout(name="healing", ratio=1),
            Layout(name="events", ratio=2)
        )
        
        return layout
    
    def create_footer_panel(self) -> Panel:
        """Create footer panel with controls"""
        controls = Table(box=None, expand=True)
        controls.add_column("", justify="center")
        
        controls.add_row(
            Text("Press [q] to quit | [r] to refresh | [h] for help", style="dim")
        )
        
        return Panel(controls, box=box.SQUARE, style="dim")
    
    async def update_dashboard(self, layout: Layout):
        """Update dashboard with latest data"""
        # Get system metrics
        system_metrics = self.get_system_metrics()
        self.metrics_history.append(system_metrics)
        
        # Keep only last 100 entries
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # Get healing metrics
        healing_metrics = await self.fetch_healing_metrics()
        
        # Update layout
        layout["header"].update(self.create_header_panel())
        layout["system"].update(self.create_system_panel(system_metrics))
        layout["healing"].update(self.create_healing_panel(healing_metrics))
        layout["events"].update(self.create_events_panel())
        layout["performance"].update(self.create_performance_panel(self.metrics_history))
        layout["footer"].update(self.create_footer_panel())
    
    async def run(self):
        """Run the dashboard"""
        layout = self.create_layout()
        
        with Live(layout, refresh_per_second=1, screen=True) as live:
            try:
                while True:
                    await self.update_dashboard(layout)
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass


class SimpleDashboard:
    """
    Simplified dashboard for environments without Rich
    """
    
    def __init__(self, metrics_url: str = "http://localhost:9090/metrics"):
        self.metrics_url = metrics_url
        self.start_time = time.time()
    
    async def run(self):
        """Run simple text-based dashboard"""
        while True:
            try:
                # Clear screen
                print("\033[2J\033[H")  # Clear screen and move cursor to top
                
                # Header
                print("=" * 60)
                print(f"Luminous Nix Self-Healing Dashboard - {datetime.now()}")
                print("=" * 60)
                
                # System metrics
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                print(f"\nSystem Metrics:")
                print(f"  CPU:    {cpu:.1f}%")
                print(f"  Memory: {memory.percent:.1f}% ({memory.used/(1024**3):.1f}/{memory.total/(1024**3):.1f}GB)")
                print(f"  Disk:   {disk.percent:.1f}% ({disk.used/(1024**3):.1f}/{disk.total/(1024**3):.1f}GB)")
                
                # Healing metrics
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.metrics_url) as response:
                            if response.status == 200:
                                text = await response.text()
                                issues_detected = 0
                                issues_resolved = 0
                                
                                for line in text.split('\n'):
                                    if 'issues_detected_total' in line:
                                        issues_detected = int(float(line.split()[-1]))
                                    elif 'issues_resolved_total' in line:
                                        issues_resolved = int(float(line.split()[-1]))
                                
                                print(f"\nHealing Metrics:")
                                print(f"  Issues Detected: {issues_detected}")
                                print(f"  Issues Resolved: {issues_resolved}")
                                if issues_detected > 0:
                                    print(f"  Success Rate:    {(issues_resolved/issues_detected)*100:.1f}%")
                except:
                    print(f"\nHealing Metrics: Not available")
                
                print("\n[Press Ctrl+C to exit]")
                
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(2)


async def main():
    """Main entry point"""
    import sys
    
    # Check if Rich is available
    try:
        import rich
        dashboard = MetricsDashboard()
    except ImportError:
        print("Rich library not available, using simple dashboard")
        dashboard = SimpleDashboard()
    
    # Check for arguments
    if len(sys.argv) > 1:
        dashboard.metrics_url = sys.argv[1]
    
    await dashboard.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDashboard stopped")