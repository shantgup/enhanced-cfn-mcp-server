# CloudFormation Best Practices

## Template Organization

### 1. Use Nested Stacks
Break large templates into smaller, manageable nested stacks:
```yaml
NetworkStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: https://s3.amazonaws.com/templates/network.yaml
    Parameters:
      VpcCidr: 10.0.0.0/16
```

### 2. Parameter Validation
Use parameter constraints:
```yaml
Parameters:
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
    Description: EC2 instance type
```

### 3. Use Conditions
Implement conditional resource creation:
```yaml
Conditions:
  CreateProdResources: !Equals [!Ref Environment, production]

Resources:
  ProdOnlyResource:
    Type: AWS::S3::Bucket
    Condition: CreateProdResources
```

## Security Best Practices

### 1. IAM Roles and Policies
- Use least privilege principle
- Avoid hardcoded credentials
- Use IAM roles for service-to-service communication

### 2. Secrets Management
Use AWS Secrets Manager or Parameter Store:
```yaml
DatabasePassword:
  Type: AWS::SecretsManager::Secret
  Properties:
    Description: RDS Database Password
    GenerateSecretString:
      SecretStringTemplate: '{"username": "admin"}'
      GenerateStringKey: 'password'
      PasswordLength: 32
      ExcludeCharacters: '"@/\'
```

## Monitoring and Troubleshooting

### 1. Stack Events
Monitor stack events during deployment:
- Use CloudFormation console
- Set up CloudWatch alarms for stack failures
- Implement rollback triggers

### 2. Drift Detection
Regularly check for configuration drift:
```bash
aws cloudformation detect-stack-drift --stack-name MyStack
```

### 3. Change Sets
Use change sets for updates:
```bash
aws cloudformation create-change-set \
  --stack-name MyStack \
  --change-set-name MyChangeSet \
  --template-body file://template.yaml
```

## Performance Optimization

### 1. Parallel Resource Creation
CloudFormation creates resources in parallel when possible:
- Minimize dependencies between resources
- Use DependsOn only when necessary

### 2. Stack Policies
Protect critical resources:
```json
{
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "Update:Delete",
      "Resource": "LogicalResourceId/ProductionDatabase"
    }
  ]
}
```

## Cost Management

### 1. Resource Tagging
Implement consistent tagging:
```yaml
Tags:
  - Key: Environment
    Value: !Ref Environment
  - Key: Project
    Value: !Ref ProjectName
  - Key: CostCenter
    Value: !Ref CostCenter
```

### 2. Lifecycle Management
Implement automated cleanup:
- Use Lambda functions for resource cleanup
- Set up lifecycle policies for S3 and other services
- Monitor unused resources

## Error Prevention

### 1. Template Validation
Always validate templates before deployment:
```bash
aws cloudformation validate-template --template-body file://template.yaml
```

### 2. Testing Strategies
- Use separate environments for testing
- Implement infrastructure testing with tools like TaskCat
- Use linting tools like cfn-lint

### 3. Rollback Configuration
Configure automatic rollback:
```yaml
RollbackConfiguration:
  RollbackTriggers:
    - Arn: !GetAtt AliasErrorMetricGreaterThanZeroAlarm.Arn
      Type: AWS::CloudWatch::Alarm
    - Arn: !GetAtt AliasAliasErrorMetricGreaterThanZeroAlarm.Arn
      Type: AWS::CloudWatch::Alarm
```
