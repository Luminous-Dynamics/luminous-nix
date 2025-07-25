# NixOS GUI - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   User Browser                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │   React/    │  │   Service    │  │   Cache      │  │   Help System     │   │
│  │   Vanilla   │  │   Worker     │  │   Layer      │  │   & Tours         │   │
│  │   JS App    │  │   (PWA)      │  │ (LocalStore) │  │                   │   │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘   │
│         │                 │                  │                    │              │
│         └─────────────────┴──────────────────┴────────────────────┘              │
│                                      │                                           │
│                                      ▼                                           │
│                           ┌───────────────────┐                                 │
│                           │   HTTP/WebSocket  │                                 │
│                           │     (HTTPS)       │                                 │
│                           └─────────┬─────────┘                                 │
└─────────────────────────────────────┼───────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 ▼                 │
┌───────────────────┴───────────────────────────────────┴────────────────────────┐
│                              NixOS GUI Server                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           Express.js Web Server                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │   │
│  │  │   Auth     │  │   Rate     │  │   CORS     │  │   Compression  │   │   │
│  │  │ Middleware │  │  Limiter   │  │  Handler   │  │   & Security   │   │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                              API Routes                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │   │
│  │  │  Package   │  │   Config   │  │  Service   │  │  Generation    │   │   │
│  │  │    API     │  │    API     │  │    API     │  │      API       │   │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───────┬────────┘   │   │
│  │        │               │               │                   │            │   │
│  │        └───────────────┴───────────────┴───────────────────┘            │   │
│  │                                │                                         │   │
│  └────────────────────────────────┼─────────────────────────────────────────┘   │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           Service Layer                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐   │   │
│  │  │  Package   │  │   Config   │  │  Service   │  │   Generation   │   │   │
│  │  │  Service   │  │  Service   │  │  Manager   │  │    Manager     │   │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───────┬────────┘   │   │
│  │        │               │               │                   │            │   │
│  └────────┼───────────────┼───────────────┼───────────────────┼────────────┘   │
│           │               │               │                   │                 │
│  ┌────────▼───────────────▼───────────────▼───────────────────▼────────────┐   │
│  │                         Data Access Layer                               │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐                  │   │
│  │  │   SQLite    │  │    Cache     │  │    Audit     │                  │   │
│  │  │  Database   │  │   Manager    │  │    Logger    │                  │   │
│  │  │             │  │  (L1/L2/L3)  │  │              │                  │   │
│  │  └─────────────┘  └──────┬───────┘  └──────────────┘                  │   │
│  │                           │                                             │   │
│  │                    ┌──────┴────────┐                                   │   │
│  │                    │ Redis Cache   │ (Optional)                        │   │
│  │                    │  (Cluster)    │                                   │   │
│  │                    └───────────────┘                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │
                 ┌─────────────────────┼─────────────────────┐
                 │                     ▼                     │
┌────────────────┴────────────────────────────────────────────┴───────────────────┐
│                            System Integration                                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │     PAM      │  │    Polkit    │  │   SystemD    │  │      Nix         │    │
│  │Authentication│  │ Privileged   │  │   Service    │  │     Daemon       │    │
│  │              │  │  Helper      │  │  Manager     │  │                  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘    │
│         │                  │                  │                   │               │
│  ┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐  ┌────────▼───────────┐   │
│  │   System    │  │   Elevated   │  │   Service    │  │    Package       │   │
│  │   Users     │  │ Operations   │  │   Control    │  │   Management     │   │
│  └─────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘    │
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                         NixOS Configuration Files                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │configuration │  │  hardware-   │  │    System    │                 │    │
│  │  │    .nix     │  │configuration │  │  Generations │                 │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘

## Component Descriptions

### Frontend Layer
- **Web App**: Single-page application with vanilla JS/Web Components
- **Service Worker**: Offline support and caching
- **Local Cache**: Browser-based storage for performance
- **Help System**: Interactive tours and contextual help

### Backend Layer  
- **Web Server**: Express.js with security middleware
- **API Routes**: RESTful endpoints for all operations
- **Service Layer**: Business logic and orchestration
- **Data Layer**: SQLite persistence with multi-tier caching

### System Integration
- **PAM**: Linux authentication integration
- **Polkit**: Secure privilege escalation
- **SystemD**: Service management
- **Nix Daemon**: Package operations

### Data Flow
1. User interacts with web interface
2. Request passes through security middleware
3. API route handles request
4. Service layer orchestrates operations
5. System integration performs privileged operations
6. Response flows back through cache layers
7. UI updates with real-time WebSocket events

### Security Boundaries
- 🔒 HTTPS encryption (production)
- 🔒 JWT authentication tokens
- 🔒 Polkit authorization
- 🔒 Input validation at all layers
- 🔒 Audit logging throughout
```