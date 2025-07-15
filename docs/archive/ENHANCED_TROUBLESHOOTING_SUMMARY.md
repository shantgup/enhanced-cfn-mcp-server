# Enhanced CloudFormation Troubleshooting Capabilities

## Overview

The CloudFormation MCP server has been enhanced with comprehensive troubleshooting capabilities that follow the **data-centric approach** used by the ECS MCP server. Instead of hardcoded pattern matching, it collects extensive raw data and provides it to the LLM for intelligent analysis.

## Key Improvements

### ✅ **Removed Hardcoded Patterns**
- No more regex-based error matching
- No predefined fix suggestions
- Dynamic analysis based on actual AWS data

### ✅ **Comprehensive Data Collection**
The troubleshooter now collects:

1. **Stack Information**
   - Complete stack status, events, and resources
   - Failed resource details with timestamps
   - Stack template and configuration
   - Parameters, outputs, tags, and capabilities

2. **CloudTrail Events**
   - Stack-related API calls (CreateStack, UpdateStack, DeleteStack)
   - User identity and source IP information
   - Error events with detailed error codes and messages
   - Request parameters and response elements

3. **Failed Resource Deep Analysis**
   - Service-specific analysis (IAM, EC2, Lambda, S3)
   - Resource configuration validation
   - Dependency relationship mapping
   - Common issue identification per service

4. **CloudWatch Logs**
   - Lambda function logs with error filtering
   - Custom resource logs
   - CloudFormation-related log events
   - Timestamped error messages

5. **Contextual Data**
   - Resource dependency analysis from template
   - Related stacks identification
   - Template complexity metrics
   - Account and region context

## New MCP Tools

### `troubleshoot_stack`
```python
troubleshoot_stack(
    stack_name: str,
    include_logs: bool = True,
    include_cloudtrail: bool = True,
    time_window_hours: int = 24
)
```

**Capabilities:**
- Comprehensive stack failure analysis
- Multi-service data correlation
- Timeline reconstruction of events
- Resource-specific troubleshooting insights

### `recover_stack`
```python
recover_stack(
    stack_name: str,
    auto_fix: bool = False,
    backup_template: bool = True
)
```

**Capabilities:**
- Recovery strategy recommendations
- Template backup for safety
- Basic automated recovery options
- State-specific recovery paths

## Architecture Comparison

### **Before (Hardcoded Approach)**
```
Error Message → Regex Pattern → Predefined Fix → Limited Scalability
```

### **After (Data-Centric Approach)**
```
AWS APIs → Structured Data → LLM Analysis → Dynamic Solutions
```

## Data Structure Example

The troubleshooter returns comprehensive structured data:

```json
{
  "success": true,
  "stack_name": "my-failed-stack",
  "raw_data": {
    "stack_info": {
      "stack_status": "CREATE_FAILED",
      "failed_resources": [...],
      "stack_events": [...],
      "stack_template": {...}
    },
    "cloudtrail_events": {
      "events": [...],
      "error_events": [...]
    },
    "failed_resource_analysis": {
      "detailed_analysis": [...],
      "iam_analysis": {...},
      "ec2_analysis": {...}
    },
    "cloudwatch_logs": {
      "error_logs": [...],
      "lambda_logs": [...]
    },
    "context": {
      "resource_dependencies": {...},
      "related_stacks": [...],
      "template_analysis": {...}
    }
  },
  "summary": {
    "key_issues": [...],
    "analysis_scope": {...}
  }
}
```

## Service-Specific Analysis

### **IAM Resources**
- Policy document validation
- Trust relationship analysis
- Permission boundary checks
- Role assumption issues

### **EC2 Resources**
- Security group configuration
- Subnet and VPC analysis
- Capacity and availability issues
- Network connectivity problems

### **Lambda Resources**
- Execution role validation
- Code storage limits
- Runtime configuration issues
- VPC connectivity problems

### **S3 Resources**
- Bucket naming conflicts
- Policy and ACL issues
- Cross-region replication problems
- Encryption configuration

## Benefits

1. **Scalability**: Can handle any new AWS service or error pattern
2. **Intelligence**: LLM provides contextual understanding
3. **Comprehensiveness**: Multi-dimensional failure analysis
4. **Accuracy**: Based on actual AWS data, not assumptions
5. **Flexibility**: Adapts to new failure scenarios automatically

## Usage Examples

### Basic Troubleshooting
```bash
# Via Q CLI
"Troubleshoot my CloudFormation stack named 'web-app-stack'"
```

### Advanced Analysis
```bash
# Via Q CLI
"Analyze the failed stack 'database-stack' including the last 48 hours of CloudTrail events and all related logs"
```

### Recovery Assistance
```bash
# Via Q CLI
"Help me recover the failed stack 'api-gateway-stack' and backup the template first"
```

## Integration with LLM

The structured data enables the LLM to:
- Correlate failures across multiple AWS services
- Understand resource dependencies and timing
- Provide context-aware recommendations
- Suggest specific configuration fixes
- Identify root causes vs. symptoms

This approach makes the CloudFormation troubleshooting significantly more powerful and intelligent than traditional pattern-matching systems.
