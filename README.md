# AWS IoT Device Management - Learning Path - Basics

## 🌍 Available Languages

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |
| 🇩🇪 Deutsch | [README.de.md](README.de.md) |
| 🇮🇹 Italiano | [README.it.md](README.it.md) |
| 🇫🇷 Français | [README.fr.md](README.fr.md) |

---

A comprehensive demonstration of AWS IoT Device Management capabilities including device provisioning, over-the-air (OTA) updates, job management, and fleet operations. This project uses modern Python scripts with native AWS SDK (boto3) integration to help you learn these concepts hands-on.

## 👥 Target Audience

**Primary Audience:** IoT developers, solution architects, and DevOps engineers working with AWS IoT device fleets

**Prerequisites:** Intermediate AWS knowledge, AWS IoT Core fundamentals, Python fundamentals, and command line usage

**Learning Level:** Associate level with a hands-on approach to device management at scale

## 🎯 Learning Objectives

- **Device Lifecycle Management**: Provision IoT devices with proper thing types and attributes
- **Fleet Organization**: Create static and dynamic thing groups for device management  
- **OTA Updates**: Implement firmware updates using AWS IoT Jobs with Amazon S3 integration
- **Package Management**: Handle multiple firmware versions with automated shadow updates
- **Job Execution**: Simulate realistic device behavior during firmware updates
- **Version Control**: Rollback devices to previous firmware versions
- **Remote Commands**: Send real-time commands to devices using AWS IoT Commands
- **Bulk Registration**: Register hundreds or thousands of devices efficiently using manufacturing-scale provisioning
- **Resource Cleanup**: Properly manage AWS resources to avoid unnecessary costs



## 📋 Prerequisites

- **AWS Account** with AWS IoT, Amazon S3, and AWS Identity and Access Management (IAM) permissions
- **AWS credentials** configured (you can use `aws configure`, environment variables, or IAM roles)
- **Python 3.10+** with pip and boto3, colorama and requests Python libraries (check the requirements.txt file)
- **Git** for cloning the repository

## 💰 Cost Analysis

**This project creates real AWS resources that will incur charges. Here's what to expect:**

| Service | Usage | Estimated Cost (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1,000 messages, 100-10,000 devices | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2,000 shadow operations | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 job executions | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50 command executions | $0.01 - $0.05 |
| **Amazon S3** | Storage + requests for firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Device queries and indexing | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Package operations | $0.01 - $0.05 |
| **AWS IoT Device Management Bulk Registration** | Bulk device provisioning | $0.05 - $0.50 |
| **AWS Identity and Access Management (IAM)** | Role/policy management | $0.00 |
| **Total Estimated** | **Complete demo session** | **$0.33 - $2.95** |

**Cost Factors:**
- Device count (100-10,000 configurable)
- Job execution frequency
- Shadow update operations
- Amazon S3 storage duration

**Cost Management:**
- ✅ Cleanup script removes all resources
- ✅ Short-lived demo resources
- ✅ Configurable scale (start small)
- ⚠️ **Remember to run cleanup script when you're finished**

**📊 Monitor costs:** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure AWS
aws configure

# 3. Complete workflow (we recommend this sequence)
python scripts/provision_script.py        # Create infrastructure with tagging
python scripts/manage_dynamic_groups.py   # Create device groups
python scripts/manage_packages.py         # Manage firmware packages
python scripts/create_job.py              # Deploy firmware updates
python scripts/simulate_job_execution.py  # Simulate device updates
python scripts/explore_jobs.py            # Monitor job progress
python scripts/manage_commands.py         # Send real-time commands to devices
python scripts/manage_bulk_provisioning.py # Bulk device registration (manufacturing scale)
python scripts/cleanup_script.py          # Safe cleanup with resource identification
```

## 📚 Available Scripts

| Script | Purpose | Key Features |
|--------|---------|-------------|
| **provision_script.py** | Complete infrastructure setup | Creates devices, groups, packages, Amazon S3 storage |
| **manage_dynamic_groups.py** | Manage dynamic device groups | Create, list, delete with Fleet Indexing validation |
| **manage_packages.py** | Comprehensive package management | Create packages/versions, Amazon S3 integration, device tracking with individual revert status |
| **create_job.py** | Create OTA update jobs | Multi-group targeting, presigned URLs |
| **simulate_job_execution.py** | Simulate device updates | Real Amazon S3 downloads, visible plan preparation, per-device progress tracking |
| **explore_jobs.py** | Monitor and manage jobs | Interactive job exploration, cancellation, deletion, and analytics |
| **manage_commands.py** | Send real-time commands to devices | Template management, command execution, status monitoring, history tracking |
| **manage_bulk_provisioning.py** | Bulk device registration | Manufacturing-scale device provisioning, certificate generation, task monitoring |
| **cleanup_script.py** | Remove AWS resources | Selective cleanup, cost management |

## ⚙️ Configuration

**Environment Variables** (optional):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=en                    # Set default language (en, es, fr, etc.)
```

**Script Features**:
- **Native AWS SDK**: Uses boto3 for better performance and reliability
- **Multi-language Support**: Interactive language selection with fallback to English
- **Debug Mode**: Shows all AWS API calls and responses
- **Parallel Processing**: Concurrent operations when not in debug mode
- **Rate Limiting**: Automatic AWS API throttling compliance
- **Progress Tracking**: Real-time operation status
- **Resource Tagging**: Automatic workshop tags for safe cleanup
- **Configurable Naming**: Customizable device naming patterns

### Resource Tagging

All workshop scripts automatically tag created resources with `workshop=learning-aws-iot-dm-basics` for safe identification during cleanup. This ensures only workshop-created resources are deleted.

**Tagged Resources**:
- IoT Thing Types
- IoT Thing Groups (static and dynamic)
- IoT Software Packages
- AWS IoT Jobs
- Amazon S3 Buckets
- AWS Identity and Access Management (IAM) Roles

**Non-Tagged Resources** (identified by naming patterns):
- IoT Things (use naming conventions)
- Certificates (identified by association)
- Thing Shadows (identified by association)

### Device Naming Configuration

Customize device naming patterns with the `--things-prefix` parameter:

```bash
# Default naming: Vehicle-VIN-001, Vehicle-VIN-002, etc.
python scripts/provision_script.py

# Custom prefix: Fleet-Device-001, Fleet-Device-002, etc.
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Custom prefix for cleanup (must match provision prefix)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**Prefix Requirements**:
- Use alphanumeric characters, hyphens, underscores, and colons
- Keep it under 20 characters
- Sequential numbers are automatically zero-padded (001-999)

## 🌍 Internationalization Support

All scripts support multiple languages with automatic language detection and interactive selection.

**Language Selection**:
- **Interactive**: Scripts prompt for language selection on first run
- **Environment Variable**: Set `AWS_IOT_LANG=en` to skip language selection
- **Fallback**: Automatically falls back to English for missing translations

**Supported Languages**:
- **English (en)**: Complete translations ✅
- **Spanish (es)**: Ready for translations
- **Japanese (ja)**: Ready for translations  
- **Chinese (zh-CN)**: Ready for translations
- **Portuguese (pt-BR)**: Ready for translations
- **Korean (ko)**: Ready for translations

**Usage Examples**:
```bash
# Set language via environment variable (recommended for automation)
export AWS_IOT_LANG=en
python scripts/provision_script.py

# Alternative language codes supported
export AWS_IOT_LANG=spanish    # or "es", "español"
export AWS_IOT_LANG=japanese   # or "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # or "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # or "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # or "ko", "한국어", "kr"

# Interactive language selection (default behavior)
python scripts/manage_packages.py
# Output: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# All user-facing text will appear in selected language
```

**Message Categories**:
- **UI Elements**: Titles, headers, separators
- **User Prompts**: Input requests, confirmations
- **Status Messages**: Progress updates, success/failure notifications
- **Error Messages**: Detailed error descriptions and troubleshooting
- **Debug Output**: API call information and responses
- **Learning Content**: Educational moments and explanations

## 📖 Usage Examples

**Complete Workflow** (we recommend this sequence):
```bash
python scripts/provision_script.py        # 1. Create infrastructure
python scripts/manage_dynamic_groups.py   # 2. Create device groups
python scripts/manage_packages.py         # 3. Manage firmware packages
python scripts/create_job.py              # 4. Deploy firmware updates
python scripts/simulate_job_execution.py  # 5. Simulate device updates
python scripts/explore_jobs.py            # 6. Monitor job progress
python scripts/manage_commands.py         # 7. Send real-time commands to devices
python scripts/cleanup_script.py          # 8. Clean up resources
```

**Individual Operations**:
```bash
python scripts/manage_packages.py         # Package and version management
python scripts/manage_dynamic_groups.py   # Dynamic group operations
```

## 🛠️ Troubleshooting

**Common Issues**:
- **Credentials**: You can configure AWS credentials via `aws configure`, environment variables, or IAM roles
- **Permissions**: Make sure your IAM user has AWS IoT, Amazon S3, and IAM permissions
- **Rate Limits**: Don't worry - scripts handle this automatically with intelligent throttling
- **Network**: Make sure you have connectivity to AWS APIs

**Debug Mode**: You can enable this in any script for detailed troubleshooting
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **Detailed Troubleshooting**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for comprehensive solutions.

## 🧹 Important: Resource Cleanup

**Remember to run cleanup when you're finished to avoid ongoing charges:**
```bash
python scripts/cleanup_script.py
# Choose option 1: ALL resources
# Type: DELETE
```

### Safe Cleanup Features

The cleanup script uses multiple identification methods to ensure only workshop resources are deleted:

1. **Tag-Based Identification** (Primary): Checks for `workshop=learning-aws-iot-dm-basics` tag
2. **Naming Pattern Matching** (Secondary): Matches known workshop naming conventions
3. **Association-Based** (Tertiary): Identifies resources attached to workshop resources

**Cleanup Options**:
```bash
# Standard cleanup (interactive)
python scripts/cleanup_script.py

# Dry-run mode (preview without deleting)
python scripts/cleanup_script.py --dry-run

# Custom device prefix (must match provision prefix)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# Dry-run with custom prefix
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**What cleanup removes:**
- All AWS IoT devices and groups (with workshop tags or matching naming patterns)
- Amazon S3 buckets and firmware files (tagged)
- AWS IoT software packages (tagged)
- AWS IoT command templates (tagged)
- IAM roles and policies (tagged)
- Fleet Indexing configuration
- Associated certificates and shadows

**Safety Features**:
- Non-workshop resources are automatically skipped
- You'll see a detailed summary of deleted and skipped resources
- Debug mode shows the identification method for each resource
- Dry-run mode lets you preview before actual deletion

## 📁 Project Structure

```
sample-aws-iot-device-management-learning-path-basics/
├── scripts/                          # User-facing executable scripts
│   ├── provision_script.py          # Provision IoT resources
│   ├── cleanup_script.py            # Clean up workshop resources
│   ├── manage_packages.py           # Package management
│   ├── manage_dynamic_groups.py     # Dynamic group operations
│   ├── create_job.py                # Create OTA jobs
│   ├── simulate_job_execution.py    # Simulate device updates
│   ├── explore_jobs.py              # Monitor job progress
│   └── manage_commands.py           # Send real-time commands
├── iot_helpers/                     # Internal helper package
│   ├── cleanup/                     # Cleanup operation modules
│   │   ├── reporter.py             # Cleanup reporting
│   │   ├── deletion_engine.py      # Resource deletion
│   │   └── resource_identifier.py  # Resource identification
│   └── utils/                       # Utility modules
│       ├── naming_conventions.py   # Naming patterns
│       ├── resource_tagger.py      # Resource tagging
│       └── dependency_handler.py   # Dependency management
├── i18n/                            # Internationalization
│   ├── common.json                 # Shared messages
│   ├── loader.py                   # Message loading
│   ├── language_selector.py        # Language selection
│   └── {language_code}/            # Language-specific messages
├── docs/                            # Documentation
│   └── TROUBLESHOOTING.md          # Troubleshooting guide
├── tests/                           # Test files
└── requirements.txt                 # Python dependencies
```

## 🔧 Developer Guide: Adding New Languages

**Message File Structure**:
```
i18n/
├── common.json                    # Shared messages across all scripts
├── loader.py                      # Message loading utility
├── language_selector.py           # Language selection interface
└── {language_code}/               # Language-specific directory
    ├── provision_script.json     # Script-specific messages
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**Adding a New Language**:

1. **Create Language Directory**:
   ```bash
   mkdir i18n/{language_code}  # e.g., i18n/es for Spanish
   ```

2. **Copy English Templates**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Translate Message Files**:
   Each JSON file contains categorized messages:
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Enable debug mode? [y/N]: ",
       "operation_choice": "Enter choice [1-11]: ",
       "continue_operation": "Continue? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Debug mode enabled",
       "package_created": "✅ Package created successfully",
       "clients_initialized": "🔍 DEBUG: Client configuration:"
     },
     "errors": {
       "invalid_choice": "❌ Invalid choice. Please enter 1-11",
       "package_not_found": "❌ Package '{}' not found",
       "api_error": "❌ Error in {} {}: {}"
     },
     "debug": {
       "api_call": "📤 API Call: {}",
       "api_response": "📤 API Response:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Select Operation:",
       "create_package": "1. Create Software Package",
       "goodbye": "👋 Thank you for using Package Manager!"
     },
     "learning": {
       "package_management_title": "Software Package Management",
       "package_management_description": "Educational content..."
     }
   }
   ```

4. **Update Language Selector** (if adding new language):
   Add your language to `i18n/language_selector.py`:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Your Language Name",  # Add new option
           # ... existing languages
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "your_code",  # Add new language code
       # ... existing mappings
   }
   ```

5. **Test Translation**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Translation Guidelines**:
- **Preserve Formatting**: Keep emojis, colors, and special characters as they are
- **Maintain Placeholders**: Keep `{}` placeholders for dynamic content
- **Technical Terms**: Keep AWS service names in English
- **Cultural Adaptation**: Feel free to adapt examples and references appropriately
- **Consistency**: Use consistent terminology across all files

**Message Key Patterns**:
- `title`: Script main title
- `separator`: Visual separators and dividers  
- `prompts.*`: User input requests and confirmations
- `status.*`: Progress updates and operation results
- `errors.*`: Error messages and warnings
- `debug.*`: Debug output and API information
- `ui.*`: User interface elements (menus, labels, buttons)
- `results.*`: Operation results and data display
- `learning.*`: Educational content and explanations
- `warnings.*`: Warning messages and important notices
- `explanations.*`: Additional context and help text

**Testing Your Translation**:
```bash
# Test specific script with your language
export AWS_IOT_LANG=your_language_code
python scripts/manage_packages.py

# Test fallback behavior (use non-existent language)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Should fall back to English
```

## 📚 Documentation

- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 📄 License

MIT No Attribution License - see [LICENSE](LICENSE) file for details.

## 🏷️ Tags

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot` 