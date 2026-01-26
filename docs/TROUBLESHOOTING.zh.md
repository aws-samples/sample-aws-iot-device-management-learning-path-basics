# 故障排除指南

这份指南会帮你解决环境设置的问题。如果遇到脚本相关的问题，试试启用调试模式 - 它会给你详细的错误信息和指导。

## 环境设置

### AWS 凭证配置

#### 问题："Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**解决方法**:
```bash
# 配置你的 AWS 凭证
aws configure
# 输入：Access Key ID、Secret Access Key、区域、输出格式

# 验证一下配置
aws sts get-caller-identity
```

**其他方法**:
- 环境变量：`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`
- AWS 凭证文件：`~/.aws/credentials`
- IAM 角色（适用于 EC2/Lambda 执行）

---

### 区域配置

#### 问题："Region not configured" 或 "You must specify a region"

**解决方法**:
```bash
# 在 AWS CLI 中设置区域
aws configure set region us-east-1

# 或者用环境变量
export AWS_DEFAULT_REGION=us-east-1

# 验证一下区域
aws configure get region
```

**支持的区域**：任何有 AWS IoT Core 服务的区域都可以

---

### Python 依赖项

#### 问题："No module named 'colorama'" 或类似的导入错误
```
ModuleNotFoundError: No module named 'colorama'
```

**解决方法**:
```bash
# 安装所有依赖项
pip install -r requirements.txt

# 或者单独安装
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**验证安装**:
```bash
python -c "import boto3, colorama, requests; print('所有依赖项都装好了')"
```

---

### IAM 权限

#### 问题："Access Denied" 或 "User is not authorized" 错误
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**解决方法**：确保你的 AWS IAM 用户/角色有所需的权限：

**需要的 IAM 操作**:
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

**注意**：在生产环境中，记得遵循最小权限原则，适当限制资源访问。

---

## 获取帮助

### 脚本相关问题

如果运行脚本时遇到问题：

1. **启用调试模式** - 会显示详细的 API 调用和响应
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **仔细看错误消息** - 脚本会给你详细的指导

3. **留意教学提示** - 它们会解释概念和要求

4. **检查前置条件** - 大多数脚本需要先运行 `provision_script.py`

### 常见工作流程

```bash
# 1. 设置环境（只需一次）
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. 创建基础设施（先运行这个）
python scripts/provision_script.py

# 3. 根据需要运行其他脚本
python scripts/manage_packages.py
python scripts/create_job.py
# 等等

# 4. 完成后清理
python scripts/cleanup_script.py
```

### 其他资源

- **README.md** - 项目概述和快速入门指南
- **脚本 i18n 消息** - 你的语言的本地化指导
- **教学提示** - 脚本运行时的学习内容
- **AWS IoT 文档** - https://docs.aws.amazon.com/zh_cn/iot/
