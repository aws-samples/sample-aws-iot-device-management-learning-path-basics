# 详细脚本文档

本文档提供有关AWS IoT Device Management项目中每个脚本的全面信息。所有脚本都使用原生AWS SDK（boto3）以获得最佳性能和可靠性。

## 核心脚本

### scripts/provision_script.py
**目的**：使用原生boto3 API为设备管理场景提供完整的AWS IoT基础设施配置。

**功能**：
- 创建具有可搜索属性（customerId、country、manufacturingDate）的物品类型
- 使用VIN样式命名（Vehicle-VIN-001）配置数千个IoT设备
- 为固件软件包设置具有版本控制的Amazon S3存储
- 创建具有多个版本的AWS IoT软件包
- 配置AWS IoT Fleet Indexing以进行设备查询
- 建立AWS Identity and Access Management（IAM）角色以进行安全操作
- 按国家创建静态物品组（Fleet命名约定）
- **并行处理**：并发操作以实现更快的配置
- **增强的错误处理**：强大的boto3异常处理

**交互式输入**：
1. 物品类型（默认：SedanVehicle,SUVVehicle,TruckVehicle）
2. 软件包版本（默认：1.0.0,1.1.0）
3. 大陆选择（1-7）
4. 国家（数量或特定代码）
5. 设备数量（默认：100）

**教育性暂停**：8个学习时刻解释IoT概念

**速率限制**：智能AWS API限流（物品80 TPS，物品类型8 TPS）

**性能**：非调试模式下并行执行，调试模式下顺序执行以获得清晰输出

---

### scripts/cleanup_script.py
**目的**：使用原生boto3 API安全删除AWS IoT资源以避免持续成本。

**清理选项**：
1. **所有资源** - 完整的基础设施清理
2. **仅物品** - 删除设备但保留基础设施
3. **仅物品组** - 删除分组但保留设备

**功能**：
- **原生boto3实现**：无CLI依赖，更好的错误处理
- 具有智能速率限制的**并行处理**
- **增强的S3清理**：使用分页器正确删除版本化对象
- 自动区分静态组与动态组
- 处理物品类型弃用（5分钟等待）
- 使用状态监控取消和删除AWS IoT作业
- 全面的IAM角色和策略清理
- 禁用Fleet Indexing配置
- **影子清理**：删除经典影子和$package影子
- **主体分离**：正确分离证书和策略

**安全性**：需要输入"DELETE"以确认

**性能**：遵守AWS API限制的并行执行（物品80 TPS，动态组4 TPS）

---

### scripts/create_job.py
**目的**：使用原生boto3 API创建用于OTA固件更新的AWS IoT作业。

**功能**：
- **原生boto3实现**：直接API调用以获得更好的性能
- 交互式物品组选择（单个或多个）
- 具有ARN解析的软件包版本选择
- 连续作业配置（自动包含新设备）
- 预签名URL配置（1小时过期）
- 多组目标支持
- **增强的作业类型**：支持OTA和自定义作业类型
- **高级配置**：推出策略、中止标准、超时设置

**作业配置**：
- 带时间戳的自动生成作业ID
- AWS IoT预签名URL占位符
- 资源的正确ARN格式
- 全面的作业文档结构
- **教育内容**：解释作业配置选项

---

### scripts/simulate_job_execution.py
**目的**：使用原生boto3 API模拟固件更新期间的真实设备行为。

**功能**：
- **原生boto3实现**：与IoT Jobs Data API直接集成
- 通过预签名URL实际下载Amazon S3工件
- **高性能并行执行**（具有信号量控制的150 TPS）
- 可配置的成功/失败率
- **可见的计划准备** - 显示每个设备被分配成功/失败状态
- **用户确认** - 在计划准备后询问是否继续
- **操作可见性** - 显示每个设备的下载进度和作业状态更新
- **增强的错误处理**：强大的boto3异常管理
- 具有详细报告的进度跟踪
- **清晰的JSON格式**：正确格式化的作业文档显示

**流程**：
1. 使用原生API扫描活动作业
2. 获取待处理的执行（QUEUED/IN_PROGRESS）
3. **准备执行计划** - 显示设备分配并请求确认
4. 从Amazon S3下载实际固件（显示每个设备的进度）
5. 使用IoT Jobs Data API更新作业执行状态
6. 报告全面的成功/失败统计信息

**性能改进**：
- **并行处理**：非调试模式下的并发执行
- **速率限制**：基于信号量的智能限流
- **内存效率**：大型固件文件的流式下载

**可见性改进**：
- 计划准备显示：`[1/100] Vehicle-VIN-001 -> SUCCESS`
- 下载进度显示：`Vehicle-VIN-001: Downloading firmware from S3...`
- 文件大小确认：`Vehicle-VIN-001: Downloaded 2.1KB firmware`
- 状态更新显示：`Vehicle-VIN-001: Job execution SUCCEEDED`

---

### scripts/explore_jobs.py
**目的**：使用原生boto3 API进行监控和故障排除的AWS IoT作业交互式探索。

**菜单选项**：
1. **列出所有作业** - 通过并行扫描概览所有状态
2. **探索特定作业** - 使用清晰JSON格式的详细作业配置
3. **探索作业执行** - 使用IoT Jobs Data API的单个设备进度
4. **列出作业执行** - 具有并行状态检查的作业的所有执行

**功能**：
- **原生boto3实现**：直接API集成以获得更好的性能
- **并行作业扫描**：跨所有作业状态的并发状态检查
- **清晰的JSON显示**：没有转义字符的正确格式化作业文档
- 颜色编码的状态指示器
- 具有可用作业列表的交互式作业选择
- 详细的预签名URL配置显示
- 具有颜色编码的执行摘要统计
- **增强的错误处理**：强大的boto3异常管理
- 连续探索循环

**性能改进**：
- **并行处理**：非调试模式下的并发操作
- **智能分页**：高效处理大型作业列表
- **速率限制**：使用信号量的适当API限流

---

### scripts/manage_packages.py
**目的**：使用原生boto3 API全面管理AWS IoT软件包、设备跟踪和版本回滚。

**操作**：
1. **创建软件包** - 创建新的软件包容器
2. **创建版本** - 通过S3固件上传和发布添加版本（带学习时刻）
3. **列出软件包** - 显示具有交互式描述选项的软件包
4. **描述软件包** - 显示具有版本探索的软件包详细信息
5. **描述版本** - 显示特定版本详细信息和Amazon S3工件
6. **检查配置** - 查看软件包配置状态和IAM角色
7. **启用配置** - 通过IAM角色创建启用自动影子更新
8. **禁用配置** - 禁用自动影子更新
9. **检查设备版本** - 检查特定设备的$package影子（多设备支持）
10. **恢复版本** - 使用Fleet Indexing进行车队范围的版本回滚

**主要功能**：
- **Amazon S3集成**：具有版本控制的自动固件上传
- **交互式导航**：列表、描述和版本操作之间的无缝流程
- **软件包配置管理**：控制Jobs-to-Shadow集成
- **设备跟踪**：单个设备软件包版本检查
- **车队回滚**：使用Fleet Indexing查询进行版本恢复
- **教育方法**：整个工作流程中的学习时刻
- **IAM角色管理**：软件包配置的自动角色创建

**软件包配置**：
- **检查状态**：显示启用/禁用状态和IAM角色ARN
- **启用**：创建具有$package影子权限的IoTPackageConfigRole
- **禁用**：在作业完成时停止自动影子更新
- **教育性**：解释Jobs-to-Shadow集成和IAM要求

**设备版本跟踪**：
- **多设备支持**：按顺序检查多个设备
- **$package影子检查**：显示当前固件版本和元数据
- **时间戳显示**：每个软件包的最后更新信息
- **错误处理**：缺少设备或影子的清晰消息

**版本回滚**：
- **Fleet Indexing查询**：按物品类型和版本查找设备
- **设备列表预览**：显示将被恢复的设备（前10个+计数）
- **需要确认**：输入'REVERT'以继续影子更新
- **单个设备状态**：显示每个设备的恢复成功/失败
- **进度跟踪**：具有成功计数的实时更新状态
- **教育性**：解释回滚概念和影子管理

**回滚可见性**：
- 设备预览：`1. Vehicle-VIN-001`、`2. Vehicle-VIN-002`、`... 以及90多个设备`
- 单个结果：`Vehicle-VIN-001: Reverted to version 1.0.0`
- 失败的尝试：`Vehicle-VIN-002: Failed to revert`

**学习重点**：
- 从创建到回滚的完整固件生命周期
- 软件包配置和自动影子更新
- 设备库存管理和跟踪
- 用于版本管理操作的Fleet Indexing

---

### scripts/manage_dynamic_groups.py
**目的**：使用原生boto3 API进行具有Fleet Indexing验证的动态物品组的全面管理。

**操作**：
1. **创建动态组** - 两种创建方法：
   - **引导向导**：交互式标准选择
   - **自定义查询**：直接Fleet Indexing查询输入
2. **列出动态组** - 显示所有组及其成员计数和查询
3. **删除动态组** - 带确认的安全删除
4. **测试查询** - 验证自定义Fleet Indexing查询

**创建方法**：
- **引导向导**（全部可选）：
  - 国家：单个或多个（例如，US,CA,MX）
  - 物品类型：车辆类别（例如，SedanVehicle）
  - 版本：单个或多个（例如，1.0.0,1.1.0）
  - 电池电量：比较（例如，>50、<30、=75）
- **自定义查询**：直接Fleet Indexing查询字符串输入

**功能**：
- **双重创建模式**：引导向导或自定义查询输入
- 智能组命名（自动生成或自定义）
- Fleet Indexing查询构建和验证
- **实时设备匹配预览**（创建前显示匹配的设备）
- 现有组的成员计数显示
- 带确认提示的安全删除
- 自定义查询测试功能
- 查询验证防止创建空组

**查询示例**：
- 单一标准：`thingTypeName:SedanVehicle AND attributes.country:US`
- 多个标准：`thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- 软件包版本：`shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- 自定义复杂：`(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**目的**：CI/CD管道的发布前语法验证。

**检查**：
- 所有脚本的Python语法验证
- 导入可用性验证
- requirements.txt验证
- 依赖项列表

**使用**：由GitHub Actions工作流自动运行

---

## 脚本依赖项

### 所需的Python软件包
- `boto3>=1.40.27` - AWS SDK for Python（支持软件包工件的最新版本）
- `colorama>=0.4.4` - 终端颜色
- `requests>=2.25.1` - 用于Amazon S3下载的HTTP请求

### 使用的AWS服务
- **AWS IoT Core** - 物品管理、作业、影子
- **AWS IoT Device Management** - 软件包、Fleet Indexing
- **Amazon S3** - 具有版本控制的固件存储
- **AWS Identity and Access Management (IAM)** - 用于安全访问的角色和策略

### AWS凭证要求
- 通过以下方式配置的凭证：
  - `aws configure`（AWS CLI）
  - 环境变量（AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY）
  - IAM角色（用于EC2/Lambda执行）
  - AWS凭证文件
- AWS IoT、Amazon S3和IAM操作的适当IAM权限
- 区域配置（AWS_DEFAULT_REGION环境变量或凭证）

## 教育功能

### 学习时刻
每个脚本都包含解释以下内容的教育性暂停：
- AWS IoT概念和架构
- 设备管理最佳实践
- 安全考虑
- 可扩展性模式

### 进度跟踪
- 实时操作状态
- 成功/失败计数
- 性能指标（TPS、持续时间）
- 颜色编码的输出以便于阅读

### 调试模式
在所有脚本中可用：
- 显示所有带参数的AWS SDK（boto3）API调用
- 以JSON格式显示完整的API响应
- 提供带有完整堆栈跟踪的详细错误信息
- **顺序处理**：顺序运行操作以获得清晰的调试输出
- 帮助进行AWS API的故障排除和学习

## 性能特性

### 速率限制
脚本遵守AWS API限制：
- 物品操作：80 TPS（100 TPS限制）
- 物品类型：8 TPS（10 TPS限制）
- 动态组：4 TPS（5 TPS限制）
- 作业执行：150 TPS（200 TPS限制）
- 软件包操作：8 TPS（10 TPS限制）

### 并行处理
- **原生boto3集成**：直接AWS SDK调用以获得更好的性能
- 用于并发操作的ThreadPoolExecutor（非调试模式时）
- **智能速率限制**：遵守AWS API限制的信号量
- **线程安全的进度跟踪**：并发操作监控
- **增强的错误处理**：强大的boto3 ClientError异常管理
- **调试模式覆盖**：调试模式下的顺序处理以获得清晰输出

### 内存管理
- 大文件的流式下载
- 临时文件清理
- 高效的JSON解析
- 退出时的资源清理
