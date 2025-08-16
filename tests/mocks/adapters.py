"""Mock CLI adapter."""

class CLIAdapter:
    def __init__(self, backend=None):
        self.backend = backend
    
    def build_request(self, query, **kwargs):
        return {"query": query, **kwargs}
    
    def process_command(self, command, **kwargs):
        return {"success": True, "output": f"Processed: {command}"}
    
    def format_response(self, response):
        return str(response)
