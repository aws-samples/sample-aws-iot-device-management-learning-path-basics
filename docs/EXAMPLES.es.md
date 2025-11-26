# Ejemplos de Uso

Este documento proporciona ejemplos prácticos para escenarios comunes de AWS IoT Device Management.

## Ejemplos de Inicio Rápido

### Configuración Básica de Flota
```bash
# 1. Crear infraestructura
python scripts/provision_script.py
# Elegir: SedanVehicle,SUVVehicle
# Versiones: 1.0.0,1.1.0
# Región: North America
# Países: US,CA
# Dispositivos: 100

# 2. Crear grupos dinámicos
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Países: US
# Tipo de cosa: SedanVehicle
# Nivel de batería: <30

# 3. Crear trabajo de actualización de firmware
python scripts/create_job.py
# Seleccionar: grupo USFleet
# Paquete: SedanVehicle v1.1.0

# 4. Simular actualizaciones de dispositivos
python scripts/simulate_job_execution.py
# Tasa de éxito: 85%
# Procesar: TODAS las ejecuciones
```

### Escenario de Reversión de Versión
```bash
# Revertir todos los dispositivos SedanVehicle a la versión 1.0.0
python scripts/manage_packages.py
# Seleccionar: 10. Revertir Versiones de Dispositivos
# Tipo de cosa: SedanVehicle
# Versión objetivo: 1.0.0
# Confirmar: REVERT
```

### Monitoreo de Trabajos
```bash
# Monitorear progreso del trabajo
python scripts/explore_jobs.py
# Opción 1: Listar todos los trabajos
# Opción 4: Listar ejecuciones de trabajo para un trabajo específico
```

## Escenarios Avanzados

### Despliegue Multi-Región
```bash
# Aprovisionar en múltiples regiones
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# Crear 500 dispositivos en América del Norte

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# Crear 300 dispositivos en Europa
```

### Despliegue Escalonado
```bash
# 1. Crear grupo de prueba
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Países: US
# Tipo de cosa: SedanVehicle
# Versiones: 1.0.0
# Nombre personalizado: TestFleet_SedanVehicle_US

# 2. Desplegar primero al grupo de prueba
python scripts/create_job.py
# Seleccionar: TestFleet_SedanVehicle_US
# Paquete: SedanVehicle v1.1.0

# 3. Monitorear despliegue de prueba
python scripts/simulate_job_execution.py
# Tasa de éxito: 95%

# 4. Desplegar a producción después de la validación
python scripts/create_job.py
# Seleccionar: USFleet
# Paquete: SedanVehicle v1.1.0
```

### Mantenimiento Basado en Batería
```bash
# Crear grupo de batería baja
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Método: 1 (Asistente guiado)
# Países: (dejar vacío para todos)
# Tipo de cosa: (dejar vacío para todos)
# Nivel de batería: <20
# Nombre personalizado: LowBatteryDevices

# Crear trabajo de mantenimiento
python scripts/create_job.py
# Seleccionar: LowBatteryDevices
# Paquete: MaintenanceFirmware v2.0.0
```

### Consulta Personalizada Avanzada
```bash
# Crear grupo complejo con consulta personalizada
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Método: 2 (Consulta personalizada)
# Consulta: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# Nombre del grupo: USVehicles_MidBattery
```

### Gestión de Paquetes
```bash
# Crear nuevo paquete y versiones
python scripts/manage_packages.py
# Operación: 1 (Crear Paquete)
# Nombre del paquete: TestVehicle

# Agregar versión con carga a S3
# Operación: 2 (Crear Versión)
# Nombre del paquete: TestVehicle
# Versión: 2.0.0

# Inspeccionar detalles del paquete
# Operación: 4 (Describir Paquete)
# Nombre del paquete: TestVehicle
```

## Flujos de Trabajo de Desarrollo

### Prueba de Nuevo Firmware
```bash
# 1. Aprovisionar entorno de prueba
python scripts/provision_script.py
# Tipos de cosa: TestSensor
# Versiones: 1.0.0,2.0.0-beta
# Países: US
# Dispositivos: 10

# 2. Crear grupo de prueba beta
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Tipo de cosa: TestSensor
# Versiones: 1.0.0
# Nombre personalizado: BetaTestGroup

# 3. Desplegar firmware beta
python scripts/create_job.py
# Seleccionar: BetaTestGroup
# Paquete: TestSensor v2.0.0-beta

# 4. Simular con alta tasa de fallo para pruebas
python scripts/simulate_job_execution.py
# Tasa de éxito: 60%

# 5. Analizar resultados
python scripts/explore_jobs.py
# Opción 4: Listar ejecuciones de trabajo
```

### Limpieza Después de Pruebas
```bash
# Limpiar recursos de prueba
python scripts/cleanup_script.py
# Opción 1: TODOS los recursos
# Confirmar: DELETE
```

## Patrones de Gestión de Flota

### Despliegue Geográfico
```bash
# Aprovisionar por continente
python scripts/provision_script.py
# Continente: 1 (América del Norte)
# Países: 3 (primeros 3 países)
# Dispositivos: 1000

# Crear grupos específicos por país (creados automáticamente como USFleet, CAFleet, MXFleet)
# Desplegar firmware específico de región
python scripts/create_job.py
# Seleccionar: USFleet,CAFleet
# Paquete: RegionalFirmware v1.2.0
```

### Gestión de Tipos de Dispositivos
```bash
# Aprovisionar múltiples tipos de vehículos
python scripts/provision_script.py
# Tipos de cosa: SedanVehicle,SUVVehicle,TruckVehicle
# Versiones: 1.0.0,1.1.0,2.0.0
# Dispositivos: 500

# Crear grupos dinámicos específicos por tipo
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Tipo de cosa: TruckVehicle
# Países: US,CA
# Nombre personalizado: NorthAmericaTrucks

# Desplegar firmware específico para camiones
python scripts/create_job.py
# Seleccionar: NorthAmericaTrucks
# Paquete: TruckVehicle v2.0.0
```

### Programación de Mantenimiento
```bash
# Encontrar dispositivos que necesitan actualizaciones
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Tipo de cosa: SedanVehicle
# Versiones: 1.0.0  # Versión antigua
# Nombre personalizado: SedanVehicle_NeedsUpdate

# Programar despliegue en ventana de mantenimiento
python scripts/create_job.py
# Seleccionar: SedanVehicle_NeedsUpdate
# Paquete: SedanVehicle v1.1.0

# Monitorear progreso del despliegue
python scripts/explore_jobs.py
# Opción 1: Listar todos los trabajos (verificar estado)
```

## Ejemplos de Solución de Problemas

### Recuperación de Trabajo Fallido
```bash
# 1. Verificar estado del trabajo
python scripts/explore_jobs.py
# Opción 2: Explorar trabajo específico
# Ingresar ID de trabajo con fallos

# 2. Verificar fallos de dispositivos individuales
python scripts/explore_jobs.py
# Opción 3: Explorar ejecución de trabajo
# Ingresar ID de trabajo y nombre del dispositivo fallido

# 3. Revertir dispositivos fallidos
python scripts/manage_packages.py
# Seleccionar: 10. Revertir Versiones de Dispositivos
# Tipo de cosa: SedanVehicle
# Versión objetivo: 1.0.0  # Versión anterior funcional
```

### Verificación de Estado de Dispositivos
```bash
# Verificar versiones actuales de firmware
python scripts/manage_dynamic_groups.py
# Operación: 1 (Crear)
# Tipo de cosa: SedanVehicle
# Versiones: 1.1.0
# Nombre personalizado: SedanVehicle_v1_1_0_Check

# Verificar membresía del grupo (debe coincidir con el conteo esperado)
python scripts/explore_jobs.py
# Usar para verificar estados de dispositivos
```

### Pruebas de Rendimiento
```bash
# Probar con gran cantidad de dispositivos
python scripts/provision_script.py
# Dispositivos: 5000

# Probar rendimiento de ejecución de trabajos
python scripts/simulate_job_execution.py
# Procesar: TODOS
# Tasa de éxito: 90%
# Monitorear tiempo de ejecución y TPS
```

## Ejemplos Específicos de Entorno

### Entorno de Desarrollo
```bash
# Escala pequeña para desarrollo
python scripts/provision_script.py
# Tipos de cosa: DevSensor
# Versiones: 1.0.0-dev
# Países: US
# Dispositivos: 5
```

### Entorno de Staging
```bash
# Escala media para staging
python scripts/provision_script.py
# Tipos de cosa: SedanVehicle,SUVVehicle
# Versiones: 1.0.0,1.1.0-rc
# Países: US,CA
# Dispositivos: 100
```

### Entorno de Producción
```bash
# Escala grande para producción
python scripts/provision_script.py
# Tipos de cosa: SedanVehicle,SUVVehicle,TruckVehicle
# Versiones: 1.0.0,1.1.0,1.2.0
# Continente: 1 (América del Norte)
# Países: TODOS
# Dispositivos: 10000
```

## Ejemplos de Integración

### Integración con Pipeline CI/CD
```bash
# Verificación de sintaxis (automatizada)
python scripts/check_syntax.py

# Pruebas automatizadas
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### Integración de Monitoreo
```bash
# Exportar métricas de trabajos
python scripts/explore_jobs.py --export-json > job_status.json

# Verificar salud del despliegue
python scripts/explore_jobs.py --health-check
```

## Ejemplos de Mejores Prácticas

### Despliegue Gradual
1. Comenzar con 5% de la flota (grupo de prueba)
2. Monitorear durante 24 horas
3. Expandir a 25% si es exitoso
4. Despliegue completo después de la validación

### Estrategia de Reversión
1. Siempre probar el procedimiento de reversión
2. Mantener versiones anteriores de firmware disponibles
3. Monitorear salud del dispositivo post-despliegue
4. Tener disparadores de reversión automatizados

### Gestión de Recursos
1. Usar script de limpieza después de pruebas
2. Monitorear costos de AWS
3. Limpiar versiones antiguas de firmware
4. Eliminar grupos de cosas no utilizados
