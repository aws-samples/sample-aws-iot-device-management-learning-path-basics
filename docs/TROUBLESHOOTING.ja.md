# トラブルシューティングガイド

このガイドでは、環境設定に関する問題の解決方法をご紹介します。スクリプト実行中に問題が起きた場合は、デバッグモードを有効にしてみてください。状況に応じたエラーメッセージとガイダンスが表示されますよ。

## 環境設定

### AWS認証情報の設定

#### 問題: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**解決方法**:
```bash
# AWS認証情報を設定しましょう
aws configure
# 入力項目: Access Key ID、Secret Access Key、リージョン、出力形式

# 設定を確認してみましょう
aws sts get-caller-identity
```

**他の方法もあります**:
- 環境変数: `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`
- AWS認証情報ファイル: `~/.aws/credentials`
- IAMロール（EC2/Lambda実行用）

---

### リージョン設定

#### 問題: "Region not configured" または "You must specify a region"

**解決方法**:
```bash
# AWS CLIでリージョンを設定してみましょう
aws configure set region us-east-1

# または環境変数を使うこともできます
export AWS_DEFAULT_REGION=us-east-1

# リージョンを確認してみましょう
aws configure get region
```

**サポートされているリージョン**: IoT Coreサービスが利用可能な任意のAWSリージョンで使えます

---

### Python依存関係

#### 問題: "No module named 'colorama'" または類似のインポートエラー
```
ModuleNotFoundError: No module named 'colorama'
```

**解決方法**:
```bash
# すべての依存関係をインストールしましょう
pip install -r requirements.txt

# または個別にインストールすることもできます
pip install boto3>=1.40.27 colorama>=0.4.4 requests>=2.25.1
```

**インストールを確認してみましょう**:
```bash
python -c "import boto3, colorama, requests; print('すべての依存関係がインストールされました')"
```

---

### IAM権限

#### 問題: "Access Denied" または "User is not authorized" エラー
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**解決方法**: AWS IAMユーザーまたはロールに必要な権限があることを確認してください。

**必要なIAMアクション**:
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

**注意**: 本番環境では、最小権限の原則に従って、リソースを適切に制限することをお勧めします。

---

## ヘルプが必要な時は

### スクリプト実行中の問題

スクリプト実行中に問題が発生した場合は、以下を試してみてください:

1. **デバッグモードを有効にする** - 詳細なAPI呼び出しと応答が表示されます
   ```
   🔧 Enable debug mode? [y/N]: y
   ```

2. **エラーメッセージを読む** - スクリプトが状況に応じたガイダンスを提供してくれます

3. **教育的な一時停止を確認** - 概念や要件について説明が表示されます

4. **前提条件を確認** - ほとんどのスクリプトは、最初に `provision_script.py` を実行する必要があります

### 一般的なワークフロー

```bash
# 1. 環境を設定（最初の1回だけ）
aws configure
export AWS_DEFAULT_REGION=us-east-1
pip install -r requirements.txt

# 2. インフラストラクチャを作成（最初に実行してください）
python scripts/provision_script.py

# 3. 必要に応じて他のスクリプトを実行できます
python scripts/manage_packages.py
python scripts/create_job.py
# など

# 4. 完了したらクリーンアップしましょう
python scripts/cleanup_script.py
```

### 追加リソース

- **README.md** - プロジェクトの概要とクイックスタートガイド
- **スクリプトi18nメッセージ** - あなたの言語でのローカライズされたガイダンス
- **教育的な一時停止** - スクリプト実行中に学べるコンテキスト情報
- **AWS IoTドキュメント** - https://docs.aws.amazon.com/ja_jp/iot/
