# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the configuration system."""

import os
import pytest
from unittest.mock import patch, MagicMock
from awslabs.cfn_mcp_server.config import ConfigManager


def test_config_initialization():
    """Test basic configuration initialization."""
    config = ConfigManager()
    
    # Check default values
    assert config.get_config('aws.default_region') is not None
    assert config.get_config('resources.ec2.performance_tiers.standard') == 't3.small'
    assert config.get_config('networking.vpc_cidr') == '10.0.0.0/16'


def test_config_environment_override():
    """Test environment variable overrides."""
    with patch.dict(os.environ, {'CFN_MCP_DEFAULT_REGION': 'eu-west-1'}):
        config = ConfigManager()
        assert config.get_config('aws.default_region') == 'eu-west-1'


def test_get_resource_config():
    """Test getting resource configuration by tier."""
    config = ConfigManager()
    
    # Test EC2 instance types by tier
    assert config.get_resource_config('ec2', 'basic', 'performance_tiers') == 't3.micro'
    assert config.get_resource_config('ec2', 'standard', 'performance_tiers') == 't3.small'
    assert config.get_resource_config('ec2', 'high', 'performance_tiers') == 't3.large'
    
    # Test Lambda memory sizes by tier
    assert config.get_resource_config('lambda', 'basic', 'memory_sizes') == 128
    assert config.get_resource_config('lambda', 'standard', 'memory_sizes') == 256
    assert config.get_resource_config('lambda', 'high', 'memory_sizes') == 1024


@patch('boto3.client')
def test_get_latest_ami(mock_boto_client):
    """Test getting the latest AMI ID."""
    # Mock SSM client response
    mock_ssm = MagicMock()
    mock_boto_client.return_value = mock_ssm
    mock_ssm.get_parameter.return_value = {
        'Parameter': {
            'Value': 'ami-12345678'
        }
    }
    
    config = ConfigManager()
    ami_id = config.get_latest_ami('us-west-2', 'amazon-linux-2')
    
    # Verify the correct parameter was requested
    mock_ssm.get_parameter.assert_called_with(
        Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
    )
    
    assert ami_id == 'ami-12345678'


@patch('boto3.client')
def test_get_latest_ami_fallback(mock_boto_client):
    """Test fallback to hardcoded AMIs when SSM fails."""
    # Mock SSM client to raise an exception
    mock_ssm = MagicMock()
    mock_boto_client.return_value = mock_ssm
    mock_ssm.get_parameter.side_effect = Exception("SSM error")
    
    config = ConfigManager()
    ami_id = config.get_latest_ami('us-west-2', 'amazon-linux-2')
    
    # Should return the fallback AMI for us-west-2
    assert ami_id == 'ami-098e42ae54c764c35'


def test_get_security_group_config():
    """Test getting security group configuration."""
    config = ConfigManager()
    
    # Test web security group rules
    web_rules = config.get_security_group_config('web')
    assert any(rule['port'] == 80 for rule in web_rules)
    assert any(rule['port'] == 443 for rule in web_rules)
    
    # Test database security group rules
    db_rules = config.get_security_group_config('database')
    assert any(rule['port'] == 3306 for rule in db_rules)  # MySQL
    assert any(rule['port'] == 5432 for rule in db_rules)  # PostgreSQL