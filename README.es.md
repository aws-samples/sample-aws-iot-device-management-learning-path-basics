# AWS IoT Device Management - Ruta de Aprendizaje - Fundamentos

## 🌍 Idiomas Disponibles

| Language | README |
|----------|---------|
| 🇺🇸 English | [README.md](README.md) |
| 🇪🇸 Español | [README.es.md](README.es.md) |
| 🇯🇵 日本語 | [README.ja.md](README.ja.md) |
| 🇰🇷 한국어 | [README.ko.md](README.ko.md) |
| 🇧🇷 Português | [README.pt.md](README.pt.md) |
| 🇨🇳 中文 | [README.zh.md](README.zh.md) |
| 🇩🇪 Deutsch | [README.de.md](README.de.md) |
| 🇮🇹 Italiano | [README.it.md](README.it.md) |
| 🇫🇷 Français | [README.fr.md](README.fr.md) |

---

Una demostración completa de las capacidades de AWS IoT Device Management que incluye aprovisionamiento de dispositivos, actualizaciones por aire (OTA), gestión de trabajos y operaciones de flota usando scripts modernos de Python con integración nativa del AWS SDK (boto3).

## 👥 Audiencia Objetivo

**Audiencia Principal:** Desarrolladores de IoT, arquitectos de soluciones, ingenieros DevOps que trabajan con flotas de dispositivos AWS IoT

**Prerrequisitos:** Conocimiento intermedio de AWS, fundamentos de AWS IoT Core, fundamentos de Python, y uso de línea de comandos

**Nivel de Aprendizaje:** Nivel asociado con enfoque práctico para gestionar dispositivos a escala

## 🎯 Objetivos de Aprendizaje

- **Gestión del Ciclo de Vida de Dispositivos**: Aprovisiona dispositivos IoT con tipos de cosas y atributos apropiados
- **Organización de Flotas**: Crea grupos de cosas estáticos y dinámicos para gestionar dispositivos
- **Actualizaciones OTA**: Implementa actualizaciones de firmware usando AWS IoT Jobs con integración de Amazon S3
- **Gestión de Paquetes**: Maneja múltiples versiones de firmware con actualizaciones automáticas de shadow
- **Ejecución de Trabajos**: Simula comportamiento realista de dispositivos durante actualizaciones de firmware
- **Control de Versiones**: Revierte dispositivos a versiones anteriores de firmware
- **Comandos Remotos**: Envía comandos en tiempo real a dispositivos usando AWS IoT Commands
- **Registro Masivo**: Registra cientos o miles de dispositivos eficientemente usando aprovisionamiento a escala de manufactura
- **Limpieza de Recursos**: Gestiona adecuadamente los recursos de AWS para evitar costos innecesarios

## 📋 Prerrequisitos

- **Cuenta de AWS** con permisos para AWS IoT, Amazon S3 y AWS Identity and Access Management (IAM)
- **Credenciales de AWS** configuradas (vía `aws configure`, variables de entorno o roles AWS Identity and Access Management (IAM))
- **Python 3.10+** con pip y las librerías de Python boto3, colorama y requests (revisar archivo requirements.txt)
- **Git** para clonar el repositorio

## 💰 Análisis de Costos

**Este proyecto crea recursos reales de AWS que generarán cargos.**

| Servicio | Uso | Costo Estimado (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1,000 mensajes, 100-10,000 dispositivos | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2,000 operaciones de shadow | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 ejecuciones de trabajos | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50 ejecuciones de comandos | $0.01 - $0.05 |
| **Amazon S3** | Almacenamiento + solicitudes para firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Consultas e indexación de dispositivos | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Operaciones de paquetes | $0.01 - $0.05 |
| **AWS IoT Device Management Bulk Registration** | Aprovisionamiento masivo de dispositivos | $0.05 - $0.50 |
| **AWS Identity and Access Management (IAM)** | Gestión de roles/políticas | $0.00 |
| **Total Estimado** | **Sesión de demostración completa** | **$0.33 - $2.95** |

**Factores de Costo:**
- Cantidad de dispositivos (100-10,000 configurable)
- Frecuencia de ejecución de trabajos
- Operaciones de actualización de shadow
- Duración de almacenamiento en Amazon S3

**Gestión de Costos:**
- ✅ El script de limpieza elimina todos los recursos
- ✅ Recursos de demostración de corta duración
- ✅ Escala configurable (puedes empezar pequeño)
- ⚠️ **Recuerda ejecutar el script de limpieza al terminar**

**📊 Monitorear costos:** [Panel de Facturación de AWS](https://console.aws.amazon.com/billing/)

## 🚀 Inicio Rápido

```bash
# 1. Clonar y configurar
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar AWS
aws configure

# 3. Flujo de trabajo completo (secuencia recomendada)
python scripts/provision_script.py        # Crear infraestructura con etiquetado
python scripts/manage_dynamic_groups.py   # Crear grupos de dispositivos
python scripts/manage_packages.py         # Gestionar paquetes de firmware
python scripts/create_job.py              # Desplegar actualizaciones de firmware
python scripts/simulate_job_execution.py  # Simular actualizaciones de dispositivos
python scripts/explore_jobs.py            # Monitorear progreso de trabajos
python scripts/manage_commands.py         # Enviar comandos en tiempo real a dispositivos
python scripts/manage_bulk_provisioning.py # Registro masivo de dispositivos (escala de manufactura)
python scripts/cleanup_script.py          # Limpieza segura con identificación de recursos
```

## 📚 Scripts Disponibles

| Script | Propósito | Características Clave |
|--------|---------|-------------|
| **provision_script.py** | Configuración completa de infraestructura | Crea dispositivos, grupos, paquetes y almacenamiento Amazon S3 |
| **manage_dynamic_groups.py** | Gestiona grupos dinámicos de dispositivos | Crea, lista y elimina con validación de Fleet Indexing |
| **manage_packages.py** | Gestión completa de paquetes | Crea paquetes/versiones, integración Amazon S3, seguimiento de dispositivos con estado de reversión individual |
| **create_job.py** | Crea trabajos de actualización OTA | Orientación multi-grupo, URLs prefirmadas |
| **simulate_job_execution.py** | Simula actualizaciones de dispositivos | Descargas reales de Amazon S3, preparación de plan visible, seguimiento de progreso por dispositivo |
| **explore_jobs.py** | Monitorea y gestiona trabajos | Exploración interactiva de trabajos, cancelación, eliminación y análisis |
| **manage_commands.py** | Envía comandos en tiempo real a dispositivos | Gestión de plantillas, ejecución de comandos, monitoreo de estado, seguimiento de historial |
| **manage_bulk_provisioning.py** | Registro masivo de dispositivos | Aprovisionamiento a escala de manufactura, generación de certificados, monitoreo de tareas |
| **cleanup_script.py** | Elimina recursos de AWS | Limpieza selectiva, gestión de costos |

## ⚙️ Configuración

**Variables de Entorno** (opcional):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=es                    # Establecer idioma predeterminado (en, es, fr, etc.)
```

**Características de Scripts**:
- **AWS SDK Nativo**: Usa boto3 para mejor rendimiento y confiabilidad
- **Soporte Multi-idioma**: Selección interactiva de idioma con respaldo a inglés
- **Modo Debug**: Te muestra todas las llamadas y respuestas de la API de AWS
- **Procesamiento Paralelo**: Operaciones concurrentes cuando no está en modo debug
- **Limitación de Velocidad**: Cumplimiento automático de limitación de API de AWS
- **Seguimiento de Progreso**: Estado de operación en tiempo real
- **Etiquetado de Recursos**: Etiquetas automáticas de taller para limpieza segura
- **Nomenclatura Configurable**: Puedes personalizar los patrones de nomenclatura de dispositivos

### Etiquetado de Recursos

Todos los scripts del taller etiquetan automáticamente los recursos creados con `workshop=learning-aws-iot-dm-basics` para identificación segura durante la limpieza. Esto asegura que solo se eliminen los recursos que creaste en el taller.

**Recursos Etiquetados**:
- Tipos de Cosas de IoT
- Grupos de Cosas de IoT (estáticos y dinámicos)
- Paquetes de Software de IoT
- Trabajos de IoT
- Buckets de Amazon S3
- Roles de AWS Identity and Access Management (IAM)

**Recursos No Etiquetados** (identificados por patrones de nomenclatura):
- Cosas de IoT (usan convenciones de nomenclatura)
- Certificados (identificados por asociación)
- Shadows de Cosas (identificados por asociación)

### Configuración de Nomenclatura de Dispositivos

Puedes personalizar los patrones de nomenclatura de dispositivos con el parámetro `--things-prefix`:

```bash
# Nomenclatura predeterminada: Vehicle-VIN-001, Vehicle-VIN-002, etc.
python scripts/provision_script.py

# Prefijo personalizado: Fleet-Device-001, Fleet-Device-002, etc.
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# Prefijo personalizado para limpieza (debe coincidir con el prefijo de aprovisionamiento)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**Requisitos del Prefijo**:
- Solo caracteres alfanuméricos, guiones, guiones bajos y dos puntos
- Máximo 20 caracteres
- Los números secuenciales se rellenan automáticamente con ceros (001-999)

## 🌍 Soporte de Internacionalización

Todos los scripts soportan múltiples idiomas con detección automática de idioma y selección interactiva.

**Selección de Idioma**:
- **Interactiva**: Los scripts te piden que selecciones el idioma en la primera ejecución
- **Variable de Entorno**: Puedes establecer `AWS_IOT_LANG=es` para omitir la selección de idioma
- **Respaldo**: Automáticamente vuelve al inglés si faltan traducciones

**Idiomas Soportados**:
- **Inglés (en)**: Traducciones completas ✅
- **Español (es)**: Listo para traducciones
- **Japonés (ja)**: Listo para traducciones
- **Chino (zh-CN)**: Listo para traducciones
- **Portugués (pt-BR)**: Listo para traducciones
- **Coreano (ko)**: Listo para traducciones

**Ejemplos de Uso**:
```bash
# Establecer idioma vía variable de entorno (recomendado para automatización)
export AWS_IOT_LANG=es
python scripts/provision_script.py

# Códigos de idioma alternativos soportados
export AWS_IOT_LANG=spanish    # o "es", "español"
export AWS_IOT_LANG=japanese   # o "ja", "日本語", "jp"
export AWS_IOT_LANG=chinese    # o "zh-cn", "中文", "zh"
export AWS_IOT_LANG=portuguese # o "pt", "pt-br", "português"
export AWS_IOT_LANG=korean     # o "ko", "한국어", "kr"

# Selección interactiva de idioma (comportamiento predeterminado)
python scripts/manage_packages.py
# Salida: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# Todo el texto dirigido al usuario aparecerá en el idioma seleccionado
```

**Categorías de Mensajes**:
- **Elementos de UI**: Títulos, encabezados, separadores
- **Solicitudes de Usuario**: Solicitudes de entrada, confirmaciones
- **Mensajes de Estado**: Actualizaciones de progreso, notificaciones de éxito/fallo
- **Mensajes de Error**: Descripciones detalladas de errores y resolución de problemas
- **Salida de Debug**: Información de llamadas API y respuestas
- **Contenido de Aprendizaje**: Momentos educativos y explicaciones

## 📖 Ejemplos de Uso

**Flujo de Trabajo Completo** (secuencia recomendada):
```bash
python scripts/provision_script.py        # 1. Crear infraestructura
python scripts/manage_dynamic_groups.py   # 2. Crear grupos de dispositivos
python scripts/manage_packages.py         # 3. Gestionar paquetes de firmware
python scripts/create_job.py              # 4. Desplegar actualizaciones de firmware
python scripts/simulate_job_execution.py  # 5. Simular actualizaciones de dispositivos
python scripts/explore_jobs.py            # 6. Monitorear progreso de trabajos
python scripts/manage_commands.py         # 7. Enviar comandos en tiempo real a dispositivos
python scripts/manage_bulk_provisioning.py # 8. Registro masivo de dispositivos (escala de manufactura)
python scripts/cleanup_script.py          # 9. Limpiar recursos
```

**Operaciones Individuales**:
```bash
python scripts/manage_packages.py         # Gestión de paquetes y versiones
python scripts/manage_dynamic_groups.py   # Operaciones de grupos dinámicos
```

## 🔧 Resolución de Problemas

**Problemas Comunes**:
- **Credenciales**: Configura tus credenciales de AWS vía `aws configure`, variables de entorno o roles AWS Identity and Access Management (IAM)
- **Permisos**: Asegúrate de que tu usuario AWS Identity and Access Management (IAM) tenga permisos para AWS IoT, Amazon S3 e AWS Identity and Access Management (IAM)
- **Límites de Velocidad**: Los scripts manejan esto automáticamente con limitación inteligente
- **Red**: Asegúrate de tener conectividad a las APIs de AWS

**Modo Debug**: Puedes habilitarlo en cualquier script para resolución detallada de problemas
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **Resolución Detallada de Problemas**: Consulta [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para soluciones completas.

## 🧹 Importante: Limpieza de Recursos

**Recuerda siempre ejecutar la limpieza al terminar para evitar cargos continuos:**
```bash
python scripts/cleanup_script.py
# Elige la opción 1: TODOS los recursos
# Escribe: DELETE
```

### Características de Limpieza Segura

El script de limpieza utiliza múltiples métodos de identificación para asegurar que solo se eliminen los recursos del taller:

1. **Identificación Basada en Etiquetas** (Primaria): Verifica la etiqueta `workshop=learning-aws-iot-dm-basics`
2. **Coincidencia de Patrones de Nomenclatura** (Secundaria): Busca convenciones de nomenclatura conocidas del taller
3. **Basada en Asociación** (Terciaria): Identifica recursos vinculados a recursos del taller

**Opciones de Limpieza**:
```bash
# Limpieza estándar (interactiva)
python scripts/cleanup_script.py

# Modo de prueba (vista previa sin eliminar)
python scripts/cleanup_script.py --dry-run

# Prefijo de dispositivo personalizado (debe coincidir con el prefijo de aprovisionamiento)
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# Prueba con prefijo personalizado
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**Lo que elimina la limpieza:**
- Todos los dispositivos y grupos de AWS IoT (con etiquetas de taller o patrones de nomenclatura coincidentes)
- Buckets de Amazon S3 y archivos de firmware (etiquetados)
- Paquetes de software de AWS IoT (etiquetados)
- Plantillas de comandos de AWS IoT (etiquetadas)
- Roles y políticas de AWS Identity and Access Management (IAM) (etiquetados)
- Configuración de Fleet Indexing
- Certificados y shadows asociados

**Características de Seguridad**:
- Los recursos que no son del taller se omiten automáticamente
- El resumen detallado te muestra los recursos eliminados y omitidos
- El modo debug te muestra el método de identificación para cada recurso
- El modo de prueba te permite ver una vista previa antes de la eliminación real

## 🔧 Guía del Desarrollador: Agregar Nuevos Idiomas

**Estructura de Archivos de Mensajes**:
```
i18n/
├── common.json                    # Mensajes compartidos entre todos los scripts
├── loader.py                      # Utilidad de carga de mensajes
├── language_selector.py           # Interfaz de selección de idioma
└── {language_code}/               # Directorio específico del idioma
    ├── provision_script.json     # Mensajes específicos del script
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**Agregar un Nuevo Idioma**:

1. **Crea el Directorio de Idioma**:
   ```bash
   mkdir i18n/{language_code}  # ej., i18n/es para español
   ```

2. **Copia las Plantillas en Inglés**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Traduce los Archivos de Mensajes**:
   Cada archivo JSON contiene mensajes categorizados:
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 ¿Habilitar modo debug? [y/N]: ",
       "operation_choice": "Ingrese opción [1-11]: ",
       "continue_operation": "¿Continuar? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Modo debug habilitado",
       "package_created": "✅ Paquete creado exitosamente",
       "clients_initialized": "🔍 DEBUG: Configuración del cliente:"
     },
     "errors": {
       "invalid_choice": "❌ Opción inválida. Por favor ingrese 1-11",
       "package_not_found": "❌ Paquete '{}' no encontrado",
       "api_error": "❌ Error en {} {}: {}"
     },
     "debug": {
       "api_call": "📤 Llamada API: {}",
       "api_response": "📤 Respuesta API:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Seleccionar Operación:",
       "create_package": "1. Crear Paquete de Software",
       "goodbye": "👋 ¡Gracias por usar Package Manager!"
     },
     "learning": {
       "package_management_title": "Gestión de Paquetes de Software",
       "package_management_description": "Contenido educativo..."
     }
   }
   ```

4. **Actualiza el Selector de Idioma** (si agregas un nuevo idioma):
   Agrega tu idioma a `i18n/language_selector.py`:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Tu Nombre de Idioma",  # Agrega tu nueva opción
           # ... idiomas existentes
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "tu_codigo",  # Agrega tu nuevo código de idioma
       # ... mapeos existentes
   }
   ```

5. **Prueba tu Traducción**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Pautas de Traducción**:
- **Preservar Formato**: Mantén los emojis, colores y caracteres especiales
- **Mantener Marcadores**: Conserva los marcadores `{}` para contenido dinámico
- **Términos Técnicos**: Mantén los nombres de servicios AWS en inglés
- **Adaptación Cultural**: Adapta los ejemplos y referencias apropiadamente
- **Consistencia**: Usa terminología consistente en todos los archivos

**Patrones de Claves de Mensajes**:
- `title`: Título principal del script
- `separator`: Separadores visuales y divisores
- `prompts.*`: Solicitudes de entrada de usuario y confirmaciones
- `status.*`: Actualizaciones de progreso y resultados de operaciones
- `errors.*`: Mensajes de error y advertencias
- `debug.*`: Salida de debug e información de API
- `ui.*`: Elementos de interfaz de usuario (menús, etiquetas, botones)
- `results.*`: Resultados de operaciones y visualización de datos
- `learning.*`: Contenido educativo y explicaciones
- `warnings.*`: Mensajes de advertencia y avisos importantes
- `explanations.*`: Contexto adicional y texto de ayuda

**Prueba tu Traducción**:
```bash
# Prueba un script específico con tu idioma
export AWS_IOT_LANG=tu_codigo_de_idioma
python scripts/manage_packages.py

# Prueba el comportamiento de respaldo (usa un idioma que no existe)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Debería volver al inglés
```

## 📚 Documentación

- **[Resolución de Problemas](docs/TROUBLESHOOTING.md)** - Problemas comunes y soluciones

## 📄 Licencia

Licencia MIT Sin Atribución - ver archivo [LICENSE](LICENSE) para detalles.

## 🏷️ Etiquetas

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot`