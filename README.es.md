# AWS IoT Device Management - Ruta de Aprendizaje - Fundamentos

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

Una demostración integral de las capacidades de AWS IoT Device Management que incluye aprovisionamiento de dispositivos, actualizaciones por aire (OTA), gestión de trabajos y operaciones de flota utilizando scripts modernos de Python con integración nativa del AWS SDK (boto3).

## 👥 Audiencia Objetivo

**Audiencia Principal:** Desarrolladores de IoT, arquitectos de soluciones, ingenieros DevOps que trabajan con flotas de dispositivos AWS IoT

**Prerrequisitos:** Conocimiento intermedio de AWS, fundamentos de AWS IoT Core, fundamentos de Python, uso de línea de comandos

**Nivel de Aprendizaje:** Nivel asociado con enfoque práctico para la gestión de dispositivos a escala

## 🎯 Objetivos de Aprendizaje

- **Gestión del Ciclo de Vida de Dispositivos**: Aprovisionar dispositivos IoT con tipos de cosas y atributos apropiados
- **Organización de Flotas**: Crear grupos de cosas estáticos y dinámicos para la gestión de dispositivos
- **Actualizaciones OTA**: Implementar actualizaciones de firmware usando AWS IoT Jobs con integración de Amazon S3
- **Gestión de Paquetes**: Manejar múltiples versiones de firmware con actualizaciones automáticas de shadow
- **Ejecución de Trabajos**: Simular comportamiento realista de dispositivos durante actualizaciones de firmware
- **Control de Versiones**: Revertir dispositivos a versiones anteriores de firmware
- **Limpieza de Recursos**: Gestionar adecuadamente los recursos de AWS para evitar costos innecesarios

## 📋 Prerrequisitos

- **Cuenta de AWS** con permisos para AWS IoT, Amazon S3 y AWS Identity and Access Management (IAM)
- **Credenciales de AWS** configuradas (vía `aws configure`, variables de entorno o roles IAM)
- **Python 3.10+** con pip y las librerías de Python boto3, colorama y requests (revisar archivo requirements.txt)
- **Git** para clonar el repositorio

## 💰 Análisis de Costos

**Este proyecto crea recursos reales de AWS que generarán cargos.**

| Servicio | Uso | Costo Estimado (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1,000 mensajes, 100-10,000 dispositivos | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2,000 operaciones de shadow | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 ejecuciones de trabajos | $0.01 - $0.10 |
| **Amazon S3** | Almacenamiento + solicitudes para firmware | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | Consultas e indexación de dispositivos | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | Operaciones de paquetes | $0.01 - $0.05 |
| **AWS Identity and Access Management (IAM)** | Gestión de roles/políticas | $0.00 |
| **Total Estimado** | **Sesión de demostración completa** | **$0.27 - $2.40** |

**Factores de Costo:**
- Cantidad de dispositivos (100-10,000 configurable)
- Frecuencia de ejecución de trabajos
- Operaciones de actualización de shadow
- Duración de almacenamiento en Amazon S3

**Gestión de Costos:**
- ✅ El script de limpieza elimina todos los recursos
- ✅ Recursos de demostración de corta duración
- ✅ Escala configurable (empezar pequeño)
- ⚠️ **Ejecutar script de limpieza al terminar**

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
python scripts/provision_script.py        # Crear infraestructura
python scripts/manage_dynamic_groups.py   # Crear grupos de dispositivos
python scripts/manage_packages.py         # Gestionar paquetes de firmware
python scripts/create_job.py              # Desplegar actualizaciones de firmware
python scripts/simulate_job_execution.py  # Simular actualizaciones de dispositivos
python scripts/explore_jobs.py            # Monitorear progreso de trabajos
python scripts/cleanup_script.py          # Limpiar recursos
```

## 📚 Scripts Disponibles

| Script | Propósito | Características Clave | Documentación |
|--------|---------|-------------|---------------|
| **provision_script.py** | Configuración completa de infraestructura | Crea dispositivos, grupos, paquetes, almacenamiento Amazon S3 | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | Gestionar grupos dinámicos de dispositivos | Crear, listar, eliminar con validación de Fleet Indexing | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | Gestión integral de paquetes | Crear paquetes/versiones, integración Amazon S3, seguimiento de dispositivos con estado de reversión individual | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | Crear trabajos de actualización OTA | Orientación multi-grupo, URLs prefirmadas | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | Simular actualizaciones de dispositivos | Descargas reales de Amazon S3, preparación de plan visible, seguimiento de progreso por dispositivo | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | Monitorear progreso de trabajos | Exploración interactiva de trabajos y resolución de problemas | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **cleanup_script.py** | Eliminar recursos de AWS | Limpieza selectiva, gestión de costos | [📖 Detalles](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **Documentación Detallada**: Ver [docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md) para información completa de scripts.

## ⚙️ Configuración

**Variables de Entorno** (opcional):
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=es                    # Establecer idioma predeterminado (en, es, fr, etc.)
```

**Características de Scripts**:
- **AWS SDK Nativo**: Usa boto3 para mejor rendimiento y confiabilidad
- **Soporte Multi-idioma**: Selección interactiva de idioma con respaldo a inglés
- **Modo Debug**: Muestra todas las llamadas y respuestas de la API de AWS
- **Procesamiento Paralelo**: Operaciones concurrentes cuando no está en modo debug
- **Limitación de Velocidad**: Cumplimiento automático de limitación de API de AWS
- **Seguimiento de Progreso**: Estado de operación en tiempo real

## 🌍 Soporte de Internacionalización

Todos los scripts soportan múltiples idiomas con detección automática de idioma y selección interactiva.

**Selección de Idioma**:
- **Interactiva**: Los scripts solicitan selección de idioma en la primera ejecución
- **Variable de Entorno**: Establecer `AWS_IOT_LANG=es` para omitir selección de idioma
- **Respaldo**: Automáticamente vuelve al inglés para traducciones faltantes

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
python scripts/cleanup_script.py          # 7. Limpiar recursos
```

**Operaciones Individuales**:
```bash
python scripts/manage_packages.py         # Gestión de paquetes y versiones
python scripts/manage_dynamic_groups.py   # Operaciones de grupos dinámicos
```

> 📖 **Más Ejemplos**: Ver [docs/EXAMPLES.md](docs/EXAMPLES.md) para escenarios de uso detallados.

## 🛠️ Resolución de Problemas

**Problemas Comunes**:
- **Credenciales**: Configurar credenciales de AWS vía `aws configure`, variables de entorno o roles IAM
- **Permisos**: Asegurar que el usuario IAM tenga permisos para AWS IoT, Amazon S3 e IAM
- **Límites de Velocidad**: Los scripts manejan automáticamente con limitación inteligente
- **Red**: Asegurar conectividad a las APIs de AWS

**Modo Debug**: Habilitar en cualquier script para resolución detallada de problemas
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **Resolución Detallada de Problemas**: Ver [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para soluciones completas.

## 🧹 Importante: Limpieza de Recursos

**Siempre ejecutar limpieza al terminar para evitar cargos continuos:**
```bash
python scripts/cleanup_script.py
# Elegir opción 1: TODOS los recursos
# Escribir: DELETE
```

**Lo que elimina la limpieza:**
- Todos los dispositivos y grupos de AWS IoT
- Buckets de Amazon S3 y archivos de firmware
- Paquetes de software de AWS IoT
- Roles y políticas de IAM
- Configuración de Fleet Indexing

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

1. **Crear Directorio de Idioma**:
   ```bash
   mkdir i18n/{language_code}  # ej., i18n/es para español
   ```

2. **Copiar Plantillas en Inglés**:
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **Traducir Archivos de Mensajes**:
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

4. **Actualizar Selector de Idioma** (si se agrega nuevo idioma):
   Agregar su idioma a `i18n/language_selector.py`:
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Su Nombre de Idioma",  # Agregar nueva opción
           # ... idiomas existentes
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "su_codigo",  # Agregar nuevo código de idioma
       # ... mapeos existentes
   }
   ```

5. **Probar Traducción**:
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**Pautas de Traducción**:
- **Preservar Formato**: Mantener emojis, colores y caracteres especiales
- **Mantener Marcadores**: Conservar marcadores `{}` para contenido dinámico
- **Términos Técnicos**: Mantener nombres de servicios AWS en inglés
- **Adaptación Cultural**: Adaptar ejemplos y referencias apropiadamente
- **Consistencia**: Usar terminología consistente en todos los archivos

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

**Probar Su Traducción**:
```bash
# Probar script específico con su idioma
export AWS_IOT_LANG=su_codigo_de_idioma
python scripts/manage_packages.py

# Probar comportamiento de respaldo (usar idioma no existente)
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # Debería volver al inglés
```

## 📚 Documentación

- **[Scripts Detallados](docs/DETAILED_SCRIPTS.md)** - Documentación completa de scripts
- **[Ejemplos de Uso](docs/EXAMPLES.md)** - Escenarios prácticos y flujos de trabajo
- **[Resolución de Problemas](docs/TROUBLESHOOTING.md)** - Problemas comunes y soluciones

## 📄 Licencia

Licencia MIT Sin Atribución - ver archivo [LICENSE](LICENSE) para detalles.

## 🏷️ Etiquetas

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot`