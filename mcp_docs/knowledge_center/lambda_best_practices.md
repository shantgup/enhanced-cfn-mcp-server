# AWS Lambda Best Practices for CloudFormation

## Performance Optimization

### 1. Memory and Timeout Configuration
```yaml
MyLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    MemorySize: 512  # Adjust based on workload
    Timeout: 30      # Set appropriate timeout
    ReservedConcurrencyLimit: 10  # Control concurrency
```

### 2. Environment Variables
Use environment variables for configuration:
```yaml
MyLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    Environment:
      Variables:
        LOG_LEVEL: INFO
        REGION: !Ref AWS::Region
```

## Security Best Practices

### 1. IAM Roles and Policies
Create least-privilege IAM roles:
```yaml
LambdaExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### 2. VPC Configuration
For VPC-enabled functions:
```yaml
MyLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

## Monitoring and Logging

### 1. CloudWatch Integration
```yaml
MyLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    DeadLetterConfig:
      TargetArn: !GetAtt DeadLetterQueue.Arn
    TracingConfig:
      Mode: Active  # Enable X-Ray tracing
```

### 2. Log Groups
Create dedicated log groups:
```yaml
LambdaLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub '/aws/lambda/${MyLambdaFunction}'
    RetentionInDays: 14
```

## Error Handling

### 1. Dead Letter Queues
Configure DLQ for failed invocations:
```yaml
DeadLetterQueue:
  Type: AWS::SQS::Queue
  Properties:
    MessageRetentionPeriod: 1209600  # 14 days
```

### 2. Retry Configuration
```yaml
MyLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    DeadLetterConfig:
      TargetArn: !GetAtt DeadLetterQueue.Arn
```

## Cost Optimization

### 1. Right-sizing Memory
- Monitor memory usage with CloudWatch
- Adjust memory allocation based on actual usage
- Consider ARM-based Graviton2 processors

### 2. Provisioned Concurrency
Use for predictable workloads:
```yaml
ProvisionedConcurrencyConfig:
  Type: AWS::Lambda::ProvisionedConcurrencyConfig
  Properties:
    FunctionName: !Ref MyLambdaFunction
    ProvisionedConcurrencyLimit: 10
    Qualifier: !GetAtt MyLambdaFunction.Version
```
