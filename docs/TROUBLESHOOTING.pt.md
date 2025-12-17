# Guia de Solução de Problemas

Este guia cobre problemas de configuração do ambiente. Para problemas específicos de scripts, habilite o modo de depuração ao executar scripts - eles fornecem mensagens de erro contextuais e orientação.

## Configuração do Ambiente

### Configuração de Credenciais da AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Solução**:
```bash
# Configurar credenciais da AWS
aws configure
# Digite: Access Key ID, Secret Access Key, Região, Formato de saída

# Verificar configuração
aws sts get-caller-identity
```

**Métodos alternativos**:
- Variáveis de ambiente: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Arquivo de credenciais da AWS: `~/.aws/credentials`
- Funções IAM (para execução em EC2/Lambda)

---

### Configuração de Região

#### Problema: "Region not configured" ou "You must specify a region"

**Solução**:
```bash
# Definir região no AWS CLI
aws configure set region us-east-1

# Ou usar variável de ambiente
export AWS_DEFAULT_REGION=us-east-1

# Verificar região
aws configure get region
```

**Regiões suportadas**: Qualquer região da AWS com disponibilidade do serviço IoT Core

---

### Dependências do Python

#### Problema: "No module named 'colorama'" ou erros de importação similares
```
ModuleNotFoundError: No module named 'colorama'
```

**Solução**:
```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar individualmente
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Verificar instalação**:
```bash
python -c "import boto3, colorama, requests; print('Todas as dependências instaladas')"
```

---

### Permissões IAM

#### Problema: "Access Denied" ou erros "User is not authorized"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Solução**: Certifique-se de que seu usuário/função IAM da AWS tenha as permissões necessárias:

**Ações IAM Necessárias**:
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
                "s3:PutBucketTagging",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:TagRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**Nota**: Para ambientes de produção, siga o princípio do menor privilégio e restrinja os recursos adequadamente.

---

## Obtendo Ajuda

### Problemas Específicos de Scripts

Se você encontrar problemas ao executar scripts:

1. **Habilite o modo de depuração** - Mostra chamadas e respostas detalhadas da API
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Leia as mensagens de erro** - Os scripts fornecem orientação contextual

3. **Verifique as pausas educacionais** - Elas explicam conceitos e requisitos

4. **Verifique os pré-requisitos** - A maioria dos scripts requer executar `provision_script.py` primeiro

### Fluxo de Trabalho Comum

```bash
# 1. Configurar ambiente (uma vez)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Criar infraestrutura (executar primeiro)
python scripts/provision_script.py

# 3. Executar outros scripts conforme necessário
python scripts/manage_packages.py
python scripts/create_job.py
# etc.

# 4. Limpar quando terminar
python scripts/cleanup_script.py
```

### Recursos Adicionais

- **README.md** - Visão geral do projeto e início rápido
- **Mensagens i18n de scripts** - Orientação localizada em seu idioma
- **Pausas educacionais** - Aprendizado contextual durante a execução de scripts
- **Documentação do AWS IoT** - https://docs.aws.amazon.com/pt_br/iot/
