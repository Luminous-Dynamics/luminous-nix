"""
Knowledge Interface - The Wisdom Repository

This interface defines how we store, retrieve, and share knowledge
about NixOS. It's the foundation of accurate, helpful responses.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.types import IntentType, Package


class KnowledgeInterface(ABC):
    """
    Contract for knowledge storage and retrieval.
    
    Implementations can use databases, files, or even remote
    services, but all must provide accurate NixOS knowledge.
    """
    
    @abstractmethod
    def get_solution(self, intent_type: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Get a solution for a specific intent and query.
        
        Args:
            intent_type: The type of intent (as string)
            query: The original user query
            
        Returns:
            Dictionary containing:
                - solution: The solution text
                - commands: List of commands to execute
                - explanation: Why this solution works
                - alternatives: Other possible approaches
                - examples: Example usage
            Or None if no solution found
        """
        pass
    
    @abstractmethod
    def search_packages(self, query: str, limit: int = 10) -> List[Package]:
        """
        Search for packages matching a query.
        
        Args:
            query: Search term
            limit: Maximum results to return
            
        Returns:
            List of Package objects matching the query
        """
        pass
    
    @abstractmethod
    def get_package_info(self, package_name: str) -> Optional[Package]:
        """
        Get detailed information about a specific package.
        
        Args:
            package_name: The package name or attribute
            
        Returns:
            Package object with full details, or None if not found
        """
        pass
    
    @abstractmethod
    def get_concept_explanation(self, concept: str) -> Optional[str]:
        """
        Get an explanation of a NixOS concept.
        
        Args:
            concept: The concept to explain (e.g., "flakes", "channels")
            
        Returns:
            Human-friendly explanation, or None if not found
        """
        pass
    
    @abstractmethod
    def add_user_solution(self, intent_type: str, query: str, solution: Dict[str, Any]) -> None:
        """
        Add a user-contributed solution to the knowledge base.
        
        This enables learning from successful interactions.
        
        Args:
            intent_type: The type of intent
            query: The query that was solved
            solution: The solution that worked
        """
        pass
    
    @abstractmethod
    def get_common_issues(self, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get common issues and their solutions.
        
        Args:
            context: Optional context to filter issues (e.g., "networking", "packages")
            
        Returns:
            List of issues, each containing:
                - issue: Description of the problem
                - solution: How to fix it
                - frequency: How often this occurs
                - severity: How serious it is
        """
        pass
    
    @abstractmethod
    def update_from_documentation(self, doc_path: str) -> int:
        """
        Update knowledge base from NixOS documentation.
        
        Args:
            doc_path: Path to documentation to process
            
        Returns:
            Number of new knowledge items added
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary containing:
                - total_solutions: Number of solutions stored
                - total_packages: Number of packages known
                - total_concepts: Number of concepts explained
                - last_updated: When the knowledge was last updated
                - coverage: Estimated coverage of NixOS topics
        """
        pass