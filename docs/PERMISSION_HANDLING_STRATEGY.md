# 🔐 Permission Handling Strategy for Self-Healing System

## 🎯 The Challenge

The self-healing system needs to perform both privileged and unprivileged operations:

### Requires Root (sudo)
- NixOS generation switching
- System service restarts
- CPU governor changes
- Network interface management
- System-wide cache clearing
- Process killing (system processes)

### Works Without Root
- Configuration file reading
- Backup creation (in user directories)
- Metrics collection (most)
- Issue detection
- Learning/knowledge storage
- Process renicing (own processes)

## 🏗️ Recommended Architecture

### Option 1: Hybrid Service Model (RECOMMENDED)
```
┌─────────────────────────────────────┐
│         User Space                   │
├─────────────────────────────────────┤
│  Monitoring & Detection Service      │
│  (Runs as regular user)              │
│  - Detects issues                    │
│  - Creates backups                   │
│  - Exposes metrics                   │
│  - Plans healing actions             │
└─────────┬───────────────────────────┘
          │ Unix Socket / DBus
          ▼
┌─────────────────────────────────────┐
│      Privileged Space                │
├─────────────────────────────────────┤
│  Healing Executor Service            │
│  (Runs as systemd service with root) │
│  - Executes approved healing plans   │
│  - Performs system changes           │
│  - Reports results back              │
└─────────────────────────────────────┘
```

### Implementation Steps

#### 1. Create SystemD Service for Privileged Operations
```nix
# /etc/nixos/luminous-healing.nix
{ config, pkgs, ... }:

{
  systemd.services.luminous-healing = {
    description = "Luminous Nix Healing Executor";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    
    serviceConfig = {
      Type = "simple";
      ExecStart = "${pkgs.python3}/bin/python /srv/luminous-dynamics/11-meta-consciousness/luminous-nix/healing_executor_service.py";
      Restart = "always";
      RestartSec = 10;
      
      # Security hardening
      PrivateTmp = true;
      ProtectSystem = "strict";
      ProtectHome = true;
      ReadWritePaths = [ 
        "/etc/nixos"
        "/var/lib/luminous-nix"
        "/sys/devices/system/cpu"
      ];
      
      # Capabilities needed
      AmbientCapabilities = [
        "CAP_SYS_NICE"      # Process priority
        "CAP_KILL"          # Kill processes
        "CAP_NET_ADMIN"     # Network management
        "CAP_SYS_ADMIN"     # System administration
      ];
    };
  };
}
```

#### 2. Create Communication Layer
```python
# healing_executor_service.py
import asyncio
import json
from pathlib import Path
import socket
import os

class HealingExecutorService:
    """Privileged healing executor that runs as systemd service"""
    
    def __init__(self):
        self.socket_path = Path("/run/luminous-healing.sock")
        self.authorized_plans = []
        
    async def start(self):
        """Start the Unix socket server"""
        # Remove old socket if exists
        if self.socket_path.exists():
            os.unlink(self.socket_path)
            
        server = await asyncio.start_unix_server(
            self.handle_client,
            path=str(self.socket_path)
        )
        
        # Set socket permissions for user access
        os.chmod(self.socket_path, 0o660)
        
        async with server:
            await server.serve_forever()
    
    async def handle_client(self, reader, writer):
        """Handle healing requests from unprivileged monitor"""
        data = await reader.read(8192)
        request = json.loads(data.decode())
        
        # Validate request
        if not self.validate_request(request):
            response = {"success": False, "error": "Invalid request"}
        else:
            # Execute healing action
            response = await self.execute_healing(request)
        
        writer.write(json.dumps(response).encode())
        await writer.drain()
        writer.close()
    
    def validate_request(self, request):
        """Validate healing request is safe"""
        # Check request signature/token
        # Verify action is in allowed list
        # Check rate limits
        return True
    
    async def execute_healing(self, request):
        """Execute the privileged healing action"""
        action = request['action']
        
        if action == 'restart_service':
            return await self.restart_service(request['service'])
        elif action == 'set_cpu_governor':
            return await self.set_cpu_governor(request['governor'])
        elif action == 'rollback_generation':
            return await self.rollback_generation()
        # ... more actions
```

#### 3. Modify Healing Engine to Use Service
```python
# healing_engine.py modifications
class SelfHealingEngine:
    def __init__(self):
        self.executor_socket = Path("/run/luminous-healing.sock")
        
    async def execute_privileged_action(self, action: dict) -> dict:
        """Send action to privileged executor service"""
        if not self.executor_socket.exists():
            # Fallback to subprocess with sudo prompt
            return await self.execute_with_sudo(action)
        
        # Connect to executor service
        reader, writer = await asyncio.open_unix_connection(
            str(self.executor_socket)
        )
        
        # Send request
        writer.write(json.dumps(action).encode())
        await writer.drain()
        
        # Get response
        data = await reader.read(8192)
        response = json.loads(data.decode())
        
        writer.close()
        await writer.wait_closed()
        
        return response
```

### Option 2: Polkit Authorization (Desktop Systems)
```xml
<!-- /etc/polkit-1/rules.d/luminous-healing.rules -->
polkit.addRule(function(action, subject) {
    if (action.id == "org.luminous.healing.execute" &&
        subject.isInGroup("luminous-users")) {
        return polkit.Result.YES;
    }
});
```

### Option 3: Sudo with Specific Commands
```bash
# /etc/sudoers.d/luminous-healing
# Allow luminous healing without password for specific commands
tstoltz ALL=(ALL) NOPASSWD: /run/current-system/sw/bin/systemctl restart *
tstoltz ALL=(ALL) NOPASSWD: /run/current-system/sw/bin/nixos-rebuild switch
tstoltz ALL=(ALL) NOPASSWD: /usr/bin/cpupower frequency-set *
tstoltz ALL=(ALL) NOPASSWD: /usr/bin/renice *
```

## 🎯 Recommended Approach

### For Development/Testing: Option 3 (Sudo)
- Quick to implement
- Easy to test
- Good for single-user systems

### For Production: Option 1 (Hybrid Service)
- Proper separation of privileges
- No sudo prompts
- Secure communication
- Rate limiting and validation
- Audit logging

### For Desktop Systems: Option 2 (Polkit)
- Integrates with desktop environment
- User-friendly authorization
- GUI password prompts when needed

## 📝 Implementation Plan

### Phase 1: Current (User-Space Only)
✅ Monitor and detect issues
✅ Create backups in user directories
✅ Expose metrics
✅ Plan healing actions
⚠️ Cannot execute privileged healings

### Phase 2: Sudo Integration
```python
async def execute_with_sudo(self, command: List[str]) -> dict:
    """Execute command with sudo"""
    try:
        # Check if we can sudo without password
        check = subprocess.run(
            ['sudo', '-n', 'true'],
            capture_output=True
        )
        
        if check.returncode != 0:
            return {
                'success': False,
                'error': 'Sudo password required',
                'needs_auth': True
            }
        
        # Execute with sudo
        result = subprocess.run(
            ['sudo'] + command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### Phase 3: SystemD Service
- Create separate privileged executor
- Secure socket communication
- Request validation
- Audit logging

## 🔒 Security Considerations

### DO's
✅ Always validate healing requests
✅ Implement rate limiting
✅ Log all privileged actions
✅ Use minimal required privileges
✅ Separate detection from execution

### DON'Ts
❌ Never run entire monitor as root
❌ Don't store sudo passwords
❌ Avoid broad sudo permissions
❌ Don't bypass validation

## 📊 Current Status

### What Works Now (No Root)
- Issue detection ✅
- Backup creation ✅
- Metrics exposure ✅
- Planning ✅
- Learning ✅

### What Needs Root
- CPU governor changes ⚠️
- Service restarts ⚠️
- Generation rollback ⚠️
- Network management ⚠️

## 🚀 Quick Start for Testing

### 1. Add Sudo Rules (Temporary)
```bash
# For testing only - allows specific commands without password
echo "$(whoami) ALL=(ALL) NOPASSWD: /run/current-system/sw/bin/systemctl restart *" | sudo tee /etc/sudoers.d/luminous-test
```

### 2. Run Monitor as User
```bash
# Start the monitoring service as regular user
python start_metrics_server.py
```

### 3. Healing Will Prompt for Sudo
The system will attempt to heal and prompt for sudo when needed.

## 🎯 Best Practice Summary

For the Luminous Nix self-healing system:

1. **Keep monitoring unprivileged** - Run detection and metrics as user
2. **Isolate privileged operations** - Use systemd service or sudo
3. **Validate everything** - Never trust requests blindly
4. **Log extensively** - Audit trail for all privileged actions
5. **Fail safely** - If no privileges, report but don't break
6. **Progressive enhancement** - Work without root, better with it

---

*"The wise system requests only the privileges it truly needs, when it needs them."* 🌊