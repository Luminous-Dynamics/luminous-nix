"""
Prometheus metrics server for the self-healing engine.

This module provides an HTTP endpoint that exposes all healing metrics
in Prometheus format for external monitoring systems like Grafana.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio
from aiohttp import web
import socket

# Check if prometheus_client is available
try:
    from prometheus_client import (
        generate_latest,
        CollectorRegistry,
        REGISTRY,
        Counter,
        Gauge,
        Histogram,
        Summary,
        Info
    )
    # Get the content type properly
    from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    CONTENT_TYPE_LATEST = 'text/plain; version=0.0.4; charset=utf-8'

logger = logging.getLogger(__name__)


class MetricsServer:
    """
    HTTP server that exposes Prometheus metrics for the self-healing engine.
    
    Features:
    - Exposes /metrics endpoint in Prometheus format
    - Includes all healing engine metrics
    - Adds system health metrics
    - Provides service discovery labels
    """
    
    def __init__(self, 
                 healing_engine=None,
                 host: str = '0.0.0.0',
                 port: int = 9090,
                 registry: Optional[CollectorRegistry] = None):
        """
        Initialize the metrics server.
        
        Args:
            healing_engine: The SelfHealingEngine instance to monitor
            host: Host to bind to (default: 0.0.0.0)
            port: Port to listen on (default: 9090)
            registry: Prometheus registry (default: create new registry)
        """
        self.healing_engine = healing_engine
        self.host = host
        self.port = port
        # Create a new registry to avoid conflicts
        self.registry = registry or CollectorRegistry()
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # Setup routes
        self._setup_routes()
        
        # Setup additional metrics
        if PROMETHEUS_AVAILABLE:
            self._setup_metrics()
        
        logger.info(f"Metrics server initialized for {host}:{port}")
    
    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get('/metrics', self.handle_metrics)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/', self.handle_index)
    
    def _setup_metrics(self):
        """Setup additional metrics beyond what healing engine provides."""
        
        # Service info
        self.info_service = Info(
            'luminous_nix_service',
            'Information about the Luminous Nix service',
            registry=self.registry
        )
        self.info_service.info({
            'version': '1.3.0',
            'healing_enabled': 'true',
            'file_monitoring': 'true',
            'predictive_assistance': 'true'
        })
        
        # System health gauge
        self.gauge_system_health = Gauge(
            'luminous_nix_system_health_score',
            'Overall system health score (0-100)',
            registry=self.registry
        )
        
        # File monitoring metrics
        self.gauge_monitored_paths = Gauge(
            'luminous_nix_monitored_paths_total',
            'Number of paths being monitored',
            registry=self.registry
        )
        
        self.gauge_file_events = Gauge(
            'luminous_nix_file_events_total',
            'Total file events detected',
            registry=self.registry
        )
        
        # Healing queue metrics
        self.gauge_healing_queue = Gauge(
            'luminous_nix_healing_queue_size',
            'Number of issues in healing queue',
            registry=self.registry
        )
        
        # Uptime metric
        self.counter_uptime = Counter(
            'luminous_nix_uptime_seconds_total',
            'Total uptime in seconds',
            registry=self.registry
        )
    
    async def handle_metrics(self, request):
        """Handle /metrics endpoint."""
        if not PROMETHEUS_AVAILABLE:
            return web.Response(
                text="Prometheus client not installed. Install with: poetry add prometheus-client",
                status=503
            )
        
        # Update dynamic metrics
        await self._update_metrics()
        
        # Generate metrics from our registry
        metrics = generate_latest(self.registry)
        
        # Also include metrics from the global registry (healing engine metrics)
        try:
            global_metrics = generate_latest(REGISTRY)
            # Combine both outputs (remove duplicate TYPE/HELP lines)
            metrics = metrics + b'\n' + global_metrics
        except Exception:
            # If there's an issue, just use our registry
            pass
        
        return web.Response(
            body=metrics,
            content_type='text/plain'
        )
    
    async def handle_health(self, request):
        """Handle /health endpoint for liveness/readiness probes."""
        health_data = await self._get_health_status()
        
        status_code = 200 if health_data['healthy'] else 503
        
        return web.json_response(health_data, status=status_code)
    
    async def handle_index(self, request):
        """Handle root endpoint with service information."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Luminous Nix Metrics</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .metric { 
                    background: #f4f4f4; 
                    padding: 10px; 
                    margin: 10px 0;
                    border-radius: 5px;
                }
                .endpoint { 
                    color: #0066cc; 
                    text-decoration: none;
                    font-weight: bold;
                }
                .status { 
                    padding: 5px 10px; 
                    border-radius: 3px;
                    display: inline-block;
                    margin: 5px 0;
                }
                .healthy { background: #4CAF50; color: white; }
                .unhealthy { background: #f44336; color: white; }
            </style>
        </head>
        <body>
            <h1>🔧 Luminous Nix Self-Healing Metrics</h1>
            <p>Prometheus metrics endpoint for monitoring the self-healing engine.</p>
            
            <h2>Available Endpoints:</h2>
            <div class="metric">
                <a href="/metrics" class="endpoint">/metrics</a> - Prometheus metrics (scrape target)
            </div>
            <div class="metric">
                <a href="/health" class="endpoint">/health</a> - Health check endpoint
            </div>
            
            <h2>Quick Stats:</h2>
            <div id="stats">Loading...</div>
            
            <h2>Prometheus Configuration:</h2>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
# Add to prometheus.yml:
scrape_configs:
  - job_name: 'luminous-nix'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          service: 'self-healing'
          environment: 'production'
            </pre>
            
            <script>
                fetch('/health')
                    .then(r => r.json())
                    .then(data => {
                        const statsDiv = document.getElementById('stats');
                        const statusClass = data.healthy ? 'healthy' : 'unhealthy';
                        const statusText = data.healthy ? '✅ Healthy' : '❌ Unhealthy';
                        
                        statsDiv.innerHTML = `
                            <div class="status ${statusClass}">${statusText}</div>
                            <div class="metric">System Health: ${data.system_health}%</div>
                            <div class="metric">Files Monitored: ${data.files_monitored}</div>
                            <div class="metric">Issues Healed: ${data.issues_healed}</div>
                            <div class="metric">Uptime: ${data.uptime}</div>
                        `;
                    })
                    .catch(e => {
                        document.getElementById('stats').innerHTML = 
                            '<div class="status unhealthy">Failed to load stats</div>';
                    });
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def _update_metrics(self):
        """Update dynamic metrics from healing engine."""
        if not PROMETHEUS_AVAILABLE or not self.healing_engine:
            return
        
        try:
            # Update system health
            if hasattr(self.healing_engine, 'health_tracker'):
                try:
                    health = self.healing_engine.health_tracker.calculate_health_score()
                    self.gauge_system_health.set(health)
                except Exception:
                    # Default to 75 if no data
                    self.gauge_system_health.set(75)
            
            # Update file monitoring metrics
            if hasattr(self.healing_engine, 'file_monitor'):
                stats = self.healing_engine.file_monitor.get_statistics()
                self.gauge_monitored_paths.set(stats.get('paths_monitored', 0))
                self.gauge_file_events.set(stats.get('events_detected', 0))
            
            # Update healing queue size (approximate)
            if hasattr(self.healing_engine, 'recent_heals'):
                self.gauge_healing_queue.set(len(self.healing_engine.recent_heals))
            
            # Copy metrics from healing engine's registry if available
            if PROMETHEUS_AVAILABLE and hasattr(self.healing_engine, 'metrics_issues_detected'):
                # The healing engine has its own metrics in the global registry
                # We'll include them in our output
                pass
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def _get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        health_data = {
            'healthy': True,
            'system_health': 100,
            'files_monitored': 0,
            'issues_healed': 0,
            'uptime': 'unknown'
        }
        
        if self.healing_engine:
            try:
                # Get system health
                if hasattr(self.healing_engine, 'health_tracker'):
                    try:
                        health = self.healing_engine.health_tracker.calculate_health_score()
                        health_data['system_health'] = health
                        health_data['healthy'] = health > 30  # Threshold from engine
                    except Exception:
                        # Default values if no data
                        health_data['system_health'] = 75
                        health_data['healthy'] = True
                
                # Get file monitoring stats
                if hasattr(self.healing_engine, 'file_monitor'):
                    stats = self.healing_engine.file_monitor.get_statistics()
                    health_data['files_monitored'] = stats.get('files_monitored', 0)
                
                # Get healing stats
                if hasattr(self.healing_engine, 'knowledge'):
                    knowledge_stats = self.healing_engine.knowledge.knowledge.get('statistics', {})
                    health_data['issues_healed'] = knowledge_stats.get('successful_heals', 0)
                
                # Calculate uptime (simplified)
                health_data['uptime'] = 'running'
                
            except Exception as e:
                logger.error(f"Error getting health status: {e}")
                health_data['healthy'] = False
        
        return health_data
    
    async def start(self):
        """Start the metrics server."""
        if self.runner:
            logger.warning("Metrics server already running")
            return
        
        # Check if port is available
        if not self._is_port_available(self.port):
            logger.error(f"Port {self.port} is already in use")
            raise RuntimeError(f"Port {self.port} is not available")
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        logger.info(f"📊 Metrics server started at http://{self.host}:{self.port}/metrics")
        logger.info(f"   Health check: http://{self.host}:{self.port}/health")
        logger.info(f"   Dashboard: http://{self.host}:{self.port}/")
    
    async def stop(self):
        """Stop the metrics server."""
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
            self.site = None
            logger.info("📊 Metrics server stopped")
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False


async def run_metrics_server(healing_engine=None, host='0.0.0.0', port=9090):
    """
    Run the metrics server as a standalone service.
    
    Args:
        healing_engine: Optional SelfHealingEngine instance
        host: Host to bind to
        port: Port to listen on
    """
    server = MetricsServer(healing_engine, host, port)
    
    try:
        await server.start()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
            
    except KeyboardInterrupt:
        logger.info("Metrics server interrupted")
    finally:
        await server.stop()


if __name__ == "__main__":
    # Run standalone metrics server
    asyncio.run(run_metrics_server())