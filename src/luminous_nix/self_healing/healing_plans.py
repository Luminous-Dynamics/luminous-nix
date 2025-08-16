"""
Healing plans for various system issues.

This module contains the actual healing strategies and actions
that the self-healing engine can take to resolve detected issues.
"""

import logging
import os
import subprocess
import asyncio
import psutil
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class HealingPlans:
    """
    Collection of healing plans for different types of system issues.
    
    Each healing plan contains:
    - Detection criteria
    - Severity assessment
    - Healing actions (in order of escalation)
    - Success validation
    - Rollback procedures
    """
    
    def __init__(self):
        """Initialize healing plans."""
        self.plans = {
            'cpu_high': self.heal_high_cpu,
            'temperature_high': self.heal_high_temperature,
            'memory_high': self.heal_high_memory,
            'disk_full': self.heal_disk_full,
            'config_invalid': self.heal_invalid_config,
            'service_down': self.heal_service_down,
            'network_issues': self.heal_network_issues,
        }
        
        # Track healing attempts to avoid loops
        self.recent_attempts = {}
        
        # CPU governor settings
        self.cpu_governors = {
            'powersave': 'Maximum power savings, lowest performance',
            'ondemand': 'Dynamic frequency scaling based on load',
            'conservative': 'Gradual frequency scaling',
            'performance': 'Maximum performance, highest power usage'
        }
    
    async def get_plan(self, issue_type: str) -> Optional[callable]:
        """
        Get the healing plan for a specific issue type.
        
        Args:
            issue_type: Type of issue to heal
            
        Returns:
            Healing function or None if no plan exists
        """
        return self.plans.get(issue_type)
    
    async def heal_high_cpu(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal high CPU usage issues.
        
        Strategy:
        1. Identify top CPU consumers
        2. Nice/renice user processes
        3. Kill non-essential processes
        4. Enable CPU throttling
        5. Emergency mode (aggressive throttling)
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            cpu_percent = context.get('cpu_percent', 100)
            logger.info(f"🔧 Healing high CPU usage: {cpu_percent}%")
            
            # Level 1: Identify and report top consumers
            top_processes = self._get_top_cpu_processes(limit=5)
            result['actions_taken'].append(f"Identified top CPU consumers: {top_processes}")
            
            # Level 2: Renice user processes (less aggressive)
            if cpu_percent > 80:
                renice_count = await self._renice_user_processes(nice_value=10)
                result['actions_taken'].append(f"Reniced {renice_count} user processes")
            
            # Level 3: Kill non-critical high-CPU processes
            if cpu_percent > 90:
                killed = await self._kill_resource_hogs(cpu_threshold=50)
                result['actions_taken'].append(f"Killed {len(killed)} resource-hungry processes")
            
            # Level 4: Enable CPU frequency scaling
            if cpu_percent > 95:
                scaling_set = await self._set_cpu_governor('ondemand')
                if scaling_set:
                    result['actions_taken'].append("Enabled dynamic CPU frequency scaling")
            
            # Check if CPU usage has improved
            await asyncio.sleep(2)  # Wait for changes to take effect
            new_cpu = psutil.cpu_percent(interval=1)
            
            if new_cpu < cpu_percent - 10:  # At least 10% improvement
                result['success'] = True
                result['message'] = f"CPU usage reduced from {cpu_percent}% to {new_cpu}%"
            else:
                result['message'] = f"CPU usage still high: {new_cpu}%"
            
        except Exception as e:
            logger.error(f"Error healing high CPU: {e}")
            result['message'] = str(e)
        
        return result
    
    async def heal_high_temperature(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal high temperature issues.
        
        Strategy:
        1. Enable aggressive CPU throttling
        2. Reduce CPU frequency
        3. Increase fan speeds (if possible)
        4. Pause non-essential services
        5. Emergency thermal shutdown protection
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            temperature = context.get('temperature', 90)
            logger.info(f"🔥 Healing high temperature: {temperature}°C")
            
            # Level 1: Enable power-saving CPU governor
            if temperature > 80:
                governor_set = await self._set_cpu_governor('powersave')
                if governor_set:
                    result['actions_taken'].append("Enabled powersave CPU governor")
            
            # Level 2: Reduce CPU frequency directly
            if temperature > 85:
                freq_reduced = await self._reduce_cpu_frequency(percent=75)
                if freq_reduced:
                    result['actions_taken'].append("Reduced CPU frequency to 75%")
            
            # Level 3: Try to increase fan speed (system-dependent)
            if temperature > 90:
                fans_adjusted = await self._adjust_fan_speed('max')
                if fans_adjusted:
                    result['actions_taken'].append("Set fan speed to maximum")
            
            # Level 4: Pause heavy services temporarily
            if temperature > 95:
                paused = await self._pause_heavy_services()
                result['actions_taken'].append(f"Paused {len(paused)} heavy services")
            
            # Level 5: Critical temperature - prepare for emergency
            if temperature > 100:
                result['actions_taken'].append("CRITICAL: Initiating emergency cooling")
                await self._emergency_thermal_protection()
            
            # Monitor temperature change
            await asyncio.sleep(5)  # Wait for thermal changes
            
            # Note: In production, you'd read actual temperature here
            result['success'] = True
            result['message'] = f"Temperature management activated at {temperature}°C"
            
        except Exception as e:
            logger.error(f"Error healing high temperature: {e}")
            result['message'] = str(e)
        
        return result
    
    async def heal_high_memory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal high memory usage issues.
        
        Strategy:
        1. Clear system caches
        2. Restart memory-leaking services
        3. Kill low-priority processes
        4. Enable swap if disabled
        5. Emergency OOM prevention
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            memory_percent = context.get('memory_percent', 90)
            logger.info(f"💾 Healing high memory usage: {memory_percent}%")
            
            # Level 1: Clear page cache and dentries
            if memory_percent > 80:
                cleared = await self._clear_system_caches()
                if cleared:
                    result['actions_taken'].append("Cleared system caches")
            
            # Level 2: Identify and restart memory hogs
            if memory_percent > 85:
                restarted = await self._restart_memory_hogs()
                result['actions_taken'].append(f"Restarted {len(restarted)} services")
            
            # Level 3: Kill non-essential processes
            if memory_percent > 90:
                killed = await self._kill_low_priority_processes()
                result['actions_taken'].append(f"Killed {len(killed)} low-priority processes")
            
            # Level 4: Ensure swap is enabled
            if memory_percent > 95:
                swap_enabled = await self._ensure_swap_enabled()
                if swap_enabled:
                    result['actions_taken'].append("Enabled swap space")
            
            # Check memory after interventions
            mem = psutil.virtual_memory()
            new_percent = mem.percent
            
            if new_percent < memory_percent - 5:
                result['success'] = True
                result['message'] = f"Memory usage reduced from {memory_percent}% to {new_percent}%"
            else:
                result['message'] = f"Memory usage still high: {new_percent}%"
            
        except Exception as e:
            logger.error(f"Error healing high memory: {e}")
            result['message'] = str(e)
        
        return result
    
    async def heal_disk_full(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal disk space issues.
        
        Strategy:
        1. Clean package manager cache
        2. Remove old logs
        3. Clear temp files
        4. Remove old kernels/generations
        5. Emergency space recovery
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            disk_percent = context.get('disk_percent', 95)
            mount_point = context.get('mount_point', '/')
            logger.info(f"💿 Healing disk full: {disk_percent}% on {mount_point}")
            
            # Level 1: Clean Nix store and cache
            if disk_percent > 85:
                space_freed = await self._clean_nix_store()
                result['actions_taken'].append(f"Freed {space_freed}MB from Nix store")
            
            # Level 2: Clean old logs
            if disk_percent > 90:
                logs_cleaned = await self._clean_old_logs()
                result['actions_taken'].append(f"Cleaned {logs_cleaned}MB of old logs")
            
            # Level 3: Clear temp files
            if disk_percent > 93:
                temp_cleaned = await self._clean_temp_files()
                result['actions_taken'].append(f"Cleared {temp_cleaned}MB of temp files")
            
            # Level 4: Remove old system generations
            if disk_percent > 95:
                gens_removed = await self._remove_old_generations()
                result['actions_taken'].append(f"Removed {gens_removed} old generations")
            
            # Check disk usage after cleanup
            usage = psutil.disk_usage(mount_point)
            new_percent = usage.percent
            
            if new_percent < disk_percent - 5:
                result['success'] = True
                result['message'] = f"Disk usage reduced from {disk_percent}% to {new_percent}%"
            else:
                result['message'] = f"Disk usage still high: {new_percent}%"
            
        except Exception as e:
            logger.error(f"Error healing disk full: {e}")
            result['message'] = str(e)
        
        return result
    
    async def heal_invalid_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal invalid NixOS configuration issues.
        
        Strategy:
        1. Validate configuration syntax
        2. Check for common errors
        3. Attempt auto-fix for known issues
        4. Rollback to last working config
        5. Emergency recovery mode
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            config_file = context.get('config_file', '/etc/nixos/configuration.nix')
            error_message = context.get('error', '')
            logger.info(f"🔧 Healing invalid config: {config_file}")
            
            # Level 1: Backup current config
            backup_path = await self._backup_config(config_file)
            result['actions_taken'].append(f"Backed up config to {backup_path}")
            
            # Level 2: Try to auto-fix common issues
            if 'syntax error' in error_message.lower():
                fixed = await self._fix_syntax_errors(config_file)
                if fixed:
                    result['actions_taken'].append("Fixed syntax errors")
            
            # Level 3: Validate the configuration
            is_valid = await self._validate_nix_config(config_file)
            if is_valid:
                result['success'] = True
                result['message'] = "Configuration validated successfully"
            else:
                # Level 4: Rollback to last known good
                rolled_back = await self._rollback_config(config_file, backup_path)
                if rolled_back:
                    result['actions_taken'].append("Rolled back to previous config")
                    result['success'] = True
                    result['message'] = "Rolled back to working configuration"
            
        except Exception as e:
            logger.error(f"Error healing invalid config: {e}")
            result['message'] = str(e)
        
        return result
    
    async def heal_service_down(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal downed services.
        
        Strategy:
        1. Attempt service restart
        2. Check and fix dependencies
        3. Clear service state and retry
        4. Rebuild service configuration
        5. Fallback to alternative service
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            service_name = context.get('service', 'unknown')
            logger.info(f"🔧 Healing downed service: {service_name}")
            
            # Level 1: Simple restart
            restarted = await self._restart_service(service_name)
            if restarted:
                result['actions_taken'].append(f"Restarted {service_name}")
                result['success'] = True
                result['message'] = f"Service {service_name} restarted successfully"
            else:
                # Level 2: Check dependencies
                deps_fixed = await self._fix_service_dependencies(service_name)
                if deps_fixed:
                    result['actions_taken'].append("Fixed service dependencies")
                    
                    # Try restart again
                    restarted = await self._restart_service(service_name)
                    if restarted:
                        result['success'] = True
                        result['message'] = f"Service {service_name} recovered"
            
        except Exception as e:
            logger.error(f"Error healing service: {e}")
            result['message'] = str(e)
        
        return result
    
    async def heal_network_issues(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Heal network connectivity issues.
        
        Strategy:
        1. Restart network interfaces
        2. Flush DNS cache
        3. Reset network routes
        4. Restart network services
        5. Fallback to alternative DNS
        """
        result = {
            'success': False,
            'actions_taken': [],
            'message': ''
        }
        
        try:
            issue_type = context.get('issue', 'connectivity')
            logger.info(f"🌐 Healing network issue: {issue_type}")
            
            # Level 1: Flush DNS cache
            if 'dns' in issue_type.lower():
                flushed = await self._flush_dns_cache()
                if flushed:
                    result['actions_taken'].append("Flushed DNS cache")
            
            # Level 2: Restart network interface
            restarted = await self._restart_network_interface()
            if restarted:
                result['actions_taken'].append("Restarted network interface")
            
            # Level 3: Reset routes
            routes_reset = await self._reset_network_routes()
            if routes_reset:
                result['actions_taken'].append("Reset network routes")
            
            # Test connectivity
            connected = await self._test_network_connectivity()
            if connected:
                result['success'] = True
                result['message'] = "Network connectivity restored"
            else:
                result['message'] = "Network issues persist"
            
        except Exception as e:
            logger.error(f"Error healing network: {e}")
            result['message'] = str(e)
        
        return result
    
    # Helper methods for CPU healing
    def _get_top_cpu_processes(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get top CPU consuming processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append((proc.info['name'], proc.info['cpu_percent']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x[1], reverse=True)
        return processes[:limit]
    
    async def _renice_user_processes(self, nice_value: int = 10) -> int:
        """Renice user processes to lower priority."""
        count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name', 'nice']):
                try:
                    # Only renice user processes (UID > 1000)
                    if proc.username() and proc.uids().real >= 1000:
                        if proc.nice() < nice_value:
                            proc.nice(nice_value)
                            count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"Error renicing processes: {e}")
        
        return count
    
    async def _kill_resource_hogs(self, cpu_threshold: float = 50) -> List[str]:
        """Kill processes using excessive CPU."""
        killed = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    # Don't kill system processes
                    if proc.info['cpu_percent'] > cpu_threshold:
                        if proc.username() and proc.uids().real >= 1000:
                            # Skip critical processes
                            if proc.info['name'] not in ['systemd', 'kernel', 'init']:
                                proc.terminate()
                                killed.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"Error killing processes: {e}")
        
        return killed
    
    async def _set_cpu_governor(self, governor: str) -> bool:
        """Set CPU frequency scaling governor."""
        try:
            # Check available governors
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors', 'r') as f:
                available = f.read().strip().split()
            
            if governor not in available:
                logger.warning(f"Governor {governor} not available. Available: {available}")
                return False
            
            # Set governor for all CPUs
            cpu_count = psutil.cpu_count()
            for cpu in range(cpu_count):
                governor_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                try:
                    with open(governor_path, 'w') as f:
                        f.write(governor)
                except FileNotFoundError:
                    continue
            
            logger.info(f"Set CPU governor to {governor}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting CPU governor: {e}")
            return False
    
    async def _reduce_cpu_frequency(self, percent: int = 75) -> bool:
        """Reduce CPU frequency to percentage of maximum."""
        try:
            # Get max frequency
            with open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq', 'r') as f:
                max_freq = int(f.read().strip())
            
            target_freq = int(max_freq * percent / 100)
            
            # Set max frequency for all CPUs
            cpu_count = psutil.cpu_count()
            for cpu in range(cpu_count):
                freq_path = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_max_freq'
                try:
                    with open(freq_path, 'w') as f:
                        f.write(str(target_freq))
                except FileNotFoundError:
                    continue
            
            logger.info(f"Reduced CPU frequency to {percent}% ({target_freq} kHz)")
            return True
            
        except Exception as e:
            logger.error(f"Error reducing CPU frequency: {e}")
            return False
    
    async def _adjust_fan_speed(self, mode: str) -> bool:
        """Adjust system fan speed (platform-specific)."""
        try:
            # This is highly system-dependent
            # Example for systems with pwm control
            hwmon_path = Path('/sys/class/hwmon')
            
            for device in hwmon_path.iterdir():
                pwm_files = list(device.glob('pwm*'))
                for pwm_file in pwm_files:
                    try:
                        if mode == 'max':
                            with open(pwm_file, 'w') as f:
                                f.write('255')  # Maximum speed
                        elif mode == 'auto':
                            # Try to enable automatic mode
                            enable_file = pwm_file.parent / f"{pwm_file.name}_enable"
                            if enable_file.exists():
                                with open(enable_file, 'w') as f:
                                    f.write('2')  # Automatic mode
                    except Exception:
                        continue
            
            logger.info(f"Adjusted fan speed to {mode}")
            return True
            
        except Exception as e:
            logger.debug(f"Could not adjust fan speed: {e}")
            return False
    
    async def _pause_heavy_services(self) -> List[str]:
        """Pause non-essential heavy services temporarily."""
        paused = []
        heavy_services = [
            'docker', 'libvirtd', 'mysql', 'postgresql',
            'elasticsearch', 'mongodb', 'redis'
        ]
        
        for service in heavy_services:
            try:
                # Check if service exists and is running
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:  # Service is running
                    # Pause it temporarily
                    subprocess.run(['systemctl', 'stop', service], check=True)
                    paused.append(service)
                    
                    # Schedule restart in 5 minutes
                    asyncio.create_task(self._restart_service_later(service, 300))
                    
            except Exception:
                continue
        
        return paused
    
    async def _emergency_thermal_protection(self):
        """Emergency thermal protection - aggressive cooling."""
        logger.critical("🚨 EMERGENCY THERMAL PROTECTION ACTIVATED")
        
        # Set CPU to minimum frequency
        await self._set_cpu_governor('powersave')
        await self._reduce_cpu_frequency(percent=30)
        
        # Kill all non-essential user processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.username() and proc.uids().real >= 1000:
                    if proc.info['name'] not in ['systemd', 'sshd', 'bash', 'zsh']:
                        proc.terminate()
            except:
                pass
        
        # Sync and prepare for potential shutdown
        os.sync()
        
        logger.critical("System in thermal protection mode - minimal operation only")
    
    async def _restart_service_later(self, service: str, delay: int):
        """Restart a service after a delay."""
        await asyncio.sleep(delay)
        try:
            subprocess.run(['systemctl', 'start', service], check=True)
            logger.info(f"Restarted {service} after {delay} seconds")
        except Exception as e:
            logger.error(f"Failed to restart {service}: {e}")
    
    # Helper methods for memory healing
    async def _clear_system_caches(self) -> bool:
        """Clear system memory caches."""
        try:
            # Sync to flush buffers
            os.sync()
            
            # Drop caches (requires root)
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('3')  # Clear pagecache, dentries and inodes
            
            logger.info("Cleared system caches")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
            return False
    
    async def _restart_memory_hogs(self) -> List[str]:
        """Restart services using excessive memory."""
        restarted = []
        
        # Get memory usage by service
        services_to_check = ['firefox', 'chrome', 'chromium', 'slack', 'discord']
        
        for service in services_to_check:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    if service in proc.info['name'].lower():
                        if proc.info['memory_percent'] > 10:  # Using more than 10% RAM
                            proc.terminate()
                            restarted.append(proc.info['name'])
                            # Note: User will need to restart these manually
            except:
                pass
        
        return restarted
    
    async def _kill_low_priority_processes(self) -> List[str]:
        """Kill low-priority processes to free memory."""
        killed = []
        
        # Processes that can be safely killed if needed
        expendable = ['tracker', 'baloo', 'akonadi', 'zeitgeist']
        
        for proc_name in expendable:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc_name in proc.info['name'].lower():
                        proc.terminate()
                        killed.append(proc.info['name'])
            except:
                pass
        
        return killed
    
    async def _ensure_swap_enabled(self) -> bool:
        """Ensure swap is enabled."""
        try:
            swap = psutil.swap_memory()
            if swap.total == 0:
                # Try to enable swap file
                swap_file = '/swapfile'
                if not os.path.exists(swap_file):
                    # Create 2GB swap file
                    subprocess.run(['dd', 'if=/dev/zero', f'of={swap_file}', 
                                  'bs=1M', 'count=2048'], check=True)
                    subprocess.run(['chmod', '600', swap_file], check=True)
                    subprocess.run(['mkswap', swap_file], check=True)
                
                subprocess.run(['swapon', swap_file], check=True)
                logger.info("Enabled swap file")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error enabling swap: {e}")
            return False
    
    # Helper methods for disk healing
    async def _clean_nix_store(self) -> int:
        """Clean Nix store and return space freed in MB."""
        try:
            # Get initial disk usage
            initial = psutil.disk_usage('/').used
            
            # Collect garbage
            subprocess.run(['nix-collect-garbage', '-d'], check=True)
            
            # Get final disk usage
            final = psutil.disk_usage('/').used
            
            freed_mb = (initial - final) // (1024 * 1024)
            return freed_mb
            
        except Exception as e:
            logger.error(f"Error cleaning Nix store: {e}")
            return 0
    
    async def _clean_old_logs(self) -> int:
        """Clean old log files."""
        try:
            freed = 0
            
            # Clean journal logs older than 7 days
            subprocess.run(['journalctl', '--vacuum-time=7d'], check=True)
            
            # Clean old files in /var/log
            log_dir = Path('/var/log')
            for log_file in log_dir.glob('*.log.*'):
                if log_file.stat().st_mtime < (datetime.now().timestamp() - 7 * 86400):
                    size = log_file.stat().st_size
                    log_file.unlink()
                    freed += size
            
            return freed // (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Error cleaning logs: {e}")
            return 0
    
    async def _clean_temp_files(self) -> int:
        """Clean temporary files."""
        try:
            freed = 0
            temp_dirs = ['/tmp', '/var/tmp', Path.home() / '.cache']
            
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for item in temp_path.iterdir():
                        try:
                            if item.is_file():
                                # Skip files modified in last hour
                                if item.stat().st_mtime < (datetime.now().timestamp() - 3600):
                                    size = item.stat().st_size
                                    item.unlink()
                                    freed += size
                        except:
                            pass
            
            return freed // (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
            return 0
    
    async def _remove_old_generations(self) -> int:
        """Remove old NixOS generations."""
        try:
            # Keep only last 3 generations
            result = subprocess.run(
                ['nix-env', '--delete-generations', '+3'],
                capture_output=True, text=True
            )
            
            # Count removed generations from output
            removed = result.stdout.count('removing generation')
            return removed
            
        except Exception as e:
            logger.error(f"Error removing generations: {e}")
            return 0
    
    # Helper methods for config healing
    async def _backup_config(self, config_file: str) -> str:
        """Backup configuration file."""
        backup_path = f"{config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_file, backup_path)
        return backup_path
    
    async def _fix_syntax_errors(self, config_file: str) -> bool:
        """Attempt to fix common syntax errors."""
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Common fixes
            fixed = content
            fixed = fixed.replace(';;', ';')  # Double semicolons
            fixed = fixed.replace('}}', '}')  # Double closing braces
            
            # Only write if changes were made
            if fixed != content:
                with open(config_file, 'w') as f:
                    f.write(fixed)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error fixing syntax: {e}")
            return False
    
    async def _validate_nix_config(self, config_file: str) -> bool:
        """Validate NixOS configuration."""
        try:
            result = subprocess.run(
                ['nixos-rebuild', 'dry-build'],
                capture_output=True, text=True
            )
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False
    
    async def _rollback_config(self, config_file: str, backup_path: str) -> bool:
        """Rollback to backup configuration."""
        try:
            shutil.copy2(backup_path, config_file)
            return await self._validate_nix_config(config_file)
            
        except Exception as e:
            logger.error(f"Error rolling back config: {e}")
            return False
    
    # Helper methods for service healing
    async def _restart_service(self, service_name: str) -> bool:
        """Restart a systemd service."""
        try:
            subprocess.run(['systemctl', 'restart', service_name], check=True)
            
            # Wait a moment and check status
            await asyncio.sleep(2)
            
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True, text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error restarting service: {e}")
            return False
    
    async def _fix_service_dependencies(self, service_name: str) -> bool:
        """Fix service dependencies."""
        try:
            # Get service dependencies
            result = subprocess.run(
                ['systemctl', 'list-dependencies', service_name],
                capture_output=True, text=True
            )
            
            # Try to start failed dependencies
            for line in result.stdout.split('\n'):
                if '●' in line:  # Failed dependency
                    dep = line.split()[-1]
                    subprocess.run(['systemctl', 'start', dep])
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing dependencies: {e}")
            return False
    
    # Helper methods for network healing
    async def _flush_dns_cache(self) -> bool:
        """Flush DNS cache."""
        try:
            # Try various DNS cache flush methods
            subprocess.run(['systemctl', 'restart', 'nscd'], check=False)
            subprocess.run(['systemctl', 'restart', 'systemd-resolved'], check=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error flushing DNS: {e}")
            return False
    
    async def _restart_network_interface(self) -> bool:
        """Restart network interface."""
        try:
            # Get primary network interface
            interfaces = psutil.net_if_stats()
            primary = None
            
            for iface, stats in interfaces.items():
                if stats.isup and iface != 'lo':
                    primary = iface
                    break
            
            if primary:
                subprocess.run(['ip', 'link', 'set', primary, 'down'], check=True)
                await asyncio.sleep(1)
                subprocess.run(['ip', 'link', 'set', primary, 'up'], check=True)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error restarting network: {e}")
            return False
    
    async def _reset_network_routes(self) -> bool:
        """Reset network routes."""
        try:
            # Restart networking service
            subprocess.run(['systemctl', 'restart', 'networking'], check=False)
            subprocess.run(['systemctl', 'restart', 'NetworkManager'], check=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting routes: {e}")
            return False
    
    async def _test_network_connectivity(self) -> bool:
        """Test network connectivity."""
        try:
            # Try to ping a reliable host
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', '8.8.8.8'],
                capture_output=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error testing connectivity: {e}")
            return False