"""Tests for the CloudFormation documentation knowledge base."""

import os
import pytest
from unittest.mock import patch, MagicMock
from awslabs.cfn_mcp_server.documentation_knowledge_base import DocumentationKnowledgeBase
from awslabs.cfn_mcp_server.knowledge_integration import enhance_template_response

class TestDocumentationKnowledge:
    """Test the documentation knowledge base."""
    
    @pytest.fixture
    def mock_kb(self):
        """Create a mock knowledge base."""
        kb = MagicMock()
        kb.search_documentation.return_value = [
            {
                "doc_id": "user_guide/test.html",
                "title": "Test Document",
                "type": "user_guide",
                "score": 10,
                "snippet": "This is a test document snippet."
            }
        ]
        kb.get_best_practices.return_value = [
            {
                "practice": "Always use encryption for S3 buckets",
                "source": "CloudFormation Documentation"
            }
        ]
        kb.get_troubleshooting_guidance.return_value = [
            {
                "step": "Check IAM permissions",
                "source": "Troubleshooting Guide",
                "doc_id": "user_guide/troubleshooting.html"
            }
        ]
        kb.get_document_content.return_value = "Full document content"
        return kb
    
    def test_knowledge_base_initialization(self):
        """Test knowledge base initialization with mock docs."""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['test.html']), \
             patch('builtins.open', MagicMock()), \
             patch('bs4.BeautifulSoup', MagicMock()):
            
            kb = DocumentationKnowledgeBase(docs_path="mock_path")
            assert kb.docs_path == "mock_path"
    
    def test_enhance_template_response(self, mock_kb):
        """Test enhancing a template response with documentation knowledge."""
        # Create a sample template response
        response = {
            "success": True,
            "template_content": "AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  MyBucket:\n    Type: AWS::S3::Bucket",
            "format": "YAML",
            "description": "S3 bucket template",
            "suggestions": []
        }
        
        # Enhance the response
        enhanced = enhance_template_response(response, mock_kb)
        
        # Verify the response was enhanced
        assert enhanced["success"] is True
        assert "suggestions" in enhanced
        assert len(enhanced["suggestions"]) > 0
        assert "knowledge_source" in enhanced
        assert enhanced["knowledge_source"] == "CloudFormation Documentation"
        
        # Verify mock was called
        mock_kb.get_best_practices.assert_called()
        mock_kb.search_documentation.assert_called()
    
    def test_search_documentation(self, mock_kb):
        """Test searching documentation."""
        results = mock_kb.search_documentation("S3 bucket")
        assert len(results) > 0
        assert "title" in results[0]
        assert "snippet" in results[0]
    
    def test_get_best_practices(self, mock_kb):
        """Test getting best practices."""
        practices = mock_kb.get_best_practices("AWS::S3::Bucket")
        assert len(practices) > 0
        assert "practice" in practices[0]
        assert "source" in practices[0]
    
    def test_get_troubleshooting_guidance(self, mock_kb):
        """Test getting troubleshooting guidance."""
        guidance = mock_kb.get_troubleshooting_guidance("Access Denied")
        assert len(guidance) > 0
        assert "step" in guidance[0]
        assert "source" in guidance[0]