# Guía de Solución de Problemas

Este documento proporciona soluciones para problemas comunes encontrados al usar los scripts de AWS IoT Device Management.

## Problemas Comunes

### Problemas de Configuración de AWS

#### Problema: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**Solución**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

#### Problema: Errores de "Access Denied"
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**Solución**: Asegúrese de que su usuario/rol de AWS IAM tenga los permisos requeridos:
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

**Solución**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

### Problemas de Ejecución de Scripts

#### Problema: "No module named 'colorama'"
```
ModuleNotFoundError: No module named 'colorama'
```

**Solución**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install colorama>=0.4.4 requests>=2.25.1
```

#### Problema: Los scripts se cuelgan o agotan el tiempo de espera
**Síntomas**: Los scripts parecen congelarse durante la ejecución

**Solución**:
1. Active el modo de depuración para ver qué está sucediendo:
   ```bash
   # When prompted, choose 'y' for debug mode
   🔧 Enable debug mode? [y/N]: y
   ```

2. Verifique los límites de servicio de AWS y el throttling
3. Reduzca los workers paralelos si es necesario
4. Verifique la conectividad de red

#### Problema: "Thing type deletion requires 5-minute wait"
```
InvalidRequestException: Thing type cannot be deleted until 5 minutes after deprecation
```

**Solución**: Este es un comportamiento esperado. El script de limpieza maneja esto automáticamente:
1. Deprecando los tipos de cosa primero
2. Esperando 5 minutos
3. Luego eliminándolos

### Problemas de Creación de Recursos

#### Problema: "Thing group already exists"
```
ResourceAlreadyExistsException: Thing group already exists
```

**Solución**: Esto generalmente es inofensivo. Los scripts verifican los recursos existentes y omiten la creación si ya existen.

#### Problema: "S3 bucket name already taken"
```
BucketAlreadyExists: The requested bucket name is not available
```

**Solución**: Los scripts usan marcas de tiempo para asegurar nombres de bucket únicos. Si esto ocurre:
1. Espere unos segundos y reintente
2. Verifique si tiene buckets existentes con nombres similares

#### Problema: "Package version already exists"
```
ConflictException: Package version already exists
```

**Solución**: Los scripts manejan esto verificando las versiones existentes primero. Si necesita actualizar:
1. Use un nuevo número de versión
2. O elimine la versión existente primero

### Problemas de Ejecución de Trabajos

#### Problema: "No active jobs found"
```
❌ No active jobs found
```

**Solución**:
1. Cree un trabajo primero usando `scripts/create_job.py`
2. Verifique el estado del trabajo: `scripts/explore_jobs.py`
3. Verifique si los trabajos fueron cancelados o completados

#### Problema: "Failed to download artifact"
```
❌ Failed to download artifact: HTTP 403 Forbidden
```

**Solución**:
1. Verifique los permisos del rol de AWS IAM para AWS IoT Jobs
2. Verifique la configuración de URL prefirmada
3. Asegúrese de que el bucket de S3 y los objetos existan
4. Verifique si las URLs prefirmadas han expirado (límite de 1 hora)

#### Problema: "Job execution not found"
```
ResourceNotFoundException: Job execution not found
```

**Solución**:
1. Verifique que el ID del trabajo y el nombre de la cosa sean correctos
2. Verifique si el dispositivo está en los grupos de cosas objetivo
3. Asegúrese de que el trabajo aún esté activo (no completado/cancelado)

### Problemas de Fleet Indexing

#### Problema: "Fleet Indexing queries return no results"
```
ℹ️ No devices currently match this query
```

**Solución**:
1. Espere a que Fleet Indexing se complete (puede tomar varios minutos)
2. Verifique que Fleet Indexing esté habilitado
3. Verifique la sintaxis de la consulta
4. Asegúrese de que los dispositivos tengan los atributos/sombras esperados

#### Problema: "Invalid Fleet Indexing query"
```
InvalidRequestException: Invalid query string
```

**Solución**: Verifique la sintaxis de la consulta. Problemas comunes:
- Use `attributes.fieldName` para atributos de dispositivo
- Use `shadow.reported.fieldName` para sombras clásicas
- Use `shadow.name.\\$package.reported.fieldName` para sombras nombradas
- Escape los caracteres especiales correctamente

### Problemas de Rendimiento

#### Problema: "Rate limiting errors"
```
ThrottlingException: Rate exceeded
```

**Solución**: Los scripts tienen limitación de velocidad incorporada, pero si encuentra esto:
1. Active el modo de depuración para ver qué API está siendo limitada
2. Reduzca los workers paralelos en el script
3. Agregue retrasos entre operaciones
4. Verifique los límites de servicio de AWS para su cuenta

#### Problema: "Scripts running slowly"
**Síntomas**: Las operaciones toman mucho más tiempo de lo esperado

**Solución**:
1. Verifique la conectividad de red
2. Verifique que la región de AWS esté geográficamente cerca
3. Active el modo de depuración para identificar cuellos de botella
4. Considere reducir los tamaños de lote

### Problemas de Consistencia de Datos

#### Problema: "Device shadows not updating"
```
❌ Failed to update device shadow
```

**Solución**:
1. Verifique la configuración del endpoint de IoT Data
2. Verifique que el dispositivo/cosa exista
3. Asegúrese del formato JSON correcto en las actualizaciones de sombra
4. Verifique los permisos de AWS IAM para operaciones de sombra

#### Problema: "Package configuration not working"
```
❌ Failed to update global package configuration
```

**Solución**:
1. Verifique que IoTPackageConfigRole exista y tenga los permisos adecuados
2. Verifique si el ARN del rol está formateado correctamente
3. Asegúrese de que la configuración de paquetes esté habilitada en su región

## Uso del Modo de Depuración

Active el modo de depuración en cualquier script para solución de problemas detallada:

```bash
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

El modo de depuración muestra:
- Todos los comandos de AWS CLI que se están ejecutando
- Parámetros de solicitud de API
- Respuestas completas de API
- Detalles de error y trazas de pila

## Análisis de Registros

### Operaciones Exitosas
Busque estos indicadores:
- ✅ Marcas de verificación verdes para operaciones exitosas
- Contadores de progreso mostrando finalización
- Mensajes de "completed successfully"

### Señales de Advertencia
Esté atento a estos patrones:
- ⚠️ Advertencias amarillas (generalmente no críticas)
- Mensajes de "already exists" (generalmente inofensivos)
- Advertencias de tiempo de espera

### Patrones de Error
Indicadores comunes de error:
- ❌ Marcas X rojas para fallos
- Mensajes de "Failed to"
- Trazas de pila de excepciones
- Códigos de error HTTP (403, 404, 500)

## Procedimientos de Recuperación

### Fallo Parcial de Aprovisionamiento
Si el aprovisionamiento falla a mitad de camino:

1. **Verifique qué se creó**:
   ```bash
   python scripts/explore_jobs.py
   # Option 1: List all jobs
   ```

2. **Limpie si es necesario**:
   ```bash
   python scripts/cleanup_script.py
   # Option 1: ALL resources
   ```

3. **Reintente el aprovisionamiento**:
   ```bash
   python scripts/provision_script.py
   # Scripts handle existing resources gracefully
   ```

### Recuperación de Trabajo Fallido
Si un trabajo falla durante la ejecución:

1. **Verifique el estado del trabajo**:
   ```bash
   python scripts/explore_jobs.py
   # Option 2: Explore specific job
   ```

2. **Verifique fallos individuales**:
   ```bash
   python scripts/explore_jobs.py
   # Option 3: Explore job execution
   ```

3. **Revierta si es necesario**:
   ```bash
   python scripts/manage_packages.py
   # Select: 10. Revert Device Versions
   # Enter thing type and previous version
   ```

### Problemas de Limpieza de Recursos
Si la limpieza falla:

1. **Intente limpieza selectiva**:
   ```bash
   python scripts/cleanup_script.py
   # Option 2: Things only (then try groups)
   ```

2. **Limpieza manual a través de la Consola de AWS**:
   - AWS IoT Core → Manage → Things
   - AWS IoT Core → Manage → Thing groups
   - AWS IoT Core → Manage → Thing types
   - Amazon S3 → Buckets
   - AWS IAM → Roles

## Problemas Específicos del Entorno

### Problemas de macOS
- **Advertencias SSL**: Los scripts suprimen las advertencias SSL de urllib3 automáticamente
- **Versión de Python**: Asegúrese de que Python 3.7+ esté instalado

### Problemas de Windows
- **Separadores de ruta**: Los scripts manejan rutas multiplataforma automáticamente
- **PowerShell**: Use Command Prompt o PowerShell con la política de ejecución adecuada

### Problemas de Linux
- **Permisos**: Asegúrese de que los scripts tengan permisos de ejecución
- **Ruta de Python**: Puede necesitar usar `python3` en lugar de `python`

## Límites de Servicio de AWS

### Límites Predeterminados (por región)
- **Things**: 500,000 por cuenta
- **Thing Types**: 100 por cuenta
- **Thing Groups**: 500 por cuenta
- **Jobs**: 100 trabajos concurrentes
- **Límites de Velocidad de API**: 
  - Operaciones de Thing: 100 TPS (los scripts usan 80 TPS)
  - Grupos dinámicos: 5 TPS (los scripts usan 4 TPS)
  - Ejecuciones de Job: 200 TPS (los scripts usan 150 TPS)
  - Operaciones de Package: 10 TPS (los scripts usan 8 TPS)

### Solicitar Aumentos de Límite
Si necesita límites más altos:
1. Vaya al Centro de Soporte de AWS
2. Cree un caso para "Service limit increase"
3. Especifique los límites de AWS IoT Core necesarios

## Obtener Ayuda

### Habilitar Registro Detallado
La mayoría de los scripts soportan modo detallado:
```bash
🔧 Enable verbose mode? [y/N]: y
```

### Verificar el Estado del Servicio de AWS
- [Panel de Estado del Servicio de AWS](https://status.aws.amazon.com/)
- Verifique su región específica para problemas de AWS IoT Core

### Recursos de la Comunidad
- Foros de Desarrolladores de AWS IoT
- Documentación de AWS
- GitHub Issues (para problemas específicos de scripts)

### Soporte Profesional
- Soporte de AWS (si tiene un plan de soporte)
- Servicios Profesionales de AWS
- Consultores de la Red de Socios de AWS

## Consejos de Prevención

### Antes de Ejecutar Scripts
1. **Verifique la configuración de AWS**: `aws sts get-caller-identity`
2. **Verifique los permisos**: Pruebe con una operación pequeña primero
3. **Revise los límites de recursos**: Asegúrese de no alcanzar los límites de cuenta
4. **Respalde datos importantes**: Si modifica recursos existentes

### Durante la Ejecución
1. **Monitoree el progreso**: Esté atento a patrones de error
2. **No interrumpa**: Deje que los scripts se completen o use Ctrl+C con cuidado
3. **Verifique la Consola de AWS**: Verifique que los recursos se estén creando como se espera

### Después de la Ejecución
1. **Verifique los resultados**: Use scripts de exploración para verificar los resultados
2. **Limpie recursos de prueba**: Use el script de limpieza para recursos temporales
3. **Monitoree los costos**: Verifique la facturación de AWS para cargos inesperados

## Problemas de Internacionalización

### Problema: Los scripts muestran claves de mensaje sin procesar en lugar de texto traducido
**Síntomas**: Los scripts muestran texto como `warnings.debug_warning` y `prompts.debug_mode` en lugar de mensajes reales

**Ejemplo**:
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

**Causa Raíz**: Este problema ocurre cuando:
1. Desajuste de código de idioma entre el selector de idioma y la estructura de directorios
2. Falta manejo de claves anidadas en la función `get_message()`
3. Carga incorrecta de archivos de mensajes

**Solución**:

1. **Verifique el Mapeo de Códigos de Idioma**: Asegúrese de que los códigos de idioma coincidan con la estructura de directorios:
   ```
   i18n/
   ├── en/     # English
   ├── es/     # Spanish  
   ├── ja/     # Japanese
   ├── ko/     # Korean
   ├── pt/     # Portuguese
   ├── zh/     # Chinese
   ```

2. **Verifique la Implementación de get_message()**: Los scripts deben manejar claves anidadas con notación de punto:
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

3. **Pruebe la Carga de Idioma**:
   ```bash
   # Test with environment variable
   export AWS_IOT_LANG=en
   python scripts/cleanup_script.py
   
   # Test different languages
   export AWS_IOT_LANG=es  # Spanish
   export AWS_IOT_LANG=ja  # Japanese
   export AWS_IOT_LANG=zh  # Chinese
   ```

4. **Verifique que Existan los Archivos de Mensajes**:
   ```bash
   # Check if translation files exist
   ls i18n/en/cleanup_script.json
   ls i18n/es/cleanup_script.json
   # etc.
   ```

**Prevención**: Al agregar nuevos scripts o idiomas:
- Use la implementación correcta de `get_message()` de scripts que funcionan
- Asegúrese de que los códigos de idioma coincidan exactamente con los nombres de directorio
- Pruebe con múltiples idiomas antes del despliegue
- Use los scripts de validación en `docs/templates/validation_scripts/`

### Problema: La selección de idioma no funciona con variables de entorno
**Síntomas**: Los scripts siempre solicitan selección de idioma a pesar de configurar `AWS_IOT_LANG`

**Solución**:
1. **Verifique el Formato de la Variable de Entorno**:
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

2. **Verifique que la Variable de Entorno Esté Configurada**:
   ```bash
   echo $AWS_IOT_LANG
   ```

3. **Pruebe la Selección de Idioma**:
   ```bash
   python3 -c "
   import sys, os
   sys.path.append('i18n')
   from language_selector import get_language
   print('Selected language:', get_language())
   "
   ```

### Problema: Faltan traducciones para nuevos idiomas
**Síntomas**: Los scripts vuelven al inglés o muestran claves de mensaje para idiomas no soportados

**Solución**:
1. **Agregue Directorio de Idioma**: Cree estructura de directorio para nuevo idioma
2. **Copie Archivos de Traducción**: Use traducciones existentes como plantillas
3. **Actualice el Selector de Idioma**: Agregue nuevo idioma a la lista soportada
4. **Pruebe Exhaustivamente**: Verifique que todos los scripts funcionen con el nuevo idioma

Para instrucciones detalladas, vea `docs/templates/NEW_LANGUAGE_TEMPLATE.md`.

## Limitaciones de la API de AWS IoT Jobs

### Problema: No se puede acceder a los detalles de ejecución de trabajos para trabajos completados
**Síntomas**: Error al intentar explorar detalles de ejecución de trabajos para trabajos completados, fallidos o cancelados

**Ejemplo de Error**:
```
❌ Error in Job Execution Detail upgradeSedanvehicle110_1761321268 on Vehicle-VIN-016: 
Job Execution has reached terminal state. It is neither IN_PROGRESS nor QUEUED
❌ Failed to get job execution details. Check job ID and thing name.
```

**Causa Raíz**: AWS proporciona dos APIs diferentes para acceder a los detalles de ejecución de trabajos:

1. **IoT Jobs Data API** (servicio `iot-jobs-data`):
   - Endpoint: `describe_job_execution`
   - **Limitación**: Solo funciona para trabajos en estado `IN_PROGRESS` o `QUEUED`
   - **Error**: Devuelve "Job Execution has reached terminal state" para trabajos completados
   - **Caso de Uso**: Diseñado para que los dispositivos obtengan sus instrucciones de trabajo actuales

2. **IoT API** (servicio `iot`):
   - Endpoint: `describe_job_execution`
   - **Capacidad**: Funciona para trabajos en CUALQUIER estado (COMPLETED, FAILED, CANCELED, etc.)
   - **Sin Restricciones**: Puede acceder a datos históricos de ejecución de trabajos
   - **Caso de Uso**: Diseñado para gestión y monitoreo de todas las ejecuciones de trabajos

**Solución**: El script explore_jobs ha sido actualizado para usar la IoT API en lugar de la IoT Jobs Data API.

**Cambio de Código**:
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

**Verificación**: Después de la corrección, ahora puede explorar detalles de ejecución de trabajos para:
- ✅ Trabajos COMPLETED
- ✅ Trabajos FAILED  
- ✅ Trabajos CANCELED
- ✅ Trabajos IN_PROGRESS
- ✅ Trabajos QUEUED
- ✅ Cualquier otro estado de trabajo

**Beneficios Adicionales**:
- Acceso a datos históricos de ejecución de trabajos
- Mejores capacidades de solución de problemas para despliegues fallidos
- Registro de auditoría completo de intentos de actualización de dispositivos

### Problema: El documento de trabajo no está disponible en los detalles de ejecución
**Síntomas**: Los detalles de ejecución de trabajo se muestran pero falta el documento de trabajo

**Solución**: El script ahora incluye un mecanismo de respaldo:
1. Primero intenta obtener el documento de trabajo de los detalles de ejecución
2. Si no está disponible, lo recupera de los detalles principales del trabajo
3. Muestra un mensaje apropiado si el documento de trabajo no está disponible

Esto asegura que siempre pueda ver las instrucciones de trabajo que se enviaron al dispositivo, independientemente del estado del trabajo o las limitaciones de la API.
