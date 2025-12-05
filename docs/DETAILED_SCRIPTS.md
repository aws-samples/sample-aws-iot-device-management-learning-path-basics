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

**Command-Line Parameters**:
- `--things-prefix PREFIX` - Custom prefix for thing names (default: "Vehicle-VIN-")
  - Must be 1-20 characters
  - Alphanumeric, hyphens, underscores, and colons only
  - Example: `--things-prefix "Fleet-Device-"` creates Fleet-Device-001, Fleet-Device-002, etc.

**Resource Tagging Behavior**:
All created resources are automatically tagged with:
- `workshop=learning-aws-iot-dm-basics` - Identifies workshop resources
- `creation-date=YYYY-MM-DD` - Timestamp for tracking

**Tagged Resources**:
- Thing types
- Thing groups (static groups)
- Software packages
- Software package versions
- Jobs
- S3 buckets
- IAM roles

**Tag Failure Handling**:
- Tagging failures don't prevent resource creation
- Script continues with warnings for failed tags
- Summary report shows resources without tags
- Cleanup script uses naming patterns as fallback

**Educational Pauses**: 8 learning moments explaining IoT concepts

**Rate Limits**: Intelligent AWS API throttling (80 TPS for things, 8 TPS for thing types)

**Performance**: Parallel execution when not in debug mode, sequential in debug mode for clean output

**Resource Tagging**:
- **Automatic Workshop Tags**: All taggable resources receive `workshop=learning-aws-iot-dm-basics` tag
- **Supported Resources**: Thing types, thing groups, packages, jobs, S3 buckets, IAM roles
- **Non-Taggable Resources**: Things, certificates, and shadows rely on naming conventions
- **Tag Failure Handling**: Graceful degradation - continues resource creation if tagging fails
- **Cleanup Integration**: Tags enable safe identification during cleanup operations

**Thing Naming Convention**:
- **--things-prefix Parameter**: Configurable prefix for thing names (default: "Vehicle-VIN-")
- **Naming Pattern**: `{prefix}{sequential_number}` (e.g., Vehicle-VIN-001, Vehicle-VIN-002)
- **Sequential Numbering**: Zero-padded 3-digit numbers (001-999)
- **Prefix Validation**: Alphanumeric, hyphens, underscores, colons only; max 20 characters
- **Legacy Support**: Also recognizes old `vehicle-{country}-{type}-{index}` pattern
- **Cleanup Integration**: Naming patterns enable identification of non-taggable resources

**Usage Examples**:
```bash
# Use default prefix (Vehicle-VIN-)
python scripts/provision_script.py

# Use custom prefix
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Custom prefix creates: Fleet-Device-001, Fleet-Device-002, etc.
```

---

### scripts/cleanup_script.py
**Purpose**: Safe removal of AWS IoT resources to avoid ongoing costs using native boto3 APIs with intelligent resource identification.

**Cleanup Options**:
1. **ALL resources** - Complete infrastructure cleanup
2. **Things only** - Remove devices but keep infrastructure
3. **Thing groups only** - Remove groupings but keep devices

**Command-Line Parameters**:
- `--things-prefix PREFIX` - Custom prefix for thing identification (default: "Vehicle-VIN-")
  - Must match the prefix used during provisioning
  - Used for identifying things with custom naming patterns
  - Example: `--things-prefix "Fleet-Device-"` identifies Fleet-Device-001, Fleet-Device-002, etc.
- `--dry-run` - Preview what would be deleted without making changes
  - Shows all resources that would be deleted
  - Displays identification method for each resource
  - No actual deletions performed
  - Useful for verifying cleanup scope before execution

**Resource Identification Methods**:

The cleanup script uses a three-tier identification system to safely identify workshop resources:

**1. Tag-Based Identification (Highest Priority)**:
- Checks for `workshop=learning-aws-iot-dm-basics` tag
- Most reliable method for resources created with tagging
- Works for: thing types, thing groups, packages, package versions, jobs, S3 buckets, IAM roles

**2. Naming Pattern Identification (Fallback)**:
- Matches resource names against workshop patterns
- Used when tags are not present or not supported
- Patterns include:
  - Things: `Vehicle-VIN-###` or custom prefix pattern (e.g., `Fleet-Device-###`)
  - Thing types: `SedanVehicle`, `SUVVehicle`, `TruckVehicle`
  - Thing groups: `Fleet-*` (static groups)
  - Dynamic groups: `DynamicGroup-*`
  - Packages: `SedanVehicle-Package`, `SUVVehicle-Package`, `TruckVehicle-Package`
  - Jobs: `OTA-Job-*`, `Command-Job-*`
  - S3 buckets: `iot-dm-workshop-*`
  - IAM roles: `IoTJobsRole`, `IoTPackageConfigRole`

**3. Association-Based Identification (For Non-Taggable Resources)**:
- Used for resources that cannot be tagged directly
- Certificates: Identified by attachment to workshop things
- Shadows: Identified by belonging to workshop things
- Ensures complete cleanup of dependent resources

**Identification Process**:
1. For each resource, check tags first
2. If no workshop tag found, check naming pattern
3. If no pattern match, check associations (for certificates/shadows)
4. If no identification method succeeds, resource is skipped
5. Debug mode shows which method identified each resource

**Features**:
- **Native boto3 Implementation**: No CLI dependencies, better error handling
- **Intelligent Resource Identification**: Three-tier system (tags → naming → associations)
- **Dry-Run Mode**: Preview deletions without making changes
- **Custom Prefix Support**: Identify things with custom naming patterns
- **Parallel processing** with intelligent rate limiting
- **Enhanced S3 Cleanup**: Proper versioned object deletion using paginators
- Distinguishes static vs dynamic groups automatically
- Handles thing type deprecation (5-minute wait)
- Cancels and deletes AWS IoT Jobs with status monitoring
- Comprehensive IAM role and policy cleanup
- Disables Fleet Indexing configuration
- **Shadow Cleanup**: Removes both classic and $package shadows
- **Principal Detachment**: Properly detaches certificates and policies
- **Comprehensive Reporting**: Shows deleted and skipped resources with counts

**Safety Features**:
- Requires typing "DELETE" to confirm (unless dry-run mode)
- Skips non-workshop resources automatically
- Shows summary of what will be deleted
- Dry-run mode for verification before actual deletion
- Error handling continues cleanup even if individual resources fail

**Dry-Run Mode Example**:
```bash
python scripts/cleanup_script.py --dry-run
```
Output shows:
- Resources that would be deleted (with identification method)
- Resources that would be skipped (non-workshop resources)
- Total counts by resource type
- No actual deletions performed

**Custom Prefix Example**:
```bash
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```
Identifies and deletes:
- Things matching Fleet-Device-### pattern
- Associated certificates and shadows
- Other workshop resources (identified by tags or patterns)

**Performance**: Parallel execution respecting AWS API limits (80 TPS things, 4 TPS dynamic groups)

**Tag-Based Cleanup Example**:
```
Scanning thing types...
Found 3 thing types
  ✓ SedanVehicle (identified by tag: workshop=learning-aws-iot-dm-basics)
  ✓ SUVVehicle (identified by tag: workshop=learning-aws-iot-dm-basics)
  ✓ TruckVehicle (identified by tag: workshop=learning-aws-iot-dm-basics)

Scanning thing groups...
Found 5 thing groups
  ✓ fleet-US (identified by tag: workshop=learning-aws-iot-dm-basics)
  ✓ fleet-CA (identified by tag: workshop=learning-aws-iot-dm-basics)
  ✗ production-fleet (skipped - no workshop tag)
```

**Naming-Based Cleanup Example**:
```
Scanning things...
Found 102 things
  ✓ Vehicle-VIN-001 (identified by naming pattern: Vehicle-VIN-###)
  ✓ Vehicle-VIN-002 (identified by naming pattern: Vehicle-VIN-###)
  ✓ vehicle-US-sedan-1 (identified by legacy pattern)
  ✗ production-device-001 (skipped - no pattern match)
```

**Association-Based Cleanup Example**:
```
Processing thing: Vehicle-VIN-001
  ✓ Classic shadow (identified by association with workshop thing)
  ✓ $package shadow (identified by association with workshop thing)
  ✓ Certificate abc123 (identified by association with workshop thing)
  
Processing thing: production-device-001
  ✗ Certificate xyz789 (skipped - attached to non-workshop thing)
```

**Cleanup Summary Output**:
```
Cleanup Summary:
================
Deleted Resources:
  - IoT Things: 100
  - Thing Groups: 5
  - Thing Types: 3
  - Packages: 3
  - Jobs: 2
  - S3 Buckets: 1
  - IAM Roles: 2
  Total: 116

Skipped Resources:
  - IoT Things: 2 (non-workshop resources)
  - Thing Groups: 1 (non-workshop resource)
  Total: 3

Execution Time: 45.3 seconds
```

**Troubleshooting Cleanup Issues**:

**Issue: Resources Not Being Deleted**

Symptoms:
- Cleanup script skips resources you expect to be deleted
- "Skipped resources" count is higher than expected
- Specific resources remain after cleanup

Solutions:
1. **Verify Thing Prefix Match**:
   ```bash
   # If you used custom prefix during provisioning:
   python scripts/provision_script.py --things-prefix "MyPrefix-"
   
   # You MUST use same prefix during cleanup:
   python scripts/cleanup_script.py --things-prefix "MyPrefix-"
   ```

2. **Check Resource Tags**:
   - Run cleanup in debug mode to see identification methods
   - Verify taggable resources have `workshop=learning-aws-iot-dm-basics` tag
   - Check AWS Console → IoT Core → Resource tags

3. **Verify Naming Patterns**:
   - Things should match: `{prefix}###` or `vehicle-{country}-{type}-{index}`
   - Groups should match: `fleet-{country}` or contain "workshop"
   - Use dry-run mode to see what would be identified

4. **Use Dry-Run First**:
   ```bash
   # Preview what will be deleted
   python scripts/cleanup_script.py --dry-run
   
   # Check output for skipped resources
   # Verify identification methods in debug mode
   ```

**Issue: Tag Application Failures During Provisioning**

Symptoms:
- Provision script shows "Failed to apply tags" warnings
- Resources created but without workshop tags
- Cleanup script skips resources that should be deleted

Solutions:
1. **Check IAM Permissions**:
   - Verify IAM user/role has tagging permissions
   - Required actions: `iot:TagResource`, `s3:PutBucketTagging`, `iam:TagRole`

2. **Rely on Naming Conventions**:
   - Resources without tags can still be identified by naming patterns
   - Ensure consistent naming during provisioning
   - Use same --things-prefix for provision and cleanup

3. **Manual Tag Addition** (if needed):
   ```bash
   # Add tags manually via AWS CLI
   aws iot tag-resource --resource-arn <arn> --tags workshop=learning-aws-iot-dm-basics
   ```

**Issue: Cleanup Deletes Wrong Resources**

Symptoms:
- Non-workshop resources being identified for deletion
- Dry-run shows unexpected resources

Solutions:
1. **Always Use Dry-Run First**:
   ```bash
   python scripts/cleanup_script.py --dry-run
   ```

2. **Review Naming Patterns**:
   - Ensure production resources don't match workshop patterns
   - Avoid using "Vehicle-VIN-" prefix for production things
   - Don't use "fleet-" prefix for production groups

3. **Check Tag Conflicts**:
   - Verify no production resources have workshop tags
   - Review tag policies in your AWS account

**Issue: Cleanup Fails with Permission Errors**

Symptoms:
- "AccessDeniedException" or "UnauthorizedException" errors
- Partial cleanup completion
- Some resource types deleted, others skipped

Solutions:
1. **Verify IAM Permissions**:
   - Required permissions listed in README.md
   - Check IAM policy for all required actions
   - Verify permissions for: IoT, S3, IAM, Fleet Indexing

2. **Check Resource Policies**:
   - S3 bucket policies may block deletion
   - IAM role trust policies may prevent deletion
   - Review resource-level policies

3. **Use Debug Mode**:
   ```bash
   # Run with debug to see exact API errors
   python scripts/cleanup_script.py
   # Answer 'y' for debug mode
   ```

**Issue: Cleanup Takes Too Long**

Symptoms:
- Cleanup runs for extended periods
- Progress appears slow
- Timeout errors

Solutions:
1. **Expected Duration**:
   - 100 things: ~2-3 minutes
   - 1000 things: ~15-20 minutes
   - Thing type deletion: +5 minutes (required deprecation wait)

2. **Rate Limiting**:
   - Script respects AWS API limits automatically
   - Parallel processing optimizes performance
   - Debug mode runs sequentially (slower but clearer output)

3. **Monitor Progress**:
   - Watch real-time progress indicators
   - Check AWS Console for deletion status
   - Use debug mode to see each operation

**Issue: Dry-Run Shows Different Results Than Actual Cleanup**

Symptoms:
- Dry-run identifies resources that actual cleanup skips
- Inconsistent behavior between modes

Solutions:
1. **Resource State Changes**:
   - Resources may be modified between dry-run and actual cleanup
   - Tags may be added/removed by other processes
   - Re-run dry-run immediately before actual cleanup

2. **Concurrent Modifications**:
   - Other users/processes may be modifying resources
   - Coordinate cleanup timing with team
   - Use resource locking if available

3. **Caching Issues**:
   - AWS API responses may be cached briefly
   - Wait a few seconds between dry-run and actual cleanup
   - Refresh AWS Console to verify current state

**Issue: Partial Cleanup**

Symptoms:
- Some resources deleted, others remain
- Error messages during cleanup
- Incomplete cleanup results

Solutions:
1. **Dependency Issues**:
   - Some resources may fail to delete due to dependencies
   - Script continues with remaining resources
   - Check error messages for specific failures
   - Re-run script to clean up remaining resources

2. **Resource State**:
   - Thing types must be deprecated before deletion (5-minute wait)
   - Jobs must be canceled before deletion
   - S3 buckets must be empty before deletion

3. **Re-run Cleanup**:
   ```bash
   # Run cleanup again to catch remaining resources
   python scripts/cleanup_script.py
   ```

**Best Practices for Safe Cleanup**:

1. **Always Start with Dry-Run**:
   ```bash
   python scripts/cleanup_script.py --dry-run
   ```

2. **Verify Thing Prefix Match**:
   - Use same --things-prefix as provisioning
   - Document custom prefixes for team reference

3. **Use Debug Mode for Troubleshooting**:
   - See identification methods for each resource
   - Understand why resources are skipped
   - Verify tag and naming pattern matches

4. **Coordinate with Team**:
   - Communicate cleanup timing
   - Verify no active workshops using resources
   - Document cleanup results

5. **Monitor AWS Console**:
   - Verify resources deleted as expected
   - Check for any remaining workshop resources
   - Review CloudWatch logs if available

6. **Keep Consistent Naming**:
   - Use standard prefixes across workshops
   - Document naming conventions
   - Avoid production naming conflicts

**Tag-Based Cleanup Not Working**:
- Verify resources were created with tagging enabled
- Check if tagging failed during provisioning (see provision script output)
- Naming pattern identification will be used as fallback
- Consider using `--dry-run` to verify identification methods

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
5. **Cancel job** - Cancel active jobs with impact analysis and educational guidance
6. **Delete job** - Delete completed/canceled jobs with automatic force flag handling
7. **View statistics** - Comprehensive job analytics with health assessment and recommendations

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
- **Job Lifecycle Management**: Cancel and delete operations with safety confirmations
- **Advanced Analytics**: Comprehensive statistics with health assessments

**Cancel Job Features**:
- Scans for active jobs (IN_PROGRESS, SCHEDULED)
- Shows job details and target count
- Impact analysis with execution counts by status (QUEUED, IN_PROGRESS, SUCCEEDED, FAILED)
- Educational content explaining when and why to cancel jobs
- Safety confirmation requiring "CANCEL" to proceed
- Optional cancellation comment for audit trail
- Real-time status updates

**Delete Job Features**:
- Scans for deletable jobs (COMPLETED, CANCELED)
- Shows job completion timestamps
- Checks execution history to determine if force flag needed
- Educational content about deletion implications
- Automatic force flag when executions exist
- Safety confirmation requiring "DELETE" to proceed
- Explains difference between cancel and delete operations

**View Statistics Features**:
- Comprehensive job overview (status, created/completed dates, targets)
- Execution statistics with percentages by status
- Success/failure rate calculations
- Detailed breakdown of all execution states
- Health assessment (Excellent ≥95%, Good ≥80%, Poor ≥50%, Critical <50%)
- Educational content about execution states and failure patterns
- Context-aware recommendations based on job state:
  - No executions: Check device connectivity and group membership
  - Canceled early: Review cancellation reasons
  - Devices removed: Verify device existence
  - In progress: Wait and monitor
  - High failure rate: Investigate and consider cancellation
  - Moderate failure: Monitor closely
  - Excellent performance: Document success patterns

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


---

### scripts/manage_commands.py
**Purpose**: Comprehensive management of AWS IoT Commands for sending real-time commands to IoT devices using native boto3 APIs.

**Operations**:
1. **Create Command** - Create new command templates with payload format definitions
2. **List Commands** - Display all command templates (predefined and custom)
3. **View Command Details** - Show complete command template specifications
4. **Delete Command** - Remove custom command templates with safety confirmations
5. **Execute Command** - Send commands to devices or thing groups
6. **View Command Status** - Monitor command execution progress and results
7. **View Command History** - Browse past command executions with filtering
8. **Cancel Command** - Cancel pending or in-progress command executions
9. **Enable/Disable Debug Mode** - Toggle detailed API logging
10. **Exit** - Exit the script

**Key Features**:
- **Native boto3 Implementation**: Direct AWS IoT Commands API integration
- **Predefined Automotive Templates**: Six ready-to-use vehicle command templates
- **Command Template Management**: Create, list, view, and delete command templates
- **Command Execution**: Send commands to individual devices or thing groups
- **Status Monitoring**: Real-time command execution tracking with progress indicators
- **Command History**: Browse and filter past command executions
- **Command Cancellation**: Cancel pending or in-progress commands
- **IoT Core Scripts Integration**: Seamless integration with certificate_manager and mqtt_client_explorer
- **MQTT Topic Documentation**: Complete topic structure reference
- **Device Simulation Examples**: Success and failure response payloads
- **Educational Approach**: Learning moments throughout workflows
- **Multilingual Support**: Full i18n support for 6 languages

**Predefined Automotive Command Templates**:
The script includes six predefined command templates for common vehicle operations:

1. **vehicle-lock** - Lock vehicle doors remotely
   - Payload: `{"action": "lock", "vehicleId": "string"}`
   - Use case: Remote door locking for security

2. **vehicle-unlock** - Unlock vehicle doors remotely
   - Payload: `{"action": "unlock", "vehicleId": "string"}`
   - Use case: Remote door unlocking for access

3. **start-engine** - Start vehicle engine remotely
   - Payload: `{"action": "start", "vehicleId": "string", "duration": "number"}`
   - Use case: Remote engine start for climate control

4. **stop-engine** - Stop vehicle engine remotely
   - Payload: `{"action": "stop", "vehicleId": "string"}`
   - Use case: Emergency engine shutdown

5. **set-climate** - Set vehicle climate temperature
   - Payload: `{"action": "setClimate", "vehicleId": "string", "temperature": "number", "unit": "string"}`
   - Use case: Pre-conditioning vehicle temperature

6. **activate-horn** - Activate vehicle horn
   - Payload: `{"action": "horn", "vehicleId": "string", "duration": "number"}`
   - Use case: Vehicle location assistance

**Command Template Management**:

**Create Command Template**:
- Interactive prompts for command name, description, and payload format
- JSON schema validation for payload structure
- AWS-IoT namespace configuration
- Binary blob payload handling with contentType
- Automatic ARN generation and display
- Validation against AWS IoT Commands requirements:
  - Name: 1-128 characters, alphanumeric/hyphen/underscore, must start with alphanumeric
  - Description: 1-256 characters
  - Payload: Valid JSON schema, max 10KB complexity

**List Command Templates**:
- Displays both predefined and custom templates
- Color-coded table format with:
  - Template name
  - Description
  - Creation date
  - Template ARN
  - Status (ACTIVE, DEPRECATED, PENDING_DELETION)
- Interactive navigation to view template details
- Pagination support for large template lists

**View Command Details**:
- Complete payload format specification display
- Parameter names, types, and constraints
- Required vs optional fields
- Example parameter values
- Template metadata (creation date, ARN, status)
- Clean JSON formatting for payload structure

**Delete Command Template**:
- Safety confirmation requiring "DELETE" to proceed
- Verification that no active commands use the template
- Protection against deleting predefined templates
- Clear error messages for deletion failures
- Automatic cleanup of template resources

**Command Execution**:

**Execute Command**:
- Interactive command template selection from available templates
- Target selection:
  - Single device (thing name)
  - Thing group (group name)
- Target validation:
  - Device existence check in IoT registry
  - Thing group validation with member count display
- Parameter collection matching template payload format
- Configurable execution timeout (default 60 seconds)
- Automatic MQTT topic publication to:
  - `$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/json`
- Success display with:
  - Command execution ID
  - Initial status (CREATED/IN_PROGRESS)
  - MQTT topic information
- Multiple target support (creates separate executions per target)

**Command Status Monitoring**:

**View Command Status**:
- Real-time status retrieval using GetCommandExecution API
- Status display includes:
  - Command execution ID
  - Target device/group name
  - Current status (CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED)
  - Creation timestamp
  - Last updated timestamp
- Progress indicators for IN_PROGRESS status:
  - Animated progress display
  - Time elapsed since creation
- Completed command information:
  - Final status (SUCCEEDED/FAILED)
  - Execution duration
  - Status reason (if provided)
  - Completion timestamp
- Color-coded status indicators:
  - Green: SUCCEEDED
  - Yellow: IN_PROGRESS, CREATED
  - Red: FAILED, TIMED_OUT, CANCELED

**View Command History**:
- Comprehensive command execution history
- Filtering options:
  - Device name filter
  - Status filter (CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED)
  - Time range filter (start/end timestamps)
- Pagination support:
  - Configurable page size (1-100, default 50)
  - Next page navigation
  - Total count display
- History display includes:
  - Command name
  - Target device/group
  - Execution status
  - Creation time
  - Completion time (if applicable)
  - Execution duration
- Empty history handling with informative message
- Color-coded status for easy scanning

**Command Cancellation**:

**Cancel Command**:
- Interactive command execution ID input
- Safety confirmation requiring "CANCEL" to proceed
- Cancellation request submission to AWS IoT
- Status update verification (CANCELED)
- Rejection handling for completed commands:
  - Clear error message for already completed commands
  - Current command state display
- Failure information display:
  - Failure reason
  - Current command status
  - Troubleshooting suggestions

**IoT Core Scripts Integration**:

The script provides comprehensive integration guidance for using AWS IoT Core scripts to simulate device-side command handling:

**Certificate Manager Integration** (`certificate_manager.py`):
- Device certificate creation and management
- Certificate-to-policy association
- Certificate-to-thing attachment
- Authentication setup for MQTT connections
- Step-by-step terminal setup instructions:
  1. Open new terminal window (Terminal 2)
  2. Copy AWS credentials from workshop environment
  3. Navigate to IoT Core scripts directory
  4. Run certificate_manager.py to set up device authentication

**MQTT Client Explorer Integration** (`mqtt_client_explorer.py`):
- Command topic subscription setup
- Real-time command reception
- Response payload publishing
- Success/failure simulation
- Step-by-step integration workflow:
  1. Subscribe to command request topic: `$aws/commands/things/<ThingName>/executions/+/request/#`
  2. Receive command payloads with execution ID
  3. Publish execution result to response topic: `$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/json`
  4. Optionally subscribe to accepted/rejected topics for confirmation

**Device Simulation Examples**:

The script provides complete example payloads for simulating device responses:

**Success Response Example**:
```json
{
  "status": "SUCCEEDED",
  "executionId": "<ExecutionId>",
  "statusReason": "Vehicle doors locked successfully",
  "timestamp": 1701518710000
}
```

**Failure Response Example**:
```json
{
  "status": "FAILED",
  "executionId": "<ExecutionId>",
  "statusReason": "Unable to lock vehicle - door sensor malfunction",
  "timestamp": 1701518710000
}
```

**Valid Status Values**: SUCCEEDED, FAILED, IN_PROGRESS, TIMED_OUT, REJECTED

**MQTT Topic Structure**:

The script documents the complete MQTT topic structure for AWS IoT Commands:

**Command Request Topic** (device subscribes to receive commands):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request
```

**Command Response Topic** (device publishes execution result):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/<PayloadFormat>
```

**Response Accepted Topic** (device subscribes for confirmation):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted
```

**Response Rejected Topic** (device subscribes for rejection notification):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected
```

**Topic Component Explanations**:
- `<ThingName>`: Name of the IoT thing or MQTT client ID
- `<ExecutionId>`: Unique identifier for each command execution (use `+` wildcard to subscribe to all)
- `<PayloadFormat>`: Format indicator (json, cbor) - may be omitted if not JSON/CBOR
- Wildcard subscription: `$aws/commands/things/<ThingName>/executions/+/request/#`

**AWS IoT Test Client Alternative**:
- Console-based alternative to mqtt_client_explorer
- Access via AWS IoT Console → Test → MQTT test client
- Subscribe to command topics
- Publish response payloads
- Useful for quick testing without local scripts

**Learning Moments**:

The script includes contextual learning moments that automatically appear after key operations:

1. **What are Command Templates?** - Displayed after first template creation
   - Explains command template purpose and structure
   - Describes payload format requirements
   - Compares to other AWS IoT features

2. **Commands vs Device Shadow vs Jobs** - Displayed after first command execution
   - Comparison table showing when to use each feature
   - Commands: Immediate, real-time device actions (seconds)
   - Device Shadow: Desired state synchronization (eventual consistency)
   - Jobs: Long-running operations, firmware updates (minutes to hours)
   - Use case examples for each feature

3. **MQTT Topic Structure** - Displayed when showing mqtt_client_explorer integration
   - Complete topic pattern documentation
   - Request/response topic explanations
   - Wildcard subscription examples
   - Topic component descriptions

4. **Command Execution Lifecycle** - Displayed after viewing command status
   - Status transition flow (CREATED → IN_PROGRESS → SUCCEEDED/FAILED)
   - Timeout handling
   - Cancellation behavior
   - Best practices for monitoring

5. **Best Practices** - Displayed after viewing command history
   - Command naming conventions
   - Timeout configuration guidance
   - Error handling strategies
   - Monitoring and alerting recommendations

6. **Console Integration** - Displayed with Console Checkpoint reminder
   - AWS IoT Console navigation
   - Command template verification
   - Execution timeline viewing
   - CLI vs Console comparison

**Error Handling**:

The script implements comprehensive error handling with user-friendly messages:

**Validation Errors**:
- Command name validation (length, characters, format)
- Description validation (length, content)
- Payload format validation (JSON schema, complexity)
- Target validation (device/group existence)
- Parameter validation (type, required fields)
- Clear error messages with correction guidance

**AWS API Errors**:
- ResourceNotFoundException: Command or target not found
- InvalidRequestException: Invalid payload or parameters
- ThrottlingException: Rate limit exceeded with retry guidance
- UnauthorizedException: Insufficient permissions
- Exponential backoff for rate limiting
- Automatic retry for transient errors (up to 3 attempts)
- Detailed error messages with troubleshooting suggestions

**Network Errors**:
- Connectivity issue detection
- AWS credentials verification guidance
- Region configuration checks
- Retry options with user prompts

**State Errors**:
- Cancellation of completed commands
- Deletion of in-use templates
- Invalid status transitions
- Clear explanations of current state

**Debug Mode**:
- Shows all AWS SDK (boto3) API calls with parameters
- Displays complete API responses in JSON format
- Provides detailed error information with full stack traces
- Helps with troubleshooting and learning AWS APIs
- Toggle on/off during script execution

**Performance Characteristics**:
- **Native boto3 Integration**: Direct AWS SDK calls for better performance
- **Rate Limiting**: Respects AWS IoT Commands API limits
- **Efficient Pagination**: Handles large command lists and history
- **Memory Management**: Efficient JSON parsing and resource cleanup
- **Error Recovery**: Automatic retry with exponential backoff

**Educational Focus**:
- Complete command lifecycle from template creation to execution
- Real-time command delivery and acknowledgment
- Device simulation using IoT Core scripts
- MQTT topic structure and message flow
- Commands vs Shadow vs Jobs decision guidance
- Best practices for production deployments

**Troubleshooting Guide**:

**Common Issues and Solutions**:

1. **Device Not Receiving Commands**
   - Verify device is subscribed to command request topic
   - Check MQTT connection status
   - Confirm certificate and policy permissions
   - Verify thing name matches target
   - Ensure device simulator is running BEFORE executing commands

2. **Template Validation Errors**
   - Check JSON schema syntax
   - Verify payload format complexity (max 10KB)
   - Ensure required fields are defined
   - Validate parameter types and constraints

3. **Command Execution Failures**
   - Verify target device/group exists
   - Check IAM permissions for AWS IoT Commands
   - Confirm AWS region configuration
   - Review command timeout settings

4. **Status Not Updating**
   - Verify device published response to correct topic
   - Check response payload format
   - Confirm execution ID matches
   - Review device logs for errors

5. **Cancellation Failures**
   - Verify command is not already completed
   - Check command execution status
   - Confirm IAM permissions for cancellation
   - Review current command state

**Integration Workflow** (Correct Order):

⚠️ **CRITICAL**: The device simulator MUST be running and subscribed to command topics BEFORE executing commands. Commands are ephemeral by default - if no device is listening when the command is published, it will be lost.

1. **Open Terminal 2 FIRST** - Copy AWS credentials
2. Navigate to IoT Core scripts directory
3. Run `certificate_manager.py` to set up device authentication
4. Run `mqtt_client_explorer.py` to subscribe to command topics
5. **Verify device simulator is ready** - Should show "Subscribed to command topics"
6. **Now open Terminal 1** - Run `manage_commands.py`
7. Create command template
8. Execute command targeting the device
9. **Device Simulator** (Terminal 2) receives command and displays payload
10. **Device Simulator** publishes acknowledgment to response topic
11. Return to Terminal 1 to view updated command status

**Why This Order Matters**: Without persistent sessions enabled, MQTT messages are not queued for offline devices. The device must be actively subscribed to the command topic when AWS IoT publishes the command, otherwise the command will not be delivered.

**Use Cases**:

**Fleet-Wide Emergency Commands**:
- Send emergency stop commands to all vehicles in a region
- Execute safety recalls across entire fleet
- Coordinate responses to security threats
- Real-time fleet-wide configuration updates

**Remote Diagnostics and Control**:
- Lock/unlock vehicles remotely for customer support
- Adjust climate settings before customer arrival
- Activate horn for vehicle location assistance
- Collect diagnostic data on demand

**Production Deployment Patterns**:
- Command template versioning and management
- Multi-region command execution
- Command execution monitoring and alerting
- Integration with fleet management systems
- Compliance and audit logging

**Commands vs Device Shadow vs Jobs Decision Guide**:

Use **Commands** when:
- Immediate action required (seconds response time)
- Real-time device control needed
- Quick acknowledgment expected
- Device must be online
- Examples: lock/unlock, horn activation, emergency stop

Use **Device Shadow** when:
- Desired state synchronization needed
- Offline device support required
- Eventual consistency acceptable
- State persistence important
- Examples: temperature settings, configuration, desired state

Use **Jobs** when:
- Long-running operations required (minutes to hours)
- Firmware updates needed
- Batch device management
- Progress tracking important
- Examples: firmware updates, certificate rotation, bulk configuration

**AWS Services Integration**:
- **AWS IoT Core**: Command template storage and execution
- **AWS IoT Device Management**: Fleet management and targeting
- **AWS Identity and Access Management (IAM)**: Permissions and policies
- **Amazon CloudWatch**: Monitoring and logging (optional)

**Security Considerations**:
- IAM permissions for command operations
- Certificate-based device authentication
- Policy-based authorization for MQTT topics
- Command payload encryption in transit
- Audit logging for compliance

**Cost Optimization**:
- Commands are charged per execution
- No storage costs for command templates
- Efficient targeting reduces unnecessary executions
- Monitor command history for usage patterns
- Consider batch operations for cost efficiency
