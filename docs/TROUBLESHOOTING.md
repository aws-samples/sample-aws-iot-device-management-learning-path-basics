# Troubleshooting Guide

This guide covers environment setup issues. For script-specific problems, enable debug mode when running scripts - they provide contextual error messages and guidance.

## Environment Setup

### AWS Credentials Configuration

#### Problem: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Solution**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

**Alternative methods**:
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- AWS credentials file: `~/.aws/credentials`
- IAM roles (for EC2/Lambda execution)

---

### Region Configuration

#### Problem: "Region not configured" or "You must specify a region"

**Solution**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1

# Verify region
aws configure get region
```

**Supported regions**: Any AWS region with IoT Core service availability

---

### Python Dependencies

#### Problem: "No module named 'colorama'" or similar import errors
```
ModuleNotFoundError: No module named 'colorama'
```

**Solution**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Verify installation**:
```bash
python -c "import boto3, colorama, requests; print('All dependencies installed')"
```

---

### IAM Permissions

#### Problem: "Access Denied" or "User is not authorized" errors
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Solution**: Ensure your AWS IAM user/role has the required permissions:

**Required IAM Actions**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:*",
                "iot-data:*",
                "iot-jobs-data:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:CreateBucket",
                "s3:DeleteBucket",
                "s3:ListBucket",
                "s3:PutBucketTagging",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:TagRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**Note**: For production environments, follow the principle of least privilege and restrict resources appropriately.

---

## Getting Help

### Script-Specific Issues

If you encounter issues while running scripts:

1. **Enable debug mode** - Shows detailed API calls and responses
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Read error messages** - Scripts provide contextual guidance

3. **Check educational pauses** - They explain concepts and requirements

4. **Verify prerequisites** - Most scripts require `provision_script.py` to run first

### Common Workflow

```bash
# 1. Set up environment (one-time)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Create infrastructure (run first)
python scripts/provision_script.py

# 3. Run other scripts as needed
python scripts/manage_packages.py
python scripts/create_job.py
# etc.

# 4. Clean up when done
python scripts/cleanup_script.py
```

### Additional Resources

- **README.md** - Project overview and quick start
- **Script i18n messages** - Localized guidance in your language
- **Educational pauses** - Contextual learning during script execution
- **AWS IoT Documentation** - https://docs.aws.amazon.com/iot/
