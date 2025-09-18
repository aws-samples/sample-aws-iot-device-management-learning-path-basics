# Usage Examples

This document provides practical examples for common AWS IoT Device Management scenarios.

## Quick Start Examples

### Basic Fleet Setup
```bash
# 1. Create infrastructure
python scripts/provision_script.py
# Choose: SedanVehicle,SUVVehicle
# Versions: 1.0.0,1.1.0
# Region: North America
# Countries: US,CA
# Devices: 100

# 2. Create dynamic groups
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Countries: US
# Thing type: SedanVehicle
# Battery level: <30

# 3. Create firmware update job
python scripts/create_job.py
# Select: USFleet group
# Package: SedanVehicle v1.1.0

# 4. Simulate device updates
python scripts/simulate_job_execution.py
# Success rate: 85%
# Process: ALL executions
```

### Version Rollback Scenario
```bash
# Rollback all SedanVehicle devices to version 1.0.0
python scripts/manage_packages.py
# Select: 10. Revert Device Versions
# Thing type: SedanVehicle
# Target version: 1.0.0
# Confirm: REVERT
```

### Job Monitoring
```bash
# Monitor job progress
python scripts/explore_jobs.py
# Option 1: List all jobs
# Option 4: List job executions for specific job
```

## Advanced Scenarios

### Multi-Region Deployment
```bash
# Provision in multiple regions
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# Create 500 devices in North America

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# Create 300 devices in Europe
```

### Staged Rollout
```bash
# 1. Create test group
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Countries: US
# Thing type: SedanVehicle
# Versions: 1.0.0
# Custom name: TestFleet_SedanVehicle_US

# 2. Deploy to test group first
python scripts/create_job.py
# Select: TestFleet_SedanVehicle_US
# Package: SedanVehicle v1.1.0

# 3. Monitor test deployment
python scripts/simulate_job_execution.py
# Success rate: 95%

# 4. Deploy to production after validation
python scripts/create_job.py
# Select: USFleet
# Package: SedanVehicle v1.1.0
```

### Battery-Based Maintenance
```bash
# Create low battery group
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Method: 1 (Guided wizard)
# Countries: (leave empty for all)
# Thing type: (leave empty for all)
# Battery level: <20
# Custom name: LowBatteryDevices

# Create maintenance job
python scripts/create_job.py
# Select: LowBatteryDevices
# Package: MaintenanceFirmware v2.0.0
```

### Advanced Custom Query
```bash
# Create complex group with custom query
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Method: 2 (Custom query)
# Query: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# Group name: USVehicles_MidBattery
```

### Package Management
```bash
# Create new package and versions
python scripts/manage_packages.py
# Operation: 1 (Create Package)
# Package name: TestVehicle

# Add version with S3 upload
# Operation: 2 (Create Version)
# Package name: TestVehicle
# Version: 2.0.0

# Inspect package details
# Operation: 4 (Describe Package)
# Package name: TestVehicle
```

## Development Workflows

### Testing New Firmware
```bash
# 1. Provision test environment
python scripts/provision_script.py
# Thing types: TestSensor
# Versions: 1.0.0,2.0.0-beta
# Countries: US
# Devices: 10

# 2. Create beta test group
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Thing type: TestSensor
# Versions: 1.0.0
# Custom name: BetaTestGroup

# 3. Deploy beta firmware
python scripts/create_job.py
# Select: BetaTestGroup
# Package: TestSensor v2.0.0-beta

# 4. Simulate with high failure rate for testing
python scripts/simulate_job_execution.py
# Success rate: 60%

# 5. Analyze results
python scripts/explore_jobs.py
# Option 4: List job executions
```

### Cleanup After Testing
```bash
# Clean up test resources
python scripts/cleanup_script.py
# Option 1: ALL resources
# Confirm: DELETE
```

## Fleet Management Patterns

### Geographic Deployment
```bash
# Provision by continent
python scripts/provision_script.py
# Continent: 1 (North America)
# Countries: 3 (first 3 countries)
# Devices: 1000

# Create country-specific groups (auto-created as USFleet, CAFleet, MXFleet)
# Deploy region-specific firmware
python scripts/create_job.py
# Select: USFleet,CAFleet
# Package: RegionalFirmware v1.2.0
```

### Device Type Management
```bash
# Provision multiple vehicle types
python scripts/provision_script.py
# Thing types: SedanVehicle,SUVVehicle,TruckVehicle
# Versions: 1.0.0,1.1.0,2.0.0
# Devices: 500

# Create type-specific dynamic groups
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Thing type: TruckVehicle
# Countries: US,CA
# Custom name: NorthAmericaTrucks

# Deploy truck-specific firmware
python scripts/create_job.py
# Select: NorthAmericaTrucks
# Package: TruckVehicle v2.0.0
```

### Maintenance Scheduling
```bash
# Find devices needing updates
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Thing type: SedanVehicle
# Versions: 1.0.0  # Old version
# Custom name: SedanVehicle_NeedsUpdate

# Schedule maintenance window deployment
python scripts/create_job.py
# Select: SedanVehicle_NeedsUpdate
# Package: SedanVehicle v1.1.0

# Monitor deployment progress
python scripts/explore_jobs.py
# Option 1: List all jobs (check status)
```

## Troubleshooting Examples

### Failed Job Recovery
```bash
# 1. Check job status
python scripts/explore_jobs.py
# Option 2: Explore specific job
# Enter job ID with failures

# 2. Check individual device failures
python scripts/explore_jobs.py
# Option 3: Explore job execution
# Enter job ID and failing device name

# 3. Rollback failed devices
python scripts/manage_packages.py
# Select: 10. Revert Device Versions
# Thing type: SedanVehicle
# Target version: 1.0.0  # Previous working version
```

### Device State Verification
```bash
# Check current firmware versions
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Thing type: SedanVehicle
# Versions: 1.1.0
# Custom name: SedanVehicle_v1_1_0_Check

# Verify group membership (should match expected count)
python scripts/explore_jobs.py
# Use to verify device states
```

### Performance Testing
```bash
# Test with large device count
python scripts/provision_script.py
# Devices: 5000

# Test job execution performance
python scripts/simulate_job_execution.py
# Process: ALL
# Success rate: 90%
# Monitor execution time and TPS
```

## Environment-Specific Examples

### Development Environment
```bash
# Small scale for development
python scripts/provision_script.py
# Thing types: DevSensor
# Versions: 1.0.0-dev
# Countries: US
# Devices: 5
```

### Staging Environment
```bash
# Medium scale for staging
python scripts/provision_script.py
# Thing types: SedanVehicle,SUVVehicle
# Versions: 1.0.0,1.1.0-rc
# Countries: US,CA
# Devices: 100
```

### Production Environment
```bash
# Large scale for production
python scripts/provision_script.py
# Thing types: SedanVehicle,SUVVehicle,TruckVehicle
# Versions: 1.0.0,1.1.0,1.2.0
# Continent: 1 (North America)
# Countries: ALL
# Devices: 10000
```

## Integration Examples

### CI/CD Pipeline Integration
```bash
# Syntax check (automated)
python scripts/check_syntax.py

# Automated testing
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### Monitoring Integration
```bash
# Export job metrics
python scripts/explore_jobs.py --export-json > job_status.json

# Check deployment health
python scripts/explore_jobs.py --health-check
```

## Best Practices Examples

### Gradual Rollout
1. Start with 5% of fleet (test group)
2. Monitor for 24 hours
3. Expand to 25% if successful
4. Full deployment after validation

### Rollback Strategy
1. Always test rollback procedure
2. Keep previous firmware versions available
3. Monitor device health post-deployment
4. Have automated rollback triggers

### Resource Management
1. Use cleanup script after testing
2. Monitor AWS costs
3. Clean up old firmware versions
4. Remove unused thing groups