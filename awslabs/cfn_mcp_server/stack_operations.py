"""CloudFormation stack operations."""

from typing import Dict, Any, List, Optional
from awslabs.cfn_mcp_server.stack_manager import StackManager
from awslabs.cfn_mcp_server.aws_client import get_actual_region
from awslabs.cfn_mcp_server.input_validator import InputValidator, ValidationError
from awslabs.cfn_mcp_server.errors import ClientError


class StackOperations:
    """Handles CloudFormation stack operations."""
    
    @staticmethod
    def deploy_stack(
        stack_name: str,
        template_body: str = None,
        template_file: str = None,
        parameters: List[Dict[str, str]] = None,
        capabilities: List[str] = None,
        tags: List[Dict[str, str]] = None,
        region: str = None,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """Deploy a CloudFormation stack."""
        try:
            # Validate inputs
            stack_name = InputValidator.validate_stack_name(stack_name)
            if template_body:
                template_body = InputValidator.validate_template_content(template_body)
            region = InputValidator.validate_aws_region(region)
            
            region = get_actual_region(region)
            stack_manager = StackManager(region=region)
            
            return stack_manager.deploy_stack(
                stack_name=stack_name,
                template_body=template_body,
                template_file=template_file,
                parameters=parameters,
                capabilities=capabilities,
                tags=tags,
                wait_for_completion=wait_for_completion
            )
        except ValidationError as e:
            raise ClientError(str(e))
    
    @staticmethod
    def get_stack_status(
        stack_name: str,
        region: str = None,
        include_resources: bool = True,
        include_events: bool = True,
        analysis_focus: str = None
    ) -> Dict[str, Any]:
        """Get detailed stack status with operational analysis."""
        region = get_actual_region(region)
        stack_manager = StackManager(region=region)
        
        return stack_manager.get_stack_status(
            stack_name=stack_name,
            include_resources=include_resources,
            include_events=include_events,
            analysis_focus=analysis_focus
        )
    
    @staticmethod
    def delete_stack(
        stack_name: str,
        region: str = None,
        retain_resources: List[str] = None,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """Delete a CloudFormation stack."""
        region = get_actual_region(region)
        stack_manager = StackManager(region=region)
        
        return stack_manager.delete_stack(
            stack_name=stack_name,
            retain_resources=retain_resources,
            wait_for_completion=wait_for_completion
        )
    
    @staticmethod
    def detect_stack_drift(stack_name: str, region: str = None) -> Dict[str, Any]:
        """Detect configuration drift in a CloudFormation stack."""
        region = get_actual_region(region)
        stack_manager = StackManager(region=region)
        
        return stack_manager.detect_drift(stack_name)
    
    @staticmethod
    def troubleshoot_stack(
        stack_name: str,
        region: str = None,
        include_logs: bool = True,
        include_cloudtrail: bool = True,
        time_window_hours: int = 24,
        max_events: int = 50
    ) -> Dict[str, Any]:
        """Generate troubleshooting guidance for CloudFormation stack issues."""
        region = get_actual_region(region)
        
        # Import here to avoid circular dependencies
        from awslabs.cfn_mcp_server.troubleshooting_enhancer_clean import TroubleshootingEnhancer
        
        enhancer = TroubleshootingEnhancer()
        return enhancer.generate_troubleshooting_prompt(
            stack_name=stack_name,
            region=region,
            include_logs=include_logs,
            include_cloudtrail=include_cloudtrail,
            time_window_hours=time_window_hours,
            max_events=max_events
        )
    
    @staticmethod
    def fix_and_retry_stack(
        stack_name: str,
        region: str = None,
        auto_fix: bool = True,
        max_retries: int = 3,
        backup_template: bool = True
    ) -> Dict[str, Any]:
        """Generate fix-and-retry guidance for failed CloudFormation deployments."""
        region = get_actual_region(region)
        
        # Import here to avoid circular dependencies
        from awslabs.cfn_mcp_server.troubleshooting_enhancer_clean import TroubleshootingEnhancer
        
        enhancer = TroubleshootingEnhancer()
        return enhancer.generate_fix_and_retry_prompt(
            stack_name=stack_name,
            region=region,
            auto_fix=auto_fix,
            max_retries=max_retries,
            backup_template=backup_template
        )
