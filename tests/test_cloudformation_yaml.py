"""Tests for CloudFormation YAML parsing utilities."""

import pytest
import json
from awslabs.cfn_mcp_server.cloudformation_yaml import (
    parse_cloudformation_template,
    preprocess_cloudformation_yaml,
    postprocess_cloudformation_dict,
    coerce_template_content
)


def test_parse_cloudformation_template_json():
    """Test parsing a CloudFormation template in JSON format."""
    template_content = json.dumps({
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {
            "MyBucket": {
                "Type": "AWS::S3::Bucket"
            }
        }
    })
    
    result = parse_cloudformation_template(template_content)
    
    assert result["AWSTemplateFormatVersion"] == "2010-09-09"
    assert "MyBucket" in result["Resources"]
    assert result["Resources"]["MyBucket"]["Type"] == "AWS::S3::Bucket"


def test_parse_cloudformation_template_yaml():
    """Test parsing a CloudFormation template in YAML format."""
    template_content = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
"""
    
    result = parse_cloudformation_template(template_content)
    
    assert result["AWSTemplateFormatVersion"] == "2010-09-09"
    assert "MyBucket" in result["Resources"]
    assert result["Resources"]["MyBucket"]["Type"] == "AWS::S3::Bucket"


def test_parse_cloudformation_template_with_intrinsic_functions():
    """Test parsing a CloudFormation template with intrinsic functions."""
    template_content = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-bucket'
  MyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: !Ref 'AWS::Region'
            Action: 'sts:AssumeRole'
"""
    
    # This should not raise an exception
    result = parse_cloudformation_template(template_content)
    
    assert result["AWSTemplateFormatVersion"] == "2010-09-09"
    assert "MyBucket" in result["Resources"]
    assert "MyRole" in result["Resources"]


def test_coerce_template_content():
    """Test coercing template content to string."""
    # Test with dictionary
    template_dict = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {
            "MyBucket": {
                "Type": "AWS::S3::Bucket"
            }
        }
    }
    
    result = coerce_template_content(template_dict)
    
    assert isinstance(result, str)
    assert json.loads(result) == template_dict
    
    # Test with string
    template_str = "AWSTemplateFormatVersion: '2010-09-09'"
    
    result = coerce_template_content(template_str)
    
    assert result == template_str
    
    # Test with None
    with pytest.raises(ValueError):
        coerce_template_content(None)