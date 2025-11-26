# Guia de Solução de Problemas

Este documento fornece soluções para problemas comuns encontrados ao usar os scripts de AWS IoT Device Management.

## Problemas Comuns

### Problemas de Configuração da AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Solução**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

#### Problema: Erros de "Access Denied"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Solução**: Certifique-se de que seu usuário/função do AWS IAM tenha as permissões necessárias:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:*",
                "iot-data:*",
                "iot-jobs-data:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:CreateBucket",
                "s3:DeleteBucket",
                "s3:ListBucket",
                "iam:GetRole",
                "iam:PassRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Problema: "Region not configured"
```
You must specify a region
```

**Solução**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

### Problemas de Execução de Scripts

#### Problema: "No module named 'colorama'"
```
ModuleNotFoundError: No module named 'colorama'
```

**Solução**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install colorama>=0.4.4 requests>=2.25.1
```

#### Problema: Scripts travam ou expiram
**Sintomas**: Scripts parecem congelar durante a execução

**Solução**:
1. Ative o modo de depuração para ver o que está acontecendo:
   ```bash
   # When prompted, choose 'y' for debug mode
   🔧 Enable debug mode? [y/N]: y
   ```

2. Verifique os limites de serviço da AWS e throttling
3. Reduza os workers paralelos se necessário
4. Verifique a conectividade de rede

#### Problema: "Thing type deletion requires 5-minute wait"
```
InvalidRequestException: Thing type cannot be deleted until 5 minutes after deprecation
```

**Solução**: Este é um comportamento esperado. O script de limpeza lida com isso automaticamente:
1. Depreciando os tipos de coisa primeiro
2. Aguardando 5 minutos
3. Depois excluindo-os

### Problemas de Criação de Recursos

#### Problema: "Thing group already exists"
```
ResourceAlreadyExistsException: Thing group already exists
```

**Solução**: Isso geralmente é inofensivo. Os scripts verificam recursos existentes e pulam a criação se já existirem.

#### Problema: "S3 bucket name already taken"
```
BucketAlreadyExists: The requested bucket name is not available
```

**Solução**: Os scripts usam timestamps para garantir nomes de bucket únicos. Se isso ocorrer:
1. Aguarde alguns segundos e tente novamente
2. Verifique se você tem buckets existentes com nomes semelhantes

#### Problema: "Package version already exists"
```
ConflictException: Package version already exists
```

**Solução**: Os scripts lidam com isso verificando as versões existentes primeiro. Se você precisar atualizar:
1. Use um novo número de versão
2. Ou exclua a versão existente primeiro

### Problemas de Execução de Trabalhos

#### Problema: "No active jobs found"
```
❌ No active jobs found
```

**Solução**:
1. Crie um trabalho primeiro usando `scripts/create_job.py`
2. Verifique o status do trabalho: `scripts/explore_jobs.py`
3. Verifique se os trabalhos foram cancelados ou concluídos

#### Problema: "Failed to download artifact"
```
❌ Failed to download artifact: HTTP 403 Forbidden
```

**Solução**:
1. Verifique as permissões da função do AWS IAM para AWS IoT Jobs
2. Verifique a configuração de URL pré-assinada
3. Certifique-se de que o bucket S3 e os objetos existam
4. Verifique se as URLs pré-assinadas expiraram (limite de 1 hora)

#### Problema: "Job execution not found"
```
ResourceNotFoundException: Job execution not found
```

**Solução**:
1. Verifique se o ID do trabalho e o nome da coisa estão corretos
2. Verifique se o dispositivo está nos grupos de coisas de destino
3. Certifique-se de que o trabalho ainda esteja ativo (não concluído/cancelado)

### Problemas de Fleet Indexing

#### Problema: "Fleet Indexing queries return no results"
```
ℹ️ No devices currently match this query
```

**Solução**:
1. Aguarde a conclusão do Fleet Indexing (pode levar vários minutos)
2. Verifique se o Fleet Indexing está habilitado
3. Verifique a sintaxe da consulta
4. Certifique-se de que os dispositivos tenham os atributos/sombras esperados

#### Problema: "Invalid Fleet Indexing query"
```
InvalidRequestException: Invalid query string
```

**Solução**: Verifique a sintaxe da consulta. Problemas comuns:
- Use `attributes.fieldName` para atributos de dispositivo
- Use `shadow.reported.fieldName` para sombras clássicas
- Use `shadow.name.\\$package.reported.fieldName` para sombras nomeadas
- Escape caracteres especiais corretamente

### Problemas de Desempenho

#### Problema: "Rate limiting errors"
```
ThrottlingException: Rate exceeded
```

**Solução**: Os scripts têm limitação de taxa incorporada, mas se você encontrar isso:
1. Ative o modo de depuração para ver qual API está sendo limitada
2. Reduza os workers paralelos no script
3. Adicione atrasos entre operações
4. Verifique os limites de serviço da AWS para sua conta

#### Problema: "Scripts running slowly"
**Sintomas**: Operações levam muito mais tempo do que o esperado

**Solução**:
1. Verifique a conectividade de rede
2. Verifique se a região da AWS está geograficamente próxima
3. Ative o modo de depuração para identificar gargalos
4. Considere reduzir os tamanhos de lote

### Problemas de Consistência de Dados

#### Problema: "Device shadows not updating"
```
❌ Failed to update device shadow
```

**Solução**:
1. Verifique a configuração do endpoint do IoT Data
2. Verifique se o dispositivo/coisa existe
3. Certifique-se do formato JSON correto nas atualizações de sombra
4. Verifique as permissões do AWS IAM para operações de sombra

#### Problema: "Package configuration not working"
```
❌ Failed to update global package configuration
```

**Solução**:
1. Verifique se o IoTPackageConfigRole existe e tem as permissões adequadas
2. Verifique se o ARN da função está formatado corretamente
3. Certifique-se de que a configuração de pacote esteja habilitada em sua região

## Uso do Modo de Depuração

Ative o modo de depuração em qualquer script para solução de problemas detalhada:

```bash
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

O modo de depuração mostra:
- Todos os comandos da AWS CLI sendo executados
- Parâmetros de solicitação da API
- Respostas completas da API
- Detalhes de erro e rastreamentos de pilha

## Análise de Logs

### Operações Bem-Sucedidas
Procure estes indicadores:
- ✅ Marcas de verificação verdes para operações bem-sucedidas
- Contadores de progresso mostrando conclusão
- Mensagens de "completed successfully"

### Sinais de Aviso
Fique atento a estes padrões:
- ⚠️ Avisos amarelos (geralmente não críticos)
- Mensagens de "already exists" (geralmente inofensivas)
- Avisos de tempo limite

### Padrões de Erro
Indicadores comuns de erro:
- ❌ Marcas X vermelhas para falhas
- Mensagens de "Failed to"
- Rastreamentos de pilha de exceção
- Códigos de erro HTTP (403, 404, 500)

## Procedimentos de Recuperação

### Falha Parcial de Provisionamento
Se o provisionamento falhar no meio do caminho:

1. **Verifique o que foi criado**:
   ```bash
   python scripts/explore_jobs.py
   # Option 1: List all jobs
   ```

2. **Limpe se necessário**:
   ```bash
   python scripts/cleanup_script.py
   # Option 1: ALL resources
   ```

3. **Tente novamente o provisionamento**:
   ```bash
   python scripts/provision_script.py
   # Scripts handle existing resources gracefully
   ```

### Recuperação de Trabalho Falhado
Se um trabalho falhar durante a execução:

1. **Verifique o status do trabalho**:
   ```bash
   python scripts/explore_jobs.py
   # Option 2: Explore specific job
   ```

2. **Verifique falhas individuais**:
   ```bash
   python scripts/explore_jobs.py
   # Option 3: Explore job execution
   ```

3. **Reverta se necessário**:
   ```bash
   python scripts/manage_packages.py
   # Select: 10. Revert Device Versions
   # Enter thing type and previous version
   ```

### Problemas de Limpeza de Recursos
Se a limpeza falhar:

1. **Tente limpeza seletiva**:
   ```bash
   python scripts/cleanup_script.py
   # Option 2: Things only (then try groups)
   ```

2. **Limpeza manual via Console da AWS**:
   - AWS IoT Core → Manage → Things
   - AWS IoT Core → Manage → Thing groups
   - AWS IoT Core → Manage → Thing types
   - Amazon S3 → Buckets
   - AWS IAM → Roles

## Problemas Específicos do Ambiente

### Problemas do macOS
- **Avisos SSL**: Os scripts suprimem avisos SSL do urllib3 automaticamente
- **Versão do Python**: Certifique-se de que o Python 3.7+ esteja instalado

### Problemas do Windows
- **Separadores de caminho**: Os scripts lidam com caminhos multiplataforma automaticamente
- **PowerShell**: Use o Prompt de Comando ou PowerShell com política de execução adequada

### Problemas do Linux
- **Permissões**: Certifique-se de que os scripts tenham permissões de execução
- **Caminho do Python**: Pode ser necessário usar `python3` em vez de `python`

## Limites de Serviço da AWS

### Limites Padrão (por região)
- **Things**: 500.000 por conta
- **Thing Types**: 100 por conta
- **Thing Groups**: 500 por conta
- **Jobs**: 100 trabalhos simultâneos
- **Limites de Taxa da API**: 
  - Operações de Thing: 100 TPS (scripts usam 80 TPS)
  - Grupos dinâmicos: 5 TPS (scripts usam 4 TPS)
  - Execuções de Job: 200 TPS (scripts usam 150 TPS)
  - Operações de Package: 10 TPS (scripts usam 8 TPS)

### Solicitar Aumentos de Limite
Se você precisar de limites mais altos:
1. Vá para o Centro de Suporte da AWS
2. Crie um caso para "Service limit increase"
3. Especifique os limites do AWS IoT Core necessários

## Obtendo Ajuda

### Habilitar Registro Detalhado
A maioria dos scripts suporta modo detalhado:
```bash
🔧 Enable verbose mode? [y/N]: y
```

### Verificar o Estado do Serviço da AWS
- [Painel de Estado do Serviço da AWS](https://status.aws.amazon.com/)
- Verifique sua região específica para problemas do AWS IoT Core

### Recursos da Comunidade
- Fóruns de Desenvolvedores do AWS IoT
- Documentação da AWS
- GitHub Issues (para problemas específicos de scripts)

### Suporte Profissional
- Suporte da AWS (se você tiver um plano de suporte)
- Serviços Profissionais da AWS
- Consultores da Rede de Parceiros da AWS

## Dicas de Prevenção

### Antes de Executar Scripts
1. **Verifique a configuração da AWS**: `aws sts get-caller-identity`
2. **Verifique as permissões**: Teste com uma operação pequena primeiro
3. **Revise os limites de recursos**: Certifique-se de não atingir os limites da conta
4. **Faça backup de dados importantes**: Se estiver modificando recursos existentes

### Durante a Execução
1. **Monitore o progresso**: Fique atento a padrões de erro
2. **Não interrompa**: Deixe os scripts concluírem ou use Ctrl+C com cuidado
3. **Verifique o Console da AWS**: Verifique se os recursos estão sendo criados conforme esperado

### Após a Execução
1. **Verifique os resultados**: Use scripts de exploração para verificar os resultados
2. **Limpe recursos de teste**: Use o script de limpeza para recursos temporários
3. **Monitore os custos**: Verifique a faturação da AWS para cobranças inesperadas

## Problemas de Internacionalização

### Problema: Scripts mostrando chaves de mensagem brutas em vez de texto traduzido
**Sintomas**: Scripts exibem texto como `warnings.debug_warning` e `prompts.debug_mode` em vez de mensagens reais

**Exemplo**:
```
🧹 AWS IoT Cleanup Script (Boto3)
===================================
📚 LEARNING GOAL:
This script demonstrates proper AWS IoT resource cleanup...
📍 Region: eu-west-1
🆔 Account ID: 278816698247
warnings.debug_warning
prompts.debug_mode
```

**Causa Raiz**: Este problema ocorre quando:
1. Incompatibilidade de código de idioma entre o seletor de idioma e a estrutura de diretórios
2. Falta de tratamento de chaves aninhadas na função `get_message()`
3. Carregamento incorreto de arquivo de mensagens

**Solução**:

1. **Verifique o Mapeamento de Código de Idioma**: Certifique-se de que os códigos de idioma correspondam à estrutura de diretórios:
   ```
   i18n/
   ├── en/     # English
   ├── es/     # Spanish  
   ├── ja/     # Japanese
   ├── ko/     # Korean
   ├── pt/     # Portuguese
   ├── zh/     # Chinese
   ```

2. **Verifique a Implementação de get_message()**: Os scripts devem lidar com chaves aninhadas com notação de ponto:
   ```python
   def get_message(self, key, *args):
       """Get localized message with optional formatting"""
       # Handle nested keys like 'warnings.debug_warning'
       if '.' in key:
           keys = key.split('.')
           msg = messages
           for k in keys:
               if isinstance(msg, dict) and k in msg:
                   msg = msg[k]
               else:
                   msg = key  # Fallback to key if not found
                   break
       else:
           msg = messages.get(key, key)
       
       if args and isinstance(msg, str):
           return msg.format(*args)
       return msg
   ```

3. **Teste o Carregamento de Idioma**:
   ```bash
   # Test with environment variable
   export AWS_IOT_LANG=en
   python scripts/cleanup_script.py
   
   # Test different languages
   export AWS_IOT_LANG=es  # Spanish
   export AWS_IOT_LANG=ja  # Japanese
   export AWS_IOT_LANG=zh  # Chinese
   ```

4. **Verifique se os Arquivos de Mensagem Existem**:
   ```bash
   # Check if translation files exist
   ls i18n/en/cleanup_script.json
   ls i18n/es/cleanup_script.json
   # etc.
   ```

**Prevenção**: Ao adicionar novos scripts ou idiomas:
- Use a implementação correta de `get_message()` de scripts que funcionam
- Certifique-se de que os códigos de idioma correspondam exatamente aos nomes de diretório
- Teste com vários idiomas antes da implantação
- Use os scripts de validação em `docs/templates/validation_scripts/`

### Problema: Seleção de idioma não funciona com variáveis de ambiente
**Sintomas**: Scripts sempre solicitam seleção de idioma apesar de definir `AWS_IOT_LANG`

**Solução**:
1. **Verifique o Formato da Variável de Ambiente**:
   ```bash
   # Supported formats
   export AWS_IOT_LANG=en        # English
   export AWS_IOT_LANG=english   # English
   export AWS_IOT_LANG=es        # Spanish
   export AWS_IOT_LANG=español   # Spanish
   export AWS_IOT_LANG=ja        # Japanese
   export AWS_IOT_LANG=japanese  # Japanese
   export AWS_IOT_LANG=zh        # Chinese
   export AWS_IOT_LANG=chinese   # Chinese
   export AWS_IOT_LANG=pt        # Portuguese
   export AWS_IOT_LANG=português # Portuguese
   export AWS_IOT_LANG=ko        # Korean
   export AWS_IOT_LANG=korean    # Korean
   ```

2. **Verifique se a Variável de Ambiente Está Definida**:
   ```bash
   echo $AWS_IOT_LANG
   ```

3. **Teste a Seleção de Idioma**:
   ```bash
   python3 -c "
   import sys, os
   sys.path.append('i18n')
   from language_selector import get_language
   print('Selected language:', get_language())
   "
   ```

### Problema: Traduções ausentes para novos idiomas
**Sintomas**: Scripts voltam para o inglês ou mostram chaves de mensagem para idiomas não suportados

**Solução**:
1. **Adicione Diretório de Idioma**: Crie estrutura de diretório para novo idioma
2. **Copie Arquivos de Tradução**: Use traduções existentes como modelos
3. **Atualize o Seletor de Idioma**: Adicione novo idioma à lista suportada
4. **Teste Completamente**: Verifique se todos os scripts funcionam com o novo idioma

Para instruções detalhadas, consulte `docs/templates/NEW_LANGUAGE_TEMPLATE.md`.

## Limitações da API do AWS IoT Jobs

### Problema: Não é possível acessar detalhes de execução de trabalho para trabalhos concluídos
**Sintomas**: Erro ao tentar explorar detalhes de execução de trabalho para trabalhos concluídos, falhados ou cancelados

**Exemplo de Erro**:
```
❌ Error in Job Execution Detail upgradeSedanvehicle110_1761321268 on Vehicle-VIN-016: 
Job Execution has reached terminal state. It is neither IN_PROGRESS nor QUEUED
❌ Failed to get job execution details. Check job ID and thing name.
```

**Causa Raiz**: A AWS fornece duas APIs diferentes para acessar detalhes de execução de trabalho:

1. **IoT Jobs Data API** (serviço `iot-jobs-data`):
   - Endpoint: `describe_job_execution`
   - **Limitação**: Funciona apenas para trabalhos no status `IN_PROGRESS` ou `QUEUED`
   - **Erro**: Retorna "Job Execution has reached terminal state" para trabalhos concluídos
   - **Caso de Uso**: Projetado para dispositivos obterem suas instruções de trabalho atuais

2. **IoT API** (serviço `iot`):
   - Endpoint: `describe_job_execution`
   - **Capacidade**: Funciona para trabalhos em QUALQUER status (COMPLETED, FAILED, CANCELED, etc.)
   - **Sem Restrições**: Pode acessar dados históricos de execução de trabalho
   - **Caso de Uso**: Projetado para gerenciamento e monitoramento de todas as execuções de trabalho

**Solução**: O script explore_jobs foi atualizado para usar a IoT API em vez da IoT Jobs Data API.

**Mudança de Código**:
```python
# Before (limited to active jobs only)
execution_response = self.iot_jobs_data_client.describe_job_execution(
    jobId=job_id,
    thingName=thing_name,
    includeJobDocument=True
)

# After (works for all job statuses)
execution_response = self.iot_client.describe_job_execution(
    jobId=job_id,
    thingName=thing_name
)
```

**Verificação**: Após a correção, agora você pode explorar detalhes de execução de trabalho para:
- ✅ Trabalhos COMPLETED
- ✅ Trabalhos FAILED  
- ✅ Trabalhos CANCELED
- ✅ Trabalhos IN_PROGRESS
- ✅ Trabalhos QUEUED
- ✅ Qualquer outro status de trabalho

**Benefícios Adicionais**:
- Acesso a dados históricos de execução de trabalho
- Melhores capacidades de solução de problemas para implantações falhadas
- Trilha de auditoria completa de tentativas de atualização de dispositivo

### Problema: Documento de trabalho não disponível nos detalhes de execução
**Sintomas**: Detalhes de execução de trabalho são exibidos, mas o documento de trabalho está faltando

**Solução**: O script agora inclui um mecanismo de fallback:
1. Primeiro tenta obter o documento de trabalho dos detalhes de execução
2. Se não estiver disponível, recupera dos detalhes principais do trabalho
3. Exibe mensagem apropriada se o documento de trabalho não estiver disponível

Isso garante que você sempre possa ver as instruções de trabalho que foram enviadas ao dispositivo, independentemente do status do trabalho ou limitações da API.
