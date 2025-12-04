# Documentación Detallada de Scripts

Este documento proporciona información completa sobre cada script en el proyecto AWS IoT Device Management. Todos los scripts utilizan el SDK nativo de AWS (boto3) para un rendimiento y confiabilidad óptimos.

## Scripts Principales

### scripts/provision_script.py
**Propósito**: Aprovisionamiento completo de infraestructura AWS IoT para escenarios de gestión de dispositivos utilizando APIs nativas de boto3.

**Características**:
- Crea tipos de cosas con atributos buscables (customerId, country, manufacturingDate)
- Aprovisiona miles de dispositivos IoT con nomenclatura estilo VIN (Vehicle-VIN-001)
- Configura almacenamiento Amazon S3 con versionado para paquetes de firmware
- Crea paquetes de software AWS IoT con múltiples versiones
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

**Límites de Tasa**: Limitación inteligente de API de AWS (80 TPS para cosas, 8 TPS para tipos de cosas)

**Rendimiento**: Ejecución paralela cuando no está en modo de depuración, secuencial en modo de depuración para salida limpia

---

### scripts/cleanup_script.py
**Propósito**: Eliminación segura de recursos AWS IoT para evitar costos continuos utilizando APIs nativas de boto3.

**Opciones de Limpieza**:
1. **TODOS los recursos** - Limpieza completa de infraestructura
2. **Solo cosas** - Eliminar dispositivos pero mantener infraestructura
3. **Solo grupos de cosas** - Eliminar agrupaciones pero mantener dispositivos

**Características**:
- **Implementación Nativa de boto3**: Sin dependencias de CLI, mejor manejo de errores
- **Procesamiento paralelo** con limitación de tasa inteligente
- **Limpieza Mejorada de S3**: Eliminación adecuada de objetos versionados usando paginadores
- Distingue automáticamente grupos estáticos vs dinámicos
- Maneja la depreciación de tipos de cosas (espera de 5 minutos)
- Cancela y elimina AWS IoT Jobs con monitoreo de estado
- Limpieza completa de roles y políticas de IAM
- Deshabilita la configuración de Fleet Indexing
- **Limpieza de Shadows**: Elimina shadows clásicos y $package
- **Desvinculación de Principales**: Desvincula adecuadamente certificados y políticas

**Seguridad**: Requiere escribir "DELETE" para confirmar

**Rendimiento**: Ejecución paralela respetando límites de API de AWS (80 TPS cosas, 4 TPS grupos dinámicos)

---

### scripts/create_job.py
**Propósito**: Crear AWS IoT Jobs para actualizaciones de firmware over-the-air utilizando APIs nativas de boto3.

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
- Descargas reales de artefactos de Amazon S3 a través de URLs prefirmadas
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
- **Limitación de Tasa**: Limitación inteligente basada en semáforos
- **Eficiencia de Memoria**: Descargas en streaming para archivos de firmware grandes

**Mejoras de Visibilidad**:
- Preparación de plan muestra: `[1/100] Vehicle-VIN-001 -> SUCCESS`
- Progreso de descarga muestra: `Vehicle-VIN-001: Downloading firmware from S3...`
- Confirmación de tamaño de archivo: `Vehicle-VIN-001: Downloaded 2.1KB firmware`
- Actualizaciones de estado muestran: `Vehicle-VIN-001: Job execution SUCCEEDED`

---

### scripts/explore_jobs.py
**Propósito**: Exploración interactiva de AWS IoT Jobs para monitoreo y solución de problemas utilizando APIs nativas de boto3.

**Opciones de Menú**:
1. **Listar todos los trabajos** - Visión general de todos los estados con escaneo paralelo
2. **Explorar trabajo específico** - Configuración detallada de trabajo con formato JSON limpio
3. **Explorar ejecución de trabajo** - Progreso de dispositivo individual usando API de IoT Jobs Data
4. **Listar ejecuciones de trabajo** - Todas las ejecuciones para un trabajo con verificación de estado paralela
5. **Cancelar trabajo** - Cancelar trabajos activos con análisis de impacto y orientación educativa
6. **Eliminar trabajo** - Eliminar trabajos completados/cancelados con manejo automático de bandera de fuerza
7. **Ver estadísticas** - Análisis completo de trabajos con evaluación de salud y recomendaciones

**Características**:
- **Implementación Nativa de boto3**: Integración directa de API para mejor rendimiento
- **Escaneo Paralelo de Trabajos**: Verificación concurrente de estado en todos los estados de trabajo
- **Visualización JSON Limpia**: Documentos de trabajo correctamente formateados sin caracteres de escape
- Indicadores de estado codificados por colores
- Selección interactiva de trabajos con listado de trabajos disponibles
- Visualización detallada de configuración de URL prefirmada
- Estadísticas resumidas de ejecución con codificación de colores
- **Manejo de Errores Mejorado**: Gestión robusta de excepciones de boto3
- Bucle de exploración continua
- **Gestión del Ciclo de Vida del Trabajo**: Operaciones de cancelación y eliminación con confirmaciones de seguridad
- **Análisis Avanzado**: Estadísticas completas con evaluaciones de salud

**Características de Cancelar Trabajo**:
- Escanea trabajos activos (IN_PROGRESS, SCHEDULED)
- Muestra detalles del trabajo y cantidad de objetivos
- Análisis de impacto con conteos de ejecución por estado (QUEUED, IN_PROGRESS, SUCCEEDED, FAILED)
- Contenido educativo explicando cuándo y por qué cancelar trabajos
- Confirmación de seguridad requiriendo "CANCEL" para proceder
- Comentario de cancelación opcional para registro de auditoría
- Actualizaciones de estado en tiempo real

**Características de Eliminar Trabajo**:
- Escanea trabajos eliminables (COMPLETED, CANCELED)
- Muestra marcas de tiempo de finalización de trabajo
- Verifica historial de ejecución para determinar si se necesita bandera de fuerza
- Contenido educativo sobre implicaciones de eliminación
- Bandera de fuerza automática cuando existen ejecuciones
- Confirmación de seguridad requiriendo "DELETE" para proceder
- Explica diferencia entre cancelar y eliminar operaciones

**Características de Ver Estadísticas**:
- Visión general completa del trabajo (estado, fechas de creación/finalización, objetivos)
- Estadísticas de ejecución con porcentajes por estado
- Cálculos de tasa de éxito/fallo
- Desglose detallado de todos los estados de ejecución
- Evaluación de salud (Excelente ≥95%, Bueno ≥80%, Pobre ≥50%, Crítico <50%)
- Contenido educativo sobre estados de ejecución y patrones de fallo
- Recomendaciones conscientes del contexto basadas en el estado del trabajo:
  - Sin ejecuciones: Verificar conectividad del dispositivo y membresía del grupo
  - Cancelado temprano: Revisar razones de cancelación
  - Dispositivos eliminados: Verificar existencia del dispositivo
  - En progreso: Esperar y monitorear
  - Alta tasa de fallo: Investigar y considerar cancelación
  - Fallo moderado: Monitorear de cerca
  - Rendimiento excelente: Documentar patrones de éxito

**Mejoras de Rendimiento**:
- **Procesamiento Paralelo**: Operaciones concurrentes cuando no está en modo de depuración
- **Paginación Inteligente**: Manejo eficiente de listas de trabajos grandes
- **Limitación de Tasa**: Limitación adecuada de API con semáforos

---



### scripts/manage_packages.py
**Propósito**: Gestión completa de AWS IoT Software Packages, seguimiento de dispositivos y reversión de versiones utilizando APIs nativas de boto3.

**Operaciones**:
1. **Crear Paquete** - Crear nuevos contenedores de paquetes de software
2. **Crear Versión** - Agregar versiones con carga de firmware S3 y publicación (con momentos de aprendizaje)
3. **Listar Paquetes** - Mostrar paquetes con opciones de descripción interactivas
4. **Describir Paquete** - Mostrar detalles del paquete con exploración de versiones
5. **Describir Versión** - Mostrar detalles de versión específica y artefactos de Amazon S3
6. **Verificar Configuración** - Ver estado de configuración del paquete y rol de IAM
7. **Habilitar Configuración** - Habilitar actualizaciones automáticas de shadow con creación de rol de IAM
8. **Deshabilitar Configuración** - Deshabilitar actualizaciones automáticas de shadow
9. **Verificar Versión del Dispositivo** - Inspeccionar shadow $package para dispositivos específicos (soporte multi-dispositivo)
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
- **Verificar Estado**: Muestra estado habilitado/deshabilitado y ARN del rol de IAM
- **Habilitar**: Crea IoTPackageConfigRole con permisos de shadow $package
- **Deshabilitar**: Detiene actualizaciones automáticas de shadow al completar trabajo
- **Educativo**: Explica integración Jobs-to-Shadow y requisitos de IAM

**Seguimiento de Versión del Dispositivo**:
- **Soporte Multi-dispositivo**: Verificar múltiples dispositivos en secuencia
- **Inspección de Shadow $package**: Muestra versiones de firmware actuales y metadatos
- **Visualización de Marca de Tiempo**: Información de última actualización para cada paquete
- **Manejo de Errores**: Mensajes claros para dispositivos o shadows faltantes

**Reversión de Versión**:
- **Consultas de Fleet Indexing**: Encontrar dispositivos por tipo de cosa y versión
- **Vista Previa de Lista de Dispositivos**: Muestra dispositivos que serán revertidos (primeros 10 + conteo)
- **Confirmación Requerida**: Escribir 'REVERT' para proceder con actualizaciones de shadow
- **Estado de Dispositivo Individual**: Muestra éxito/fallo de reversión por dispositivo
- **Seguimiento de Progreso**: Estado de actualización en tiempo real con conteos de éxito
- **Educativo**: Explica conceptos de reversión y gestión de shadow

**Visibilidad de Reversión**:
- Vista previa de dispositivo: `1. Vehicle-VIN-001`, `2. Vehicle-VIN-002`, `... y 90 dispositivos más`
- Resultados individuales: `Vehicle-VIN-001: Reverted to version 1.0.0`
- Intentos fallidos: `Vehicle-VIN-002: Failed to revert`

**Enfoque de Aprendizaje**:
- Ciclo de vida completo de firmware desde creación hasta reversión
- Configuración de paquetes y actualizaciones automáticas de shadow
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
- **Asistente Guiado** (todos opcionales):
  - Países: Único o múltiple (ej., US,CA,MX)
  - Tipo de Cosa: Categoría de vehículo (ej., SedanVehicle)
  - Versiones: Único o múltiple (ej., 1.0.0,1.1.0)
  - Nivel de Batería: Comparaciones (ej., >50, <30, =75)
- **Consulta Personalizada**: Entrada directa de cadena de consulta de Fleet Indexing

**Características**:
- **Modos de creación duales**: Asistente guiado o entrada de consulta personalizada
- Nomenclatura inteligente de grupos (autogenerada o personalizada)
- Construcción y validación de consultas de Fleet Indexing
- **Vista previa de coincidencia de dispositivos en tiempo real** (muestra dispositivos coincidentes antes de la creación)
- Visualización de conteo de miembros para grupos existentes
- Eliminación segura con indicaciones de confirmación
- Capacidades de prueba de consultas personalizadas
- La validación de consultas previene la creación de grupos vacíos

**Ejemplos de Consultas**:
- Criterio único: `thingTypeName:SedanVehicle AND attributes.country:US`
- Criterios múltiples: `thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- Versiones de paquetes: `shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- Complejo personalizado: `(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**Propósito**: Validación de sintaxis pre-publicación para pipeline de CI/CD.

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
- **AWS IoT Core** - Gestión de cosas, trabajos, shadows
- **AWS IoT Device Management** - Paquetes de software, Fleet Indexing
- **Amazon S3** - Almacenamiento de firmware con versionado
- **AWS Identity and Access Management (IAM)** - Roles y políticas para acceso seguro

### Requisitos de Credenciales de AWS
- Credenciales configuradas a través de:
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

### Limitación de Tasa
Los scripts respetan los límites de API de AWS:
- Operaciones de cosas: 80 TPS (límite de 100 TPS)
- Tipos de cosas: 8 TPS (límite de 10 TPS)
- Grupos dinámicos: 4 TPS (límite de 5 TPS)
- Ejecuciones de trabajos: 150 TPS (límite de 200 TPS)
- Operaciones de paquetes: 8 TPS (límite de 10 TPS)

### Procesamiento Paralelo
- **Integración Nativa de boto3**: Llamadas directas al SDK de AWS para mejor rendimiento
- ThreadPoolExecutor para operaciones concurrentes (cuando no está en modo de depuración)
- **Limitación de Tasa Inteligente**: Semáforos respetando límites de API de AWS
- **Seguimiento de Progreso Thread-Safe**: Monitoreo de operación concurrente
- **Manejo de Errores Mejorado**: Gestión robusta de excepciones ClientError de boto3
- **Anulación de Modo de Depuración**: Procesamiento secuencial en modo de depuración para salida limpia

### Gestión de Memoria
- Descargas en streaming para archivos grandes
- Limpieza de archivos temporales
- Análisis eficiente de JSON
- Limpieza de recursos al salir

---


### scripts/manage_commands.py
**Propósito**: Gestión completa de AWS IoT Commands para enviar comandos en tiempo real a dispositivos IoT utilizando APIs nativas de boto3.

**Operaciones**:
1. **Crear Comando** - Crear nuevas plantillas de comando con definiciones de formato de carga útil
2. **Listar Comandos** - Mostrar todas las plantillas de comando (predefinidas y personalizadas)
3. **Ver Detalles del Comando** - Mostrar especificaciones completas de plantilla de comando
4. **Eliminar Comando** - Eliminar plantillas de comando personalizadas con confirmaciones de seguridad
5. **Ejecutar Comando** - Enviar comandos a dispositivos o grupos de cosas
6. **Ver Estado del Comando** - Monitorear progreso y resultados de ejecución de comandos
7. **Ver Historial de Comandos** - Navegar ejecuciones de comandos pasadas con filtrado
8. **Cancelar Comando** - Cancelar ejecuciones de comandos pendientes o en progreso
9. **Habilitar/Deshabilitar Modo de Depuración** - Alternar registro detallado de API
10. **Salir** - Salir del script

**Características Clave**:
- **Implementación Nativa de boto3**: Integración directa con API de AWS IoT Commands
- **Plantillas Automotrices Predefinidas**: Seis plantillas de comando de vehículo listas para usar
- **Gestión de Plantillas de Comando**: Crear, listar, ver y eliminar plantillas de comando
- **Ejecución de Comandos**: Enviar comandos a dispositivos individuales o grupos de cosas
- **Monitoreo de Estado**: Seguimiento de ejecución de comandos en tiempo real con indicadores de progreso
- **Historial de Comandos**: Navegar y filtrar ejecuciones de comandos pasadas
- **Cancelación de Comandos**: Cancelar comandos pendientes o en progreso
- **Integración con Scripts de IoT Core**: Integración fluida con certificate_manager y mqtt_client_explorer
- **Documentación de Tópicos MQTT**: Referencia completa de estructura de tópicos
- **Ejemplos de Simulación de Dispositivos**: Cargas útiles de respuesta de éxito y fallo
- **Enfoque Educativo**: Momentos de aprendizaje a lo largo de los flujos de trabajo
- **Soporte Multilingüe**: Soporte completo de i18n para 6 idiomas

**Plantillas de Comando Automotrices Predefinidas**:
El script incluye seis plantillas de comando predefinidas para operaciones comunes de vehículos:

1. **vehicle-lock** - Bloquear puertas del vehículo remotamente
   - Carga útil: `{"action": "lock", "vehicleId": "string"}`
   - Caso de uso: Bloqueo remoto de puertas para seguridad

2. **vehicle-unlock** - Desbloquear puertas del vehículo remotamente
   - Carga útil: `{"action": "unlock", "vehicleId": "string"}`
   - Caso de uso: Desbloqueo remoto de puertas para acceso

3. **start-engine** - Arrancar motor del vehículo remotamente
   - Carga útil: `{"action": "start", "vehicleId": "string", "duration": "number"}`
   - Caso de uso: Arranque remoto del motor para control de clima

4. **stop-engine** - Detener motor del vehículo remotamente
   - Carga útil: `{"action": "stop", "vehicleId": "string"}`
   - Caso de uso: Apagado de emergencia del motor

5. **set-climate** - Establecer temperatura de clima del vehículo
   - Carga útil: `{"action": "setClimate", "vehicleId": "string", "temperature": "number", "unit": "string"}`
   - Caso de uso: Pre-acondicionamiento de temperatura del vehículo

6. **activate-horn** - Activar bocina del vehículo
   - Carga útil: `{"action": "horn", "vehicleId": "string", "duration": "number"}`
   - Caso de uso: Asistencia de ubicación del vehículo

**Gestión de Plantillas de Comando**:

**Crear Plantilla de Comando**:
- Indicaciones interactivas para nombre de comando, descripción y formato de carga útil
- Validación de esquema JSON para estructura de carga útil
- Configuración de espacio de nombres AWS-IoT
- Manejo de carga útil de blob binario con contentType
- Generación y visualización automática de ARN
- Validación contra requisitos de AWS IoT Commands:
  - Nombre: 1-128 caracteres, alfanumérico/guión/guión bajo, debe comenzar con alfanumérico
  - Descripción: 1-256 caracteres
  - Carga útil: Esquema JSON válido, complejidad máxima de 10KB

**Listar Plantillas de Comando**:
- Muestra plantillas predefinidas y personalizadas
- Formato de tabla codificado por colores con:
  - Nombre de plantilla
  - Descripción
  - Fecha de creación
  - ARN de plantilla
  - Estado (ACTIVE, DEPRECATED, PENDING_DELETION)
- Navegación interactiva para ver detalles de plantilla
- Soporte de paginación para listas de plantillas grandes

**Ver Detalles del Comando**:
- Visualización completa de especificación de formato de carga útil
- Nombres de parámetros, tipos y restricciones
- Campos requeridos vs opcionales
- Valores de parámetros de ejemplo
- Metadatos de plantilla (fecha de creación, ARN, estado)
- Formato JSON limpio para estructura de carga útil

**Eliminar Plantilla de Comando**:
- Confirmación de seguridad requiriendo "DELETE" para proceder
- Verificación de que ningún comando activo usa la plantilla
- Protección contra eliminación de plantillas predefinidas
- Mensajes de error claros para fallos de eliminación
- Limpieza automática de recursos de plantilla

**Ejecución de Comandos**:

**Ejecutar Comando**:
- Selección interactiva de plantilla de comando de plantillas disponibles
- Selección de objetivo:
  - Dispositivo único (nombre de cosa)
  - Grupo de cosas (nombre de grupo)
- Validación de objetivo:
  - Verificación de existencia de dispositivo en registro de IoT
  - Validación de grupo de cosas con visualización de conteo de miembros
- Recopilación de parámetros coincidentes con formato de carga útil de plantilla
- Tiempo de espera de ejecución configurable (predeterminado 60 segundos)
- Publicación automática de tópico MQTT a:
  - `$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/json`
- Visualización de éxito con:
  - ID de ejecución de comando
  - Estado inicial (CREATED/IN_PROGRESS)
  - Información de tópico MQTT
- Soporte de múltiples objetivos (crea ejecuciones separadas por objetivo)

**Monitoreo de Estado de Comandos**:

**Ver Estado del Comando**:
- Recuperación de estado en tiempo real usando API GetCommandExecution
- La visualización de estado incluye:
  - ID de ejecución de comando
  - Nombre de dispositivo/grupo objetivo
  - Estado actual (CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED)
  - Marca de tiempo de creación
  - Marca de tiempo de última actualización
- Indicadores de progreso para estado IN_PROGRESS:
  - Visualización de progreso animada
  - Tiempo transcurrido desde la creación
- Información de comando completado:
  - Estado final (SUCCEEDED/FAILED)
  - Duración de ejecución
  - Razón de estado (si se proporciona)
  - Marca de tiempo de finalización
- Indicadores de estado codificados por colores:
  - Verde: SUCCEEDED
  - Amarillo: IN_PROGRESS, CREATED
  - Rojo: FAILED, TIMED_OUT, CANCELED

**Ver Historial de Comandos**:
- Historial completo de ejecución de comandos
- Opciones de filtrado:
  - Filtro de nombre de dispositivo
  - Filtro de estado (CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED)
  - Filtro de rango de tiempo (marcas de tiempo de inicio/fin)
- Soporte de paginación:
  - Tamaño de página configurable (1-100, predeterminado 50)
  - Navegación de página siguiente
  - Visualización de conteo total
- La visualización de historial incluye:
  - Nombre de comando
  - Dispositivo/grupo objetivo
  - Estado de ejecución
  - Hora de creación
  - Hora de finalización (si aplica)
  - Duración de ejecución
- Manejo de historial vacío con mensaje informativo
- Estado codificado por colores para escaneo fácil

**Cancelación de Comandos**:

**Cancelar Comando**:
- Entrada interactiva de ID de ejecución de comando
- Confirmación de seguridad requiriendo "CANCEL" para proceder
- Envío de solicitud de cancelación a AWS IoT
- Verificación de actualización de estado (CANCELED)
- Manejo de rechazo para comandos completados:
  - Mensaje de error claro para comandos ya completados
  - Visualización de estado actual del comando
- Visualización de información de fallo:
  - Razón de fallo
  - Estado actual del comando
  - Sugerencias de solución de problemas


**Integración con Scripts de IoT Core**:

El script proporciona orientación completa de integración para usar scripts de AWS IoT Core para simular manejo de comandos del lado del dispositivo:

**Integración con Certificate Manager** (`certificate_manager.py`):
- Creación y gestión de certificados de dispositivos
- Asociación de certificado a política
- Adjunción de certificado a cosa
- Configuración de autenticación para conexiones MQTT
- Instrucciones paso a paso de configuración de terminal:
  1. Abrir nueva ventana de terminal (Terminal 2)
  2. Copiar credenciales de AWS del entorno del taller
  3. Navegar al directorio de scripts de IoT Core
  4. Ejecutar certificate_manager.py para configurar autenticación de dispositivo

**Integración con MQTT Client Explorer** (`mqtt_client_explorer.py`):
- Configuración de suscripción a tópico de comando
- Recepción de comandos en tiempo real
- Publicación de carga útil de respuesta
- Simulación de éxito/fallo
- Flujo de trabajo de integración paso a paso:
  1. Suscribirse al tópico de solicitud de comando: `$aws/commands/things/<ThingName>/executions/+/request/#`
  2. Recibir cargas útiles de comando con ID de ejecución
  3. Publicar resultado de ejecución al tópico de respuesta: `$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/json`
  4. Opcionalmente suscribirse a tópicos aceptados/rechazados para confirmación

**Ejemplos de Simulación de Dispositivos**:

El script proporciona cargas útiles de ejemplo completas para simular respuestas de dispositivos:

**Ejemplo de Respuesta de Éxito**:
```json
{
  "status": "SUCCEEDED",
  "executionId": "<ExecutionId>",
  "statusReason": "Vehicle doors locked successfully",
  "timestamp": 1701518710000
}
```

**Ejemplo de Respuesta de Fallo**:
```json
{
  "status": "FAILED",
  "executionId": "<ExecutionId>",
  "statusReason": "Unable to lock vehicle - door sensor malfunction",
  "timestamp": 1701518710000
}
```

**Valores de Estado Válidos**: SUCCEEDED, FAILED, IN_PROGRESS, TIMED_OUT, REJECTED

**Estructura de Tópicos MQTT**:

El script documenta la estructura completa de tópicos MQTT para AWS IoT Commands:

**Tópico de Solicitud de Comando** (el dispositivo se suscribe para recibir comandos):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request
```

**Tópico de Respuesta de Comando** (el dispositivo publica resultado de ejecución):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/<PayloadFormat>
```

**Tópico Aceptado de Respuesta** (el dispositivo se suscribe para confirmación):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted
```

**Tópico Rechazado de Respuesta** (el dispositivo se suscribe para notificación de rechazo):
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected
```

**Explicaciones de Componentes de Tópico**:
- `<ThingName>`: Nombre de la cosa IoT o ID de cliente MQTT
- `<ExecutionId>`: Identificador único para cada ejecución de comando (usar comodín `+` para suscribirse a todas)
- `<PayloadFormat>`: Indicador de formato (json, cbor) - puede omitirse si no es JSON/CBOR
- Suscripción con comodín: `$aws/commands/things/<ThingName>/executions/+/request/#`

**Alternativa de Cliente de Prueba de AWS IoT**:
- Alternativa basada en consola a mqtt_client_explorer
- Acceso a través de Consola de AWS IoT → Prueba → Cliente de prueba MQTT
- Suscribirse a tópicos de comando
- Publicar cargas útiles de respuesta
- Útil para pruebas rápidas sin scripts locales

**Momentos de Aprendizaje**:

El script incluye momentos de aprendizaje contextuales que aparecen automáticamente después de operaciones clave:

1. **¿Qué son las Plantillas de Comando?** - Mostrado después de la primera creación de plantilla
   - Explica el propósito y estructura de la plantilla de comando
   - Describe requisitos de formato de carga útil
   - Compara con otras características de AWS IoT

2. **Commands vs Device Shadow vs Jobs** - Mostrado después de la primera ejecución de comando
   - Tabla de comparación mostrando cuándo usar cada característica
   - Commands: Acción inmediata, en tiempo real del dispositivo (segundos)
   - Device Shadow: Sincronización de estado deseado (consistencia eventual)
   - Jobs: Operaciones de larga duración, actualizaciones de firmware (minutos a horas)
   - Ejemplos de casos de uso para cada característica

3. **Estructura de Tópicos MQTT** - Mostrado al mostrar integración con mqtt_client_explorer
   - Documentación completa de patrón de tópico
   - Explicaciones de tópicos de solicitud/respuesta
   - Ejemplos de suscripción con comodín
   - Descripciones de componentes de tópico

4. **Ciclo de Vida de Ejecución de Comando** - Mostrado después de ver estado de comando
   - Flujo de transición de estado (CREATED → IN_PROGRESS → SUCCEEDED/FAILED)
   - Manejo de tiempo de espera
   - Comportamiento de cancelación
   - Mejores prácticas para monitoreo

5. **Mejores Prácticas** - Mostrado después de ver historial de comandos
   - Convenciones de nomenclatura de comandos
   - Orientación de configuración de tiempo de espera
   - Estrategias de manejo de errores
   - Recomendaciones de monitoreo y alertas

6. **Integración con Consola** - Mostrado con recordatorio de Punto de Control de Consola
   - Navegación de Consola de AWS IoT
   - Verificación de plantilla de comando
   - Visualización de línea de tiempo de ejecución
   - Comparación CLI vs Consola

**Manejo de Errores**:

El script implementa manejo completo de errores con mensajes amigables para el usuario:

**Errores de Validación**:
- Validación de nombre de comando (longitud, caracteres, formato)
- Validación de descripción (longitud, contenido)
- Validación de formato de carga útil (esquema JSON, complejidad)
- Validación de objetivo (existencia de dispositivo/grupo)
- Validación de parámetros (tipo, campos requeridos)
- Mensajes de error claros con orientación de corrección

**Errores de API de AWS**:
- ResourceNotFoundException: Comando u objetivo no encontrado
- InvalidRequestException: Carga útil o parámetros inválidos
- ThrottlingException: Límite de tasa excedido con orientación de reintento
- UnauthorizedException: Permisos insuficientes
- Retroceso exponencial para limitación de tasa
- Reintento automático para errores transitorios (hasta 3 intentos)
- Mensajes de error detallados con sugerencias de solución de problemas

**Errores de Red**:
- Detección de problemas de conectividad
- Orientación de verificación de credenciales de AWS
- Verificaciones de configuración de región
- Opciones de reintento con indicaciones de usuario

**Errores de Estado**:
- Cancelación de comandos completados
- Eliminación de plantillas en uso
- Transiciones de estado inválidas
- Explicaciones claras del estado actual

**Modo de Depuración**:
- Muestra todas las llamadas a API del SDK de AWS (boto3) con parámetros
- Muestra respuestas completas de API en formato JSON
- Proporciona información detallada de errores con trazas de pila completas
- Ayuda con solución de problemas y aprendizaje de APIs de AWS
- Alternar activado/desactivado durante la ejecución del script

**Características de Rendimiento**:
- **Integración Nativa de boto3**: Llamadas directas al SDK de AWS para mejor rendimiento
- **Limitación de Tasa**: Respeta límites de API de AWS IoT Commands
- **Paginación Eficiente**: Maneja listas de comandos grandes e historial
- **Gestión de Memoria**: Análisis eficiente de JSON y limpieza de recursos
- **Recuperación de Errores**: Reintento automático con retroceso exponencial

**Enfoque Educativo**:
- Ciclo de vida completo de comando desde creación de plantilla hasta ejecución
- Entrega de comandos en tiempo real y reconocimiento
- Simulación de dispositivos usando scripts de IoT Core
- Estructura de tópicos MQTT y flujo de mensajes
- Orientación de decisión Commands vs Shadow vs Jobs
- Mejores prácticas para implementación en producción

**Guía de Solución de Problemas**:

**Problemas Comunes y Soluciones**:

1. **Dispositivo No Recibe Comandos**
   - Verificar que el dispositivo esté suscrito al tópico de solicitud de comando
   - Verificar estado de conexión MQTT
   - Confirmar permisos de certificado y política
   - Verificar que el nombre de cosa coincida con el objetivo
   - Asegurar que el simulador de dispositivo esté ejecutándose ANTES de ejecutar comandos

2. **Errores de Validación de Plantilla**
   - Verificar sintaxis de esquema JSON
   - Verificar complejidad de formato de carga útil (máximo 10KB)
   - Asegurar que los campos requeridos estén definidos
   - Validar tipos y restricciones de parámetros

3. **Fallos de Ejecución de Comando**
   - Verificar que el dispositivo/grupo objetivo exista
   - Verificar permisos de IAM para AWS IoT Commands
   - Confirmar configuración de región de AWS
   - Revisar configuración de tiempo de espera de comando

4. **Estado No Se Actualiza**
   - Verificar que el dispositivo publicó respuesta al tópico correcto
   - Verificar formato de carga útil de respuesta
   - Confirmar que el ID de ejecución coincida
   - Revisar registros del dispositivo para errores

5. **Fallos de Cancelación**
   - Verificar que el comando no esté ya completado
   - Verificar estado de ejecución de comando
   - Confirmar permisos de IAM para cancelación
   - Revisar estado actual del comando

**Flujo de Trabajo de Integración** (Orden Correcto):

⚠️ **CRÍTICO**: El simulador de dispositivo DEBE estar ejecutándose y suscrito a tópicos de comando ANTES de ejecutar comandos. Los comandos son efímeros por defecto - si ningún dispositivo está escuchando cuando se publica el comando, se perderá.

1. **Abrir Terminal 2 PRIMERO** - Copiar credenciales de AWS
2. Navegar al directorio de scripts de IoT Core
3. Ejecutar `certificate_manager.py` para configurar autenticación de dispositivo
4. Ejecutar `mqtt_client_explorer.py` para suscribirse a tópicos de comando
5. **Verificar que el simulador de dispositivo esté listo** - Debería mostrar "Subscribed to command topics"
6. **Ahora abrir Terminal 1** - Ejecutar `manage_commands.py`
7. Crear plantilla de comando
8. Ejecutar comando dirigido al dispositivo
9. **Simulador de Dispositivo** (Terminal 2) recibe comando y muestra carga útil
10. **Simulador de Dispositivo** publica reconocimiento al tópico de respuesta
11. Regresar a Terminal 1 para ver estado de comando actualizado

**Por Qué Este Orden Importa**: Sin sesiones persistentes habilitadas, los mensajes MQTT no se ponen en cola para dispositivos fuera de línea. El dispositivo debe estar activamente suscrito al tópico de comando cuando AWS IoT publica el comando, de lo contrario el comando no será entregado.

**Casos de Uso**:

**Comandos de Emergencia a Nivel de Flota**:
- Enviar comandos de parada de emergencia a todos los vehículos en una región
- Ejecutar retiros de seguridad en toda la flota
- Coordinar respuestas a amenazas de seguridad
- Actualizaciones de configuración en tiempo real a nivel de flota

**Diagnóstico y Control Remoto**:
- Bloquear/desbloquear vehículos remotamente para soporte al cliente
- Ajustar configuración de clima antes de la llegada del cliente
- Activar bocina para asistencia de ubicación del vehículo
- Recopilar datos de diagnóstico bajo demanda

**Patrones de Implementación en Producción**:
- Versionado y gestión de plantillas de comando
- Ejecución de comandos multi-región
- Monitoreo y alertas de ejecución de comandos
- Integración con sistemas de gestión de flotas
- Registro de cumplimiento y auditoría

**Guía de Decisión Commands vs Device Shadow vs Jobs**:

Usar **Commands** cuando:
- Se requiere acción inmediata (tiempo de respuesta en segundos)
- Se necesita control de dispositivo en tiempo real
- Se espera reconocimiento rápido
- El dispositivo debe estar en línea
- Ejemplos: bloquear/desbloquear, activación de bocina, parada de emergencia

Usar **Device Shadow** cuando:
- Se necesita sincronización de estado deseado
- Se requiere soporte de dispositivo fuera de línea
- La consistencia eventual es aceptable
- La persistencia de estado es importante
- Ejemplos: configuración de temperatura, configuración, estado deseado

Usar **Jobs** cuando:
- Se requieren operaciones de larga duración (minutos a horas)
- Se necesitan actualizaciones de firmware
- Gestión de dispositivos por lotes
- El seguimiento de progreso es importante
- Ejemplos: actualizaciones de firmware, rotación de certificados, configuración masiva

**Integración de Servicios de AWS**:
- **AWS IoT Core**: Almacenamiento y ejecución de plantillas de comando
- **AWS IoT Device Management**: Gestión de flotas y orientación
- **AWS Identity and Access Management (IAM)**: Permisos y políticas
- **Amazon CloudWatch**: Monitoreo y registro (opcional)

**Consideraciones de Seguridad**:
- Permisos de IAM para operaciones de comando
- Autenticación de dispositivo basada en certificados
- Autorización basada en políticas para tópicos MQTT
- Cifrado de carga útil de comando en tránsito
- Registro de auditoría para cumplimiento

**Optimización de Costos**:
- Los comandos se cobran por ejecución
- Sin costos de almacenamiento para plantillas de comando
- La orientación eficiente reduce ejecuciones innecesarias
- Monitorear historial de comandos para patrones de uso
- Considerar operaciones por lotes para eficiencia de costos

