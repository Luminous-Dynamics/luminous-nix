"""
D-Bus helper using subprocess calls.

This approach avoids the complex build dependencies of dbus-python
while still providing full D-Bus functionality.
"""

import json
import subprocess
import sys
from typing import Dict, List, Any, Optional

# Use standard library logging by importing from sys.modules
import importlib
stdlib_logging = importlib.import_module('logging')
logger = stdlib_logging.getLogger(__name__)


class DBusHelper:
    """Helper class for D-Bus operations using busctl."""
    
    @staticmethod
    def list_services() -> List[str]:
        """List all available D-Bus services."""
        try:
            result = subprocess.run(
                ['busctl', 'list', '--json=short'],
                capture_output=True,
                text=True,
                check=True
            )
            services = json.loads(result.stdout)
            return [s['name'] for s in services if 'name' in s]
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Failed to list D-Bus services: {e}")
            return []
    
    @staticmethod
    def get_service_status(service: str) -> Optional[str]:
        """Get the status of a systemd service via D-Bus."""
        try:
            result = subprocess.run(
                [
                    'busctl', 'get-property',
                    'org.freedesktop.systemd1',
                    f'/org/freedesktop/systemd1/unit/{service.replace("-", "_2d").replace(".", "_2e")}_2eservice',
                    'org.freedesktop.systemd1.Unit',
                    'ActiveState'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse output: "s "active""
            status = result.stdout.strip().split('"')[1]
            return status
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def restart_service(service: str) -> bool:
        """Restart a systemd service via D-Bus."""
        try:
            subprocess.run(
                [
                    'busctl', 'call',
                    'org.freedesktop.systemd1',
                    '/org/freedesktop/systemd1',
                    'org.freedesktop.systemd1.Manager',
                    'RestartUnit',
                    'ss',
                    f'{service}.service',
                    'replace'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart service {service}: {e}")
            return False
    
    @staticmethod
    def monitor_signals(callback, service: Optional[str] = None):
        """
        Monitor D-Bus signals (would need to be run in a separate thread).
        
        Example:
            busctl monitor org.freedesktop.systemd1
        """
        cmd = ['busctl', 'monitor']
        if service:
            cmd.append(service)
        else:
            cmd.append('org.freedesktop.systemd1')
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in process.stdout:
                if callback:
                    callback(line.strip())
                    
        except Exception as e:
            logger.error(f"Error monitoring D-Bus signals: {e}")
    
    @staticmethod
    def get_system_properties() -> Dict[str, Any]:
        """Get system properties from systemd via D-Bus."""
        properties = {}
        
        try:
            # Get system state
            result = subprocess.run(
                [
                    'busctl', 'get-property',
                    'org.freedesktop.systemd1',
                    '/org/freedesktop/systemd1',
                    'org.freedesktop.systemd1.Manager',
                    'SystemState'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            properties['system_state'] = result.stdout.strip().split('"')[1]
            
            # Get number of failed units
            result = subprocess.run(
                [
                    'busctl', 'get-property',
                    'org.freedesktop.systemd1',
                    '/org/freedesktop/systemd1',
                    'org.freedesktop.systemd1.Manager',
                    'NFailedUnits'
                ],
                capture_output=True,
                text=True,
                check=True
            )
            properties['failed_units'] = int(result.stdout.strip().split()[1])
            
        except (subprocess.CalledProcessError, IndexError, ValueError) as e:
            logger.error(f"Failed to get system properties: {e}")
        
        return properties
    
    @staticmethod
    def send_notification(title: str, message: str, urgency: str = "normal") -> bool:
        """Send a desktop notification via D-Bus."""
        try:
            subprocess.run(
                [
                    'notify-send',
                    '--urgency', urgency,
                    title,
                    message
                ],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            # Fallback to direct D-Bus call
            try:
                subprocess.run(
                    [
                        'busctl', 'call',
                        '--user',
                        'org.freedesktop.Notifications',
                        '/org/freedesktop/Notifications',
                        'org.freedesktop.Notifications',
                        'Notify',
                        'susssasa{sv}i',
                        'luminous-nix',  # app_name
                        '0',  # replaces_id
                        '',  # icon
                        title,
                        message,
                        '0',  # actions (array)
                        '0',  # hints (dict)
                        '5000'  # timeout in ms
                    ],
                    check=True
                )
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to send notification: {e}")
                return False


# Convenience functions
def check_service_health() -> Dict[str, Any]:
    """Check the health of critical services."""
    helper = DBusHelper()
    
    critical_services = [
        'NetworkManager',
        'systemd-resolved',
        'sshd',
        'nix-daemon'
    ]
    
    health = {
        'healthy': [],
        'unhealthy': [],
        'unknown': []
    }
    
    for service in critical_services:
        status = helper.get_service_status(service)
        if status == 'active':
            health['healthy'].append(service)
        elif status:
            health['unhealthy'].append((service, status))
        else:
            health['unknown'].append(service)
    
    return health


def monitor_system_changes(callback):
    """Monitor system changes via D-Bus."""
    helper = DBusHelper()
    
    def process_signal(line: str):
        """Process D-Bus signal and call callback if relevant."""
        if 'UnitNew' in line or 'UnitRemoved' in line:
            callback('unit_change', line)
        elif 'JobNew' in line or 'JobRemoved' in line:
            callback('job_change', line)
        elif 'PropertiesChanged' in line:
            callback('properties_change', line)
    
    helper.monitor_signals(process_signal)


if __name__ == "__main__":
    # Test the helper
    helper = DBusHelper()
    
    print("System Properties:")
    print(helper.get_system_properties())
    
    print("\nService Health:")
    print(check_service_health())
    
    print("\nSending test notification...")
    helper.send_notification(
        "Luminous Nix",
        "D-Bus integration is working!",
        "normal"
    )