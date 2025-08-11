# Security Standards

## Core Principles

### Defense in Depth
- Multiple layers of security
- Assume any layer can fail
- Validate at every boundary
- Fail securely (deny by default)

### Least Privilege
- Minimal permissions required
- Separate privileges by function
- Drop privileges when possible
- Time-limited access

## Input Validation

### All User Input is Untrusted
```python
from typing import Optional
import re
from pathlib import Path

def validate_package_name(name: str) -> str:
    """Validate Nix package name."""
    # Only allow alphanumeric, dash, underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError(f"Invalid package name: {name}")

    # Prevent path traversal
    if '..' in name or '/' in name:
        raise ValueError(f"Invalid characters in package name: {name}")

    # Length limits
    if len(name) > 100:
        raise ValueError(f"Package name too long: {len(name)} > 100")

    return name

def validate_file_path(path_str: str, base_dir: Path) -> Path:
    """Validate file path is within allowed directory."""
    # Resolve to absolute path
    path = Path(path_str).resolve()

    # Ensure within allowed directory
    try:
        path.relative_to(base_dir.resolve())
    except ValueError:
        raise ValueError(f"Path outside allowed directory: {path}")

    return path
```

### Validation Rules
- Whitelist acceptable input (don't blacklist)
- Validate type, length, format, and range
- Canonicalize before validation
- Re-validate after transformation

## Command Execution

### Safe Subprocess Usage
```python
import subprocess
import shlex
from typing import List

# GOOD: List arguments, no shell
def safe_execute(cmd: List[str], timeout: int = 30) -> str:
    """Safely execute command."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
            # Security options
            env={'PATH': '/usr/bin:/bin'},  # Minimal PATH
            cwd='/',  # Known working directory
            # Prevent shell execution
            shell=False
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout}s")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr}")

# BAD: Never do this
def unsafe_execute(user_input: str) -> str:
    # VULNERABLE to command injection!
    return subprocess.run(
        f"nix-env -iA {user_input}",  # NO!
        shell=True,  # NO!
        capture_output=True
    ).stdout
```

### Command Sandboxing
```python
import os
import pwd

def drop_privileges(uid_name: str = 'nobody'):
    """Drop root privileges."""
    if os.getuid() != 0:
        # Not root, nothing to drop
        return

    # Get UID/GID for nobody user
    nobody = pwd.getpwnam(uid_name)

    # Remove group privileges
    os.setgroups([])

    # Set new UID/GID
    os.setgid(nobody.pw_gid)
    os.setuid(nobody.pw_uid)

    # Ensure we can't get privileges back
    if os.getuid() == 0 or os.getgid() == 0:
        raise RuntimeError("Failed to drop privileges")
```

## Authentication & Authorization

### Password Handling
```python
import hashlib
import secrets
import hmac

def hash_password(password: str) -> tuple[str, str]:
    """Hash password with salt."""
    # Generate random salt
    salt = secrets.token_hex(32)

    # Use PBKDF2 for password hashing
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )

    return salt, pwdhash.hex()

def verify_password(password: str, salt: str, pwdhash: str) -> bool:
    """Verify password against hash."""
    new_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )

    # Use constant-time comparison
    return hmac.compare_digest(new_hash.hex(), pwdhash)
```

### Session Management
```python
import secrets
from datetime import datetime, timedelta

class SessionManager:
    """Secure session management."""

    def create_session(self, user_id: str) -> str:
        """Create secure session token."""
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)

        # Store with expiration
        self.sessions[token] = {
            'user_id': user_id,
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(hours=24)
        }

        return token

    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token."""
        session = self.sessions.get(token)

        if not session:
            return None

        # Check expiration
        if datetime.now() > session['expires']:
            del self.sessions[token]
            return None

        # Refresh expiration on activity
        session['expires'] = datetime.now() + timedelta(hours=24)

        return session['user_id']
```

## Secrets Management

### Environment Variables
```python
import os
from pathlib import Path

class Config:
    """Secure configuration management."""

    def __init__(self):
        # Never hardcode secrets
        self.api_key = os.environ.get('API_KEY')
        if not self.api_key:
            raise ValueError("API_KEY environment variable not set")

        # Use secrets file for sensitive data
        secrets_file = Path(os.environ.get('SECRETS_FILE', '/run/secrets/app'))
        if secrets_file.exists():
            self.load_secrets(secrets_file)

    def load_secrets(self, path: Path):
        """Load secrets from file."""
        # Ensure proper permissions
        if path.stat().st_mode & 0o077:
            raise ValueError(f"Secrets file has insecure permissions: {path}")

        with open(path) as f:
            # Parse secrets securely
            pass
```

### Never Commit
- Passwords, API keys, tokens
- Private keys or certificates
- Database credentials
- AWS/cloud credentials
- .env files with real values

## Cryptography

### Use Established Libraries
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

def encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt data with password."""
    # Derive key from password
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=os.urandom(16),
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    # Encrypt with Fernet
    f = Fernet(key)
    return f.encrypt(data)

# NEVER: Roll your own crypto
def bad_encrypt(data: str, key: str) -> str:
    # This is NOT secure encryption!
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(data, key))
```

## Network Security

### TLS/HTTPS
```python
import ssl
import urllib.request

def secure_request(url: str) -> str:
    """Make secure HTTPS request."""
    # Create secure SSL context
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    # Optional: Pin certificate
    # context.load_verify_locations('/path/to/ca-cert.pem')

    with urllib.request.urlopen(url, context=context) as response:
        return response.read().decode()
```

### API Security
```python
from functools import wraps
from flask import request, jsonify
import hmac
import time

def require_api_key(f):
    """Require valid API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'No API key provided'}), 401

        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 403

        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests: int = 100, window: int = 3600):
    """Rate limit decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = request.remote_addr

            # Check rate limit
            if exceeded_rate_limit(client_id, max_requests, window):
                return jsonify({'error': 'Rate limit exceeded'}), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## File Operations

### Safe File Handling
```python
import tempfile
import os
from pathlib import Path

def safe_write_file(content: str, filename: str, base_dir: Path):
    """Safely write file with atomic operation."""
    # Validate filename
    if '/' in filename or '..' in filename:
        raise ValueError(f"Invalid filename: {filename}")

    # Create in temp directory first
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=base_dir,
        delete=False,
        prefix='tmp_',
        suffix='.tmp'
    ) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name

    # Set secure permissions
    os.chmod(tmp_path, 0o644)

    # Atomic rename
    target_path = base_dir / filename
    os.rename(tmp_path, target_path)

    return target_path
```

## Logging & Monitoring

### Security Logging
```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    """Log security-relevant events."""

    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('/var/log/app/security.log')
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_auth_attempt(self, username: str, success: bool, ip: str):
        """Log authentication attempt."""
        self.logger.info(json.dumps({
            'event': 'auth_attempt',
            'username': username,
            'success': success,
            'ip': ip,
            'timestamp': datetime.now().isoformat()
        }))

    def log_suspicious_activity(self, description: str, context: dict):
        """Log suspicious activity."""
        self.logger.warning(json.dumps({
            'event': 'suspicious_activity',
            'description': description,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }))
```

### What to Log
- Authentication attempts (success/failure)
- Authorization failures
- Input validation failures
- System errors and exceptions
- Configuration changes
- Privilege escalations

### What NOT to Log
- Passwords or authentication tokens
- Full credit card numbers
- Personal identification numbers
- Session tokens
- Encryption keys

## Dependency Security

### Checking Dependencies
```bash
# Check for known vulnerabilities
pip-audit

# Update dependencies
poetry update

# Lock dependencies
poetry lock

# Review dependency tree
poetry show --tree
```

### Supply Chain Security
```python
# requirements.txt with hashes
cryptography==41.0.0 \
    --hash=sha256:abc123...
requests==2.31.0 \
    --hash=sha256:def456...
```

## Security Checklist

### Before Deployment
- [ ] All user input validated
- [ ] No hardcoded secrets
- [ ] Dependencies updated and audited
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] Logging configured (no sensitive data)
- [ ] Error messages don't leak information
- [ ] File uploads restricted and validated
- [ ] Rate limiting implemented
- [ ] Security tests written

### Regular Audits
- [ ] Dependency vulnerabilities checked
- [ ] Penetration testing performed
- [ ] Security logs reviewed
- [ ] Access controls verified
- [ ] Certificates not expired
- [ ] Backup restoration tested
- [ ] Incident response plan updated

## Incident Response

### Security Incident Procedure
1. **Detect**: Identify potential security issue
2. **Contain**: Isolate affected systems
3. **Assess**: Determine scope and impact
4. **Notify**: Inform stakeholders
5. **Remediate**: Fix vulnerability
6. **Review**: Post-mortem and improvements

### Contact Information
- Security Team: security@example.com
- On-call: +1-xxx-xxx-xxxx
- Escalation: management@example.com
