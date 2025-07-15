#!/usr/bin/env python3
"""
Example usage of the Enhanced CloudFormation MCP Server capabilities.

This script demonstrates how to use the new CloudFormation template generation,
deployment, troubleshooting, and auto-fix features.
"""

import asyncio
import json
from awslabs.cfn_mcp_server.template_generator import TemplateGenerator
from awslabs.cfn_mcp_server.stack_manager import StackManager
from awslabs.cfn_mcp_server.troubleshooter import CloudFormationTroubleshooter


async def example_template_generation():
    """Example of generating CloudFormation templates from natural language."""
    print("=== Template Generation Example ===")
    
    generator = TemplateGenerator('us-east-1')
    
    # Generate a simple web application template
    description = "Create a web application with an Application Load Balancer, Lambda function, and DynamoDB table"
    
    result = await generator.generate_from_description(
        description=description,
        template_format='YAML',
        save_to_file='web-app-template.yaml'
    )
    
    if result['success']:
        print(f"✅ Template generated successfully!")
        print(f"📄 Resources identified: {', '.join(result['resources_identified'])}")
        print(f"💾 Template saved to: {result['file_saved']}")
        print(f"💡 Suggestions: {len(result['suggestions'])} recommendations provided")
    else:
        print(f"❌ Template generation failed: {result['error']}")


async def example_stack_deployment():
    """Example of deploying a CloudFormation stack."""
    print("\n=== Stack Deployment Example ===")
    
    stack_manager = StackManager('us-east-1')
    
    # Simple S3 bucket template
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Simple S3 bucket example",
        "Resources": {
            "MyBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": {"Fn::Sub": "${AWS::StackName}-example-bucket"},
                    "VersioningConfiguration": {"Status": "Enabled"}
                }
            }
        },
        "Outputs": {
            "BucketName": {
                "Description": "Name of the created S3 bucket",
                "Value": {"Ref": "MyBucket"}
            }
        }
    }
    
    result = await stack_manager.deploy_stack(
        stack_name='example-s3-stack',
        template_body=json.dumps(template),
        tags=[
            {'Key': 'Environment', 'Value': 'Development'},
            {'Key': 'Project', 'Value': 'MCP-Demo'}
        ],
        wait_for_completion=False  # Set to True in real usage
    )
    
    if result['success']:
        print(f"✅ Stack deployment initiated!")
        print(f"🏗️  Operation: {result['operation']}")
        print(f"📋 Stack Name: {result['stack_name']}")
        print(f"🆔 Stack ID: {result['stack_id']}")
    else:
        print(f"❌ Stack deployment failed: {result['error']}")


async def example_stack_status():
    """Example of getting stack status."""
    print("\n=== Stack Status Example ===")
    
    stack_manager = StackManager('us-east-1')
    
    result = await stack_manager.get_stack_status(
        stack_name='example-s3-stack',
        include_resources=True,
        include_events=True
    )
    
    if result['success']:
        print(f"✅ Stack status retrieved!")
        print(f"📊 Status: {result['stack_status']}")
        print(f"📅 Created: {result.get('creation_time', 'N/A')}")
        print(f"🔧 Resources: {len(result.get('resources', []))} resources")
        print(f"📝 Events: {len(result.get('events', []))} recent events")
    else:
        print(f"❌ Failed to get stack status: {result['error']}")


async def example_troubleshooting():
    """Example of troubleshooting a CloudFormation stack."""
    print("\n=== Troubleshooting Example ===")
    
    troubleshooter = CloudFormationTroubleshooter('us-east-1')
    
    # This would typically be used on a failed stack
    result = await troubleshooter.analyze_stack(
        stack_name='example-s3-stack',
        include_logs=True,
        max_events=20
    )
    
    if result['success']:
        print(f"✅ Stack analysis completed!")
        print(f"⚠️  Severity: {result['severity']}")
        print(f"🔍 Issues found: {len(result['issues_found'])}")
        print(f"💡 Recommendations: {len(result['recommendations'])}")
        
        if result['recommendations']:
            print("\n📋 Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"   {i}. {rec}")
    else:
        print(f"❌ Stack analysis failed: {result['error']}")


async def example_cleanup():
    """Example of cleaning up resources."""
    print("\n=== Cleanup Example ===")
    
    stack_manager = StackManager('us-east-1')
    
    result = await stack_manager.delete_stack(
        stack_name='example-s3-stack',
        wait_for_completion=False  # Set to True in real usage
    )
    
    if result['success']:
        print(f"✅ Stack deletion initiated!")
        print(f"🗑️  Operation: {result['operation']}")
        print(f"📋 Stack Name: {result['stack_name']}")
    else:
        print(f"❌ Stack deletion failed: {result['error']}")


async def main():
    """Run all examples."""
    print("🚀 Enhanced CloudFormation MCP Server Examples")
    print("=" * 50)
    
    try:
        await example_template_generation()
        await example_stack_deployment()
        await example_stack_status()
        await example_troubleshooting()
        await example_cleanup()
        
        print("\n✨ All examples completed!")
        print("\n📝 Note: Some operations were run with wait_for_completion=False")
        print("   In real usage, you might want to wait for operations to complete.")
        
    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        print("💡 Make sure you have valid AWS credentials configured.")


if __name__ == "__main__":
    asyncio.run(main())
