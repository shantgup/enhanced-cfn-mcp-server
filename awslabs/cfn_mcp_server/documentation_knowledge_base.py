"""CloudFormation Documentation Knowledge Base.

This module provides access to CloudFormation documentation from the API reference,
user guide, and knowledge center articles to enhance MCP server responses.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from functools import lru_cache

# Optional imports
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)

class DocumentationKnowledgeBase:
    """Knowledge base for CloudFormation documentation."""
    
    def __init__(self, docs_path: str = None):
        """Initialize the knowledge base.
        
        Args:
            docs_path: Path to the documentation files. If None, uses default path.
        """
        self.docs_path = docs_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_docs")
        self.api_docs_path = os.path.join(self.docs_path, "api")
        self.user_guide_path = os.path.join(self.docs_path, "user_guide")
        self.knowledge_center_path = os.path.join(self.docs_path, "knowledge_center")
        
        # Document index
        self.document_index = {}
        self.document_content = {}
        self.document_embeddings = {}
        
        # Load document index
        self._load_document_index()
        
    def _load_document_index(self):
        """Load the document index from the documentation files."""
        logger.info(f"Loading CloudFormation documentation from {self.docs_path}")
        
        # Check if docs path exists
        if not os.path.exists(self.docs_path):
            logger.warning(f"Documentation path {self.docs_path} does not exist")
            return
            
        # Load API docs
        self._load_docs_from_directory(self.api_docs_path, "api")
        
        # Load user guide
        self._load_docs_from_directory(self.user_guide_path, "user_guide")
        
        # Load knowledge center
        self._load_docs_from_directory(self.knowledge_center_path, "knowledge_center")
        
        logger.info(f"Loaded {len(self.document_index)} documentation files")
        
    def _load_docs_from_directory(self, directory: str, doc_type: str):
        """Load documentation from a directory.
        
        Args:
            directory: Directory containing documentation files
            doc_type: Type of documentation (api, user_guide, knowledge_center)
        """
        if not os.path.exists(directory):
            logger.warning(f"Documentation directory {directory} does not exist")
            return
            
        for filename in os.listdir(directory):
            if filename.endswith(".html"):
                file_path = os.path.join(directory, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Parse HTML content if BeautifulSoup is available
                    if BEAUTIFULSOUP_AVAILABLE:
                        soup = BeautifulSoup(content, "html.parser")
                        
                        # Extract title
                        title = soup.title.string if soup.title else filename
                        
                        # Extract main content
                        main_content = ""
                        if soup.body:
                            # Remove script and style elements
                            for script in soup.find_all(["script", "style"]):
                                script.extract()
                            
                            # Get text content
                            main_content = soup.body.get_text(separator=" ", strip=True)
                    else:
                        # Fallback: use raw content and extract title from HTML tags
                        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                        title = title_match.group(1) if title_match else filename
                        
                        # Simple HTML tag removal
                        main_content = re.sub(r'<[^>]+>', ' ', content)
                        main_content = re.sub(r'\s+', ' ', main_content).strip()
                    
                    # Create document entry
                    doc_id = f"{doc_type}/{filename}"
                    self.document_index[doc_id] = {
                        "title": title,
                        "type": doc_type,
                        "filename": filename,
                        "path": file_path
                    }
                    
                    # Store content
                    self.document_content[doc_id] = main_content
                    
                except Exception as e:
                    logger.error(f"Error loading documentation file {file_path}: {e}")
    
    @lru_cache(maxsize=100)
    def search_documentation(self, query: str, doc_type: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search documentation for relevant content.
        
        Args:
            query: Search query
            doc_type: Optional type of documentation to search (api, user_guide, knowledge_center)
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant documentation entries
        """
        results = []
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b\w+\b', query_lower))
        
        # Filter by doc_type if specified
        docs_to_search = {
            doc_id: doc for doc_id, doc in self.document_index.items()
            if not doc_type or doc["type"] == doc_type
        }
        
        # Score documents based on term matches
        scored_docs = []
        for doc_id, doc in docs_to_search.items():
            content = self.document_content.get(doc_id, "").lower()
            title = doc["title"].lower()
            
            # Calculate score based on term matches
            score = 0
            for term in query_terms:
                # Title matches are weighted higher
                if term in title:
                    score += 10
                
                # Content matches
                term_count = content.count(term)
                score += min(term_count, 5)  # Cap to avoid overly long documents dominating
            
            if score > 0:
                scored_docs.append((doc_id, score))
        
        # Sort by score and take top results
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_docs = scored_docs[:max_results]
        
        # Prepare results
        for doc_id, score in top_docs:
            doc = self.document_index[doc_id]
            content = self.document_content[doc_id]
            
            # Extract a relevant snippet
            snippet = self._extract_relevant_snippet(content, query_terms)
            
            results.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "type": doc["type"],
                "score": score,
                "snippet": snippet
            })
        
        return results
    
    def _extract_relevant_snippet(self, content: str, query_terms: Set[str], max_length: int = 300) -> str:
        """Extract a relevant snippet from content based on query terms.
        
        Args:
            content: Document content
            query_terms: Set of query terms
            max_length: Maximum snippet length
            
        Returns:
            Relevant snippet from content
        """
        # Find the best paragraph containing query terms
        paragraphs = content.split("\n\n")
        best_paragraph = None
        best_score = -1
        
        for paragraph in paragraphs:
            if len(paragraph.strip()) < 20:  # Skip very short paragraphs
                continue
                
            paragraph_lower = paragraph.lower()
            score = sum(paragraph_lower.count(term) for term in query_terms)
            
            if score > best_score:
                best_score = score
                best_paragraph = paragraph
        
        if not best_paragraph:
            # If no good paragraph found, return the beginning of the content
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # Truncate if necessary
        if len(best_paragraph) > max_length:
            return best_paragraph[:max_length] + "..."
        
        return best_paragraph
    
    def get_document_content(self, doc_id: str) -> Optional[str]:
        """Get the full content of a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document content or None if not found
        """
        return self.document_content.get(doc_id)
    
    def get_best_practices(self, resource_type: Optional[str] = None, topic: Optional[str] = None) -> List[Dict[str, str]]:
        """Get best practices for CloudFormation.
        
        Args:
            resource_type: Optional resource type to get best practices for
            topic: Optional topic to get best practices for
            
        Returns:
            List of best practices
        """
        query = "best practices"
        if resource_type:
            query += f" {resource_type}"
        if topic:
            query += f" {topic}"
            
        results = self.search_documentation(query, doc_type="user_guide", max_results=3)
        
        best_practices = []
        for result in results:
            doc_id = result["doc_id"]
            content = self.get_document_content(doc_id)
            
            if content:
                # Extract best practices from content
                practices = self._extract_best_practices(content, resource_type)
                best_practices.extend(practices)
        
        return best_practices[:10]  # Limit to top 10 best practices
    
    def _extract_best_practices(self, content: str, resource_type: Optional[str] = None) -> List[Dict[str, str]]:
        """Extract best practices from content.
        
        Args:
            content: Document content
            resource_type: Optional resource type to filter best practices
            
        Returns:
            List of best practices
        """
        practices = []
        
        # Look for sections that might contain best practices
        sections = re.split(r'\n\s*#+\s+', content)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if section is relevant
            is_relevant = (
                "best practice" in section.lower() or
                "recommend" in section.lower() or
                "guideline" in section.lower() or
                "tip" in section.lower()
            )
            
            if resource_type:
                is_relevant = is_relevant and resource_type.lower() in section.lower()
            
            if is_relevant:
                # Extract bullet points or numbered lists
                bullet_points = re.findall(r'(?:^|\n)(?:\*|\-|\d+\.)\s+(.+?)(?=\n|$)', section)
                
                for point in bullet_points:
                    if len(point) > 20:  # Skip very short points
                        practices.append({
                            "practice": point.strip(),
                            "source": "CloudFormation Documentation"
                        })
        
        return practices
    
    def get_troubleshooting_guidance(self, error_message: str) -> List[Dict[str, str]]:
        """Get troubleshooting guidance for an error message.
        
        Args:
            error_message: Error message to get guidance for
            
        Returns:
            List of troubleshooting steps
        """
        # Extract key terms from error message
        error_terms = set(re.findall(r'\b\w+\b', error_message.lower()))
        error_terms = {term for term in error_terms if len(term) > 3}  # Filter out short terms
        
        # Add common troubleshooting terms
        search_terms = error_terms.union({"error", "troubleshoot", "fix", "resolve", "issue"})
        
        # Construct search query
        query = " ".join(search_terms)
        
        # Search documentation
        results = self.search_documentation(query, max_results=5)
        
        guidance = []
        for result in results:
            doc_id = result["doc_id"]
            content = self.get_document_content(doc_id)
            
            if content:
                # Extract troubleshooting steps
                steps = self._extract_troubleshooting_steps(content, error_terms)
                
                for step in steps:
                    guidance.append({
                        "step": step,
                        "source": result["title"],
                        "doc_id": doc_id
                    })
        
        return guidance[:7]  # Limit to top 7 troubleshooting steps
    
    def _extract_troubleshooting_steps(self, content: str, error_terms: Set[str]) -> List[str]:
        """Extract troubleshooting steps from content.
        
        Args:
            content: Document content
            error_terms: Terms from the error message
            
        Returns:
            List of troubleshooting steps
        """
        steps = []
        
        # Look for sections that might contain troubleshooting steps
        sections = re.split(r'\n\s*#+\s+', content)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if section is relevant
            is_relevant = (
                "troubleshoot" in section.lower() or
                "error" in section.lower() or
                "issue" in section.lower() or
                "problem" in section.lower() or
                "fix" in section.lower() or
                "resolve" in section.lower() or
                any(term in section.lower() for term in error_terms)
            )
            
            if is_relevant:
                # Extract bullet points or numbered lists
                bullet_points = re.findall(r'(?:^|\n)(?:\*|\-|\d+\.)\s+(.+?)(?=\n|$)', section)
                
                for point in bullet_points:
                    if len(point) > 20:  # Skip very short points
                        steps.append(point.strip())
                
                # If no bullet points found, extract paragraphs
                if not bullet_points:
                    paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
                    for paragraph in paragraphs:
                        if len(paragraph) > 50 and len(paragraph) < 500:  # Reasonable paragraph size
                            steps.append(paragraph)
        
        return steps
    
    def enhance_template_with_best_practices(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a CloudFormation template with best practices.
        
        Args:
            template: CloudFormation template
            
        Returns:
            Enhanced template and list of suggestions
        """
        suggestions = []
        
        # Identify resource types in the template
        resource_types = set()
        if "Resources" in template:
            for resource_id, resource in template["Resources"].items():
                if "Type" in resource:
                    resource_types.add(resource["Type"])
        
        # Get best practices for each resource type
        for resource_type in resource_types:
            practices = self.get_best_practices(resource_type)
            for practice in practices:
                suggestions.append({
                    "resource_type": resource_type,
                    "suggestion": practice["practice"],
                    "source": practice["source"]
                })
        
        # Get general best practices
        general_practices = self.get_best_practices(topic="template")
        for practice in general_practices:
            suggestions.append({
                "resource_type": "General",
                "suggestion": practice["practice"],
                "source": practice["source"]
            })
        
        return suggestions
    
    def get_documentation_references(self, resource_type: str) -> List[Dict[str, Any]]:
        """Get documentation references for a specific resource type.
        
        Args:
            resource_type: AWS resource type (e.g., AWS::S3::Bucket)
            
        Returns:
            List of documentation references
        """
        # Search for documentation related to the resource type
        results = self.search_documentation(resource_type, max_results=3)
        
        # Format results as documentation references
        references = []
        for result in results:
            references.append({
                "doc_id": result["doc_id"],
                "title": result["title"],
                "type": result["type"],
                "score": result["score"],
                "snippet": result["snippet"]
            })
        
        return references
    
    def get_resource_documentation(self, resource_type: str) -> Dict[str, Any]:
        """Get comprehensive documentation for a specific resource type.
        
        Args:
            resource_type: AWS resource type (e.g., AWS::S3::Bucket)
            
        Returns:
            Dictionary containing documentation information
        """
        # Search for documentation related to the resource type
        results = self.search_documentation(resource_type, max_results=5)
        
        # Get best practices for the resource type
        best_practices = self.get_best_practices(resource_type)
        
        # Compile comprehensive documentation
        documentation = {
            "resource_type": resource_type,
            "documentation_references": results,
            "best_practices": best_practices,
            "troubleshooting": self.get_troubleshooting_guidance(f"{resource_type} error"),
            "source": "CloudFormation Documentation Knowledge Base"
        }
        
        return documentation
    
    def get_best_practices_by_category(self, category: str) -> List[Dict[str, str]]:
        """Get best practices by category.
        
        Args:
            category: Category of best practices (e.g., security, performance, cost)
            
        Returns:
            List of best practices for the category
        """
        return self.get_best_practices(topic=category)
    
    def get_all_best_practices(self) -> List[Dict[str, str]]:
        """Get all available best practices.
        
        Returns:
            List of all best practices
        """
        return self.get_best_practices()
    
    def get_common_troubleshooting_scenarios(self) -> List[Dict[str, str]]:
        """Get common troubleshooting scenarios.
        
        Returns:
            List of common troubleshooting scenarios
        """
        common_errors = [
            "stack rollback",
            "resource creation failed",
            "permission denied",
            "resource limit exceeded",
            "dependency error",
            "timeout error"
        ]
        
        all_guidance = []
        for error in common_errors:
            guidance = self.get_troubleshooting_guidance(error)
            all_guidance.extend(guidance)
        
        # Remove duplicates and limit results
        seen = set()
        unique_guidance = []
        for item in all_guidance:
            if item["step"] not in seen:
                seen.add(item["step"])
                unique_guidance.append(item)
        
        return unique_guidance[:15]  # Limit to top 15 scenarios

# Singleton instance
_knowledge_base = None

def get_knowledge_base() -> DocumentationKnowledgeBase:
    """Get the singleton knowledge base instance."""
    global _knowledge_base
    try:
        if _knowledge_base is None:
            _knowledge_base = DocumentationKnowledgeBase()
        return _knowledge_base
    except Exception as e:
        logger.error(f"Error creating knowledge base: {e}")
        # Return a minimal knowledge base that won't crash the server
        return DocumentationKnowledgeBase(docs_path="/tmp")