"""
CloudFormation Context Loader

Loads structured troubleshooting context files for specific CloudFormation scenarios.
"""

import json
import os
from pathlib import Path
from typing import Dict, List

class CloudFormationContextLoader:
    """Loads CloudFormation troubleshooting context files"""
    
    def __init__(self):
        """Initialize the context loader"""
        self.context_dir = Path(__file__).parent / "context_files"
        
    def get_context(self, context_name: str) -> Dict:
        """
        Load and return a specific context file
        
        Args:
            context_name: Name of the context file (without .json extension)
            
        Returns:
            Dictionary containing the context data or error information
        """
        file_path = self.context_dir / f"{context_name}.json"
        
        if not file_path.exists():
            return {
                "error": f"Context '{context_name}' not found",
                "available_contexts": self.list_available_contexts(),
                "message": f"The context file '{context_name}.json' does not exist. Use one of the available contexts listed above."
            }
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                
            # Add metadata
            context_data["_metadata"] = {
                "context_name": context_name,
                "file_path": str(file_path),
                "loaded_at": str(Path(__file__).stat().st_mtime)
            }
            
            return context_data
            
        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid JSON in context file '{context_name}'",
                "details": str(e),
                "available_contexts": self.list_available_contexts()
            }
        except Exception as e:
            return {
                "error": f"Error loading context '{context_name}'",
                "details": str(e),
                "available_contexts": self.list_available_contexts()
            }
    
    def list_available_contexts(self) -> List[str]:
        """
        Return list of available context file names
        
        Returns:
            List of context names (without .json extension)
        """
        if not self.context_dir.exists():
            return []
            
        return [f.stem for f in self.context_dir.glob("*.json")]
    
    def get_all_contexts(self) -> Dict[str, Dict]:
        """
        Load all available context files
        
        Returns:
            Dictionary mapping context names to their data
        """
        contexts = {}
        for context_name in self.list_available_contexts():
            contexts[context_name] = self.get_context(context_name)
        return contexts
