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

"""awslabs CFN MCP Server implementation."""

import argparse
import json
import time
import yaml
from typing import Dict, List, Any, Optional
import botocore.exceptions
from awslabs.cfn_mcp_server.resource_operations import ResourceOperations
from awslabs.cfn_mcp_server.stack_operations import StackOperations
from awslabs.cfn_mcp_server.template_operations import TemplateOperations
from awslabs.cfn_mcp_server.context import Context
from awslabs.cfn_mcp_server.aws_client import get_aws_client, get_actual_region
from awslabs.cfn_mcp_server.errors import ClientError, handle_aws_api_error
from awslabs.cfn_mcp_server.stack_manager import StackManager
from awslabs.cfn_mcp_server.iac_generator import create_template as create_template_impl
from mcp.server.fastmcp import FastMCP
from pydantic import Field


mcp = FastMCP(
    'awslabs.cfn-mcp-server',
    instructions="""
    # Enhanced CloudFormation MCP

    This MCP allows you to:
    1. Read and List all of your AWS resources by the CloudFormation type name (e.g. AWS::S3::Bucket)
    2. Create/Update/Delete your AWS resources
    3. Generate CloudFormation templates from natural language descriptions
    4. Deploy CloudFormation stacks with comprehensive parameter and tag support
    5. Troubleshoot CloudFormation deployments with detailed error analysis
    6. Automatically fix and retry failed CloudFormation deployments
    7. Monitor stack events and CloudWatch logs for debugging
    8. Handle stack updates, rollbacks, and deletions
    """,
    dependencies=['pydantic', 'loguru', 'boto3', 'botocore', 'pyyaml'],
)


@mcp.tool()
async def get_resource_schema_information(
    resource_type: str = Field(
        description='The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Get schema information for an AWS resource.

    Parameters:
        resource_type: The AWS resource type (e.g., "AWS::S3::Bucket")

    Returns:
        The resource schema information
    """
    if not resource_type:
        raise ClientError('Please provide a resource type (e.g., AWS::S3::Bucket)')

    return await ResourceOperations.get_resource_schema(resource_type, region)


@mcp.tool()
async def list_resources(
    resource_type: str = Field(
        description='The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> list:
    """List AWS resources of a specified type.

    Parameters:
        resource_type: The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        A list of resource identifiers
    """
    return ResourceOperations.list_resources(resource_type, region)


@mcp.tool()
async def get_resource(
    resource_type: str = Field(
        description='The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")'
    ),
    identifier: str = Field(
        description='The primary identifier of the resource to get (e.g., bucket name for S3 buckets)'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Get details of a specific AWS resource.

    Parameters:
        resource_type: The AWS resource type (e.g., "AWS::S3::Bucket")
        identifier: The primary identifier of the resource to get (e.g., bucket name for S3 buckets)
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        Detailed information about the specified resource with a consistent structure:
        {
            "identifier": The resource identifier,
            "properties": The detailed information about the resource
        }
    """
    return ResourceOperations.get_resource(resource_type, identifier, region)


@mcp.tool()
async def update_resource(
    resource_type: str = Field(
        description='The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")'
    ),
    identifier: str = Field(
        description='The primary identifier of the resource to get (e.g., bucket name for S3 buckets)'
    ),
    patch_document: list = Field(
        description='A list of RFC 6902 JSON Patch operations to apply', default=[]
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Update an AWS resource.

    Parameters:
        resource_type: The AWS resource type (e.g., "AWS::S3::Bucket")
        identifier: The primary identifier of the resource to update
        patch_document: A list of RFC 6902 JSON Patch operations to apply
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        Information about the updated resource with a consistent structure:
        {
            "status": Status of the operation ("SUCCESS", "PENDING", "FAILED", etc.)
            "resource_type": The AWS resource type
            "identifier": The resource identifier
            "is_complete": Boolean indicating whether the operation is complete
            "status_message": Human-readable message describing the result
            "request_token": A token that allows you to track long running operations via the get_resource_request_status tool
            "resource_info": Optional information about the resource properties
        }
    """
    if not resource_type:
        raise ClientError('Please provide a resource type (e.g., AWS::S3::Bucket)')

    if not identifier:
        raise ClientError('Please provide a resource identifier')

    if not patch_document:
        raise ClientError('Please provide a patch document for the update')

    return ResourceOperations.update_resource(resource_type, identifier, patch_document, region)


@mcp.tool()
async def create_resource(
    resource_type: str = Field(
        description='The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")'
    ),
    properties: dict = Field(description='A dictionary of properties for the resource'),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Create an AWS resource.

    Parameters:
        resource_type: The AWS resource type (e.g., "AWS::S3::Bucket")
        properties: A dictionary of properties for the resource
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        Information about the created resource with a consistent structure:
        {
            "status": Status of the operation ("SUCCESS", "PENDING", "FAILED", etc.)
            "resource_type": The AWS resource type
            "identifier": The resource identifier
            "is_complete": Boolean indicating whether the operation is complete
            "status_message": Human-readable message describing the result
            "request_token": A token that allows you to track long running operations via the get_resource_request_status tool
            "resource_info": Optional information about the resource properties
        }
    """
    return ResourceOperations.create_resource(resource_type, properties, region)


@mcp.tool()
async def delete_resource(
    resource_type: str = Field(
        description='The AWS resource type (e.g., "AWS::S3::Bucket", "AWS::RDS::DBInstance")'
    ),
    identifier: str = Field(
        description='The primary identifier of the resource to get (e.g., bucket name for S3 buckets)'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Delete an AWS resource.

    Parameters:
        resource_type: The AWS resource type (e.g., "AWS::S3::Bucket")
        identifier: The primary identifier of the resource to delete (e.g., bucket name for S3 buckets)
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        Information about the deletion operation with a consistent structure:
        {
            "status": Status of the operation ("SUCCESS", "PENDING", "FAILED", "NOT_FOUND", etc.)
            "resource_type": The AWS resource type
            "identifier": The resource identifier
            "is_complete": Boolean indicating whether the operation is complete
            "status_message": Human-readable message describing the result
            "request_token": A token that allows you to track long running operations via the get_resource_request_status tool
        }
    """
    return ResourceOperations.delete_resource(resource_type, identifier, region)


@mcp.tool()
async def get_resource_request_status(
    request_token: str = Field(
        description='The request_token returned from the long running operation'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Get the status of a long running operation with the request token.

    Args:
        request_token: The request_token returned from the long running operation
        region: AWS region to use (e.g., "us-east-1", "us-west-2")

    Returns:
        Detailed information about the request status structured as
        {
            "status": Status of the operation ("SUCCESS", "PENDING", "FAILED", "NOT_FOUND", etc.)
            "resource_type": The AWS resource type
            "identifier": The resource identifier
            "is_complete": Boolean indicating whether the operation is complete
            "status_message": Human-readable message describing the result
            "request_token": A token that allows you to track long running operations via the get_resource_request_status tool
            "error_code": A code associated with any errors if the request failed
            "retry_after": A duration to wait before retrying the request
        }
    """
    return ResourceOperations.get_resource_request_status(request_token, region)


@mcp.tool()
async def create_template(
    template_name: str | None = Field(None, description='Name for the generated template'),
    resources: list | None = Field(
        None,
        description="List of resources to include in the template, each with 'ResourceType' and 'ResourceIdentifier'",
    ),
    output_format: str = Field(
        'YAML', description='Output format for the template (JSON or YAML)'
    ),
    deletion_policy: str = Field(
        'RETAIN',
        description='Default DeletionPolicy for resources in the template (RETAIN, DELETE, or SNAPSHOT)',
    ),
    update_replace_policy: str = Field(
        'RETAIN',
        description='Default UpdateReplacePolicy for resources in the template (RETAIN, DELETE, or SNAPSHOT)',
    ),
    template_id: str | None = Field(
        None,
        description='ID of an existing template generation process to check status or retrieve template',
    ),
    save_to_file: str | None = Field(
        None, description='Path to save the generated template to a file'
    ),
    region: str | None = Field(
        description='The AWS region that the operation should be performed in', default=None
    ),
) -> dict:
    """Create a CloudFormation template from existing resources using the IaC Generator API.

    This tool allows you to generate CloudFormation templates from existing AWS resources
    that are not already managed by CloudFormation. The template generation process is
    asynchronous, so you can check the status of the process and retrieve the template
    once it's complete. You can pass up to 500 resources at a time.

    Examples:
    1. Start template generation for an S3 bucket:
       create_template(
           template_name="my-template",
           resources=[{"ResourceType": "AWS::S3::Bucket", "ResourceIdentifier": {"BucketName": "my-bucket"}}],
           deletion_policy="RETAIN",
           update_replace_policy="RETAIN"
       )

    2. Check status of template generation:
       create_template(template_id="arn:aws:cloudformation:us-east-1:ACCOUNT-ID:generatedtemplate/abcdef12-3456-7890-abcd-ef1234567890")

    3. Retrieve and save generated template:
       create_template(
           template_id="arn:aws:cloudformation:us-east-1:ACCOUNT-ID:generatedtemplate/abcdef12-3456-7890-abcd-ef1234567890",
           save_to_file="/path/to/template.yaml",
           output_format="YAML"
       )
    """
    return await create_template_impl(
        template_name=template_name,
        resources=resources,
        output_format=output_format,
        deletion_policy=deletion_policy,
        update_replace_policy=update_replace_policy,
        template_id=template_id,
        save_to_file=save_to_file,
        region_name=region,
    )


@mcp.tool()
async def generate_cloudformation_template(
    description: str = Field(
        description='Natural language description of the infrastructure you want to create'
    ),
    template_format: str = Field(
        default='YAML',
        description='Output format for the template (YAML or JSON)'
    ),
    region: str | None = Field(
        description='The AWS region for the template', default=None
    ),
    conversation_stage: str = Field(
        default='DISCOVERY',
        description='Conversation stage: DISCOVERY, REFINEMENT, VALIDATION, or GENERATION'
    ),
    previous_response: str | None = Field(
        description='Previous LLM response for iterative refinement', default=None
    ),
    save_to_file: str | None = Field(
        description='Optional file path to save the generated template', default=None
    ),
) -> dict:
    """Generate expert CloudFormation prompts with intelligent conversation flow.
    
    This tool creates multi-stage conversations that guide the LLM through:
    
    DISCOVERY Stage:
    - Intelligent requirements discovery with targeted questions
    - Architecture pattern detection and disambiguation
    - Implicit requirements identification
    
    REFINEMENT Stage: 
    - Requirements specification based on user responses
    - Architecture recommendations and trade-offs
    - Gap identification and follow-up questions
    
    VALIDATION Stage:
    - Final architecture review and validation
    - Security and compliance verification
    - Cost and operational considerations
    
    GENERATION Stage:
    - Production-ready CloudFormation template creation
    - Comprehensive documentation and deployment guides
    - Best practices implementation
    
    Examples:
    - "Create a web application with an ALB, ECS service, and RDS database"
    - "Set up a serverless API with Lambda, API Gateway, and DynamoDB"  
    - "Build a HIPAA-compliant data processing pipeline"
    - "Create a microservices platform with service mesh"
    """
    try:
        from awslabs.cfn_mcp_server.template_generator_clean import TemplateGenerator
        from awslabs.cfn_mcp_server.prompt_validator import PromptValidator
        
        generator = TemplateGenerator()
        validator = PromptValidator()
        
        # Enhanced analysis with new capabilities
        analysis = generator._analyze_request(description)
        
        # Add implicit requirements detection
        implicit_reqs = generator._detect_implicit_requirements(description.lower(), analysis["architecture_type"])
        analysis["implicit_requirements"] = implicit_reqs
        
        if conversation_stage == "DISCOVERY":
            # Generate intelligent discovery questions
            try:
                from .intelligent_question_generator import IntelligentQuestionGenerator
                question_gen = IntelligentQuestionGenerator()
                
                discovery_prompt = question_gen.create_discovery_prompt_with_questions(
                    description, analysis
                )
                
                result = {
                    "conversation_stage": "DISCOVERY",
                    "expert_prompt_for_claude": discovery_prompt,
                    "analysis": analysis,
                    "next_stage": "REFINEMENT",
                    "instructions": "Please answer the questions in the prompt, then call this tool again with conversation_stage='REFINEMENT' and include your responses in previous_response."
                }
            except ImportError as ie:
                return {
                    "error": f"Import error: {str(ie)}",
                    "conversation_stage": "DISCOVERY",
                    "fallback": "Using basic template generation instead"
                }
            except Exception as e:
                return {
                    "error": f"Error in discovery stage: {str(e)}",
                    "conversation_stage": "DISCOVERY"
                }
            
        elif conversation_stage == "REFINEMENT" and previous_response:
            # Create refinement prompt based on discovery responses
            refinement_prompt = generator._create_refinement_prompt_from_discovery(
                description, analysis, previous_response
            )
            
            result = {
                "conversation_stage": "REFINEMENT", 
                "expert_prompt_for_claude": refinement_prompt,
                "analysis": analysis,
                "discovery_responses": previous_response,
                "next_stage": "VALIDATION",
                "instructions": "Please create the refined specification, then call this tool again with conversation_stage='VALIDATION'."
            }
            
        elif conversation_stage == "VALIDATION" and previous_response:
            # Create validation prompt
            validation_prompt = generator._create_validation_prompt_from_refinement(
                description, analysis, previous_response
            )
            
            result = {
                "conversation_stage": "VALIDATION",
                "expert_prompt_for_claude": validation_prompt, 
                "analysis": analysis,
                "refined_spec": previous_response,
                "next_stage": "GENERATION",
                "instructions": "Please validate the architecture, then call this tool again with conversation_stage='GENERATION'."
            }
            
        elif conversation_stage == "GENERATION":
            # Generate final template creation prompt
            generation_prompt = generator._create_generation_prompt(
                description, analysis, previous_response
            )
            
            # Validate prompt quality
            validation_result = validator.validate_prompt_quality(generation_prompt, analysis)
            
            # Enhance prompt if quality is insufficient
            if validation_result["quality_level"] in ["NEEDS_IMPROVEMENT", "POOR"]:
                generation_prompt = validator.enhance_prompt_based_on_validation(
                    generation_prompt, validation_result, analysis
                )
            
            result = {
                "conversation_stage": "GENERATION",
                "expert_prompt_for_claude": generation_prompt,
                "analysis": analysis,
                "prompt_quality": validation_result,
                "final_stage": True,
                "instructions": "This is the final prompt - please generate the complete CloudFormation template and documentation."
            }
            
        else:
            # Fallback to original single-stage prompt
            result = generator.generate_enhanced_prompt(
                description=description,
                template_format=template_format,
                region=region
            )
            result["conversation_stage"] = "SINGLE_STAGE"
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": f"An error occurred in generate_cloudformation_template: {str(e)}",
            "error_details": error_details,
            "conversation_stage": conversation_stage
        }


@mcp.tool()
async def deploy_cloudformation_stack(
    stack_name: str = Field(
        description='Name for the CloudFormation stack'
    ),
    template_body: str | None = Field(
        description='CloudFormation template as a string (JSON or YAML)', default=None
    ),
    template_file: str | None = Field(
        description='Path to CloudFormation template file', default=None
    ),
    parameters: List[Dict[str, str]] | None = Field(
        description='Stack parameters as list of {"ParameterKey": "key", "ParameterValue": "value"}',
        default=None
    ),
    tags: List[Dict[str, str]] | None = Field(
        description='Stack tags as list of {"Key": "key", "Value": "value"}',
        default=None
    ),
    capabilities: List[str] | None = Field(
        description='IAM capabilities (CAPABILITY_IAM, CAPABILITY_NAMED_IAM, CAPABILITY_AUTO_EXPAND)',
        default=None
    ),
    region: str | None = Field(
        description='The AWS region for deployment', default=None
    ),
    wait_for_completion: bool = Field(
        description='Whether to wait for stack deployment to complete',
        default=True
    ),
) -> dict:
    """Deploy a CloudFormation stack with comprehensive configuration options.
    
    This tool deploys CloudFormation templates as stacks, supporting both new
    deployments and updates to existing stacks. It provides detailed progress
    monitoring and error reporting.
    
    Examples:
    1. Deploy from template file:
       deploy_cloudformation_stack(
           stack_name="my-web-app",
           template_file="./template.yaml",
           parameters=[{"ParameterKey": "Environment", "ParameterValue": "prod"}]
       )
    
    2. Deploy with inline template:
       deploy_cloudformation_stack(
           stack_name="simple-s3",
           template_body='{"Resources": {"MyBucket": {"Type": "AWS::S3::Bucket"}}}'
       )
    """
    try:
        from awslabs.cfn_mcp_server.stack_manager import StackManager
        from awslabs.cfn_mcp_server.aws_client import get_actual_region
        
        stack_manager = StackManager(get_actual_region(region))
        result = await stack_manager.deploy_stack(
            stack_name=stack_name,
            template_body=template_body,
            template_file=template_file,
            parameters=parameters or [],
            tags=tags or [],
            capabilities=capabilities or [],
            wait_for_completion=wait_for_completion
        )
        return result
    except Exception as e:
        return handle_aws_api_error(e, 'deploy_cloudformation_stack')







@mcp.tool()
async def delete_cloudformation_stack(
    stack_name: str = Field(
        description='Name of the CloudFormation stack to delete'
    ),
    region: str | None = Field(
        description='The AWS region where the stack is located', default=None
    ),
    retain_resources: List[str] | None = Field(
        description='List of logical resource IDs to retain during deletion',
        default=None
    ),
    wait_for_completion: bool = Field(
        description='Whether to wait for stack deletion to complete',
        default=True
    ),
) -> dict:
    """Delete a CloudFormation stack with optional resource retention.
    
    This tool safely deletes CloudFormation stacks with options to retain
    specific resources and monitor the deletion process.
    
    Examples:
    1. Simple deletion:
       delete_cloudformation_stack(stack_name="old-stack")
    
    2. Delete with resource retention:
       delete_cloudformation_stack(
           stack_name="app-stack",
           retain_resources=["DatabaseInstance", "S3Bucket"]
       )
    """
    try:
        from awslabs.cfn_mcp_server.stack_manager import StackManager
        from awslabs.cfn_mcp_server.aws_client import get_actual_region
        
        stack_manager = StackManager(get_actual_region(region))
        result = await stack_manager.delete_stack(
            stack_name=stack_name,
            retain_resources=retain_resources or [],
            wait_for_completion=wait_for_completion
        )
        return result
    except Exception as e:
        return handle_aws_api_error(e, 'delete_cloudformation_stack')


# Additional enhanced tools for CloudFormation best practices
@mcp.tool()
async def detect_template_capabilities(
    template_content: str = Field(
        description='CloudFormation template content (JSON or YAML)'
    ),
) -> dict:
    """Analyze a CloudFormation template and detect required capabilities."""
    try:
        import json
        import re
        
        capabilities = []
        
        # Parse template using enhanced CloudFormation parser
        try:
            from awslabs.cfn_mcp_server.cloudformation_yaml import parse_cloudformation_template
            template = parse_cloudformation_template(template_content)
        except Exception:
            # Fallback to basic detection if parsing fails
            if 'AWS::IAM::' in template_content:
                if any(name in template_content for name in ['RoleName:', 'UserName:', 'GroupName:', 'PolicyName:']):
                    return {
                        'success': True,
                        'required_capabilities': ['CAPABILITY_NAMED_IAM'],
                        'recommendations': ['CAPABILITY_NAMED_IAM is required for IAM resources with custom names']
                    }
                else:
                    return {
                        'success': True,
                        'required_capabilities': ['CAPABILITY_IAM'],
                        'recommendations': ['CAPABILITY_IAM is required for IAM resources']
                    }
            if 'Transform:' in template_content and 'AWS::Serverless' in template_content:
                return {
                    'success': True,
                    'required_capabilities': ['CAPABILITY_AUTO_EXPAND'],
                    'recommendations': ['CAPABILITY_AUTO_EXPAND is required for SAM templates']
                }
            return {
                'success': True,
                'required_capabilities': [],
                'recommendations': ['No special capabilities required']
            }
        
        # Analyze JSON template
        if isinstance(template, dict):
            resources = template.get('Resources', {})
            iam_resources = [
                'AWS::IAM::AccessKey', 'AWS::IAM::Group', 'AWS::IAM::InstanceProfile',
                'AWS::IAM::Policy', 'AWS::IAM::Role', 'AWS::IAM::User', 'AWS::IAM::UserToGroupAddition'
            ]
            
            has_iam = any(resource.get('Type') in iam_resources for resource in resources.values())
            has_named_iam = False
            
            if has_iam:
                for resource in resources.values():
                    if resource.get('Type') in iam_resources:
                        props = resource.get('Properties', {})
                        if any(prop in props for prop in ['RoleName', 'UserName', 'GroupName', 'PolicyName']):
                            has_named_iam = True
                            break
            
            if has_named_iam:
                capabilities.append('CAPABILITY_NAMED_IAM')
            elif has_iam:
                capabilities.append('CAPABILITY_IAM')
            
            # Check for transforms
            if template.get('Transform'):
                capabilities.append('CAPABILITY_AUTO_EXPAND')
        
        return {
            'success': True,
            'required_capabilities': capabilities,
            'recommendations': [
                f'Template requires capabilities: {", ".join(capabilities)}' if capabilities else 'No special capabilities required'
            ]
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to analyze template capabilities'
        }




@mcp.tool()
async def cloudformation_best_practices_guide(
    issue_description: str = Field(
        description='Description of the infrastructure issue or change needed'
    ),
) -> dict:
    """Generate expert CloudFormation best practices prompts and guidance.
    
    This tool creates comprehensive best practices prompts that help Claude provide
    expert-level guidance for CloudFormation infrastructure management. It analyzes
    the issue description and provides context-aware recommendations.
    """
    
    # Analyze the issue to provide context-aware guidance
    issue_lower = issue_description.lower()
    
    # Determine issue category for targeted guidance
    issue_category = "general"
    if any(term in issue_lower for term in ['performance', 'slow', 'timeout', 'latency']):
        issue_category = "performance"
    elif any(term in issue_lower for term in ['security', 'permission', 'access', 'vulnerability']):
        issue_category = "security"
    elif any(term in issue_lower for term in ['cost', 'expensive', 'billing', 'optimize']):
        issue_category = "cost"
    elif any(term in issue_lower for term in ['scale', 'scaling', 'capacity', 'load']):
        issue_category = "scaling"
    elif any(term in issue_lower for term in ['deploy', 'deployment', 'failed', 'error']):
        issue_category = "deployment"
    
    # Generate context-aware step-by-step solutions
    step_by_step_solutions = {
        "performance": [
            "1. ANALYZE: Use enhanced_troubleshoot_cloudformation_stack to identify performance bottlenecks",
            "2. DIAGNOSE: Use analyze_template_structure for comprehensive performance analysis", 
            "3. OPTIMIZE: Use generate_template_fixes to automatically identify performance improvements",
            "4. IMPLEMENT: Update CloudFormation template with optimized resource configurations",
            "5. DEPLOY: Use deploy_cloudformation_stack with performance monitoring enabled",
            "6. VALIDATE: Use enhanced_troubleshoot_cloudformation_stack to monitor and verify improvements"
        ],
        "security": [
            "1. AUDIT: Use analyze_template_structure to identify security vulnerabilities",
            "2. ASSESS: Use generate_template_fixes to automatically detect security issues",
            "3. REMEDIATE: Update CloudFormation template with security best practices",
            "4. VALIDATE: Use detect_template_capabilities to ensure proper IAM capabilities",
            "5. DEPLOY: Use deploy_cloudformation_stack with security validation",
            "6. MONITOR: Set up CloudTrail and Config for ongoing security monitoring"
        ],
        "deployment": [
            "1. ANALYZE: Use enhanced_troubleshoot_cloudformation_stack to understand the current state",
            "2. DIAGNOSE: Use analyze_template_structure for comprehensive issue analysis",
            "3. FIX: Use generate_template_fixes to automatically identify and apply fixes",
            "4. RETRY: Use autonomous_fix_and_deploy_stack to get guided deployment coaching",
            "5. VERIFY: Use enhanced_troubleshoot_cloudformation_stack to confirm successful deployment",
            "6. MONITOR: Use enhanced_troubleshoot_cloudformation_stack to ensure infrastructure consistency"
        ]
    }
    
    # Generate context-aware tool recommendations
    tools_by_category = {
        "performance": [
            "enhanced_troubleshoot_cloudformation_stack - Analyze current infrastructure state",
            "analyze_template_structure - Deep performance analysis with metrics",
            "generate_template_fixes - Identify performance optimization opportunities",
            "enhanced_troubleshoot_cloudformation_stack - Review resource configurations for efficiency"
        ],
        "security": [
            "analyze_template_structure - Security vulnerability assessment",
            "generate_template_fixes - Automatic security issue detection and fixes",
            "detect_template_capabilities - IAM capability validation",
            "prevent_out_of_band_changes - Maintain security through IaC consistency"
        ],
        "deployment": [
            "enhanced_troubleshoot_cloudformation_stack - Analyze current infrastructure state",
            "enhanced_troubleshoot_cloudformation_stack - Monitor deployment progress",
            "enhanced_troubleshoot_cloudformation_stack - Verify infrastructure consistency",
            "generate_template_fixes - Automatically identify and fix template issues",
            "autonomous_fix_and_deploy_stack - Get guided deployment coaching"
        ]
    }
    
    return {
        'success': True,
        'issue_description': issue_description,
        'issue_category': issue_category,
        'cloudformation_approach': '''
The CloudFormation-first approach to infrastructure management:

1. NEVER make direct AWS API calls to CloudFormation-managed resources
2. ALWAYS update the CloudFormation template first
3. Use CloudFormation tools to deploy template changes
4. Maintain infrastructure-as-code consistency
            ''',
        'step_by_step_solution': step_by_step_solutions.get(issue_category, step_by_step_solutions["deployment"]),
        'tools_to_use': tools_by_category.get(issue_category, tools_by_category["deployment"]),
        'best_practices': [],  # Could be populated with specific practices
        'troubleshooting_guidance': [],  # Could be populated with specific guidance
        'anti_patterns_to_avoid': [
            "❌ aws lambda update-function-code (for CFN-managed Lambda)",
            "❌ aws s3api put-bucket-policy (for CFN-managed S3 bucket)",
            "❌ aws iam update-role (for CFN-managed IAM role)",
            "❌ Any direct AWS service API calls to CFN-managed resources",
            "✅ Update the CloudFormation template and redeploy instead"
        ]
    }


@mcp.tool()
async def prevent_out_of_band_changes(
    proposed_aws_command: str = Field(
        description='The AWS CLI command or direct API call that the user wants to make'
    ),
    stack_name: str | None = Field(
        default=None,
        description='CloudFormation stack name that manages the resource (if known)'
    ),
) -> dict:
    """Prevent out-of-band changes to CloudFormation-managed resources."""
    
    command_lower = proposed_aws_command.lower().strip()
    
    # Detect dangerous patterns
    dangerous_patterns = [
        'aws lambda update-function',
        'aws s3api put-',
        'aws iam update-',
        'aws ec2 modify-',
        'aws rds modify-'
    ]
    
    is_dangerous = any(pattern in command_lower for pattern in dangerous_patterns)
    
    response = {
        'success': True,
        'proposed_command': proposed_aws_command,
        'is_out_of_band_change': is_dangerous,
        'severity': 'CRITICAL' if is_dangerous else 'INFO',
        'alternative_approach': '',
        'step_by_step_fix': []
    }
    
    if is_dangerous:
        response['alternative_approach'] = f'''
🚨 STOP! This is an OUT-OF-BAND CHANGE that will break CloudFormation consistency!

The command you want to run:
{proposed_aws_command}

This is WRONG because it bypasses CloudFormation and creates configuration drift.

CORRECT approach:
Update your CloudFormation template instead and redeploy the stack.
        '''
        
        response['step_by_step_fix'] = [
            "1. 🛑 DO NOT run the proposed AWS CLI command",
            "2. 📝 Update your CloudFormation template instead",
            "3. 🔍 Use detect_template_capabilities to validate the template",
            "4. 🚀 Use deploy_cloudformation_stack to apply the changes",
            "5. ✅ Use enhanced_troubleshoot_cloudformation_stack to verify the deployment"
        ]
    else:
        response['alternative_approach'] = '''
This command doesn't appear to be a direct modification of CloudFormation-managed resources.

However, remember the CloudFormation-first principle:
- Always prefer template-based infrastructure changes
- Use CloudFormation tools for operations
- Maintain infrastructure-as-code consistency
        '''
    
    return response


@mcp.tool()
async def enhanced_troubleshoot_cloudformation_stack(
    stack_name: str = Field(
        description='Name of the CloudFormation stack to troubleshoot'
    ),
    region: str | None = Field(
        description='The AWS region where the stack is located', default=None
    ),
    include_template_analysis: bool = Field(
        description='Whether to perform deep template analysis',
        default=True
    ),
    include_logs: bool = Field(
        description='Whether to analyze CloudWatch logs',
        default=True
    ),
    include_cloudtrail: bool = Field(
        description='Whether to include CloudTrail events',
        default=True
    ),
    time_window_hours: int = Field(
        description='Time window in hours for log/event collection',
        default=24
    ),
    symptoms_description: str | None = Field(
        description='Optional description of observed symptoms',
        default=None
    ),
) -> dict:
    """Perform comprehensive CloudFormation analysis - replaces get_stack_status with enhanced capabilities.
    
    🎯 USE THIS TOOL FOR ALL STACK ANALYSIS NEEDS:
    
    📊 STACK STATUS & MONITORING:
    - Real-time stack health assessment and operational status
    - Resource state analysis and dependency mapping
    - Deployment progress tracking and validation
    
    🔍 TROUBLESHOOTING & DEBUGGING:
    - Automated failure root cause analysis
    - CloudWatch logs correlation and error pattern detection
    - CloudTrail event analysis for change tracking
    - Resource-level failure diagnosis with fix recommendations
    
    🛡️ SECURITY ANALYSIS:
    - Security vulnerability scanning in templates
    - IAM policy analysis and recommendations
    - Basic security best practices assessment
    
    🔧 TEMPLATE ANALYSIS & VALIDATION:
    - Deep template structure analysis and syntax validation
    - Resource dependency cycle detection
    - Missing component identification and recommendations
    - Template best practices alignment
    
    🔄 DRIFT DETECTION GUIDANCE:
    - Smart resource-specific drift checking for failed resources
    - Out-of-band change detection with service-specific API guidance
    - Manual verification commands for suspected configuration drift
    - Integration with AWS CLI/API MCP Server for resource validation
    
    PARAMETER USAGE GUIDE:
    
    📈 For Stack Status Monitoring:
       enhanced_troubleshoot_cloudformation_stack(
           stack_name="production-app",
           include_template_analysis=True,
           include_logs=True,
           symptoms_description="Monitor deployment health"
       )
    
    🚨 For Failure Troubleshooting:
       enhanced_troubleshoot_cloudformation_stack(
           stack_name="failed-stack", 
           include_logs=True,
           include_cloudtrail=True,
           time_window_hours=6,
           symptoms_description="Stack creation failed with timeout errors"
       )
    
    🔒 For Security Analysis:
       enhanced_troubleshoot_cloudformation_stack(
           stack_name="security-stack",
           include_template_analysis=True,
           include_logs=False,
           symptoms_description="Security review of template configuration"
       )
    
    🔍 For Template Validation & Drift Check:
       enhanced_troubleshoot_cloudformation_stack(
           stack_name="template-review",
           include_logs=False,
           include_cloudtrail=False,
           symptoms_description="Validate template structure and check for out-of-band changes"
       )
    """
    try:
        from awslabs.cfn_mcp_server.enhanced_troubleshooter import EnhancedCloudFormationTroubleshooter
        from awslabs.cfn_mcp_server.aws_client import get_actual_region
        
        troubleshooter = EnhancedCloudFormationTroubleshooter(get_actual_region(region))
        result = await troubleshooter.comprehensive_analysis(
            stack_name=stack_name,
            include_template_analysis=include_template_analysis,
            include_logs=include_logs,
            include_cloudtrail=include_cloudtrail,
            time_window_hours=time_window_hours,
            symptoms_description=symptoms_description
        )
        return result
    except Exception as e:
        return handle_aws_api_error(e, 'enhanced_troubleshoot_cloudformation_stack')


@mcp.tool()
async def autonomous_fix_and_deploy_stack(
    stack_name: str = Field(
        description='Name of the CloudFormation stack to fix and deploy'
    ),
    region: str | None = Field(
        description='The AWS region where the stack is located', default=None
    ),
    auto_apply_fixes: bool = Field(
        description='Whether to automatically apply high-confidence fixes',
        default=True
    ),
    max_iterations: int = Field(
        description='Maximum fix-deploy iterations',
        default=5
    ),
    parameters: list[dict] | None = Field(
        description='Stack parameters as list of {"ParameterKey": "key", "ParameterValue": "value"}',
        default=None
    ),
    capabilities: list[str] | None = Field(
        description='IAM capabilities (e.g., ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"])',
        default=None
    ),
    tags: list[dict] | None = Field(
        description='Stack tags as list of {"Key": "key", "Value": "value"}',
        default=None
    ),
) -> str:
    """Provides expert guidance for autonomous CloudFormation deployment with interactive coaching.
    
    This tool acts as an intelligent deployment coach that guides you through:
    - Step-by-step autonomous deployment process
    - Interactive problem-solving and decision-making
    - Adaptive guidance based on stack state and results
    - Comprehensive error recovery strategies
    - Best practices coaching throughout the process
    
    The guidance includes:
    1. Initial stack assessment and template analysis
    2. Intelligent fixing recommendations with explanations
    3. Deployment monitoring and failure analysis
    4. Iterative problem-solving until success
    
    Examples:
    1. Basic autonomous deployment guidance:
       autonomous_fix_and_deploy_stack(stack_name="my-app-stack")
    
    2. Conservative approach with limited iterations:
       autonomous_fix_and_deploy_stack(
           stack_name="critical-stack",
           auto_apply_fixes=False,
           max_iterations=2
       )
    """
    try:
        from awslabs.cfn_mcp_server.aws_client import get_actual_region
        
        actual_region = get_actual_region(region)
        
        # Handle parameter counts safely
        param_count = len(parameters) if parameters and isinstance(parameters, list) else 0
        cap_list = ', '.join(capabilities) if capabilities and isinstance(capabilities, list) else 'None specified'
        tag_count = len(tags) if tags and isinstance(tags, list) else 0
        
        return f"""# 🚀 Autonomous CloudFormation Deployment Coach

I'll guide you through an autonomous deployment process for stack **{stack_name}** in region **{actual_region}**.

## 📋 Configuration Summary
- **Auto-apply fixes**: {auto_apply_fixes}
- **Max iterations**: {max_iterations}
- **Parameters**: {param_count} provided
- **Capabilities**: {cap_list}
- **Tags**: {tag_count} provided

## 🎯 Step 1: Initial Assessment
Let's start by checking the current state of your stack:

**Action Required**: Run this command first:
```
enhanced_troubleshoot_cloudformation_stack(stack_name="{stack_name}", region="{actual_region}")
```

**What to expect**:
- If stack exists: We'll analyze its current state and template
- If stack doesn't exist: We'll need to create a template first
- If stack is in failed state: We'll begin troubleshooting immediately

## 🔄 Next Steps (I'll guide you through these based on the results):

### If Stack Exists:
2. **Template Analysis**: `analyze_template_structure(template_content=current_template)`
3. **Generate Fixes**: `generate_template_fixes(template_content=template, auto_apply={auto_apply_fixes})`
4. **Deploy Updates**: `deploy_cloudformation_stack(...)`

### If Stack Doesn't Exist:
2. **Template Creation**: Use `generate_cloudformation_template(description="your requirements")`
3. **Template Analysis**: Analyze the generated template
4. **Initial Deployment**: Deploy with monitoring

### If Deployment Fails:
2. **Troubleshoot**: `enhanced_troubleshoot_cloudformation_stack(stack_name="{stack_name}")`
3. **Apply Fixes**: Based on troubleshooting results
4. **Retry**: Up to {max_iterations} iterations until success

## 🎓 Coaching Notes:
- I'll provide specific guidance after each step
- Ask questions if you're unsure about any recommendations
- I'll adapt the process based on what we discover
- We'll maintain an audit trail of all changes

**Ready to begin?** Please run the initial stack status check and share the results with me.
"""
    except Exception as e:
        return f"Error initializing autonomous deployment coach: {str(e)}"


@mcp.tool()
async def analyze_template_structure(
    template_content: str = Field(
        description='CloudFormation template content (JSON or YAML)'
    ),
    region: str | None = Field(
        description='AWS region for validation context', default=None
    ),
    analysis_focus: str | None = Field(
        description='Specific analysis focus: security, performance, compliance, architecture, cost', default=None
    ),
) -> dict:
    """Generate expert CloudFormation template analysis prompts and guidance.
    
    This tool transforms your template analysis request into comprehensive, expert-level prompts
    that help Claude perform master-level template analysis. Instead of analyzing templates 
    directly, it provides:
    
    - Enhanced prompts with security vulnerability detection
    - Architecture pattern recognition and best practices
    - Compliance framework alignment (HIPAA, PCI, SOX, GDPR)
    - Performance optimization recommendations
    - Cost optimization guidance
    - Comprehensive remediation workflows
    - Investigation commands and validation steps
    
    Examples:
    1. Comprehensive template analysis:
       analyze_template_structure(template_content=yaml_template_string)
    
    2. Security-focused analysis:
       analyze_template_structure(
           template_content=template_string,
           region="us-west-2",
           analysis_focus="security"
       )
    
    3. Compliance analysis:
       analyze_template_structure(
           template_content=template_string,
           analysis_focus="compliance"
       )
    """
    try:
        from awslabs.cfn_mcp_server.intelligent_template_analyzer import IntelligentTemplateAnalyzer
        
        # Create intelligent analyzer
        analyzer = IntelligentTemplateAnalyzer()
        
        # Generate expert analysis prompt with advanced pattern recognition
        result = analyzer.generate_intelligent_analysis_prompt(
            template_content=template_content,
            analysis_focus=analysis_focus,
            region=region
        )
        
        return result
        
    except Exception as e:
        print(f"DEBUG: Exception in analyze_template_structure: {e}")
        import traceback
        traceback.print_exc()
        return handle_aws_api_error(e, 'analyze_template_structure')


@mcp.tool()
async def generate_template_fixes(
    template_content: str = Field(
        description='CloudFormation template content (JSON or YAML)'
    ),
    auto_apply: bool = Field(
        description='Whether to automatically apply high-confidence fixes',
        default=True
    ),
    max_fixes: int = Field(
        description='Maximum number of fixes to apply',
        default=50
    ),
) -> dict:
    """Generate and optionally apply fixes for CloudFormation template issues.
    
    This tool:
    - Identifies all template issues through deep analysis
    - Generates specific fixes for each issue with confidence levels
    - Optionally applies high-confidence fixes automatically
    - Provides detailed explanation of each fix applied
    - Maintains backup of original template
    - Validates fixed template for correctness
    
    Examples:
    1. Generate and apply fixes:
       generate_template_fixes(template_content=template_string)
    
    2. Generate fixes without applying:
       generate_template_fixes(
           template_content=template_string,
           auto_apply=False
       )
    
    3. Limited fix application:
       generate_template_fixes(
           template_content=template_string,
           max_fixes=10
       )
    """
    try:
        from awslabs.cfn_mcp_server.template_analyzer import TemplateAnalyzer
        from awslabs.cfn_mcp_server.template_fixer import TemplateFixer
        import json
        import yaml
        
        # Parse template content using enhanced CloudFormation parser
        try:
            from awslabs.cfn_mcp_server.cloudformation_yaml import parse_cloudformation_template
            template = parse_cloudformation_template(template_content)
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse template: {str(e)}',
                'message': 'Template must be valid JSON or YAML'
            }
        
        # Analyze template
        analyzer = TemplateAnalyzer()
        analysis = analyzer.analyze_template(template)
        
        # Generate fixes
        fixer = TemplateFixer()
        fix_result = fixer.fix_template(
            template=template,
            analysis=analysis,
            auto_apply=auto_apply,
            max_fixes=max_fixes
        )
        
        # Convert fixed template back to original format
        fixed_template_str = template_content
        if fix_result.get('success') and fix_result.get('fixed_template'):
            if template_content.strip().startswith('{'):
                fixed_template_str = json.dumps(fix_result['fixed_template'], indent=2)
            else:
                fixed_template_str = yaml.dump(fix_result['fixed_template'], default_flow_style=False)
        
        return {
            'success': fix_result.get('success', False),
            'original_template': template_content,
            'fixed_template': fixed_template_str,
            'fixes_applied': fix_result.get('fixes_applied', []),
            'fixes_skipped': fix_result.get('fixes_skipped', []),
            'validation_result': fix_result.get('validation', {}),
            'summary': {
                'total_fixes_applied': len(fix_result.get('fixes_applied', [])),
                'total_fixes_skipped': len(fix_result.get('fixes_skipped', [])),
                'template_improved': len(fix_result.get('fixes_applied', [])) > 0
            }
        }
    except Exception as e:
        return handle_aws_api_error(e, 'generate_template_fixes')




def main():
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(
        description='An AWS Labs Model Context Protocol (MCP) server for doing common cloudformation tasks and for managing your resources in your AWS account'
    )
    parser.add_argument(
        '--readonly',
        action=argparse.BooleanOptionalAction,
        help='Prevents the MCP server from performing mutating operations',
    )

    args = parser.parse_args()
    Context.initialize(args.readonly)
    mcp.run()


if __name__ == '__main__':
    main()
