"""Health check framework for CloudFormation MCP server components."""

import os
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime


class HealthCheckResult:
    """Result of a health check operation."""
    
    def __init__(self, name: str, status: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.name = name
        self.status = status  # "HEALTHY", "UNHEALTHY", "WARNING"
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class HealthChecker:
    """Performs health checks on system components."""
    
    def check_aws_connectivity(self, region: str = "us-east-1") -> HealthCheckResult:
        """Check AWS connectivity and basic permissions."""
        try:
            from awslabs.cfn_mcp_server.aws_client import get_aws_client
            
            # Test STS connectivity (basic AWS access)
            sts_client = get_aws_client('sts', region)
            identity = sts_client.get_caller_identity()
            
            return HealthCheckResult(
                name="AWS Connectivity",
                status="HEALTHY",
                message=f"Connected as {identity.get('Arn', 'Unknown')}",
                details={"account": identity.get('Account'), "region": region}
            )
        except Exception as e:
            return HealthCheckResult(
                name="AWS Connectivity",
                status="UNHEALTHY",
                message=f"AWS connection failed: {str(e)}"
            )
    
    def check_configuration(self) -> HealthCheckResult:
        """Check configuration manager health."""
        try:
            from awslabs.cfn_mcp_server.config import get_config_manager
            
            config_manager = get_config_manager()
            
            if not config_manager.is_initialized():
                return HealthCheckResult(
                    name="Configuration",
                    status="UNHEALTHY",
                    message="Configuration manager not initialized"
                )
            
            # Test basic config access
            region = config_manager.get_config('aws.default_region', 'us-east-1')
            
            return HealthCheckResult(
                name="Configuration",
                status="HEALTHY",
                message="Configuration loaded successfully",
                details={"default_region": region}
            )
        except Exception as e:
            return HealthCheckResult(
                name="Configuration",
                status="UNHEALTHY",
                message=f"Configuration check failed: {str(e)}"
            )
    
    def check_schema_manager(self) -> HealthCheckResult:
        """Check schema manager health."""
        try:
            from awslabs.cfn_mcp_server.schema_manager import get_schema_manager
            
            schema_manager = get_schema_manager()
            
            if not schema_manager.is_initialized():
                return HealthCheckResult(
                    name="Schema Manager",
                    status="UNHEALTHY",
                    message="Schema manager not initialized"
                )
            
            # Check cache directory
            cache_exists = schema_manager.cache_dir.exists()
            
            return HealthCheckResult(
                name="Schema Manager",
                status="HEALTHY",
                message="Schema manager operational",
                details={"cache_directory_exists": cache_exists}
            )
        except Exception as e:
            return HealthCheckResult(
                name="Schema Manager",
                status="UNHEALTHY",
                message=f"Schema manager check failed: {str(e)}"
            )
    
    def check_file_system(self) -> HealthCheckResult:
        """Check file system access and permissions."""
        try:
            # Test write access to temp directory
            with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
                tmp_file.write(b"health check test")
                tmp_file.flush()
            
            # Check current directory write access
            current_dir = os.getcwd()
            writable = os.access(current_dir, os.W_OK)
            
            return HealthCheckResult(
                name="File System",
                status="HEALTHY",
                message="File system access verified",
                details={"current_dir_writable": writable, "temp_access": True}
            )
        except Exception as e:
            return HealthCheckResult(
                name="File System",
                status="UNHEALTHY",
                message=f"File system check failed: {str(e)}"
            )
    
    def check_context(self) -> HealthCheckResult:
        """Check context initialization."""
        try:
            from awslabs.cfn_mcp_server.context import Context
            
            # Test context access
            readonly = Context.readonly_mode()
            
            return HealthCheckResult(
                name="Context",
                status="HEALTHY",
                message="Context initialized successfully",
                details={"readonly_mode": readonly}
            )
        except Exception as e:
            return HealthCheckResult(
                name="Context",
                status="UNHEALTHY",
                message=f"Context check failed: {str(e)}"
            )
    
    def run_all_checks(self, region: str = "us-east-1") -> Dict[str, Any]:
        """Run all health checks and return comprehensive status."""
        checks = [
            self.check_configuration(),
            self.check_context(),
            self.check_file_system(),
            self.check_aws_connectivity(region),
            self.check_schema_manager(),
        ]
        
        results = [check.to_dict() for check in checks]
        
        # Determine overall status
        unhealthy_count = sum(1 for check in checks if check.status == "UNHEALTHY")
        warning_count = sum(1 for check in checks if check.status == "WARNING")
        
        if unhealthy_count > 0:
            overall_status = "UNHEALTHY"
            overall_message = f"{unhealthy_count} component(s) unhealthy"
        elif warning_count > 0:
            overall_status = "WARNING"
            overall_message = f"{warning_count} component(s) have warnings"
        else:
            overall_status = "HEALTHY"
            overall_message = "All components healthy"
        
        return {
            "overall_status": overall_status,
            "overall_message": overall_message,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results,
            "summary": {
                "total": len(checks),
                "healthy": sum(1 for check in checks if check.status == "HEALTHY"),
                "warning": warning_count,
                "unhealthy": unhealthy_count
            }
        }


# Singleton instance
_health_checker = HealthChecker()

def get_health_checker() -> HealthChecker:
    """Get the singleton health checker instance."""
    return _health_checker
