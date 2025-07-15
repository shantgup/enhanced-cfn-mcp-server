"""Tests for CloudFormation template capabilities detection."""

import pytest
from awslabs.cfn_mcp_server.template_capabilities import (
    detect_required_capabilities,
    detect_template_parameters,
    detect_template_outputs,
    _contains_iam_resources,
    _contains_named_iam_resources,
    _contains_transforms
)


def test_detect_required_capabilities_iam():
    """Test detecting IAM capabilities."""
    template = {
        "Resources": {
            "MyRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "lambda.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    }
                }
            }
        }
    }
    
    capabilities = detect_required_capabilities(template)
    
    assert "CAPABILITY_IAM" in capabilities


def test_detect_required_capabilities_named_iam():
    """Test detecting named IAM capabilities."""
    template = {
        "Resources": {
            "MyRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "RoleName": "MyExplicitRoleName",
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "lambda.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    }
                }
            }
        }
    }
    
    capabilities = detect_required_capabilities(template)
    
    assert "CAPABILITY_IAM" in capabilities
    assert "CAPABILITY_NAMED_IAM" in capabilities


def test_detect_required_capabilities_transform():
    """Test detecting transform capabilities."""
    template = {
        "Transform": "AWS::Serverless-2016-10-31",
        "Resources": {
            "MyFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "index.handler",
                    "Runtime": "nodejs14.x",
                    "CodeUri": "./src"
                }
            }
        }
    }
    
    capabilities = detect_required_capabilities(template)
    
    assert "CAPABILITY_AUTO_EXPAND" in capabilities


def test_detect_template_parameters():
    """Test detecting template parameters."""
    template = {
        "Parameters": {
            "InstanceType": {
                "Type": "String",
                "Default": "t3.micro",
                "AllowedValues": ["t3.micro", "t3.small", "t3.medium"],
                "Description": "EC2 instance type"
            },
            "KeyName": {
                "Type": "AWS::EC2::KeyPair::KeyName",
                "Description": "Name of an existing EC2 KeyPair"
            }
        }
    }
    
    parameters = detect_template_parameters(template)
    
    assert len(parameters) == 2
    assert "InstanceType" in parameters
    assert "KeyName" in parameters
    assert parameters["InstanceType"]["Type"] == "String"
    assert parameters["InstanceType"]["Default"] == "t3.micro"


def test_detect_template_outputs():
    """Test detecting template outputs."""
    template = {
        "Outputs": {
            "BucketName": {
                "Description": "Name of the S3 bucket",
                "Value": {"Ref": "MyBucket"},
                "Export": {
                    "Name": {"Fn::Sub": "${AWS::StackName}-bucket-name"}
                }
            },
            "WebsiteURL": {
                "Description": "URL of the website",
                "Value": {"Fn::GetAtt": ["MyBucket", "WebsiteURL"]}
            }
        }
    }
    
    outputs = detect_template_outputs(template)
    
    assert len(outputs) == 2
    assert "BucketName" in outputs
    assert "WebsiteURL" in outputs
    assert outputs["BucketName"]["Description"] == "Name of the S3 bucket"
    assert "Export" in outputs["BucketName"]