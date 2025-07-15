"""Resource mapping for CloudFormation template generation."""

from typing import Dict, List, Any, Set

# Comprehensive mapping of common terms to AWS resource types
RESOURCE_MAPPING = {
    # Compute
    "ec2": "AWS::EC2::Instance",
    "instance": "AWS::EC2::Instance",
    "server": "AWS::EC2::Instance",
    "vm": "AWS::EC2::Instance",
    "lambda": "AWS::Lambda::Function",
    "function": "AWS::Lambda::Function",
    "serverless": "AWS::Lambda::Function",
    "ecs": "AWS::ECS::Service",
    "container": "AWS::ECS::Service",
    "docker": "AWS::ECS::Service",
    "fargate": "AWS::ECS::Service",
    "eks": "AWS::EKS::Cluster",
    "kubernetes": "AWS::EKS::Cluster",
    "k8s": "AWS::EKS::Cluster",
    
    # Storage
    "s3": "AWS::S3::Bucket",
    "bucket": "AWS::S3::Bucket",
    "storage": "AWS::S3::Bucket",
    "ebs": "AWS::EC2::Volume",
    "volume": "AWS::EC2::Volume",
    "efs": "AWS::EFS::FileSystem",
    "file system": "AWS::EFS::FileSystem",
    
    # Database
    "rds": "AWS::RDS::DBInstance",
    "database": "AWS::RDS::DBInstance",
    "db": "AWS::RDS::DBInstance",
    "mysql": "AWS::RDS::DBInstance",
    "postgres": "AWS::RDS::DBInstance",
    "postgresql": "AWS::RDS::DBInstance",
    "aurora": "AWS::RDS::DBCluster",
    "dynamodb": "AWS::DynamoDB::Table",
    "nosql": "AWS::DynamoDB::Table",
    "table": "AWS::DynamoDB::Table",
    "elasticache": "AWS::ElastiCache::CacheCluster",
    "redis": "AWS::ElastiCache::CacheCluster",
    "memcached": "AWS::ElastiCache::CacheCluster",
    
    # Networking
    "vpc": "AWS::EC2::VPC",
    "subnet": "AWS::EC2::Subnet",
    "security group": "AWS::EC2::SecurityGroup",
    "sg": "AWS::EC2::SecurityGroup",
    "alb": "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "elb": "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "load balancer": "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "lb": "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "api gateway": "AWS::ApiGateway::RestApi",
    "api": "AWS::ApiGateway::RestApi",
    "rest": "AWS::ApiGateway::RestApi",
    "cloudfront": "AWS::CloudFront::Distribution",
    "cdn": "AWS::CloudFront::Distribution",
    "route53": "AWS::Route53::HostedZone",
    "dns": "AWS::Route53::HostedZone",
    
    # Security
    "iam": "AWS::IAM::Role",
    "role": "AWS::IAM::Role",
    "policy": "AWS::IAM::Policy",
    "kms": "AWS::KMS::Key",
    "key": "AWS::KMS::Key",
    "encryption": "AWS::KMS::Key",
    "certificate": "AWS::CertificateManager::Certificate",
    "acm": "AWS::CertificateManager::Certificate",
    "ssl": "AWS::CertificateManager::Certificate",
    "tls": "AWS::CertificateManager::Certificate",
    
    # Monitoring
    "cloudwatch": "AWS::CloudWatch::Alarm",
    "alarm": "AWS::CloudWatch::Alarm",
    "logs": "AWS::Logs::LogGroup",
    "logging": "AWS::Logs::LogGroup",
    "sns": "AWS::SNS::Topic",
    "notification": "AWS::SNS::Topic",
    "sqs": "AWS::SQS::Queue",
    "queue": "AWS::SQS::Queue",
    
    # Integration
    "step functions": "AWS::StepFunctions::StateMachine",
    "state machine": "AWS::StepFunctions::StateMachine",
    "eventbridge": "AWS::Events::Rule",
    "event": "AWS::Events::Rule",
    "kinesis": "AWS::Kinesis::Stream",
    "stream": "AWS::Kinesis::Stream",
    "firehose": "AWS::KinesisFirehose::DeliveryStream"
}

# Architecture patterns with required components
ARCHITECTURE_PATTERNS = {
    "web application": {
        "components": [
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::EC2::Instance",
            "AWS::EC2::SecurityGroup",
            "AWS::EC2::VPC"
        ],
        "optional": [
            "AWS::RDS::DBInstance",
            "AWS::ElastiCache::CacheCluster"
        ]
    },
    "serverless api": {
        "components": [
            "AWS::ApiGateway::RestApi",
            "AWS::Lambda::Function",
            "AWS::IAM::Role"
        ],
        "optional": [
            "AWS::DynamoDB::Table",
            "AWS::S3::Bucket"
        ]
    },
    "microservices": {
        "components": [
            "AWS::ECS::Service",
            "AWS::ECS::Cluster",
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::EC2::VPC"
        ],
        "optional": [
            "AWS::RDS::DBInstance",
            "AWS::ElastiCache::CacheCluster"
        ]
    },
    "data pipeline": {
        "components": [
            "AWS::S3::Bucket",
            "AWS::Lambda::Function",
            "AWS::IAM::Role"
        ],
        "optional": [
            "AWS::Kinesis::Stream",
            "AWS::Glue::Job"
        ]
    },
    "static website": {
        "components": [
            "AWS::S3::Bucket",
            "AWS::CloudFront::Distribution"
        ],
        "optional": [
            "AWS::Route53::RecordSet",
            "AWS::CertificateManager::Certificate"
        ]
    }
}

def identify_resources_from_description(description: str) -> Dict[str, str]:
    """Identify AWS resources from a natural language description.
    
    Args:
        description: Natural language description
        
    Returns:
        Dictionary mapping resource names to AWS resource types
    """
    description_lower = description.lower()
    identified_resources = {}
    
    # First, try to identify architecture patterns
    architecture = None
    for pattern_name in ARCHITECTURE_PATTERNS:
        if pattern_name in description_lower:
            architecture = pattern_name
            break
    
    # If an architecture pattern is identified, add its components
    if architecture:
        components = ARCHITECTURE_PATTERNS[architecture]["components"]
        for i, component_type in enumerate(components):
            resource_name = f"{component_type.split('::')[-1]}{i+1}"
            identified_resources[resource_name] = component_type
    
    # Then look for specific resources
    for term, resource_type in RESOURCE_MAPPING.items():
        if term in description_lower:
            # Generate a unique name for this resource type
            base_name = resource_type.split('::')[-1]
            count = 1
            resource_name = f"{base_name}{count}"
            
            # Ensure we don't duplicate resource types from the architecture pattern
            while resource_name in identified_resources and identified_resources[resource_name] == resource_type:
                count += 1
                resource_name = f"{base_name}{count}"
            
            identified_resources[resource_name] = resource_type
    
    # Ensure we have at least one resource
    if not identified_resources:
        identified_resources["DefaultBucket"] = "AWS::S3::Bucket"
    
    return identified_resources


def get_related_resources(resources: Dict[str, str]) -> Dict[str, str]:
    """Get related resources that should be included based on the identified resources.
    
    Args:
        resources: Dictionary of identified resources
        
    Returns:
        Dictionary of additional related resources
    """
    related_resources = {}
    resource_types = set(resources.values())
    
    # Add IAM roles for Lambda functions
    if "AWS::Lambda::Function" in resource_types:
        related_resources["LambdaExecutionRole"] = "AWS::IAM::Role"
    
    # Add security groups for EC2 instances
    if "AWS::EC2::Instance" in resource_types and "AWS::EC2::SecurityGroup" not in resource_types:
        related_resources["InstanceSecurityGroup"] = "AWS::EC2::SecurityGroup"
    
    # Add VPC for resources that require it
    vpc_dependent_resources = [
        "AWS::EC2::Instance", 
        "AWS::RDS::DBInstance", 
        "AWS::ElasticLoadBalancingV2::LoadBalancer",
        "AWS::ECS::Service"
    ]
    
    if any(res in resource_types for res in vpc_dependent_resources) and "AWS::EC2::VPC" not in resource_types:
        related_resources["VPC"] = "AWS::EC2::VPC"
        related_resources["Subnet1"] = "AWS::EC2::Subnet"
        related_resources["Subnet2"] = "AWS::EC2::Subnet"
    
    # Add DB subnet group for RDS instances
    if "AWS::RDS::DBInstance" in resource_types and "AWS::EC2::VPC" in resource_types:
        related_resources["DBSubnetGroup"] = "AWS::RDS::DBSubnetGroup"
    
    # Add target group for ALB
    if "AWS::ElasticLoadBalancingV2::LoadBalancer" in resource_types:
        related_resources["TargetGroup"] = "AWS::ElasticLoadBalancingV2::TargetGroup"
    
    return related_resources