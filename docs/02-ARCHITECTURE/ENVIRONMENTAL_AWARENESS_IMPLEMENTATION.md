# Environmental Awareness Implementation Guide

## Core Principle: The AI Assistant Must Know Everything

For Luminous Nix to be a true NixOS management assistant, it needs comprehensive, real-time awareness of the entire system state. This document outlines the technical implementation.

## 1. System State Collection Architecture

```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import asyncio
import psutil
import dbus
import sqlite3

@dataclass
class SystemState:
    """Complete system state snapshot"""
    # Hardware
    cpu: CPUState
    memory: MemoryState
    disks: List[DiskState]
    network: NetworkState
    gpu: Optional[GPUState]
    sensors: SensorState
    
    # NixOS Specific
    nixos_version: str
    current_generation: int
    generations: List[Generation]
    channels: List[Channel]
    flakes: List[Flake]
    overlays: List[Overlay]
    
    # Services & Processes
    services: List[ServiceState]
    processes: List[ProcessState]
    containers: List[ContainerState]
    
    # Configuration
    config_files: Dict[str, str]  # Path -> content
    environment_vars: Dict[str, str]
    kernel_params: List[str]
    boot_config: BootConfig
    
    # Security
    firewall_rules: List[FirewallRule]
    open_ports: List[Port]
    users: List[User]
    groups: List[Group]
    permissions: PermissionState
    
    # Performance Metrics
    load_average: LoadAverage
    io_stats: IOStats
    network_stats: NetworkStats
    
    # Timestamp
    collected_at: datetime
    collection_duration: float
```

## 2. Real-Time Monitoring System

### Continuous State Monitoring
```python
class SystemMonitor:
    """Real-time system state monitoring"""
    
    def __init__(self):
        self.state_cache = {}
        self.update_intervals = {
            'cpu': 1,      # Every second
            'memory': 5,   # Every 5 seconds
            'disk': 30,    # Every 30 seconds
            'network': 5,  # Every 5 seconds
            'services': 10, # Every 10 seconds
            'packages': 300, # Every 5 minutes
        }
        self.collectors = self._init_collectors()
        
    async def start_monitoring(self):
        """Start all monitoring tasks"""
        tasks = []
        for category, interval in self.update_intervals.items():
            task = asyncio.create_task(
                self._monitor_category(category, interval)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
    
    async def _monitor_category(self, category: str, interval: int):
        """Monitor a specific category continuously"""
        collector = self.collectors[category]
        while True:
            try:
                data = await collector.collect()
                self.state_cache[category] = {
                    'data': data,
                    'timestamp': time.time()
                }
                await self._check_alerts(category, data)
            except Exception as e:
                logger.error(f"Monitor error {category}: {e}")
            await asyncio.sleep(interval)
    
    async def _check_alerts(self, category: str, data: Any):
        """Check for conditions requiring user notification"""
        alerts = []
        
        if category == 'disk':
            for disk in data:
                if disk.usage_percent > 90:
                    alerts.append(f"Disk {disk.mount} is {disk.usage_percent}% full")
        
        if category == 'memory':
            if data.available < 500_000_000:  # Less than 500MB
                alerts.append("Memory critically low")
        
        if category == 'services':
            failed = [s for s in data if s.status == 'failed']
            if failed:
                alerts.append(f"{len(failed)} services have failed")
        
        for alert in alerts:
            await self.notify_user(alert)
```

### Event-Driven Updates
```python
class EventMonitor:
    """Monitor system events via D-Bus and inotify"""
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.systemd = self.bus.get_object(
            'org.freedesktop.systemd1',
            '/org/freedesktop/systemd1'
        )
        self.inotify = inotify.adapters.Inotify()
        
    def watch_systemd_events(self):
        """Watch for service state changes"""
        self.systemd.connect_to_signal(
            'UnitNew',
            self.on_unit_new
        )
        self.systemd.connect_to_signal(
            'UnitRemoved',
            self.on_unit_removed
        )
        self.systemd.connect_to_signal(
            'PropertiesChanged',
            self.on_properties_changed
        )
    
    def watch_config_files(self):
        """Watch NixOS configuration files for changes"""
        paths = [
            '/etc/nixos/configuration.nix',
            '/etc/nixos/hardware-configuration.nix',
            '~/.config/nixpkgs/home.nix'
        ]
        for path in paths:
            self.inotify.add_watch(path)
    
    def on_config_change(self, event):
        """Handle configuration file changes"""
        logger.info(f"Config changed: {event.path}")
        # Trigger re-analysis of configuration
        self.analyze_config_change(event.path)
```

## 3. NixOS-Specific State Collection

### Package & Generation Management
```python
class NixOSCollector:
    """Collect NixOS-specific system state"""
    
    async def collect_generations(self) -> List[Generation]:
        """Get all system generations"""
        result = await run_command("nix-env --list-generations -p /nix/var/nix/profiles/system")
        return self.parse_generations(result)
    
    async def collect_packages(self) -> Dict[str, List[Package]]:
        """Collect all installed packages by profile"""
        packages = {}
        
        # System packages
        packages['system'] = await self.get_system_packages()
        
        # User packages
        for user in self.get_users():
            packages[user] = await self.get_user_packages(user)
        
        # Home-manager packages
        if await self.has_home_manager():
            packages['home-manager'] = await self.get_home_manager_packages()
        
        return packages
    
    async def collect_configuration(self) -> NixConfig:
        """Parse and understand current configuration"""
        config_path = "/etc/nixos/configuration.nix"
        
        # Read raw configuration
        with open(config_path) as f:
            raw_config = f.read()
        
        # Parse with rnix-parser for AST
        ast = await self.parse_nix_ast(raw_config)
        
        # Extract key settings
        return NixConfig(
            raw=raw_config,
            ast=ast,
            imports=self.extract_imports(ast),
            packages=self.extract_packages(ast),
            services=self.extract_services(ast),
            users=self.extract_users(ast),
            networking=self.extract_networking(ast),
            boot=self.extract_boot(ast)
        )
    
    async def analyze_config_implications(self, changes: str) -> Analysis:
        """Understand what a configuration change would do"""
        # Create temporary configuration
        temp_config = self.apply_changes(self.current_config, changes)
        
        # Dry-run build
        result = await run_command(
            f"nixos-rebuild dry-build -I nixos-config={temp_config}"
        )
        
        # Parse what would change
        return Analysis(
            packages_added=self.parse_additions(result),
            packages_removed=self.parse_removals(result),
            services_affected=self.parse_service_changes(result),
            disk_space_needed=self.parse_space_requirement(result),
            download_size=self.parse_download_size(result),
            risks=self.assess_risks(result)
        )
```

### Flake & Channel Management
```python
class FlakeManager:
    """Manage Nix flakes and channels"""
    
    async def collect_flakes(self) -> List[Flake]:
        """Collect all flakes in the system"""
        flakes = []
        
        # System flake
        if os.path.exists("/etc/nixos/flake.nix"):
            flakes.append(await self.parse_flake("/etc/nixos/flake.nix"))
        
        # User flakes
        for project in self.find_flake_projects():
            flakes.append(await self.parse_flake(project))
        
        return flakes
    
    async def collect_channels(self) -> List[Channel]:
        """Get all configured channels"""
        result = await run_command("nix-channel --list")
        channels = []
        
        for line in result.split('\n'):
            if line:
                name, url = line.split()
                # Get channel metadata
                metadata = await self.get_channel_metadata(url)
                channels.append(Channel(
                    name=name,
                    url=url,
                    branch=metadata.branch,
                    revision=metadata.revision,
                    last_updated=metadata.updated
                ))
        
        return channels
```

## 4. Intelligent Context Understanding

### Intent Recognition with Context
```python
class ContextAwareIntentRecognizer:
    """Understand user intent based on system context"""
    
    def __init__(self, system_state: SystemState):
        self.state = system_state
        self.history = CommandHistory()
        
    def recognize_intent(self, query: str) -> ContextualIntent:
        """Recognize intent with full system context"""
        
        # Basic intent recognition
        base_intent = self.parse_query(query)
        
        # Enhance with context
        if "slow" in query.lower():
            # Check what might be causing slowness
            if self.state.memory.available < 1_000_000_000:
                base_intent.context['likely_cause'] = 'low_memory'
                base_intent.suggestions.append('close memory-intensive applications')
            
            if self.state.cpu.usage > 90:
                high_cpu_process = self.find_high_cpu_process()
                base_intent.context['likely_cause'] = 'high_cpu'
                base_intent.context['culprit'] = high_cpu_process
        
        if "broken" in query.lower():
            # Check recent failures
            failed_services = self.state.get_failed_services()
            if failed_services:
                base_intent.context['failed_services'] = failed_services
                base_intent.suggestions.append(
                    f"Service {failed_services[0]} failed. View logs?"
                )
        
        if "update" in query.lower():
            # Check update context
            if self.state.has_security_updates():
                base_intent.priority = 'high'
                base_intent.context['security_updates'] = True
            
            if self.state.disk.free_space < 5_000_000_000:
                base_intent.warnings.append(
                    "Low disk space. Updates need ~3GB free"
                )
        
        return base_intent
```

### Predictive Assistance
```python
class PredictiveAssistant:
    """Predict user needs based on patterns and state"""
    
    def __init__(self):
        self.pattern_db = PatternDatabase()
        self.ml_model = load_model('intent_prediction.pkl')
        
    async def predict_next_action(self, state: SystemState, history: List[Command]) -> List[Prediction]:
        """Predict what user might want to do next"""
        
        predictions = []
        
        # Time-based patterns
        current_time = datetime.now()
        if current_time.hour == 9 and current_time.weekday() < 5:
            # Workday morning
            if 'docker' not in state.running_services:
                predictions.append(
                    Prediction(
                        action="start docker",
                        confidence=0.8,
                        reason="Usually started at this time"
                    )
                )
        
        # Sequence patterns
        if history[-1].action == 'install_package':
            package = history[-1].package
            related = self.get_related_packages(package)
            predictions.append(
                Prediction(
                    action=f"install {related[0]}",
                    confidence=0.6,
                    reason=f"Often installed with {package}"
                )
            )
        
        # State-based predictions
        if state.disk.usage_percent > 85:
            predictions.append(
                Prediction(
                    action="garbage collect",
                    confidence=0.9,
                    reason="Disk space is low"
                )
            )
        
        return sorted(predictions, key=lambda p: p.confidence, reverse=True)[:3]
```

## 5. Configuration Generation Intelligence

### Smart Configuration Builder
```python
class ConfigurationGenerator:
    """Generate complete NixOS configurations from natural language"""
    
    def __init__(self):
        self.templates = load_templates()
        self.validator = NixValidator()
        
    async def generate_config(self, request: str, state: SystemState) -> str:
        """Generate a complete configuration.nix"""
        
        # Parse the request
        requirements = self.parse_requirements(request)
        
        # Start with base configuration
        config = self.get_base_config(state)
        
        # Add requested features
        for req in requirements:
            if req.type == 'service':
                config = self.add_service(config, req.service, state)
            elif req.type == 'package':
                config = self.add_package(config, req.package)
            elif req.type == 'user':
                config = self.add_user(config, req.user)
        
        # Optimize configuration
        config = self.optimize_config(config, state)
        
        # Validate
        validation = await self.validator.validate(config)
        if not validation.valid:
            config = self.fix_issues(config, validation.issues)
        
        return config
    
    def add_service(self, config: NixConfig, service: str, state: SystemState) -> NixConfig:
        """Intelligently add a service with all dependencies"""
        
        if service == 'nginx':
            # Check if ports 80/443 are free
            if state.is_port_used(80):
                config.add_comment("Port 80 in use, configuring nginx on 8080")
                config.services.nginx.port = 8080
            
            # Add firewall rules
            config.networking.firewall.allowedTCPPorts.extend([80, 443])
            
            # If SSL requested, add Let's Encrypt
            if 'ssl' in service or 'https' in service:
                config.security.acme.enable = True
        
        return config
```

## 6. Complete OS Operation Methods

### Service Management
```python
class ServiceManager:
    """Complete systemd service management"""
    
    async def manage_service(self, action: str, service: str) -> Result:
        actions = {
            'start': self.start_service,
            'stop': self.stop_service,
            'restart': self.restart_service,
            'enable': self.enable_service,
            'disable': self.disable_service,
            'status': self.get_status,
            'logs': self.get_logs
        }
        return await actions[action](service)
    
    async def create_service(self, spec: ServiceSpec) -> Result:
        """Create a new systemd service"""
        service_config = f"""
        systemd.services.{spec.name} = {{
            description = "{spec.description}";
            wantedBy = [ "multi-user.target" ];
            after = {spec.after};
            serviceConfig = {{
                Type = "{spec.type}";
                ExecStart = "{spec.exec_start}";
                Restart = "{spec.restart}";
                User = "{spec.user}";
                {self.generate_limits(spec.limits)}
            }};
        }};
        """
        return await self.add_to_configuration(service_config)
```

### Network Management
```python
class NetworkManager:
    """Complete network configuration management"""
    
    async def configure_interface(self, interface: str, config: InterfaceConfig) -> Result:
        """Configure network interface"""
        nix_config = f"""
        networking.interfaces.{interface} = {{
            ipv4.addresses = [ {{
                address = "{config.ip}";
                prefixLength = {config.prefix};
            }} ];
            ipv6.addresses = [ {{
                address = "{config.ipv6}";
                prefixLength = {config.ipv6_prefix};
            }} ];
        }};
        """
        return await self.apply_network_config(nix_config)
    
    async def configure_wifi(self, ssid: str, password: str) -> Result:
        """Configure WiFi connection"""
        # Securely store password
        password_file = await self.store_secret(password)
        
        config = f"""
        networking.wireless.networks."{ssid}" = {{
            pskRaw = builtins.readFile {password_file};
        }};
        """
        return await self.apply_network_config(config)
```

### Hardware Management
```python
class HardwareManager:
    """Hardware configuration and management"""
    
    async def configure_graphics(self, driver: str) -> Result:
        """Configure graphics drivers"""
        configs = {
            'nvidia': self.configure_nvidia,
            'amd': self.configure_amd,
            'intel': self.configure_intel,
            'hybrid': self.configure_hybrid_graphics
        }
        return await configs[driver]()
    
    async def configure_nvidia(self) -> Result:
        """Configure NVIDIA drivers with optimal settings"""
        config = """
        services.xserver.videoDrivers = [ "nvidia" ];
        hardware.nvidia = {
            modesetting.enable = true;
            powerManagement.enable = true;
            prime = {
                sync.enable = true;
                nvidiaBusId = "PCI:1:0:0";
                intelBusId = "PCI:0:2:0";
            };
        };
        """
        return await self.apply_hardware_config(config)
```

## 7. Safety & Validation Layer

### Change Validation
```python
class SafetyValidator:
    """Validate all changes before applying"""
    
    async def validate_change(self, change: Change, state: SystemState) -> Validation:
        """Comprehensive validation of proposed changes"""
        
        checks = []
        
        # Check disk space
        space_needed = await self.calculate_space_needed(change)
        if space_needed > state.disk.free_space:
            checks.append(ValidationError(
                level='critical',
                message=f"Insufficient disk space. Need {space_needed}, have {state.disk.free_space}"
            ))
        
        # Check for conflicts
        conflicts = await self.check_conflicts(change, state)
        if conflicts:
            checks.append(ValidationWarning(
                level='warning',
                message=f"Potential conflicts: {conflicts}"
            ))
        
        # Check for breaking changes
        if await self.is_breaking_change(change):
            checks.append(ValidationWarning(
                level='warning',
                message="This change may break existing functionality",
                suggestion="Create a backup generation first"
            ))
        
        # Dry run
        dry_run_result = await self.dry_run(change)
        if not dry_run_result.success:
            checks.append(ValidationError(
                level='critical',
                message=f"Dry run failed: {dry_run_result.error}"
            ))
        
        return Validation(
            valid=not any(c.level == 'critical' for c in checks),
            checks=checks,
            estimated_time=self.estimate_time(change),
            download_size=self.calculate_downloads(change)
        )
```

## 8. Performance Optimization

### Caching Strategy for Environmental Data
```python
class EnvironmentCache:
    """Multi-tier cache for system state"""
    
    def __init__(self):
        self.memory_cache = {}  # Hot cache (1s TTL)
        self.redis_cache = redis.Redis()  # Warm cache (10s TTL)
        self.disk_cache = DiskCache()  # Cold cache (60s TTL)
        
        self.ttls = {
            'cpu': 1,      # Very dynamic
            'memory': 2,   # Dynamic
            'processes': 3, # Dynamic
            'network': 5,   # Semi-dynamic
            'services': 10, # Semi-static
            'packages': 60, # Mostly static
            'config': 300,  # Static
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from fastest available cache"""
        # L1: Memory
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry['timestamp'] < self.ttls.get(key, 60):
                return entry['data']
        
        # L2: Redis
        if cached := await self.redis_cache.get(key):
            data = json.loads(cached)
            self.memory_cache[key] = {'data': data, 'timestamp': time.time()}
            return data
        
        # L3: Disk
        if cached := await self.disk_cache.get(key):
            await self.redis_cache.set(key, json.dumps(cached))
            self.memory_cache[key] = {'data': cached, 'timestamp': time.time()}
            return cached
        
        return None
```

## 9. Integration Points

### D-Bus Integration for SystemD
```python
import dbus

class SystemDBus:
    """Direct systemd integration via D-Bus"""
    
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.systemd = self.bus.get_object(
            'org.freedesktop.systemd1',
            '/org/freedesktop/systemd1'
        )
        self.manager = dbus.Interface(
            self.systemd,
            'org.freedesktop.systemd1.Manager'
        )
    
    def get_unit_status(self, unit: str) -> dict:
        """Get detailed unit status"""
        unit_path = self.manager.LoadUnit(unit)
        unit_obj = self.bus.get_object('org.freedesktop.systemd1', unit_path)
        props = dbus.Interface(unit_obj, 'org.freedesktop.DBus.Properties')
        
        return {
            'active_state': props.Get('org.freedesktop.systemd1.Unit', 'ActiveState'),
            'sub_state': props.Get('org.freedesktop.systemd1.Unit', 'SubState'),
            'load_state': props.Get('org.freedesktop.systemd1.Unit', 'LoadState'),
            'description': props.Get('org.freedesktop.systemd1.Unit', 'Description'),
        }
```

### Native Nix Store API
```python
import ctypes

class NixStoreAPI:
    """Direct access to Nix store via C API"""
    
    def __init__(self):
        self.libnixstore = ctypes.CDLL('libnixstore.so')
        self._init_store()
    
    def query_path_info(self, path: str) -> PathInfo:
        """Query detailed path information"""
        info = self.libnixstore.queryPathInfo(path.encode())
        return PathInfo(
            size=info.narSize,
            references=self._parse_references(info.references),
            deriver=info.deriver,
            registration_time=info.registrationTime
        )
    
    def query_dependencies(self, path: str) -> List[str]:
        """Get all dependencies of a store path"""
        deps = self.libnixstore.queryReferences(path.encode())
        return [dep.decode() for dep in deps]
```

## 10. Full Implementation Checklist

### Phase 1: Core Environmental Awareness (Current Focus)
- [x] Basic system info (CPU, memory, disk)
- [x] Package listing
- [ ] Service status monitoring
- [ ] Network interface detection
- [ ] User and group enumeration
- [ ] Configuration file parsing

### Phase 2: Real-Time Monitoring
- [ ] Continuous state updates
- [ ] Event-driven notifications
- [ ] Performance metrics collection
- [ ] Alert system
- [ ] Historical data storage

### Phase 3: Intelligent Assistance
- [ ] Context-aware intent recognition
- [ ] Predictive suggestions
- [ ] Automatic issue detection
- [ ] Configuration validation
- [ ] Risk assessment

### Phase 4: Complete OS Management
- [ ] All systemd operations
- [ ] Network configuration
- [ ] Hardware management
- [ ] User management
- [ ] Security configuration
- [ ] Backup and recovery

### Phase 5: Advanced Features
- [ ] Configuration generation from requirements
- [ ] Automated optimization
- [ ] Multi-system management
- [ ] Declarative deployment
- [ ] Infrastructure as code

## Success Metrics

### Coverage
- **100%** of common NixOS operations
- **95%** of advanced operations
- **100%** of configuration options

### Performance
- **<100ms** for cached state queries
- **<1s** for fresh state collection
- **<10ms** for intent recognition
- **Real-time** event processing

### Intelligence
- **>90%** intent recognition accuracy
- **>80%** useful predictive suggestions
- **100%** critical issue detection
- **Zero** unsafe operations allowed

## Conclusion

Full environmental awareness requires:
1. **Comprehensive data collection** from all system sources
2. **Real-time monitoring** with event-driven updates
3. **Intelligent caching** for instant responses
4. **Deep NixOS integration** via native APIs
5. **Safety validation** for all operations

This forms the foundation for an AI assistant that truly understands and can manage the entire NixOS system through natural conversation.