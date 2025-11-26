# Exemplos de Uso

Este documento fornece exemplos práticos para cenários comuns de AWS IoT Device Management.

## Exemplos de Início Rápido

### Configuração Básica de Frota
```bash
# 1. Criar infraestrutura
python scripts/provision_script.py
# Escolher: SedanVehicle,SUVVehicle
# Versões: 1.0.0,1.1.0
# Região: North America
# Países: US,CA
# Dispositivos: 100

# 2. Criar grupos dinâmicos
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Países: US
# Tipo de coisa: SedanVehicle
# Nível de bateria: <30

# 3. Criar trabalho de atualização de firmware
python scripts/create_job.py
# Selecionar: grupo USFleet
# Pacote: SedanVehicle v1.1.0

# 4. Simular atualizações de dispositivos
python scripts/simulate_job_execution.py
# Taxa de sucesso: 85%
# Processar: TODAS as execuções
```

### Cenário de Reversão de Versão
```bash
# Reverter todos os dispositivos SedanVehicle para a versão 1.0.0
python scripts/manage_packages.py
# Selecionar: 10. Reverter Versões de Dispositivos
# Tipo de coisa: SedanVehicle
# Versão alvo: 1.0.0
# Confirmar: REVERT
```

### Monitoramento de Trabalhos
```bash
# Monitorar progresso do trabalho
python scripts/explore_jobs.py
# Opção 1: Listar todos os trabalhos
# Opção 4: Listar execuções de trabalho para um trabalho específico
```

## Cenários Avançados

### Implantação Multi-Região
```bash
# Provisionar em múltiplas regiões
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# Criar 500 dispositivos na América do Norte

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# Criar 300 dispositivos na Europa
```

### Implantação Escalonada
```bash
# 1. Criar grupo de teste
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Países: US
# Tipo de coisa: SedanVehicle
# Versões: 1.0.0
# Nome personalizado: TestFleet_SedanVehicle_US

# 2. Implantar primeiro no grupo de teste
python scripts/create_job.py
# Selecionar: TestFleet_SedanVehicle_US
# Pacote: SedanVehicle v1.1.0

# 3. Monitorar implantação de teste
python scripts/simulate_job_execution.py
# Taxa de sucesso: 95%

# 4. Implantar em produção após validação
python scripts/create_job.py
# Selecionar: USFleet
# Pacote: SedanVehicle v1.1.0
```

### Manutenção Baseada em Bateria
```bash
# Criar grupo de bateria baixa
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Método: 1 (Assistente guiado)
# Países: (deixar vazio para todos)
# Tipo de coisa: (deixar vazio para todos)
# Nível de bateria: <20
# Nome personalizado: LowBatteryDevices

# Criar trabalho de manutenção
python scripts/create_job.py
# Selecionar: LowBatteryDevices
# Pacote: MaintenanceFirmware v2.0.0
```

### Consulta Personalizada Avançada
```bash
# Criar grupo complexo com consulta personalizada
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Método: 2 (Consulta personalizada)
# Consulta: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# Nome do grupo: USVehicles_MidBattery
```

### Gerenciamento de Pacotes
```bash
# Criar novo pacote e versões
python scripts/manage_packages.py
# Operação: 1 (Criar Pacote)
# Nome do pacote: TestVehicle

# Adicionar versão com upload para S3
# Operação: 2 (Criar Versão)
# Nome do pacote: TestVehicle
# Versão: 2.0.0

# Inspecionar detalhes do pacote
# Operação: 4 (Descrever Pacote)
# Nome do pacote: TestVehicle
```

## Fluxos de Trabalho de Desenvolvimento

### Teste de Novo Firmware
```bash
# 1. Provisionar ambiente de teste
python scripts/provision_script.py
# Tipos de coisa: TestSensor
# Versões: 1.0.0,2.0.0-beta
# Países: US
# Dispositivos: 10

# 2. Criar grupo de teste beta
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Tipo de coisa: TestSensor
# Versões: 1.0.0
# Nome personalizado: BetaTestGroup

# 3. Implantar firmware beta
python scripts/create_job.py
# Selecionar: BetaTestGroup
# Pacote: TestSensor v2.0.0-beta

# 4. Simular com alta taxa de falha para testes
python scripts/simulate_job_execution.py
# Taxa de sucesso: 60%

# 5. Analisar resultados
python scripts/explore_jobs.py
# Opção 4: Listar execuções de trabalho
```

### Limpeza Após Testes
```bash
# Limpar recursos de teste
python scripts/cleanup_script.py
# Opção 1: TODOS os recursos
# Confirmar: DELETE
```

## Padrões de Gerenciamento de Frota

### Implantação Geográfica
```bash
# Provisionar por continente
python scripts/provision_script.py
# Continente: 1 (América do Norte)
# Países: 3 (primeiros 3 países)
# Dispositivos: 1000

# Criar grupos específicos por país (criados automaticamente como USFleet, CAFleet, MXFleet)
# Implantar firmware específico da região
python scripts/create_job.py
# Selecionar: USFleet,CAFleet
# Pacote: RegionalFirmware v1.2.0
```

### Gerenciamento de Tipos de Dispositivos
```bash
# Provisionar múltiplos tipos de veículos
python scripts/provision_script.py
# Tipos de coisa: SedanVehicle,SUVVehicle,TruckVehicle
# Versões: 1.0.0,1.1.0,2.0.0
# Dispositivos: 500

# Criar grupos dinâmicos específicos por tipo
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Tipo de coisa: TruckVehicle
# Países: US,CA
# Nome personalizado: NorthAmericaTrucks

# Implantar firmware específico para caminhões
python scripts/create_job.py
# Selecionar: NorthAmericaTrucks
# Pacote: TruckVehicle v2.0.0
```

### Agendamento de Manutenção
```bash
# Encontrar dispositivos que precisam de atualizações
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Tipo de coisa: SedanVehicle
# Versões: 1.0.0  # Versão antiga
# Nome personalizado: SedanVehicle_NeedsUpdate

# Agendar implantação na janela de manutenção
python scripts/create_job.py
# Selecionar: SedanVehicle_NeedsUpdate
# Pacote: SedanVehicle v1.1.0

# Monitorar progresso da implantação
python scripts/explore_jobs.py
# Opção 1: Listar todos os trabalhos (verificar status)
```

## Exemplos de Solução de Problemas

### Recuperação de Trabalho Falho
```bash
# 1. Verificar status do trabalho
python scripts/explore_jobs.py
# Opção 2: Explorar trabalho específico
# Inserir ID do trabalho com falhas

# 2. Verificar falhas de dispositivos individuais
python scripts/explore_jobs.py
# Opção 3: Explorar execução de trabalho
# Inserir ID do trabalho e nome do dispositivo com falha

# 3. Reverter dispositivos com falha
python scripts/manage_packages.py
# Selecionar: 10. Reverter Versões de Dispositivos
# Tipo de coisa: SedanVehicle
# Versão alvo: 1.0.0  # Versão anterior funcional
```

### Verificação de Estado de Dispositivos
```bash
# Verificar versões atuais de firmware
python scripts/manage_dynamic_groups.py
# Operação: 1 (Criar)
# Tipo de coisa: SedanVehicle
# Versões: 1.1.0
# Nome personalizado: SedanVehicle_v1_1_0_Check

# Verificar associação ao grupo (deve corresponder à contagem esperada)
python scripts/explore_jobs.py
# Usar para verificar estados de dispositivos
```

### Teste de Desempenho
```bash
# Testar com grande quantidade de dispositivos
python scripts/provision_script.py
# Dispositivos: 5000

# Testar desempenho de execução de trabalhos
python scripts/simulate_job_execution.py
# Processar: TODOS
# Taxa de sucesso: 90%
# Monitorar tempo de execução e TPS
```

## Exemplos Específicos de Ambiente

### Ambiente de Desenvolvimento
```bash
# Escala pequena para desenvolvimento
python scripts/provision_script.py
# Tipos de coisa: DevSensor
# Versões: 1.0.0-dev
# Países: US
# Dispositivos: 5
```

### Ambiente de Staging
```bash
# Escala média para staging
python scripts/provision_script.py
# Tipos de coisa: SedanVehicle,SUVVehicle
# Versões: 1.0.0,1.1.0-rc
# Países: US,CA
# Dispositivos: 100
```

### Ambiente de Produção
```bash
# Escala grande para produção
python scripts/provision_script.py
# Tipos de coisa: SedanVehicle,SUVVehicle,TruckVehicle
# Versões: 1.0.0,1.1.0,1.2.0
# Continente: 1 (América do Norte)
# Países: TODOS
# Dispositivos: 10000
```

## Exemplos de Integração

### Integração com Pipeline CI/CD
```bash
# Verificação de sintaxe (automatizada)
python scripts/check_syntax.py

# Testes automatizados
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### Integração de Monitoramento
```bash
# Exportar métricas de trabalhos
python scripts/explore_jobs.py --export-json > job_status.json

# Verificar saúde da implantação
python scripts/explore_jobs.py --health-check
```

## Exemplos de Melhores Práticas

### Implantação Gradual
1. Começar com 5% da frota (grupo de teste)
2. Monitorar por 24 horas
3. Expandir para 25% se bem-sucedido
4. Implantação completa após validação

### Estratégia de Reversão
1. Sempre testar o procedimento de reversão
2. Manter versões anteriores de firmware disponíveis
3. Monitorar saúde do dispositivo pós-implantação
4. Ter gatilhos de reversão automatizados

### Gerenciamento de Recursos
1. Usar script de limpeza após testes
2. Monitorar custos da AWS
3. Limpar versões antigas de firmware
4. Remover grupos de coisas não utilizados
