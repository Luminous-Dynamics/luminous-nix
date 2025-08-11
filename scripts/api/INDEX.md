# Api

**A RESTful API service exposing the intelligent headless core**

## 📚 Contents


### 📁 Subdirectories

- [__pycache__/](__pycache__/) - 0 documents
- [examples/](examples/) - 0 documents

---

## Original Documentation


*A RESTful API service exposing the intelligent headless core*

## Quick Start

### 1. Install Dependencies

```bash
# Using pip
pip install flask flask-cors flask-limiter

# Or using Nix
nix-shell -p python3 python3Packages.flask python3Packages.flask-cors
```

### 2. Start the Server

```bash
# From project root
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
python scripts/api/nix_api_server.py

# Or with custom settings
API_PORT=8080 API_DEBUG=true python scripts/api/nix_api_server.py
```

### 3. Test the API

```bash
# Check if running
curl http://localhost:5000/api/v1/health

# Run all examples
bash scripts/api/examples/curl_examples.sh
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check and version info |
| POST | `/api/v1/query` | Process natural language query |
| POST | `/api/v1/feedback` | Submit user feedback |
| GET | `/api/v1/search` | Search NixOS packages |
| GET | `/api/v1/stats` | Get engine statistics |
| GET | `/api/v1/capabilities` | List API capabilities |
| GET | `/api/v1/session/{id}` | Get session details |

### WebSocket Events (Optional)

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client→Server | Establish connection |
| `query` | Client→Server | Send query |
| `response` | Server→Client | Query response |
| `error` | Server→Client | Error message |

## Request/Response Examples

### Query Request

```json
{
  "query": "How do I install Firefox?",
  "session_id": "optional-session-id",
  "context": {
    "personality": "friendly",
    "execution_mode": "dry_run",
    "collect_feedback": true,
    "capabilities": ["text", "visual"]
  }
}
```

### Query Response

```json
{
  "status": "success",
  "session_id": "abc123",
  "response": {
    "text": "I'll help you install Firefox! Here are your options...",
    "intent": {
      "action": "install_package",
      "package": "firefox",
      "confidence": 0.9
    },
    "commands": [
      "nix-env -iA nixos.firefox",
      "nix-shell -p firefox"
    ],
    "visual": {
      "type": "options",
      "choices": [...]
    },
    "feedback_request": {
      "type": "simple",
      "prompt": "Was this helpful?"
    }
  },
  "timestamp": "2025-01-29T12:00:00Z"
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Bind address |
| `API_PORT` | `5000` | Port number |
| `API_DEBUG` | `false` | Enable debug mode |
| `API_CERT` | - | SSL certificate path |
| `API_KEY` | - | SSL key path |

### Rate Limits

- Query endpoint: 30/minute
- Search endpoint: 20/minute
- Feedback endpoint: 10/minute
- Default: 200/day, 50/hour

## Client Libraries

### JavaScript/TypeScript

```javascript
import NixForHumanityClient from './examples/javascript_client.js';

const client = new NixForHumanityClient();
const response = await client.query('Install Firefox');
console.log(response);
```

### Python

```python
from examples.python_client import NixForHumanityClient

with NixForHumanityClient() as client:
    response = client.query("Install Firefox")
    print(response['response']['text'])
```

## Deployment

### Using systemd

```bash
# Copy service file
sudo cp scripts/api/nix-for-humanity-api.service /etc/systemd/system/

# Create API user
sudo useradd -r -s /bin/false nix-api

# Start service
sudo systemctl enable --now nix-for-humanity-api
```

### Using Docker

```bash
# Build image
docker build -t nix-api -f scripts/api/Dockerfile .

# Run container
docker run -p 5000:5000 nix-api
```

### Using Nix

```nix
# In your configuration.nix
systemd.services.nix-api = {
  description = "Nix for Humanity API";
  wantedBy = [ "multi-user.target" ];
  after = [ "network.target" ];

  serviceConfig = {
    ExecStart = "${pkgs.python3}/bin/python /srv/nix-for-humanity/scripts/api/nix_api_server.py";
    Restart = "always";
    User = "nix-api";
    Group = "nix-api";
  };
};
```

## Security

### Production Checklist

- [ ] Enable HTTPS with valid certificates
- [ ] Configure CORS for your domains only
- [ ] Implement API key authentication
- [ ] Set up reverse proxy (nginx/caddy)
- [ ] Configure firewall rules
- [ ] Enable request logging
- [ ] Set up monitoring/alerting
- [ ] Regular security updates

### Example nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.nixforhumanity.org;

    ssl_certificate /etc/letsencrypt/live/api.nixforhumanity.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.nixforhumanity.org/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Monitoring

### Health Checks

```bash
# Simple health check
curl -f http://localhost:5000/api/v1/health || exit 1

# Detailed monitoring
watch -n 5 'curl -s http://localhost:5000/api/v1/stats | jq .'
```

### Logging

```bash
# View logs
journalctl -u nix-for-humanity-api -f

# Export logs
journalctl -u nix-for-humanity-api --since today > api.log
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   lsof -i :5000
   # Change port with API_PORT=5001
   ```

2. **Module not found**
   ```bash
   export PYTHONPATH=/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts
   ```

3. **Permission denied**
   ```bash
   # Check file permissions
   ls -la scripts/api/
   chmod +x scripts/api/nix_api_server.py
   ```

4. **Rate limit exceeded**
   - Implement caching on client side
   - Request rate limit increase
   - Use batch endpoints

## Development

### Running Tests

```bash
# Unit tests
python -m pytest tests/api/

# Integration tests
python scripts/api/test_integration.py
```

### Adding New Endpoints

1. Add route to `nix_api_server.py`
2. Update client libraries
3. Add tests
4. Update documentation
5. Bump version

## API Versioning

Current version: `v1`

All endpoints are prefixed with `/api/v1/`. Future versions will use `/api/v2/` etc.

## Support

- GitHub Issues: [Report bugs](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
- Documentation: [Integration Guide](../../docs/ACTIVE/development/HEADLESS_INTEGRATION_GUIDE.md)
- Examples: See `examples/` directory

---

*Making NixOS accessible through standard web APIs!*
