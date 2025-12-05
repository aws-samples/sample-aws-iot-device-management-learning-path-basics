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
- Estabelece funções do AWS Identity and Access Management (IAM) para operações seguras
- Cria grupos de coisas estáticos por país (convenção de nomenclatura Fleet)
- **Processamento Paralelo**: Operações concorrentes para provisionamento mais rápido
- **Tratamento de Erros Aprimorado**: Tratamento robusto de exceções do boto3

**Entradas Interativas**:
1. Tipos de coisas (padrão: SedanVehicle,SUVVehicle,TruckVehicle)
2. Versões de pacotes (padrão: 1.0.0,1.1.0)
3. Seleção de continente (1-7)
4. Países (contagem ou códigos específicos)
5. Contagem de dispositivos (padrão: 100)

**Parâmetros de Linha de Comando**:
- `--things-prefix PREFIX` - Prefixo personalizado para nomes de coisas (padrão: "Vehicle-VIN-")
  - Deve ter de 1 a 20 caracteres
  - Apenas alfanuméricos, hífens, sublinhados e dois-pontos
  - Exemplo: `--things-prefix "Fleet-Device-"` cria Fleet-Device-001, Fleet-Device-002, etc.

**Comportamento de Marcação de Recursos**:
Todos os recursos criados são automaticamente marcados com:
- `workshop=learning-aws-iot-dm-basics` - Identifica recursos do workshop
- `creation-date=YYYY-MM-DD` - Timestamp para rastreamento

**Recursos Marcados**:
- Tipos de coisas
- Grupos de coisas (grupos estáticos)
- Pacotes de software
- Versões de pacotes de software
- Jobs
- Buckets S3
- Funções IAM

**Tratamento de Falha de Marcação**:
- Falhas de marcação não impedem a criação de recursos
- O script continua com avisos para tags falhadas
- Relatório de resumo mostra recursos sem tags
- Script de limpeza usa padrões de nomenclatura como fallback

**Pausas Educacionais**: 8 momentos de aprendizado explicando conceitos de IoT

**Limites de Taxa**: Limitação inteligente de API da AWS (80 TPS para coisas, 8 TPS para tipos de coisas)

**Desempenho**: Execução paralela quando não está em modo de depuração, sequencial em modo de depuração para saída limpa

**Marcação de Recursos**:
- **Tags Automáticas de Workshop**: Todos os recursos marcáveis recebem a tag `workshop=learning-aws-iot-dm-basics`
- **Recursos Suportados**: Tipos de coisas, grupos de coisas, pacotes, jobs, buckets S3, funções IAM
- **Recursos Não Marcáveis**: Coisas, certificados e shadows dependem de convenções de nomenclatura
- **Tratamento de Falha de Tag**: Degradação graciosa - continua a criação de recursos se a marcação falhar
- **Integração de Limpeza**: Tags permitem identificação segura durante operações de limpeza

**Convenção de Nomenclatura de Coisas**:
- **Parâmetro --things-prefix**: Prefixo configurável para nomes de coisas (padrão: "Vehicle-VIN-")
- **Padrão de Nomenclatura**: `{prefix}{sequential_number}` (ex: Vehicle-VIN-001, Vehicle-VIN-002)
- **Numeração Sequencial**: Números de 3 dígitos preenchidos com zeros (001-999)
- **Validação de Prefixo**: Apenas alfanuméricos, hífens, sublinhados, dois-pontos; máximo 20 caracteres
- **Suporte Legado**: Também reconhece o padrão antigo `vehicle-{country}-{type}-{index}`
- **Integração de Limpeza**: Padrões de nomenclatura permitem identificação de recursos não marcáveis

**Exemplos de Uso**:
```bash
# Usar prefixo padrão (Vehicle-VIN-)
python scripts/provision_script.py

# Usar prefixo personalizado
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Prefixo personalizado cria: Fleet-Device-001, Fleet-Device-002, etc.
```

---

### scripts/cleanup_script.py
**Propósito**: Remoção segura de recursos AWS IoT para evitar custos contínuos usando APIs nativas do boto3 com identificação inteligente de recursos.

**Opções de Limpeza**:
1. **TODOS os recursos** - Limpeza completa de infraestrutura
2. **Apenas coisas** - Remover dispositivos mas manter infraestrutura
3. **Apenas grupos de coisas** - Remover agrupamentos mas manter dispositivos

**Parâmetros de Linha de Comando**:
- `--things-prefix PREFIX` - Prefixo personalizado para identificação de coisas (padrão: "Vehicle-VIN-")
  - Deve corresponder ao prefixo usado durante o provisionamento
  - Usado para identificar coisas com padrões de nomenclatura personalizados
  - Exemplo: `--things-prefix "Fleet-Device-"` identifica Fleet-Device-001, Fleet-Device-002, etc.
- `--dry-run` - Visualizar o que seria excluído sem fazer alterações
  - Mostra todos os recursos que seriam excluídos
  - Exibe o método de identificação para cada recurso
  - Nenhuma exclusão real é realizada
  - Útil para verificar o escopo da limpeza antes da execução

**Métodos de Identificação de Recursos**:

O script de limpeza usa um sistema de identificação de três camadas para identificar com segurança os recursos do workshop:

**1. Identificação Baseada em Tags (Prioridade Mais Alta)**:
- Verifica a tag `workshop=learning-aws-iot-dm-basics`
- Método mais confiável para recursos criados com marcação
- Funciona para: tipos de coisas, grupos de coisas, pacotes, versões de pacotes, jobs, buckets S3, funções IAM

**2. Identificação de Padrão de Nomenclatura (Fallback)**:
- Corresponde nomes de recursos com padrões de workshop
- Usado quando tags não estão presentes ou não são suportadas
- Padrões incluem:
  - Coisas: `Vehicle-VIN-###` ou padrão de prefixo personalizado (ex: `Fleet-Device-###`)
  - Tipos de coisas: `SedanVehicle`, `SUVVehicle`, `TruckVehicle`
  - Grupos de coisas: `Fleet-*` (grupos estáticos)
  - Grupos dinâmicos: `DynamicGroup-*`
  - Pacotes: `SedanVehicle-Package`, `SUVVehicle-Package`, `TruckVehicle-Package`
  - Jobs: `OTA-Job-*`, `Command-Job-*`
  - Buckets S3: `iot-dm-workshop-*`
  - Funções IAM: `IoTJobsRole`, `IoTPackageConfigRole`

**3. Identificação Baseada em Associação (Para Recursos Não Marcáveis)**:
- Usado para recursos que não podem ser marcados diretamente
- Certificados: Identificados por anexo a coisas do workshop
- Shadows: Identificados por pertencer a coisas do workshop
- Garante limpeza completa de recursos dependentes

**Processo de Identificação**:
1. Para cada recurso, verifica tags primeiro
2. Se nenhuma tag de workshop for encontrada, verifica padrão de nomenclatura
3. Se não houver correspondência de padrão, verifica associações (para certificados/shadows)
4. Se nenhum método de identificação for bem-sucedido, o recurso é ignorado
5. Modo de depuração mostra qual método identificou cada recurso

**Recursos**:
- **Implementação Nativa do boto3**: Sem dependências de CLI, melhor tratamento de erros
- **Identificação Inteligente de Recursos**: Sistema de três camadas (tags → nomenclatura → associações)
- **Modo Dry-Run**: Visualizar exclusões sem fazer alterações
- **Suporte a Prefixo Personalizado**: Identificar coisas com padrões de nomenclatura personalizados
- **Processamento paralelo** com limitação de taxa inteligente
- **Limpeza Aprimorada do S3**: Exclusão adequada de objetos versionados usando paginadores
- Distingue automaticamente grupos estáticos vs dinâmicos
- Lida com depreciação de tipos de coisas (espera de 5 minutos)
- Cancela e exclui AWS IoT Jobs com monitoramento de status
- Limpeza abrangente de funções e políticas do IAM
- Desabilita configuração do Fleet Indexing
- **Limpeza de Shadows**: Remove shadows clássicos e $package
- **Desvinculação de Principais**: Desvincula adequadamente certificados e políticas
- **Relatório Abrangente**: Mostra recursos excluídos e ignorados com contagens

**Recursos de Segurança**:
- Requer digitar "DELETE" para confirmar (exceto modo dry-run)
- Ignora automaticamente recursos não relacionados ao workshop
- Mostra resumo do que será excluído
- Modo dry-run para verificação antes da exclusão real
- Tratamento de erros continua a limpeza mesmo se recursos individuais falharem

**Exemplo de Modo Dry-Run**:
```bash
python scripts/cleanup_script.py --dry-run
```
Saída mostra:
- Recursos que seriam excluídos (com método de identificação)
- Recursos que seriam ignorados (recursos não relacionados ao workshop)
- Contagens totais por tipo de recurso
- Nenhuma exclusão real realizada

**Exemplo de Prefixo Personalizado**:
```bash
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```
Identifica e exclui:
- Coisas correspondentes ao padrão Fleet-Device-###
- Certificados e shadows associados
- Outros recursos do workshop (identificados por tags ou padrões)

**Desempenho**: Execução paralela respeitando limites de API da AWS (80 TPS coisas, 4 TPS grupos dinâmicos)

**Exemplo de Limpeza Baseada em Tags**:
```
Escaneando tipos de coisas...
Encontrados 3 tipos de coisas
  ✓ SedanVehicle (identificado por tag: workshop=learning-aws-iot-dm-basics)
  ✓ SUVVehicle (identificado por tag: workshop=learning-aws-iot-dm-basics)
  ✓ TruckVehicle (identificado por tag: workshop=learning-aws-iot-dm-basics)

Escaneando grupos de coisas...
Encontrados 5 grupos de coisas
  ✓ fleet-US (identificado por tag: workshop=learning-aws-iot-dm-basics)
  ✓ fleet-CA (identificado por tag: workshop=learning-aws-iot-dm-basics)
  ✗ production-fleet (ignorado - sem tag de workshop)
```

**Exemplo de Limpeza Baseada em Nomenclatura**:
```
Escaneando coisas...
Encontradas 102 coisas
  ✓ Vehicle-VIN-001 (identificado por padrão de nomenclatura: Vehicle-VIN-###)
  ✓ Vehicle-VIN-002 (identificado por padrão de nomenclatura: Vehicle-VIN-###)
  ✓ vehicle-US-sedan-1 (identificado por padrão legado)
  ✗ production-device-001 (ignorado - sem correspondência de padrão)
```

**Exemplo de Limpeza Baseada em Associação**:
```
Processando coisa: Vehicle-VIN-001
  ✓ Shadow clássico (identificado por associação com coisa do workshop)
  ✓ Shadow $package (identificado por associação com coisa do workshop)
  ✓ Certificado abc123 (identificado por associação com coisa do workshop)
  
Processando coisa: production-device-001
  ✗ Certificado xyz789 (ignorado - anexado a coisa não relacionada ao workshop)
```

**Saída de Resumo de Limpeza**:
```
Resumo de Limpeza:
================
Recursos Excluídos:
  - Coisas IoT: 100
  - Grupos de Coisas: 5
  - Tipos de Coisas: 3
  - Pacotes: 3
  - Jobs: 2
  - Buckets S3: 1
  - Funções IAM: 2
  Total: 116

Recursos Ignorados:
  - Coisas IoT: 2 (recursos não relacionados ao workshop)
  - Grupos de Coisas: 1 (recurso não relacionado ao workshop)
  Total: 3

Tempo de Execução: 45.3 segundos
```

**Solução de Problemas de Limpeza**:

**Problema: Recursos Não Estão Sendo Excluídos**

Sintomas:
- Script de limpeza ignora recursos que você espera que sejam excluídos
- Contagem de "recursos ignorados" é maior do que o esperado
- Recursos específicos permanecem após a limpeza

Soluções:
1. **Verificar Correspondência de Prefixo de Coisa**:
   ```bash
   # Se você usou prefixo personalizado durante o provisionamento:
   python scripts/provision_script.py --things-prefix "MyPrefix-"
   
   # Você DEVE usar o mesmo prefixo durante a limpeza:
   python scripts/cleanup_script.py --things-prefix "MyPrefix-"
   ```

2. **Verificar Tags de Recursos**:
   - Execute a limpeza em modo de depuração para ver métodos de identificação
   - Verifique se recursos marcáveis têm a tag `workshop=learning-aws-iot-dm-basics`
   - Verifique Console AWS → IoT Core → Tags de recursos

3. **Verificar Padrões de Nomenclatura**:
   - Coisas devem corresponder: `{prefix}###` ou `vehicle-{country}-{type}-{index}`
   - Grupos devem corresponder: `fleet-{country}` ou conter "workshop"
   - Use modo dry-run para ver o que seria identificado

4. **Usar Dry-Run Primeiro**:
   ```bash
   # Visualizar o que será excluído
   python scripts/cleanup_script.py --dry-run
   
   # Verificar saída para recursos ignorados
   # Verificar métodos de identificação em modo de depuração
   ```

**Problema: Falhas de Aplicação de Tag Durante o Provisionamento**

Sintomas:
- Script de provisionamento mostra avisos "Falha ao aplicar tags"
- Recursos criados mas sem tags de workshop
- Script de limpeza ignora recursos que deveriam ser excluídos

Soluções:
1. **Verificar Permissões IAM**:
   - Verifique se usuário/função IAM tem permissões de marcação
   - Ações necessárias: `iot:TagResource`, `s3:PutBucketTagging`, `iam:TagRole`

2. **Confiar em Convenções de Nomenclatura**:
   - Recursos sem tags ainda podem ser identificados por padrões de nomenclatura
   - Garanta nomenclatura consistente durante o provisionamento
   - Use o mesmo --things-prefix para provisionamento e limpeza

3. **Adição Manual de Tag** (se necessário):
   ```bash
   # Adicionar tags manualmente via AWS CLI
   aws iot tag-resource --resource-arn <arn> --tags workshop=learning-aws-iot-dm-basics
   ```

**Problema: Limpeza Exclui Recursos Errados**

Sintomas:
- Recursos não relacionados ao workshop sendo identificados para exclusão
- Dry-run mostra recursos inesperados

Soluções:
1. **Sempre Usar Dry-Run Primeiro**:
   ```bash
   python scripts/cleanup_script.py --dry-run
   ```

2. **Revisar Padrões de Nomenclatura**:
   - Garanta que recursos de produção não correspondam a padrões de workshop
   - Evite usar prefixo "Vehicle-VIN-" para coisas de produção
   - Não use prefixo "fleet-" para grupos de produção

3. **Verificar Conflitos de Tags**:
   - Verifique se nenhum recurso de produção tem tags de workshop
   - Revise políticas de tags em sua conta AWS

**Problema: Limpeza Falha com Erros de Permissão**

Sintomas:
- Erros "AccessDeniedException" ou "UnauthorizedException"
- Conclusão parcial da limpeza
- Alguns tipos de recursos excluídos, outros ignorados

Soluções:
1. **Verificar Permissões IAM**:
   - Permissões necessárias listadas em README.md
   - Verifique política IAM para todas as ações necessárias
   - Verifique permissões para: IoT, S3, IAM, Fleet Indexing

2. **Verificar Políticas de Recursos**:
   - Políticas de bucket S3 podem bloquear exclusão
   - Políticas de confiança de função IAM podem impedir exclusão
   - Revise políticas em nível de recurso

3. **Usar Modo de Depuração**:
   ```bash
   # Executar com depuração para ver erros exatos da API
   python scripts/cleanup_script.py
   # Responda 'y' para modo de depuração
   ```

**Problema: Limpeza Demora Muito**

Sintomas:
- Limpeza executa por períodos prolongados
- Progresso parece lento
- Erros de timeout

Soluções:
1. **Duração Esperada**:
   - 100 coisas: ~2-3 minutos
   - 1000 coisas: ~15-20 minutos
   - Exclusão de tipo de coisa: +5 minutos (espera de depreciação necessária)

2. **Limitação de Taxa**:
   - Script respeita limites de API da AWS automaticamente
   - Processamento paralelo otimiza desempenho
   - Modo de depuração executa sequencialmente (mais lento mas saída mais clara)

3. **Monitorar Progresso**:
   - Observe indicadores de progresso em tempo real
   - Verifique Console AWS para status de exclusão
   - Use modo de depuração para ver cada operação

**Problema: Dry-Run Mostra Resultados Diferentes da Limpeza Real**

Sintomas:
- Dry-run identifica recursos que a limpeza real ignora
- Comportamento inconsistente entre modos

Soluções:
1. **Mudanças de Estado de Recursos**:
   - Recursos podem ser modificados entre dry-run e limpeza real
   - Tags podem ser adicionadas/removidas por outros processos
   - Execute dry-run novamente imediatamente antes da limpeza real

2. **Modificações Concorrentes**:
   - Outros usuários/processos podem estar modificando recursos
   - Coordene o timing de limpeza com a equipe
   - Use bloqueio de recursos se disponível

3. **Problemas de Cache**:
   - Respostas da API AWS podem ser armazenadas em cache brevemente
   - Aguarde alguns segundos entre dry-run e limpeza real
   - Atualize Console AWS para verificar estado atual

**Problema: Limpeza Parcial**

Sintomas:
- Alguns recursos excluídos, outros permanecem
- Mensagens de erro durante a limpeza
- Resultados de limpeza incompletos

Soluções:
1. **Problemas de Dependência**:
   - Alguns recursos podem falhar ao excluir devido a dependências
   - Script continua com recursos restantes
   - Verifique mensagens de erro para falhas específicas
   - Execute o script novamente para limpar recursos restantes

2. **Estado de Recursos**:
   - Tipos de coisas devem ser depreciados antes da exclusão (espera de 5 minutos)
   - Jobs devem ser cancelados antes da exclusão
   - Buckets S3 devem estar vazios antes da exclusão

3. **Executar Limpeza Novamente**:
   ```bash
   # Execute a limpeza novamente para capturar recursos restantes
   python scripts/cleanup_script.py
   ```

**Melhores Práticas para Limpeza Segura**:

1. **Sempre Comece com Dry-Run**:
   ```bash
   python scripts/cleanup_script.py --dry-run
   ```

2. **Verificar Correspondência de Prefixo de Coisa**:
   - Use o mesmo --things-prefix do provisionamento
   - Documente prefixos personalizados para referência da equipe

3. **Usar Modo de Depuração para Solução de Problemas**:
   - Veja métodos de identificação para cada recurso
   - Entenda por que recursos são ignorados
   - Verifique correspondências de tags e padrões de nomenclatura

4. **Coordenar com a Equipe**:
   - Comunique o timing de limpeza
   - Verifique se não há workshops ativos usando recursos
   - Documente resultados de limpeza

5. **Monitorar Console AWS**:
   - Verifique se recursos foram excluídos conforme esperado
   - Verifique recursos de workshop restantes
   - Revise logs do CloudWatch se disponíveis

6. **Manter Nomenclatura Consistente**:
   - Use prefixos padrão em todos os workshops
   - Documente convenções de nomenclatura
   - Evite conflitos de nomenclatura de produção

**Limpeza Baseada em Tags Não Funciona**:
- Verifique se recursos foram criados com marcação habilitada
- Verifique se a marcação falhou durante o provisionamento (veja saída do script de provisionamento)
- Identificação por padrão de nomenclatura será usada como fallback
- Considere usar `--dry-run` para verificar métodos de identificação

---


### scripts/create_job.py
**Propósito**: Criar AWS IoT Jobs para atualizações de firmware over-the-air usando APIs nativas boto3.

**Recursos**:
- **Implementação Nativa boto3**: Chamadas diretas de API para melhor desempenho
- Seleção interativa de grupo de coisas (único ou múltiplo)
- Seleção de versão de pacote com resolução de ARN
- Configuração de job contínuo (inclui automaticamente novos dispositivos)
- Configuração de URL pré-assinada (expiração de 1 hora)
- Suporte a segmentação de múltiplos grupos
- **Tipos de Job Aprimorados**: Suporte para tipos de job OTA e personalizados
- **Configuração Avançada**: Políticas de rollout, critérios de aborto, configurações de timeout

**Configuração de Job**:
- IDs de job gerados automaticamente com timestamps
- Placeholders de URL pré-assinada do AWS IoT
- Formatação adequada de ARN para recursos
- Estrutura abrangente de documento de job
- **Conteúdo Educacional**: Explica opções de configuração de job

---

### scripts/simulate_job_execution.py
**Propósito**: Simular comportamento realista de dispositivo durante atualizações de firmware usando APIs nativas boto3.

**Recursos**:
- **Implementação Nativa boto3**: Integração direta com IoT Jobs Data API
- Downloads reais de artefatos do Amazon S3 via URLs pré-assinadas
- **Execução Paralela de Alto Desempenho** (150 TPS com controle de semáforo)
- Taxas de sucesso/falha configuráveis
- **Preparação de plano visível** - Mostra cada dispositivo sendo atribuído status de sucesso/falha
- **Confirmação do usuário** - Pergunta para prosseguir após preparação do plano
- **Visibilidade de operação** - Mostra progresso de download e atualizações de status de job para cada dispositivo
- **Tratamento de Erros Aprimorado**: Gerenciamento robusto de exceções boto3
- Rastreamento de progresso com relatórios detalhados
- **Formatação JSON Limpa**: Exibição de documento de job formatado adequadamente

**Fluxo de Processo**:
1. Escaneia jobs ativos usando APIs nativas
2. Obtém execuções pendentes (QUEUED/IN_PROGRESS)
3. **Prepara plano de execução** - Mostra atribuições de dispositivos e pede confirmação
4. Baixa firmware real do Amazon S3 (mostra progresso por dispositivo)
5. Atualiza status de execução de job usando IoT Jobs Data API
6. Relata estatísticas abrangentes de sucesso/falha

**Melhorias de Desempenho**:
- **Processamento Paralelo**: Execução concorrente quando não em modo de depuração
- **Limitação de Taxa**: Throttling inteligente baseado em semáforo
- **Eficiência de Memória**: Downloads em streaming para arquivos de firmware grandes

**Melhorias de Visibilidade**:
- Preparação de plano mostra: `[1/100] Vehicle-VIN-001 -> SUCCESS`
- Progresso de download mostra: `Vehicle-VIN-001: Baixando firmware do S3...`
- Confirmação de tamanho de arquivo: `Vehicle-VIN-001: Baixado 2.1KB de firmware`
- Atualizações de status mostram: `Vehicle-VIN-001: Execução de job SUCCEEDED`

---

### scripts/explore_jobs.py
**Propósito**: Exploração interativa de AWS IoT Jobs para monitoramento e solução de problemas usando APIs nativas boto3.

**Opções de Menu**:
1. **Listar todos os jobs** - Visão geral em todos os status com escaneamento paralelo
2. **Explorar job específico** - Configuração detalhada de job com formatação JSON limpa
3. **Explorar execução de job** - Progresso de dispositivo individual usando IoT Jobs Data API
4. **Listar execuções de job** - Todas as execuções para um job com verificação de status paralela
5. **Cancelar job** - Cancelar jobs ativos com análise de impacto e orientação educacional
6. **Excluir job** - Excluir jobs concluídos/cancelados com tratamento automático de flag de força
7. **Ver estatísticas** - Análise abrangente de job com avaliação de saúde e recomendações

**Recursos**:
- **Implementação Nativa boto3**: Integração direta de API para melhor desempenho
- **Escaneamento Paralelo de Jobs**: Verificação de status concorrente em todos os estados de job
- **Exibição JSON Limpa**: Documentos de job formatados adequadamente sem caracteres de escape
- Indicadores de status codificados por cores
- Seleção interativa de job com listagem de jobs disponíveis
- Exibição detalhada de configuração de URL pré-assinada
- Estatísticas resumidas de execução com codificação de cores
- **Tratamento de Erros Aprimorado**: Gerenciamento robusto de exceções boto3
- Loop de exploração contínua
- **Gerenciamento de Ciclo de Vida de Job**: Operações de cancelamento e exclusão com confirmações de segurança
- **Análise Avançada**: Estatísticas abrangentes com avaliações de saúde

**Recursos de Cancelamento de Job**:
- Escaneia jobs ativos (IN_PROGRESS, SCHEDULED)
- Mostra detalhes de job e contagem de alvos
- Análise de impacto com contagens de execução por status (QUEUED, IN_PROGRESS, SUCCEEDED, FAILED)
- Conteúdo educacional explicando quando e por que cancelar jobs
- Confirmação de segurança exigindo "CANCEL" para prosseguir
- Comentário de cancelamento opcional para trilha de auditoria
- Atualizações de status em tempo real

**Recursos de Exclusão de Job**:
- Escaneia jobs excluíveis (COMPLETED, CANCELED)
- Mostra timestamps de conclusão de job
- Verifica histórico de execução para determinar se flag de força é necessária
- Conteúdo educacional sobre implicações de exclusão
- Flag de força automática quando existem execuções
- Confirmação de segurança exigindo "DELETE" para prosseguir
- Explica diferença entre operações de cancelamento e exclusão

**Recursos de Ver Estatísticas**:
- Visão geral abrangente de job (status, datas de criação/conclusão, alvos)
- Estatísticas de execução com porcentagens por status
- Cálculos de taxa de sucesso/falha
- Detalhamento detalhado de todos os estados de execução
- Avaliação de saúde (Excelente ≥95%, Bom ≥80%, Ruim ≥50%, Crítico <50%)
- Conteúdo educacional sobre estados de execução e padrões de falha
- Recomendações contextuais baseadas no estado do job:
  - Sem execuções: Verificar conectividade de dispositivo e associação de grupo
  - Cancelado cedo: Revisar razões de cancelamento
  - Dispositivos removidos: Verificar existência de dispositivo
  - Em progresso: Aguardar e monitorar
  - Alta taxa de falha: Investigar e considerar cancelamento
  - Falha moderada: Monitorar de perto
  - Desempenho excelente: Documentar padrões de sucesso

**Melhorias de Desempenho**:
- **Processamento Paralelo**: Operações concorrentes quando não em modo de depuração
- **Paginação Inteligente**: Tratamento eficiente de listas grandes de jobs
- **Limitação de Taxa**: Throttling adequado de API com semáforos

---

### scripts/manage_packages.py
**Propósito**: Gerenciamento abrangente de Pacotes de Software AWS IoT, rastreamento de dispositivos e rollback de versão usando APIs nativas boto3.

**Operações**:
1. **Criar Pacote** - Criar novos contêineres de pacote de software
2. **Criar Versão** - Adicionar versões com upload e publicação de firmware S3 (com momentos de aprendizado)
3. **Listar Pacotes** - Exibir pacotes com opções de descrição interativas
4. **Descrever Pacote** - Mostrar detalhes de pacote com exploração de versão
5. **Descrever Versão** - Mostrar detalhes de versão específica e artefatos do Amazon S3
6. **Verificar Configuração** - Ver status de configuração de pacote e função IAM
7. **Habilitar Configuração** - Habilitar atualizações automáticas de shadow com criação de função IAM
8. **Desabilitar Configuração** - Desabilitar atualizações automáticas de shadow
9. **Verificar Versão de Dispositivo** - Inspecionar shadow $package para dispositivos específicos (suporte a múltiplos dispositivos)
10. **Reverter Versões** - Rollback de versão em toda a frota usando Fleet Indexing

**Recursos Principais**:
- **Integração Amazon S3**: Upload automático de firmware com versionamento
- **Navegação Interativa**: Fluxo contínuo entre operações de listar, descrever e versão
- **Gerenciamento de Configuração de Pacote**: Controlar integração Jobs-to-Shadow
- **Rastreamento de Dispositivo**: Inspeção de versão de pacote de dispositivo individual
- **Rollback de Frota**: Reversão de versão usando consultas Fleet Indexing
- **Abordagem Educacional**: Momentos de aprendizado ao longo dos fluxos de trabalho
- **Gerenciamento de Função IAM**: Criação automática de função para configuração de pacote

**Configuração de Pacote**:
- **Verificar Status**: Mostra estado habilitado/desabilitado e ARN de função IAM
- **Habilitar**: Cria IoTPackageConfigRole com permissões de shadow $package
- **Desabilitar**: Para atualizações automáticas de shadow na conclusão de job
- **Educacional**: Explica integração Jobs-to-Shadow e requisitos IAM

**Rastreamento de Versão de Dispositivo**:
- **Suporte a Múltiplos Dispositivos**: Verificar múltiplos dispositivos em sequência
- **Inspeção de Shadow $package**: Mostra versões de firmware atuais e metadados
- **Exibição de Timestamp**: Informações de última atualização para cada pacote
- **Tratamento de Erros**: Mensagens claras para dispositivos ou shadows ausentes

**Rollback de Versão**:
- **Consultas Fleet Indexing**: Encontrar dispositivos por tipo de coisa e versão
- **Visualização de Lista de Dispositivos**: Mostra dispositivos que serão revertidos (primeiros 10 + contagem)
- **Confirmação Necessária**: Digite 'REVERT' para prosseguir com atualizações de shadow
- **Status de Dispositivo Individual**: Mostra sucesso/falha de reversão por dispositivo
- **Rastreamento de Progresso**: Status de atualização em tempo real com contagens de sucesso
- **Educacional**: Explica conceitos de rollback e gerenciamento de shadow

**Visibilidade de Rollback**:
- Visualização de dispositivo: `1. Vehicle-VIN-001`, `2. Vehicle-VIN-002`, `... e mais 90 dispositivos`
- Resultados individuais: `Vehicle-VIN-001: Revertido para versão 1.0.0`
- Tentativas falhadas: `Vehicle-VIN-002: Falha ao reverter`

**Foco de Aprendizado**:
- Ciclo de vida completo de firmware desde criação até rollback
- Configuração de pacote e atualizações automáticas de shadow
- Gerenciamento e rastreamento de inventário de dispositivos
- Fleet Indexing para operações de gerenciamento de versão

---

### scripts/manage_dynamic_groups.py
**Propósito**: Gerenciamento abrangente de grupos de coisas dinâmicos com validação Fleet Indexing usando APIs nativas boto3.

**Operações**:
1. **Criar Grupos Dinâmicos** - Dois métodos de criação:
   - **Assistente guiado**: Seleção interativa de critérios
   - **Consulta personalizada**: Entrada direta de consulta Fleet Indexing
2. **Listar Grupos Dinâmicos** - Exibir todos os grupos com contagens de membros e consultas
3. **Excluir Grupos Dinâmicos** - Exclusão segura com confirmação
4. **Testar Consultas** - Validar consultas Fleet Indexing personalizadas

**Métodos de Criação**:
- **Assistente Guiado** (todos opcionais):
  - Países: Único ou múltiplo (ex: US,CA,MX)
  - Tipo de Coisa: Categoria de veículo (ex: SedanVehicle)
  - Versões: Único ou múltiplo (ex: 1.0.0,1.1.0)
  - Nível de Bateria: Comparações (ex: >50, <30, =75)
- **Consulta Personalizada**: Entrada direta de string de consulta Fleet Indexing

**Recursos**:
- **Modos duplos de criação**: Assistente guiado ou entrada de consulta personalizada
- Nomenclatura inteligente de grupo (gerada automaticamente ou personalizada)
- Construção e validação de consulta Fleet Indexing
- **Visualização de correspondência de dispositivo em tempo real** (mostra dispositivos correspondentes antes da criação)
- Exibição de contagem de membros para grupos existentes
- Exclusão segura com prompts de confirmação
- Capacidades de teste de consulta personalizada
- Validação de consulta previne criação de grupo vazio

**Exemplos de Consulta**:
- Critério único: `thingTypeName:SedanVehicle AND attributes.country:US`
- Múltiplos critérios: `thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- Versões de pacote: `shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- Complexo personalizado: `(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**Propósito**: Validação de sintaxe pré-publicação para pipeline CI/CD.

**Verificações**:
- Validação de sintaxe Python para todos os scripts
- Verificação de disponibilidade de importação
- Validação de requirements.txt
- Listagem de dependências

**Uso**: Executado automaticamente pelo fluxo de trabalho GitHub Actions

---

## Dependências de Script

### Pacotes Python Necessários
- `boto3>=1.40.27` - AWS SDK para Python (versão mais recente para suporte a artefato de pacote)
- `colorama>=0.4.4` - Cores de terminal
- `requests>=2.25.1` - Requisições HTTP para downloads do Amazon S3

### Serviços AWS Usados
- **AWS IoT Core** - Gerenciamento de coisas, jobs, shadows
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

### Momentos de Aprendizado
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
- Mostra todas as chamadas de API do AWS SDK (boto3) com parâmetros
- Exibe respostas completas de API em formato JSON
- Fornece informações detalhadas de erro com rastreamentos de pilha completos
- **Processamento Sequencial**: Executa operações sequencialmente para saída de depuração limpa
- Ajuda com solução de problemas e aprendizado de APIs AWS

## Características de Desempenho

### Limitação de Taxa
Scripts respeitam limites de API AWS:
- Operações de coisa: 80 TPS (limite de 100 TPS)
- Tipos de coisa: 8 TPS (limite de 10 TPS)
- Grupos dinâmicos: 4 TPS (limite de 5 TPS)
- Execuções de job: 150 TPS (limite de 200 TPS)
- Operações de pacote: 8 TPS (limite de 10 TPS)

### Processamento Paralelo
- **Integração Nativa boto3**: Chamadas diretas de AWS SDK para melhor desempenho
- ThreadPoolExecutor para operações concorrentes (quando não em modo de depuração)
- **Limitação de Taxa Inteligente**: Semáforos respeitando limites de API AWS
- **Rastreamento de Progresso Thread-Safe**: Monitoramento de operação concorrente
- **Tratamento de Erros Aprimorado**: Gerenciamento robusto de exceção ClientError boto3
- **Substituição de Modo de Depuração**: Processamento sequencial em modo de depuração para saída limpa

### Gerenciamento de Memória
- Downloads em streaming para arquivos grandes
- Limpeza de arquivo temporário
- Análise JSON eficiente
- Limpeza de recursos na saída

---

### scripts/manage_commands.py
**Propósito**: Gerenciamento abrangente de AWS IoT Commands para enviar comandos em tempo real para dispositivos IoT usando APIs nativas boto3.

**Operações**:
1. **Criar Comando** - Criar novos modelos de comando com definições de formato de payload
2. **Listar Comandos** - Exibir todos os modelos de comando (predefinidos e personalizados)
3. **Ver Detalhes do Comando** - Mostrar especificações completas de modelo de comando
4. **Excluir Comando** - Remover modelos de comando personalizados com confirmações de segurança
5. **Executar Comando** - Enviar comandos para dispositivos ou grupos de coisas
6. **Ver Status do Comando** - Monitorar progresso e resultados de execução de comando
7. **Ver Histórico de Comandos** - Navegar execuções de comando passadas com filtragem
8. **Cancelar Comando** - Cancelar execuções de comando pendentes ou em progresso
9. **Habilitar/Desabilitar Modo de Depuração** - Alternar registro detalhado de API
10. **Sair** - Sair do script

**Recursos Principais**:
- **Implementação Nativa boto3**: Integração direta com AWS IoT Commands API
- **Modelos Automotivos Predefinidos**: Seis modelos de comando de veículo prontos para uso
- **Gerenciamento de Modelo de Comando**: Criar, listar, ver e excluir modelos de comando
- **Execução de Comando**: Enviar comandos para dispositivos individuais ou grupos de coisas
- **Monitoramento de Status**: Rastreamento de execução de comando em tempo real com indicadores de progresso
- **Histórico de Comandos**: Navegar e filtrar execuções de comando passadas
- **Cancelamento de Comando**: Cancelar comandos pendentes ou em progresso
- **Integração de Scripts IoT Core**: Integração perfeita com certificate_manager e mqtt_client_explorer
- **Documentação de Tópico MQTT**: Referência completa de estrutura de tópico
- **Exemplos de Simulação de Dispositivo**: Payloads de resposta de sucesso e falha
- **Abordagem Educacional**: Momentos de aprendizado ao longo dos fluxos de trabalho
- **Suporte Multilíngue**: Suporte completo i18n para 6 idiomas

**Modelos de Comando Automotivo Predefinidos**:
O script inclui seis modelos de comando predefinidos para operações comuns de veículos:

1. **vehicle-lock** - Trancar portas do veículo remotamente
   - Payload: `{"action": "lock", "vehicleId": "string"}`
   - Caso de uso: Travamento remoto de porta para segurança

2. **vehicle-unlock** - Destrancar portas do veículo remotamente
   - Payload: `{"action": "unlock", "vehicleId": "string"}`
   - Caso de uso: Destravamento remoto de porta para acesso

3. **start-engine** - Ligar motor do veículo remotamente
   - Payload: `{"action": "start", "vehicleId": "string", "duration": "number"}`
   - Caso de uso: Partida remota do motor para controle de clima

4. **stop-engine** - Desligar motor do veículo remotamente
   - Payload: `{"action": "stop", "vehicleId": "string"}`
   - Caso de uso: Desligamento de emergência do motor

5. **set-climate** - Definir temperatura do clima do veículo
   - Payload: `{"action": "setClimate", "vehicleId": "string", "temperature": "number", "unit": "string"}`
   - Caso de uso: Pré-condicionamento de temperatura do veículo

6. **activate-horn** - Ativar buzina do veículo
   - Payload: `{"action": "horn", "vehicleId": "string", "duration": "number"}`
   - Caso de uso: Assistência de localização de veículo

**Gerenciamento de Modelo de Comando**:

**Criar Modelo de Comando**:
- Prompts interativos para nome de comando, descrição e formato de payload
- Validação de esquema JSON para estrutura de payload
- Configuração de namespace AWS-IoT
- Tratamento de payload de blob binário com contentType
- Geração e exibição automática de ARN
- Validação contra requisitos AWS IoT Commands:
  - Nome: 1-128 caracteres, alfanumérico/hífen/sublinhado, deve começar com alfanumérico
  - Descrição: 1-256 caracteres
  - Payload: Esquema JSON válido, complexidade máxima de 10KB

**Listar Modelos de Comando**:
- Exibe modelos predefinidos e personalizados
- Formato de tabela codificado por cores com:
  - Nome do modelo
  - Descrição
  - Data de criação
  - ARN do modelo
  - Status (ACTIVE, DEPRECATED, PENDING_DELETION)
- Navegação interativa para ver detalhes do modelo
- Suporte a paginação para listas grandes de modelos

**Ver Detalhes do Comando**:
- Exibição completa de especificação de formato de payload
- Nomes de parâmetros, tipos e restrições
- Campos obrigatórios vs opcionais
- Valores de parâmetro de exemplo
- Metadados de modelo (data de criação, ARN, status)
- Formatação JSON limpa para estrutura de payload

**Excluir Modelo de Comando**:
- Confirmação de segurança exigindo "DELETE" para prosseguir
- Verificação de que nenhum comando ativo usa o modelo
- Proteção contra exclusão de modelos predefinidos
- Mensagens de erro claras para falhas de exclusão
- Limpeza automática de recursos de modelo

**Execução de Comando**:

**Executar Comando**:
- Seleção interativa de modelo de comando de modelos disponíveis
- Seleção de alvo:
  - Dispositivo único (nome da coisa)
  - Grupo de coisas (nome do grupo)
- Validação de alvo:
  - Verificação de existência de dispositivo no registro IoT
  - Validação de grupo de coisas com exibição de contagem de membros
- Coleta de parâmetros correspondendo formato de payload do modelo
- Timeout de execução configurável (padrão 60 segundos)
- Publicação automática de tópico MQTT para:
  - `$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/json`
- Exibição de sucesso com:
  - ID de execução de comando
  - Status inicial (CREATED/IN_PROGRESS)
  - Informações de tópico MQTT
- Suporte a múltiplos alvos (cria execuções separadas por alvo)

**Monitoramento de Status de Comando**:

**Ver Status de Comando**:
- Recuperação de status em tempo real usando GetCommandExecution API
- Exibição de status inclui:
  - ID de execução de comando
  - Nome de dispositivo/grupo alvo
  - Status atual (CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED)
  - Timestamp de criação
  - Timestamp de última atualização
- Indicadores de progresso para status IN_PROGRESS:
  - Exibição de progresso animada
  - Tempo decorrido desde criação
- Informações de comando concluído:
  - Status final (SUCCEEDED/FAILED)
  - Duração de execução
  - Razão de status (se fornecida)
  - Timestamp de conclusão
- Indicadores de status codificados por cores:
  - Verde: SUCCEEDED
  - Amarelo: IN_PROGRESS, CREATED
  - Vermelho: FAILED, TIMED_OUT, CANCELED

**Ver Histórico de Comandos**:
- Histórico abrangente de execução de comando
- Opções de filtragem:
  - Filtro de nome de dispositivo
  - Filtro de status (CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED)
  - Filtro de intervalo de tempo (timestamps de início/fim)
- Suporte a paginação:
  - Tamanho de página configurável (1-100, padrão 50)
  - Navegação de próxima página
  - Exibição de contagem total
- Exibição de histórico inclui:
  - Nome do comando
  - Dispositivo/grupo alvo
  - Status de execução
  - Hora de criação
  - Hora de conclusão (se aplicável)
  - Duração de execução
- Tratamento de histórico vazio com mensagem informativa
- Status codificado por cores para fácil varredura

**Cancelamento de Comando**:

**Cancelar Comando**:
- Entrada interativa de ID de execução de comando
- Confirmação de segurança exigindo "CANCEL" para prosseguir
- Envio de solicitação de cancelamento para AWS IoT
- Verificação de atualização de status (CANCELED)
- Tratamento de rejeição para comandos concluídos:
  - Mensagem de erro clara para comandos já concluídos
  - Exibição de estado atual do comando
- Exibição de informações de falha:
  - Razão de falha
  - Status atual do comando
  - Sugestões de solução de problemas

**Integração de Scripts IoT Core**:

O script fornece orientação abrangente de integração para usar scripts AWS IoT Core para simular tratamento de comando do lado do dispositivo:

**Integração Certificate Manager** (`certificate_manager.py`):
- Criação e gerenciamento de certificado de dispositivo
- Associação certificado-política
- Anexação certificado-coisa
- Configuração de autenticação para conexões MQTT
- Instruções passo a passo de configuração de terminal:
  1. Abrir nova janela de terminal (Terminal 2)
  2. Copiar credenciais AWS do ambiente de workshop
  3. Navegar para diretório de scripts IoT Core
  4. Executar certificate_manager.py para configurar autenticação de dispositivo

**Integração MQTT Client Explorer** (`mqtt_client_explorer.py`):
- Configuração de assinatura de tópico de comando
- Recepção de comando em tempo real
- Publicação de payload de resposta
- Simulação de sucesso/falha
- Fluxo de trabalho de integração passo a passo:
  1. Assinar tópico de solicitação de comando: `$aws/commands/things/<ThingName>/executions/+/request/#`
  2. Receber payloads de comando com ID de execução
  3. Publicar resultado de execução para tópico de resposta: `$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/json`
  4. Opcionalmente assinar tópicos accepted/rejected para confirmação

**Exemplos de Simulação de Dispositivo**:

O script fornece payloads de exemplo completos para simular respostas de dispositivo:

**Exemplo de Resposta de Sucesso**:
```json
{
  "status": "SUCCEEDED",
  "executionId": "<ExecutionId>",
  "statusReason": "Portas do veículo trancadas com sucesso",
  "timestamp": 1701518710000
}
```

**Exemplo de Resposta de Falha**:
```json
{
  "status": "FAILED",
  "executionId": "<ExecutionId>",
  "statusReason": "Não foi possível trancar veículo - mau funcionamento do sensor da porta",
  "timestamp": 1701518710000
}
```

**Valores de Status Válidos**: SUCCEEDED, FAILED, IN_PROGRESS, TIMED_OUT, REJECTED

**Estrutura de Tópico MQTT**:

O script documenta a estrutura completa de tópico MQTT para AWS IoT Commands:

**Tópico de Solicitação de Comando** (dispositivo assina para receber comandos):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request
```

**Tópico de Resposta de Comando** (dispositivo publica resultado de execução):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/<PayloadFormat>
```

**Tópico de Resposta Aceita** (dispositivo assina para confirmação):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted
```

**Tópico de Resposta Rejeitada** (dispositivo assina para notificação de rejeição):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected
```

**Explicações de Componentes de Tópico**:
- `<ThingName>`: Nome da coisa IoT ou ID de cliente MQTT
- `<ExecutionId>`: Identificador único para cada execução de comando (use curinga `+` para assinar todos)
- `<PayloadFormat>`: Indicador de formato (json, cbor) - pode ser omitido se não for JSON/CBOR
- Assinatura curinga: `$aws/commands/things/<ThingName>/executions/+/request/#`

**Alternativa AWS IoT Test Client**:
- Alternativa baseada em console para mqtt_client_explorer
- Acesso via AWS IoT Console → Test → MQTT test client
- Assinar tópicos de comando
- Publicar payloads de resposta
- Útil para teste rápido sem scripts locais

**Momentos de Aprendizado**:

O script inclui momentos de aprendizado contextuais que aparecem automaticamente após operações-chave:

1. **O que são Modelos de Comando?** - Exibido após primeira criação de modelo
   - Explica propósito e estrutura de modelo de comando
   - Descreve requisitos de formato de payload
   - Compara com outros recursos AWS IoT

2. **Commands vs Device Shadow vs Jobs** - Exibido após primeira execução de comando
   - Tabela de comparação mostrando quando usar cada recurso
   - Commands: Ações de dispositivo imediatas em tempo real (segundos)
   - Device Shadow: Sincronização de estado desejado (consistência eventual)
   - Jobs: Operações de longa duração, atualizações de firmware (minutos a horas)
   - Exemplos de caso de uso para cada recurso

3. **Estrutura de Tópico MQTT** - Exibido ao mostrar integração mqtt_client_explorer
   - Documentação completa de padrão de tópico
   - Explicações de tópico de solicitação/resposta
   - Exemplos de assinatura curinga
   - Descrições de componentes de tópico

4. **Ciclo de Vida de Execução de Comando** - Exibido após ver status de comando
   - Fluxo de transição de status (CREATED → IN_PROGRESS → SUCCEEDED/FAILED)
   - Tratamento de timeout
   - Comportamento de cancelamento
   - Melhores práticas para monitoramento

5. **Melhores Práticas** - Exibido após ver histórico de comandos
   - Convenções de nomenclatura de comando
   - Orientação de configuração de timeout
   - Estratégias de tratamento de erros
   - Recomendações de monitoramento e alerta

6. **Integração de Console** - Exibido com lembrete de Console Checkpoint
   - Navegação AWS IoT Console
   - Verificação de modelo de comando
   - Visualização de linha do tempo de execução
   - Comparação CLI vs Console

**Tratamento de Erros**:

O script implementa tratamento abrangente de erros com mensagens amigáveis ao usuário:

**Erros de Validação**:
- Validação de nome de comando (comprimento, caracteres, formato)
- Validação de descrição (comprimento, conteúdo)
- Validação de formato de payload (esquema JSON, complexidade)
- Validação de alvo (existência de dispositivo/grupo)
- Validação de parâmetro (tipo, campos obrigatórios)
- Mensagens de erro claras com orientação de correção

**Erros de API AWS**:
- ResourceNotFoundException: Comando ou alvo não encontrado
- InvalidRequestException: Payload ou parâmetros inválidos
- ThrottlingException: Limite de taxa excedido com orientação de repetição
- UnauthorizedException: Permissões insuficientes
- Backoff exponencial para limitação de taxa
- Repetição automática para erros transitórios (até 3 tentativas)
- Mensagens de erro detalhadas com sugestões de solução de problemas

**Erros de Rede**:
- Detecção de problema de conectividade
- Orientação de verificação de credenciais AWS
- Verificações de configuração de região
- Opções de repetição com prompts de usuário

**Erros de Estado**:
- Cancelamento de comandos concluídos
- Exclusão de modelos em uso
- Transições de status inválidas
- Explicações claras de estado atual

**Modo de Depuração**:
- Mostra todas as chamadas de API do AWS SDK (boto3) com parâmetros
- Exibe respostas completas de API em formato JSON
- Fornece informações detalhadas de erro com rastreamentos de pilha completos
- Ajuda com solução de problemas e aprendizado de APIs AWS
- Alternar ligado/desligado durante execução de script

**Características de Desempenho**:
- **Integração Nativa boto3**: Chamadas diretas de AWS SDK para melhor desempenho
- **Limitação de Taxa**: Respeita limites de AWS IoT Commands API
- **Paginação Eficiente**: Trata listas grandes de comandos e histórico
- **Gerenciamento de Memória**: Análise JSON eficiente e limpeza de recursos
- **Recuperação de Erros**: Repetição automática com backoff exponencial

**Foco Educacional**:
- Ciclo de vida completo de comando desde criação de modelo até execução
- Entrega e reconhecimento de comando em tempo real
- Simulação de dispositivo usando scripts IoT Core
- Estrutura de tópico MQTT e fluxo de mensagens
- Orientação de decisão Commands vs Shadow vs Jobs
- Melhores práticas para implantações de produção

**Guia de Solução de Problemas**:

**Problemas Comuns e Soluções**:

1. **Dispositivo Não Recebe Comandos**
   - Verificar se dispositivo está assinado no tópico de solicitação de comando
   - Verificar status de conexão MQTT
   - Confirmar permissões de certificado e política
   - Verificar se nome da coisa corresponde ao alvo
   - Garantir que simulador de dispositivo esteja em execução ANTES de executar comandos

2. **Erros de Validação de Modelo**
   - Verificar sintaxe de esquema JSON
   - Verificar complexidade de formato de payload (máx 10KB)
   - Garantir que campos obrigatórios estejam definidos
   - Validar tipos e restrições de parâmetros

3. **Falhas de Execução de Comando**
   - Verificar se dispositivo/grupo alvo existe
   - Verificar permissões IAM para AWS IoT Commands
   - Confirmar configuração de região AWS
   - Revisar configurações de timeout de comando

4. **Status Não Atualiza**:
   - Verificar se dispositivo publicou resposta para tópico correto
   - Verificar formato de payload de resposta
   - Confirmar se ID de execução corresponde
   - Revisar logs de dispositivo para erros

5. **Falhas de Cancelamento**:
   - Verificar se comando já não está concluído
   - Verificar status de execução de comando
   - Confirmar permissões IAM para cancelamento
   - Revisar estado atual do comando

**Fluxo de Trabalho de Integração** (Ordem Correta):

⚠️ **CRÍTICO**: O simulador de dispositivo DEVE estar em execução e assinado nos tópicos de comando ANTES de executar comandos. Comandos são efêmeros por padrão - se nenhum dispositivo estiver ouvindo quando o comando for publicado, ele será perdido.

1. **Abrir Terminal 2 PRIMEIRO** - Copiar credenciais AWS
2. Navegar para diretório de scripts IoT Core
3. Executar `certificate_manager.py` para configurar autenticação de dispositivo
4. Executar `mqtt_client_explorer.py` para assinar tópicos de comando
5. **Verificar se simulador de dispositivo está pronto** - Deve mostrar "Assinado nos tópicos de comando"
6. **Agora abrir Terminal 1** - Executar `manage_commands.py`
7. Criar modelo de comando
8. Executar comando direcionado ao dispositivo
9. **Simulador de Dispositivo** (Terminal 2) recebe comando e exibe payload
10. **Simulador de Dispositivo** publica reconhecimento para tópico de resposta
11. Retornar ao Terminal 1 para ver status de comando atualizado

**Por Que Esta Ordem Importa**: Sem sessões persistentes habilitadas, mensagens MQTT não são enfileiradas para dispositivos offline. O dispositivo deve estar ativamente assinado no tópico de comando quando AWS IoT publica o comando, caso contrário o comando não será entregue.

**Casos de Uso**:

**Comandos de Emergência em Toda a Frota**:
- Enviar comandos de parada de emergência para todos os veículos em uma região
- Executar recalls de segurança em toda a frota
- Coordenar respostas a ameaças de segurança
- Atualizações de configuração em tempo real em toda a frota

**Diagnóstico e Controle Remoto**:
- Trancar/destrancar veículos remotamente para suporte ao cliente
- Ajustar configurações de clima antes da chegada do cliente
- Ativar buzina para assistência de localização de veículo
- Coletar dados de diagnóstico sob demanda

**Padrões de Implantação de Produção**:
- Versionamento e gerenciamento de modelo de comando
- Execução de comando multi-região
- Monitoramento e alerta de execução de comando
- Integração com sistemas de gerenciamento de frota
- Registro de conformidade e auditoria

**Guia de Decisão Commands vs Device Shadow vs Jobs**:

Use **Commands** quando:
- Ação imediata necessária (tempo de resposta em segundos)
- Controle de dispositivo em tempo real necessário
- Reconhecimento rápido esperado
- Dispositivo deve estar online
- Exemplos: trancar/destrancar, ativação de buzina, parada de emergência

Use **Device Shadow** quando:
- Sincronização de estado desejado necessária
- Suporte a dispositivo offline necessário
- Consistência eventual aceitável
- Persistência de estado importante
- Exemplos: configurações de temperatura, configuração, estado desejado

Use **Jobs** quando:
- Operações de longa duração necessárias (minutos a horas)
- Atualizações de firmware necessárias
- Gerenciamento de dispositivo em lote
- Rastreamento de progresso importante
- Exemplos: atualizações de firmware, rotação de certificado, configuração em massa

**Integração de Serviços AWS**:
- **AWS IoT Core**: Armazenamento e execução de modelo de comando
- **AWS IoT Device Management**: Gerenciamento de frota e direcionamento
- **AWS Identity and Access Management (IAM)**: Permissões e políticas
- **Amazon CloudWatch**: Monitoramento e registro (opcional)

**Considerações de Segurança**:
- Permissões IAM para operações de comando
- Autenticação de dispositivo baseada em certificado
- Autorização baseada em política para tópicos MQTT
- Criptografia de payload de comando em trânsito
- Registro de auditoria para conformidade

**Otimização de Custos**:
- Comandos são cobrados por execução
- Sem custos de armazenamento para modelos de comando
- Direcionamento eficiente reduz execuções desnecessárias
- Monitorar histórico de comandos para padrões de uso
- Considerar operações em lote para eficiência de custos
