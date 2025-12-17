# 故障排除指南

本指南涵盖环境设置问题。对于脚本特定问题，请在运行脚本时启用调试模式 - 它们提供上下文错误消息和指导。

## 环境设置

### AWS 凭证配置

#### 问题："Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**解决方案**:
```bash
# 配置 AWS 凭证
aws configure
# 输入：Access Key ID、Secret Access Key、区域、输出格式

# 验证配置
aws sts get-caller-identity
```

**替代方法**:
- 环境变量：`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`
- AWS 凭证文件：`~/.aws/credentials`
- IAM 角色（用于 EC2/Lambda 执行）

---

### 区域配置

#### 问题："Region not configured" 或 "You must specify a region"

**解决方案**:
```bash
# 在 AWS CLI 中设置区域
aws configure set region us-east-1

# 或使用环境变量
export AWS_DEFAULT_REGION=us-east-1

# 验证区域
aws configure get region
```

**支持的区域**：任何具有 IoT Core 服务可用性的 AWS 区域

---

### Python 依赖项

#### 问题："No module named 'colorama'" 或类似的导入错误
```
ModuleNotFoundError: No module named 'colorama'
```

**解决方案**:
```bash
# 安装所有依赖项
pip install -r requirements.txt

# 或单独安装
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**验证安装**:
```bash
python -c "import boto3, colorama, requests; print('所有依赖项已安装')"
```

---

### IAM 权限

#### 问题："Access Denied" 或 "User is not authorized" 错误
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**解决方案**：确保您的 AWS IAM 用户/角色具有所需权限：

**所需的 IAM 操作**:
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
                "s3:PutBucketTagging",
                "iam:GetRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:TagRole",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**注意**：对于生产环境，请遵循最小权限原则并适当限制资源。

---

## 获取帮助

### 脚本特定问题

如果在运行脚本时遇到问题：

1. **启用调试模式** - 显示详细的 API 调用和响应
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **阅读错误消息** - 脚本提供上下文指导

3. **查看教育性暂停** - 它们解释概念和要求

4. **验证先决条件** - 大多数脚本需要首先运行 `provision_script.py`

### 常见工作流程

```bash
# 1. 设置环境（一次性）
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. 创建基础设施（首先运行）
python scripts/provision_script.py

# 3. 根据需要运行其他脚本
python scripts/manage_packages.py
python scripts/create_job.py
# 等等

# 4. 完成后清理
python scripts/cleanup_script.py
```

### 其他资源

- **README.md** - 项目概述和快速入门
- **脚本 i18n 消息** - 您的语言的本地化指导
- **教育性暂停** - 脚本执行期间的上下文学习
- **AWS IoT 文档** - https://docs.aws.amazon.com/zh_cn/iot/
