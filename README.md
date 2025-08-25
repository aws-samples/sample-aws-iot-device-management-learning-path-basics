# AWS IoT Device Management - Basics

A comprehensive demonstration of AWS IoT Device Management basic capabilities including device provisioning, over-the-air (OTA) updates, job management, and fleet operations using Python scripts.

The learning experience is about learning the basics of AWS IoT Device Management, discovering the features of AWS IoT Jobs, Software Package Catalog and Fleet Indexing and how they integrate with each other.

## 🎯 Project Overview

<details>
<summary><strong>Click to expand project scope and learning objectives</strong></summary>

This project demonstrates real-world AWS IoT scenarios through practical, hands-on scripts that showcase:

- **Device Lifecycle Management**: Provision thousands of IoT devices with proper thing types, attributes, and shadows
- **Fleet Organization**: Create static and dynamic thing groups for device categorization and management  
- **OTA Updates**: Implement over-the-air firmware updates using AWS IoT Jobs with S3 integration
- **Package Management**: Handle multiple firmware versions with automated shadow updates
- **Job Execution**: Simulate realistic device behavior during firmware update processes
- **Version Control**: Rollback devices to previous firmware versions when needed
- **Resource Cleanup**: Properly clean up all AWS resources to avoid unnecessary costs

### Learning Outcomes
- Understanding AWS IoT Core architecture and components
- Implementing scalable IoT device management patterns
- Working with AWS IoT Jobs for device orchestration
- Managing device shadows for state synchronization
- Handling S3 integration for firmware distribution
- Using Fleet Indexing for device queries and grouping
- Implementing proper IAM roles and policies for IoT operations

</details>



## 📋 Prerequisites

<details>
<summary><strong>Click to expand prerequisites and setup requirements</strong></summary>

### AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- IAM user with IoT, S3, and IAM permissions

### Required AWS Permissions
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
                "s3:*",
                "iam:*",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

### Local Environment
- Python 3.7 or higher
- pip package manager
- Git (for cloning and version control)

### Environment Variables (Optional)
```bash
export AWS_DEFAULT_REGION=us-east-1
export BUCKET_KEY_VERSION_1_1_0=firmware-v1.1.0.zip
export BUCKET_KEY_VERSION_1_1_1=firmware-v1.1.1.zip
```

</details>

## 🚀 Quick Start

<details>
<summary><strong>Click to expand installation and setup steps</strong></summary>

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Demo
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure AWS
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

### 3. Verify Setup
```bash
aws sts get-caller-identity
aws iot list-things --max-items 1
```

### 4. Run Your First Script
```bash
python provision_script.py
```

</details>

## 📚 Scripts Overview

### 🏭 Core Provisioning

<details>
<summary><strong>provision_script.py - Main Infrastructure Setup</strong></summary>

**Purpose**: Creates the complete AWS IoT infrastructure including devices, groups, packages, and supporting resources.

**Features**:
- ✅ **Parallel Processing**: Creates thousands of devices efficiently (80 TPS)
- ✅ **Flexible Versions**: User-defined package versions (e.g., 1.0.0, 1.1.0, 2.0.0)
- ✅ **Global Coverage**: 204+ countries across 7 continents
- ✅ **Multiple Thing Types**: Support for various device categories
- ✅ **Automated S3 Setup**: Firmware storage with versioning
- ✅ **IAM Configuration**: Proper roles and policies
- ✅ **Fleet Indexing**: Search and query capabilities
- ✅ **Package Configuration**: Automated shadow updates from jobs

**Usage**:
```bash
python provision_script.py
```

**Interactive Prompts**:
1. Thing types (e.g., `motionSensor,temperatureSensor`)
2. Package versions (e.g., `1.0.0,1.1.0,2.0.0`)
3. Continent selection (1-7)
4. Countries (count or specific codes)
5. Device count

**What Gets Created**:
- Thing types with proper attributes
- S3 bucket with firmware packages
- IoT software packages (multiple versions)
- Static thing groups by country
- Thousands of IoT things with shadows
- IAM roles for jobs and package configuration
- Fleet indexing configuration

</details>

### 🧹 Resource Management

<details>
<summary><strong>cleanup_script.py - Complete Resource Cleanup</strong></summary>

**Purpose**: Safely removes all AWS IoT resources to avoid ongoing costs.

**Features**:
- ✅ **Selective Cleanup**: Choose what to delete (ALL/Things/Groups)
- ✅ **Parallel Processing**: Fast deletion with rate limiting
- ✅ **Smart Detection**: Distinguishes static vs dynamic groups
- ✅ **Job Cleanup**: Cancels and deletes all IoT jobs
- ✅ **S3 Cleanup**: Handles versioned objects properly
- ✅ **IAM Cleanup**: Removes roles and policies
- ✅ **Configuration Reset**: Disables Fleet Indexing and package config
- ✅ **Thing Type Handling**: Proper deprecation and deletion workflow

**Usage**:
```bash
python cleanup_script.py
```

**Cleanup Options**:
1. **ALL resources** - Complete cleanup
2. **Things only** - Remove devices but keep infrastructure  
3. **Thing groups only** - Remove groupings but keep devices

**Safety Features**:
- Confirmation prompt requiring "DELETE"
- Progress tracking with success/failure counts
- Graceful handling of missing resources
- Debug mode for troubleshooting

</details>

### 🚀 Job Management

<details>
<summary><strong>create_job.py - IoT Job Creation</strong></summary>

**Purpose**: Creates AWS IoT Jobs for over-the-air firmware updates.

**Features**:
- ✅ **Multi-Group Targeting**: Select multiple thing groups
- ✅ **Package Integration**: Automatic package version ARN resolution
- ✅ **Presigned URLs**: AWS IoT managed S3 access
- ✅ **Continuous Jobs**: Automatically includes new devices
- ✅ **User-Friendly Selection**: Interactive group and package selection

**Usage**:
```bash
python create_job.py
```

**Job Configuration**:
- Auto-generated job IDs with timestamps
- Proper ARN formatting for thing groups and packages
- AWS IoT presigned URL placeholders
- 1-hour URL expiration
- Comprehensive job document structure

</details>

<details>
<summary><strong>simulate_job_execution.py - Job Execution Simulation</strong></summary>

**Purpose**: Simulates realistic device behavior during firmware update jobs.

**Features**:
- ✅ **Real Downloads**: Actual S3 artifact downloads via presigned URLs
- ✅ **Parallel Execution**: Process multiple devices simultaneously (150 TPS)
- ✅ **Success/Failure Simulation**: Configurable success rates
- ✅ **Progress Tracking**: Individual device results and overall statistics
- ✅ **IoT Data Endpoint**: Proper ATS endpoint usage

**Usage**:
```bash
python simulate_job_execution.py
```

**Simulation Features**:
- Processes QUEUED and IN_PROGRESS job executions
- Downloads real firmware artifacts from S3
- Updates job execution status (SUCCEEDED/FAILED)
- Configurable success percentage
- Detailed progress reporting

</details>

### 🔄 Version Management

<details>
<summary><strong>revert_versions.py - Firmware Version Rollback</strong></summary>

**Purpose**: Rollback devices to previous firmware versions by updating device shadows.

**Features**:
- ✅ **Fleet Indexing Search**: Finds devices needing version changes
- ✅ **Efficient Updates**: Only processes devices with different versions
- ✅ **Parallel Processing**: Fast shadow updates (80 TPS)
- ✅ **IoT Data Endpoint**: Proper shadow update mechanism

**Usage**:
```bash
python revert_versions.py
```

**Process Flow**:
1. Enter thing type (e.g., `motionSensor`)
2. Enter target version (e.g., `1.0.0`)
3. Script finds devices NOT on target version
4. Confirm rollback operation
5. Parallel shadow updates with progress tracking

</details>

### 🔍 Dynamic Group Management

<details>
<summary><strong>create_dynamic_groups.py - Custom Dynamic Groups</strong></summary>

**Purpose**: Create custom dynamic thing groups with flexible criteria.

**Features**:
- ✅ **Flexible Criteria**: Countries, thing types, versions, battery levels
- ✅ **Smart Naming**: Auto-generated or custom group names
- ✅ **Fleet Indexing Queries**: Proper query syntax for complex conditions
- ✅ **Multiple Values**: Support for multiple countries/versions with OR logic

**Usage**:
```bash
python create_dynamic_groups.py
```

**Criteria Options** (all optional):
- **Countries**: Single or multiple (e.g., `US,CA,MX`)
- **Thing Type**: Device category (e.g., `motionSensor`)
- **Versions**: Single or multiple (e.g., `1.0.0,1.1.0`)
- **Battery Level**: Comparisons (e.g., `>50`, `<30`, `=75`)

**Naming Examples**:
- Single criteria: `US_motionSensor_1_0_0_batterygt50_Devices`
- Multiple criteria: Custom name required
- Missing fields: Automatically omitted from name

</details>

## 🔧 Configuration

<details>
<summary><strong>Click to expand configuration options and environment variables</strong></summary>

### Environment Variables
```bash
# AWS Region (default: us-east-1)
export AWS_DEFAULT_REGION=eu-west-2

# S3 Firmware Keys (optional)
export BUCKET_KEY_VERSION_1_1_0=firmware-v1.1.0.zip
export BUCKET_KEY_VERSION_1_1_1=firmware-v1.1.1.zip
```

### Script Configuration
Most scripts support:
- **Debug Mode**: Shows all AWS CLI commands and outputs
- **Verbose Mode**: Additional progress information
- **Rate Limiting**: Automatic AWS API throttling compliance
- **Progress Tracking**: Real-time operation status

### AWS Service Limits
The scripts respect AWS API rate limits:
- **Thing Operations**: 100 TPS (scripts use 80 TPS)
- **Thing Types**: 10 TPS (scripts use 8 TPS)
- **Dynamic Groups**: 5 TPS (scripts use 4 TPS)
- **Job Executions**: 200 TPS (scripts use 150 TPS)
- **Package Operations**: 10 TPS (scripts use 8 TPS)

</details>

## 📖 Usage Examples

<details>
<summary><strong>Click to expand common usage scenarios and examples</strong></summary>

### Scenario 1: Basic Fleet Setup
```bash
# 1. Create infrastructure
python provision_script.py
# Choose: motionSensor, versions 1.0.0,1.1.0, North America, US,CA, 100 devices

# 2. Create a firmware update job
python create_job.py
# Select thing groups and package version

# 3. Simulate device updates
python simulate_job_execution.py
# Choose success rate and process executions
```

### Scenario 2: Version Rollback
```bash
# Rollback all motionSensor devices to version 1.0.0
python revert_versions.py
# Enter: motionSensor, 1.0.0
```

### Scenario 3: Custom Device Grouping
```bash
# Create group for US devices with low battery
python create_dynamic_groups.py
# Countries: US
# Thing type: motionSensor  
# Battery level: <30
```

### Scenario 4: Complete Cleanup
```bash
# Remove all resources
python cleanup_script.py
# Choose option 1 (ALL resources)
# Type: DELETE
```

</details>

## 🛠️ Troubleshooting

<details>
<summary><strong>Click to expand common issues and solutions</strong></summary>

### Common Issues

**AWS Credentials Not Configured**
```bash
# Solution: Configure AWS CLI
aws configure
```

**Permission Denied Errors**
```bash
# Solution: Check IAM permissions
aws iam get-user
aws sts get-caller-identity
```

**Rate Limiting Errors**
- Scripts automatically handle rate limiting
- Enable debug mode to see retry behavior
- Reduce parallel workers if needed

**Thing Type Deletion Issues**
- Thing types require 5-minute wait after deprecation
- Cleanup script handles this automatically
- Manual deletion: wait 5 minutes after deprecation

**S3 Bucket Issues**
- Ensure bucket names are globally unique
- Scripts use timestamps for uniqueness
- Check region consistency

### Debug Mode
Enable debug mode in any script for detailed troubleshooting:
```bash
# When prompted, choose 'y' for debug mode
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

### Log Analysis
Scripts provide colored output for easy issue identification:
- 🟢 **Green**: Successful operations
- 🟡 **Yellow**: Warnings or skipped operations  
- 🔴 **Red**: Errors requiring attention
- 🔵 **Blue**: Informational messages

</details>

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT No Attribution License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bug reports or feature requests
- Check existing issues for solutions
- Enable debug mode for detailed error information

## 🏷️ Tags

`aws-iot` `iot-core` `device-management` `ota-updates` `fleet-management` `python` `demo` `tutorial`