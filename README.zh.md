# AWS IoT 设备管理 - 学习路径 - 基础

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

全面演示 AWS IoT 设备管理功能，包括设备配置、空中下载 (OTA) 更新、作业管理和车队操作，使用现代 Python 脚本与原生 AWS SDK (boto3) 集成。

## 👥 目标受众

**主要受众：** IoT 开发人员、解决方案架构师、使用 AWS IoT 设备车队的 DevOps 工程师

**先决条件：** 中级 AWS 知识、AWS IoT Core 基础知识、Python 基础知识、命令行使用

**学习级别：** 具有大规模设备管理实践方法的助理级别

## 🎯 学习目标

- **设备生命周期管理**：使用适当的事物类型和属性配置 IoT 设备
- **车队组织**：创建静态和动态事物组进行设备管理
- **OTA 更新**：使用 AWS IoT Jobs 与 Amazon S3 集成实现固件更新
- **包管理**：处理多个固件版本并自动更新影子
- **作业执行**：在固件更新期间模拟真实的设备行为
- **版本控制**：将设备回滚到以前的固件版本
- **远程命令**：使用 AWS IoT Commands 向设备发送实时命令
- **资源清理**：正确管理 AWS 资源以避免不必要的成本

## 📋 先决条件

- 具有 AWS IoT、Amazon S3 和 AWS Identity and Access Management (IAM) 权限的 **AWS 账户**
- 已配置的 **AWS 凭证**（通过 `aws configure`、环境变量或 IAM 角色）
- **Python 3.10+** 以及 pip 和 boto3、colorama 和 requests Python 库（检查 requirements.txt 文件）
- 用于克隆存储库的 **Git**

## 💰 成本分析

**此项目创建真实的 AWS 资源，将产生费用。**

| 服务 | 使用情况 | 预估成本 (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~1,000 条消息，100-10,000 台设备 | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | ~200-2,000 次影子操作 | $0.10 - $1.00 |
| **AWS IoT Jobs** | ~10-100 次作业执行 | $0.01 - $0.10 |
| **AWS IoT Commands** | ~10-50 次命令执行 | $0.01 - $0.05 |
| **Amazon S3** | 固件存储 + 请求 | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | 设备查询和索引 | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | 包操作 | $0.01 - $0.05 |
| **AWS Identity and Access Management (IAM)** | 角色/策略管理 | $0.00 |
| **总预估** | **完整演示会话** | **$0.28 - $2.45** |

**成本因素：**
- 设备数量（可配置 100-10,000）
- 作业执行频率
- 影子更新操作
- Amazon S3 存储持续时间

**成本管理：**
- ✅ 清理脚本删除所有资源
- ✅ 短期演示资源
- ✅ 可配置规模（从小开始）
- ⚠️ **完成后运行清理脚本**

**📊 监控成本：** [AWS 账单控制台](https://console.aws.amazon.com/billing/)

## 🚀 快速开始

```bash
# 1. 克隆和设置
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # Windows 上：venv\Scripts\activate
pip install -r requirements.txt

# 2. 配置 AWS
aws configure

# 3. 完整工作流程（推荐顺序）
python scripts/provision_script.py        # 创建带标签的基础设施
python scripts/manage_dynamic_groups.py   # 创建设备组
python scripts/manage_packages.py         # 管理固件包
python scripts/create_job.py              # 部署固件更新
python scripts/simulate_job_execution.py  # 模拟设备更新
python scripts/explore_jobs.py            # 监控作业进度
python scripts/manage_commands.py         # 向设备发送实时命令
python scripts/cleanup_script.py          # 通过资源识别进行安全清理
```

## 📚 可用脚本

| 脚本 | 目的 | 主要功能 | 文档 |
|--------|---------|-------------|---------------|
| **provision_script.py** | 完整基础设施设置 | 创建设备、组、包、Amazon S3 存储 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | 管理动态设备组 | 使用 Fleet Indexing 验证创建、列出、删除 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | 综合包管理 | 创建包/版本、Amazon S3 集成、具有个别回滚状态的设备跟踪 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | 创建 OTA 更新作业 | 多组目标、预签名 URL | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | 模拟设备更新 | 真实 Amazon S3 下载、可见计划准备、每设备进度跟踪 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | 监控和管理作业 | 交互式作业探索、取消、删除和分析 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **manage_commands.py** | 向设备发送实时命令 | 模板管理、命令执行、状态监控、历史跟踪 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptsmanage_commandspy) |
| **cleanup_script.py** | 删除 AWS 资源 | 选择性清理、成本管理 | [📖 详情](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **详细文档**：有关全面的脚本信息，请参阅 [docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md)。

## ⚙️ 配置

**环境变量**（可选）：
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=zh                    # 设置默认语言（en、es、fr 等）
```

**脚本功能**：
- **原生 AWS SDK**：使用 boto3 获得更好的性能和可靠性
- **多语言支持**：交互式语言选择，回退到英语
- **调试模式**：显示所有 AWS API 调用和响应
- **并行处理**：非调试模式下的并发操作
- **速率限制**：自动 AWS API 节流合规性
- **进度跟踪**：实时操作状态
- **资源标记**：自动工作坊标签以实现安全清理
- **可配置命名**：可自定义的设备命名模式

### 资源标记

所有工作坊脚本都会自动为创建的资源标记 `workshop=learning-aws-iot-dm-basics`，以便在清理期间进行安全识别。这确保只删除工作坊创建的资源。

**已标记的资源**：
- IoT Thing 类型
- IoT Thing 组（静态和动态）
- IoT 软件包
- IoT 作业
- Amazon S3 存储桶
- IAM 角色

**未标记的资源**（通过命名模式识别）：
- IoT Thing（使用命名约定）
- 证书（通过关联识别）
- Thing 影子（通过关联识别）

### 设备命名配置

使用 `--things-prefix` 参数自定义设备命名模式：

```bash
# 默认命名：Vehicle-VIN-001、Vehicle-VIN-002 等
python scripts/provision_script.py

# 自定义前缀：Fleet-Device-001、Fleet-Device-002 等
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# 清理的自定义前缀（必须与配置前缀匹配）
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**前缀要求**：
- 仅限字母数字字符、连字符、下划线和冒号
- 最多 20 个字符
- 序列号自动补零（001-999）

## 🌍 国际化支持

所有脚本都支持多种语言，具有自动语言检测和交互式选择功能。

**语言选择**：
- **交互式**：脚本在首次运行时提示语言选择
- **环境变量**：设置 `AWS_IOT_LANG=zh` 以跳过语言选择
- **回退**：对于缺失的翻译自动回退到英语

**支持的语言**：
- **English (en)**：完整翻译 ✅
- **Spanish (es)**：准备翻译
- **Japanese (ja)**：准备翻译
- **Chinese (zh-CN)**：准备翻译
- **Portuguese (pt-BR)**：准备翻译
- **Korean (ko)**：准备翻译

**使用示例**：
```bash
# 通过环境变量设置语言（推荐用于自动化）
export AWS_IOT_LANG=zh
python scripts/provision_script.py

# 支持的替代语言代码
export AWS_IOT_LANG=chinese    # 或 "zh-cn"、"中文"、"zh"
export AWS_IOT_LANG=spanish    # 或 "es"、"español"
export AWS_IOT_LANG=japanese   # 或 "ja"、"日本語"、"jp"
export AWS_IOT_LANG=portuguese # 或 "pt"、"pt-br"、"português"
export AWS_IOT_LANG=korean     # 或 "ko"、"한국어"、"kr"

# 交互式语言选择（默认行为）
python scripts/manage_packages.py
# 输出：🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# 所有面向用户的文本将以所选语言显示
```

**消息类别**：
- **UI 元素**：标题、标头、分隔符
- **用户提示**：输入请求、确认
- **状态消息**：进度更新、成功/失败通知
- **错误消息**：详细错误描述和故障排除
- **调试输出**：API 调用信息和响应
- **学习内容**：教育时刻和解释

## 📖 使用示例

**完整工作流程**（推荐顺序）：
```bash
python scripts/provision_script.py        # 1. 创建基础设施
python scripts/manage_dynamic_groups.py   # 2. 创建设备组
python scripts/manage_packages.py         # 3. 管理固件包
python scripts/create_job.py              # 4. 部署固件更新
python scripts/simulate_job_execution.py  # 5. 模拟设备更新
python scripts/explore_jobs.py            # 6. 监控作业进度
python scripts/manage_commands.py         # 7. 向设备发送实时命令
python scripts/cleanup_script.py          # 8. 清理资源
```

**单独操作**：
```bash
python scripts/manage_packages.py         # 包和版本管理
python scripts/manage_dynamic_groups.py   # 动态组操作
```

> 📖 **更多示例**：有关详细使用场景，请参阅 [docs/EXAMPLES.md](docs/EXAMPLES.md)。

## 🛠️ 故障排除

**常见问题**：
- **凭证**：通过 `aws configure`、环境变量或 IAM 角色配置 AWS 凭证
- **权限**：确保 IAM 用户具有 AWS IoT、Amazon S3 和 IAM 权限
- **速率限制**：脚本通过智能节流自动处理
- **网络**：确保与 AWS API 的连接

**调试模式**：在任何脚本中启用以进行详细故障排除
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **详细故障排除**：有关全面解决方案，请参阅 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)。

## 🧹 重要：资源清理

**完成后始终运行清理以避免持续费用：**
```bash
python scripts/cleanup_script.py
# 选择选项 1：所有资源
# 输入：DELETE
```

### 安全清理功能

清理脚本使用多种识别方法来确保仅删除工作坊资源：

1. **基于标签的识别**（主要）：检查 `workshop=learning-aws-iot-dm-basics` 标签
2. **命名模式匹配**（次要）：匹配已知的工作坊命名约定
3. **基于关联**（第三）：识别附加到工作坊资源的资源

**清理选项**：
```bash
# 标准清理（交互式）
python scripts/cleanup_script.py

# 试运行模式（预览而不删除）
python scripts/cleanup_script.py --dry-run

# 自定义设备前缀（必须与配置前缀匹配）
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# 带自定义前缀的试运行
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**清理删除的内容**：
- 所有 AWS IoT 设备和组（带有工作坊标签或匹配的命名模式）
- Amazon S3 存储桶和固件文件（已标记）
- AWS IoT 软件包（已标记）
- AWS IoT 命令模板（已标记）
- IAM 角色和策略（已标记）
- Fleet Indexing 配置
- 关联的证书和影子

**安全功能**：
- 非工作坊资源会自动跳过
- 详细摘要显示已删除和跳过的资源
- 调试模式显示每个资源的识别方法
- 试运行模式允许在实际删除前预览

## 🔧 开发者指南：添加新语言

**消息文件结构**：
```
i18n/
├── common.json                    # 所有脚本共享的消息
├── loader.py                      # 消息加载实用程序
├── language_selector.py           # 语言选择界面
└── {language_code}/               # 特定语言目录
    ├── provision_script.json     # 脚本特定消息
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**添加新语言**：

1. **创建语言目录**：
   ```bash
   mkdir i18n/{language_code}  # 例如，西班牙语为 i18n/es
   ```

2. **复制英语模板**：
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **翻译消息文件**：
   每个 JSON 文件包含分类消息：
   ```json
   {
     "title": "📦 AWS IoT Software Package Manager (Boto3)",
     "separator": "============================================",
     "prompts": {
       "debug_mode": "🔧 Enable debug mode? [y/N]: ",
       "operation_choice": "Enter choice [1-11]: ",
       "continue_operation": "Continue? [Y/n]: "
     },
     "status": {
       "debug_enabled": "✅ Debug mode enabled",
       "package_created": "✅ Package created successfully",
       "clients_initialized": "🔍 DEBUG: Client configuration:"
     },
     "errors": {
       "invalid_choice": "❌ Invalid choice. Please enter 1-11",
       "package_not_found": "❌ Package '{}' not found",
       "api_error": "❌ Error in {} {}: {}"
     },
     "debug": {
       "api_call": "📤 API Call: {}",
       "api_response": "📤 API Response:",
       "debug_operation": "🔍 DEBUG: {}: {}"
     },
     "ui": {
       "operation_menu": "🎯 Select Operation:",
       "create_package": "1. Create Software Package",
       "goodbye": "👋 Thank you for using Package Manager!"
     },
     "learning": {
       "package_management_title": "Software Package Management",
       "package_management_description": "Educational content..."
     }
   }
   ```

4. **更新语言选择器**（如果添加新语言）：
   将您的语言添加到 `i18n/language_selector.py`：
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Your Language Name",  # 添加新选项
           # ... 现有语言
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "your_code",  # 添加新语言代码
       # ... 现有映射
   }
   ```

5. **测试翻译**：
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**翻译指南**：
- **保留格式**：保持表情符号、颜色和特殊字符
- **维护占位符**：保持 `{}` 占位符用于动态内容
- **技术术语**：保持 AWS 服务名称为英语
- **文化适应**：适当调整示例和引用
- **一致性**：在所有文件中使用一致的术语

**消息键模式**：
- `title`：脚本主标题
- `separator`：视觉分隔符和分隔线
- `prompts.*`：用户输入请求和确认
- `status.*`：进度更新和操作结果
- `errors.*`：错误消息和警告
- `debug.*`：调试输出和 API 信息
- `ui.*`：用户界面元素（菜单、标签、按钮）
- `results.*`：操作结果和数据显示
- `learning.*`：教育内容和解释
- `warnings.*`：警告消息和重要通知
- `explanations.*`：附加上下文和帮助文本

**测试您的翻译**：
```bash
# 使用您的语言测试特定脚本
export AWS_IOT_LANG=your_language_code
python scripts/manage_packages.py

# 测试回退行为（使用不存在的语言）
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # 应该回退到英语
```

## 📚 文档

- **[详细脚本](docs/DETAILED_SCRIPTS.md)** - 全面的脚本文档
- **[使用示例](docs/EXAMPLES.md)** - 实际场景和工作流程
- **[故障排除](docs/TROUBLESHOOTING.md)** - 常见问题和解决方案

## 📄 许可证

MIT No Attribution License - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🏷️ 标签

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot`