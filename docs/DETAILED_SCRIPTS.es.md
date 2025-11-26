# Documentación Detallada de Scripts

Este documento proporciona información completa sobre cada script en el proyecto de AWS IoT Device Management. Todos los scripts utilizan el SDK nativo de AWS (boto3) para un rendimiento y confiabilidad óptimos.

## Scripts Principales

### scripts/provision_script.py
**Propósito**: Aprovisionamiento completo de infraestructura de AWS IoT para escenarios de gestión de dispositivos utilizando APIs nativas de boto3.

**Características**:
- Crea tipos de cosas con atributos buscables (customerId, country, manufacturingDate)
- Aprovisiona miles de dispositivos IoT con nomenclatura estilo VIN (Vehicle-VIN-001)
- Configura almacenamiento de Amazon S3 con versionado para paquetes de firmware
- Crea paquetes de software de AWS IoT con múltiples versiones
- Configura AWS IoT Fleet Indexing para consultas de dispositivos
- Establece roles de AWS Identity and Access Management (IAM) para operaciones seguras
- Crea grupos de cosas estáticos por país (convención de nomenclatura Fleet)
- **Procesamiento Paralelo**: Operaciones concurrentes para aprovisionamiento más rápido
- **Manejo de Errores Mejorado**: Manejo robusto de excepciones de boto3

**Entradas Interactivas**:
1. Tipos de cosas (predeterminado: SedanVehicle,SUVVehicle,TruckVehicle)
2. Versiones de paquetes (predeterminado: 1.0.0,1.1.0)
3. Selección de continente (1-7)
4. Países (cantidad o códigos específicos)
5. Cantidad de dispositivos (predeterminado: 100)

**Pausas Educativas**: 8 momentos de aprendizaje explicando conceptos de IoT

**Límites de Velocidad**: Limitación inteligente de API de AWS (80 TPS para cosas, 8 TPS para tipos de cosas)

**Rendimiento**: Ejecución paralela cuando no está en modo de depuración, secuencial en modo de depuración para salida limpia

---

### scripts/cleanup_script.py
**Propósito**: Eliminación segura de recursos de AWS IoT para evitar costos continuos utilizando APIs nativas de boto3.

**Opciones de Limpieza**:
1. **TODOS los recursos** - Limpieza completa de infraestructura
2. **Solo cosas** - Eliminar dispositivos pero mantener infraestructura
3. **Solo grupos de cosas** - Eliminar agrupaciones pero mantener dispositivos

**Características**:
- **Implementación Nativa de boto3**: Sin dependencias de CLI, mejor manejo de errores
- **Procesamiento paralelo** con limitación inteligente de velocidad
- **Limpieza Mejorada de S3**: Eliminación adecuada de objetos versionados usando paginadores
- Distingue automáticamente grupos estáticos vs dinámicos
- Maneja la depreciación de tipos de cosas (espera de 5 minutos)
- Cancela y elimina trabajos de AWS IoT con monitoreo de estado
- Limpieza completa de roles y políticas de IAM
- Deshabilita la configuración de Fleet Indexing
- **Limpieza de Sombras**: Elimina sombras clásicas y $package
- **Desvinculación de Principales**: Desvincula correctamente certificados y políticas

**Seguridad**: Requiere escribir "DELETE" para confirmar

**Rendimiento**: Ejecución paralela respetando límites de API de AWS (80 TPS cosas, 4 TPS grupos dinámicos)

---

### scripts/create_job.py
**Propósito**: Crear trabajos de AWS IoT para actualizaciones de firmware por aire utilizando APIs nativas de boto3.

**Características**:
- **Implementación Nativa de boto3**: Llamadas directas a API para mejor rendimiento
- Selección interactiva de grupos de cosas (único o múltiple)
- Selección de versión de paquete con resolución de ARN
- Configuración de trabajo continuo (incluye automáticamente nuevos dispositivos)
- Configuración de URL prefirmada (expiración de 1 hora)
- Soporte para múltiples grupos objetivo
- **Tipos de Trabajo Mejorados**: Soporte para tipos de trabajo OTA y personalizados
- **Configuración Avanzada**: Políticas de despliegue, criterios de aborto, configuración de tiempo de espera

**Configuración de Trabajo**:
- IDs de trabajo autogenerados con marcas de tiempo
- Marcadores de posición de URL prefirmada de AWS IoT
- Formato ARN adecuado para recursos
- Estructura completa de documento de trabajo
- **Contenido Educativo**: Explica opciones de configuración de trabajo

---

### scripts/simulate_job_execution.py
**Propósito**: Simular comportamiento realista de dispositivos durante actualizaciones de firmware utilizando APIs nativas de boto3.

**Características**:
- **Implementación Nativa de boto3**: Integración directa con API de IoT Jobs Data
- Descargas reales de artefactos de Amazon S3 mediante URLs prefirmadas
- **Ejecución Paralela de Alto Rendimiento** (150 TPS con control de semáforo)
- Tasas de éxito/fallo configurables
- **Preparación de plan visible** - Muestra cada dispositivo siendo asignado estado de éxito/fallo
- **Confirmación del usuario** - Pregunta para proceder después de la preparación del plan
- **Visibilidad de operación** - Muestra progreso de descarga y actualizaciones de estado de trabajo para cada dispositivo
- **Manejo de Errores Mejorado**: Gestión robusta de excepciones de boto3
- Seguimiento de progreso con informes detallados
- **Formato JSON Limpio**: Visualización de documento de trabajo correctamente formateado

**Flujo de Proceso**:
1. Escanea trabajos activos usando APIs nativas
2. Obtiene ejecuciones pendientes (QUEUED/IN_PROGRESS)
3. **Prepara plan de ejecución** - Muestra asignaciones de dispositivos y solicita confirmación
4. Descarga firmware real de Amazon S3 (muestra progreso por dispositivo)
5. Actualiza estado de ejecución de trabajo usando API de IoT Jobs Data
6. Reporta estadísticas completas de éxito/fallo

**Mejoras de Rendimiento**:
- **Procesamiento Paralelo**: Ejecución concurrente cuando no está en modo de depuración
- **Limitación de Velocidad**: Limitación inteligente basada en semáforos
- **Eficiencia de Memoria**: Descargas en streaming para archivos de firmware grandes

**Mejoras de Visibilidad**:
- Preparación de plan muestra: `[1/100] Vehicle-VIN-001 -> SUCCESS`
- Progreso de descarga muestra: `Vehicle-VIN-001: Downloading firmware from S3...`
- Confirmación de tamaño de archivo: `Vehicle-VIN-001: Downloaded 2.1KB firmware`
- Actualizaciones de estado muestran: `Vehicle-VIN-001: Job execution SUCCEEDED`

---

### scripts/explore_jobs.py
**Propósito**: Exploración interactiva de trabajos de AWS IoT para monitoreo y solución de problemas utilizando APIs nativas de boto3.

**Opciones de Menú**:
1. **Listar todos los trabajos** - Visión general de todos los estados con escaneo paralelo
2. **Explorar trabajo específico** - Configuración detallada de trabajo con formato JSON limpio
3. **Explorar ejecución de trabajo** - Progreso de dispositivo individual usando API de IoT Jobs Data
4. **Listar ejecuciones de trabajo** - Todas las ejecuciones para un trabajo con verificación de estado paralela

**Características**:
- **Implementación Nativa de boto3**: Integración directa de API para mejor rendimiento
- **Escaneo Paralelo de Trabajos**: Verificación concurrente de estado en todos los estados de trabajo
- **Visualización JSON Limpia**: Documentos de trabajo correctamente formateados sin caracteres de escape
- Indicadores de estado codificados por colores
- Selección interactiva de trabajo con listado de trabajos disponibles
- Visualización detallada de configuración de URL prefirmada
- Estadísticas de resumen de ejecución con codificación de colores
- **Manejo de Errores Mejorado**: Gestión robusta de excepciones de boto3
- Bucle de exploración continua

**Mejoras de Rendimiento**:
- **Procesamiento Paralelo**: Operaciones concurrentes cuando no está en modo de depuración
- **Paginación Inteligente**: Manejo eficiente de listas grandes de trabajos
- **Limitación de Velocidad**: Limitación adecuada de API con semáforos

---

### scripts/manage_packages.py
**Propósito**: Gestión completa de paquetes de software de AWS IoT, seguimiento de dispositivos y reversión de versiones utilizando APIs nativas de boto3.

**Operaciones**:
1. **Crear Paquete** - Crear nuevos contenedores de paquetes de software
2. **Crear Versión** - Agregar versiones con carga de firmware a S3 y publicación (con momentos de aprendizaje)
3. **Listar Paquetes** - Mostrar paquetes con opciones de descripción interactivas
4. **Describir Paquete** - Mostrar detalles del paquete con exploración de versiones
5. **Describir Versión** - Mostrar detalles de versión específica y artefactos de Amazon S3
6. **Verificar Configuración** - Ver estado de configuración del paquete y rol de IAM
7. **Habilitar Configuración** - Habilitar actualizaciones automáticas de sombra con creación de rol de IAM
8. **Deshabilitar Configuración** - Deshabilitar actualizaciones automáticas de sombra
9. **Verificar Versión de Dispositivo** - Inspeccionar sombra $package para dispositivos específicos (soporte multi-dispositivo)
10. **Revertir Versiones** - Reversión de versión a nivel de flota usando Fleet Indexing

**Características Clave**:
- **Integración con Amazon S3**: Carga automática de firmware con versionado
- **Navegación Interactiva**: Flujo fluido entre operaciones de listar, describir y versión
- **Gestión de Configuración de Paquetes**: Control de integración Jobs-to-Shadow
- **Seguimiento de Dispositivos**: Inspección de versión de paquete de dispositivo individual
- **Reversión de Flota**: Reversión de versión usando consultas de Fleet Indexing
- **Enfoque Educativo**: Momentos de aprendizaje a lo largo de los flujos de trabajo
- **Gestión de Roles de IAM**: Creación automática de roles para configuración de paquetes

**Configuración de Paquetes**:
- **Verificar Estado**: Muestra estado habilitado/deshabilitado y ARN de rol de IAM
- **Habilitar**: Crea IoTPackageConfigRole con permisos de sombra $package
- **Deshabilitar**: Detiene actualizaciones automáticas de sombra al completar trabajo
- **Educativo**: Explica integración Jobs-to-Shadow y requisitos de IAM

**Seguimiento de Versión de Dispositivos**:
- **Soporte Multi-dispositivo**: Verificar múltiples dispositivos en secuencia
- **Inspección de Sombra $package**: Muestra versiones actuales de firmware y metadatos
- **Visualización de Marca de Tiempo**: Información de última actualización para cada paquete
- **Manejo de Errores**: Mensajes claros para dispositivos o sombras faltantes

**Reversión de Versión**:
- **Consultas de Fleet Indexing**: Encontrar dispositivos por tipo de cosa y versión
- **Vista Previa de Lista de Dispositivos**: Muestra dispositivos que serán revertidos (primeros 10 + conteo)
- **Confirmación Requerida**: Escribir 'REVERT' para proceder con actualizaciones de sombra
- **Estado de Dispositivo Individual**: Muestra éxito/fallo de reversión por dispositivo
- **Seguimiento de Progreso**: Estado de actualización en tiempo real con conteos de éxito
- **Educativo**: Explica conceptos de reversión y gestión de sombras

**Visibilidad de Reversión**:
- Vista previa de dispositivos: `1. Vehicle-VIN-001`, `2. Vehicle-VIN-002`, `... y 90 dispositivos más`
- Resultados individuales: `Vehicle-VIN-001: Reverted to version 1.0.0`
- Intentos fallidos: `Vehicle-VIN-002: Failed to revert`

**Enfoque de Aprendizaje**:
- Ciclo de vida completo de firmware desde creación hasta reversión
- Configuración de paquetes y actualizaciones automáticas de sombra
- Gestión y seguimiento de inventario de dispositivos
- Fleet Indexing para operaciones de gestión de versiones

---

### scripts/manage_dynamic_groups.py
**Propósito**: Gestión completa de grupos de cosas dinámicos con validación de Fleet Indexing utilizando APIs nativas de boto3.

**Operaciones**:
1. **Crear Grupos Dinámicos** - Dos métodos de creación:
   - **Asistente guiado**: Selección interactiva de criterios
   - **Consulta personalizada**: Entrada directa de consulta de Fleet Indexing
2. **Listar Grupos Dinámicos** - Mostrar todos los grupos con conteos de miembros y consultas
3. **Eliminar Grupos Dinámicos** - Eliminación segura con confirmación
4. **Probar Consultas** - Validar consultas personalizadas de Fleet Indexing

**Métodos de Creación**:
- **Asistente Guiado** (todo opcional):
  - Países: Único o múltiple (ej., US,CA,MX)
  - Tipo de Cosa: Categoría de vehículo (ej., SedanVehicle)
  - Versiones: Única o múltiple (ej., 1.0.0,1.1.0)
  - Nivel de Batería: Comparaciones (ej., >50, <30, =75)
- **Consulta Personalizada**: Entrada directa de cadena de consulta de Fleet Indexing

**Características**:
- **Modos de creación duales**: Asistente guiado o entrada de consulta personalizada
- Nomenclatura inteligente de grupos (autogenerada o personalizada)
- Construcción y validación de consultas de Fleet Indexing
- **Vista previa de coincidencia de dispositivos en tiempo real** (muestra dispositivos coincidentes antes de la creación)
- Visualización de conteo de miembros para grupos existentes
- Eliminación segura con solicitudes de confirmación
- Capacidades de prueba de consultas personalizadas
- La validación de consultas previene la creación de grupos vacíos

**Ejemplos de Consultas**:
- Criterio único: `thingTypeName:SedanVehicle AND attributes.country:US`
- Múltiples criterios: `thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- Versiones de paquetes: `shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- Complejo personalizado: `(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**Propósito**: Validación de sintaxis previa a la publicación para pipeline CI/CD.

**Verificaciones**:
- Validación de sintaxis de Python para todos los scripts
- Verificación de disponibilidad de importaciones
- Validación de requirements.txt
- Listado de dependencias

**Uso**: Ejecutado automáticamente por flujo de trabajo de GitHub Actions

---

## Dependencias de Scripts

### Paquetes de Python Requeridos
- `boto3>=1.40.27` - AWS SDK para Python (última versión para soporte de artefactos de paquetes)
- `colorama>=0.4.4` - Colores de terminal
- `requests>=2.25.1` - Solicitudes HTTP para descargas de Amazon S3

### Servicios de AWS Utilizados
- **AWS IoT Core** - Gestión de cosas, trabajos, sombras
- **AWS IoT Device Management** - Paquetes de software, Fleet Indexing
- **Amazon S3** - Almacenamiento de firmware con versionado
- **AWS Identity and Access Management (IAM)** - Roles y políticas para acceso seguro

### Requisitos de Credenciales de AWS
- Credenciales configuradas mediante:
  - `aws configure` (AWS CLI)
  - Variables de entorno (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - Roles de IAM (para ejecución en EC2/Lambda)
  - Archivo de credenciales de AWS
- Permisos de IAM apropiados para operaciones de AWS IoT, Amazon S3 e IAM
- Configuración de región (variable de entorno AWS_DEFAULT_REGION o credenciales)

## Características Educativas

### Momentos de Aprendizaje
Cada script incluye pausas educativas explicando:
- Conceptos y arquitectura de AWS IoT
- Mejores prácticas para gestión de dispositivos
- Consideraciones de seguridad
- Patrones de escalabilidad

### Seguimiento de Progreso
- Estado de operación en tiempo real
- Conteos de éxito/fallo
- Métricas de rendimiento (TPS, duración)
- Salida codificada por colores para fácil lectura

### Modo de Depuración
Disponible en todos los scripts:
- Muestra todas las llamadas a API del SDK de AWS (boto3) con parámetros
- Muestra respuestas completas de API en formato JSON
- Proporciona información detallada de errores con trazas de pila completas
- **Procesamiento Secuencial**: Ejecuta operaciones secuencialmente para salida de depuración limpia
- Ayuda con solución de problemas y aprendizaje de APIs de AWS

## Características de Rendimiento

### Limitación de Velocidad
Los scripts respetan los límites de API de AWS:
- Operaciones de cosas: 80 TPS (límite de 100 TPS)
- Tipos de cosas: 8 TPS (límite de 10 TPS)
- Grupos dinámicos: 4 TPS (límite de 5 TPS)
- Ejecuciones de trabajos: 150 TPS (límite de 200 TPS)
- Operaciones de paquetes: 8 TPS (límite de 10 TPS)

### Procesamiento Paralelo
- **Integración Nativa de boto3**: Llamadas directas al SDK de AWS para mejor rendimiento
- ThreadPoolExecutor para operaciones concurrentes (cuando no está en modo de depuración)
- **Limitación Inteligente de Velocidad**: Semáforos respetando límites de API de AWS
- **Seguimiento de Progreso Thread-Safe**: Monitoreo de operaciones concurrentes
- **Manejo de Errores Mejorado**: Gestión robusta de excepciones ClientError de boto3
- **Anulación de Modo de Depuración**: Procesamiento secuencial en modo de depuración para salida limpia

### Gestión de Memoria
- Descargas en streaming para archivos grandes
- Limpieza de archivos temporales
- Análisis eficiente de JSON
- Limpieza de recursos al salir
