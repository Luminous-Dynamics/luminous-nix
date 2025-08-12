"""OpenTelemetry instrumentation for Nix for Humanity."""

import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Generator, Optional, TypeVar

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.metrics import Counter, Histogram, UpDownCounter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TelemetryManager:
    """Manage OpenTelemetry instrumentation."""
    
    def __init__(
        self,
        service_name: str = "nix-for-humanity",
        service_version: str = "1.2.0",
        environment: str = "development",
        otlp_endpoint: Optional[str] = None,
        prometheus_port: int = 9090,
        enabled: bool = True,
    ):
        """Initialize telemetry manager.
        
        Args:
            service_name: Name of the service
            service_version: Version of the service
            environment: Deployment environment
            otlp_endpoint: OTLP collector endpoint
            prometheus_port: Port for Prometheus metrics
            enabled: Whether telemetry is enabled
        """
        self.service_name = service_name
        self.service_version = service_version
        self.environment = environment
        self.enabled = enabled
        
        if not self.enabled:
            logger.info("Telemetry disabled")
            return
        
        # Create resource
        self.resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        })
        
        # Initialize tracing
        self._setup_tracing(otlp_endpoint)
        
        # Initialize metrics
        self._setup_metrics(prometheus_port, otlp_endpoint)
        
        # Instrument libraries
        self._instrument_libraries()
        
        # Create default instruments
        self._create_instruments()
        
        logger.info(f"Telemetry initialized for {service_name}")
    
    def _setup_tracing(self, otlp_endpoint: Optional[str]) -> None:
        """Set up distributed tracing.
        
        Args:
            otlp_endpoint: OTLP collector endpoint
        """
        # Create tracer provider
        provider = TracerProvider(resource=self.resource)
        
        # Add OTLP exporter if endpoint provided
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                insecure=True,  # Use insecure for local development
            )
            provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
        
        # Set global tracer provider
        trace.set_tracer_provider(provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(
            self.service_name,
            self.service_version,
        )
    
    def _setup_metrics(
        self,
        prometheus_port: int,
        otlp_endpoint: Optional[str],
    ) -> None:
        """Set up metrics collection.
        
        Args:
            prometheus_port: Port for Prometheus metrics
            otlp_endpoint: OTLP collector endpoint
        """
        # Create metric readers
        readers = []
        
        # Add Prometheus reader
        if prometheus_port:
            prometheus_reader = PrometheusMetricReader(
                port=prometheus_port
            )
            readers.append(prometheus_reader)
        
        # Add OTLP exporter if endpoint provided
        if otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(
                endpoint=otlp_endpoint,
                insecure=True,
            )
            readers.append(otlp_exporter)
        
        # Create meter provider
        provider = MeterProvider(
            resource=self.resource,
            metric_readers=readers,
        )
        
        # Set global meter provider
        metrics.set_meter_provider(provider)
        
        # Get meter
        self.meter = metrics.get_meter(
            self.service_name,
            self.service_version,
        )
    
    def _instrument_libraries(self) -> None:
        """Instrument third-party libraries."""
        try:
            # Instrument HTTP requests
            RequestsInstrumentor().instrument()
            
            # Instrument SQLAlchemy if available
            try:
                from sqlalchemy import create_engine
                SQLAlchemyInstrumentor().instrument()
            except ImportError:
                pass
            
        except Exception as e:
            logger.warning(f"Failed to instrument libraries: {e}")
    
    def _create_instruments(self) -> None:
        """Create default metric instruments."""
        # Counters
        self.request_counter = self.meter.create_counter(
            name="nix_humanity_requests_total",
            description="Total number of requests",
            unit="1",
        )
        
        self.error_counter = self.meter.create_counter(
            name="nix_humanity_errors_total",
            description="Total number of errors",
            unit="1",
        )
        
        self.command_counter = self.meter.create_counter(
            name="nix_humanity_commands_total",
            description="Total number of commands executed",
            unit="1",
        )
        
        # Histograms
        self.request_duration = self.meter.create_histogram(
            name="nix_humanity_request_duration_seconds",
            description="Request duration in seconds",
            unit="s",
        )
        
        self.command_duration = self.meter.create_histogram(
            name="nix_humanity_command_duration_seconds",
            description="Command execution duration in seconds",
            unit="s",
        )
        
        # UpDownCounters
        self.active_sessions = self.meter.create_up_down_counter(
            name="nix_humanity_active_sessions",
            description="Number of active sessions",
            unit="1",
        )
        
        self.cache_size = self.meter.create_up_down_counter(
            name="nix_humanity_cache_size_bytes",
            description="Cache size in bytes",
            unit="By",
        )
    
    @contextmanager
    def span(
        self,
        name: str,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Generator[trace.Span, None, None]:
        """Create a new span.
        
        Args:
            name: Span name
            kind: Span kind
            attributes: Span attributes
            
        Yields:
            Span instance
        """
        if not self.enabled:
            yield None
            return
        
        with self.tracer.start_as_current_span(
            name,
            kind=kind,
            attributes=attributes or {},
        ) as span:
            yield span
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
    ) -> None:
        """Record HTTP request metrics.
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            status_code: Response status code
            duration: Request duration in seconds
        """
        if not self.enabled:
            return
        
        attributes = {
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code),
        }
        
        # Increment counter
        self.request_counter.add(1, attributes)
        
        # Record duration
        self.request_duration.record(duration, attributes)
        
        # Record errors
        if status_code >= 400:
            self.error_counter.add(1, attributes)
    
    def record_command(
        self,
        command_type: str,
        success: bool,
        duration: float,
        persona: Optional[str] = None,
    ) -> None:
        """Record command execution metrics.
        
        Args:
            command_type: Type of command executed
            success: Whether command succeeded
            duration: Command duration in seconds
            persona: User persona if applicable
        """
        if not self.enabled:
            return
        
        attributes = {
            "command_type": command_type,
            "success": str(success),
        }
        
        if persona:
            attributes["persona"] = persona
        
        # Increment counter
        self.command_counter.add(1, attributes)
        
        # Record duration
        self.command_duration.record(duration, attributes)
        
        # Record errors
        if not success:
            self.error_counter.add(1, {"type": "command_failure"})
    
    def update_active_sessions(self, delta: int) -> None:
        """Update active sessions count.
        
        Args:
            delta: Change in session count (+1 for new, -1 for closed)
        """
        if not self.enabled:
            return
        
        self.active_sessions.add(delta)
    
    def update_cache_size(self, size_bytes: int) -> None:
        """Update cache size metric.
        
        Args:
            size_bytes: Current cache size in bytes
        """
        if not self.enabled:
            return
        
        # Reset to current value
        self.cache_size.add(-self.cache_size._value if hasattr(self.cache_size, '_value') else 0)
        self.cache_size.add(size_bytes)


def traced(
    name: Optional[str] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
) -> Callable:
    """Decorator for tracing function execution.
    
    Args:
        name: Span name (defaults to function name)
        kind: Span kind
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            # Get telemetry manager
            from nix_for_humanity.monitoring import telemetry_manager
            
            if telemetry_manager and telemetry_manager.enabled:
                with telemetry_manager.span(
                    span_name,
                    kind=kind,
                    attributes={
                        "function": func.__name__,
                        "module": func.__module__,
                    },
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        if span:
                            span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        if span:
                            span.record_exception(e)
                            span.set_status(
                                trace.Status(
                                    trace.StatusCode.ERROR,
                                    str(e),
                                )
                            )
                        raise
            else:
                # No telemetry, just run function
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def metered(
    metric_name: str,
    metric_type: str = "counter",
    labels: Optional[Dict[str, str]] = None,
) -> Callable:
    """Decorator for recording metrics.
    
    Args:
        metric_name: Name of the metric
        metric_type: Type of metric (counter, histogram)
        labels: Static labels for the metric
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get telemetry manager
            from nix_for_humanity.monitoring import telemetry_manager
            
            if telemetry_manager and telemetry_manager.enabled:
                import time
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record metric
                    attributes = labels or {}
                    attributes["function"] = func.__name__
                    attributes["success"] = "true"
                    
                    if metric_type == "counter":
                        telemetry_manager.meter.create_counter(
                            name=metric_name,
                            description=f"Calls to {func.__name__}",
                        ).add(1, attributes)
                    elif metric_type == "histogram":
                        telemetry_manager.meter.create_histogram(
                            name=metric_name,
                            description=f"Duration of {func.__name__}",
                            unit="s",
                        ).record(duration, attributes)
                    
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Record error metric
                    attributes = labels or {}
                    attributes["function"] = func.__name__
                    attributes["success"] = "false"
                    attributes["error"] = type(e).__name__
                    
                    if metric_type == "counter":
                        telemetry_manager.meter.create_counter(
                            name=metric_name,
                            description=f"Calls to {func.__name__}",
                        ).add(1, attributes)
                    elif metric_type == "histogram":
                        telemetry_manager.meter.create_histogram(
                            name=metric_name,
                            description=f"Duration of {func.__name__}",
                            unit="s",
                        ).record(duration, attributes)
                    
                    raise
            else:
                # No telemetry, just run function
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global telemetry manager instance
telemetry_manager: Optional[TelemetryManager] = None


def initialize_telemetry(**kwargs) -> TelemetryManager:
    """Initialize global telemetry manager.
    
    Args:
        **kwargs: Arguments to pass to TelemetryManager constructor
        
    Returns:
        Initialized telemetry manager
    """
    global telemetry_manager
    telemetry_manager = TelemetryManager(**kwargs)
    return telemetry_manager