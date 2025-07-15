"""Integration of CloudFormation documentation knowledge with MCP server tools."""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from awslabs.cfn_mcp_server.documentation_knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)

def enhance_with_knowledge(func: Callable) -> Callable:
    """Decorator to enhance MCP tool responses with documentation knowledge.
    
    This decorator will:
    1. Execute the original function
    2. Analyze the response
    3. Enhance it with relevant documentation knowledge
    4. Return the enhanced response
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Execute original function
        try:
            response = await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in original function: {e}")
            # Re-raise the exception to maintain original behavior
            raise
        
        try:
            # Only enhance successful responses
            if isinstance(response, dict) and response.get("success", False):
                try:
                    # Get knowledge base
                    kb = get_knowledge_base()
                    
                    # Determine the type of response and enhance accordingly
                    if "template_content" in response or "template" in response:
                        # Template generation response
                        enhanced_response = enhance_template_response(response, kb)
                        return enhanced_response
                    elif "resource_type" in response:
                        # Resource-related response
                        enhanced_response = enhance_resource_response(response, kb)
                        return enhanced_response
                    elif "error" in response:
                        # Error response
                        enhanced_response = enhance_error_response(response, kb)
                        return enhanced_response
                except Exception as e:
                    logger.error(f"Error in knowledge enhancement: {e}")
                    # Fall through to return original response
                
            # Return original response if no enhancement applied
            return response
            
        except Exception as e:
            logger.error(f"Error enhancing response with knowledge: {e}")
            # Return original response if enhancement fails
            return response
            
    return wrapper

def enhance_template_response(response: Dict[str, Any], kb) -> Dict[str, Any]:
    """Enhance a template generation response with documentation knowledge.
    
    Args:
        response: Original response from template generation
        kb: Knowledge base instance
        
    Returns:
        Enhanced response
    """
    # Extract template from response
    template = None
    if "template_content" in response and response["format"] == "YAML":
        try:
            template = yaml.safe_load(response["template_content"])
        except Exception as e:
            logger.error(f"Error parsing YAML template: {e}")
    elif "template" in response and response["format"] == "JSON":
        template = response["template"]
    
    if not template:
        return response
    
    # Get template description or use empty string
    description = template.get("Description", "") if isinstance(template, dict) else ""
    
    # Get best practices based on template content
    suggestions = []
    
    # Add best practices for resource types in the template
    if isinstance(template, dict) and "Resources" in template:
        for resource_id, resource in template["Resources"].items():
            if isinstance(resource, dict) and "Type" in resource:
                resource_type = resource["Type"]
                
                # Get best practices for this resource type
                practices = kb.get_best_practices(resource_type)
                for practice in practices:
                    suggestion = {
                        "type": "best_practice",
                        "resource_type": resource_type,
                        "resource_id": resource_id,
                        "suggestion": practice["practice"],
                        "source": "CloudFormation Documentation"
                    }
                    suggestions.append(suggestion)
    
    # Add general template best practices
    general_practices = kb.get_best_practices(topic="template")
    for practice in general_practices:
        suggestion = {
            "type": "best_practice",
            "resource_type": "General",
            "suggestion": practice["practice"],
            "source": "CloudFormation Documentation"
        }
        suggestions.append(suggestion)
    
    # Add documentation references
    doc_results = kb.search_documentation(description, max_results=3)
    for result in doc_results:
        suggestion = {
            "type": "documentation",
            "title": result["title"],
            "snippet": result["snippet"],
            "doc_id": result["doc_id"]
        }
        suggestions.append(suggestion)
    
    # Add suggestions to response
    if "suggestions" in response and isinstance(response["suggestions"], list):
        # Merge with existing suggestions
        response["suggestions"].extend(suggestions)
    else:
        response["suggestions"] = suggestions
    
    # Add documentation knowledge source
    response["knowledge_source"] = "CloudFormation Documentation"
    
    return response

def enhance_resource_response(response: Dict[str, Any], kb) -> Dict[str, Any]:
    """Enhance a resource-related response with documentation knowledge.
    
    Args:
        response: Original response from resource operation
        kb: Knowledge base instance
        
    Returns:
        Enhanced response
    """
    # Extract resource type
    resource_type = response.get("resource_type")
    if not resource_type:
        return response
    
    # Get best practices for this resource type
    practices = kb.get_best_practices(resource_type)
    
    # Add best practices to response
    if practices:
        response["best_practices"] = practices
    
    # Add documentation references
    doc_results = kb.search_documentation(resource_type, max_results=3)
    if doc_results:
        response["documentation_references"] = doc_results
    
    return response

def enhance_error_response(response: Dict[str, Any], kb) -> Dict[str, Any]:
    """Enhance an error response with troubleshooting guidance.
    
    Args:
        response: Original error response
        kb: Knowledge base instance
        
    Returns:
        Enhanced response with troubleshooting guidance
    """
    # Extract error message
    error_message = response.get("error", "")
    if not error_message:
        return response
    
    # Get troubleshooting guidance
    guidance = kb.get_troubleshooting_guidance(error_message)
    
    # Add troubleshooting guidance to response
    if guidance:
        response["troubleshooting_guidance"] = guidance
    
    return response

def get_documentation_for_topic(topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Get documentation for a specific topic.
    
    Args:
        topic: Topic to get documentation for
        max_results: Maximum number of results to return
        
    Returns:
        List of documentation entries
    """
    kb = get_knowledge_base()
    return kb.search_documentation(topic, max_results=max_results)

def get_best_practices_for_resource(resource_type: str) -> List[Dict[str, str]]:
    """Get best practices for a specific resource type.
    
    Args:
        resource_type: Resource type to get best practices for
        
    Returns:
        List of best practices
    """
    kb = get_knowledge_base()
    return kb.get_best_practices(resource_type)

def get_troubleshooting_for_error(error_message: str) -> List[Dict[str, str]]:
    """Get troubleshooting guidance for an error message.
    
    Args:
        error_message: Error message to get guidance for
        
    Returns:
        List of troubleshooting steps
    """
    kb = get_knowledge_base()
    return kb.get_troubleshooting_guidance(error_message)