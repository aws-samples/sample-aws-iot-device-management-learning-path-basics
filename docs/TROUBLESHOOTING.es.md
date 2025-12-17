# Guía de Solución de Problemas

Esta guía cubre problemas de configuración del entorno. Para problemas específicos de scripts, habilite el modo de depuración al ejecutar scripts - proporcionan mensajes de error contextuales y orientación.

## Configuración del Entorno

### Configuración de Credenciales de AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Solución**:
```bash
# Configurar credenciales de AWS
aws configure
# Ingrese: Access Key ID, Secret Access Key, Región, Formato de salida

# Verificar configuración
aws sts get-caller-identity
```

**Métodos alternativos**:
- Variables de entorno: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Archivo de credenciales de AWS: `~/.aws/credentials`
- Roles IAM (para ejecución en EC2/Lambda)

---

### Configuración de Región

#### Problema: "Region not configured" o "You must specify a region"

**Solución**:
```bash
# Establecer región en AWS CLI
aws configure set region us-east-1

# O usar variable de entorno
export AWS_DEFAULT_REGION=us-east-1

# Verificar región
aws configure get region
```

**Regiones soportadas**: Cualquier región de AWS con disponibilidad del servicio IoT Core

---

### Dependencias de Python

#### Problema: "No module named 'colorama'" o errores de importación similares
```
ModuleNotFoundError: No module named 'colorama'
```

**Solución**:
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O instalar individualmente
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Verificar instalación**:
```bash
python -c "import boto3, colorama, requests; print('Todas las dependencias instaladas')"
```

---

### Permisos IAM

#### Problema: "Access Denied" o errores "User is not authorized"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Solución**: Asegúrese de que su usuario/rol IAM de AWS tenga los permisos requeridos:

**Acciones IAM Requeridas**:
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

**Nota**: Para entornos de producción, siga el principio de privilegio mínimo y restrinja los recursos apropiadamente.

---

## Obtener Ayuda

### Problemas Específicos de Scripts

Si encuentra problemas al ejecutar scripts:

1. **Habilite el modo de depuración** - Muestra llamadas y respuestas detalladas de API
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Lea los mensajes de error** - Los scripts proporcionan orientación contextual

3. **Revise las pausas educativas** - Explican conceptos y requisitos

4. **Verifique los prerequisitos** - La mayoría de los scripts requieren ejecutar `provision_script.py` primero

### Flujo de Trabajo Común

```bash
# 1. Configurar entorno (una vez)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Crear infraestructura (ejecutar primero)
python scripts/provision_script.py

# 3. Ejecutar otros scripts según sea necesario
python scripts/manage_packages.py
python scripts/create_job.py
# etc.

# 4. Limpiar cuando termine
python scripts/cleanup_script.py
```

### Recursos Adicionales

- **README.md** - Descripción general del proyecto e inicio rápido
- **Mensajes i18n de scripts** - Orientación localizada en su idioma
- **Pausas educativas** - Aprendizaje contextual durante la ejecución de scripts
- **Documentación de AWS IoT** - https://docs.aws.amazon.com/es_es/iot/
