"""
Executor Interface - Safe Command Execution

This interface defines how we safely execute system commands.
Security, safety, and user control are paramount.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from ..core.types import Command, ExecutionResult, Plan, Intent


class ExecutorInterface(ABC):
    """
    Contract for safe command execution.
    
    All executors must prioritize safety, provide clear feedback,
    and respect user preferences for dry-run vs actual execution.
    """
    
    @abstractmethod
    def execute(self, plan: Plan, intent: Intent, dry_run: bool = True) -> ExecutionResult:
        """
        Execute a plan based on the recognized intent.
        
        Args:
            plan: The execution plan containing steps and commands
            intent: The original intent for context
            dry_run: If True, show what would happen without executing
            
        Returns:
            ExecutionResult: The result of execution (or simulation)
        """
        pass
    
    @abstractmethod
    async def execute_async(self, plan: Plan, intent: Intent, dry_run: bool = True) -> ExecutionResult:
        """
        Asynchronously execute a plan.
        
        This is preferred for long-running operations.
        
        Args:
            plan: The execution plan
            intent: The original intent
            dry_run: If True, simulate only
            
        Returns:
            ExecutionResult: The result of execution
        """
        pass
    
    @abstractmethod
    def validate_command(self, command: Command) -> tuple[bool, Optional[str]]:
        """
        Validate a command for safety before execution.
        
        Args:
            command: The command to validate
            
        Returns:
            Tuple of (is_safe, error_message)
            If is_safe is False, error_message explains why
        """
        pass
    
    @abstractmethod
    def set_sudo_handler(self, handler: Callable[[str], bool]) -> None:
        """
        Set a handler for sudo password requests.
        
        Args:
            handler: Function that takes a prompt and returns True if
                    password was provided successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """
        Set a callback for execution progress updates.
        
        Args:
            callback: Function that takes (message, progress)
                     where progress is 0.0-1.0
        """
        pass
    
    @abstractmethod
    def get_safety_rules(self) -> List[Dict[str, Any]]:
        """
        Get the current safety rules being enforced.
        
        Returns:
            List of safety rules, each containing:
                - name: Rule name
                - description: What the rule prevents
                - pattern: Pattern or condition being checked
                - severity: How serious violations are
        """
        pass
    
    @abstractmethod
    def add_safety_rule(self, rule: Dict[str, Any]) -> None:
        """
        Add a custom safety rule.
        
        Args:
            rule: Dictionary containing:
                - name: Rule name
                - pattern: Regex or condition to check
                - action: What to do when rule matches
                - severity: How serious this is
        """
        pass
    
    @abstractmethod
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent execution history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of execution records, each containing:
                - timestamp: When executed
                - command: What was executed
                - success: Whether it succeeded
                - dry_run: Whether it was a simulation
                - duration: How long it took
        """
        pass
    
    @abstractmethod
    def can_execute_native(self) -> bool:
        """
        Check if native Python-Nix API execution is available.
        
        Returns:
            True if native API is available and configured
        """
        pass