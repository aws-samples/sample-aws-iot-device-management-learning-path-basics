# 使用示例

本文档提供AWS IoT Device Management常见场景的实用示例。

## 快速入门示例

### 基本车队设置
```bash
# 1. 创建基础设施
python scripts/provision_script.py
# 选择: SedanVehicle,SUVVehicle
# 版本: 1.0.0,1.1.0
# 地区: North America
# 国家: US,CA
# 设备: 100

# 2. 创建动态组
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 国家: US
# 物品类型: SedanVehicle
# 电池电量: <30

# 3. 创建固件更新作业
python scripts/create_job.py
# 选择: USFleet组
# 软件包: SedanVehicle v1.1.0

# 4. 模拟设备更新
python scripts/simulate_job_execution.py
# 成功率: 85%
# 处理: 所有执行
```

### 版本回滚场景
```bash
# 将所有SedanVehicle设备回滚到版本1.0.0
python scripts/manage_packages.py
# 选择: 10. 恢复设备版本
# 物品类型: SedanVehicle
# 目标版本: 1.0.0
# 确认: REVERT
```

### 作业监控
```bash
# 监控作业进度
python scripts/explore_jobs.py
# 选项1: 列出所有作业
# 选项4: 列出特定作业的作业执行
```

## 高级场景

### 多区域部署
```bash
# 在多个区域中配置
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# 在北美创建500个设备

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# 在欧洲创建300个设备
```

### 分阶段推出
```bash
# 1. 创建测试组
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 国家: US
# 物品类型: SedanVehicle
# 版本: 1.0.0
# 自定义名称: TestFleet_SedanVehicle_US

# 2. 首先部署到测试组
python scripts/create_job.py
# 选择: TestFleet_SedanVehicle_US
# 软件包: SedanVehicle v1.1.0

# 3. 监控测试部署
python scripts/simulate_job_execution.py
# 成功率: 95%

# 4. 验证后部署到生产环境
python scripts/create_job.py
# 选择: USFleet
# 软件包: SedanVehicle v1.1.0
```

### 基于电池的维护
```bash
# 创建低电量组
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 方法: 1 (引导向导)
# 国家: (留空表示全部)
# 物品类型: (留空表示全部)
# 电池电量: <20
# 自定义名称: LowBatteryDevices

# 创建维护作业
python scripts/create_job.py
# 选择: LowBatteryDevices
# 软件包: MaintenanceFirmware v2.0.0
```

### 高级自定义查询
```bash
# 使用自定义查询创建复杂组
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 方法: 2 (自定义查询)
# 查询: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# 组名称: USVehicles_MidBattery
```

### 软件包管理
```bash
# 创建新软件包和版本
python scripts/manage_packages.py
# 操作: 1 (创建软件包)
# 软件包名称: TestVehicle

# 通过S3上传添加版本
# 操作: 2 (创建版本)
# 软件包名称: TestVehicle
# 版本: 2.0.0

# 检查软件包详细信息
# 操作: 4 (描述软件包)
# 软件包名称: TestVehicle
```

## 开发工作流

### 测试新固件
```bash
# 1. 配置测试环境
python scripts/provision_script.py
# 物品类型: TestSensor
# 版本: 1.0.0,2.0.0-beta
# 国家: US
# 设备: 10

# 2. 创建beta测试组
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 物品类型: TestSensor
# 版本: 1.0.0
# 自定义名称: BetaTestGroup

# 3. 部署beta固件
python scripts/create_job.py
# 选择: BetaTestGroup
# 软件包: TestSensor v2.0.0-beta

# 4. 使用高失败率进行测试模拟
python scripts/simulate_job_execution.py
# 成功率: 60%

# 5. 分析结果
python scripts/explore_jobs.py
# 选项4: 列出作业执行
```

### 测试后清理
```bash
# 清理测试资源
python scripts/cleanup_script.py
# 选项1: 所有资源
# 确认: DELETE
```

## 车队管理模式

### 地理部署
```bash
# 按大陆配置
python scripts/provision_script.py
# 大陆: 1 (北美)
# 国家: 3 (前3个国家)
# 设备: 1000

# 创建特定国家组 (自动创建为USFleet, CAFleet, MXFleet)
# 部署特定区域固件
python scripts/create_job.py
# 选择: USFleet,CAFleet
# 软件包: RegionalFirmware v1.2.0
```

### 设备类型管理
```bash
# 配置多种车辆类型
python scripts/provision_script.py
# 物品类型: SedanVehicle,SUVVehicle,TruckVehicle
# 版本: 1.0.0,1.1.0,2.0.0
# 设备: 500

# 创建特定类型的动态组
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 物品类型: TruckVehicle
# 国家: US,CA
# 自定义名称: NorthAmericaTrucks

# 部署卡车专用固件
python scripts/create_job.py
# 选择: NorthAmericaTrucks
# 软件包: TruckVehicle v2.0.0
```

### 维护调度
```bash
# 查找需要更新的设备
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 物品类型: SedanVehicle
# 版本: 1.0.0  # 旧版本
# 自定义名称: SedanVehicle_NeedsUpdate

# 安排维护窗口部署
python scripts/create_job.py
# 选择: SedanVehicle_NeedsUpdate
# 软件包: SedanVehicle v1.1.0

# 监控部署进度
python scripts/explore_jobs.py
# 选项1: 列出所有作业 (检查状态)
```

## 故障排除示例

### 失败作业恢复
```bash
# 1. 检查作业状态
python scripts/explore_jobs.py
# 选项2: 探索特定作业
# 输入有失败的作业ID

# 2. 检查单个设备失败
python scripts/explore_jobs.py
# 选项3: 探索作业执行
# 输入作业ID和失败的设备名称

# 3. 回滚失败的设备
python scripts/manage_packages.py
# 选择: 10. 恢复设备版本
# 物品类型: SedanVehicle
# 目标版本: 1.0.0  # 之前的工作版本
```

### 设备状态验证
```bash
# 检查当前固件版本
python scripts/manage_dynamic_groups.py
# 操作: 1 (创建)
# 物品类型: SedanVehicle
# 版本: 1.1.0
# 自定义名称: SedanVehicle_v1_1_0_Check

# 验证组成员资格 (应与预期计数匹配)
python scripts/explore_jobs.py
# 用于验证设备状态
```

### 性能测试
```bash
# 使用大量设备进行测试
python scripts/provision_script.py
# 设备: 5000

# 测试作业执行性能
python scripts/simulate_job_execution.py
# 处理: 全部
# 成功率: 90%
# 监控执行时间和TPS
```

## 特定环境示例

### 开发环境
```bash
# 开发用小规模
python scripts/provision_script.py
# 物品类型: DevSensor
# 版本: 1.0.0-dev
# 国家: US
# 设备: 5
```

### 预发布环境
```bash
# 预发布用中等规模
python scripts/provision_script.py
# 物品类型: SedanVehicle,SUVVehicle
# 版本: 1.0.0,1.1.0-rc
# 国家: US,CA
# 设备: 100
```

### 生产环境
```bash
# 生产用大规模
python scripts/provision_script.py
# 物品类型: SedanVehicle,SUVVehicle,TruckVehicle
# 版本: 1.0.0,1.1.0,1.2.0
# 大陆: 1 (北美)
# 国家: 全部
# 设备: 10000
```

## 集成示例

### CI/CD管道集成
```bash
# 语法检查 (自动化)
python scripts/check_syntax.py

# 自动化测试
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### 监控集成
```bash
# 导出作业指标
python scripts/explore_jobs.py --export-json > job_status.json

# 检查部署健康状况
python scripts/explore_jobs.py --health-check
```

## 最佳实践示例

### 渐进式推出
1. 从车队的5%开始 (测试组)
2. 监控24小时
3. 如果成功则扩展到25%
4. 验证后完全部署

### 回滚策略
1. 始终测试回滚程序
2. 保持以前的固件版本可用
3. 监控部署后的设备健康状况
4. 准备自动回滚触发器

### 资源管理
1. 测试后使用清理脚本
2. 监控AWS成本
3. 清理旧固件版本
4. 删除未使用的物品组
