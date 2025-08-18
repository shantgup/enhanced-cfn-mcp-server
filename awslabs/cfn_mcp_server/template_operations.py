"""CloudFormation template operations."""

from typing import Dict, Any, List, Optional
from awslabs.cfn_mcp_server.aws_client import get_actual_region
from awslabs.cfn_mcp_server.input_validator import InputValidator, ValidationError
from awslabs.cfn_mcp_server.errors import ClientError


class TemplateOperations:
    """Handles CloudFormation template operations."""
    
    @staticmethod
    def generate_template(
        description: str,
        region: str = None,
        save_to_file: str = None,
        template_format: str = "YAML",
        conversation_stage: str = "DISCOVERY",
        previous_response: str = None
    ) -> Dict[str, Any]:
        """Generate CloudFormation template from natural language description."""
        try:
            # Validate inputs
            description = InputValidator.validate_description(description)
            region = InputValidator.validate_aws_region(region)
            
            region = get_actual_region(region)
            
            # Import here to avoid circular dependencies
            from awslabs.cfn_mcp_server.template_generator_clean import TemplateGenerator
            
            generator = TemplateGenerator()
            result = generator.generate_enhanced_prompt(
                description=description,
                region=region,
                template_format=template_format
            )
            
            # Handle save_to_file if requested
            if save_to_file and result.get("success"):
                try:
                    with open(save_to_file, 'w') as f:
                        f.write(result.get("enhanced_prompt", ""))
                    result["saved_to_file"] = save_to_file
                except Exception as e:
                    result["save_error"] = f"Failed to save to file: {str(e)}"
            
            return result
        except ValidationError as e:
            raise ClientError(str(e))
    
    @staticmethod
    def create_template_from_resources(
        template_name: str = None,
        resources: List[Dict[str, Any]] = None,
        template_id: str = None,
        region: str = None,
        save_to_file: str = None,
        output_format: str = "YAML",
        deletion_policy: str = "RETAIN",
        update_replace_policy: str = "RETAIN"
    ) -> Dict[str, Any]:
        """Create CloudFormation template from existing resources."""
        region = get_actual_region(region)
        
        # Import here to avoid circular dependencies
        from awslabs.cfn_mcp_server.iac_generator import create_template as create_template_impl
        
        return create_template_impl(
            template_name=template_name,
            resources=resources,
            template_id=template_id,
            region=region,
            save_to_file=save_to_file,
            output_format=output_format,
            deletion_policy=deletion_policy,
            update_replace_policy=update_replace_policy
        )
    
    @staticmethod
    def analyze_template(
        template_content: str,
        region: str = None,
        analysis_focus: str = None
    ) -> Dict[str, Any]:
        """Analyze CloudFormation template structure and provide recommendations."""
        try:
            # Validate inputs
            template_content = InputValidator.validate_template_content(template_content)
            region = InputValidator.validate_aws_region(region)
            
            region = get_actual_region(region)
            
            # Import here to avoid circular dependencies
            from awslabs.cfn_mcp_server.template_analyzer_clean import TemplateAnalyzer
            
            analyzer = TemplateAnalyzer()
            return analyzer.generate_enhanced_prompt(
                template_content=template_content,
                region=region,
                analysis_focus=analysis_focus
            )
        except ValidationError as e:
            raise ClientError(str(e))
    
    @staticmethod
    def detect_template_capabilities(template_content: str) -> Dict[str, Any]:
        """Analyze CloudFormation template and detect required capabilities."""
        # Import here to avoid circular dependencies
        from awslabs.cfn_mcp_server.template_capabilities import detect_capabilities
        
        return detect_capabilities(template_content)
    
    @staticmethod
    def generate_template_fixes(
        template_content: str,
        auto_apply: bool = True,
        max_fixes: int = 50
    ) -> Dict[str, Any]:
        """Generate and optionally apply fixes for CloudFormation template issues."""
        # Import here to avoid circular dependencies
        from awslabs.cfn_mcp_server.template_analyzer import TemplateAnalyzer
        from awslabs.cfn_mcp_server.template_fixer import TemplateFixer
        
        try:
            # Parse template
            from awslabs.cfn_mcp_server.cloudformation_yaml import parse_cloudformation_template
            template_dict = parse_cloudformation_template(template_content)
            
            # Analyze template for issues
            analyzer = TemplateAnalyzer()
            analysis_result = analyzer.analyze_template(template_dict)
            
            if not analysis_result.get("success", False):
                return {
                    "success": False,
                    "error": analysis_result.get("error", "Template analysis failed"),
                    "fixes_applied": [],
                    "fixed_template": template_content
                }
            
            # Generate fixes
            fixer = TemplateFixer()
            fixes_result = fixer.generate_fixes(
                template_dict=template_dict,
                analysis_result=analysis_result,
                auto_apply=auto_apply,
                max_fixes=max_fixes
            )
            
            return fixes_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Template fixing failed: {str(e)}",
                "fixes_applied": [],
                "fixed_template": template_content
            }
