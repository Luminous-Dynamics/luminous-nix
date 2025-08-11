# Implementation Roadmap: From Current State to Future Vision

## 📍 Where We Are Now

```python
# Current Working Implementation
ask-nix-simple.py → Knowledge Engine → Command Executor → Native Python API
                                                              ↓
                                                        NixOS Operations
```

## 🎯 Where We're Going

```python
# Future Architecture
Any Frontend → Unified API → Headless Core → Native Python API → NixOS
     ↑              ↑             ↑               ↑
  Extensible    Versioned    Plugin-able    10x-1500x faster
```

## 📋 Phase 1: Consolidate Foundation (Week 1)

### Step 1.1: Create Unified Backend Class
```python
# nix_for_humanity/backend.py
class NixForHumanityBackend:
    """Single source of truth for all operations"""

    def __init__(self):
        # Use what we already built
        self.native_api = NixPythonAPI()
        self.knowledge = ModernNixOSKnowledgeEngine()
        self.executor = CommandExecutor()

        # Prepare for future
        self.plugins = PluginRegistry()
        self.hooks = HookSystem()

    async def execute(self, query: str, options: Options = None) -> Result:
        """Single entry point for all operations"""
        # Current implementation
        intent = self.knowledge.extract_intent(query)
        result = self.executor.execute(intent.name, **intent.params)

        # Future hooks
        result = await self.hooks.run("post_execute", result)

        return result
```

### Step 1.2: Create Minimal API Layer
```python
# nix_for_humanity/api/v1.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
backend = NixForHumanityBackend()

class QueryRequest(BaseModel):
    query: str
    dry_run: bool = True
    options: dict = {}

@app.post("/api/v1/execute")
async def execute(request: QueryRequest):
    """RESTful API for any frontend"""
    result = await backend.execute(
        request.query,
        Options(dry_run=request.dry_run, **request.options)
    )
    return {
        "success": result.success,
        "output": result.output,
        "command": result.command
    }
```

### Step 1.3: Refactor CLI to Use Backend
```python
# bin/ask-nix (simplified)
#!/usr/bin/env python3

from nix_for_humanity.backend import NixForHumanityBackend
import asyncio

backend = NixForHumanityBackend()

def main():
    query = " ".join(sys.argv[1:])
    result = asyncio.run(backend.execute(query))
    print(result.output)

if __name__ == "__main__":
    main()
```

## 📋 Phase 2: Enable Extensibility (Week 2)

### Step 2.1: Plugin System
```python
# nix_for_humanity/plugins/base.py
class Plugin(ABC):
    """Base class for all plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def process(self, intent: Intent) -> Optional[Result]:
        """Process intent if this plugin handles it"""
        pass

# nix_for_humanity/plugins/config_generator.py
class ConfigGeneratorPlugin(Plugin):
    name = "config_generator"

    async def process(self, intent: Intent) -> Optional[Result]:
        if intent.name == "generate_config":
            config = self.generate_nix_config(intent.params)
            return Result(success=True, output=config)
        return None
```

### Step 2.2: Hook System
```python
# nix_for_humanity/hooks.py
class HookSystem:
    """Lifecycle hooks for extensibility"""

    def __init__(self):
        self.hooks = defaultdict(list)

    def register(self, event: str, callback: Callable):
        self.hooks[event].append(callback)

    async def run(self, event: str, data: Any) -> Any:
        for callback in self.hooks[event]:
            data = await callback(data)
        return data

# Usage in plugins
def register_hooks(hooks: HookSystem):
    hooks.register("pre_execute", validate_intent)
    hooks.register("post_execute", log_metrics)
```

### Step 2.3: Configuration System
```python
# config.toml
[core]
backend = "native"  # or "subprocess" for fallback
cache_dir = "~/.cache/nix-for-humanity"

[plugins]
enabled = ["config_generator", "error_translator"]

[api]
enabled = true
port = 8080

[features]
learning = true
streaming = false  # Coming in v2
```

## 📋 Phase 3: Advanced Features (Week 3-4)

### Step 3.1: Streaming Operations
```python
# nix_for_humanity/streaming.py
class StreamingExecutor:
    """Real-time progress for long operations"""

    async def execute_streaming(self, intent: Intent):
        """Yield progress updates"""
        async with self.monitor.track() as tracker:
            if intent.name == "rebuild_system":
                async for progress in self.native.rebuild_streaming():
                    yield {
                        "type": "progress",
                        "percent": progress.percent,
                        "message": progress.message
                    }
```

### Step 3.2: Learning System
```python
# nix_for_humanity/learning/engine.py
class LearningEngine:
    """Learn from user interactions"""

    def __init__(self):
        self.db = Database("learning.db")
        self.patterns = PatternMatcher()

    async def learn(self, interaction: Interaction):
        # Record interaction
        await self.db.record(interaction)

        # Extract patterns
        if pattern := self.patterns.match(interaction):
            await self.improve_intent_recognition(pattern)

        # Update user preferences
        await self.update_preferences(interaction.user, interaction)
```

### Step 3.3: Config Generation
```python
# nix_for_humanity/generators/config.py
class NixConfigGenerator:
    """Natural language to Nix configuration"""

    def generate(self, description: str) -> str:
        """
        Example:
        "web server with nginx and postgresql"
        →
        {
          services.nginx.enable = true;
          services.postgresql.enable = true;
        }
        """
        requirements = self.parse_requirements(description)

        config = NixConfig()
        for req in requirements:
            if module := self.module_db.find(req):
                config.add(module)

        return config.render()
```

## 📋 Phase 4: Multiple Frontends (Month 2)

### TUI Frontend
```python
# nix_for_humanity/frontends/tui.py
from textual.app import App
from nix_for_humanity.backend import NixForHumanityBackend

class NixTUI(App):
    def __init__(self):
        super().__init__()
        self.backend = NixForHumanityBackend()

    async def on_command(self, command: str):
        result = await self.backend.execute(command)
        self.display(result)
```

### Voice Frontend
```python
# nix_for_humanity/frontends/voice.py
import speech_recognition as sr
from nix_for_humanity.backend import NixForHumanityBackend

class VoiceInterface:
    def __init__(self):
        self.backend = NixForHumanityBackend()
        self.recognizer = sr.Recognizer()

    async def listen_and_execute(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
            query = self.recognizer.recognize_google(audio)
            result = await self.backend.execute(query)
            self.speak(result.output)
```

## 🚀 Deployment Strategy

### 1. **Nix Flake** (Reproducible)
```nix
{
  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.python3Packages.buildPythonApplication {
      pname = "nix-for-humanity";
      version = "1.0.0";
      src = ./.;

      propagatedBuildInputs = with nixpkgs.legacyPackages.x86_64-linux.python3Packages; [
        click
        rich
        fastapi
        pydantic
      ];
    };
  };
}
```

### 2. **Docker** (Universal)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["python", "-m", "nix_for_humanity.api"]
```

### 3. **Systemd Service** (Production)
```ini
[Unit]
Description=Nix for Humanity API
After=network.target

[Service]
Type=simple
User=nix-humanity
ExecStart=/usr/bin/python -m nix_for_humanity.api
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 Success Metrics

### Phase 1 Success (Week 1)
- [ ] Unified backend class works
- [ ] Basic API endpoint works
- [ ] CLI uses backend
- [ ] All tests pass

### Phase 2 Success (Week 2)
- [ ] Plugin system loads plugins
- [ ] Hooks execute properly
- [ ] Configuration drives behavior
- [ ] Performance maintained

### Phase 3 Success (Week 3-4)
- [ ] Streaming works for long operations
- [ ] Learning improves accuracy
- [ ] Config generation produces valid Nix
- [ ] Error messages are helpful

### Phase 4 Success (Month 2)
- [ ] TUI provides better UX than CLI
- [ ] Voice interface works reliably
- [ ] API handles concurrent requests
- [ ] Deployment is reproducible

## 🎯 The Key Insight

**Start simple, stay extensible, ship continuously**

1. **Today**: Consolidate what works into unified backend
2. **This Week**: Add plugin system for extensibility
3. **This Month**: Add ONE killer feature properly
4. **Next Month**: Multiple frontends share same backend

This approach ensures:
- We ship working software immediately
- We don't break what works
- We can extend without rewriting
- We build on solid foundations

---

*"The best architecture is one that can evolve without revolution"*
