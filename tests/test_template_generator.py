"""Tests for the TemplateGenerator module."""

import pytest
import json
import yaml
from unittest.mock import Mock, patch
from awslabs.cfn_mcp_server.template_generator_clean import TemplateGenerator


class TestTemplateGenerator:
    """Test cases for TemplateGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create a TemplateGenerator instance for testing."""
        with patch('awslabs.cfn_mcp_server.template_generator.get_aws_client'):
            return TemplateGenerator('us-east-1')
    
    @pytest.mark.asyncio
    async def test_generate_simple_s3_template(self, generator):
        """Test generating a simple S3 bucket template."""
        description = "Create an S3 bucket for storing files"
        
        result = await generator.generate_from_description(
            description=description,
            template_format='YAML'
        )
        
        assert result['success'] is True
        assert 'template' in result
        assert 'S3Bucket' in result['template']['Resources']
        assert result['template']['Resources']['S3Bucket']['Type'] == 'AWS::S3::Bucket'
        assert result['format'] == 'YAML'
        assert 'template_content' in result
    
    @pytest.mark.asyncio
    async def test_generate_lambda_template(self, generator):
        """Test generating a Lambda function template."""
        description = "Create a Lambda function to process data"
        
        result = await generator.generate_from_description(
            description=description,
            template_format='JSON'
        )
        
        assert result['success'] is True
        template = result['template']
        
        # Should have Lambda function and IAM role
        assert 'LambdaFunction' in template['Resources']
        assert 'LambdaExecutionRole' in template['Resources']
        assert template['Resources']['LambdaFunction']['Type'] == 'AWS::Lambda::Function'
        assert template['Resources']['LambdaExecutionRole']['Type'] == 'AWS::IAM::Role'
    
    @pytest.mark.asyncio
    async def test_generate_multi_resource_template(self, generator):
        """Test generating a template with multiple resources."""
        description = "Create a web application with Lambda, API Gateway, and DynamoDB"
        
        result = await generator.generate_from_description(
            description=description,
            template_format='YAML'
        )
        
        assert result['success'] is True
        resources = result['template']['Resources']
        
        # Should identify multiple resource types
        resource_types = [res['Type'] for res in resources.values()]
        assert 'AWS::Lambda::Function' in resource_types
        assert 'AWS::ApiGateway::RestApi' in resource_types
        assert 'AWS::DynamoDB::Table' in resource_types
    
    def test_analyze_description(self, generator):
        """Test description analysis for resource identification."""
        description = "Create an RDS database and S3 bucket"
        
        resources = generator._analyze_description(description)
        
        # Filter out non-resource entries (like Parameters)
        resource_types = [res['Type'] for res in resources.values() if 'Type' in res]
        assert 'AWS::RDS::DBInstance' in resource_types
        assert 'AWS::S3::Bucket' in resource_types
    
    def test_generate_resource_name(self, generator):
        """Test resource name generation."""
        name = generator._generate_resource_name('AWS::S3::Bucket')
        assert name == 'S3Bucket'
        
        name = generator._generate_resource_name('AWS::Lambda::Function')
        assert name == 'LambdaFunction'
    
    def test_get_default_properties(self, generator):
        """Test default properties generation."""
        props = generator._get_default_properties('AWS::S3::Bucket', 'storage bucket')
        
        assert 'BucketName' in props
        assert 'VersioningConfiguration' in props
        assert 'BucketEncryption' in props
    
    @pytest.mark.asyncio
    async def test_save_to_file(self, generator, tmp_path):
        """Test saving template to file."""
        description = "Create an S3 bucket"
        file_path = tmp_path / "test_template.yaml"
        
        result = await generator.generate_from_description(
            description=description,
            template_format='YAML',
            save_to_file=str(file_path)
        )
        
        assert result['success'] is True
        assert result['file_saved'] == str(file_path)
        assert file_path.exists()
        
        # Verify file content is valid YAML
        with open(file_path, 'r') as f:
            template = yaml.safe_load(f)
        
        assert 'AWSTemplateFormatVersion' in template
        assert 'Resources' in template
