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

"""Dynamic configuration management for CloudFormation MCP server."""

import os
import json
import ipaddress
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import boto3 only when needed to avoid circular imports
import importlib


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigManager:
    """Manages dynamic configuration for the CloudFormation MCP server."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Optional path to a configuration file
            
        Raises:
            ConfigValidationError: If configuration is invalid
        """
        self._initialized = False
        try:
            self.config = self._load_default_config()
            
            # Load from config file if provided
            if config_file and os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        self.config.update(file_config)
                except (json.JSONDecodeError, IOError) as e:
                    raise ConfigValidationError(f"Failed to load config file {config_file}: {e}")
            
            # Override with environment variables
            self._override_from_env()
            
            # Validate configuration
            self.validate_config()
            
            # Cache for AMI IDs
            self._ami_cache = {}
            
            self._initialized = True
        except Exception as e:
            self._initialized = False
            raise ConfigValidationError(f"Failed to initialize configuration: {e}")
    
    def is_initialized(self) -> bool:
        """Check if the configuration manager is properly initialized."""
        return getattr(self, '_initialized', False)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the configuration manager."""
        if not self.is_initialized():
            return {"status": "UNHEALTHY", "message": "Not initialized"}
        
        try:
            # Test basic config access
            region = self.get_config('aws.default_region', 'us-east-1')
            return {
                "status": "HEALTHY", 
                "message": "Configuration operational",
                "details": {"default_region": region}
            }
        except Exception as e:
            return {"status": "UNHEALTHY", "message": f"Config access failed: {e}"}
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "aws": {
                "default_region": os.environ.get("AWS_REGION", "us-east-1"),
                "user_agent": "cfn-mcp-server/1.0.0"
            },
            "resources": {
                "ec2": {
                    "performance_tiers": {
                        "basic": "t3.micro",
                        "standard": "t3.small",
                        "high": "t3.large"
                    }
                },
                "rds": {
                    "performance_tiers": {
                        "basic": "db.t3.micro",
                        "standard": "db.t3.small",
                        "high": "db.t3.medium"
                    },
                    "default_storage": {
                        "basic": 20,
                        "standard": 50,
                        "high": 100
                    },
                    "backup_retention": {
                        "basic": 7,
                        "standard": 14,
                        "high": 30
                    }
                },
                "lambda": {
                    "runtimes": {
                        "python": "python3.11",
                        "nodejs": "nodejs18.x",
                        "java": "java17",
                        "dotnet": "dotnet6",
                        "go": "go1.x",
                        "ruby": "ruby3.2"
                    },
                    "memory_sizes": {
                        "basic": 128,
                        "standard": 256,
                        "high": 1024
                    },
                    "timeouts": {
                        "basic": 15,
                        "standard": 30,
                        "high": 300
                    }
                },
                "dynamodb": {
                    "billing_modes": {
                        "basic": "PAY_PER_REQUEST",
                        "standard": "PAY_PER_REQUEST",
                        "high": "PROVISIONED"
                    },
                    "provisioned_capacity": {
                        "read": 5,
                        "write": 5
                    }
                },
                "kinesis": {
                    "shard_counts": {
                        "basic": 1,
                        "standard": 2,
                        "high": 5
                    },
                    "retention_hours": {
                        "basic": 24,
                        "standard": 48,
                        "high": 168
                    }
                }
            },
            "networking": {
                "vpc_cidr": "10.0.0.0/16",
                "subnet_cidrs": ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
                "security_groups": {
                    "web": {
                        "ingress": [
                            {"port": 80, "cidr": "0.0.0.0/0"},
                            {"port": 443, "cidr": "0.0.0.0/0"}
                        ]
                    },
                    "api": {
                        "ingress": [
                            {"port": 443, "cidr": "0.0.0.0/0"}
                        ]
                    },
                    "database": {
                        "ingress": [
                            {"port": 3306, "cidr": "10.0.0.0/16"},  # MySQL
                            {"port": 5432, "cidr": "10.0.0.0/16"}   # PostgreSQL
                        ]
                    }
                }
            },
            "template": {
                "format_version": "2010-09-09",
                "yaml_options": {
                    "default_flow_style": False,
                    "sort_keys": False
                }
            }
        }
    
    def _override_from_env(self):
        """Override configuration with environment variables."""
        # AWS configuration
        if os.environ.get("CFN_MCP_DEFAULT_REGION"):
            self.config["aws"]["default_region"] = os.environ.get("CFN_MCP_DEFAULT_REGION")
        
        # Resource configuration
        if os.environ.get("CFN_MCP_EC2_BASIC_TIER"):
            self.config["resources"]["ec2"]["performance_tiers"]["basic"] = os.environ.get("CFN_MCP_EC2_BASIC_TIER")
        
        if os.environ.get("CFN_MCP_EC2_STANDARD_TIER"):
            self.config["resources"]["ec2"]["performance_tiers"]["standard"] = os.environ.get("CFN_MCP_EC2_STANDARD_TIER")
        
        if os.environ.get("CFN_MCP_EC2_HIGH_TIER"):
            self.config["resources"]["ec2"]["performance_tiers"]["high"] = os.environ.get("CFN_MCP_EC2_HIGH_TIER")
        
        # Network configuration
        if os.environ.get("CFN_MCP_VPC_CIDR"):
            self.config["networking"]["vpc_cidr"] = os.environ.get("CFN_MCP_VPC_CIDR")
    
    def get_config(self, path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation path.
        
        Args:
            path: Dot-notation path (e.g., "aws.default_region")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
            
        Raises:
            ConfigValidationError: If the configuration value is invalid
        """
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if part not in value:
                return default
            value = value[part]
        
        # Validate specific config paths
        self._validate_config_value(path, value)
        
        return value
    
    def _validate_config_value(self, path: str, value: Any) -> None:
        """Validate a specific configuration value."""
        if path == "networking.vpc_cidr" and value:
            try:
                ipaddress.IPv4Network(value, strict=False)
            except ipaddress.AddressValueError:
                raise ConfigValidationError(f"Invalid VPC CIDR: {value}")
        elif path == "aws.default_region" and value:
            if not re.match(r'^[a-z]{2}-[a-z]+-\d+$', value):
                raise ConfigValidationError(f"Invalid AWS region: {value}")
    
    def get_latest_ami(self, region: str, os_type: str = "amazon-linux-2") -> str:
        """Get the latest AMI ID for the specified region and OS type.
        
        Uses AWS Systems Manager Parameter Store to get the latest AMIs.
        For example, Amazon Linux 2 AMIs are available at:
        /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
        
        Args:
            region: AWS region
            os_type: OS type (e.g., "amazon-linux-2", "amazon-linux-2023")
            
        Returns:
            Latest AMI ID
        """
        # Check cache first
        cache_key = f"{region}:{os_type}"
        if cache_key in self._ami_cache:
            return self._ami_cache[cache_key]
        
        # Fallback AMI mappings in case SSM call fails
        fallback_amis = {
            "amazon-linux-2": {
                "us-east-1": "ami-0c02fb55956c7d316",
                "us-east-2": "ami-05d8392b5a6a56e93",
                "us-west-1": "ami-0d9858aa3c6322f73",
                "us-west-2": "ami-098e42ae54c764c35",
                "eu-west-1": "ami-04f7efe62f419d9f5",
                "eu-central-1": "ami-0a1ee2fb28fe05df3",
                "ap-northeast-1": "ami-0218d08a1f9dac831",
                "ap-southeast-1": "ami-0b89f7b3f054b957e",
                "ap-southeast-2": "ami-075a72b1992cb0687"
            },
            "amazon-linux-2023": {
                "us-east-1": "ami-0440d3b780d96b29d",
                "us-east-2": "ami-02ca28e7c7b8f8be1",
                "us-west-1": "ami-0688ba7eeef921a60",
                "us-west-2": "ami-008fe2fc65df48dac",
                "eu-west-1": "ami-0a3c3a20c09d6f377",
                "eu-central-1": "ami-0faab6bdbac9486fb",
                "ap-northeast-1": "ami-0dafcef159a1fc745",
                "ap-southeast-1": "ami-0df7a207adb9748c7",
                "ap-southeast-2": "ami-0310483fb2b488153"
            }
        }
        
        try:
            # Import boto3 here to avoid circular imports
            boto3 = importlib.import_module('boto3')
            
            # Try to get the latest AMI from SSM Parameter Store
            ssm_client = boto3.client('ssm', region_name=region)
            
            if os_type == "amazon-linux-2":
                parameter_name = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
            elif os_type == "amazon-linux-2023":
                parameter_name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
            else:
                # Default to Amazon Linux 2
                parameter_name = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
            
            response = ssm_client.get_parameter(Name=parameter_name)
            ami_id = response['Parameter']['Value']
            
            # Cache the result
            self._ami_cache[cache_key] = ami_id
            return ami_id
            
        except Exception as e:
            # Fallback to hardcoded AMIs if SSM call fails
            os_amis = fallback_amis.get(os_type, fallback_amis["amazon-linux-2"])
            ami_id = os_amis.get(region, os_amis["us-east-1"])
            
            # Cache the result
            self._ami_cache[cache_key] = ami_id
            return ami_id
    
    def get_security_group_config(self, sg_type: str) -> List[Dict[str, Any]]:
        """Get security group configuration for a specific type.
        
        Args:
            sg_type: Security group type (e.g., "web", "api", "database")
            
        Returns:
            List of ingress rules
        """
        default_rules = [{"port": 22, "cidr": "0.0.0.0/0"}]  # Default SSH access
        
        sg_config = self.config.get("networking", {}).get("security_groups", {}).get(sg_type, {})
        ingress_rules = sg_config.get("ingress", [])
        
        return ingress_rules if ingress_rules else default_rules
    
    def get_resource_config(self, resource_type: str, tier: str, config_key: str, default: Any = None) -> Any:
        """Get resource configuration for a specific resource type, tier, and key.
        
        Args:
            resource_type: Resource type (e.g., "ec2", "rds", "lambda")
            tier: Performance tier (e.g., "basic", "standard", "high")
            config_key: Configuration key (e.g., "memory_sizes", "timeouts")
            default: Default value if configuration not found
            
        Returns:
            Configuration value or default
        """
        try:
            return self.config["resources"][resource_type][config_key][tier]
        except (KeyError, TypeError):
            return default
    
    def validate_config(self) -> None:
        """Validate the entire configuration."""
        self._validate_aws_config()
        self._validate_network_config()
        self._validate_resource_config()
    
    def _validate_aws_config(self) -> None:
        """Validate AWS configuration."""
        aws_config = self.config.get("aws", {})
        
        # Validate region
        region = aws_config.get("default_region")
        if region and not re.match(r'^[a-z]{2}-[a-z]+-\d+$', region):
            raise ConfigValidationError(f"Invalid AWS region format: {region}")
    
    def _validate_network_config(self) -> None:
        """Validate network configuration."""
        network_config = self.config.get("networking", {})
        
        # Validate VPC CIDR
        vpc_cidr = network_config.get("vpc_cidr")
        if vpc_cidr:
            try:
                ipaddress.IPv4Network(vpc_cidr, strict=False)
            except ipaddress.AddressValueError:
                raise ConfigValidationError(f"Invalid VPC CIDR: {vpc_cidr}")
        
        # Validate subnet CIDRs
        subnet_cidrs = network_config.get("subnet_cidrs", [])
        for cidr in subnet_cidrs:
            try:
                ipaddress.IPv4Network(cidr, strict=False)
            except ipaddress.AddressValueError:
                raise ConfigValidationError(f"Invalid subnet CIDR: {cidr}")
    
    def _validate_resource_config(self) -> None:
        """Validate resource configuration."""
        resources_config = self.config.get("resources", {})
        
        # Validate EC2 instance types
        ec2_config = resources_config.get("ec2", {})
        performance_tiers = ec2_config.get("performance_tiers", {})
        for tier, instance_type in performance_tiers.items():
            if not re.match(r'^[a-z]\d+\.[a-z]+$', instance_type):
                raise ConfigValidationError(f"Invalid EC2 instance type: {instance_type}")
        
        # Validate RDS instance classes
        rds_config = resources_config.get("rds", {})
        rds_tiers = rds_config.get("performance_tiers", {})
        for tier, instance_class in rds_tiers.items():
            if not re.match(r'^db\.[a-z]\d+\.[a-z]+$', instance_class):
                raise ConfigValidationError(f"Invalid RDS instance class: {instance_class}")


# Create a singleton instance with error handling
_config_manager_instance = None

def get_config_manager() -> ConfigManager:
    """Get the singleton config manager instance."""
    global _config_manager_instance
    if _config_manager_instance is None:
        try:
            _config_manager_instance = ConfigManager()
        except ConfigValidationError as e:
            raise ConfigValidationError(f"Failed to initialize config manager: {e}")
    
    if not _config_manager_instance.is_initialized():
        raise ConfigValidationError("Config manager is not properly initialized")
    
    return _config_manager_instance

# Backward compatibility
config_manager = get_config_manager()