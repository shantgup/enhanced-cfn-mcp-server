# Amazon S3 Best Practices for CloudFormation

## Security Best Practices

### 1. Bucket Encryption
Always enable encryption for S3 buckets:
```yaml
MyBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketEncryption:
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: AES256
```

### 2. Block Public Access
Configure bucket to block public access:
```yaml
MyBucket:
  Type: AWS::S3::Bucket
  Properties:
    PublicAccessBlockConfiguration:
      BlockPublicAcls: true
      BlockPublicPolicy: true
      IgnorePublicAcls: true
      RestrictPublicBuckets: true
```

### 3. Versioning
Enable versioning for data protection:
```yaml
MyBucket:
  Type: AWS::S3::Bucket
  Properties:
    VersioningConfiguration:
      Status: Enabled
```

## Performance Best Practices

### 1. Transfer Acceleration
For global applications, enable transfer acceleration:
```yaml
MyBucket:
  Type: AWS::S3::Bucket
  Properties:
    AccelerateConfiguration:
      AccelerationStatus: Enabled
```

### 2. Lifecycle Policies
Implement lifecycle policies for cost optimization:
```yaml
MyBucket:
  Type: AWS::S3::Bucket
  Properties:
    LifecycleConfiguration:
      Rules:
        - Id: TransitionToIA
          Status: Enabled
          Transitions:
            - TransitionInDays: 30
              StorageClass: STANDARD_IA
```

## Compliance Considerations

### HIPAA Compliance
- Enable encryption at rest and in transit
- Implement access logging
- Configure bucket policies with least privilege

### PCI DSS Compliance
- Use KMS encryption for sensitive data
- Implement MFA delete protection
- Regular access auditing

## Common Issues and Solutions

### Issue: Bucket name conflicts
**Solution**: Use dynamic naming with stack parameters or random suffixes

### Issue: Cross-region replication setup
**Solution**: Ensure proper IAM roles and destination bucket configuration

### Issue: Performance degradation
**Solution**: Implement request rate optimization and consider S3 Transfer Acceleration
