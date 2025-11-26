# Troubleshooting Guide

This document provides solutions for common issues encountered when using the AWS IoT Device Management scripts.

## Common Issues

### AWS Configuration Issues

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

#### Problem: "Access Denied" errors
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Solution**: Ensure your AWS IAM user/role has the required permissions:
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
                "iam:GetRole",
                "iam:PassRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Problem: "Region not configured"
```
You must specify a region
```

**Solution**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

### Script Execution Issues

#### Problem: "No module named 'colorama'"
```
ModuleNotFoundError: No module named 'colorama'
```

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install colorama>=0.4.4 requests>=2.25.1
```

#### Problem: Scripts hang or timeout
**Symptoms**: Scripts appear to freeze during execution

**Solution**:
1. Enable debug mode to see what's happening:
   ```bash
   # When prompted, choose 'y' for debug mode
   🔧 Enable debug mode? [y/N]: y
   ```

2. Check AWS service limits and throttling
3. Reduce parallel workers if needed
4. Check network connectivity

#### Problem: "Thing type deletion requires 5-minute wait"
```
InvalidRequestException: Thing type cannot be deleted until 5 minutes after deprecation
```

**Solution**: This is expected behavior. The cleanup script handles this automatically by:
1. Deprecating thing types first
2. Waiting 5 minutes
3. Then deleting them

### Resource Creation Issues

#### Problem: "Thing group already exists"
```
ResourceAlreadyExistsException: Thing group already exists
```

**Solution**: This is usually harmless. Scripts check for existing resources and skip creation if they already exist.

#### Problem: "S3 bucket name already taken"
```
BucketAlreadyExists: The requested bucket name is not available
```

**Solution**: Scripts use timestamps to ensure unique bucket names. If this occurs:
1. Wait a few seconds and retry
2. Check if you have existing buckets with similar names

#### Problem: "Package version already exists"
```
ConflictException: Package version already exists
```

**Solution**: Scripts handle this by checking existing versions first. If you need to update:
1. Use a new version number
2. Or delete the existing version first

### Job Execution Issues

#### Problem: "No active jobs found"
```
❌ No active jobs found
```

**Solution**:
1. Create a job first using `scripts/create_job.py`
2. Verify job status: `scripts/explore_jobs.py`
3. Check if jobs were cancelled or completed

#### Problem: "Failed to download artifact"
```
❌ Failed to download artifact: HTTP 403 Forbidden
```

**Solution**:
1. Check AWS IAM role permissions for AWS IoT Jobs
2. Verify presigned URL configuration
3. Ensure S3 bucket and objects exist
4. Check if presigned URLs have expired (1-hour limit)

#### Problem: "Job execution not found"
```
ResourceNotFoundException: Job execution not found
```

**Solution**:
1. Verify job ID and thing name are correct
2. Check if the device is in the target thing groups
3. Ensure the job is still active (not completed/cancelled)

### Fleet Indexing Issues

#### Problem: "Fleet Indexing queries return no results"
```
ℹ️ No devices currently match this query
```

**Solution**:
1. Wait for Fleet Indexing to complete (can take several minutes)
2. Verify Fleet Indexing is enabled
3. Check query syntax
4. Ensure devices have the expected attributes/shadows

#### Problem: "Invalid Fleet Indexing query"
```
InvalidRequestException: Invalid query string
```

**Solution**: Check query syntax. Common issues:
- Use `attributes.fieldName` for device attributes
- Use `shadow.reported.fieldName` for classic shadows
- Use `shadow.name.\\$package.reported.fieldName` for named shadows
- Escape special characters properly

### Performance Issues

#### Problem: "Rate limiting errors"
```
ThrottlingException: Rate exceeded
```

**Solution**: Scripts have built-in rate limiting, but if you encounter this:
1. Enable debug mode to see which API is being throttled
2. Reduce parallel workers in the script
3. Add delays between operations
4. Check AWS service limits for your account

#### Problem: "Scripts running slowly"
**Symptoms**: Operations take much longer than expected

**Solution**:
1. Check network connectivity
2. Verify AWS region is geographically close
3. Enable debug mode to identify bottlenecks
4. Consider reducing batch sizes

### Data Consistency Issues

#### Problem: "Device shadows not updating"
```
❌ Failed to update device shadow
```

**Solution**:
1. Check IoT Data endpoint configuration
2. Verify device/thing exists
3. Ensure proper JSON formatting in shadow updates
4. Check AWS IAM permissions for shadow operations

#### Problem: "Package configuration not working"
```
❌ Failed to update global package configuration
```

**Solution**:
1. Verify IoTPackageConfigRole exists and has proper permissions
2. Check if role ARN is correctly formatted
3. Ensure package configuration is enabled in your region

## Debug Mode Usage

Enable debug mode in any script for detailed troubleshooting:

```bash
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

Debug mode shows:
- All AWS CLI commands being executed
- API request parameters
- Full API responses
- Error details and stack traces

## Log Analysis

### Successful Operations
Look for these indicators:
- ✅ Green checkmarks for successful operations
- Progress counters showing completion
- "completed successfully" messages

### Warning Signs
Watch for these patterns:
- ⚠️ Yellow warnings (usually non-critical)
- "already exists" messages (usually harmless)
- Timeout warnings

### Error Patterns
Common error indicators:
- ❌ Red X marks for failures
- "Failed to" messages
- Exception stack traces
- HTTP error codes (403, 404, 500)

## Recovery Procedures

### Partial Provisioning Failure
If provisioning fails partway through:

1. **Check what was created**:
   ```bash
   python scripts/explore_jobs.py
   # Option 1: List all jobs
   ```

2. **Clean up if needed**:
   ```bash
   python scripts/cleanup_script.py
   # Option 1: ALL resources
   ```

3. **Retry provisioning**:
   ```bash
   python scripts/provision_script.py
   # Scripts handle existing resources gracefully
   ```

### Failed Job Recovery
If a job fails during execution:

1. **Check job status**:
   ```bash
   python scripts/explore_jobs.py
   # Option 2: Explore specific job
   ```

2. **Check individual failures**:
   ```bash
   python scripts/explore_jobs.py
   # Option 3: Explore job execution
   ```

3. **Rollback if needed**:
   ```bash
   python scripts/manage_packages.py
   # Select: 10. Revert Device Versions
   # Enter thing type and previous version
   ```

### Resource Cleanup Issues
If cleanup fails:

1. **Try selective cleanup**:
   ```bash
   python scripts/cleanup_script.py
   # Option 2: Things only (then try groups)
   ```

2. **Manual cleanup via AWS Console**:
   - AWS IoT Core → Manage → Things
   - AWS IoT Core → Manage → Thing groups
   - AWS IoT Core → Manage → Thing types
   - Amazon S3 → Buckets
   - AWS IAM → Roles

## Environment-Specific Issues

### macOS Issues
- **SSL warnings**: Scripts suppress urllib3 SSL warnings automatically
- **Python version**: Ensure Python 3.7+ is installed

### Windows Issues
- **Path separators**: Scripts handle cross-platform paths automatically
- **PowerShell**: Use Command Prompt or PowerShell with proper execution policy

### Linux Issues
- **Permissions**: Ensure scripts have execute permissions
- **Python path**: May need to use `python3` instead of `python`

## AWS Service Limits

### Default Limits (per region)
- **Things**: 500,000 per account
- **Thing Types**: 100 per account
- **Thing Groups**: 500 per account
- **Jobs**: 100 concurrent jobs
- **API Rate Limits**: 
  - Thing operations: 100 TPS (scripts use 80 TPS)
  - Dynamic groups: 5 TPS (scripts use 4 TPS)
  - Job executions: 200 TPS (scripts use 150 TPS)
  - Package operations: 10 TPS (scripts use 8 TPS)

### Request Limit Increases
If you need higher limits:
1. Go to AWS Support Center
2. Create a case for "Service limit increase"
3. Specify AWS IoT Core limits needed

## Getting Help

### Enable Verbose Logging
Most scripts support verbose mode:
```bash
🔧 Enable verbose mode? [y/N]: y
```

### Check AWS Service Health
- [AWS Service Health Dashboard](https://status.aws.amazon.com/)
- Check your specific region for AWS IoT Core issues

### Community Resources
- AWS IoT Developer Forums
- AWS Documentation
- GitHub Issues (for script-specific problems)

### Professional Support
- AWS Support (if you have a support plan)
- AWS Professional Services
- AWS Partner Network consultants

## Prevention Tips

### Before Running Scripts
1. **Verify AWS configuration**: `aws sts get-caller-identity`
2. **Check permissions**: Test with a small operation first
3. **Review resource limits**: Ensure you won't hit account limits
4. **Backup important data**: If modifying existing resources

### During Execution
1. **Monitor progress**: Watch for error patterns
2. **Don't interrupt**: Let scripts complete or use Ctrl+C gracefully
3. **Check AWS Console**: Verify resources are being created as expected

### After Execution
1. **Verify results**: Use explore scripts to check outcomes
2. **Clean up test resources**: Use cleanup script for temporary resources
3. **Monitor costs**: Check AWS billing for unexpected charges
## Inte
rnationalization Issues

### Problem: Scripts showing raw message keys instead of translated text
**Symptoms**: Scripts display text like `warnings.debug_warning` and `prompts.debug_mode` instead of actual messages

**Example**:
```
🧹 AWS IoT Cleanup Script (Boto3)
===================================
📚 LEARNING GOAL:
This script demonstrates proper AWS IoT resource cleanup...
📍 Region: eu-west-1
🆔 Account ID: 278816698247
warnings.debug_warning
prompts.debug_mode
```

**Root Cause**: This issue occurs when:
1. Language code mismatch between language selector and directory structure
2. Missing nested key handling in `get_message()` function
3. Incorrect message file loading

**Solution**:

1. **Verify Language Code Mapping**: Ensure language codes match directory structure:
   ```
   i18n/
   ├── en/     # English
   ├── es/     # Spanish  
   ├── ja/     # Japanese
   ├── ko/     # Korean
   ├── pt/     # Portuguese
   ├── zh/     # Chinese
   ```

2. **Check get_message() Implementation**: Scripts should handle nested keys with dot notation:
   ```python
   def get_message(self, key, *args):
       """Get localized message with optional formatting"""
       # Handle nested keys like 'warnings.debug_warning'
       if '.' in key:
           keys = key.split('.')
           msg = messages
           for k in keys:
               if isinstance(msg, dict) and k in msg:
                   msg = msg[k]
               else:
                   msg = key  # Fallback to key if not found
                   break
       else:
           msg = messages.get(key, key)
       
       if args and isinstance(msg, str):
           return msg.format(*args)
       return msg
   ```

3. **Test Language Loading**:
   ```bash
   # Test with environment variable
   export AWS_IOT_LANG=en
   python scripts/cleanup_script.py
   
   # Test different languages
   export AWS_IOT_LANG=es  # Spanish
   export AWS_IOT_LANG=ja  # Japanese
   export AWS_IOT_LANG=zh  # Chinese
   ```

4. **Verify Message Files Exist**:
   ```bash
   # Check if translation files exist
   ls i18n/en/cleanup_script.json
   ls i18n/es/cleanup_script.json
   # etc.
   ```

**Prevention**: When adding new scripts or languages:
- Use the correct `get_message()` implementation from working scripts
- Ensure language codes match directory names exactly
- Test with multiple languages before deployment
- Use the validation scripts in `docs/templates/validation_scripts/`

### Problem: Language selection not working with environment variables
**Symptoms**: Scripts always prompt for language selection despite setting `AWS_IOT_LANG`

**Solution**:
1. **Check Environment Variable Format**:
   ```bash
   # Supported formats
   export AWS_IOT_LANG=en        # English
   export AWS_IOT_LANG=english   # English
   export AWS_IOT_LANG=es        # Spanish
   export AWS_IOT_LANG=español   # Spanish
   export AWS_IOT_LANG=ja        # Japanese
   export AWS_IOT_LANG=japanese  # Japanese
   export AWS_IOT_LANG=zh        # Chinese
   export AWS_IOT_LANG=chinese   # Chinese
   export AWS_IOT_LANG=pt        # Portuguese
   export AWS_IOT_LANG=português # Portuguese
   export AWS_IOT_LANG=ko        # Korean
   export AWS_IOT_LANG=korean    # Korean
   ```

2. **Verify Environment Variable is Set**:
   ```bash
   echo $AWS_IOT_LANG
   ```

3. **Test Language Selection**:
   ```bash
   python3 -c "
   import sys, os
   sys.path.append('i18n')
   from language_selector import get_language
   print('Selected language:', get_language())
   "
   ```

### Problem: Missing translations for new languages
**Symptoms**: Scripts fall back to English or show message keys for unsupported languages

**Solution**:
1. **Add Language Directory**: Create directory structure for new language
2. **Copy Translation Files**: Use existing translations as templates
3. **Update Language Selector**: Add new language to supported list
4. **Test Thoroughly**: Verify all scripts work with new language

For detailed instructions, see `docs/templates/NEW_LANGUAGE_TEMPLATE.md`.
#
# AWS IoT Jobs API Limitations

### Problem: Cannot access job execution details for completed jobs
**Symptoms**: Error when trying to explore job execution details for completed, failed, or canceled jobs

**Example Error**:
```
❌ Error in Job Execution Detail upgradeSedanvehicle110_1761321268 on Vehicle-VIN-016: 
Job Execution has reached terminal state. It is neither IN_PROGRESS nor QUEUED
❌ Failed to get job execution details. Check job ID and thing name.
```

**Root Cause**: AWS provides two different APIs for accessing job execution details:

1. **IoT Jobs Data API** (`iot-jobs-data` service):
   - Endpoint: `describe_job_execution`
   - **Limitation**: Only works for jobs in `IN_PROGRESS` or `QUEUED` status
   - **Error**: Returns "Job Execution has reached terminal state" for completed jobs
   - **Use Case**: Designed for devices to get their current job instructions

2. **IoT API** (`iot` service):
   - Endpoint: `describe_job_execution`
   - **Capability**: Works for jobs in ANY status (COMPLETED, FAILED, CANCELED, etc.)
   - **No Restrictions**: Can access historical job execution data
   - **Use Case**: Designed for management and monitoring of all job executions

**Solution**: The explore_jobs script has been updated to use the IoT API instead of the IoT Jobs Data API.

**Code Change**:
```python
# Before (limited to active jobs only)
execution_response = self.iot_jobs_data_client.describe_job_execution(
    jobId=job_id,
    thingName=thing_name,
    includeJobDocument=True
)

# After (works for all job statuses)
execution_response = self.iot_client.describe_job_execution(
    jobId=job_id,
    thingName=thing_name
)
```

**Verification**: After the fix, you can now explore job execution details for:
- ✅ COMPLETED jobs
- ✅ FAILED jobs  
- ✅ CANCELED jobs
- ✅ IN_PROGRESS jobs
- ✅ QUEUED jobs
- ✅ Any other job status

**Additional Benefits**:
- Access to historical job execution data
- Better troubleshooting capabilities for failed deployments
- Complete audit trail of device update attempts

### Problem: Job document not available in execution details
**Symptoms**: Job execution details show but job document is missing

**Solution**: The script now includes a fallback mechanism:
1. First tries to get job document from execution details
2. If not available, retrieves it from the main job details
3. Displays appropriate message if job document is not available

This ensures you can always see the job instructions that were sent to the device, regardless of the job status or API limitations.