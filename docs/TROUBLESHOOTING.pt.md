# Guia de Solução de Problemas

Este guia vai te ajudar com problemas de configuração do ambiente. Se você encontrar problemas específicos nos scripts, pode habilitar o modo de depuração ao executá-los - eles vão te dar mensagens de erro bem detalhadas e orientação sobre o que fazer.

## Configuração do Ambiente

### Configuração de Credenciais da AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Como resolver**:
```bash
# Vamos configurar suas credenciais da AWS
aws configure
# Você vai precisar digitar: Access Key ID, Secret Access Key, Região, Formato de saída

# Depois, você pode verificar se está tudo certo
aws sts get-caller-identity
```

**Outras formas de configurar**:
- Usando variáveis de ambiente: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Através do arquivo de credenciais da AWS: `~/.aws/credentials`
- Com funções IAM (se você estiver rodando em EC2/Lambda)

---

### Configuração de Região

#### Problema: "Region not configured" ou "You must specify a region"

**Como resolver**:
```bash
# Você pode definir a região no AWS CLI assim
aws configure set region us-east-1

# Ou usar uma variável de ambiente
export AWS_DEFAULT_REGION=us-east-1

# Para verificar qual região está configurada
aws configure get region
```

**Regiões suportadas**: Você pode usar qualquer região da AWS que tenha o serviço AWS IoT Core disponível

---

### Dependências do Python

#### Problema: "No module named 'colorama'" ou erros de importação similares
```
ModuleNotFoundError: No module named 'colorama'
```

**Como resolver**:
```bash
# Você pode instalar todas as dependências de uma vez
pip install -r requirements.txt

# Ou instalar cada uma separadamente
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Para verificar se está tudo instalado**:
```bash
python -c "import boto3, colorama, requests; print('Todas as dependências instaladas')"
```

---

### Permissões IAM

#### Problema: "Access Denied" ou erros "User is not authorized"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Como resolver**: Você vai precisar garantir que seu usuário ou função IAM da AWS tenha as permissões necessárias. Aqui está o que você precisa:
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

**Dica importante**: Para ambientes de produção, é uma boa ideia seguir o princípio do menor privilégio e restringir os recursos de forma apropriada.

---

## Como Conseguir Ajuda

### Problemas Específicos de Scripts

Se você encontrar algum problema ao executar os scripts:

1. **Habilite o modo de depuração** - Ele vai te mostrar chamadas e respostas detalhadas da API
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Leia as mensagens de erro com atenção** - Os scripts vão te dar orientação contextual sobre o que está acontecendo

3. **Preste atenção nas pausas educacionais** - Elas explicam conceitos importantes e o que você precisa saber

4. **Verifique os pré-requisitos** - A maioria dos scripts precisa que você execute o `provision_script.py` primeiro

### Fluxo de Trabalho Comum

```bash
# 1. Configurar o ambiente (só precisa fazer uma vez)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Criar a infraestrutura (execute este primeiro)
python scripts/provision_script.py

# 3. Depois você pode executar outros scripts conforme precisar
python scripts/manage_packages.py
python scripts/create_job.py
# e assim por diante

# 4. Quando terminar, você pode limpar tudo
python scripts/cleanup_script.py
```

### Recursos Adicionais

- **README.md** - Visão geral do projeto e início rápido
- **Mensagens i18n de scripts** - Orientação localizada em seu idioma
- **Pausas educacionais** - Aprendizado contextual durante a execução de scripts
- **Documentação do AWS IoT** - https://docs.aws.amazon.com/pt_br/iot/
