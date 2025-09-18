# AWS IoT Device Management - Learning Path - Basics

A comprehensive demonstration of AWS IoT Device Management capabilities including device provisioning, over-the-air (OTA) updates, job management, and fleet operations using modern Python scripts with native AWS SDK (boto3) integration.

## 👥 Target Audience

**Primary Audience:** IoT developers, solution architects, DevOps engineers working with AWS IoT device fleets

**Prerequisites:** Intermediate AWS knowledge, AWS IoT Core fundamentals, Python fundamentals, command line usage

**Learning Level:** Associate level with hands-on approach to device management at scale

## 🎯 Learning Objectives

- **Device Lifecycle Management**: Provision IoT devices with proper thing types and attributes
- **Fleet Organization**: Create static and dynamic thing groups for device management  
- **OTA Updates**: Implement firmware updates using AWS IoT Jobs with Amazon S3 integration
- **Package Management**: Handle multiple firmware versions with automated shadow updates
- **Job Execution**: Simulate realistic device behavior during firmware updates
- **Version Control**: Rollback devices to previous firmware versions
- **Resource Cleanup**: Properly manage AWS resources to avoid unnecessary costs



## 📋 Prerequisites

- **AWS Account** with AWS IoT, Amazon S3, and AWS Identity and Access Management (IAM) permissions
- **AWS credentials** configured (via `aws configure`, environment variables, or IAM roles)
- **Python 3.10+** with pip and boto3, colorama and requests Python libraries (check requirements.txt file)
- **Git** for cloning the repository

## 💰 Cost Analysis

**This project creates real AWS resources that will incur charges.**

| Service | Usage | Estimated Cost (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1,000 messages, 100-10,000 devices | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2,000 shadow operations | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 job executions | $0.01 - $0.10 |
| **Amazon S3** | Storage + requests for firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Device queries and indexing | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Package operations | $0.01 - $0.05 |
| **AWS Identity and Access Management (IAM)** | Role/policy management | $0.00 |
| **Total Estimated** | **Complete demo session** | **$0.27 - $2.40** |

**Cost Factors:**
- Device count (100-10,000 configurable)
- Job execution frequency
- Shadow update operations
- Amazon S3 storage duration

**Cost Management:**
- ✅ Cleanup script removes all resources
- ✅ Short-lived demo resources
- ✅ Configurable scale (start small)
- ⚠️ **Run cleanup script when finished**

**📊 Monitor costs:** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd aws-iot-dm-basics-learning-path
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure AWS
aws configure

# 3. Complete workflow (recommended sequence)
python scripts/provision_script.py        # Create infrastructure
python scripts/manage_dynamic_groups.py   # Create device groups
python scripts/manage_packages.py         # Manage firmware packages
python scripts/create_job.py              # Deploy firmware updates
python scripts/simulate_job_execution.py  # Simulate device updates
python scripts/explore_jobs.py            # Monitor job progress
python scripts/cleanup_script.py          # Clean up resources
```

## 📚 Available Scripts

| Script | Purpose | Key Features | Documentation |
|--------|---------|-------------|---------------|
| **provision_script.py** | Complete infrastructure setup | Creates devices, groups, packages, Amazon S3 storage | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | Manage dynamic device groups | Create, list, delete with Fleet Indexing validation | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | Comprehensive package management | Create packages/versions, Amazon S3 integration, device tracking with individual revert status | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | Create OTA update jobs | Multi-group targeting, presigned URLs | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | Simulate device updates | Real Amazon S3 downloads, visible plan preparation, per-device progress tracking | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | Monitor job progress | Interactive job exploration and troubleshooting | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **cleanup_script.py** | Remove AWS resources | Selective cleanup, cost management | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **Detailed Documentation**: See [docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md) for comprehensive script information.

## ⚙️ Configuration

**Environment Variables** (optional):
```bash
export AWS_DEFAULT_REGION=us-east-1
```

**Script Features**:
- **Native AWS SDK**: Uses boto3 for better performance and reliability
- **Debug Mode**: Shows all AWS API calls and responses
- **Parallel Processing**: Concurrent operations when not in debug mode
- **Rate Limiting**: Automatic AWS API throttling compliance
- **Progress Tracking**: Real-time operation status

## 📖 Usage Examples

**Complete Workflow** (recommended sequence):
```bash
python scripts/provision_script.py        # 1. Create infrastructure
python scripts/manage_dynamic_groups.py   # 2. Create device groups
python scripts/manage_packages.py         # 3. Manage firmware packages
python scripts/create_job.py              # 4. Deploy firmware updates
python scripts/simulate_job_execution.py  # 5. Simulate device updates
python scripts/explore_jobs.py            # 6. Monitor job progress
python scripts/cleanup_script.py          # 7. Clean up resources
```

**Individual Operations**:
```bash
python scripts/manage_packages.py         # Package and version management
python scripts/manage_dynamic_groups.py   # Dynamic group operations
```

> 📖 **More Examples**: See [docs/EXAMPLES.md](docs/EXAMPLES.md) for detailed usage scenarios.

## 🛠️ Troubleshooting

**Common Issues**:
- **Credentials**: Configure AWS credentials via `aws configure`, environment variables, or IAM roles
- **Permissions**: Ensure IAM user has AWS IoT, Amazon S3, and IAM permissions
- **Rate Limits**: Scripts handle automatically with intelligent throttling
- **Network**: Ensure connectivity to AWS APIs

**Debug Mode**: Enable in any script for detailed troubleshooting
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **Detailed Troubleshooting**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for comprehensive solutions.

## 🧹 Important: Resource Cleanup

**Always run cleanup when finished to avoid ongoing charges:**
```bash
python scripts/cleanup_script.py
# Choose option 1: ALL resources
# Type: DELETE
```

**What cleanup removes:**
- All AWS IoT devices and groups
- Amazon S3 buckets and firmware files
- AWS IoT software packages
- IAM roles and policies
- Fleet Indexing configuration

## 📚 Documentation

- **[Detailed Scripts](docs/DETAILED_SCRIPTS.md)** - Comprehensive scripts documentation
- **[Usage Examples](docs/EXAMPLES.md)** - Practical scenarios and workflows  
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 📄 License

MIT No Attribution License - see [LICENSE](LICENSE) file for details.

## 🏷️ Tags

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot` 