# AWS IoT Device Management - Learning Path - Basics

## 🌍 Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |

---

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
- **Remote Commands**: Send real-time commands to devices using AWS IoT Commands
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
| **AWS IoT Commands** | ~10-50 command executions | $0.01 - $0.05 |
| **Amazon S3** | Storage + requests for firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Device queries and indexing | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Package operations | $0.01 - $0.05 |
| **AWS Identity and Access Management (IAM)** | Role/policy management | $0.00 |
| **Total Estimated** | **Complete demo session** | **$0.28 - $2.45** |

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
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure AWS
aws configure

# 3. Complete workflow (recommended sequence)
python scripts/provision_script.py        # Create infrastructure with tagging
python scripts/manage_dynamic_groups.py   # Create device groups
python scripts/manage_packages.py         # Manage firmware packages
python scripts/create_job.py              # Deploy firmware updates
python scripts/simulate_job_execution.py  # Simulate device updates
python scripts/explore_jobs.py            # Monitor job progress
python scripts/manage_commands.py         # Send real-time commands to devices
python scripts/cleanup_script.py          # Safe cleanup with resource identification
```

## 📚 Available Scripts

| Script | Purpose | Key Features | Documentation |
|--------|---------|-------------|---------------|
| **provision_script.py** | Complete infrastructure setup | Creates devices, groups, packages, Amazon S3 storage | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | Manage dynamic device groups | Create, list, delete with Fleet Indexing validation | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | Comprehensive package management | Create packages/versions, Amazon S3 integration, device tracking with individual revert status | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | Create OTA update jobs | Multi-group targeting, presigned URLs | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | Simulate device updates | Real Amazon S3 downloads, visible plan preparation, per-device progress tracking | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | Monitor and manage jobs | Interactive job exploration, cancellation, deletion, and analytics | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **manage_commands.py** | Send real-time commands to devices | Template management, command execution, status monitoring, history tracking | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptsmanage_commandspy) |
| **cleanup_script.py** | Remove AWS resources | Selective cleanup, cost management | [📖 Details](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **Detailed Documentation**: See [docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md) for comprehensive script information.

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
- IoT Jobs
- Amazon S3 Buckets
- IAM Roles

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
- Only alphanumeric characters, hyphens, underscores, and colons
- Maximum 20 characters
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

**Complete Workflow** (recommended sequence):
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
- Detailed summary shows deleted and skipped resources
- Debug mode shows identification method for each resource
- Dry-run mode allows preview before actual deletion

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
│   ├── DETAILED_SCRIPTS.md         # Script documentation
│   ├── EXAMPLES.md                 # Usage examples
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
- **Preserve Formatting**: Keep emojis, colors, and special characters
- **Maintain Placeholders**: Keep `{}` placeholders for dynamic content
- **Technical Terms**: Keep AWS service names in English
- **Cultural Adaptation**: Adapt examples and references appropriately
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

- **[Detailed Scripts](docs/DETAILED_SCRIPTS.md)** - Comprehensive scripts documentation
- **[Usage Examples](docs/EXAMPLES.md)** - Practical scenarios and workflows  
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 📄 License

MIT No Attribution License - see [LICENSE](LICENSE) file for details.

## 🏷️ Tags

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot` 