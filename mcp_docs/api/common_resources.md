# Common CloudFormation Resources Reference

## AWS::S3::Bucket

### Required Properties
None - all properties are optional

### Common Properties
```yaml
BucketName: String
BucketEncryption:
  ServerSideEncryptionConfiguration:
    - ServerSideEncryptionByDefault:
        SSEAlgorithm: AES256 | aws:kms
        KMSMasterKeyID: String
PublicAccessBlockConfiguration:
  BlockPublicAcls: Boolean
  BlockPublicPolicy: Boolean
  IgnorePublicAcls: Boolean
  RestrictPublicBuckets: Boolean
VersioningConfiguration:
  Status: Enabled | Suspended
```

### Return Values
- **Ref**: Returns the bucket name
- **Fn::GetAtt**:
  - `Arn`: ARN of the bucket
  - `DomainName`: DNS name of the bucket
  - `RegionalDomainName`: Regional DNS name

## AWS::Lambda::Function

### Required Properties
- `Code`: Function code
- `Role`: Execution role ARN
- `Runtime`: Runtime environment

### Common Properties
```yaml
FunctionName: String
Runtime: python3.9 | nodejs18.x | java11 | dotnet6 | go1.x
Handler: String
MemorySize: Integer (128-10240)
Timeout: Integer (1-900)
Environment:
  Variables:
    Key: Value
VpcConfig:
  SecurityGroupIds:
    - String
  SubnetIds:
    - String
```

### Return Values
- **Ref**: Returns the function name
- **Fn::GetAtt**:
  - `Arn`: ARN of the function
  - `Version`: Version of the function

## AWS::EC2::Instance

### Required Properties
- `ImageId`: AMI ID
- `InstanceType`: Instance type

### Common Properties
```yaml
ImageId: String
InstanceType: t3.micro | t3.small | t3.medium | m5.large | etc.
KeyName: String
SecurityGroupIds:
  - String
SubnetId: String
IamInstanceProfile: String
UserData:
  Fn::Base64: !Sub |
    #!/bin/bash
    # User data script
Tags:
  - Key: Name
    Value: String
```

### Return Values
- **Ref**: Returns the instance ID
- **Fn::GetAtt**:
  - `AvailabilityZone`: AZ of the instance
  - `PrivateDnsName`: Private DNS name
  - `PrivateIp`: Private IP address
  - `PublicDnsName`: Public DNS name
  - `PublicIp`: Public IP address

## AWS::RDS::DBInstance

### Required Properties
- `DBInstanceClass`: Instance class
- `Engine`: Database engine

### Common Properties
```yaml
DBInstanceIdentifier: String
DBInstanceClass: db.t3.micro | db.t3.small | db.r5.large | etc.
Engine: mysql | postgres | oracle-ee | sqlserver-ex
MasterUsername: String
MasterUserPassword: String
AllocatedStorage: Integer
VPCSecurityGroups:
  - String
DBSubnetGroupName: String
BackupRetentionPeriod: Integer (0-35)
MultiAZ: Boolean
StorageEncrypted: Boolean
```

### Return Values
- **Ref**: Returns the DB instance identifier
- **Fn::GetAtt**:
  - `Endpoint.Address`: Connection endpoint
  - `Endpoint.Port`: Port number

## AWS::IAM::Role

### Required Properties
- `AssumeRolePolicyDocument`: Trust policy

### Common Properties
```yaml
RoleName: String
AssumeRolePolicyDocument:
  Version: '2012-10-17'
  Statement:
    - Effect: Allow
      Principal:
        Service: lambda.amazonaws.com
      Action: sts:AssumeRole
ManagedPolicyArns:
  - String
Policies:
  - PolicyName: String
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow | Deny
          Action: String | [String]
          Resource: String | [String]
```

### Return Values
- **Ref**: Returns the role name
- **Fn::GetAtt**:
  - `Arn`: ARN of the role

## AWS::EC2::VPC

### Required Properties
- `CidrBlock`: CIDR block for the VPC

### Common Properties
```yaml
CidrBlock: String (e.g., 10.0.0.0/16)
EnableDnsHostnames: Boolean
EnableDnsSupport: Boolean
InstanceTenancy: default | dedicated
Tags:
  - Key: Name
    Value: String
```

### Return Values
- **Ref**: Returns the VPC ID
- **Fn::GetAtt**:
  - `CidrBlock`: CIDR block of the VPC
  - `DefaultNetworkAcl`: Default network ACL
  - `DefaultSecurityGroup`: Default security group
