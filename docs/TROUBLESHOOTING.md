# Troubleshooting Guide

This guide helps you work through environment setup issues. If you run into script-specific problems, try enabling debug mode when running scripts - it'll give you helpful error messages and guidance along the way.

## Environment Setup

### AWS Credentials Configuration

#### Problem: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Here's how to fix it**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

**You can also try these alternative methods**:
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- AWS credentials file: `~/.aws/credentials`
- IAM roles (if you're running on EC2 or Lambda)

---

### Region Configuration

#### Problem: "Region not configured" or "You must specify a region"

**Here's how to fix it**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1

# Verify region
aws configure get region
```

**Works with these regions**: Any AWS region where IoT Core is available

---

### Python Dependencies

#### Problem: "No module named 'colorama'" or similar import errors
```
ModuleNotFoundError: No module named 'colorama'
```

**Here's how to fix it**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**You can check your installation like this**:
```bash
python -c "import boto3, colorama, requests; print('All dependencies installed')"
```

---

### IAM Permissions

#### Problem: "Access Denied" or "User is not authorized" errors
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Here's how to fix it**: Make sure your AWS IAM user or role has the permissions it needs:

**What you'll need - IAM Actions**:
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

**Quick note**: For production environments, it's a good idea to follow the principle of least privilege and restrict resources as needed.

---

## Getting Help

### Script-Specific Issues

If you run into issues while running scripts, here are some helpful tips:

1. **Enable debug mode** - It'll show you detailed API calls and responses
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Read error messages** - The scripts provide helpful contextual guidance

3. **Check educational pauses** - They explain concepts and requirements as you go

4. **Check prerequisites** - Most scripts need `provision_script.py` to run first

### Here's a typical workflow

```bash
# 1. Set up your environment (just once)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Create your infrastructure (run this first)
python scripts/provision_script.py

# 3. Run other scripts as you need them
python scripts/manage_packages.py
python scripts/create_job.py
# etc.

# 4. Clean up when you're done
python scripts/cleanup_script.py
```

### More helpful resources

- **README.md** - Project overview and quick start guide
- **Script i18n messages** - Helpful guidance in your language
- **Educational pauses** - Learn as you go during script execution
- **AWS IoT Documentation** - https://docs.aws.amazon.com/iot/
