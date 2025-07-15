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

"""Resource generation logic for CloudFormation templates."""

from typing import Dict, List, Any, Optional
import uuid

# Import config_manager only when needed to avoid circular dependencies
import importlib

# Get config_manager lazily
def get_config():
    from awslabs.cfn_mcp_server.config import config_manager
    return config_manager

class ResourceGenerator:
    """Generates CloudFormation resources with intelligent configurations."""
    
    def __init__(self, config=None):
        """Initialize the resource generator.
        
        Args:
            config: Optional configuration manager instance
        """
        self.config = config or get_config()
    
    def generate_resources(
        self, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Generate CloudFormation resources based on analysis."""
        resources = {}
        parameters = {}
        
        # Generate resources based on identified types
        for resource_key, resource_type in analysis['resources'].items():
            if resource_type == 'AWS::S3::Bucket':
                resources.update(self._generate_s3_bucket(resource_key, analysis))
            elif resource_type == 'AWS::Lambda::Function':
                resources.update(self._generate_lambda_function(resource_key, analysis))
            elif resource_type == 'AWS::DynamoDB::Table':
                resources.update(self._generate_dynamodb_table(resource_key, analysis))
            elif resource_type == 'AWS::ApiGateway::RestApi':
                resources.update(self._generate_api_gateway(resource_key, analysis))
            elif resource_type == 'AWS::EC2::Instance':
                resources.update(self._generate_ec2_instance(resource_key, analysis))
            elif resource_type == 'AWS::RDS::DBInstance':
                resources.update(self._generate_rds_instance(resource_key, analysis))
            elif resource_type == 'AWS::ElasticLoadBalancingV2::LoadBalancer':
                resources.update(self._generate_load_balancer(resource_key, analysis))
            elif resource_type == 'AWS::ECS::Service':
                resources.update(self._generate_ecs_service(resource_key, analysis))
            elif resource_type == 'AWS::CloudFront::Distribution':
                resources.update(self._generate_cloudfront(resource_key, analysis))
            elif resource_type == 'AWS::Kinesis::Stream':
                resources.update(self._generate_kinesis_stream(resource_key, analysis))
        
        # Add supporting resources
        if analysis.get('security_requirements', {}).get('vpc_isolation'):
            resources.update(self._generate_vpc_resources(analysis))
        
        # Add IAM roles where needed
        resources.update(self._generate_iam_resources(analysis))
        
        return resources
    
    def _generate_s3_bucket(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate S3 bucket configuration."""
        bucket_name = f"{key.title()}Bucket"
        
        config = {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": {"Fn::Sub": f"${{AWS::StackName}}-{key}-bucket"},
                "VersioningConfiguration": {"Status": "Enabled"},
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                }
            }
        }
        
        # Add encryption if required
        if analysis.get('security_requirements', {}).get('encryption'):
            config["Properties"]["BucketEncryption"] = {
                "ServerSideEncryptionConfiguration": [{
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            }
        
        # Add lifecycle configuration for cost optimization
        config["Properties"]["LifecycleConfiguration"] = {
            "Rules": [{
                "Id": "TransitionToIA",
                "Status": "Enabled",
                "Transitions": [{
                    "TransitionInDays": 30,
                    "StorageClass": "STANDARD_IA"
                }]
            }]
        }
        
        return {bucket_name: config}
    
    def _generate_lambda_function(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Lambda function configuration."""
        function_name = f"{key.title()}Function"
        role_name = f"{key.title()}FunctionRole"
        
        # Determine runtime based on description
        description = analysis.get('original_description', '').lower()
        
        # Default to Python
        runtime_key = 'python'
        handler = 'index.handler'
        code = 'def handler(event, context):\n    return {"statusCode": 200, "body": "Hello from Python Lambda!"}'
        
        # Check for specific languages in description
        if 'node' in description or 'javascript' in description or 'js' in description:
            runtime_key = 'nodejs'
            handler = 'index.handler'
            code = 'exports.handler = async (event) => {\n    return {\n        statusCode: 200,\n        body: "Hello from Node.js Lambda!"\n    };\n};'
        elif 'java' in description:
            runtime_key = 'java'
            handler = 'example.Handler::handleRequest'
            code = '// Java code would be provided as a JAR or ZIP file\n// This is a placeholder'
        elif 'go' in description or 'golang' in description:
            runtime_key = 'go'
            handler = 'main'
            code = '// Go code would be provided as a ZIP file\n// This is a placeholder'
        elif 'ruby' in description:
            runtime_key = 'ruby'
            handler = 'index.handler'
            code = 'def handler(event:, context:)\n  { statusCode: 200, body: "Hello from Ruby Lambda!" }\nend'
        elif 'dotnet' in description or 'c#' in description or 'csharp' in description:
            runtime_key = 'dotnet'
            handler = 'Assembly::Namespace.Class::Method'
            code = '// .NET code would be provided as a ZIP file\n// This is a placeholder'
        
        # Get runtime from configuration
        runtime = self.config.get_config(f'resources.lambda.runtimes.{runtime_key}', 'python3.11')
        
        # Determine performance tier
        perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
        
        # Get memory and timeout from configuration
        memory_size = self.config.get_resource_config('lambda', perf_tier, 'memory_sizes', 256)
        timeout = self.config.get_resource_config('lambda', perf_tier, 'timeouts', 30)
        
        # Function configuration
        function_config = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "FunctionName": {"Fn::Sub": f"${{AWS::StackName}}-{key}-function"},
                "Runtime": runtime,
                "Handler": handler,
                "Code": {"ZipFile": code},
                "Role": {"Fn::GetAtt": [role_name, "Arn"]},
                "Timeout": timeout,
                "MemorySize": memory_size
            }
        }
        
        # Add architecture - ARM for better price/performance if not specified otherwise
        if not any(arch in description for arch in ['x86', 'intel', 'amd64']):
            function_config["Properties"]["Architectures"] = ["arm64"]
        
        # Add tracing for non-basic tiers
        if perf_tier != 'basic':
            function_config["Properties"]["TracingConfig"] = {"Mode": "Active"}
        
        # Add environment variables if mentioned in description
        if 'environment' in description or 'env var' in description:
            function_config["Properties"]["Environment"] = {
                "Variables": {
                    "ENVIRONMENT": {"Ref": "AWS::StackName"},
                    "LOG_LEVEL": "INFO"
                }
            }
        
        # Determine required policies based on description
        managed_policies = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
        
        if 's3' in description or 'bucket' in description:
            managed_policies.append("arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
        
        if 'dynamodb' in description or 'dynamo' in description:
            managed_policies.append("arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess")
        
        # IAM Role
        role_config = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }]
                },
                "ManagedPolicyArns": managed_policies
            }
        }
        
        return {
            function_name: function_config,
            role_name: role_config
        }
    
    def _generate_dynamodb_table(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DynamoDB table configuration."""
        table_name = f"{key.title()}Table"
        
        # Determine performance tier
        perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
        
        # Get billing mode from configuration
        billing_mode = self.config.get_resource_config('dynamodb', perf_tier, 'billing_modes', 'PAY_PER_REQUEST')
        
        # Basic table configuration
        config = {
            "Type": "AWS::DynamoDB::Table",
            "Properties": {
                "TableName": {"Fn::Sub": f"${{AWS::StackName}}-{key}-table"},
                "BillingMode": billing_mode,
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ]
            }
        }
        
        # Add provisioned capacity if not using on-demand
        if billing_mode == 'PROVISIONED':
            read_capacity = self.config.get_config('resources.dynamodb.provisioned_capacity.read', 5)
            write_capacity = self.config.get_config('resources.dynamodb.provisioned_capacity.write', 5)
            
            config["Properties"]["ProvisionedThroughput"] = {
                "ReadCapacityUnits": read_capacity,
                "WriteCapacityUnits": write_capacity
            }
        
        # Add encryption for all but basic tier
        if analysis.get('security_requirements', {}).get('encryption') or perf_tier != 'basic':
            config["Properties"]["SSESpecification"] = {
                "SSEEnabled": True
            }
        
        # Add point-in-time recovery for standard and high tiers
        if analysis.get('scale_requirements', {}).get('high_availability') or perf_tier != 'basic':
            config["Properties"]["PointInTimeRecoverySpecification"] = {
                "PointInTimeRecoveryEnabled": True
            }
            
        # Add global secondary index if mentioned in description
        description = analysis.get('original_description', '').lower()
        if 'index' in description or 'query' in description or 'search' in description:
            # Add a GSI for common query patterns
            config["Properties"]["GlobalSecondaryIndexes"] = [
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "gsi1pk", "KeyType": "HASH"},
                        {"AttributeName": "gsi1sk", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ]
            
            # Add the GSI key attributes
            config["Properties"]["AttributeDefinitions"].extend([
                {"AttributeName": "gsi1pk", "AttributeType": "S"},
                {"AttributeName": "gsi1sk", "AttributeType": "S"}
            ])
            
            # Add provisioned capacity for the GSI if using provisioned billing
            if billing_mode == 'PROVISIONED':
                config["Properties"]["GlobalSecondaryIndexes"][0]["ProvisionedThroughput"] = {
                    "ReadCapacityUnits": read_capacity,
                    "WriteCapacityUnits": write_capacity
                }
        
        return {table_name: config}
    
    def _generate_api_gateway(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API Gateway configuration."""
        api_name = f"{key.title()}Api"
        
        config = {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "Name": {"Fn::Sub": f"${{AWS::StackName}}-{key}-api"},
                "Description": f"API Gateway for {analysis.get('original_description', 'application')}",
                "EndpointConfiguration": {
                    "Types": ["REGIONAL"]
                }
            }
        }
        
        return {api_name: config}
    
    def _generate_ec2_instance(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate EC2 instance configuration."""
        instance_name = f"{key.title()}Instance"
        sg_name = f"{key.title()}SecurityGroup"
        
        # Determine instance type based on performance requirements
        perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
        instance_type = self.config.get_resource_config('ec2', perf_tier, 'performance_tiers', 't3.small')
        
        # Get the latest AMI for the region
        region = analysis.get('region', self.config.get_config('aws.default_region'))
        os_type = 'amazon-linux-2'
        
        # Check if a specific OS is mentioned in the description
        description = analysis.get('original_description', '').lower()
        if 'amazon linux 2023' in description or 'al2023' in description:
            os_type = 'amazon-linux-2023'
        
        # Get the latest AMI ID
        ami_id = self.config.get_latest_ami(region, os_type)
        
        instance_config = {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "ImageId": ami_id,
                "InstanceType": instance_type,
                "SecurityGroupIds": [{"Ref": sg_name}],
                "Tags": [
                    {"Key": "Name", "Value": {"Fn::Sub": f"${{AWS::StackName}}-{key}-instance"}}
                ]
            }
        }
        
        # Determine security group type based on description
        sg_type = "web"  # Default to web security group
        if 'api' in description or 'backend' in description:
            sg_type = "api"
        elif 'database' in description or 'db' in description:
            sg_type = "database"
        
        # Get security group rules from configuration
        sg_rules = self.config.get_security_group_config(sg_type)
        sg_ingress = []
        
        for rule in sg_rules:
            sg_ingress.append({
                "IpProtocol": "tcp",
                "FromPort": rule.get('port'),
                "ToPort": rule.get('port'),
                "CidrIp": rule.get('cidr')
            })
        
        # Add default SSH access if no rules defined
        if not sg_ingress:
            sg_ingress = [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "CidrIp": "0.0.0.0/0"
                }
            ]
        
        # Security Group
        sg_config = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": f"Security group for {key} instance",
                "SecurityGroupIngress": sg_ingress
            }
        }
        
        return {
            instance_name: instance_config,
            sg_name: sg_config
        }
    
    def _generate_rds_instance(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RDS instance configuration."""
        db_name = f"{key.title()}Database"
        
        # Determine engine based on description
        description = analysis.get('original_description', '').lower()
        if 'postgres' in description:
            engine = 'postgres'
            engine_version = '15.3'
        elif 'mysql' in description:
            engine = 'mysql'
            engine_version = '8.0.33'
        elif 'mariadb' in description:
            engine = 'mariadb'
            engine_version = '10.6.14'
        elif 'aurora' in description:
            if 'postgres' in description:
                engine = 'aurora-postgresql'
                engine_version = '15.3'
            else:
                engine = 'aurora-mysql'
                engine_version = '8.0.mysql_aurora.3.04.0'
        else:
            engine = 'mysql'
            engine_version = '8.0.33'
        
        # Determine performance tier
        perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
        
        # Get instance class from configuration
        instance_class = self.config.get_resource_config('rds', perf_tier, 'performance_tiers', 'db.t3.small')
        
        # Get storage and backup settings from configuration
        allocated_storage = str(self.config.get_resource_config('rds', perf_tier, 'default_storage', 20))
        backup_retention = self.config.get_resource_config('rds', perf_tier, 'backup_retention', 7)
        
        config = {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "DBInstanceIdentifier": {"Fn::Sub": f"${{AWS::StackName}}-{key}-db"},
                "DBInstanceClass": instance_class,
                "Engine": engine,
                "EngineVersion": engine_version,
                "MasterUsername": "admin",
                "MasterUserPassword": {"Ref": "DatabasePassword"},
                "AllocatedStorage": allocated_storage,
                "StorageType": "gp3",
                "BackupRetentionPeriod": backup_retention,
                "DeletionProtection": perf_tier == 'high'  # Enable deletion protection for high tier
            }
        }
        
        # Add Multi-AZ for high availability
        if analysis.get('scale_requirements', {}).get('high_availability') or perf_tier == 'high':
            config["Properties"]["MultiAZ"] = True
        
        # Add encryption if required or for high tier
        if analysis.get('security_requirements', {}).get('encryption') or perf_tier == 'high':
            config["Properties"]["StorageEncrypted"] = True
            
        # Add performance insights for standard and high tiers
        if perf_tier in ['standard', 'high']:
            config["Properties"]["EnablePerformanceInsights"] = True
            config["Properties"]["PerformanceInsightsRetentionPeriod"] = 7
        
        return {db_name: config}
    
    def _generate_load_balancer(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Application Load Balancer configuration."""
        alb_name = f"{key.title()}LoadBalancer"
        
        config = {
            "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "Properties": {
                "Name": {"Fn::Sub": f"${{AWS::StackName}}-{key}-alb"},
                "Scheme": "internet-facing",
                "Type": "application",
                "IpAddressType": "ipv4"
            }
        }
        
        return {alb_name: config}
    
    def _generate_ecs_service(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ECS service configuration."""
        cluster_name = f"{key.title()}Cluster"
        service_name = f"{key.title()}Service"
        task_def_name = f"{key.title()}TaskDefinition"
        
        cluster_config = {
            "Type": "AWS::ECS::Cluster",
            "Properties": {
                "ClusterName": {"Fn::Sub": f"${{AWS::StackName}}-{key}-cluster"}
            }
        }
        
        task_def_config = {
            "Type": "AWS::ECS::TaskDefinition",
            "Properties": {
                "Family": {"Fn::Sub": f"${{AWS::StackName}}-{key}-task"},
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "Cpu": "256",
                "Memory": "512",
                "ContainerDefinitions": [{
                    "Name": f"{key}-container",
                    "Image": "nginx:latest",
                    "PortMappings": [{
                        "ContainerPort": 80,
                        "Protocol": "tcp"
                    }]
                }]
            }
        }
        
        return {
            cluster_name: cluster_config,
            task_def_name: task_def_config
        }
    
    def _generate_cloudfront(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CloudFront distribution configuration."""
        cf_name = f"{key.title()}Distribution"
        
        config = {
            "Type": "AWS::CloudFront::Distribution",
            "Properties": {
                "DistributionConfig": {
                    "Enabled": True,
                    "Comment": f"CloudFront distribution for {key}",
                    "DefaultCacheBehavior": {
                        "TargetOriginId": f"{key}-origin",
                        "ViewerProtocolPolicy": "redirect-to-https",
                        "AllowedMethods": ["GET", "HEAD"],
                        "CachedMethods": ["GET", "HEAD"],
                        "Compress": True
                    },
                    "Origins": [{
                        "Id": f"{key}-origin",
                        "DomainName": {"Fn::GetAtt": ["S3Bucket", "DomainName"]},
                        "S3OriginConfig": {}
                    }]
                }
            }
        }
        
        return {cf_name: config}
    
    def _generate_kinesis_stream(self, key: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Kinesis stream configuration."""
        stream_name = f"{key.title()}Stream"
        
        # Determine performance tier
        perf_tier = analysis.get('scale_requirements', {}).get('performance_tier', 'standard')
        
        # Get shard count and retention period from configuration
        shard_count = self.config.get_resource_config('kinesis', perf_tier, 'shard_counts', 1)
        retention_hours = self.config.get_resource_config('kinesis', perf_tier, 'retention_hours', 24)
        
        # Adjust shard count based on description if it mentions high throughput
        description = analysis.get('original_description', '').lower()
        if 'high throughput' in description or 'high volume' in description:
            shard_count = max(shard_count * 2, 5)  # Double the shard count or use at least 5
        
        config = {
            "Type": "AWS::Kinesis::Stream",
            "Properties": {
                "Name": {"Fn::Sub": f"${{AWS::StackName}}-{key}-stream"},
                "ShardCount": shard_count,
                "RetentionPeriodHours": retention_hours,
                "StreamModeDetails": {
                    "StreamMode": "PROVISIONED"
                }
            }
        }
        
        # Use on-demand mode for high tier or if mentioned in description
        if perf_tier == 'high' or 'on demand' in description or 'auto scaling' in description:
            config["Properties"]["StreamModeDetails"] = {
                "StreamMode": "ON_DEMAND"
            }
            # Remove shard count for on-demand mode
            if "ShardCount" in config["Properties"]:
                del config["Properties"]["ShardCount"]
        
        # Add encryption for all but basic tier
        if analysis.get('security_requirements', {}).get('encryption') or perf_tier != 'basic':
            config["Properties"]["StreamEncryption"] = {
                "EncryptionType": "KMS",
                "KeyId": "alias/aws/kinesis"
            }
        
        return {stream_name: config}
    
    def _generate_vpc_resources(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate VPC and related networking resources."""
        # Get VPC CIDR from configuration
        vpc_cidr = self.config.get_config('networking.vpc_cidr', '10.0.0.0/16')
        
        # Get subnet CIDRs from configuration
        subnet_cidrs = self.config.get_config('networking.subnet_cidrs', ['10.0.1.0/24', '10.0.2.0/24', '10.0.3.0/24'])
        
        # Determine how many subnets to create based on availability requirements
        high_availability = analysis.get('scale_requirements', {}).get('high_availability', False)
        multi_az = high_availability or analysis.get('scale_requirements', {}).get('multi_az', False)
        
        # For high availability, create at least 2 subnets in different AZs
        subnet_count = min(3 if multi_az else 1, len(subnet_cidrs))
        
        # Start with basic VPC resources
        resources = {
            "VPC": {
                "Type": "AWS::EC2::VPC",
                "Properties": {
                    "CidrBlock": vpc_cidr,
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True,
                    "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-vpc"}}]
                }
            },
            "InternetGateway": {
                "Type": "AWS::EC2::InternetGateway",
                "Properties": {
                    "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-igw"}}]
                }
            },
            "AttachGateway": {
                "Type": "AWS::EC2::VPCGatewayAttachment",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "InternetGatewayId": {"Ref": "InternetGateway"}
                }
            },
            "RouteTable": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-route-table"}}]
                }
            },
            "InternetRoute": {
                "Type": "AWS::EC2::Route",
                "DependsOn": "AttachGateway",
                "Properties": {
                    "RouteTableId": {"Ref": "RouteTable"},
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {"Ref": "InternetGateway"}
                }
            }
        }
        
        # Create multiple subnets for high availability
        for i in range(subnet_count):
            subnet_name = f"PublicSubnet{i+1}" if i > 0 else "PublicSubnet"
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
            
            # Create route table association for each subnet
            resources[f"RouteTableAssociation{i+1}"] = {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "SubnetId": {"Ref": subnet_name},
                    "RouteTableId": {"Ref": "RouteTable"}
                }
            }
        
        # Add NAT Gateway for private subnets if high availability is required
        if high_availability and 'private' in analysis.get('original_description', '').lower():
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
                    "SubnetId": {"Ref": "PublicSubnet"}
                }
            }
            
            # Add private subnet and route table
            resources["PrivateSubnet"] = {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "CidrBlock": "10.0.10.0/24",
                    "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                    "MapPublicIpOnLaunch": False,
                    "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-private-subnet"}}]
                }
            }
            
            resources["PrivateRouteTable"] = {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "VpcId": {"Ref": "VPC"},
                    "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${AWS::StackName}-private-route-table"}}]
                }
            }
            
            resources["PrivateRoute"] = {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "RouteTableId": {"Ref": "PrivateRouteTable"},
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "NatGatewayId": {"Ref": "NATGateway"}
                }
            }
            
            resources["PrivateRouteTableAssociation"] = {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "SubnetId": {"Ref": "PrivateSubnet"},
                    "RouteTableId": {"Ref": "PrivateRouteTable"}
                }
            }
        
        return resources
    
    def _generate_iam_resources(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate common IAM resources."""
        resources = {}
        
        # Add database password parameter if RDS is present
        if any('rds' in key.lower() for key in analysis.get('resources', {})):
            resources["DatabasePassword"] = {
                "Type": "AWS::SSM::Parameter::Value<String>",
                "Default": "/myapp/database/password",
                "NoEcho": True,
                "Description": "Database password stored in Systems Manager Parameter Store"
            }
        
        return resources
