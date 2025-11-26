# トラブルシューティングガイド

このドキュメントは、AWS IoT Device Managementスクリプトを使用する際に発生する一般的な問題の解決策を提供します。

## 一般的な問題

### AWS設定の問題

#### 問題: "Unable to locate credentials"
```
NoCredentialsError: Unable to locate credentials
```

**解決策**:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Verify configuration
aws sts get-caller-identity
```

#### 問題: "Access Denied"エラー
```
AccessDeniedException: User is not authorized to perform: iot:CreateThing
```

**解決策**: AWS IAMユーザー/ロールに必要な権限があることを確認してください:
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

#### 問題: "Region not configured"
```
You must specify a region
```

**解決策**:
```bash
# Set region in AWS CLI
aws configure set region us-east-1

# Or use environment variable
export AWS_DEFAULT_REGION=us-east-1
```

### スクリプト実行の問題

#### 問題: "No module named 'colorama'"
```
ModuleNotFoundError: No module named 'colorama'
```

**解決策**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install colorama>=0.4.4 requests>=2.25.1
```

#### 問題: スクリプトがハングまたはタイムアウトする
**症状**: スクリプトが実行中にフリーズしているように見える

**解決策**:
1. デバッグモードを有効にして何が起こっているかを確認します:
   ```bash
   # When prompted, choose 'y' for debug mode
   🔧 Enable debug mode? [y/N]: y
   ```

2. AWSサービスの制限とスロットリングを確認します
3. 必要に応じて並列ワーカーを減らします
4. ネットワーク接続を確認します

#### 問題: "Thing type deletion requires 5-minute wait"
```
InvalidRequestException: Thing type cannot be deleted until 5 minutes after deprecation
```

**解決策**: これは予想される動作です。クリーンアップスクリプトは次のように自動的に処理します:
1. まずモノタイプを非推奨にします
2. 5分間待機します
3. その後削除します

### リソース作成の問題

#### 問題: "Thing group already exists"
```
ResourceAlreadyExistsException: Thing group already exists
```

**解決策**: これは通常無害です。スクリプトは既存のリソースをチェックし、既に存在する場合は作成をスキップします。

#### 問題: "S3 bucket name already taken"
```
BucketAlreadyExists: The requested bucket name is not available
```

**解決策**: スクリプトはタイムスタンプを使用して一意のバケット名を確保します。これが発生した場合:
1. 数秒待ってから再試行します
2. 類似した名前の既存のバケットがないか確認します

#### 問題: "Package version already exists"
```
ConflictException: Package version already exists
```

**解決策**: スクリプトは最初に既存のバージョンをチェックすることでこれを処理します。更新が必要な場合:
1. 新しいバージョン番号を使用します
2. または最初に既存のバージョンを削除します

### ジョブ実行の問題

#### 問題: "No active jobs found"
```
❌ No active jobs found
```

**解決策**:
1. まず`scripts/create_job.py`を使用してジョブを作成します
2. ジョブのステータスを確認します: `scripts/explore_jobs.py`
3. ジョブがキャンセルまたは完了されたかどうかを確認します

#### 問題: "Failed to download artifact"
```
❌ Failed to download artifact: HTTP 403 Forbidden
```

**解決策**:
1. AWS IoT JobsのAWS IAMロール権限を確認します
2. 署名付きURL設定を確認します
3. S3バケットとオブジェクトが存在することを確認します
4. 署名付きURLの有効期限が切れていないか確認します（1時間制限）

#### 問題: "Job execution not found"
```
ResourceNotFoundException: Job execution not found
```

**解決策**:
1. ジョブIDとモノ名が正しいことを確認します
2. デバイスがターゲットのモノグループに含まれているか確認します
3. ジョブがまだアクティブであることを確認します（完了/キャンセルされていない）

### Fleet Indexingの問題

#### 問題: "Fleet Indexing queries return no results"
```
ℹ️ No devices currently match this query
```

**解決策**:
1. Fleet Indexingが完了するまで待ちます（数分かかる場合があります）
2. Fleet Indexingが有効になっていることを確認します
3. クエリ構文を確認します
4. デバイスに期待される属性/シャドウがあることを確認します

#### 問題: "Invalid Fleet Indexing query"
```
InvalidRequestException: Invalid query string
```

**解決策**: クエリ構文を確認してください。一般的な問題:
- デバイス属性には`attributes.fieldName`を使用します
- クラシックシャドウには`shadow.reported.fieldName`を使用します
- 名前付きシャドウには`shadow.name.\\$package.reported.fieldName`を使用します
- 特殊文字を適切にエスケープします

### パフォーマンスの問題

#### 問題: "Rate limiting errors"
```
ThrottlingException: Rate exceeded
```

**解決策**: スクリプトには組み込みのレート制限がありますが、これが発生した場合:
1. デバッグモードを有効にして、どのAPIがスロットリングされているかを確認します
2. スクリプト内の並列ワーカーを減らします
3. 操作間に遅延を追加します
4. アカウントのAWSサービス制限を確認します

#### 問題: "Scripts running slowly"
**症状**: 操作が予想よりもはるかに長くかかる

**解決策**:
1. ネットワーク接続を確認します
2. AWSリージョンが地理的に近いことを確認します
3. デバッグモードを有効にしてボトルネックを特定します
4. バッチサイズを減らすことを検討します

### データ整合性の問題

#### 問題: "Device shadows not updating"
```
❌ Failed to update device shadow
```

**解決策**:
1. IoT Dataエンドポイント設定を確認します
2. デバイス/モノが存在することを確認します
3. シャドウ更新で適切なJSON形式を確保します
4. シャドウ操作のAWS IAM権限を確認します

#### 問題: "Package configuration not working"
```
❌ Failed to update global package configuration
```

**解決策**:
1. IoTPackageConfigRoleが存在し、適切な権限があることを確認します
2. ロールARNが正しくフォーマットされているか確認します
3. リージョンでパッケージ設定が有効になっていることを確認します

## デバッグモードの使用

詳細なトラブルシューティングのために、任意のスクリプトでデバッグモードを有効にします:

```bash
🔧 Enable debug mode (show all commands and outputs)? [y/N]: y
```

デバッグモードは以下を表示します:
- 実行されているすべてのAWS CLIコマンド
- APIリクエストパラメータ
- 完全なAPIレスポンス
- エラーの詳細とスタックトレース

## ログ分析

### 成功した操作
これらの指標を探します:
- ✅ 成功した操作の緑色のチェックマーク
- 完了を示す進行状況カウンター
- "completed successfully"メッセージ

### 警告サイン
これらのパターンに注意してください:
- ⚠️ 黄色の警告（通常は重大ではない）
- "already exists"メッセージ（通常は無害）
- タイムアウト警告

### エラーパターン
一般的なエラー指標:
- ❌ 失敗の赤いXマーク
- "Failed to"メッセージ
- 例外スタックトレース
- HTTPエラーコード（403、404、500）

## 復旧手順

### 部分的なプロビジョニング失敗
プロビジョニングが途中で失敗した場合:

1. **作成されたものを確認します**:
   ```bash
   python scripts/explore_jobs.py
   # Option 1: List all jobs
   ```

2. **必要に応じてクリーンアップします**:
   ```bash
   python scripts/cleanup_script.py
   # Option 1: ALL resources
   ```

3. **プロビジョニングを再試行します**:
   ```bash
   python scripts/provision_script.py
   # Scripts handle existing resources gracefully
   ```

### 失敗したジョブの復旧
実行中にジョブが失敗した場合:

1. **ジョブのステータスを確認します**:
   ```bash
   python scripts/explore_jobs.py
   # Option 2: Explore specific job
   ```

2. **個別の失敗を確認します**:
   ```bash
   python scripts/explore_jobs.py
   # Option 3: Explore job execution
   ```

3. **必要に応じてロールバックします**:
   ```bash
   python scripts/manage_packages.py
   # Select: 10. Revert Device Versions
   # Enter thing type and previous version
   ```

### リソースクリーンアップの問題
クリーンアップが失敗した場合:

1. **選択的クリーンアップを試します**:
   ```bash
   python scripts/cleanup_script.py
   # Option 2: Things only (then try groups)
   ```

2. **AWSコンソールを介した手動クリーンアップ**:
   - AWS IoT Core → Manage → Things
   - AWS IoT Core → Manage → Thing groups
   - AWS IoT Core → Manage → Thing types
   - Amazon S3 → Buckets
   - AWS IAM → Roles

## 環境固有の問題

### macOSの問題
- **SSL警告**: スクリプトはurllib3 SSL警告を自動的に抑制します
- **Pythonバージョン**: Python 3.7+がインストールされていることを確認してください

### Windowsの問題
- **パス区切り文字**: スクリプトはクロスプラットフォームパスを自動的に処理します
- **PowerShell**: 適切な実行ポリシーでコマンドプロンプトまたはPowerShellを使用します

### Linuxの問題
- **権限**: スクリプトに実行権限があることを確認します
- **Pythonパス**: `python`の代わりに`python3`を使用する必要がある場合があります

## AWSサービス制限

### デフォルト制限（リージョンごと）
- **Things**: アカウントあたり500,000
- **Thing Types**: アカウントあたり100
- **Thing Groups**: アカウントあたり500
- **Jobs**: 100の同時ジョブ
- **APIレート制限**: 
  - Thing操作: 100 TPS（スクリプトは80 TPSを使用）
  - 動的グループ: 5 TPS（スクリプトは4 TPSを使用）
  - ジョブ実行: 200 TPS（スクリプトは150 TPSを使用）
  - パッケージ操作: 10 TPS（スクリプトは8 TPSを使用）

### 制限の引き上げをリクエスト
より高い制限が必要な場合:
1. AWSサポートセンターに移動します
2. "Service limit increase"のケースを作成します
3. 必要なAWS IoT Core制限を指定します

## ヘルプを得る

### 詳細ログを有効にする
ほとんどのスクリプトは詳細モードをサポートしています:
```bash
🔧 Enable verbose mode? [y/N]: y
```

### AWSサービスの状態を確認する
- [AWSサービス状態ダッシュボード](https://status.aws.amazon.com/)
- AWS IoT Coreの問題について特定のリージョンを確認します

### コミュニティリソース
- AWS IoT開発者フォーラム
- AWSドキュメント
- GitHub Issues（スクリプト固有の問題）

### プロフェッショナルサポート
- AWSサポート（サポートプランをお持ちの場合）
- AWSプロフェッショナルサービス
- AWSパートナーネットワークコンサルタント

## 予防のヒント

### スクリプトを実行する前に
1. **AWS設定を確認**: `aws sts get-caller-identity`
2. **権限を確認**: まず小さな操作でテストします
3. **リソース制限を確認**: アカウント制限に達しないことを確認します
4. **重要なデータをバックアップ**: 既存のリソースを変更する場合

### 実行中
1. **進行状況を監視**: エラーパターンに注意します
2. **中断しない**: スクリプトを完了させるか、Ctrl+Cを慎重に使用します
3. **AWSコンソールを確認**: リソースが期待どおりに作成されていることを確認します

### 実行後
1. **結果を確認**: 探索スクリプトを使用して結果を確認します
2. **テストリソースをクリーンアップ**: 一時的なリソースにはクリーンアップスクリプトを使用します
3. **コストを監視**: 予期しない料金についてAWS請求を確認します

## 国際化の問題

### 問題: スクリプトが翻訳されたテキストの代わりに生のメッセージキーを表示する
**症状**: スクリプトが実際のメッセージの代わりに`warnings.debug_warning`や`prompts.debug_mode`のようなテキストを表示する

**例**:
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

**根本原因**: この問題は次の場合に発生します:
1. 言語セレクターとディレクトリ構造間の言語コードの不一致
2. `get_message()`関数でのネストされたキー処理の欠如
3. 不正なメッセージファイルの読み込み

**解決策**:

1. **言語コードマッピングを確認**: 言語コードがディレクトリ構造と一致することを確認します:
   ```
   i18n/
   ├── en/     # English
   ├── es/     # Spanish  
   ├── ja/     # Japanese
   ├── ko/     # Korean
   ├── pt/     # Portuguese
   ├── zh/     # Chinese
   ```

2. **get_message()の実装を確認**: スクリプトはドット表記でネストされたキーを処理する必要があります:
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

3. **言語読み込みをテスト**:
   ```bash
   # Test with environment variable
   export AWS_IOT_LANG=en
   python scripts/cleanup_script.py
   
   # Test different languages
   export AWS_IOT_LANG=es  # Spanish
   export AWS_IOT_LANG=ja  # Japanese
   export AWS_IOT_LANG=zh  # Chinese
   ```

4. **メッセージファイルが存在することを確認**:
   ```bash
   # Check if translation files exist
   ls i18n/en/cleanup_script.json
   ls i18n/es/cleanup_script.json
   # etc.
   ```

**予防**: 新しいスクリプトや言語を追加する場合:
- 動作するスクリプトから正しい`get_message()`実装を使用します
- 言語コードがディレクトリ名と正確に一致することを確認します
- デプロイ前に複数の言語でテストします
- `docs/templates/validation_scripts/`の検証スクリプトを使用します

### 問題: 環境変数で言語選択が機能しない
**症状**: `AWS_IOT_LANG`を設定しているにもかかわらず、スクリプトが常に言語選択を求める

**解決策**:
1. **環境変数の形式を確認**:
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

2. **環境変数が設定されていることを確認**:
   ```bash
   echo $AWS_IOT_LANG
   ```

3. **言語選択をテスト**:
   ```bash
   python3 -c "
   import sys, os
   sys.path.append('i18n')
   from language_selector import get_language
   print('Selected language:', get_language())
   "
   ```

### 問題: 新しい言語の翻訳が不足している
**症状**: スクリプトが英語にフォールバックするか、サポートされていない言語のメッセージキーを表示する

**解決策**:
1. **言語ディレクトリを追加**: 新しい言語のディレクトリ構造を作成します
2. **翻訳ファイルをコピー**: 既存の翻訳をテンプレートとして使用します
3. **言語セレクターを更新**: サポートされているリストに新しい言語を追加します
4. **徹底的にテスト**: すべてのスクリプトが新しい言語で動作することを確認します

詳細な手順については、`docs/templates/NEW_LANGUAGE_TEMPLATE.md`を参照してください。

## AWS IoT Jobs APIの制限

### 問題: 完了したジョブのジョブ実行詳細にアクセスできない
**症状**: 完了、失敗、またはキャンセルされたジョブのジョブ実行詳細を探索しようとするとエラーが発生する

**エラー例**:
```
❌ Error in Job Execution Detail upgradeSedanvehicle110_1761321268 on Vehicle-VIN-016: 
Job Execution has reached terminal state. It is neither IN_PROGRESS nor QUEUED
❌ Failed to get job execution details. Check job ID and thing name.
```

**根本原因**: AWSはジョブ実行詳細にアクセスするための2つの異なるAPIを提供しています:

1. **IoT Jobs Data API**（`iot-jobs-data`サービス）:
   - エンドポイント: `describe_job_execution`
   - **制限**: `IN_PROGRESS`または`QUEUED`ステータスのジョブに対してのみ機能します
   - **エラー**: 完了したジョブに対して"Job Execution has reached terminal state"を返します
   - **使用例**: デバイスが現在のジョブ指示を取得するために設計されています

2. **IoT API**（`iot`サービス）:
   - エンドポイント: `describe_job_execution`
   - **機能**: 任意のステータス（COMPLETED、FAILED、CANCELEDなど）のジョブに対して機能します
   - **制限なし**: 履歴ジョブ実行データにアクセスできます
   - **使用例**: すべてのジョブ実行の管理と監視のために設計されています

**解決策**: explore_jobsスクリプトは、IoT Jobs Data APIの代わりにIoT APIを使用するように更新されました。

**コード変更**:
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

**検証**: 修正後、次のジョブ実行詳細を探索できるようになりました:
- ✅ COMPLETEDジョブ
- ✅ FAILEDジョブ  
- ✅ CANCELEDジョブ
- ✅ IN_PROGRESSジョブ
- ✅ QUEUEDジョブ
- ✅ その他のジョブステータス

**追加の利点**:
- 履歴ジョブ実行データへのアクセス
- 失敗したデプロイメントのより良いトラブルシューティング機能
- デバイス更新試行の完全な監査証跡

### 問題: 実行詳細でジョブドキュメントが利用できない
**症状**: ジョブ実行詳細は表示されるが、ジョブドキュメントが欠落している

**解決策**: スクリプトにはフォールバックメカニズムが含まれるようになりました:
1. まず実行詳細からジョブドキュメントを取得しようとします
2. 利用できない場合は、メインジョブ詳細から取得します
3. ジョブドキュメントが利用できない場合は適切なメッセージを表示します

これにより、ジョブのステータスやAPIの制限に関係なく、デバイスに送信されたジョブ指示を常に確認できます。
