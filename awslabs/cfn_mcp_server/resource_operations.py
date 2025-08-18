"""Resource operations for AWS CloudFormation resources."""

from typing import Dict, Any, List
from awslabs.cfn_mcp_server.aws_client import get_aws_client, get_actual_region
from awslabs.cfn_mcp_server.cloud_control_utils import progress_event, validate_patch
from awslabs.cfn_mcp_server.errors import ClientError, handle_aws_api_error
from awslabs.cfn_mcp_server.schema_manager import schema_manager
from awslabs.cfn_mcp_server.input_validator import InputValidator, ValidationError


class ResourceOperations:
    """Handles AWS resource CRUD operations."""
    
    @staticmethod
    async def get_resource_schema(resource_type: str, region: str = None) -> Dict[str, Any]:
        """Get schema information for an AWS resource type."""
        try:
            # Validate inputs
            resource_type = InputValidator.validate_aws_resource_type(resource_type)
            region = InputValidator.validate_aws_region(region)
            
            region = get_actual_region(region)
            sm = schema_manager()
            return await sm.get_schema(resource_type, region)
        except ValidationError as e:
            raise ClientError(str(e))
        except Exception as e:
            raise handle_aws_api_error(e)
            print(f"DEBUG: Exception in get_resource_schema: {e}")
            raise handle_aws_api_error(e)
    
    @staticmethod
    def list_resources(resource_type: str, region: str = None) -> List[str]:
        """List AWS resources of a specified type."""
        try:
            # Validate inputs
            resource_type = InputValidator.validate_aws_resource_type(resource_type)
            region = InputValidator.validate_aws_region(region)
            
            region = get_actual_region(region)
            client = get_aws_client('cloudcontrol', region)
            
            paginator = client.get_paginator('list_resources')
            page_iterator = paginator.paginate(TypeName=resource_type)
            
            identifiers = []
            for page in page_iterator:
                for resource in page.get('ResourceDescriptions', []):
                    identifiers.append(resource['Identifier'])
            
            return identifiers
        except ValidationError as e:
            raise ClientError(str(e))
        except Exception as e:
            raise handle_aws_api_error(e)
    
    @staticmethod
    def get_resource(resource_type: str, identifier: str, region: str = None) -> Dict[str, Any]:
        """Get details of a specific AWS resource."""
        try:
            region = get_actual_region(region)
            client = get_aws_client('cloudcontrol', region)
            
            response = client.get_resource(
                TypeName=resource_type,
                Identifier=identifier
            )
            
            return {
                "identifier": identifier,
                "properties": response['ResourceDescription']['Properties']
            }
        except Exception as e:
            raise handle_aws_api_error(e)
    
    @staticmethod
    def create_resource(resource_type: str, properties: Dict[str, Any], region: str = None) -> Dict[str, Any]:
        """Create an AWS resource."""
        try:
            # Validate inputs
            resource_type = InputValidator.validate_aws_resource_type(resource_type)
            properties = InputValidator.validate_properties(properties)
            region = InputValidator.validate_aws_region(region)
            
            region = get_actual_region(region)
            client = get_aws_client('cloudcontrol', region)
            
            response = client.create_resource(
                TypeName=resource_type,
                DesiredState=str(properties)
            )
            
            return progress_event(response['ProgressEvent'])
        except ValidationError as e:
            raise ClientError(str(e))
        except Exception as e:
            raise handle_aws_api_error(e)
    
    @staticmethod
    def update_resource(resource_type: str, identifier: str, patch_document: List[Dict[str, Any]], region: str = None) -> Dict[str, Any]:
        """Update an AWS resource."""
        try:
            region = get_actual_region(region)
            
            # Validate patch document
            if patch_document:
                validate_patch(patch_document)
            
            client = get_aws_client('cloudcontrol', region)
            
            response = client.update_resource(
                TypeName=resource_type,
                Identifier=identifier,
                PatchDocument=str(patch_document) if patch_document else None
            )
            
            return progress_event(response['ProgressEvent'])
        except Exception as e:
            raise handle_aws_api_error(e)
    
    @staticmethod
    def delete_resource(resource_type: str, identifier: str, region: str = None) -> Dict[str, Any]:
        """Delete an AWS resource."""
        try:
            region = get_actual_region(region)
            client = get_aws_client('cloudcontrol', region)
            
            response = client.delete_resource(
                TypeName=resource_type,
                Identifier=identifier
            )
            
            return progress_event(response['ProgressEvent'])
        except Exception as e:
            raise handle_aws_api_error(e)
    
    @staticmethod
    def get_resource_request_status(request_token: str, region: str = None) -> Dict[str, Any]:
        """Get the status of a long running operation."""
        try:
            region = get_actual_region(region)
            client = get_aws_client('cloudcontrol', region)
            
            response = client.get_resource_request_status(
                RequestToken=request_token
            )
            
            return progress_event(response['ProgressEvent'])
        except Exception as e:
            raise handle_aws_api_error(e)
