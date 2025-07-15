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

"""Architecture-specific CloudFormation template generators."""

from typing import Dict, List, Any, Optional

# Import config_manager only when needed to avoid circular dependencies
import importlib

# Get config_manager lazily
def get_config():
    from awslabs.cfn_mcp_server.config import config_manager
    return config_manager


def generate_web_application_architecture(analysis: Dict[str, Any], config=None) -> Dict[str, Dict[str, Any]]:
    """Generate a comprehensive web application architecture with proper networking and security.
    
    This includes:
    - VPC with public and private subnets
    - Auto Scaling Group with Launch Template
    - Application Load Balancer with Target Group and Listener
    - RDS Database in private subnet
    - Security Groups with proper rules
    - IAM roles for EC2 instances
    
    Args:
        analysis: Analysis dictionary containing requirements
        config: Optional configuration manager
        
    Returns:
        Dictionary of CloudFormation resources
    """
    cfg = config or config_manager
    resources = {}
    
    # Extract requirements
    scale_req = analysis.get('scale_requirements', {})
    security_req = analysis.get('security_requirements', {})
    description = analysis.get('original_description', '').lower()
    
    # Determine instance count based on requirements
    instance_count = 1
    if scale_req.get('high_availability', False):
        instance_count = 3
    elif 'multiple instances' in description or 'auto scaling' in description:
        instance_count = 2
    
    # Determine if we need a database
    needs_database = any(resource_type.startswith('AWS::RDS::') for resource_type in analysis.get('resources', {}).values())
    
    # 1. Create VPC and networking components
    vpc_resources = _generate_vpc_with_subnets(analysis)
    resources.update(vpc_resources)
    
    # 2. Create security groups
    sg_resources = _generate_web_security_groups(analysis, needs_database)
    resources.update(sg_resources)
    
    # 3. Create IAM roles for EC2
    iam_resources = _generate_ec2_iam_role(analysis)
    resources.update(iam_resources)
    
    # 4. Create Launch Template
    lt_resources = _generate_launch_template(analysis)
    resources.update(lt_resources)
    
    # 5. Create Auto Scaling Group
    asg_resources = _generate_auto_scaling_group(analysis, instance_count)
    resources.update(asg_resources)
    
    # 6. Create Load Balancer, Target Group, and Listener
    lb_resources = _generate_load_balancer_resources(analysis)
    resources.update(lb_resources)
    
    # 7. Create Database if needed
    if needs_database:
        db_resources = _generate_database_resources(analysis)
        resources.update(db_resources)
    
    # 8. Add standard tags to all resources
    resources = add_standard_tags(resources)
    
    # 9. Add outputs
    outputs = _generate_web_app_outputs(analysis)
    
    return resources


def _generate_vpc_with_subnets(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate VPC with public and private subnets across multiple AZs."""
    resources = {}
    
    # Get configuration
    config = get_config()
    vpc_cidr = config.get_config('networking.vpc_cidr', '10.0.0.0/16')
    subnet_cidrs = config.get_config('networking.subnet_cidrs', ['10.0.1.0/24', '10.0.2.0/24', '10.0.3.0/24'])
    
    # Determine if we need multi-AZ setup
    high_availability = analysis.get('scale_requirements', {}).get('high_availability', False)
    multi_az = high_availability or analysis.get('scale_requirements', {}).get('multi_az', False)
    
    # Always create at least 2 subnets in different AZs for proper ALB and RDS support
    # For high availability, create 3 subnets if possible
    subnet_count = min(3 if multi_az else 2, len(subnet_cidrs))
    
    # Create VPC
    resources["VPC"] = {
        "Type": "AWS::EC2::VPC",
        "Properties": {
            "CidrBlock": vpc_cidr,
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True,
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-vpc"}}]
        }
    }
    
    # Create Internet Gateway
    resources["InternetGateway"] = {
        "Type": "AWS::EC2::InternetGateway",
        "Properties": {
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-igw"}}]
        }
    }
    
    # Attach Internet Gateway to VPC
    resources["AttachGateway"] = {
        "Type": "AWS::EC2::VPCGatewayAttachment",
        "Properties": {
            "VpcId": {"Ref": "VPC"},
            "InternetGatewayId": {"Ref": "InternetGateway"}
        }
    }
    
    # Create public route table
    resources["PublicRouteTable"] = {
        "Type": "AWS::EC2::RouteTable",
        "Properties": {
            "VpcId": {"Ref": "VPC"},
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-public-route-table"}}]
        }
    }
    
    # Create route to Internet Gateway
    resources["PublicRoute"] = {
        "Type": "AWS::EC2::Route",
        "DependsOn": "AttachGateway",
        "Properties": {
            "RouteTableId": {"Ref": "PublicRouteTable"},
            "DestinationCidrBlock": "0.0.0.0/0",
            "GatewayId": {"Ref": "InternetGateway"}
        }
    }
    
    # Create public subnets
    for i in range(subnet_count):
        subnet_name = f"PublicSubnet{i+1}"
        resources[subnet_name] = {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": {"Ref": "VPC"},
                "CidrBlock": subnet_cidrs[i],
                "AvailabilityZone": {"Fn::Select": [i, {"Fn::GetAZs": ""}]},
                "MapPublicIpOnLaunch": True,
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": f"${{AWS::StackName}}-public-subnet-{i+1}"}}]
            }
        }
        
        # Associate subnet with public route table
        resources[f"PublicSubnetRouteTableAssociation{i+1}"] = {
            "Type": "AWS::EC2::SubnetRouteTableAssociation",
            "Properties": {
                "SubnetId": {"Ref": subnet_name},
                "RouteTableId": {"Ref": "PublicRouteTable"}
            }
        }
    
    # Create private subnets and NAT Gateway if needed
    if multi_az or analysis.get('security_requirements', {}).get('vpc_isolation'):
        # Create NAT Gateway
        resources["ElasticIP"] = {
            "Type": "AWS::EC2::EIP",
            "DependsOn": "AttachGateway",
            "Properties": {
                "Domain": "vpc"
            }
        }
        
        resources["NATGateway"] = {
            "Type": "AWS::EC2::NatGateway",
            "Properties": {
                "AllocationId": {"Fn::GetAtt": ["ElasticIP", "AllocationId"]},
                "SubnetId": {"Ref": "PublicSubnet1"}
            }
        }
        
        # Create private route table
        resources["PrivateRouteTable"] = {
            "Type": "AWS::EC2::RouteTable",
            "Properties": {
                "VpcId": {"Ref": "VPC"},
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-private-route-table"}}]
            }
        }
        
        # Create route to NAT Gateway
        resources["PrivateRoute"] = {
            "Type": "AWS::EC2::Route",
            "Properties": {
                "RouteTableId": {"Ref": "PrivateRouteTable"},
                "DestinationCidrBlock": "0.0.0.0/0",
                "NatGatewayId": {"Ref": "NATGateway"}
            }
        }
        
        # Create private subnets - always create at least 2 for RDS multi-AZ support
        private_subnet_cidrs = ['10.0.10.0/24', '10.0.11.0/24', '10.0.12.0/24']
        # Always create at least 2 private subnets for RDS subnet groups
        private_subnet_count = max(2, min(subnet_count, len(private_subnet_cidrs)))
        
        for i in range(private_subnet_count):
            subnet_name = f"PrivateSubnet{i+1}"
            resources[subnet_name] = {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "CidrBlock": private_subnet_cidrs[i],
                    "AvailabilityZone": {"Fn::Select": [i, {"Fn::GetAZs": ""}]},
                    "MapPublicIpOnLaunch": False,
                    "Tags": [{"Key": "Name", "Value": {"Fn::Sub": f"${{AWS::StackName}}-private-subnet-{i+1}"}}]
                }
            }
            
            # Associate subnet with private route table
            resources[f"PrivateSubnetRouteTableAssociation{i+1}"] = {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "SubnetId": {"Ref": subnet_name},
                    "RouteTableId": {"Ref": "PrivateRouteTable"}
                }
            }
    
    return resources


def _generate_web_security_groups(analysis: Dict[str, Any], needs_database: bool) -> Dict[str, Dict[str, Any]]:
    """Generate security groups for web application components."""
    resources = {}
    
    # Create ALB security group
    resources["ALBSecurityGroup"] = {
        "Type": "AWS::EC2::SecurityGroup",
        "Properties": {
            "GroupDescription": "Security group for Application Load Balancer",
            "VpcId": {"Ref": "VPC"},
            "SecurityGroupIngress": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "CidrIp": "0.0.0.0/0"
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 443,
                    "ToPort": 443,
                    "CidrIp": "0.0.0.0/0"
                }
            ],
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-alb-sg"}}]
        }
    }
    
    # Create EC2 security group with more secure configuration
    resources["EC2SecurityGroup"] = {
        "Type": "AWS::EC2::SecurityGroup",
        "Properties": {
            "GroupDescription": "Security group for EC2 instances",
            "VpcId": {"Ref": "VPC"},
            "SecurityGroupIngress": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "SourceSecurityGroupId": {"Ref": "ALBSecurityGroup"}
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 443,
                    "ToPort": 443,
                    "SourceSecurityGroupId": {"Ref": "ALBSecurityGroup"}
                }
                # SSH access is not enabled by default for security reasons
                # Use AWS Systems Manager Session Manager for secure instance access
            ],
            "Tags": [
                {"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-ec2-sg"}},
                {"Key": "Description", "Value": "Restricts access to EC2 instances from ALB only"}
            ]
        }
    }
    
    # Add SSM access role to EC2 instance profile for secure shell access
    # This allows using AWS Systems Manager Session Manager instead of SSH
    
    # Create database security group if needed
    if needs_database:
        resources["DBSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for RDS database",
                "VpcId": {"Ref": "VPC"},
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": db_port,  # Use the correct port for the database engine
                        "ToPort": db_port,
                        "SourceSecurityGroupId": {"Ref": "EC2SecurityGroup"}
                    }
                ],
                "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-db-sg"}}]
            }
        }
    
    return resources


def _generate_ec2_iam_role(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate IAM role for EC2 instances."""
    resources = {}
    
    # Create IAM role
    resources["EC2InstanceRole"] = {
        "Type": "AWS::IAM::Role",
        "Properties": {
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            },
            "ManagedPolicyArns": [
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
            ],
            "Path": "/",
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-ec2-role"}}]
        }
    }
    
    # Create instance profile
    resources["EC2InstanceProfile"] = {
        "Type": "AWS::IAM::InstanceProfile",
        "Properties": {
            "Path": "/",
            "Roles": [{"Ref": "EC2InstanceRole"}]
        }
    }
    
    return resources


def _generate_launch_template(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate Launch Template for EC2 instances."""
    resources = {}
    
    # Determine performance tier
    perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
    
    # Get configuration
    config = get_config()
    
    # Get instance type from configuration
    instance_type = config.get_resource_config('ec2', perf_tier, 'performance_tiers', 't3.small')
    
    # Get configuration
    config = get_config()
    
    # Get the latest AMI for the region
    region = analysis.get('region', config.get_config('aws.default_region'))
    os_type = 'amazon-linux-2'
    
    # Check if a specific OS is mentioned in the description
    description = analysis.get('original_description', '').lower()
    if 'amazon linux 2023' in description or 'al2023' in description:
        os_type = 'amazon-linux-2023'
    
    # Get the latest AMI ID
    ami_id = config.get_latest_ami(region, os_type)
    
    # Create user data script
    user_data = {
        "Fn::Base64": {
            "Fn::Join": ["", [
                "#!/bin/bash -xe\n",
                "yum update -y\n",
                "yum install -y httpd\n",
                "systemctl start httpd\n",
                "systemctl enable httpd\n",
                "echo '<html><body><h1>Hello from ",
                {"Ref": "AWS::StackName"},
                "</h1></body></html>' > /var/www/html/index.html\n"
            ]]
        }
    }
    
    # Create Launch Template
    resources["LaunchTemplate"] = {
        "Type": "AWS::EC2::LaunchTemplate",
        "Properties": {
            "LaunchTemplateName": {"Fn::Sub": "${AWS::StackName}-launch-template"},
            "VersionDescription": "Initial version",
            "LaunchTemplateData": {
                "ImageId": ami_id,
                "InstanceType": instance_type,
                "SecurityGroupIds": [{"Ref": "EC2SecurityGroup"}],
                "IamInstanceProfile": {
                    "Arn": {"Fn::GetAtt": ["EC2InstanceProfile", "Arn"]}
                },
                "UserData": user_data,
                "TagSpecifications": [
                    {
                        "ResourceType": "instance",
                        "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-web-server"}}]
                    }
                ]
            }
        }
    }
    
    return resources


def _generate_auto_scaling_group(analysis: Dict[str, Any], instance_count: int) -> Dict[str, Dict[str, Any]]:
    """Generate Auto Scaling Group for EC2 instances."""
    resources = {}
    
    # Determine min/max/desired capacity
    min_size = 1
    max_size = instance_count * 2  # Allow scaling to double the initial size
    desired_capacity = instance_count
    
    # Create Auto Scaling Group - always use at least 2 subnets for high availability
    resources["AutoScalingGroup"] = {
        "Type": "AWS::AutoScaling::AutoScalingGroup",
        "Properties": {
            "AutoScalingGroupName": {"Fn::Sub": "${AWS::StackName}-asg"},
            "MinSize": str(min_size),
            "MaxSize": str(max_size),
            "DesiredCapacity": str(desired_capacity),
            "LaunchTemplate": {
                "LaunchTemplateId": {"Ref": "LaunchTemplate"},
                "Version": {"Fn::GetAtt": ["LaunchTemplate", "LatestVersionNumber"]}
            },
            "VPCZoneIdentifier": [
                {"Ref": "PublicSubnet1"},
                {"Ref": "PublicSubnet2"}
            ],
            "TargetGroupARNs": [
                {"Ref": "TargetGroup"}
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": {"Fn::Sub": "${AWS::StackName}-web-server"},
                    "PropagateAtLaunch": True
                }
            ]
        }
    }
    
    # If we have a third subnet, use it too
    if "PublicSubnet3" in resources:
        resources["AutoScalingGroup"]["Properties"]["VPCZoneIdentifier"].append({"Ref": "PublicSubnet3"})
    
    # Add scaling policies if auto scaling is requested
    if analysis.get('scale_requirements', {}).get('auto_scaling'):
        resources["ScaleUpPolicy"] = {
            "Type": "AWS::AutoScaling::ScalingPolicy",
            "Properties": {
                "AutoScalingGroupName": {"Ref": "AutoScalingGroup"},
                "PolicyType": "TargetTrackingScaling",
                "TargetTrackingConfiguration": {
                    "PredefinedMetricSpecification": {
                        "PredefinedMetricType": "ASGAverageCPUUtilization"
                    },
                    "TargetValue": 70.0
                }
            }
        }
    
    return resources


def _generate_load_balancer_resources(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate Load Balancer, Target Group, and Listener."""
    resources = {}
    
    # Create Target Group
    resources["TargetGroup"] = {
        "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
        "Properties": {
            "Name": {"Fn::Sub": "${AWS::StackName}-tg"},
            "Port": 80,
            "Protocol": "HTTP",
            "VpcId": {"Ref": "VPC"},
            "HealthCheckPath": "/",
            "HealthCheckProtocol": "HTTP",
            "HealthCheckIntervalSeconds": 30,
            "HealthCheckTimeoutSeconds": 5,
            "HealthyThresholdCount": 2,
            "UnhealthyThresholdCount": 5,
            "TargetType": "instance",
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-target-group"}}]
        }
    }
    
    # Create Application Load Balancer - always use at least 2 subnets for high availability
    resources["ApplicationLoadBalancer"] = {
        "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
        "Properties": {
            "Name": {"Fn::Sub": "${AWS::StackName}-alb"},
            "Scheme": "internet-facing",
            "LoadBalancerAttributes": [
                {"Key": "idle_timeout.timeout_seconds", "Value": "60"}
            ],
            "Subnets": [
                {"Ref": "PublicSubnet1"},
                {"Ref": "PublicSubnet2"}
            ],
            "SecurityGroups": [{"Ref": "ALBSecurityGroup"}],
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-alb"}}]
        }
    }
    
    # If we have a third subnet, use it too
    if "PublicSubnet3" in resources:
        resources["ApplicationLoadBalancer"]["Properties"]["Subnets"].append({"Ref": "PublicSubnet3"})
    
    # Create HTTP Listener
    resources["HTTPListener"] = {
        "Type": "AWS::ElasticLoadBalancingV2::Listener",
        "Properties": {
            "DefaultActions": [{
                "Type": "forward",
                "TargetGroupArn": {"Ref": "TargetGroup"}
            }],
            "LoadBalancerArn": {"Ref": "ApplicationLoadBalancer"},
            "Port": 80,
            "Protocol": "HTTP"
        }
    }
    
    return resources


def _generate_database_resources(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate RDS database resources."""
    resources = {}
    
    # Determine performance tier
    perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
    
    # Get configuration
    config = get_config()
    
    # Get instance class from configuration
    instance_class = config.get_resource_config('rds', perf_tier, 'performance_tiers', 'db.t3.small')
    
    # Get storage and backup settings from configuration
    allocated_storage = str(config.get_resource_config('rds', perf_tier, 'default_storage', 20))
    backup_retention = config.get_resource_config('rds', perf_tier, 'backup_retention', 7)
    
    # Determine engine based on description
    description = analysis.get('original_description', '').lower()
    if 'postgres' in description:
        engine = 'postgres'
        engine_version = '15.3'
        port = 5432
    elif 'mysql' in description:
        engine = 'mysql'
        engine_version = '8.0.33'
        port = 3306
    elif 'mariadb' in description:
        engine = 'mariadb'
        engine_version = '10.6.14'
        port = 3306
    elif 'aurora' in description:
        if 'postgres' in description:
            engine = 'aurora-postgresql'
            engine_version = '15.3'
            port = 5432
        else:
            engine = 'aurora-mysql'
            engine_version = '8.0.mysql_aurora.3.04.0'
            port = 3306
    else:
        engine = 'mysql'
        engine_version = '8.0.33'
        port = 3306
        
    # Store the port in the resources for security group configuration
    db_port = port
    
    # Create DB Subnet Group - always include at least 2 subnets for multi-AZ support
    resources["DBSubnetGroup"] = {
        "Type": "AWS::RDS::DBSubnetGroup",
        "Properties": {
            "DBSubnetGroupDescription": "Subnet group for RDS database",
            "SubnetIds": [
                {"Ref": "PrivateSubnet1"},
                {"Ref": "PrivateSubnet2"}
            ],
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-db-subnet-group"}}]
        }
    }
    
    # If we have a third private subnet, use it too
    if "PrivateSubnet3" in resources:
        resources["DBSubnetGroup"]["Properties"]["SubnetIds"].append({"Ref": "PrivateSubnet3"})
    
    # Create DB Parameter Group
    resources["DBParameterGroup"] = {
        "Type": "AWS::RDS::DBParameterGroup",
        "Properties": {
            "Description": f"Parameter group for {engine}",
            "Family": f"{engine}{engine_version.split('.')[0]}.{engine_version.split('.')[1]}",
            "Parameters": {
                "character_set_server": "utf8mb4",
                "collation_server": "utf8mb4_unicode_ci"
            },
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-db-parameter-group"}}]
        }
    }
    
    # Create DB Instance
    resources["DBInstance"] = {
        "Type": "AWS::RDS::DBInstance",
        "Properties": {
            "DBInstanceIdentifier": {"Fn::Sub": "${AWS::StackName}-db"},
            "DBInstanceClass": instance_class,
            "Engine": engine,
            "EngineVersion": engine_version,
            "MasterUsername": "admin",
            "MasterUserPassword": {"Ref": "DBPassword"},
            "AllocatedStorage": allocated_storage,
            "StorageType": "gp3",
            "BackupRetentionPeriod": backup_retention,
            "DBSubnetGroupName": {"Ref": "DBSubnetGroup"},
            "VPCSecurityGroups": [{"Ref": "DBSecurityGroup"}],
            "DBParameterGroupName": {"Ref": "DBParameterGroup"},
            "MultiAZ": analysis.get('scale_requirements', {}).get('high_availability', False),
            "StorageEncrypted": analysis.get('security_requirements', {}).get('encryption', True),
            "DeletionProtection": perf_tier == 'high',
            "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-db"}}]
        }
    }
    
    # Add DB password parameter
    resources["DBPassword"] = {
        "Type": "AWS::SSM::Parameter",
        "Properties": {
            "Name": {"Fn::Sub": "/${AWS::StackName}/database/password"},
            "Type": "SecureString",
            "Value": {"Fn::Join": ["", ["{{resolve:secretsmanager:", {"Ref": "DBPasswordSecret"}, ":SecretString:password}}"]]}
        }
    }
    
    # Add DB password secret
    resources["DBPasswordSecret"] = {
        "Type": "AWS::SecretsManager::Secret",
        "Properties": {
            "Name": {"Fn::Sub": "${AWS::StackName}-db-password"},
            "Description": {"Fn::Sub": "Password for ${AWS::StackName} database"},
            "GenerateSecretString": {
                "SecretStringTemplate": '{"username": "admin"}',
                "GenerateStringKey": "password",
                "PasswordLength": 16,
                "ExcludeCharacters": "\"@/\\"
            }
        }
    }
    
    return resources


def _generate_web_app_outputs(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate comprehensive outputs for web application."""
    outputs = {}
    
    # Add VPC ID
    outputs["VPCId"] = {
        "Description": "ID of the VPC",
        "Value": {"Ref": "VPC"},
        "Export": {
            "Name": {"Fn::Sub": "${AWS::StackName}-vpc-id"}
        }
    }
    
    # Add ALB DNS Name
    outputs["ALBDNSName"] = {
        "Description": "DNS name of the Application Load Balancer",
        "Value": {"Fn::GetAtt": ["ApplicationLoadBalancer", "DNSName"]},
        "Export": {
            "Name": {"Fn::Sub": "${AWS::StackName}-alb-dns"}
        }
    }
    
    # Add Application URL
    outputs["ApplicationURL"] = {
        "Description": "URL of the application",
        "Value": {"Fn::Sub": "http://${ApplicationLoadBalancer.DNSName}"}
    }
    
    # Add Auto Scaling Group Name
    outputs["AutoScalingGroupName"] = {
        "Description": "Name of the Auto Scaling Group",
        "Value": {"Ref": "AutoScalingGroup"},
        "Export": {
            "Name": {"Fn::Sub": "${AWS::StackName}-asg-name"}
        }
    }
    
    # Add DB Endpoint if database exists
    if "DBInstance" in analysis.get('resources', {}):
        outputs["DBEndpoint"] = {
            "Description": "Endpoint of the RDS database",
            "Value": {"Fn::GetAtt": ["DBInstance", "Endpoint.Address"]},
            "Export": {
                "Name": {"Fn::Sub": "${AWS::StackName}-db-endpoint"}
            }
        }
        
        outputs["DBName"] = {
            "Description": "Name of the RDS database",
            "Value": {"Ref": "DBInstance"},
            "Export": {
                "Name": {"Fn::Sub": "${AWS::StackName}-db-name"}
            }
        }
    
    return outputs


def generate_serverless_api_architecture(analysis: Dict[str, Any], config=None) -> Dict[str, Dict[str, Any]]:
    """Generate a comprehensive serverless API architecture.
    
    This includes:
    - API Gateway
    - Lambda Functions
    - DynamoDB Table
    - IAM Roles
    - CloudWatch Logs
    
    Args:
        analysis: Analysis dictionary containing requirements
        config: Optional configuration manager
        
    Returns:
        Dictionary of CloudFormation resources
    """
    # Implementation will be similar to web application architecture
    # This is a placeholder for future implementation
    return {}


def generate_data_pipeline_architecture(analysis: Dict[str, Any], config=None) -> Dict[str, Dict[str, Any]]:
    """Generate a comprehensive data pipeline architecture.
    
    This includes:
    - S3 Buckets
    - Lambda Functions
    - Kinesis Streams
    - Glue Jobs
    - IAM Roles
    
    Args:
        analysis: Analysis dictionary containing requirements
        config: Optional configuration manager
        
    Returns:
        Dictionary of CloudFormation resources
    """
    # Implementation will be similar to web application architecture
    # This is a placeholder for future implementation
    return {}


def add_standard_tags(resources: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Add standard tags to all resources that support tagging.
    
    Args:
        resources: Dictionary of CloudFormation resources
        
    Returns:
        Updated resources with standard tags
    """
    standard_tags = [
        {"Key": "Environment", "Value": {"Ref": "Environment"}},
        {"Key": "Project", "Value": {"Ref": "AWS::StackName"}},
        {"Key": "ManagedBy", "Value": "CloudFormation"},
        {"Key": "CreatedBy", "Value": "EnhancedCFNMCPServer"}
    ]
    
    for resource_name, resource in resources.items():
        # Skip resources that don't support tags
        if resource.get('Type') in [
            'AWS::CloudFormation::WaitConditionHandle',
            'AWS::CloudFormation::WaitCondition',
            'AWS::IAM::Policy',
            'AWS::EC2::Route',
            'AWS::EC2::SubnetRouteTableAssociation',
            'AWS::EC2::VPCGatewayAttachment',
            'AWS::ElasticLoadBalancingV2::Listener',
            'AWS::AutoScaling::ScalingPolicy'
        ]:
            continue
        
        # Add tags to resources that support them
        if 'Properties' in resource:
            # Some resources use Tags, others use TagSpecifications
            if 'Tags' in resource['Properties']:
                # Check if Tags is a list (most resources)
                if isinstance(resource['Properties']['Tags'], list):
                    # Add standard tags if they don't already exist
                    existing_keys = [tag.get('Key') for tag in resource['Properties']['Tags']]
                    for tag in standard_tags:
                        if tag['Key'] not in existing_keys:
                            resource['Properties']['Tags'].append(tag)
            elif resource['Type'] == 'AWS::AutoScaling::AutoScalingGroup':
                # AutoScaling Groups use a different tag format with PropagateAtLaunch
                if 'Tags' not in resource['Properties']:
                    resource['Properties']['Tags'] = []
                
                existing_keys = [tag.get('Key') for tag in resource['Properties']['Tags']]
                for tag in standard_tags:
                    if tag['Key'] not in existing_keys:
                        asg_tag = {
                            'Key': tag['Key'],
                            'Value': tag['Value'],
                            'PropagateAtLaunch': True
                        }
                        resource['Properties']['Tags'].append(asg_tag)
    
    return resources