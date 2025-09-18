# Detailed Scripts Documentation

This document provides comprehensive information about each script in the AWS IoT Device Management project. All scripts use native AWS SDK (boto3) for optimal performance and reliability.

## Core Scripts

### scripts/provision_script.py
**Purpose**: Complete AWS IoT infrastructure provisioning for device management scenarios using native boto3 APIs.

**Features**:
- Creates thing types with searchable attributes (customerId, country, manufacturingDate)
- Provisions thousands of IoT devices with VIN-style naming (Vehicle-VIN-001)
- Sets up Amazon S3 storage with versioning for firmware packages
- Creates AWS IoT software packages with multiple versions
- Configures AWS IoT Fleet Indexing for device queries
- Establishes AWS Identity and Access Management (IAM) roles for secure operations
- Creates static thing groups by country (Fleet naming convention)
- **Parallel Processing**: Concurrent operations for faster provisioning
- **Enhanced Error Handling**: Robust boto3 exception handling

**Interactive Inputs**:
1. Thing types (default: SedanVehicle,SUVVehicle,TruckVehicle)
2. Package versions (default: 1.0.0,1.1.0)
3. Continent selection (1-7)
4. Countries (count or specific codes)
5. Device count (default: 100)

**Educational Pauses**: 8 learning moments explaining IoT concepts

**Rate Limits**: Intelligent AWS API throttling (80 TPS for things, 8 TPS for thing types)

**Performance**: Parallel execution when not in debug mode, sequential in debug mode for clean output

---

### scripts/cleanup_script.py
**Purpose**: Safe removal of AWS IoT resources to avoid ongoing costs using native boto3 APIs.

**Cleanup Options**:
1. **ALL resources** - Complete infrastructure cleanup
2. **Things only** - Remove devices but keep infrastructure
3. **Thing groups only** - Remove groupings but keep devices

**Features**:
- **Native boto3 Implementation**: No CLI dependencies, better error handling
- **Parallel processing** with intelligent rate limiting
- **Enhanced S3 Cleanup**: Proper versioned object deletion using paginators
- Distinguishes static vs dynamic groups automatically
- Handles thing type deprecation (5-minute wait)
- Cancels and deletes AWS IoT Jobs with status monitoring
- Comprehensive IAM role and policy cleanup
- Disables Fleet Indexing configuration
- **Shadow Cleanup**: Removes both classic and $package shadows
- **Principal Detachment**: Properly detaches certificates and policies

**Safety**: Requires typing "DELETE" to confirm

**Performance**: Parallel execution respecting AWS API limits (80 TPS things, 4 TPS dynamic groups)

---

### scripts/create_job.py
**Purpose**: Create AWS IoT Jobs for over-the-air firmware updates using native boto3 APIs.

**Features**:
- **Native boto3 Implementation**: Direct API calls for better performance
- Interactive thing group selection (single or multiple)
- Package version selection with ARN resolution
- Continuous job configuration (auto-includes new devices)
- Presigned URL configuration (1-hour expiration)
- Multi-group targeting support
- **Enhanced Job Types**: Support for both OTA and custom job types
- **Advanced Configuration**: Rollout policies, abort criteria, timeout settings

**Job Configuration**:
- Auto-generated job IDs with timestamps
- AWS IoT presigned URL placeholders
- Proper ARN formatting for resources
- Comprehensive job document structure
- **Educational Content**: Explains job configuration options

---

### scripts/simulate_job_execution.py
**Purpose**: Simulate realistic device behavior during firmware updates using native boto3 APIs.

**Features**:
- **Native boto3 Implementation**: Direct IoT Jobs Data API integration
- Real Amazon S3 artifact downloads via presigned URLs
- **High-Performance Parallel Execution** (150 TPS with semaphore control)
- Configurable success/failure rates
- **Visible plan preparation** - Shows each device being assigned success/failure status
- **User confirmation** - Asks to proceed after plan preparation
- **Operation visibility** - Shows download progress and job status updates for each device
- **Enhanced Error Handling**: Robust boto3 exception management
- Progress tracking with detailed reporting
- **Clean JSON Formatting**: Properly formatted job document display

**Process Flow**:
1. Scans for active jobs using native APIs
2. Gets pending executions (QUEUED/IN_PROGRESS)
3. **Prepares execution plan** - Shows device assignments and asks for confirmation
4. Downloads actual firmware from Amazon S3 (shows progress per device)
5. Updates job execution status using IoT Jobs Data API
6. Reports comprehensive success/failure statistics

**Performance Improvements**:
- **Parallel Processing**: Concurrent execution when not in debug mode
- **Rate Limiting**: Intelligent semaphore-based throttling
- **Memory Efficient**: Streaming downloads for large firmware files

**Visibility Improvements**:
- Plan preparation shows: `[1/100] Vehicle-VIN-001 -> SUCCESS`
- Download progress shows: `Vehicle-VIN-001: Downloading firmware from S3...`
- File size confirmation: `Vehicle-VIN-001: Downloaded 2.1KB firmware`
- Status updates show: `Vehicle-VIN-001: Job execution SUCCEEDED`

---

### scripts/explore_jobs.py
**Purpose**: Interactive exploration of AWS IoT Jobs for monitoring and troubleshooting using native boto3 APIs.

**Menu Options**:
1. **List all jobs** - Overview across all statuses with parallel scanning
2. **Explore specific job** - Detailed job configuration with clean JSON formatting
3. **Explore job execution** - Individual device progress using IoT Jobs Data API
4. **List job executions** - All executions for a job with parallel status checking

**Features**:
- **Native boto3 Implementation**: Direct API integration for better performance
- **Parallel Job Scanning**: Concurrent status checking across all job states
- **Clean JSON Display**: Properly formatted job documents without escape characters
- Color-coded status indicators
- Interactive job selection with available job listing
- Detailed presigned URL configuration display
- Execution summary statistics with color coding
- **Enhanced Error Handling**: Robust boto3 exception management
- Continuous exploration loop

**Performance Improvements**:
- **Parallel Processing**: Concurrent operations when not in debug mode
- **Intelligent Pagination**: Efficient handling of large job lists
- **Rate Limiting**: Proper API throttling with semaphores

---



### scripts/manage_packages.py
**Purpose**: Comprehensive management of AWS IoT Software Packages, device tracking, and version rollback using native boto3 APIs.

**Operations**:
1. **Create Package** - Create new software package containers
2. **Create Version** - Add versions with S3 firmware upload and publishing (with learning moments)
3. **List Packages** - Display packages with interactive describe options
4. **Describe Package** - Show package details with version exploration
5. **Describe Version** - Show specific version details and Amazon S3 artifacts
6. **Check Configuration** - View package configuration status and IAM role
7. **Enable Configuration** - Enable automatic shadow updates with IAM role creation
8. **Disable Configuration** - Disable automatic shadow updates
9. **Check Device Version** - Inspect $package shadow for specific devices (multi-device support)
10. **Revert Versions** - Fleet-wide version rollback using Fleet Indexing

**Key Features**:
- **Amazon S3 Integration**: Automatic firmware upload with versioning
- **Interactive Navigation**: Seamless flow between list, describe, and version operations
- **Package Configuration Management**: Control Jobs-to-Shadow integration
- **Device Tracking**: Individual device package version inspection
- **Fleet Rollback**: Version revert using Fleet Indexing queries
- **Educational Approach**: Learning moments throughout workflows
- **IAM Role Management**: Automatic role creation for package configuration

**Package Configuration**:
- **Check Status**: Shows enabled/disabled state and IAM role ARN
- **Enable**: Creates IoTPackageConfigRole with $package shadow permissions
- **Disable**: Stops automatic shadow updates on job completion
- **Educational**: Explains Jobs-to-Shadow integration and IAM requirements

**Device Version Tracking**:
- **Multi-device Support**: Check multiple devices in sequence
- **$package Shadow Inspection**: Shows current firmware versions and metadata
- **Timestamp Display**: Last update information for each package
- **Error Handling**: Clear messages for missing devices or shadows

**Version Rollback**:
- **Fleet Indexing Queries**: Find devices by thing type and version
- **Device List Preview**: Shows devices that will be reverted (first 10 + count)
- **Confirmation Required**: Type 'REVERT' to proceed with shadow updates
- **Individual Device Status**: Shows revert success/failure per device
- **Progress Tracking**: Real-time update status with success counts
- **Educational**: Explains rollback concepts and shadow management

**Rollback Visibility**:
- Device preview: `1. Vehicle-VIN-001`, `2. Vehicle-VIN-002`, `... and 90 more devices`
- Individual results: `Vehicle-VIN-001: Reverted to version 1.0.0`
- Failed attempts: `Vehicle-VIN-002: Failed to revert`

**Learning Focus**:
- Complete firmware lifecycle from creation to rollback
- Package configuration and automatic shadow updates
- Device inventory management and tracking
- Fleet Indexing for version management operations

---

### scripts/manage_dynamic_groups.py
**Purpose**: Comprehensive management of dynamic thing groups with Fleet Indexing validation using native boto3 APIs.

**Operations**:
1. **Create Dynamic Groups** - Two creation methods:
   - **Guided wizard**: Interactive criteria selection
   - **Custom query**: Direct Fleet Indexing query input
2. **List Dynamic Groups** - Display all groups with member counts and queries
3. **Delete Dynamic Groups** - Safe deletion with confirmation
4. **Test Queries** - Validate custom Fleet Indexing queries

**Create Methods**:
- **Guided Wizard** (all optional):
  - Countries: Single or multiple (e.g., US,CA,MX)
  - Thing Type: Vehicle category (e.g., SedanVehicle)
  - Versions: Single or multiple (e.g., 1.0.0,1.1.0)
  - Battery Level: Comparisons (e.g., >50, <30, =75)
- **Custom Query**: Direct Fleet Indexing query string input

**Features**:
- **Dual creation modes**: Guided wizard or custom query input
- Smart group naming (auto-generated or custom)
- Fleet Indexing query construction and validation
- **Real-time device matching preview** (shows matching devices before creation)
- Member count display for existing groups
- Safe deletion with confirmation prompts
- Custom query testing capabilities
- Query validation prevents empty group creation

**Query Examples**:
- Single criteria: `thingTypeName:SedanVehicle AND attributes.country:US`
- Multiple criteria: `thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- Package versions: `shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- Custom complex: `(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**Purpose**: Pre-publication syntax validation for CI/CD pipeline.

**Checks**:
- Python syntax validation for all scripts
- Import availability verification
- Requirements.txt validation
- Dependency listing

**Usage**: Automatically run by GitHub Actions workflow

---

## Script Dependencies

### Required Python Packages
- `boto3>=1.40.27` - AWS SDK for Python (latest version for package artifact support)
- `colorama>=0.4.4` - Terminal colors
- `requests>=2.25.1` - HTTP requests for Amazon S3 downloads

### AWS Services Used
- **AWS IoT Core** - Thing management, jobs, shadows
- **AWS IoT Device Management** - Software packages, Fleet Indexing
- **Amazon S3** - Firmware storage with versioning
- **AWS Identity and Access Management (IAM)** - Roles and policies for secure access

### AWS Credentials Requirements
- Configured credentials via:
  - `aws configure` (AWS CLI)
  - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - IAM roles (for EC2/Lambda execution)
  - AWS credentials file
- Appropriate IAM permissions for AWS IoT, Amazon S3, and IAM operations
- Region configuration (AWS_DEFAULT_REGION environment variable or credentials)

## Educational Features

### Learning Moments
Each script includes educational pauses explaining:
- AWS IoT concepts and architecture
- Best practices for device management
- Security considerations
- Scalability patterns

### Progress Tracking
- Real-time operation status
- Success/failure counts
- Performance metrics (TPS, duration)
- Color-coded output for easy reading

### Debug Mode
Available in all scripts:
- Shows all AWS SDK (boto3) API calls with parameters
- Displays complete API responses in JSON format
- Provides detailed error information with full stack traces
- **Sequential Processing**: Runs operations sequentially for clean debug output
- Helps with troubleshooting and learning AWS APIs

## Performance Characteristics

### Rate Limiting
Scripts respect AWS API limits:
- Thing operations: 80 TPS (100 TPS limit)
- Thing types: 8 TPS (10 TPS limit)
- Dynamic groups: 4 TPS (5 TPS limit)
- Job executions: 150 TPS (200 TPS limit)
- Package operations: 8 TPS (10 TPS limit)

### Parallel Processing
- **Native boto3 Integration**: Direct AWS SDK calls for better performance
- ThreadPoolExecutor for concurrent operations (when not in debug mode)
- **Intelligent Rate Limiting**: Semaphores respecting AWS API limits
- **Thread-Safe Progress Tracking**: Concurrent operation monitoring
- **Enhanced Error Handling**: Robust boto3 ClientError exception management
- **Debug Mode Override**: Sequential processing in debug mode for clean output

### Memory Management
- Streaming downloads for large files
- Temporary file cleanup
- Efficient JSON parsing
- Resource cleanup on exit