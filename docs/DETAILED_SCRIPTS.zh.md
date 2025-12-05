# 详细脚本文档

本文档提供有关AWS IoT Device Management项目中每个脚本的全面信息。所有脚本都使用原生AWS SDK（boto3）以获得最佳性能和可靠性。

## 核心脚本

### scripts/provision_script.py
**目的**: 使用原生boto3 API为设备管理场景提供完整的AWS IoT基础设施配置。

**功能**:
- 创建具有可搜索属性（customerId、country、manufacturingDate）的物品类型
- 使用VIN样式命名（Vehicle-VIN-001）配置数千个IoT设备
- 为固件包设置具有版本控制的Amazon S3存储
- 创建具有多个版本的AWS IoT软件包
- 配置AWS IoT Fleet Indexing以进行设备查询
- 建立AWS Identity and Access Management（IAM）角色以进行安全操作
- 按国家创建静态物品组（Fleet命名约定）
- **并行处理**: 并发操作以实现更快的配置
- **增强的错误处理**: 强大的boto3异常处理

**交互式输入**:
1. 物品类型（默认: SedanVehicle,SUVVehicle,TruckVehicle）
2. 包版本（默认: 1.0.0,1.1.0）
3. 大陆选择（1-7）
4. 国家（计数或特定代码）
5. 设备数量（默认: 100）

**命令行参数**:
- `--things-prefix PREFIX` - 物品名称的自定义前缀（默认: "Vehicle-VIN-"）
  - 必须为1-20个字符
  - 仅限字母数字、连字符、下划线和冒号
  - 示例: `--things-prefix "Fleet-Device-"` 创建 Fleet-Device-001、Fleet-Device-002 等

**资源标记行为**:
所有创建的资源都会自动标记为:
- `workshop=learning-aws-iot-dm-basics` - 标识研讨会资源
- `creation-date=YYYY-MM-DD` - 用于跟踪的时间戳

**已标记的资源**:
- 物品类型
- 物品组（静态组）
- 软件包
- 软件包版本
- 作业
- S3存储桶
- IAM角色

**标记失败处理**:
- 标记失败不会阻止资源创建
- 脚本会继续执行并对失败的标记发出警告
- 摘要报告显示没有标记的资源
- 清理脚本使用命名模式作为后备

**教育暂停**: 8个学习时刻解释IoT概念

**速率限制**: 智能AWS API限流（物品80 TPS，物品类型8 TPS）

**性能**: 非调试模式下并行执行，调试模式下顺序执行以获得清晰输出

**资源标记**:
- **自动研讨会标记**: 所有可标记的资源都会收到 `workshop=learning-aws-iot-dm-basics` 标记
- **支持的资源**: 物品类型、物品组、包、作业、S3存储桶、IAM角色
- **不可标记的资源**: 物品、证书和shadow依赖于命名约定
- **标记失败处理**: 优雅降级 - 如果标记失败，继续创建资源
- **清理集成**: 标记可在清理操作期间实现安全识别

**物品命名约定**:
- **--things-prefix 参数**: 物品名称的可配置前缀（默认: "Vehicle-VIN-"）
- **命名模式**: `{prefix}{sequential_number}`（例如: Vehicle-VIN-001、Vehicle-VIN-002）
- **顺序编号**: 零填充的3位数字（001-999）
- **前缀验证**: 仅限字母数字、连字符、下划线、冒号；最多20个字符
- **旧版支持**: 也识别旧的 `vehicle-{country}-{type}-{index}` 模式
- **清理集成**: 命名模式可识别不可标记的资源

**使用示例**:
```bash
# 使用默认前缀（Vehicle-VIN-）
python scripts/provision_script.py

# 使用自定义前缀
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# 自定义前缀创建: Fleet-Device-001、Fleet-Device-002 等
```

---

### scripts/cleanup_script.py
**目的**: 使用原生boto3 API和智能资源识别安全删除AWS IoT资源以避免持续成本。

**清理选项**:
1. **所有资源** - 完整的基础设施清理
2. **仅物品** - 删除设备但保留基础设施
3. **仅物品组** - 删除分组但保留设备

**命令行参数**:
- `--things-prefix PREFIX` - 用于物品识别的自定义前缀（默认: "Vehicle-VIN-"）
  - 必须与配置期间使用的前缀匹配
  - 用于识别具有自定义命名模式的物品
  - 示例: `--things-prefix "Fleet-Device-"` 识别 Fleet-Device-001、Fleet-Device-002 等
- `--dry-run` - 预览将被删除的内容而不进行更改
  - 显示将被删除的所有资源
  - 显示每个资源的识别方法
  - 不执行实际删除
  - 在执行前验证清理范围很有用

**资源识别方法**:

清理脚本使用三层识别系统来安全识别研讨会资源:

**1. 基于标记的识别（最高优先级）**:
- 检查 `workshop=learning-aws-iot-dm-basics` 标记
- 对于使用标记创建的资源最可靠的方法
- 适用于: 物品类型、物品组、包、包版本、作业、S3存储桶、IAM角色

**2. 命名模式识别（后备）**:
- 将资源名称与研讨会模式匹配
- 当标记不存在或不受支持时使用
- 模式包括:
  - 物品: `Vehicle-VIN-###` 或自定义前缀模式（例如: `Fleet-Device-###`）
  - 物品类型: `SedanVehicle`、`SUVVehicle`、`TruckVehicle`
  - 物品组: `Fleet-*`（静态组）
  - 动态组: `DynamicGroup-*`
  - 包: `SedanVehicle-Package`、`SUVVehicle-Package`、`TruckVehicle-Package`
  - 作业: `OTA-Job-*`、`Command-Job-*`
  - S3存储桶: `iot-dm-workshop-*`
  - IAM角色: `IoTJobsRole`、`IoTPackageConfigRole`

**3. 基于关联的识别（用于不可标记的资源）**:
- 用于无法直接标记的资源
- 证书: 通过附加到研讨会物品来识别
- Shadow: 通过属于研讨会物品来识别
- 确保依赖资源的完整清理

**识别过程**:
1. 对于每个资源，首先检查标记
2. 如果未找到研讨会标记，检查命名模式
3. 如果没有模式匹配，检查关联（用于证书/shadow）
4. 如果没有识别方法成功，跳过资源
5. 调试模式显示识别每个资源的方法

**功能**:
- **原生boto3实现**: 无CLI依赖，更好的错误处理
- **智能资源识别**: 三层系统（标记 → 命名 → 关联）
- **试运行模式**: 预览删除而不进行更改
- **自定义前缀支持**: 识别具有自定义命名模式的物品
- 具有智能速率限制的**并行处理**
- **增强的S3清理**: 使用分页器正确删除版本化对象
- 自动区分静态组与动态组
- 处理物品类型弃用（5分钟等待）
- 使用状态监控取消和删除AWS IoT Jobs
- 全面的IAM角色和策略清理
- 禁用Fleet Indexing配置
- **Shadow清理**: 删除经典和$package shadow
- **主体分离**: 正确分离证书和策略
- **全面报告**: 显示已删除和跳过的资源及计数

**安全功能**:
- 需要输入"DELETE"以确认（试运行模式除外）
- 自动跳过非研讨会资源
- 显示将被删除内容的摘要
- 实际删除前的试运行模式用于验证
- 错误处理即使个别资源失败也继续清理

**试运行模式示例**:
```bash
python scripts/cleanup_script.py --dry-run
```
输出显示:
- 将被删除的资源（带识别方法）
- 将被跳过的资源（非研讨会资源）
- 按资源类型的总计数
- 不执行实际删除

**自定义前缀示例**:
```bash
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```
识别并删除:
- 匹配 Fleet-Device-### 模式的物品
- 关联的证书和shadow
- 其他研讨会资源（通过标记或模式识别）

**性能**: 遵守AWS API限制的并行执行（物品80 TPS，动态组4 TPS）

**基于标记的清理示例**:
```
扫描物品类型...
找到3个物品类型
  ✓ SedanVehicle（通过标记识别: workshop=learning-aws-iot-dm-basics）
  ✓ SUVVehicle（通过标记识别: workshop=learning-aws-iot-dm-basics）
  ✓ TruckVehicle（通过标记识别: workshop=learning-aws-iot-dm-basics）

扫描物品组...
找到5个物品组
  ✓ fleet-US（通过标记识别: workshop=learning-aws-iot-dm-basics）
  ✓ fleet-CA（通过标记识别: workshop=learning-aws-iot-dm-basics）
  ✗ production-fleet（跳过 - 无研讨会标记）
```

**基于命名的清理示例**:
```
扫描物品...
找到102个物品
  ✓ Vehicle-VIN-001（通过命名模式识别: Vehicle-VIN-###）
  ✓ Vehicle-VIN-002（通过命名模式识别: Vehicle-VIN-###）
  ✓ vehicle-US-sedan-1（通过旧版模式识别）
  ✗ production-device-001（跳过 - 无模式匹配）
```

**基于关联的清理示例**:
```
处理物品: Vehicle-VIN-001
  ✓ 经典shadow（通过与研讨会物品的关联识别）
  ✓ $package shadow（通过与研讨会物品的关联识别）
  ✓ 证书 abc123（通过与研讨会物品的关联识别）
  
处理物品: production-device-001
  ✗ 证书 xyz789（跳过 - 附加到非研讨会物品）
```

**清理摘要输出**:
```
清理摘要:
================
已删除的资源:
  - IoT物品: 100
  - 物品组: 5
  - 物品类型: 3
  - 包: 3
  - 作业: 2
  - S3存储桶: 1
  - IAM角色: 2
  总计: 116

跳过的资源:
  - IoT物品: 2（非研讨会资源）
  - 物品组: 1（非研讨会资源）
  总计: 3

执行时间: 45.3秒
```

**清理问题故障排除**:

**问题: 资源未被删除**

症状:
- 清理脚本跳过您期望删除的资源
- "跳过的资源"计数高于预期
- 清理后特定资源仍然存在

解决方案:
1. **验证物品前缀匹配**:
   ```bash
   # 如果在配置期间使用了自定义前缀:
   python scripts/provision_script.py --things-prefix "MyPrefix-"
   
   # 在清理期间必须使用相同的前缀:
   python scripts/cleanup_script.py --things-prefix "MyPrefix-"
   ```

2. **检查资源标记**:
   - 在调试模式下运行清理以查看识别方法
   - 验证可标记资源具有 `workshop=learning-aws-iot-dm-basics` 标记
   - 检查AWS控制台 → IoT Core → 资源标记

3. **验证命名模式**:
   - 物品应匹配: `{prefix}###` 或 `vehicle-{country}-{type}-{index}`
   - 组应匹配: `fleet-{country}` 或包含"workshop"
   - 使用试运行模式查看将被识别的内容

4. **首先使用试运行**:
   ```bash
   # 预览将被删除的内容
   python scripts/cleanup_script.py --dry-run
   
   # 检查跳过资源的输出
   # 在调试模式下验证识别方法
   ```

**问题: 配置期间标记应用失败**

症状:
- 配置脚本显示"应用标记失败"警告
- 资源已创建但没有研讨会标记
- 清理脚本跳过应该删除的资源

解决方案:
1. **检查IAM权限**:
   - 验证IAM用户/角色具有标记权限
   - 所需操作: `iot:TagResource`、`s3:PutBucketTagging`、`iam:TagRole`

2. **依赖命名约定**:
   - 没有标记的资源仍可通过命名模式识别
   - 确保配置期间命名一致
   - 对配置和清理使用相同的 --things-prefix

3. **手动添加标记**（如果需要）:
   ```bash
   # 通过AWS CLI手动添加标记
   aws iot tag-resource --resource-arn <arn> --tags workshop=learning-aws-iot-dm-basics
   ```

**问题: 清理删除错误的资源**

症状:
- 非研讨会资源被识别为删除对象
- 试运行显示意外资源

解决方案:
1. **始终首先使用试运行**:
   ```bash
   python scripts/cleanup_script.py --dry-run
   ```

2. **审查命名模式**:
   - 确保生产资源不匹配研讨会模式
   - 避免对生产物品使用"Vehicle-VIN-"前缀
   - 不要对生产组使用"fleet-"前缀

3. **检查标记冲突**:
   - 验证没有生产资源具有研讨会标记
   - 审查AWS账户中的标记策略

**问题: 清理因权限错误而失败**

症状:
- "AccessDeniedException"或"UnauthorizedException"错误
- 部分清理完成
- 某些资源类型已删除，其他被跳过

解决方案:
1. **验证IAM权限**:
   - README.md中列出的所需权限
   - 检查所有所需操作的IAM策略
   - 验证以下权限: IoT、S3、IAM、Fleet Indexing

2. **检查资源策略**:
   - S3存储桶策略可能阻止删除
   - IAM角色信任策略可能阻止删除
   - 审查资源级策略

3. **使用调试模式**:
   ```bash
   # 使用调试运行以查看确切的API错误
   python scripts/cleanup_script.py
   # 对调试模式回答'y'
   ```

**问题: 清理时间过长**

症状:
- 清理运行时间延长
- 进度看起来很慢
- 超时错误

解决方案:
1. **预期持续时间**:
   - 100个物品: 约2-3分钟
   - 1000个物品: 约15-20分钟
   - 物品类型删除: +5分钟（所需的弃用等待）

2. **速率限制**:
   - 脚本自动遵守AWS API限制
   - 并行处理优化性能
   - 调试模式顺序运行（较慢但输出更清晰）

3. **监控进度**:
   - 观察实时进度指示器
   - 检查AWS控制台的删除状态
   - 使用调试模式查看每个操作

**问题: 试运行显示与实际清理不同的结果**

症状:
- 试运行识别的资源实际清理跳过
- 模式之间的行为不一致

解决方案:
1. **资源状态更改**:
   - 资源可能在试运行和实际清理之间被修改
   - 标记可能被其他进程添加/删除
   - 在实际清理之前立即重新运行试运行

2. **并发修改**:
   - 其他用户/进程可能正在修改资源
   - 与团队协调清理时间
   - 如果可用，使用资源锁定

3. **缓存问题**:
   - AWS API响应可能会短暂缓存
   - 在试运行和实际清理之间等待几秒钟
   - 刷新AWS控制台以验证当前状态

**问题: 部分清理**

症状:
- 某些资源已删除，其他资源仍然存在
- 清理期间的错误消息
- 不完整的清理结果

解决方案:
1. **依赖问题**:
   - 某些资源可能由于依赖关系而无法删除
   - 脚本继续处理剩余资源
   - 检查特定失败的错误消息
   - 重新运行脚本以清理剩余资源

2. **资源状态**:
   - 物品类型必须在删除前弃用（5分钟等待）
   - 作业必须在删除前取消
   - S3存储桶必须在删除前清空

3. **重新运行清理**:
   ```bash
   # 再次运行清理以捕获剩余资源
   python scripts/cleanup_script.py
   ```

**安全清理的最佳实践**:

1. **始终从试运行开始**:
   ```bash
   python scripts/cleanup_script.py --dry-run
   ```

2. **验证物品前缀匹配**:
   - 使用与配置相同的 --things-prefix
   - 记录自定义前缀供团队参考

3. **使用调试模式进行故障排除**:
   - 查看每个资源的识别方法
   - 了解资源被跳过的原因
   - 验证标记和命名模式匹配

4. **与团队协调**:
   - 传达清理时间
   - 验证没有使用资源的活动研讨会
   - 记录清理结果

5. **监控AWS控制台**:
   - 验证资源按预期删除
   - 检查剩余的研讨会资源
   - 如果可用，审查CloudWatch日志

6. **保持一致的命名**:
   - 在研讨会中使用标准前缀
   - 记录命名约定
   - 避免生产命名冲突

**基于标记的清理不起作用**:
- 验证资源是否在启用标记的情况下创建
- 检查配置期间标记是否失败（查看配置脚本输出）
- 命名模式识别将用作后备
- 考虑使用 `--dry-run` 验证识别方法

---


### scripts/create_job.py
**目的**: 使用原生boto3 API创建用于无线(OTA)固件更新的AWS IoT作业。

**功能**:
- **原生boto3实现**: 直接API调用以获得更好的性能
- 交互式物品组选择（单个或多个）
- 带ARN解析的包版本选择
- 连续作业配置（自动包含新设备）
- 预签名URL配置（1小时过期）
- 多组目标支持
- **增强的作业类型**: 支持OTA和自定义作业类型
- **高级配置**: 推出策略、中止标准、超时设置

**作业配置**:
- 带时间戳的自动生成作业ID
- AWS IoT预签名URL占位符
- 资源的正确ARN格式
- 全面的作业文档结构
- **教育内容**: 解释作业配置选项

---

### scripts/simulate_job_execution.py
**目的**: 使用原生boto3 API模拟固件更新期间的真实设备行为。

**功能**:
- **原生boto3实现**: 直接IoT Jobs Data API集成
- 通过预签名URL从Amazon S3实际下载工件
- **高性能并行执行**（使用信号量控制的150 TPS）
- 可配置的成功/失败率
- **可见的计划准备** - 显示每个设备被分配成功/失败状态
- **用户确认** - 在计划准备后询问是否继续
- **操作可见性** - 显示每个设备的下载进度和作业状态更新
- **增强的错误处理**: 强大的boto3异常管理
- 带详细报告的进度跟踪
- **清晰的JSON格式**: 正确格式化的作业文档显示

**流程**:
1. 使用原生API扫描活动作业
2. 获取待处理的执行（QUEUED/IN_PROGRESS）
3. **准备执行计划** - 显示设备分配并请求确认
4. 从Amazon S3下载实际固件（显示每个设备的进度）
5. 使用IoT Jobs Data API更新作业执行状态
6. 报告全面的成功/失败统计信息

**性能改进**:
- **并行处理**: 非调试模式下的并发执行
- **速率限制**: 基于信号量的智能节流
- **内存效率**: 大型固件文件的流式下载

**可见性改进**:
- 计划准备显示: `[1/100] Vehicle-VIN-001 -> SUCCESS`
- 下载进度显示: `Vehicle-VIN-001: 正在从S3下载固件...`
- 文件大小确认: `Vehicle-VIN-001: 已下载2.1KB固件`
- 状态更新显示: `Vehicle-VIN-001: 作业执行成功`

---

### scripts/explore_jobs.py
**目的**: 使用原生boto3 API进行监控和故障排除的AWS IoT作业交互式探索。

**菜单选项**:
1. **列出所有作业** - 通过并行扫描跨所有状态的概览
2. **探索特定作业** - 带清晰JSON格式的详细作业配置
3. **探索作业执行** - 使用IoT Jobs Data API的单个设备进度
4. **列出作业执行** - 带并行状态检查的作业的所有执行
5. **取消作业** - 通过影响分析和教育指导取消活动作业
6. **删除作业** - 通过自动强制标志处理删除已完成/已取消的作业
7. **查看统计信息** - 带健康评估和建议的全面作业分析

**功能**:
- **原生boto3实现**: 直接API集成以获得更好的性能
- **并行作业扫描**: 跨所有作业状态的并发状态检查
- **清晰的JSON显示**: 正确格式化的作业文档，无转义字符
- 颜色编码的状态指示器
- 带可用作业列表的交互式作业选择
- 详细的预签名URL配置显示
- 带颜色编码的执行摘要统计信息
- **增强的错误处理**: 强大的boto3异常管理
- 连续探索循环
- **作业生命周期管理**: 带安全确认的取消和删除操作
- **高级分析**: 带健康评估的全面统计信息

**取消作业功能**:
- 扫描活动作业（IN_PROGRESS, SCHEDULED）
- 显示作业详细信息和目标计数
- 按状态的执行计数影响分析（QUEUED, IN_PROGRESS, SUCCEEDED, FAILED）
- 解释何时以及为何取消作业的教育内容
- 需要"CANCEL"才能继续的安全确认
- 用于审计跟踪的可选取消注释
- 实时状态更新

**删除作业功能**:
- 扫描可删除的作业（COMPLETED, CANCELED）
- 显示作业完成时间戳
- 检查执行历史以确定是否需要强制标志
- 关于删除影响的教育内容
- 存在执行时的自动强制标志
- 需要"DELETE"才能继续的安全确认
- 解释取消和删除操作之间的区别

**查看统计信息功能**:
- 全面的作业概览（状态、创建/完成日期、目标）
- 按状态百分比的执行统计信息
- 成功/失败率计算
- 所有执行状态的详细分解
- 健康评估（优秀≥95%，良好≥80%，差≥50%，严重<50%）
- 关于执行状态和失败模式的教育内容
- 基于作业状态的上下文感知建议:
  - 无执行: 检查设备连接和组成员资格
  - 提前取消: 审查取消原因
  - 设备已删除: 验证设备存在
  - 进行中: 等待和监控
  - 高失败率: 调查并考虑取消
  - 中等失败: 密切监控
  - 优秀性能: 记录成功模式

**性能改进**:
- **并行处理**: 非调试模式下的并发操作
- **智能分页**: 高效处理大型作业列表
- **速率限制**: 使用信号量的适当API节流

---

### scripts/manage_packages.py
**目的**: 使用原生boto3 API全面管理AWS IoT软件包、设备跟踪和版本回滚。

**操作**:
1. **创建包** - 创建新的软件包容器
2. **创建版本** - 通过S3固件上传和发布添加版本（带学习时刻）
3. **列出包** - 显示带交互式描述选项的包
4. **描述包** - 显示带版本探索的包详细信息
5. **描述版本** - 显示特定版本详细信息和Amazon S3工件
6. **检查配置** - 查看包配置状态和IAM角色
7. **启用配置** - 通过IAM角色创建启用自动影子更新
8. **禁用配置** - 禁用自动影子更新
9. **检查设备版本** - 检查特定设备的$package影子（多设备支持）
10. **恢复版本** - 使用Fleet Indexing的全车队版本回滚

**关键功能**:
- **Amazon S3集成**: 带版本控制的自动固件上传
- **交互式导航**: 列表、描述和版本操作之间的无缝流程
- **包配置管理**: 控制Jobs-to-Shadow集成
- **设备跟踪**: 单个设备包版本检查
- **车队回滚**: 使用Fleet Indexing查询的版本恢复
- **教育方法**: 整个工作流程中的学习时刻
- **IAM角色管理**: 包配置的自动角色创建

**包配置**:
- **检查状态**: 显示启用/禁用状态和IAM角色ARN
- **启用**: 创建具有$package影子权限的IoTPackageConfigRole
- **禁用**: 在作业完成时停止自动影子更新
- **教育**: 解释Jobs-to-Shadow集成和IAM要求

**设备版本跟踪**:
- **多设备支持**: 按顺序检查多个设备
- **$package影子检查**: 显示当前固件版本和元数据
- **时间戳显示**: 每个包的最后更新信息
- **错误处理**: 缺少设备或影子的清晰消息

**版本回滚**:
- **Fleet Indexing查询**: 按物品类型和版本查找设备
- **设备列表预览**: 显示将被恢复的设备（前10个+计数）
- **需要确认**: 输入'REVERT'以继续影子更新
- **单个设备状态**: 显示每个设备的恢复成功/失败
- **进度跟踪**: 带成功计数的实时更新状态
- **教育**: 解释回滚概念和影子管理

**回滚可见性**:
- 设备预览: `1. Vehicle-VIN-001`, `2. Vehicle-VIN-002`, `... 还有90个设备`
- 单个结果: `Vehicle-VIN-001: 已恢复到版本1.0.0`
- 失败尝试: `Vehicle-VIN-002: 恢复失败`

**学习重点**:
- 从创建到回滚的完整固件生命周期
- 包配置和自动影子更新
- 设备库存管理和跟踪
- 用于版本管理操作的Fleet Indexing

---

### scripts/manage_dynamic_groups.py
**目的**: 使用原生boto3 API通过Fleet Indexing验证全面管理动态物品组。

**操作**:
1. **创建动态组** - 两种创建方法:
   - **引导向导**: 交互式标准选择
   - **自定义查询**: 直接Fleet Indexing查询输入
2. **列出动态组** - 显示所有组及成员计数和查询
3. **删除动态组** - 带确认的安全删除
4. **测试查询** - 验证自定义Fleet Indexing查询

**创建方法**:
- **引导向导**（全部可选）:
  - 国家: 单个或多个（例如: US,CA,MX）
  - 物品类型: 车辆类别（例如: SedanVehicle）
  - 版本: 单个或多个（例如: 1.0.0,1.1.0）
  - 电池电量: 比较（例如: >50, <30, =75）
- **自定义查询**: 直接Fleet Indexing查询字符串输入

**功能**:
- **双创建模式**: 引导向导或自定义查询输入
- 智能组命名（自动生成或自定义）
- Fleet Indexing查询构建和验证
- **实时设备匹配预览**（创建前显示匹配的设备）
- 现有组的成员计数显示
- 带确认提示的安全删除
- 自定义查询测试功能
- 查询验证防止空组创建

**查询示例**:
- 单一标准: `thingTypeName:SedanVehicle AND attributes.country:US`
- 多个标准: `thingTypeName:SedanVehicle AND attributes.country:(US OR CA) AND shadow.reported.batteryStatus:[50 TO *]`
- 包版本: `shadow.name.\$package.reported.SedanVehicle.version:1.1.0`
- 自定义复杂: `(thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]`

---

### scripts/check_syntax.py
**目的**: CI/CD管道的发布前语法验证。

**检查**:
- 所有脚本的Python语法验证
- 导入可用性验证
- requirements.txt验证
- 依赖项列表

**用法**: 由GitHub Actions工作流自动运行

---

## 脚本依赖项

### 所需的Python包
- `boto3>=1.40.27` - Python的AWS SDK（包工件支持的最新版本）
- `colorama>=0.4.4` - 终端颜色
- `requests>=2.25.1` - Amazon S3下载的HTTP请求

### 使用的AWS服务
- **AWS IoT Core** - 物品管理、作业、影子
- **AWS IoT Device Management** - 软件包、Fleet Indexing
- **Amazon S3** - 带版本控制的固件存储
- **AWS Identity and Access Management (IAM)** - 安全访问的角色和策略

### AWS凭证要求
- 通过以下方式配置的凭证:
  - `aws configure`（AWS CLI）
  - 环境变量（AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY）
  - IAM角色（用于EC2/Lambda执行）
  - AWS凭证文件
- AWS IoT、Amazon S3和IAM操作的适当IAM权限
- 区域配置（AWS_DEFAULT_REGION环境变量或凭证）

## 教育功能

### 学习时刻
每个脚本都包含解释以下内容的教育暂停:
- AWS IoT概念和架构
- 设备管理最佳实践
- 安全考虑
- 可扩展性模式

### 进度跟踪
- 实时操作状态
- 成功/失败计数
- 性能指标（TPS、持续时间）
- 颜色编码输出以便于阅读

### 调试模式
在所有脚本中可用:
- 显示所有带参数的AWS SDK（boto3）API调用
- 以JSON格式显示完整的API响应
- 提供带完整堆栈跟踪的详细错误信息
- **顺序处理**: 顺序运行操作以获得清晰的调试输出
- 帮助排除故障和学习AWS API

## 性能特征

### 速率限制
脚本遵守AWS API限制:
- 物品操作: 80 TPS（100 TPS限制）
- 物品类型: 8 TPS（10 TPS限制）
- 动态组: 4 TPS（5 TPS限制）
- 作业执行: 150 TPS（200 TPS限制）
- 包操作: 8 TPS（10 TPS限制）

### 并行处理
- **原生boto3集成**: 直接AWS SDK调用以获得更好的性能
- 用于并发操作的ThreadPoolExecutor（非调试模式时）
- **智能速率限制**: 遵守AWS API限制的信号量
- **线程安全进度跟踪**: 并发操作监控
- **增强的错误处理**: 强大的boto3 ClientError异常管理
- **调试模式覆盖**: 调试模式下的顺序处理以获得清晰的输出

### 内存管理
- 大文件的流式下载
- 临时文件清理
- 高效的JSON解析
- 退出时的资源清理

---

### scripts/manage_commands.py
**目的**: 使用原生boto3 API全面管理AWS IoT Commands，用于向IoT设备发送实时命令。

**操作**:
1. **创建命令** - 创建带有效负载格式定义的新命令模板
2. **列出命令** - 显示所有命令模板（预定义和自定义）
3. **查看命令详细信息** - 显示完整的命令模板规范
4. **删除命令** - 通过安全确认删除自定义命令模板
5. **执行命令** - 向设备或物品组发送命令
6. **查看命令状态** - 监控命令执行进度和结果
7. **查看命令历史** - 通过过滤浏览过去的命令执行
8. **取消命令** - 取消待处理或进行中的命令执行
9. **启用/禁用调试模式** - 切换详细的API日志记录
10. **退出** - 退出脚本

**关键功能**:
- **原生boto3实现**: 直接AWS IoT Commands API集成
- **预定义的汽车模板**: 六个即用型车辆命令模板
- **命令模板管理**: 创建、列出、查看和删除命令模板
- **命令执行**: 向单个设备或物品组发送命令
- **状态监控**: 带进度指示器的实时命令执行跟踪
- **命令历史**: 浏览和过滤过去的命令执行
- **命令取消**: 取消待处理或进行中的命令
- **IoT Core脚本集成**: 与certificate_manager和mqtt_client_explorer无缝集成
- **MQTT主题文档**: 完整的主题结构参考
- **设备模拟示例**: 成功和失败响应有效负载
- **教育方法**: 整个工作流程中的学习时刻
- **多语言支持**: 6种语言的完整i18n支持

**预定义的汽车命令模板**:
脚本包含六个用于常见车辆操作的预定义命令模板:

1. **vehicle-lock** - 远程锁定车辆门
   - 有效负载: `{"action": "lock", "vehicleId": "string"}`
   - 用例: 安全的远程门锁

2. **vehicle-unlock** - 远程解锁车辆门
   - 有效负载: `{"action": "unlock", "vehicleId": "string"}`
   - 用例: 访问的远程门解锁

3. **start-engine** - 远程启动车辆引擎
   - 有效负载: `{"action": "start", "vehicleId": "string", "duration": "number"}`
   - 用例: 气候控制的远程引擎启动

4. **stop-engine** - 远程停止车辆引擎
   - 有效负载: `{"action": "stop", "vehicleId": "string"}`
   - 用例: 紧急引擎关闭

5. **set-climate** - 设置车辆气候温度
   - 有效负载: `{"action": "setClimate", "vehicleId": "string", "temperature": "number", "unit": "string"}`
   - 用例: 车辆温度预调节

6. **activate-horn** - 激活车辆喇叭
   - 有效负载: `{"action": "horn", "vehicleId": "string", "duration": "number"}`
   - 用例: 车辆位置协助

**命令模板管理**:

**创建命令模板**:
- 命令名称、描述和有效负载格式的交互式提示
- 有效负载结构的JSON模式验证
- AWS-IoT命名空间配置
- 带contentType的二进制blob有效负载处理
- 自动ARN生成和显示
- 针对AWS IoT Commands要求的验证:
  - 名称: 1-128个字符，字母数字/连字符/下划线，必须以字母数字开头
  - 描述: 1-256个字符
  - 有效负载: 有效的JSON模式，最大10KB复杂度

**列出命令模板**:
- 显示预定义和自定义模板
- 颜色编码的表格格式，包含:
  - 模板名称
  - 描述
  - 创建日期
  - 模板ARN
  - 状态（ACTIVE, DEPRECATED, PENDING_DELETION）
- 查看模板详细信息的交互式导航
- 大型模板列表的分页支持

**查看命令详细信息**:
- 完整的有效负载格式规范显示
- 参数名称、类型和约束
- 必需字段与可选字段
- 示例参数值
- 模板元数据（创建日期、ARN、状态）
- 有效负载结构的清晰JSON格式

**删除命令模板**:
- 需要"DELETE"才能继续的安全确认
- 验证没有活动命令使用该模板
- 防止删除预定义模板
- 删除失败的清晰错误消息
- 模板资源的自动清理

**命令执行**:

**执行命令**:
- 从可用模板中交互式选择命令模板
- 目标选择:
  - 单个设备（物品名称）
  - 物品组（组名称）
- 目标验证:
  - IoT注册表中的设备存在检查
  - 带成员计数显示的物品组验证
- 匹配模板有效负载格式的参数收集
- 可配置的执行超时（默认60秒）
- 自动MQTT主题发布到:
  - `$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/json`
- 成功显示包含:
  - 命令执行ID
  - 初始状态（CREATED/IN_PROGRESS）
  - MQTT主题信息
- 多目标支持（为每个目标创建单独的执行）

**命令状态监控**:

**查看命令状态**:
- 使用GetCommandExecution API的实时状态检索
- 状态显示包括:
  - 命令执行ID
  - 目标设备/组名称
  - 当前状态（CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED）
  - 创建时间戳
  - 最后更新时间戳
- IN_PROGRESS状态的进度指示器:
  - 动画进度显示
  - 自创建以来经过的时间
- 已完成命令信息:
  - 最终状态（SUCCEEDED/FAILED）
  - 执行持续时间
  - 状态原因（如果提供）
  - 完成时间戳
- 颜色编码的状态指示器:
  - 绿色: SUCCEEDED
  - 黄色: IN_PROGRESS, CREATED
  - 红色: FAILED, TIMED_OUT, CANCELED

**查看命令历史**:
- 全面的命令执行历史
- 过滤选项:
  - 设备名称过滤器
  - 状态过滤器（CREATED, IN_PROGRESS, SUCCEEDED, FAILED, TIMED_OUT, CANCELED）
  - 时间范围过滤器（开始/结束时间戳）
- 分页支持:
  - 可配置的页面大小（1-100，默认50）
  - 下一页导航
  - 总计数显示
- 历史显示包括:
  - 命令名称
  - 目标设备/组
  - 执行状态
  - 创建时间
  - 完成时间（如果适用）
  - 执行持续时间
- 带信息性消息的空历史处理
- 颜色编码状态以便于扫描

**命令取消**:

**取消命令**:
- 交互式命令执行ID输入
- 需要"CANCEL"才能继续的安全确认
- 向AWS IoT提交取消请求
- 状态更新验证（CANCELED）
- 已完成命令的拒绝处理:
  - 已完成命令的清晰错误消息
  - 当前命令状态显示
- 失败信息显示:
  - 失败原因
  - 当前命令状态
  - 故障排除建议

**IoT Core脚本集成**:

脚本提供全面的集成指导，用于使用AWS IoT Core脚本模拟设备端命令处理:

**Certificate Manager集成**（`certificate_manager.py`）:
- 设备证书创建和管理
- 证书到策略关联
- 证书到物品附件
- MQTT连接的身份验证设置
- 分步终端设置说明:
  1. 打开新终端窗口（终端2）
  2. 从研讨会环境复制AWS凭证
  3. 导航到IoT Core脚本目录
  4. 运行certificate_manager.py设置设备身份验证

**MQTT Client Explorer集成**（`mqtt_client_explorer.py`）:
- 命令主题订阅设置
- 实时命令接收
- 响应有效负载发布
- 成功/失败模拟
- 分步集成工作流:
  1. 订阅命令请求主题: `$aws/commands/things/<ThingName>/executions/+/request/#`
  2. 接收带执行ID的命令有效负载
  3. 将执行结果发布到响应主题: `$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/json`
  4. 可选择订阅accepted/rejected主题以进行确认

**设备模拟示例**:

脚本提供用于模拟设备响应的完整示例有效负载:

**成功响应示例**:
```json
{
  "status": "SUCCEEDED",
  "executionId": "<ExecutionId>",
  "statusReason": "车辆门成功锁定",
  "timestamp": 1701518710000
}
```

**失败响应示例**:
```json
{
  "status": "FAILED",
  "executionId": "<ExecutionId>",
  "statusReason": "无法锁定车辆 - 门传感器故障",
  "timestamp": 1701518710000
}
```

**有效状态值**: SUCCEEDED, FAILED, IN_PROGRESS, TIMED_OUT, REJECTED

**MQTT主题结构**:

脚本记录了AWS IoT Commands的完整MQTT主题结构:

**命令请求主题**（设备订阅以接收命令）:
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/request
```

**命令响应主题**（设备发布执行结果）:
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/<PayloadFormat>
```

**响应接受主题**（设备订阅以进行确认）:
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/accepted
```

**响应拒绝主题**（设备订阅以进行拒绝通知）:
```
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected/<PayloadFormat>
$aws/commands/things/<ThingName>/executions/<ExecutionId>/response/rejected
```

**主题组件说明**:
- `<ThingName>`: IoT物品名称或MQTT客户端ID
- `<ExecutionId>`: 每个命令执行的唯一标识符（使用`+`通配符订阅所有）
- `<PayloadFormat>`: 格式指示器（json, cbor） - 如果不是JSON/CBOR可以省略
- 通配符订阅: `$aws/commands/things/<ThingName>/executions/+/request/#`

**AWS IoT Test Client替代方案**:
- mqtt_client_explorer的基于控制台的替代方案
- 通过AWS IoT Console → Test → MQTT test client访问
- 订阅命令主题
- 发布响应有效负载
- 对于没有本地脚本的快速测试很有用

**学习时刻**:

脚本包含在关键操作后自动出现的上下文学习时刻:

1. **什么是命令模板？** - 在第一次模板创建后显示
   - 解释命令模板目的和结构
   - 描述有效负载格式要求
   - 与其他AWS IoT功能比较

2. **Commands vs Device Shadow vs Jobs** - 在第一次命令执行后显示
   - 显示何时使用每个功能的比较表
   - Commands: 即时、实时设备操作（秒）
   - Device Shadow: 期望状态同步（最终一致性）
   - Jobs: 长时间运行的操作、固件更新（分钟到小时）
   - 每个功能的用例示例

3. **MQTT主题结构** - 在显示mqtt_client_explorer集成时显示
   - 完整的主题模式文档
   - 请求/响应主题说明
   - 通配符订阅示例
   - 主题组件描述

4. **命令执行生命周期** - 在查看命令状态后显示
   - 状态转换流程（CREATED → IN_PROGRESS → SUCCEEDED/FAILED）
   - 超时处理
   - 取消行为
   - 监控最佳实践

5. **最佳实践** - 在查看命令历史后显示
   - 命令命名约定
   - 超时配置指导
   - 错误处理策略
   - 监控和警报建议

6. **控制台集成** - 与Console Checkpoint提醒一起显示
   - AWS IoT Console导航
   - 命令模板验证
   - 执行时间线查看
   - CLI与Console比较

**错误处理**:

脚本实现了带有用户友好消息的全面错误处理:

**验证错误**:
- 命令名称验证（长度、字符、格式）
- 描述验证（长度、内容）
- 有效负载格式验证（JSON模式、复杂度）
- 目标验证（设备/组存在）
- 参数验证（类型、必需字段）
- 带纠正指导的清晰错误消息

**AWS API错误**:
- ResourceNotFoundException: 未找到命令或目标
- InvalidRequestException: 无效的有效负载或参数
- ThrottlingException: 超过速率限制，带重试指导
- UnauthorizedException: 权限不足
- 速率限制的指数退避
- 瞬态错误的自动重试（最多3次尝试）
- 带故障排除建议的详细错误消息

**网络错误**:
- 连接问题检测
- AWS凭证验证指导
- 区域配置检查
- 带用户提示的重试选项

**状态错误**:
- 已完成命令的取消
- 使用中模板的删除
- 无效的状态转换
- 当前状态的清晰说明

**调试模式**:
- 显示所有带参数的AWS SDK（boto3）API调用
- 以JSON格式显示完整的API响应
- 提供带完整堆栈跟踪的详细错误信息
- 帮助排除故障和学习AWS API
- 在脚本执行期间切换开/关

**性能特征**:
- **原生boto3集成**: 直接AWS SDK调用以获得更好的性能
- **速率限制**: 遵守AWS IoT Commands API限制
- **高效分页**: 处理大型命令列表和历史
- **内存管理**: 高效的JSON解析和资源清理
- **错误恢复**: 带指数退避的自动重试

**教育重点**:
- 从模板创建到执行的完整命令生命周期
- 实时命令传递和确认
- 使用IoT Core脚本的设备模拟
- MQTT主题结构和消息流
- Commands vs Shadow vs Jobs决策指导
- 生产部署的最佳实践

**故障排除指南**:

**常见问题和解决方案**:

1. **设备未接收命令**
   - 验证设备已订阅命令请求主题
   - 检查MQTT连接状态
   - 确认证书和策略权限
   - 验证物品名称与目标匹配
   - 确保在执行命令之前设备模拟器正在运行

2. **模板验证错误**
   - 检查JSON模式语法
   - 验证有效负载格式复杂度（最大10KB）
   - 确保定义了必需字段
   - 验证参数类型和约束

3. **命令执行失败**
   - 验证目标设备/组存在
   - 检查AWS IoT Commands的IAM权限
   - 确认AWS区域配置
   - 审查命令超时设置

4. **状态未更新**
   - 验证设备已将响应发布到正确的主题
   - 检查响应有效负载格式
   - 确认执行ID匹配
   - 审查设备日志以查找错误

5. **取消失败**
   - 验证命令尚未完成
   - 检查命令执行状态
   - 确认取消的IAM权限
   - 审查当前命令状态

**集成工作流**（正确顺序）:

⚠️ **关键**: 在执行命令之前，设备模拟器必须正在运行并订阅命令主题。命令默认是临时的 - 如果在发布命令时没有设备在监听，它将丢失。

1. **首先打开终端2** - 复制AWS凭证
2. 导航到IoT Core脚本目录
3. 运行`certificate_manager.py`设置设备身份验证
4. 运行`mqtt_client_explorer.py`订阅命令主题
5. **验证设备模拟器已准备就绪** - 应显示"已订阅命令主题"
6. **现在打开终端1** - 运行`manage_commands.py`
7. 创建命令模板
8. 执行针对设备的命令
9. **设备模拟器**（终端2）接收命令并显示有效负载
10. **设备模拟器**将确认发布到响应主题
11. 返回终端1查看更新的命令状态

**为什么这个顺序很重要**: 如果没有启用持久会话，MQTT消息不会为离线设备排队。当AWS IoT发布命令时，设备必须主动订阅命令主题，否则命令将不会被传递。

**用例**:

**全车队紧急命令**:
- 向区域内的所有车辆发送紧急停止命令
- 在整个车队执行安全召回
- 协调对安全威胁的响应
- 实时全车队配置更新

**远程诊断和控制**:
- 为客户支持远程锁定/解锁车辆
- 在客户到达前调整气候设置
- 激活喇叭以协助车辆定位
- 按需收集诊断数据

**生产部署模式**:
- 命令模板版本控制和管理
- 多区域命令执行
- 命令执行监控和警报
- 与车队管理系统集成
- 合规性和审计日志记录

**Commands vs Device Shadow vs Jobs决策指南**:

使用**Commands**当:
- 需要立即操作（秒响应时间）
- 需要实时设备控制
- 期望快速确认
- 设备必须在线
- 示例: 锁定/解锁、喇叭激活、紧急停止

使用**Device Shadow**当:
- 需要期望状态同步
- 需要离线设备支持
- 可接受最终一致性
- 状态持久性重要
- 示例: 温度设置、配置、期望状态

使用**Jobs**当:
- 需要长时间运行的操作（分钟到小时）
- 需要固件更新
- 批量设备管理
- 进度跟踪重要
- 示例: 固件更新、证书轮换、批量配置

**AWS服务集成**:
- **AWS IoT Core**: 命令模板存储和执行
- **AWS IoT Device Management**: 车队管理和目标定位
- **AWS Identity and Access Management (IAM)**: 权限和策略
- **Amazon CloudWatch**: 监控和日志记录（可选）

**安全考虑**:
- 命令操作的IAM权限
- 基于证书的设备身份验证
- MQTT主题的基于策略的授权
- 传输中的命令有效负载加密
- 合规性的审计日志记录

**成本优化**:
- 命令按执行收费
- 命令模板没有存储成本
- 高效的目标定位减少不必要的执行
- 监控命令历史以了解使用模式
- 考虑批量操作以提高成本效率
