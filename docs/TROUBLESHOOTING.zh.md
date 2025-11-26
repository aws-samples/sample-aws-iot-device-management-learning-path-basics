# 故障排除指南

本文档提供使用AWS IoT Device Management脚本时遇到的常见问题的解决方案。

## 常见问题

### AWS配置问题

#### 问题: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**解决方案**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

#### 问题: "Access Denied"错误
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**解决方案**: 确保您的AWS IAM用户/角色具有所需的权限:
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

#### 问题: "Region not configured"
```
You must specify a region
```

**解决方案**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

### 脚本执行问题

#### 问题: "No module named 'colorama'"
```
ModuleNotFoundError: No module named 'colorama'
```

**解决方案**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install colorama>=0.4.4 requests>=2.25.1
```

#### 问题: 脚本挂起或超时
**症状**: 脚本在执行期间似乎冻结

**解决方案**:
1. 启用调试模式以查看发生了什么:
   ```bash
   # When prompted, choose 'y' for debug mode
   🔧 Enable debug mode? [y/N]: y
   ```

2. 检查AWS服务限制和节流
3. 如有必要，减少并行工作线程
4. 检查网络连接

#### 问题: "Thing type deletion requires 5-minute wait"
```
InvalidRequestException: Thing type cannot be deleted until 5 minutes after deprecation
```

**解决方案**: 这是预期的行为。清理脚本会自动处理此问题:
1. 首先弃用物品类型
2. 等待5分钟
3. 然后删除它们

### 资源创建问题

#### 问题: "Thing group already exists"
```
ResourceAlreadyExistsException: Thing group already exists
```

**解决方案**: 这通常是无害的。脚本会检查现有资源，如果已存在则跳过创建。

#### 问题: "S3 bucket name already taken"
```
BucketAlreadyExists: The requested bucket name is not available
```

**解决方案**: 脚本使用时间戳来确保存储桶名称唯一。如果发生这种情况:
1. 等待几秒钟后重试
2. 检查是否有类似名称的现有存储桶

#### 问题: "Package version already exists"
```
ConflictException: Package version already exists
```

**解决方案**: 脚本通过首先检查现有版本来处理此问题。如果需要更新:
1. 使用新的版本号
2. 或先删除现有版本

### 作业执行问题

#### 问题: "No active jobs found"
```
❌ No active jobs found
```

**解决方案**:
1. 首先使用`scripts/create_job.py`创建作业
2. 验证作业状态: `scripts/explore_jobs.py`
3. 检查作业是否已取消或完成

#### 问题: "Failed to download artifact"
```
❌ Failed to download artifact: HTTP 403 Forbidden
```

**解决方案**:
1. 检查AWS IoT Jobs的AWS IAM角色权限
2. 验证预签名URL配置
3. 确保S3存储桶和对象存在
4. 检查预签名URL是否已过期(1小时限制)

#### 问题: "Job execution not found"
```
ResourceNotFoundException: Job execution not found
```

**解决方案**:
1. 验证作业ID和物品名称是否正确
2. 检查设备是否在目标物品组中
3. 确保作业仍处于活动状态(未完成/取消)

### Fleet Indexing问题

#### 问题: "Fleet Indexing queries return no results"
```
ℹ️ No devices currently match this query
```

**解决方案**:
1. 等待Fleet Indexing完成(可能需要几分钟)
2. 验证Fleet Indexing已启用
3. 检查查询语法
4. 确保设备具有预期的属性/影子

#### 问题: "Invalid Fleet Indexing query"
```
InvalidRequestException: Invalid query string
```

**解决方案**: 检查查询语法。常见问题:
- 对设备属性使用`attributes.fieldName`
- 对经典影子使用`shadow.reported.fieldName`
- 对命名影子使用`shadow.name.\\$package.reported.fieldName`
- 正确转义特殊字符

### 性能问题

#### 问题: "Rate limiting errors"
```
ThrottlingException: Rate exceeded
```

**解决方案**: 脚本具有内置的速率限制，但如果遇到此问题:
1. 启用调试模式以查看哪个API被限制
2. 减少脚本中的并行工作线程
3. 在操作之间添加延迟
4. 检查您账户的AWS服务限制

#### 问题: "Scripts running slowly"
**症状**: 操作花费的时间比预期长得多

**解决方案**:
1. 检查网络连接
2. 验证AWS区域在地理位置上是否接近
3. 启用调试模式以识别瓶颈
4. 考虑减少批处理大小

### 数据一致性问题

#### 问题: "Device shadows not updating"
```
❌ Failed to update device shadow
```

**解决方案**:
1. 检查IoT Data端点配置
2. 验证设备/物品是否存在
3. 确保影子更新中的JSON格式正确
4. 检查影子操作的AWS IAM权限

#### 问题: "Package configuration not working"
```
❌ Failed to update global package configuration
```

**解决方案**:
1. 验证IoTPackageConfigRole存在并具有适当的权限
2. 检查角色ARN格式是否正确
3. 确保在您的区域中启用了软件包配置

## 调试模式使用

在任何脚本中启用调试模式以进行详细的故障排除:

```bash
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

调试模式显示:
- 正在执行的所有AWS CLI命令
- API请求参数
- 完整的API响应
- 错误详细信息和堆栈跟踪

## 日志分析

### 成功的操作
查找这些指标:
- ✅ 成功操作的绿色复选标记
- 显示完成的进度计数器
- "completed successfully"消息

### 警告信号
注意这些模式:
- ⚠️ 黄色警告(通常不严重)
- "already exists"消息(通常无害)
- 超时警告

### 错误模式
常见错误指标:
- ❌ 失败的红色X标记
- "Failed to"消息
- 异常堆栈跟踪
- HTTP错误代码(403, 404, 500)

## 恢复程序

### 部分配置失败
如果配置中途失败:

1. **检查创建了什么**:
   ```bash
   python scripts/explore_jobs.py
   # Option 1: List all jobs
   ```

2. **如有必要进行清理**:
   ```bash
   python scripts/cleanup_script.py
   # Option 1: ALL resources
   ```

3. **重试配置**:
   ```bash
   python scripts/provision_script.py
   # Scripts handle existing resources gracefully
   ```

### 失败作业恢复
如果作业在执行期间失败:

1. **检查作业状态**:
   ```bash
   python scripts/explore_jobs.py
   # Option 2: Explore specific job
   ```

2. **检查单个失败**:
   ```bash
   python scripts/explore_jobs.py
   # Option 3: Explore job execution
   ```

3. **如有必要进行回滚**:
   ```bash
   python scripts/manage_packages.py
   # Select: 10. Revert Device Versions
   # Enter thing type and previous version
   ```

### 资源清理问题
如果清理失败:

1. **尝试选择性清理**:
   ```bash
   python scripts/cleanup_script.py
   # Option 2: Things only (then try groups)
   ```

2. **通过AWS控制台手动清理**:
   - AWS IoT Core → Manage → Things
   - AWS IoT Core → Manage → Thing groups
   - AWS IoT Core → Manage → Thing types
   - Amazon S3 → Buckets
   - AWS IAM → Roles

## 环境特定问题

### macOS问题
- **SSL警告**: 脚本自动抑制urllib3 SSL警告
- **Python版本**: 确保安装了Python 3.7+

### Windows问题
- **路径分隔符**: 脚本自动处理跨平台路径
- **PowerShell**: 使用具有适当执行策略的命令提示符或PowerShell

### Linux问题
- **权限**: 确保脚本具有执行权限
- **Python路径**: 可能需要使用`python3`而不是`python`

## AWS服务限制

### 默认限制(每个区域)
- **Things**: 每个账户500,000个
- **Thing Types**: 每个账户100个
- **Thing Groups**: 每个账户500个
- **Jobs**: 100个并发作业
- **API速率限制**: 
  - Thing操作: 100 TPS(脚本使用80 TPS)
  - 动态组: 5 TPS(脚本使用4 TPS)
  - 作业执行: 200 TPS(脚本使用150 TPS)
  - 软件包操作: 10 TPS(脚本使用8 TPS)

### 请求限制增加
如果您需要更高的限制:
1. 转到AWS支持中心
2. 为"Service limit increase"创建案例
3. 指定所需的AWS IoT Core限制

## 获取帮助

### 启用详细日志记录
大多数脚本支持详细模式:
```bash
🔧 Enable verbose mode? [y/N]: y
```

### 检查AWS服务健康状况
- [AWS服务健康仪表板](https://status.aws.amazon.com/)
- 检查您的特定区域是否存在AWS IoT Core问题

### 社区资源
- AWS IoT开发者论坛
- AWS文档
- GitHub Issues(针对特定于脚本的问题)

### 专业支持
- AWS支持(如果您有支持计划)
- AWS专业服务
- AWS合作伙伴网络顾问

## 预防提示

### 运行脚本之前
1. **验证AWS配置**: `aws sts get-caller-identity`
2. **检查权限**: 首先使用小操作进行测试
3. **查看资源限制**: 确保不会达到账户限制
4. **备份重要数据**: 如果修改现有资源

### 执行期间
1. **监控进度**: 注意错误模式
2. **不要中断**: 让脚本完成或谨慎使用Ctrl+C
3. **检查AWS控制台**: 验证资源是否按预期创建

### 执行后
1. **验证结果**: 使用探索脚本检查结果
2. **清理测试资源**: 对临时资源使用清理脚本
3. **监控成本**: 检查AWS账单是否有意外费用

## 国际化问题

### 问题: 脚本显示原始消息键而不是翻译文本
**症状**: 脚本显示`warnings.debug_warning`和`prompts.debug_mode`等文本，而不是实际消息

**示例**:
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

**根本原因**: 此问题发生在以下情况:
1. 语言选择器和目录结构之间的语言代码不匹配
2. `get_message()`函数中缺少嵌套键处理
3. 消息文件加载不正确

**解决方案**:

1. **验证语言代码映射**: 确保语言代码与目录结构匹配:
   ```
   i18n/
   ├── en/     # English
   ├── es/     # Spanish  
   ├── ja/     # Japanese
   ├── ko/     # Korean
   ├── pt/     # Portuguese
   ├── zh/     # Chinese
   ```

2. **检查get_message()实现**: 脚本应使用点表示法处理嵌套键:
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

3. **测试语言加载**:
   ```bash
   # Test with environment variable
   export AWS_IOT_LANG=en
   python scripts/cleanup_script.py
   
   # Test different languages
   export AWS_IOT_LANG=es  # Spanish
   export AWS_IOT_LANG=ja  # Japanese
   export AWS_IOT_LANG=zh  # Chinese
   ```

4. **验证消息文件存在**:
   ```bash
   # Check if translation files exist
   ls i18n/en/cleanup_script.json
   ls i18n/es/cleanup_script.json
   # etc.
   ```

**预防**: 添加新脚本或语言时:
- 使用工作脚本中正确的`get_message()`实现
- 确保语言代码与目录名称完全匹配
- 在部署前使用多种语言进行测试
- 使用`docs/templates/validation_scripts/`中的验证脚本

### 问题: 环境变量的语言选择不起作用
**症状**: 尽管设置了`AWS_IOT_LANG`，脚本仍始终提示选择语言

**解决方案**:
1. **检查环境变量格式**:
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

2. **验证环境变量已设置**:
   ```bash
   echo $AWS_IOT_LANG
   ```

3. **测试语言选择**:
   ```bash
   python3 -c "
   import sys, os
   sys.path.append('i18n')
   from language_selector import get_language
   print('Selected language:', get_language())
   "
   ```

### 问题: 新语言缺少翻译
**症状**: 脚本回退到英语或显示不支持语言的消息键

**解决方案**:
1. **添加语言目录**: 为新语言创建目录结构
2. **复制翻译文件**: 使用现有翻译作为模板
3. **更新语言选择器**: 将新语言添加到支持列表
4. **彻底测试**: 验证所有脚本都适用于新语言

有关详细说明，请参阅`docs/templates/NEW_LANGUAGE_TEMPLATE.md`。

## AWS IoT Jobs API限制

### 问题: 无法访问已完成作业的作业执行详细信息
**症状**: 尝试探索已完成、失败或已取消作业的作业执行详细信息时出错

**错误示例**:
```
❌ Error in Job Execution Detail upgradeSedanvehicle110_1761321268 on Vehicle-VIN-016: 
Job Execution has reached terminal state. It is neither IN_PROGRESS nor QUEUED
❌ Failed to get job execution details. Check job ID and thing name.
```

**根本原因**: AWS提供两个不同的API来访问作业执行详细信息:

1. **IoT Jobs Data API**(`iot-jobs-data`服务):
   - 端点: `describe_job_execution`
   - **限制**: 仅适用于`IN_PROGRESS`或`QUEUED`状态的作业
   - **错误**: 对已完成的作业返回"Job Execution has reached terminal state"
   - **用例**: 设计用于设备获取其当前作业指令

2. **IoT API**(`iot`服务):
   - 端点: `describe_job_execution`
   - **功能**: 适用于任何状态的作业(COMPLETED、FAILED、CANCELED等)
   - **无限制**: 可以访问历史作业执行数据
   - **用例**: 设计用于管理和监控所有作业执行

**解决方案**: explore_jobs脚本已更新为使用IoT API而不是IoT Jobs Data API。

**代码更改**:
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

**验证**: 修复后，您现在可以探索以下作业执行详细信息:
- ✅ COMPLETED作业
- ✅ FAILED作业  
- ✅ CANCELED作业
- ✅ IN_PROGRESS作业
- ✅ QUEUED作业
- ✅ 任何其他作业状态

**额外好处**:
- 访问历史作业执行数据
- 更好的失败部署故障排除功能
- 设备更新尝试的完整审计跟踪

### 问题: 执行详细信息中作业文档不可用
**症状**: 显示作业执行详细信息但缺少作业文档

**解决方案**: 脚本现在包含回退机制:
1. 首先尝试从执行详细信息获取作业文档
2. 如果不可用，则从主作业详细信息中检索
3. 如果作业文档不可用，则显示适当的消息

这确保您始终可以看到发送到设备的作业指令，无论作业状态或API限制如何。
