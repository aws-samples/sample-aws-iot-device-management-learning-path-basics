# Technology Stack

## Core Technologies
- **Python 3.10+**: Primary programming language
- **boto3**: Native AWS SDK for Python (>=1.40.27)
- **AWS IoT Core**: Device management and messaging
- **Amazon S3**: Firmware package storage with versioning
- **AWS IAM**: Role and policy management

## Dependencies
```
boto3>=1.40.27
colorama>=0.4.4
requests>=2.25.1
```

## Architecture Patterns
- **Native AWS SDK**: All scripts use boto3 directly (no CLI dependencies)
- **Parallel Processing**: Concurrent operations with intelligent rate limiting
- **Rate Limiting**: Automatic AWS API throttling compliance (80 TPS for things, 8 TPS for thing types)
- **Error Handling**: Robust boto3 exception handling with retry logic
- **Debug Mode**: Optional detailed API call logging for troubleshooting

## Code Conventions
- **Class-based Architecture**: Main functionality encapsulated in manager classes
- **Safe API Calls**: Centralized `safe_api_call()` method for error handling
- **Semaphore Control**: Thread-safe operations with configurable limits
- **Progress Tracking**: Real-time operation status with colorama formatting
- **Interactive UX**: User confirmation for destructive operations

## Common Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
aws configure
```

### Recommended Workflow
```bash
python scripts/provision_script.py        # Create infrastructure
python scripts/manage_dynamic_groups.py   # Create device groups
python scripts/manage_packages.py         # Manage firmware packages
python scripts/create_job.py              # Deploy firmware updates
python scripts/simulate_job_execution.py  # Simulate device updates
python scripts/explore_jobs.py            # Monitor job progress
python scripts/cleanup_script.py          # Clean up resources
```

### Debug Mode
Enable in any script for detailed troubleshooting:
```
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

## Performance Considerations
- Scripts automatically handle AWS API rate limits
- Parallel execution when not in debug mode
- Sequential execution in debug mode for clean output
- Intelligent semaphore control for concurrent operations