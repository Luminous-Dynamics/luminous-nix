"""JSON-RPC server module."""

class JSONRPCServer:
    """JSON-RPC server."""
    
    def __init__(self):
        pass
    
    def start(self):
        pass

class JSONRPCClient:
    """JSON-RPC client."""
    
    def __init__(self, socket_path=None, tcp_port=None):
        self.socket_path = socket_path
        self.tcp_port = tcp_port
    
    def call(self, method: str, params: dict = None):
        return {}
