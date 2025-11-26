# Documentação Detalhada de Scripts

Este documento fornece informações abrangentes sobre cada script no projeto AWS IoT Device Management. Todos os scripts usam o SDK nativo da AWS (boto3) para desempenho e confiabilidade ideais.

## Scripts Principais

### scripts/provision_script.py
**Propósito**: Provisionamento completo de infraestrutura AWS IoT para cenários de gerenciamento de dispositivos usando APIs nativas do boto3.

**Recursos**:
- Cria tipos de coisas com atributos pesquisáveis (customerId, country, manufacturingDate)
- Provisiona milhares de dispositivos IoT com nomenclatura estilo VIN (Vehicle-VIN-001)
- Configura armazenamento Amazon S3 com versionamento para pacotes de firmware
- Cria pacotes de software AWS IoT com múltiplas versões
- Configura AWS IoT Fleet Indexing para consultas de dispositivos
- Estabelece funções AWS Identity and Access Management (IAM) para operações seguras
- Cria grupos de coisas estáticos por país (convenção de nomenclatura Fleet)
- **Processamento Paralelo**: Operações concorrentes para provisionamento mais rápido
- **Tratamento de Erros Aprimorado**: Tratamento robusto de exceções do boto3

**Entradas Interativas**:
1. Tipos de coisas (padrão: SedanVehicle,SUVVehicle,TruckVehicle)
2. Versões de pacotes (padrão: 1.0.0,1.1.0)
3. Seleção de continente (1-7)
4. Países (contagem ou códigos específicos)
5. Contagem de dispositivos (padrão: 100)

**Pausas Educacionais**: 8 momentos de aprendizagem explicando conceitos de IoT

**Limites de Taxa**: Limitação inteligente de API da AWS (80 TPS para coisas, 8 TPS para tipos de coisas)

**Desempenho**: Execução paralela quando não está em modo de depuração, sequencial em modo de depuração para saída limpa

---

### scripts/cleanup_script.py
**Propósito**: Remoção segura de recursos AWS IoT para evitar custos contínuos usando APIs nativas do boto3.

**Opções de Limpeza**:
1. **TODOS os recursos** - Limpeza completa de infraestrutura
2. **Apenas coisas** - Remover dispositivos mas manter infraestrutura
3. **Apenas grupos de coisas** - Remover agrupamentos mas manter dispositivos

**Recursos**:
- **Implementação Nativa do boto3**: Sem dependências de CLI, melhor tratamento de erros
- **Processamento paralelo** com limitação inteligente de taxa
- **Limpeza Aprimorada do S3**: Exclusão adequada de objetos versionados usando paginadores
- Distingue automaticamente grupos estáticos vs dinâmicos
- Lida com depreciação de tipos de coisas (espera de 5 minutos)
- Cancela e exclui trabalhos AWS IoT com monitoramento de status
- Limpeza abrangente de funções e políticas IAM
- Desabilita configuração de Fleet Indexing
- **Limpeza de Sombras**: Remove sombras clássicas e $package
- **Desvinculação de Principais**: Desvincula adequadamente certificados e políticas

**Segurança**: Requer digitar "DELETE" para confirmar

**Desempenho**: Execução paralela respeitando limites de API da AWS (80 TPS coisas, 4 TPS grupos dinâmicos)

---

### scripts/create_job.py
**Propósito**: Criar trabalhos AWS IoT para atualizações de firmware over-the-air usando APIs nativas do boto3.

**Recursos**:
- **Implementação Nativa do boto3**: Chamadas diretas de API para melhor desempenho
- Seleção interativa de grupos de coisas (único ou múltiplo)
- Seleção de versão de pacote com resolução de ARN
- Configuração de trabalho contínuo (inclui automaticamente novos dispositivos)
- Configuração de URL pré-assinada (expiração de 1 hora)
- Suporte para direcionamento de múltiplos grupos
- **Tipos de Trabalho Aprimorados**: Suporte para tipos de trabalho OTA e personalizados
- **Configuração Avançada**: Políticas de implantação, critérios de aborto, configurações de tempo limite

**Configuração de Trabalho**:
- IDs de trabalho gerados automaticamente com carimbos de data/hora
- Espaços reservados de URL pré-assinada AWS IoT
- Formatação ARN adequada para recursos
- Estrutura abrangente de documento de trabalho
- **Conteúdo Educacional**: Explica opções de configuração de trabalho

---

### scripts/simulate_job_execution.py
**Propósito**: Simular comportamento realista de dispositivos durante atualizações de firmware usando APIs nativas do boto3.

**Recursos**:
- **Implementação Nativa do boto3**: Integração direta com API IoT Jobs Data
- Downloads reais de artefatos Amazon S3 via URLs pré-assinadas
- **Execução Paralela de Alto Desempenho** (150 TPS com controle de semáforo)
- Taxas de sucesso/falha configuráveis
- **Preparação de plano visível** - Mostra cada dispositivo sendo atribuído status de sucesso/falha
- **Confirmação do usuário** - Pergunta para prosseguir após preparação do plano
- **Visibilidade de operação** - Mostra progresso de download e atualizações de status de trabalho para cada dispositivo
- **Tratamento de Erros Aprimorado**: Gerenciamento robusto de exceções do boto3
- Rastreamento de progresso com relatórios detalhados
- **Formatação JSON Limpa**: Exibição de documento de trabalho adequadamente formatado

**Fluxo de Processo**:
1. Escaneia trabalhos ativos usando APIs nativas
2. Obtém execuções pendentes (QUEUED/IN_PROGRESS)
3. **Prepara plano de execução** - Mostra atribuições de dispositivos e solicita confirmação
4. Baixa firmware real do Amazon S3 (mostra progresso por dispositivo)
5. Atualiza status de execução de trabalho usando API IoT Jobs Data
6. Relata estatísticas abrangentes de sucesso/falha

**Melhorias de Desempenho**:
- **Processamento Paralelo**: Execução concorrente quando não está em modo de depuração
- **Limitação de Taxa**: Limitação inteligente baseada em semáforo
- **Eficiência de Memória**: Downloads em streaming para arquivos de firmware grandes

**Melhorias de Visibilidade**:
- Preparação de plano mostra: `[1/100] Vehicle-VIN-001 -> SUCCESS`
- Progresso de download mostra: `Vehicle-VIN-001: Downloading firmware from S3...`
- Confirmação de tamanho de arquivo: `Vehicle-VIN-001: Downloaded 2.1KB firmware`
- Atualizações de status mostram: `Vehicle-VIN-001: Job execution SUCCEEDED`

---

### scripts/explore_jobs.py
**Propósito**: Exploração interativa de trabalhos AWS IoT para monitoramento e solução de problemas usando APIs nativas do boto3.

**Opções de Menu**:
1. **Listar todos os trabalhos** - Visão geral de todos os status com varredura paralela
2. **Explorar trabalho específico** - Configuração detalhada de trabalho com formatação JSON limpa
3. **Explorar execução de trabalho** - Progresso de dispositivo individual usando API IoT Jobs Data
4. **Listar execuções de trabalho** - Todas as execuções para um trabalho com verificação de status paralela

**Recursos**:
- **Implementação Nativa do boto3**: Integração direta de API para melhor desempenho
- **Varredura Paralela de Trabalhos**: Verificação concorrente de status em todos os estados de trabalho
- **Exibição JSON Limpa**: Documentos de trabalho adequadamente formatados sem caracteres de escape
- Indicadores de status codificados por cores
- Seleção interativa de trabalho com listagem de trabalhos disponíveis
- Exibição detalhada de configuração de URL pré-assinada
- Estatísticas de resumo de execução com codificação de cores
- **Tratamento de Erros Aprimorado**: Gerenciamento robusto de exceções do boto3
- Loop de exploração contínua

**Melhorias de Desempenho**:
- **Processamento Paralelo**: Operações concorrentes quando não está em modo de depuração
- **Paginação Inteligente**: Tratamento eficiente de listas grandes de trabalhos
- **Limitação de Taxa**: Limitação adequada de API com semáforos

---

### scripts/manage_packages.py
**Propósito**: Gerenciamento abrangente de pacotes de software AWS IoT, rastreamento de dispositivos e reversão de versão usando APIs nativas do boto3.

**Operações**:
1. **Criar Pacote** - Criar novos contêineres de pacotes de software
2. **Criar Versão** - Adicionar versões com upload de firmware S3 e publicação (com momentos de aprendizagem)
3. **Listar Pacotes** - Exibir pacotes com opções de descrição interativas
4. **Descrever Pacote** - Mostrar detalhes do pacote com exploração de versões
5. **Descrever Versão** - Mostrar detalhes de versão específica e artefatos Amazon S3
6. **Verificar Configuração** - Ver status de configuração do pacote e função IAM
7. **Habilitar Configuração** - Habilitar atualizações automáticas de sombra com criação de função IAM
8. **Desabilitar Configuração** - Desabilitar atualizações automáticas de sombra
9. **Verificar Versão do Dispositivo** - Inspecionar sombra $package para dispositivos específicos (suporte multi-dispositivo)
10. **Reverter Versões** - Reversão de versão em toda a frota usando Fleet Indexing

**Recursos Principais**:
- **Integração Amazon S3**: Upload automático de firmware com versionamento
- **Navegação Interativa**: Fluxo contínuo entre operações de listar, descrever e versão
- **Gerenciamento de Configuração de Pacotes**: Controle de integração Jobs-to-Shadow
- **Rastreamento de Dispositivos**: Inspeção de versão de pacote de dispositivo individual
- **Reversão de Frota**: Reversão de versão usando consultas Fleet Indexing
- **Abordagem Educacional**: Momentos de aprendizagem ao longo dos fluxos de trabalho
- **Gerenciamento de Funções IAM**: Criação automática de função para configuração de pacotes

**Configuração de Pacotes**:
- **Verificar Status**: Mostra estado habilitado/desabilitado e ARN de função IAM
- **Habilitar**: Cria IoTPackageConfigRole com permissões de sombra $package
- **Desabilitar**: Para atualizações automáticas de sombra na conclusão do trabalho
- **Educacional**: Explica integração Jobs-to-Shadow e requisitos IAM

**Rastreamento de Versão de Dispositivos**:
- **Suporte Multi-dispositivo**: Verificar múltiplos dispositivos em sequência
- **Inspeção de Sombra $package**: Mostra versões atuais de firmware e metadados
- **Exibição de Carimbo de Data/Hora**: Informações de última atualização para cada pacote
- **Tratamento de Erros**: Mensagens claras para dispositivos ou sombras ausentes

**Reversão de Versão**:
- **Consultas Fleet Indexing**: Encontrar dispositivos por tipo de coisa e versão
- **Visualização de Lista de Dispositivos**: Mostra dispositivos que serão revertidos (primeiros 10 + contagem)
- **Confirmação Necessária**: Digite 'REVERT' para prosseguir com atualizações de sombra
- **Status de Dispositivo Individual**: Mostra sucesso/falha de reversão por dispositivo
- **Rastreamento de Progresso**: Status de atualização em tempo real com contagens de sucesso
- **Educacional**: Explica conceitos de reversão e gerenciamento de sombras

**Visibilidade de Reversão**:
- Visualização de dispositivos: `1. Vehicle-VIN-001`, `2. Vehicle-VIN-002`, `... e mais 90 dispositivos`
- Resultados individuais: `Vehicle-VIN-001: Reverted to version 1.0.0`
- Tentativas falhadas: `Vehicle-VIN-002: Failed to revert`

**Foco de Aprendizagem**:
- Ciclo de vida completo de firmware desde criação até reversão
- Configuração de pacotes e atualizações automáticas de sombra
- Gerenciamento e rastreamento de inventário de dispositivos
- Fleet Indexing para operações de gerenciamento de versões

---

### scripts/manage_dynamic_groups.py
**Propósito**: Gerenciamento abrangente de grupos de coisas dinâmicos com validação Fleet Indexing usando APIs nativas do boto3.

**Operações**:
1. **Criar Grupos Dinâmicos** - Dois métodos de criação:
   - **Assistente guiado**: Seleção interativa de critérios
   - **Consulta personalizada**: Entrada direta de consulta Fleet Indexing
2. **Listar Grupos Dinâmicos** - Exibir todos os grupos com contagens de membros e consultas
3. **Excluir Grupos Dinâmicos** - Exclusão segura com confirmação
4. **Testar Consultas** - Validar consultas personalizadas Fleet Indexing

**Métodos de Criação**:
- **Assistente Guiado** (tudo opcional):
  - Países: Único ou múltiplo (ex., US,CA,MX)
  - Tipo de Coisa: Categoria de veículo (ex., SedanVehicle)
  - Versões: Única ou múltipla (ex., 1.0.0,1.1.0)
  - Nível de Bateria: Comparações (ex., >50, <30, =75)
- **Consulta Personalizada**: Entrada direta de string de consulta Fleet Indexing

**Recursos**:
- **Modos de criação duplos**: Assistente guiado ou entrada de consulta personalizada
- Nomenclatura inteligente de grupos (gerada automaticamente ou personalizada)
- Construção e validação de consultas Fleet Indexing
- **Visualização de correspondência de dispositivos em tempo real** (mostra dispositivos correspondentes antes da criação)
- Exibição de contagem de membros para grupos existentes
- Exclusão segura com prompts de confirmação
- Capacidades de teste de consultas personalizadas
- Validação de consulta previne criação de grupos vazios

**Exemplos de Consultas**:
- Critério único: `thingTypeName:SedanVehicle AND attributes.country:US`
- Múltiplos critérios: `thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- Versões de pacotes: `shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- Complexo personalizado: `(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**Propósito**: Validação de sintaxe pré-publicação para pipeline CI/CD.

**Verificações**:
- Validação de sintaxe Python para todos os scripts
- Verificação de disponibilidade de importações
- Validação de requirements.txt
- Listagem de dependências

**Uso**: Executado automaticamente pelo fluxo de trabalho GitHub Actions

---

## Dependências de Scripts

### Pacotes Python Necessários
- `boto3>=1.40.27` - AWS SDK para Python (versão mais recente para suporte de artefatos de pacotes)
- `colorama>=0.4.4` - Cores de terminal
- `requests>=2.25.1` - Requisições HTTP para downloads Amazon S3

### Serviços AWS Usados
- **AWS IoT Core** - Gerenciamento de coisas, trabalhos, sombras
- **AWS IoT Device Management** - Pacotes de software, Fleet Indexing
- **Amazon S3** - Armazenamento de firmware com versionamento
- **AWS Identity and Access Management (IAM)** - Funções e políticas para acesso seguro

### Requisitos de Credenciais AWS
- Credenciais configuradas via:
  - `aws configure` (AWS CLI)
  - Variáveis de ambiente (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - Funções IAM (para execução EC2/Lambda)
  - Arquivo de credenciais AWS
- Permissões IAM apropriadas para operações AWS IoT, Amazon S3 e IAM
- Configuração de região (variável de ambiente AWS_DEFAULT_REGION ou credenciais)

## Recursos Educacionais

### Momentos de Aprendizagem
Cada script inclui pausas educacionais explicando:
- Conceitos e arquitetura AWS IoT
- Melhores práticas para gerenciamento de dispositivos
- Considerações de segurança
- Padrões de escalabilidade

### Rastreamento de Progresso
- Status de operação em tempo real
- Contagens de sucesso/falha
- Métricas de desempenho (TPS, duração)
- Saída codificada por cores para fácil leitura

### Modo de Depuração
Disponível em todos os scripts:
- Mostra todas as chamadas de API do SDK AWS (boto3) com parâmetros
- Exibe respostas completas de API em formato JSON
- Fornece informações detalhadas de erro com rastreamentos de pilha completos
- **Processamento Sequencial**: Executa operações sequencialmente para saída de depuração limpa
- Ajuda com solução de problemas e aprendizagem de APIs AWS

## Características de Desempenho

### Limitação de Taxa
Scripts respeitam limites de API da AWS:
- Operações de coisas: 80 TPS (limite de 100 TPS)
- Tipos de coisas: 8 TPS (limite de 10 TPS)
- Grupos dinâmicos: 4 TPS (limite de 5 TPS)
- Execuções de trabalhos: 150 TPS (limite de 200 TPS)
- Operações de pacotes: 8 TPS (limite de 10 TPS)

### Processamento Paralelo
- **Integração Nativa do boto3**: Chamadas diretas do SDK AWS para melhor desempenho
- ThreadPoolExecutor para operações concorrentes (quando não está em modo de depuração)
- **Limitação Inteligente de Taxa**: Semáforos respeitando limites de API da AWS
- **Rastreamento de Progresso Thread-Safe**: Monitoramento de operações concorrentes
- **Tratamento de Erros Aprimorado**: Gerenciamento robusto de exceções ClientError do boto3
- **Substituição de Modo de Depuração**: Processamento sequencial em modo de depuração para saída limpa

### Gerenciamento de Memória
- Downloads em streaming para arquivos grandes
- Limpeza de arquivos temporários
- Análise eficiente de JSON
- Limpeza de recursos na saída
