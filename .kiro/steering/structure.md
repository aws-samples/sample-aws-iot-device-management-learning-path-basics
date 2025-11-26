# Project Structure

## Root Directory
```
├── scripts/           # Main Python scripts for AWS IoT operations
├── i18n/             # Internationalization support
├── docs/             # Comprehensive documentation
├── .kiro/            # Kiro AI assistant configuration
├── .github/          # GitHub workflows and templates
├── requirements.txt  # Python dependencies
└── README.md         # Main project documentation
```

## Scripts Directory (`scripts/`)
Core operational scripts following a logical workflow sequence:

- **`provision_script.py`**: Infrastructure setup (devices, groups, packages, S3)
- **`manage_dynamic_groups.py`**: Dynamic device group management with Fleet Indexing
- **`manage_packages.py`**: Firmware package and version management
- **`create_job.py`**: OTA update job creation and deployment
- **`simulate_job_execution.py`**: Device behavior simulation during updates
- **`explore_jobs.py`**: Job monitoring and troubleshooting
- **`cleanup_script.py`**: Resource cleanup and cost management
- **`check_syntax.py`**: Code validation utility

## Internationalization (`i18n/`)
Multi-language support structure:

- **`common.json`**: Shared messages across all scripts
- **`loader.py`**: Message loading utility
- **`language_selector.py`**: Interactive language selection
- **`en/`**: English language files (script-specific messages)

## Documentation (`docs/`)
Comprehensive project documentation:

- **`DETAILED_SCRIPTS.md`**: In-depth script documentation
- **`EXAMPLES.md`**: Practical usage scenarios
- **`TROUBLESHOOTING.md`**: Common issues and solutions

## Naming Conventions

### Scripts
- Use descriptive names with underscores: `provision_script.py`
- Follow workflow sequence in naming and documentation
- Include `.py.backup` files for critical script versions

### AWS Resources
- **Thing Types**: `SedanVehicle`, `SUVVehicle`, `TruckVehicle`
- **Devices**: VIN-style naming `Vehicle-VIN-001`
- **Groups**: Country-based `Fleet-{country_code}`
- **Jobs**: Timestamp-based `firmware-update-{timestamp}`
- **S3 Buckets**: `iot-firmware-{account_id}-{region}`

### Code Organization
- **Class Names**: PascalCase (`PackageManager`, `DeviceProvisioner`)
- **Method Names**: snake_case (`safe_api_call`, `create_thing_type`)
- **Constants**: UPPER_SNAKE_CASE (`CONTINENTS`, `LANGUAGE_CODES`)

## File Patterns
- All Python scripts include shebang: `#!/usr/bin/env python3`
- Consistent import order: standard library, third-party, local imports
- Main execution scripts include `if __name__ == "__main__":` pattern
- Configuration through environment variables with sensible defaults