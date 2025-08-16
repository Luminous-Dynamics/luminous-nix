"""
CLI Wrapper for programmatic access to ask-nix.

This allows TUI, Voice, and other interfaces to use ask-nix as the single
source of truth for command execution, preventing wheel reinvention.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional
from dataclasses import dataclass

from .utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CommandResult:
    """Result from executing a command"""
    success: bool
    output: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    executed: bool = False


class AskNixAPI:
    """
    Programmatic interface to ask-nix CLI.
    
    This wrapper ensures all interfaces (TUI, Voice, Web) use the same
    command execution path through ask-nix, maintaining consistency
    and preventing code duplication.
    """
    
    def __init__(self, execute_mode: bool = False):
        """
        Initialize the API wrapper.
        
        Args:
            execute_mode: If True, commands execute for real (not dry-run)
        """
        self.execute_mode = execute_mode
        self.ask_nix_path = self._find_ask_nix()
        
    def _find_ask_nix(self) -> Path:
        """Find the ask-nix executable"""
        # First try relative to this file
        project_root = Path(__file__).parent.parent.parent
        ask_nix = project_root / "bin" / "ask-nix"
        if ask_nix.exists():
            return ask_nix
            
        # Try in PATH
        try:
            result = subprocess.run(
                ['which', 'ask-nix'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
            
        # Default
        return Path("ask-nix")
    
    async def execute(self, command: str, execute: bool = None) -> CommandResult:
        """
        Execute a command through ask-nix CLI.
        
        Args:
            command: Natural language command
            execute: Override default execute mode
            
        Returns:
            CommandResult with output and status
        """
        if execute is None:
            execute = self.execute_mode
            
        # Build command
        cmd = [str(self.ask_nix_path), "--json"]
        if execute:
            cmd.append("--execute")
        cmd.append(command)
        
        logger.debug(f"Executing: {' '.join(cmd)}")
        
        try:
            # Run command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse JSON output
            if stdout:
                try:
                    data = json.loads(stdout.decode())
                    return CommandResult(
                        success=data.get("success", False),
                        output=data.get("output", ""),
                        error=data.get("error"),
                        data=data,
                        executed=data.get("executed", False)
                    )
                except json.JSONDecodeError:
                    # Fallback to text output
                    return CommandResult(
                        success=process.returncode == 0,
                        output=stdout.decode(),
                        error=stderr.decode() if stderr else None,
                        executed=execute
                    )
            else:
                return CommandResult(
                    success=False,
                    output="",
                    error=stderr.decode() if stderr else "No output",
                    executed=False
                )
                
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return CommandResult(
                success=False,
                output="",
                error=str(e),
                executed=False
            )
    
    async def stream_execute(self, command: str, execute: bool = None) -> AsyncIterator[str]:
        """
        Execute a command and stream output line by line.
        
        Useful for long-running operations in TUI/Voice interfaces.
        
        Args:
            command: Natural language command
            execute: Override default execute mode
            
        Yields:
            Output lines as they arrive
        """
        if execute is None:
            execute = self.execute_mode
            
        # Build command (without --json for streaming)
        cmd = [str(self.ask_nix_path)]
        if execute:
            cmd.append("--execute")
        cmd.append(command)
        
        logger.debug(f"Streaming: {' '.join(cmd)}")
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT  # Combine streams
            )
            
            # Stream output
            async for line in process.stdout:
                yield line.decode().rstrip()
                
            await process.wait()
            
        except Exception as e:
            logger.error(f"Stream execution failed: {e}")
            yield f"Error: {e}"
    
    def execute_sync(self, command: str, execute: bool = None) -> CommandResult:
        """
        Synchronous version of execute for non-async contexts.
        
        Args:
            command: Natural language command
            execute: Override default execute mode
            
        Returns:
            CommandResult with output and status
        """
        if execute is None:
            execute = self.execute_mode
            
        # Build command
        cmd = [str(self.ask_nix_path), "--json"]
        if execute:
            cmd.append("--execute")
        cmd.append(command)
        
        logger.debug(f"Executing sync: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Parse JSON output
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    return CommandResult(
                        success=data.get("success", False),
                        output=data.get("output", ""),
                        error=data.get("error"),
                        data=data,
                        executed=data.get("executed", False)
                    )
                except json.JSONDecodeError:
                    # Fallback to text
                    return CommandResult(
                        success=result.returncode == 0,
                        output=result.stdout,
                        error=result.stderr if result.stderr else None,
                        executed=execute
                    )
            else:
                return CommandResult(
                    success=False,
                    output="",
                    error=result.stderr if result.stderr else "No output",
                    executed=False
                )
                
        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            return CommandResult(
                success=False,
                output="",
                error="Command timed out after 30 seconds",
                executed=False
            )
        except Exception as e:
            logger.error(f"Sync execution failed: {e}")
            return CommandResult(
                success=False,
                output="",
                error=str(e),
                executed=False
            )
    
    def test_connection(self) -> bool:
        """Test if ask-nix is available and working"""
        try:
            result = self.execute_sync("help")
            return result.success
        except Exception:
            return False


# Convenience functions for quick access
async def ask_nix(command: str, execute: bool = False) -> CommandResult:
    """Quick function to execute a command through ask-nix"""
    api = AskNixAPI(execute_mode=execute)
    return await api.execute(command)


def ask_nix_sync(command: str, execute: bool = False) -> CommandResult:
    """Quick synchronous function to execute a command"""
    api = AskNixAPI(execute_mode=execute)
    return api.execute_sync(command)


# Example usage for TUI/Voice interfaces
if __name__ == "__main__":
    # Test the wrapper
    async def test():
        api = AskNixAPI()
        
        # Test basic command
        result = await api.execute("help")
        print(f"Success: {result.success}")
        print(f"Output: {result.output[:100]}...")
        
        # Test streaming
        print("\nStreaming output:")
        async for line in api.stream_execute("search firefox"):
            print(f"  > {line}")
            if "firefox" in line.lower():
                break  # Stop after finding firefox
        
        # Test sync version
        sync_result = api.execute_sync("help")
        print(f"\nSync success: {sync_result.success}")
    
    asyncio.run(test())