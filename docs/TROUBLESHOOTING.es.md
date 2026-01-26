# Guía de Solución de Problemas

Esta guía te ayuda a resolver problemas de configuración del entorno. Si encuentras problemas específicos con los scripts, prueba habilitar el modo de depuración al ejecutarlos - te dará mensajes de error útiles y orientación en el camino.

## Configuración del Entorno

### Configuración de Credenciales de AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Aquí te mostramos cómo solucionarlo**:
```bash
# Configurar credenciales de AWS
aws configure
# Ingresa: Access Key ID, Secret Access Key, Región, Formato de salida

# Verificar configuración
aws sts get-caller-identity
```

**También puedes probar estos métodos alternativos**:
- Variables de entorno: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Archivo de credenciales de AWS: `~/.aws/credentials`
- Roles IAM (si estás ejecutando en EC2 o Lambda)

---

### Configuración de Región

#### Problema: "Region not configured" o "You must specify a region"

**Aquí te mostramos cómo solucionarlo**:
```bash
# Establecer región en AWS CLI
aws configure set region us-east-1

# O usar variable de entorno
export AWS_DEFAULT_REGION=us-east-1

# Verificar región
aws configure get region
```

**Funciona con estas regiones**: Cualquier región de AWS donde IoT Core esté disponible

---

### Dependencias de Python

#### Problema: "No module named 'colorama'" o errores de importación similares
```
ModuleNotFoundError: No module named 'colorama'
```

**Aquí te mostramos cómo solucionarlo**:
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O instalar individualmente
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**Puedes verificar tu instalación así**:
```bash
python -c "import boto3, colorama, requests; print('Todas las dependencias instaladas')"
```

---

### Permisos IAM

#### Problema: "Access Denied" o errores "User is not authorized"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Aquí te mostramos cómo solucionarlo**: Asegúrate de que tu usuario o rol IAM de AWS tenga los permisos necesarios:

**Lo que necesitarás - Acciones IAM**:
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

**Nota rápida**: Para entornos de producción, es buena idea seguir el principio de privilegio mínimo y restringir los recursos según sea necesario.

---

## Obtener Ayuda

### Problemas Específicos de Scripts

Si encuentras problemas al ejecutar scripts, aquí hay algunos consejos útiles:

1. **Habilita el modo de depuración** - Te mostrará llamadas y respuestas detalladas de API
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **Lee los mensajes de error** - Los scripts proporcionan orientación contextual útil

3. **Revisa las pausas educativas** - Explican conceptos y requisitos a medida que avanzas

4. **Verifica los prerequisitos** - La mayoría de los scripts necesitan que ejecutes `provision_script.py` primero

### Aquí hay un flujo de trabajo típico

```bash
# 1. Configurar entorno (solo una vez)
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. Crear infraestructura (ejecuta esto primero)
python scripts/provision_script.py

# 3. Ejecutar otros scripts según los necesites
python scripts/manage_packages.py
python scripts/create_job.py
# etc.

# 4. Limpiar cuando termines
python scripts/cleanup_script.py
```

### Más recursos útiles

- **README.md** - Descripción general del proyecto y guía de inicio rápido
- **Mensajes i18n de scripts** - Orientación útil en tu idioma
- **Pausas educativas** - Aprende mientras avanzas durante la ejecución de scripts
- **Documentación de AWS IoT** - https://docs.aws.amazon.com/es_es/iot/
