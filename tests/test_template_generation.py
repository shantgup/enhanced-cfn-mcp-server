"""Tests for CloudFormation template generation."""

import pytest
import json
import yaml
import asyncio
from awslabs.cfn_mcp_server.server_robust import generate_cloudformation_template
from awslabs.cfn_mcp_server.resource_mapping import identify_resources_from_description


def test_identify_resources_from_description():
    """Test identifying resources from a description."""
    # Test with a simple description
    description = "I need an S3 bucket"
    resources = identify_resources_from_description(description)
    assert "Bucket" in resources
    assert resources["Bucket"] == "AWS::S3::Bucket"
    
    # Test with a more complex description
    description = "I need a web application with EC2 instances behind an ALB, and an RDS database"
    resources = identify_resources_from_description(description)
    assert any("LoadBalancer" in key for key, value in resources.items() if value == "AWS::ElasticLoadBalancingV2::LoadBalancer")
    assert any("Instance" in key for key, value in resources.items() if value == "AWS::EC2::Instance")
    assert any("DBInstance" in key for key, value in resources.items() if value == "AWS::RDS::DBInstance")


@pytest.mark.asyncio
async def test_generate_cloudformation_template():
    """Test generating a CloudFormation template."""
    # Test with a simple description
    description = "I need an S3 bucket"
    result = await generate_cloudformation_template(description=description, template_format="JSON")
    
    assert result["success"] is True
    assert "Resources" in result["template"]
    assert any("Bucket" in key for key in result["template"]["Resources"])
    
    # Test with a more complex description
    description = "I need a web application with EC2 instances behind an ALB, and an RDS database"
    result = await generate_cloudformation_template(description=description, template_format="JSON")
    
    assert result["success"] is True
    assert "Resources" in result["template"]
    assert any("LoadBalancer" in key for key in result["template"]["Resources"])
    assert any("Instance" in key for key in result["template"]["Resources"])
    assert any("DB" in key for key in result["template"]["Resources"])


@pytest.mark.asyncio
async def test_generate_cloudformation_template_yaml():
    """Test generating a CloudFormation template in YAML format."""
    description = "I need an S3 bucket"
    result = await generate_cloudformation_template(description=description, template_format="YAML")
    
    assert result["success"] is True
    assert "template_content" in result
    assert "Resources:" in result["template_content"]
    
    # Try to parse the YAML to ensure it's valid
    template = yaml.safe_load(result["template_content"])
    assert "Resources" in template
    assert any("Bucket" in key for key in template["Resources"])


@pytest.mark.asyncio
async def test_generate_cloudformation_template_with_intrinsic_functions():
    """Test generating a CloudFormation template with intrinsic functions."""
    description = "I need an EC2 instance with user data"
    result = await generate_cloudformation_template(description=description, template_format="JSON")
    
    assert result["success"] is True
    assert "Resources" in result["template"]
    
    # Check for intrinsic functions
    template_str = json.dumps(result["template"])
    assert "Fn::Sub" in template_str or "Ref" in template_str or "Fn::GetAtt" in template_str


if __name__ == "__main__":
    asyncio.run(test_generate_cloudformation_template())
    asyncio.run(test_generate_cloudformation_template_yaml())
    asyncio.run(test_generate_cloudformation_template_with_intrinsic_functions())
    test_identify_resources_from_description()