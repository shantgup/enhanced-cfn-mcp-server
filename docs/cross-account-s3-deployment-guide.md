# Cross-Account S3 Bucket Setup - Deployment Guide

## Overview

This CloudFormation template creates a secure, production-ready cross-account S3 bucket setup that allows controlled access from multiple AWS accounts while maintaining enterprise-grade security, compliance, and monitoring.

## Architecture Components

### Core Resources
- **S3 Bucket**: Main storage bucket with versioning and lifecycle policies
- **KMS Key**: Customer-managed encryption key with automatic rotation
- **IAM Role**: Cross-account access role with least privilege permissions
- **CloudTrail**: API logging for audit and compliance
- **CloudWatch**: Monitoring and alerting for security events

### Security Features
- **Encryption**: KMS encryption for data at rest and in transit
- **Access Control**: Resource-based policies with IP restrictions
- **Audit Logging**: Comprehensive CloudTrail logging
- **Monitoring**: CloudWatch alarms for unauthorized access
- **Compliance**: SOX-compliant configuration

## Prerequisites

1. **AWS CLI Configuration**
   ```bash
   aws configure list
   aws sts get-caller-identity
   ```

2. **Required Permissions**
   - CloudFormation full access
   - S3 full access
   - IAM role creation
   - KMS key management
   - CloudTrail management

3. **Account Information**
   - List of trusted AWS account IDs
   - Desired bucket name (globally unique)
   - Target AWS region

## Deployment Steps

### 1. Template Validation

```bash
# Validate template syntax
aws cloudformation validate-template \
  --template-body file://cross-account-s3-template.yaml

# Check for drift detection
aws cloudformation detect-stack-drift \
  --stack-name cross-account-s3-stack
```

### 2. Parameter Configuration

Create a parameters file (`parameters.json`):

```json
[
  {
    "ParameterKey": "BucketName",
    "ParameterValue": "my-company-cross-account-data"
  },
  {
    "ParameterKey": "TrustedAccountIds",
    "ParameterValue": "123456789012,987654321098"
  },
  {
    "ParameterKey": "CrossAccountRoleName",
    "ParameterValue": "CrossAccountS3AccessRole"
  },
  {
    "ParameterKey": "Environment",
    "ParameterValue": "production"
  },
  {
    "ParameterKey": "KMSKeyRotation",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "CloudTrailRetentionDays",
    "ParameterValue": "90"
  },
  {
    "ParameterKey": "AccessLoggingEnabled",
    "ParameterValue": "true"
  }
]
```

### 3. Stack Deployment

```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name cross-account-s3-stack \
  --template-body file://cross-account-s3-template.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --tags Key=Environment,Value=production Key=Purpose,Value=CrossAccountStorage

# Monitor deployment progress
aws cloudformation describe-stack-events \
  --stack-name cross-account-s3-stack \
  --query 'StackEvents[?ResourceStatus!=`CREATE_COMPLETE`]'

# Check stack status
aws cloudformation describe-stacks \
  --stack-name cross-account-s3-stack \
  --query 'Stacks[0].StackStatus'
```

### 4. Post-Deployment Verification

```bash
# Verify bucket creation
aws s3 ls | grep your-bucket-name

# Check KMS key
aws kms describe-key --key-id alias/your-bucket-name-s3-key

# Verify CloudTrail
aws cloudtrail describe-trails \
  --trail-name-list your-bucket-name-cloudtrail

# Test cross-account role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT-ID:role/CrossAccountS3AccessRole \
  --role-session-name TestSession \
  --external-id your-bucket-name-external-id
```

## Cross-Account Access Configuration

### For Trusted Accounts

1. **Create IAM Policy** in the trusted account:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::BUCKET-OWNER-ACCOUNT:role/CrossAccountS3AccessRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "your-bucket-name-external-id"
        }
      }
    }
  ]
}
```

2. **Attach Policy** to users/roles that need access

3. **Test Access**:

```bash
# Assume role
aws sts assume-role \
  --role-arn arn:aws:iam::BUCKET-OWNER-ACCOUNT:role/CrossAccountS3AccessRole \
  --role-session-name CrossAccountAccess \
  --external-id your-bucket-name-external-id

# Use temporary credentials
export AWS_ACCESS_KEY_ID=<from-assume-role-output>
export AWS_SECRET_ACCESS_KEY=<from-assume-role-output>
export AWS_SESSION_TOKEN=<from-assume-role-output>

# Test S3 access
aws s3 ls s3://your-bucket-name/
aws s3 cp test-file.txt s3://your-bucket-name/
```

## Security Configuration

### Encryption Details
- **At Rest**: KMS encryption with customer-managed keys
- **In Transit**: HTTPS/TLS enforced via bucket policy
- **Key Rotation**: Automatic annual rotation enabled

### Access Controls
- **IP Restrictions**: Limited to private IP ranges
- **External ID**: Required for role assumption
- **Least Privilege**: Minimal necessary permissions

### Monitoring and Alerting
- **CloudTrail**: All API calls logged
- **CloudWatch**: Unauthorized access alarms
- **SNS**: Security alert notifications

## Cost Optimization

### Storage Classes
- **Standard**: First 30 days
- **Standard-IA**: 30-90 days
- **Glacier**: 90-365 days
- **Deep Archive**: 365+ days

### Cost Monitoring
```bash
# Check S3 storage metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=your-bucket-name \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Average
```

## Maintenance and Operations

### Regular Tasks
1. **Monthly**: Review access logs and CloudTrail events
2. **Quarterly**: Audit cross-account permissions
3. **Annually**: Review and update security policies

### Backup and Recovery
- **Versioning**: Enabled with 30-day retention
- **Cross-Region Replication**: Consider for critical data
- **Point-in-Time Recovery**: Available via versioning

### Troubleshooting

#### Common Issues

1. **Access Denied Errors**
   - Verify external ID matches
   - Check IP address restrictions
   - Confirm role trust policy

2. **Encryption Errors**
   - Ensure KMS key permissions
   - Verify encryption headers
   - Check key policy for cross-account access

3. **CloudTrail Issues**
   - Verify S3 bucket permissions
   - Check CloudWatch Logs role
   - Confirm trail configuration

#### Diagnostic Commands

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket your-bucket-name

# Verify KMS key policy
aws kms get-key-policy --key-id alias/your-bucket-name-s3-key --policy-name default

# Review CloudTrail status
aws cloudtrail get-trail-status --name your-bucket-name-cloudtrail

# Check CloudWatch alarms
aws cloudwatch describe-alarms --alarm-names your-bucket-name-unauthorized-access
```

## Compliance and Audit

### SOX Compliance Features
- **Audit Trail**: Complete API logging
- **Access Control**: Role-based permissions
- **Data Integrity**: Versioning and encryption
- **Monitoring**: Real-time security alerts

### Audit Reports
```bash
# Generate access report
aws s3api get-bucket-logging --bucket your-bucket-name

# CloudTrail event history
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=your-bucket-name \
  --start-time 2024-01-01 \
  --end-time 2024-01-31
```

## Stack Updates

### Safe Update Process
1. **Test in Development**: Deploy changes to dev environment first
2. **Backup Configuration**: Export current stack template
3. **Change Sets**: Use CloudFormation change sets for preview
4. **Rolling Updates**: Update non-critical resources first

```bash
# Create change set
aws cloudformation create-change-set \
  --stack-name cross-account-s3-stack \
  --template-body file://updated-template.yaml \
  --parameters file://updated-parameters.json \
  --change-set-name update-$(date +%Y%m%d-%H%M%S) \
  --capabilities CAPABILITY_NAMED_IAM

# Review changes
aws cloudformation describe-change-set \
  --change-set-name update-$(date +%Y%m%d-%H%M%S) \
  --stack-name cross-account-s3-stack

# Execute change set
aws cloudformation execute-change-set \
  --change-set-name update-$(date +%Y%m%d-%H%M%S) \
  --stack-name cross-account-s3-stack
```

## Emergency Procedures

### Security Incident Response
1. **Immediate**: Disable cross-account role
2. **Investigation**: Review CloudTrail logs
3. **Containment**: Update bucket policies
4. **Recovery**: Restore from backups if needed

### Disaster Recovery
1. **Data Recovery**: Use versioning to restore objects
2. **Infrastructure**: Redeploy from CloudFormation template
3. **Access Restoration**: Reconfigure cross-account permissions

This template provides a comprehensive, secure foundation for cross-account S3 access with enterprise-grade security, monitoring, and compliance features.
