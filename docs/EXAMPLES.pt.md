# Exemplos de Uso

Este documento fornece exemplos práticos para cenários comuns do AWS IoT Device Management.

## Exemplos de Início Rápido

### Configuração Básica de Frota
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

### Cenário de Reversão de Versão
```bash
# Rollback all SedanVehicle devices to version 1.0.0
python scripts/manage_packages.py
# Select: 10. Revert Device Versions
# Thing type: SedanVehicle
# Target version: 1.0.0
# Confirm: REVERT
```

### Monitoramento e Gerenciamento de Trabalhos
```bash
# Monitor job progress
python scripts/explore_jobs.py
# Option 1: List all jobs
# Option 2: Explore specific job details
# Option 4: List job executions for specific job
# Option 7: View comprehensive statistics and health assessment

# Cancel stuck or problematic jobs
python scripts/explore_jobs.py
# Option 5: Cancel job
# - Shows impact analysis before cancellation
# - Provides educational guidance
# - Requires confirmation

# Clean up completed jobs
python scripts/explore_jobs.py
# Option 6: Delete job
# - Automatically handles force flag
# - Shows completion timestamps
# - Safe cleanup of old jobs
```

## Cenários Avançados

### Implantação Multi-Região
```bash
# Provision in multiple regions
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# Create 500 devices in North America

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# Create 300 devices in Europe
```

### Implantação Escalonada
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

### Manutenção Baseada em Bateria
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

### Consulta Personalizada Avançada
```bash
# Create complex group with custom query
python scripts/manage_dynamic_groups.py
# Operation: 1 (Create)
# Method: 2 (Custom query)
# Query: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# Group name: USVehicles_MidBattery
```

### Gerenciamento de Pacotes
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

### Exemplos de AWS IoT Commands

AWS IoT Commands permite enviar comandos em tempo real para dispositivos IoT através de tópicos MQTT. Estes exemplos demonstram criação de modelos, execução de comandos, monitoramento de status e simulação de dispositivos.

#### Exemplo 1: Criar e Executar um Comando Simples

Este exemplo mostra como criar um modelo de comando e executar um comando simples de travamento de veículo.

```bash
# 1. Start the manage_commands script
python scripts/manage_commands.py

# 2. Create a command template (Option 1)
# Select: 1. Create Command Template
# Template name: vehicle-lock
# Description: Lock vehicle doors remotely
# Payload format: {"action": "lock", "vehicleId": "{{vehicleId}}"}

# Expected output:
# ✓ Command template created successfully
# Template ARN: arn:aws:iot:us-east-1:123456789012:commandtemplate/vehicle-lock
# Template Name: vehicle-lock
# Description: Lock vehicle doors remotely

# 3. Execute the command (Option 5)
# Select: 5. Execute Command
# Select template: vehicle-lock
# Target device: vehicle-001
# Parameter vehicleId: vehicle-001

# Expected output:
# ✓ Command execution started
# Command ID: cmd-12345678-1234-1234-1234-123456789012
# Status: CREATED
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-001
# MQTT Topic: $aws/commands/things/vehicle-001/executions/exec-abc123/request/json
```

**Simulação de Dispositivo (usando mqtt_client_explorer.py):**
```bash
# In a separate terminal, subscribe to command topics
python scripts/mqtt_client_explorer.py
# Select: 2. Subscribe to topic
# Topic: $aws/commands/things/vehicle-001/executions/+/request/#

# When command is received, publish acknowledgment:
# Select: 1. Publish message
# Topic: $aws/commands/things/vehicle-001/executions/exec-abc123/response/json
# Message: {"status": "SUCCEEDED", "statusReason": "Vehicle locked successfully"}
```

#### Exemplo 2: Executar Comando em Múltiplos Dispositivos

Este exemplo demonstra a execução de um comando em múltiplos dispositivos simultaneamente.

```bash
# 1. Start manage_commands script
python scripts/manage_commands.py

# 2. Use predefined template (Option 2 to list templates)
# Select: 2. List Command Templates
# View available templates including predefined ones

# Expected output:
# ┌─────────────────────┬──────────────────────────────┬─────────────────────┐
# │ Template Name       │ Description                  │ Created At          │
# ├─────────────────────┼──────────────────────────────┼─────────────────────┤
# │ vehicle-lock        │ Lock vehicle doors remotely  │ 2024-12-02 10:00:00 │
# │ vehicle-unlock      │ Unlock vehicle doors         │ 2024-12-02 10:00:00 │
# │ start-engine        │ Start vehicle engine         │ 2024-12-02 10:00:00 │
# │ set-climate         │ Set climate temperature      │ 2024-12-02 10:00:00 │
# └─────────────────────┴──────────────────────────────┴─────────────────────┘

# 3. Execute command to multiple devices (Option 5)
# Select: 5. Execute Command
# Select template: set-climate
# Target type: Multiple devices
# Devices: vehicle-001,vehicle-002,vehicle-003
# Parameter temperature: 22
# Parameter unit: celsius

# Expected output:
# ✓ Command executions created for 3 devices
# Command IDs:
#   - vehicle-001: cmd-11111111-1111-1111-1111-111111111111
#   - vehicle-002: cmd-22222222-2222-2222-2222-222222222222
#   - vehicle-003: cmd-33333333-3333-3333-3333-333333333333
# Status: CREATED
# All commands published to respective MQTT topics
```

#### Exemplo 3: Monitorar Status do Comando

Este exemplo mostra como verificar o status dos comandos executados.

```bash
# 1. View command status (Option 6)
python scripts/manage_commands.py
# Select: 6. View Command Status
# Enter command ID: cmd-12345678-1234-1234-1234-123456789012

# Expected output for IN_PROGRESS command:
# Command Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-12345678-1234-1234-1234-123456789012
# Template: vehicle-lock
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-001
# Status: IN_PROGRESS ⏳
# Created: 2024-12-02 10:05:00
# Last Updated: 2024-12-02 10:05:05
# Duration: 5 seconds
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Expected output for SUCCEEDED command:
# Command Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-12345678-1234-1234-1234-123456789012
# Template: vehicle-lock
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-001
# Status: SUCCEEDED ✓
# Created: 2024-12-02 10:05:00
# Completed: 2024-12-02 10:05:15
# Duration: 15 seconds
# Status Reason: Vehicle locked successfully
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Expected output for FAILED command:
# Command Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-12345678-1234-1234-1234-123456789012
# Template: vehicle-unlock
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-002
# Status: FAILED ✗
# Created: 2024-12-02 10:10:00
# Completed: 2024-12-02 10:10:08
# Duration: 8 seconds
# Status Reason: Door sensor malfunction - unable to unlock
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Exemplo 4: Ver Histórico de Comandos com Filtros

Este exemplo demonstra a visualização do histórico de comandos com vários filtros.

```bash
# 1. View all command history (Option 7)
python scripts/manage_commands.py
# Select: 7. View Command History
# Filter by: None (show all)
# Page size: 10

# Expected output:
# Command History
# ┌──────────────────────┬─────────────┬──────────────┬────────────┬─────────────────────┬─────────────────────┐
# │ Command ID           │ Template    │ Target       │ Status     │ Created At          │ Completed At        │
# ├──────────────────────┼─────────────┼──────────────┼────────────┼─────────────────────┼─────────────────────┤
# │ cmd-12345678-...     │ vehicle-lock│ vehicle-001  │ SUCCEEDED  │ 2024-12-02 10:05:00 │ 2024-12-02 10:05:15 │
# │ cmd-22222222-...     │ set-climate │ vehicle-002  │ SUCCEEDED  │ 2024-12-02 10:08:00 │ 2024-12-02 10:08:12 │
# │ cmd-33333333-...     │ vehicle-unlock│ vehicle-003│ FAILED     │ 2024-12-02 10:10:00 │ 2024-12-02 10:10:08 │
# │ cmd-44444444-...     │ start-engine│ vehicle-001  │ IN_PROGRESS│ 2024-12-02 10:12:00 │ -                   │
# └──────────────────────┴─────────────┴──────────────┴────────────┴─────────────────────┴─────────────────────┘
# Total: 4 commands | Page 1 of 1

# 2. Filter by device (Option 7)
# Select: 7. View Command History
# Filter by: Device
# Device name: vehicle-001

# Expected output:
# Command History (Filtered by device: vehicle-001)
# ┌──────────────────────┬─────────────┬──────────────┬────────────┬─────────────────────┬─────────────────────┐
# │ Command ID           │ Template    │ Target       │ Status     │ Created At          │ Completed At        │
# ├──────────────────────┼─────────────┼──────────────┼────────────┼─────────────────────┼─────────────────────┤
# │ cmd-12345678-...     │ vehicle-lock│ vehicle-001  │ SUCCEEDED  │ 2024-12-02 10:05:00 │ 2024-12-02 10:05:15 │
# │ cmd-44444444-...     │ start-engine│ vehicle-001  │ SUCCEEDED  │ 2024-12-02 10:12:00 │ 2024-12-02 10:12:20 │
# └──────────────────────┴─────────────┴──────────────┴────────────┴─────────────────────┴─────────────────────┘
# Total: 2 commands

# 3. Filter by status (Option 7)
# Select: 7. View Command History
# Filter by: Status
# Status: FAILED

# Expected output:
# Command History (Filtered by status: FAILED)
# ┌──────────────────────┬─────────────┬──────────────┬────────────┬─────────────────────┬─────────────────────┐
# │ Command ID           │ Template    │ Target       │ Status     │ Created At          │ Completed At        │
# ├──────────────────────┼─────────────┼──────────────┼────────────┼─────────────────────┼─────────────────────┤
# │ cmd-33333333-...     │ vehicle-unlock│ vehicle-003│ FAILED     │ 2024-12-02 10:10:00 │ 2024-12-02 10:10:08 │
# └──────────────────────┴─────────────┴──────────────┴────────────┴─────────────────────┴─────────────────────┘
# Total: 1 command

# 4. Filter by time range (Option 7)
# Select: 7. View Command History
# Filter by: Time range
# Start time: 2024-12-02T10:00:00
# End time: 2024-12-02T10:10:00

# Expected output:
# Command History (Time range: 2024-12-02 10:00:00 to 2024-12-02 10:10:00)
# ┌──────────────────────┬─────────────┬──────────────┬────────────┬─────────────────────┬─────────────────────┐
# │ Command ID           │ Template    │ Target       │ Status     │ Created At          │ Completed At        │
# ├──────────────────────┼─────────────┼──────────────┼────────────┼─────────────────────┼─────────────────────┤
# │ cmd-12345678-...     │ vehicle-lock│ vehicle-001  │ SUCCEEDED  │ 2024-12-02 10:05:00 │ 2024-12-02 10:05:15 │
# │ cmd-22222222-...     │ set-climate │ vehicle-002  │ SUCCEEDED  │ 2024-12-02 10:08:00 │ 2024-12-02 10:08:12 │
# └──────────────────────┴─────────────┴──────────────┴────────────┴─────────────────────┴─────────────────────┘
# Total: 2 commands
```

#### Exemplo 5: Cancelar um Comando em Execução

Este exemplo mostra como cancelar um comando que está em andamento.

```bash
# 1. Check current command status
python scripts/manage_commands.py
# Select: 6. View Command Status
# Enter command ID: cmd-44444444-4444-4444-4444-444444444444

# Expected output:
# Command Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-44444444-4444-4444-4444-444444444444
# Template: start-engine
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-001
# Status: IN_PROGRESS ⏳
# Created: 2024-12-02 10:15:00
# Last Updated: 2024-12-02 10:15:30
# Duration: 30 seconds
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 2. Cancel the command (Option 8)
# Select: 8. Cancel Command
# Enter command ID: cmd-44444444-4444-4444-4444-444444444444
# Confirm cancellation: yes

# Expected output:
# ⚠ Cancel Command Confirmation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-44444444-4444-4444-4444-444444444444
# Template: start-engine
# Target: vehicle-001
# Current Status: IN_PROGRESS
# 
# Are you sure you want to cancel this command? (yes/no): yes
# 
# ✓ Command cancellation request sent
# Command ID: cmd-44444444-4444-4444-4444-444444444444
# New Status: CANCELED
# Cancellation Reason: User requested cancellation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 3. Verify cancellation
# Select: 6. View Command Status
# Enter command ID: cmd-44444444-4444-4444-4444-444444444444

# Expected output:
# Command Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-44444444-4444-4444-4444-444444444444
# Template: start-engine
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-001
# Status: CANCELED ⊗
# Created: 2024-12-02 10:15:00
# Canceled: 2024-12-02 10:15:45
# Duration: 45 seconds
# Status Reason: User requested cancellation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 4. Attempt to cancel completed command (will fail)
# Select: 8. Cancel Command
# Enter command ID: cmd-12345678-1234-1234-1234-123456789012

# Expected output:
# ✗ Cannot cancel command
# Command ID: cmd-12345678-1234-1234-1234-123456789012
# Current Status: SUCCEEDED
# Reason: Command has already completed
# 
# Note: Only commands with status CREATED or IN_PROGRESS can be canceled
```

#### Exemplo de Fluxo de Trabalho Completo: Parada de Emergência do Veículo

Este exemplo abrangente demonstra o fluxo de trabalho completo para um comando de parada de emergência.

```bash
# Step 1: Set up device simulator (Terminal 2)
# Navigate to IoT Core scripts directory
cd githubsdks/sample-aws-iot-core-learning-path-basics/scripts

# Set up device authentication
python certificate_manager.py
# Select device: vehicle-emergency-001
# Create and attach certificate

# Subscribe to command topics
python mqtt_client_explorer.py
# Select: 2. Subscribe to topic
# Topic: $aws/commands/things/vehicle-emergency-001/executions/+/request/#

# Step 2: Create emergency stop template (Terminal 1)
cd githubsdks/sample-aws-iot-device-management-learning-path-basics/scripts
python manage_commands.py

# Select: 1. Create Command Template
# Template name: emergency-stop
# Description: Emergency vehicle stop command
# Payload format: {"action": "emergency_stop", "vehicleId": "{{vehicleId}}", "reason": "{{reason}}"}

# Step 3: Execute emergency stop command
# Select: 5. Execute Command
# Template: emergency-stop
# Target: vehicle-emergency-001
# Parameter vehicleId: vehicle-emergency-001
# Parameter reason: Suspected theft

# Expected output:
# ✓ Command execution started
# Command ID: cmd-emergency-12345
# Status: CREATED
# MQTT Topic: $aws/commands/things/vehicle-emergency-001/executions/exec-xyz/request/json

# Step 4: Device receives command (Terminal 2 - mqtt_client_explorer)
# Received message on topic: $aws/commands/things/vehicle-emergency-001/executions/exec-xyz/request/json
# Payload: {"action": "emergency_stop", "vehicleId": "vehicle-emergency-001", "reason": "Suspected theft"}

# Step 5: Device acknowledges (Terminal 2)
# Select: 1. Publish message
# Topic: $aws/commands/things/vehicle-emergency-001/executions/exec-xyz/response/json
# Message: {"status": "SUCCEEDED", "statusReason": "Vehicle stopped and immobilized"}

# Step 6: Verify command completion (Terminal 1)
# Select: 6. View Command Status
# Command ID: cmd-emergency-12345

# Expected output:
# Command Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Command ID: cmd-emergency-12345
# Template: emergency-stop
# Target: arn:aws:iot:us-east-1:123456789012:thing/vehicle-emergency-001
# Status: SUCCEEDED ✓
# Created: 2024-12-02 10:20:00
# Completed: 2024-12-02 10:20:05
# Duration: 5 seconds
# Status Reason: Vehicle stopped and immobilized
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Step 7: View command in history
# Select: 7. View Command History
# Filter: None

# Command appears in history with SUCCEEDED status
```

#### Melhores Práticas para AWS IoT Commands

1. **Template Management**
   - Create reusable templates for common operations
   - Use descriptive names and detailed descriptions
   - Validate payload formats before creating templates
   - Keep templates organized by use case

2. **Command Execution**
   - Always verify device is online before sending commands
   - Use appropriate timeout values for command responses
   - Monitor command status for critical operations
   - Implement retry logic for failed commands

3. **Device Simulation**
   - Set up device simulator before executing commands
   - Subscribe to command topics using wildcards for flexibility
   - Test both success and failure scenarios
   - Publish detailed status reasons for troubleshooting

4. **Monitoring and Troubleshooting**
   - Regularly check command history for patterns
   - Filter history by device or status to identify issues
   - Use command status to track execution progress
   - Cancel stuck commands to free up resources

5. **Integration with Other Services**
   - Combine Commands with Device Shadow for state management
   - Use Jobs for long-running operations
   - Leverage Fleet Indexing to target devices dynamically
   - Monitor command metrics in CloudWatch

## Fluxos de Trabalho de Desenvolvimento

### Teste de Novo Firmware
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

### Limpeza Após Testes
```bash
# Clean up test resources
python scripts/cleanup_script.py
# Option 1: ALL resources
# Confirm: DELETE
```

### Provisionamento com Prefixo Personalizado de Thing
```bash
# Provisionar com prefixo personalizado de thing
python scripts/provision_script.py
# Thing prefix: Fleet-VIN-
# Thing types: SedanVehicle
# Versions: 1.0.0
# Countries: US
# Devices: 50

# Saída esperada:
# ✓ Created thing: Fleet-VIN-001
# ✓ Created thing: Fleet-VIN-002
# ✓ Created thing: Fleet-VIN-003
# ...
# ✓ Created thing: Fleet-VIN-050
```

### Visualização de Limpeza em Modo Dry-Run
```bash
# Visualizar o que seria excluído sem realmente excluir
python scripts/cleanup_script.py
# Enable dry-run mode: yes
# Option 1: ALL resources

# Saída esperada:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODO DRY RUN - Nenhum recurso será excluído
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 
# Resumo de Limpeza (Dry Run):
# ================
# Recursos que seriam excluídos:
#   - IoT Things: 50
#   - Thing Shadows: 50
#   - Certificates: 50
#   - Thing Groups: 5
#   - Packages: 3
#   - Package Versions: 6
#   - S3 Buckets: 1
#   - IAM Roles: 2
#   - Thing Types: 3
#   Total: 170
# 
# Recursos que seriam ignorados:
#   - IoT Things: 2 (recursos não do workshop)
#   Total: 2
# 
# Tempo de Execução: 12.5 segundos
```

### Limpeza com Prefixo Personalizado de Thing
```bash
# Limpar recursos criados com prefixo personalizado
python scripts/cleanup_script.py
# Enable dry-run mode: no
# Thing prefix: Fleet-VIN-
# Option 1: ALL resources
# Confirm: DELETE

# Saída esperada:
# Escaneando recursos do workshop...
# ✓ Identificados 50 things correspondentes ao prefixo: Fleet-VIN-
# ✓ Identificados 5 thing groups com tags do workshop
# ✓ Identificados 3 packages com tags do workshop
# 
# Excluindo recursos...
# [1/50] Thing excluído: Fleet-VIN-001 (correspondência de tag)
# [2/50] Thing excluído: Fleet-VIN-002 (correspondência de tag)
# ...
# [50/50] Thing excluído: Fleet-VIN-050 (correspondência de tag)
# 
# Resumo de Limpeza:
# ================
# Recursos Excluídos:
#   - IoT Things: 50
#   - Thing Shadows: 50
#   - Certificates: 50
#   - Thing Groups: 5
#   - Packages: 3
#   Total: 158
# 
# Recursos Ignorados:
#   - IoT Things: 0
#   Total: 0
```

### Modo Debug com Métodos de Identificação
```bash
# Executar limpeza com modo debug para ver métodos de identificação
python scripts/cleanup_script.py
# Enable debug mode: yes
# Enable dry-run mode: yes
# Option 1: ALL resources

# Saída esperada com detalhes de identificação:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODO DEBUG ATIVADO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 
# Escaneando IoT Things...
# [DEBUG] Thing: Vehicle-VIN-001
#   → Verificando tags... ✓ Tag do workshop encontrada
#   → Identificação: CORRESPONDÊNCIA DE TAG
# 
# [DEBUG] Thing: Vehicle-VIN-002
#   → Verificando tags... ✗ Sem tag do workshop
#   → Verificando padrão de nomenclatura... ✓ Corresponde ao padrão Vehicle-VIN-*
#   → Identificação: CORRESPONDÊNCIA DE NOMENCLATURA
# 
# [DEBUG] Thing: production-sensor-001
#   → Verificando tags... ✗ Sem tag do workshop
#   → Verificando padrão de nomenclatura... ✗ Sem correspondência de padrão
#   → Identificação: IGNORADO (recurso não do workshop)
# 
# Escaneando Certificates...
# [DEBUG] Certificate: abc123def456
#   → Verificando tags... N/A (certificados não são marcáveis)
#   → Verificando associação... ✓ Anexado a Vehicle-VIN-001
#   → Identificação: CORRESPONDÊNCIA DE ASSOCIAÇÃO
# 
# [DEBUG] Certificate: xyz789ghi012
#   → Verificando tags... N/A (certificados não são marcáveis)
#   → Verificando associação... ✗ Não anexado a thing do workshop
#   → Identificação: IGNORADO (recurso não do workshop)
# 
# Escaneando Thing Shadows...
# [DEBUG] Shadow: Vehicle-VIN-001 (classic)
#   → Verificando tags... N/A (shadows não são marcáveis)
#   → Verificando associação... ✓ Pertence a Vehicle-VIN-001
#   → Identificação: CORRESPONDÊNCIA DE ASSOCIAÇÃO
# 
# Escaneando Thing Groups...
# [DEBUG] Thing Group: USFleet
#   → Verificando tags... ✓ Tag do workshop encontrada
#   → Identificação: CORRESPONDÊNCIA DE TAG
# 
# [DEBUG] Thing Group: ProductionFleet
#   → Verificando tags... ✗ Sem tag do workshop
#   → Verificando padrão de nomenclatura... ✗ Sem correspondência de padrão
#   → Identificação: IGNORADO (recurso não do workshop)
# 
# Resumo de Limpeza (Dry Run):
# ================
# Recursos que seriam excluídos:
#   - IoT Things: 48 (45 por tag, 3 por nomenclatura)
#   - Certificates: 48 (por associação)
#   - Thing Shadows: 48 (por associação)
#   - Thing Groups: 5 (por tag)
#   - Packages: 3 (por tag)
#   Total: 152
# 
# Recursos que seriam ignorados:
#   - IoT Things: 2 (sem correspondência)
#   - Certificates: 1 (sem correspondência)
#   - Thing Groups: 1 (sem correspondência)
#   Total: 4
# 
# Resumo do Método de Identificação:
#   - Correspondências de tag: 56
#   - Correspondências de nomenclatura: 3
#   - Correspondências de associação: 96
#   - Sem correspondências (ignorados): 4
```

## Padrões de Gerenciamento de Frota

### Implantação Geográfica
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

### Gerenciamento de Tipo de Dispositivo
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

### Agendamento de Manutenção
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

## Exemplos de Solução de Problemas

### Recuperação de Trabalho Falhado
```bash
# 1. Analyze job health and statistics
python scripts/explore_jobs.py
# Option 7: View statistics
# - Get health assessment (Excellent/Good/Poor/Critical)
# - See failure patterns and recommendations
# - Understand execution distribution

# 2. Check job status details
python scripts/explore_jobs.py
# Option 2: Explore specific job
# Enter job ID with failures

# 3. Check individual device failures
python scripts/explore_jobs.py
# Option 3: Explore job execution
# Enter job ID and failing device name

# 4. Cancel problematic job if needed
python scripts/explore_jobs.py
# Option 5: Cancel job
# - Review impact analysis
# - Add cancellation comment for audit trail

# 5. Rollback failed devices
python scripts/manage_packages.py
# Select: 10. Revert Device Versions
# Thing type: SedanVehicle
# Target version: 1.0.0  # Previous working version

# 6. Clean up canceled job
python scripts/explore_jobs.py
# Option 6: Delete job
# - Remove canceled job from system
```

### Verificação de Estado do Dispositivo
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

### Teste de Desempenho
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

## Exemplos Específicos de Ambiente

### Ambiente de Desenvolvimento
```bash
# Small scale for development
python scripts/provision_script.py
# Thing types: DevSensor
# Versions: 1.0.0-dev
# Countries: US
# Devices: 5
```

### Ambiente de Staging
```bash
# Medium scale for staging
python scripts/provision_script.py
# Thing types: SedanVehicle,SUVVehicle
# Versions: 1.0.0,1.1.0-rc
# Countries: US,CA
# Devices: 100
```

### Ambiente de Produção
```bash
# Large scale for production
python scripts/provision_script.py
# Thing types: SedanVehicle,SUVVehicle,TruckVehicle
# Versions: 1.0.0,1.1.0,1.2.0
# Continent: 1 (North America)
# Countries: ALL
# Devices: 10000
```

## Exemplos de Integração

### Integração de Pipeline CI/CD
```bash
# Syntax check (automated)
python scripts/check_syntax.py

# Automated testing
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### Integração de Monitoramento
```bash
# View comprehensive job analytics
python scripts/explore_jobs.py
# Option 7: View statistics
# - Health assessment with recommendations
# - Execution distribution analysis
# - Context-aware troubleshooting guidance

# Monitor active jobs
python scripts/explore_jobs.py
# Option 1: List all jobs (filter by status)

# Cancel jobs programmatically (with confirmation)
python scripts/explore_jobs.py
# Option 5: Cancel job
# - Impact analysis before action
# - Audit trail with comments

# Clean up old completed jobs
python scripts/explore_jobs.py
# Option 6: Delete job
# - Batch cleanup of completed jobs
# - Automatic force flag handling
```

## Exemplos de Melhores Práticas

### Implantação Gradual
1. Start with 5% of fleet (test group)
2. Monitor for 24 hours
3. Expand to 25% if successful
4. Full deployment after validation

### Estratégia de Reversão
1. Always test rollback procedure
2. Keep previous firmware versions available
3. Monitor device health post-deployment
4. Have automated rollback triggers

### Gerenciamento de Recursos
1. Use cleanup script after testing
2. Monitor AWS costs
3. Clean up old firmware versions
4. Remove unused thing groups