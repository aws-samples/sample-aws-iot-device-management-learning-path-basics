# AWS IoT Device Management - Caminho de Aprendizado - Básico

## 🌍 Available Languages | Idiomas Disponibles | 利用可能な言語 | 사용 가능한 언어 | Idiomas Disponíveis | 可用语言

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |

---

Uma demonstração abrangente das capacidades do AWS IoT Device Management incluindo provisionamento de dispositivos, atualizações over-the-air (OTA), gerenciamento de jobs e operações de frota usando scripts Python modernos com integração nativa do AWS SDK (boto3).

## 👥 Público-Alvo

**Público Principal:** Desenvolvedores IoT, arquitetos de soluções, engenheiros DevOps trabalhando com frotas de dispositivos AWS IoT

**Pré-requisitos:** Conhecimento intermediário de AWS, fundamentos do AWS IoT Core, fundamentos de Python, uso de linha de comando

**Nível de Aprendizado:** Nível associado com abordagem prática para gerenciamento de dispositivos em escala

## 🎯 Objetivos de Aprendizado

- **Gerenciamento do Ciclo de Vida do Dispositivo**: Provisionar dispositivos IoT com tipos de thing e atributos apropriados
- **Organização de Frota**: Criar grupos de things estáticos e dinâmicos para gerenciamento de dispositivos
- **Atualizações OTA**: Implementar atualizações de firmware usando AWS IoT Jobs com integração do Amazon S3
- **Gerenciamento de Pacotes**: Lidar com múltiplas versões de firmware com atualizações automáticas de shadow
- **Execução de Jobs**: Simular comportamento realista de dispositivos durante atualizações de firmware
- **Controle de Versão**: Reverter dispositivos para versões anteriores de firmware
- **Comandos Remotos**: Enviar comandos em tempo real para dispositivos usando AWS IoT Commands
- **Limpeza de Recursos**: Gerenciar adequadamente recursos AWS para evitar custos desnecessários

## 📋 Pré-requisitos

- **Conta AWS** com permissões para AWS IoT, Amazon S3 e AWS Identity and Access Management (IAM)
- **Credenciais AWS** configuradas (via `aws configure`, variáveis de ambiente ou roles IAM)
- **Python 3.10+** com pip e bibliotecas Python boto3, colorama e requests (verifique o arquivo requirements.txt)
- **Git** para clonar o repositório

## 💰 Análise de Custos

**Este projeto cria recursos AWS reais que incorrerão em cobranças.**

| Serviço | Uso | Custo Estimado (USD) |
|---------|-----|---------------------|
| **AWS IoT Core** | ~1.000 mensagens, 100-10.000 dispositivos | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2.000 operações de shadow | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 execuções de job | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50 execuções de comando | $0.01 - $0.05 |
| **Amazon S3** | Armazenamento + requisições para firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Consultas e indexação de dispositivos | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Operações de pacote | $0.01 - $0.05 |
| **AWS Identity and Access Management (IAM)** | Gerenciamento de roles/políticas | $0.00 |
| **Total Estimado** | **Sessão de demonstração completa** | **$0.28 - $2.45** |

**Fatores de Custo:**
- Quantidade de dispositivos (100-10.000 configurável)
- Frequência de execução de jobs
- Operações de atualização de shadow
- Duração de armazenamento no Amazon S3

**Gerenciamento de Custos:**
- ✅ Script de limpeza remove todos os recursos
- ✅ Recursos de demonstração de curta duração
- ✅ Escala configurável (comece pequeno)
- ⚠️ **Execute o script de limpeza quando terminar**

**📊 Monitore custos:** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

## 🚀 Início Rápido

```bash
# 1. Clonar e configurar
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar AWS
aws configure

# 3. Fluxo de trabalho completo (sequência recomendada)
python scripts/provision_script.py        # Criar infraestrutura
python scripts/manage_dynamic_groups.py   # Criar grupos de dispositivos
python scripts/manage_packages.py         # Gerenciar pacotes de firmware
python scripts/create_job.py              # Implantar atualizações de firmware
python scripts/simulate_job_execution.py  # Simular atualizações de dispositivos
python scripts/explore_jobs.py            # Monitorar progresso dos jobs
python scripts/manage_commands.py         # Enviar comandos em tempo real para dispositivos
python scripts/cleanup_script.py          # Limpar recursos
```

## 📚 Scripts Disponíveis

| Script | Propósito | Recursos Principais | Documentação |
|--------|-----------|-------------------|--------------|
| **provision_script.py** | Configuração completa da infraestrutura | Cria dispositivos, grupos, pacotes, armazenamento Amazon S3 | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | Gerenciar grupos dinâmicos de dispositivos | Criar, listar, excluir com validação Fleet Indexing | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | Gerenciamento abrangente de pacotes | Criar pacotes/versões, integração Amazon S3, rastreamento de dispositivos com status de reversão individual | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | Criar jobs de atualização OTA | Direcionamento multi-grupo, URLs pré-assinadas | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | Simular atualizações de dispositivos | Downloads reais do Amazon S3, preparação de plano visível, rastreamento de progresso por dispositivo | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | Monitorar e gerenciar jobs | Exploração interativa de jobs, cancelamento, exclusão e análise | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **manage_commands.py** | Enviar comandos em tempo real para dispositivos | Gerenciamento de templates, execução de comandos, monitoramento de status, rastreamento de histórico | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptsmanage_commandspy) |
| **cleanup_script.py** | Remover recursos AWS | Limpeza seletiva, gerenciamento de custos | [📖 Detalhes](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **Documentação Detalhada**: Veja [docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md) para informações abrangentes sobre os scripts.

## ⚙️ Configuração

**Variáveis de Ambiente** (opcional):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=pt                    # Definir idioma padrão (en, es, pt, etc.)
```

**Recursos dos Scripts**:
- **AWS SDK Nativo**: Usa boto3 para melhor desempenho e confiabilidade
- **Suporte Multi-idioma**: Seleção interativa de idioma com fallback para inglês
- **Modo Debug**: Mostra todas as chamadas e respostas da API AWS
- **Processamento Paralelo**: Operações concorrentes quando não está no modo debug
- **Limitação de Taxa**: Conformidade automática com throttling da API AWS
- **Rastreamento de Progresso**: Status de operação em tempo real

## 🌍 Suporte à Internacionalização

Todos os scripts suportam múltiplos idiomas com detecção automática de idioma e seleção interativa.

**Seleção de Idioma**:
- **Interativa**: Scripts solicitam seleção de idioma na primeira execução
- **Variável de Ambiente**: Defina `AWS_IOT_LANG=pt` para pular a seleção de idioma
- **Fallback**: Automaticamente volta para inglês para traduções ausentes

**Idiomas Suportados**:
- **English (en)**: Traduções completas ✅
- **Spanish (es)**: Pronto para traduções
- **Japanese (ja)**: Pronto para traduções
- **Chinese (zh-CN)**: Pronto para traduções
- **Portuguese (pt-BR)**: Pronto para traduções
- **Korean (ko)**: Pronto para traduções

**Exemplos de Uso**:
```bash
# Definir idioma via variável de ambiente (recomendado para automação)
export AWS_IOT_LANG=pt
python scripts/provision_script.py

# Códigos de idioma alternativos suportados
export AWS_IOT_LANG=spanish    # ou "es", "español"
export AWS_IOT_LANG=japanese   # ou "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # ou "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # ou "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # ou "ko", "한국어", "kr"

# Seleção interativa de idioma (comportamento padrão)
python scripts/manage_packages.py
# Saída: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# Todo texto voltado ao usuário aparecerá no idioma selecionado
```

**Categorias de Mensagens**:
- **Elementos de UI**: Títulos, cabeçalhos, separadores
- **Prompts do Usuário**: Solicitações de entrada, confirmações
- **Mensagens de Status**: Atualizações de progresso, notificações de sucesso/falha
- **Mensagens de Erro**: Descrições detalhadas de erro e solução de problemas
- **Saída de Debug**: Informações de chamadas de API e respostas
- **Conteúdo de Aprendizado**: Momentos educacionais e explicações

## 📖 Exemplos de Uso

**Fluxo de Trabalho Completo** (sequência recomendada):
```bash
python scripts/provision_script.py        # 1. Criar infraestrutura
python scripts/manage_dynamic_groups.py   # 2. Criar grupos de dispositivos
python scripts/manage_packages.py         # 3. Gerenciar pacotes de firmware
python scripts/create_job.py              # 4. Implantar atualizações de firmware
python scripts/simulate_job_execution.py  # 5. Simular atualizações de dispositivos
python scripts/explore_jobs.py            # 6. Monitorar progresso dos jobs
python scripts/manage_commands.py         # 7. Enviar comandos em tempo real para dispositivos
python scripts/cleanup_script.py          # 8. Limpar recursos
```

**Operações Individuais**:
```bash
python scripts/manage_packages.py         # Gerenciamento de pacotes e versões
python scripts/manage_dynamic_groups.py   # Operações de grupos dinâmicos
```

> 📖 **Mais Exemplos**: Veja [docs/EXAMPLES.md](docs/EXAMPLES.md) para cenários de uso detalhados.

## 🛠️ Solução de Problemas

**Problemas Comuns**:
- **Credenciais**: Configure credenciais AWS via `aws configure`, variáveis de ambiente ou roles IAM
- **Permissões**: Certifique-se de que o usuário IAM tem permissões para AWS IoT, Amazon S3 e IAM
- **Limites de Taxa**: Scripts lidam automaticamente com throttling inteligente
- **Rede**: Certifique-se da conectividade com APIs AWS

**Modo Debug**: Habilite em qualquer script para solução detalhada de problemas
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **Solução Detalhada de Problemas**: Veja [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para soluções abrangentes.

## 🧹 Importante: Limpeza de Recursos

**Sempre execute a limpeza quando terminar para evitar cobranças contínuas:**
```bash
python scripts/cleanup_script.py
# Escolha opção 1: TODOS os recursos
# Digite: DELETE
```

**O que a limpeza remove:**
- Todos os dispositivos e grupos AWS IoT
- Buckets Amazon S3 e arquivos de firmware
- Pacotes de software AWS IoT
- Templates de comandos AWS IoT
- Roles e políticas IAM
- Configuração Fleet Indexing

## 🔧 Guia do Desenvolvedor: Adicionando Novos Idiomas

**Estrutura de Arquivos de Mensagem**:
```
i18n/
├── common.json                    # Mensagens compartilhadas entre todos os scripts
├── loader.py                      # Utilitário de carregamento de mensagens
├── language_selector.py           # Interface de seleção de idioma
└── {language_code}/               # Diretório específico do idioma
    ├── provision_script.json     # Mensagens específicas do script
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**Adicionando um Novo Idioma**:

1. **Criar Diretório do Idioma**:
   ```bash
   mkdir i18n/{language_code}  # ex., i18n/pt para Português
   ```

2. **Copiar Templates em Inglês**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Traduzir Arquivos de Mensagem**:
   Cada arquivo JSON contém mensagens categorizadas:
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Enable debug mode? [y/N]: ",
       "operation_choice": "Enter choice [1-11]: ",
       "continue_operation": "Continue? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Debug mode enabled",
       "package_created": "✅ Package created successfully",
       "clients_initialized": "🔍 DEBUG: Client configuration:"
     },
     "errors": {
       "invalid_choice": "❌ Invalid choice. Please enter 1-11",
       "package_not_found": "❌ Package '{}' not found",
       "api_error": "❌ Error in {} {}: {}"
     },
     "debug": {
       "api_call": "📤 API Call: {}",
       "api_response": "📤 API Response:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Select Operation:",
       "create_package": "1. Create Software Package",
       "goodbye": "👋 Thank you for using Package Manager!"
     },
     "learning": {
       "package_management_title": "Software Package Management",
       "package_management_description": "Educational content..."
     }
   }
   ```

4. **Atualizar Seletor de Idioma** (se adicionando novo idioma):
   Adicione seu idioma ao `i18n/language_selector.py`:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Seu Nome do Idioma",  # Adicionar nova opção
           # ... idiomas existentes
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "seu_codigo",  # Adicionar novo código de idioma
       # ... mapeamentos existentes
   }
   ```

5. **Testar Tradução**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Diretrizes de Tradução**:
- **Preservar Formatação**: Manter emojis, cores e caracteres especiais
- **Manter Placeholders**: Manter placeholders `{}` para conteúdo dinâmico
- **Termos Técnicos**: Manter nomes de serviços AWS em inglês
- **Adaptação Cultural**: Adaptar exemplos e referências adequadamente
- **Consistência**: Usar terminologia consistente em todos os arquivos

**Padrões de Chaves de Mensagem**:
- `title`: Título principal do script
- `separator`: Separadores visuais e divisores
- `prompts.*`: Solicitações de entrada do usuário e confirmações
- `status.*`: Atualizações de progresso e resultados de operação
- `errors.*`: Mensagens de erro e avisos
- `debug.*`: Saída de debug e informações de API
- `ui.*`: Elementos de interface do usuário (menus, rótulos, botões)
- `results.*`: Resultados de operação e exibição de dados
- `learning.*`: Conteúdo educacional e explicações
- `warnings.*`: Mensagens de aviso e avisos importantes
- `explanations.*`: Contexto adicional e texto de ajuda

**Testando Sua Tradução**:
```bash
# Testar script específico com seu idioma
export AWS_IOT_LANG=seu_codigo_de_idioma
python scripts/manage_packages.py

# Testar comportamento de fallback (usar idioma inexistente)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Deve voltar para inglês
```

## 📚 Documentação

- **[Scripts Detalhados](docs/DETAILED_SCRIPTS.md)** - Documentação abrangente dos scripts
- **[Exemplos de Uso](docs/EXAMPLES.md)** - Cenários práticos e fluxos de trabalho
- **[Solução de Problemas](docs/TROUBLESHOOTING.md)** - Problemas comuns e soluções

## 📄 Licença

MIT No Attribution License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏷️ Tags

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot`