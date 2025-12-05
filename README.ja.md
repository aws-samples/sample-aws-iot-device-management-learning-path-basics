# AWS IoT Device Management - Learning Path - Basics

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

デバイスプロビジョニング、Over-the-Air（OTA）アップデート、ジョブ管理、フリート運用を含むAWS IoT Device Managementの包括的なデモンストレーション。ネイティブAWS SDK（boto3）統合を使用したモダンなPythonスクリプトを活用しています。

## 👥 対象読者

**主要対象者：** IoT開発者、ソリューションアーキテクト、AWS IoTデバイスフリートを扱うDevOpsエンジニア

**前提条件：** 中級レベルのAWS知識、AWS IoT Coreの基礎、Pythonの基礎、コマンドライン使用経験

**学習レベル：** 大規模デバイス管理への実践的アプローチを含むアソシエイトレベル

## 🎯 学習目標

- **デバイスライフサイクル管理**: 適切なthingタイプと属性を使用したIoTデバイスのプロビジョニング
- **フリート組織**: デバイス管理のための静的および動的thingグループの作成
- **OTAアップデート**: Amazon S3統合を使用したAWS IoT Jobsによるファームウェアアップデートの実装
- **パッケージ管理**: 自動化されたシャドウアップデートによる複数のファームウェアバージョンの処理
- **ジョブ実行**: ファームウェアアップデート中のリアルなデバイス動作のシミュレーション
- **バージョン管理**: デバイスを以前のファームウェアバージョンにロールバック
- **リモートコマンド**: AWS IoT Commandsを使用したデバイスへのリアルタイムコマンド送信
- **リソースクリーンアップ**: 不要なコストを避けるためのAWSリソースの適切な管理

## 📋 前提条件

- **AWSアカウント** - AWS IoT、Amazon S3、AWS Identity and Access Management（AWS Identity and Access Management (IAM)）の権限を持つもの
- **AWS認証情報** - 設定済み（`aws configure`、環境変数、またはAWS Identity and Access Management (IAM)ロール経由）
- **Python 3.10+** - pip、boto3、colorama、requestsライブラリ（requirements.txtファイルを確認）
- **Git** - リポジトリのクローン用

## 💰 コスト分析

**このプロジェクトは実際のAWSリソースを作成し、料金が発生します。**

| サービス | 使用量 | 推定コスト（USD） |
|---------|-------|---------------------|
| **AWS IoT Core** | 約1,000メッセージ、100-10,000デバイス | $0.08 - $0.80 |
| **AWS IoT Device Shadow** | 約200-2,000シャドウ操作 | $0.10 - $1.00 |
| **AWS IoT Jobs** | 約10-100ジョブ実行 | $0.01 - $0.10 |
| **AWS IoT Commands** | 約10-50コマンド実行 | $0.01 - $0.05 |
| **Amazon S3** | ファームウェアのストレージ + リクエスト | $0.05 - $0.25 |
| **AWS IoT Fleet Indexing** | デバイスクエリとインデックス作成 | $0.02 - $0.20 |
| **AWS IoT Device Management Software Package Catalog** | パッケージ操作 | $0.01 - $0.05 |
| **AWS Identity and Access Management（AWS Identity and Access Management (IAM)）** | ロール/ポリシー管理 | $0.00 |
| **合計推定** | **完全なデモセッション** | **$0.28 - $2.45** |

**コスト要因：**
- デバイス数（100-10,000設定可能）
- ジョブ実行頻度
- シャドウアップデート操作
- Amazon S3ストレージ期間

**コスト管理：**
- ✅ クリーンアップスクリプトがすべてのリソースを削除
- ✅ 短期間のデモリソース
- ✅ 設定可能なスケール（小さく開始）
- ⚠️ **完了時にクリーンアップスクリプトを実行**

**📊 コスト監視：** [AWS請求ダッシュボード](https://console.aws.amazon.com/billing/)

## 🚀 クイックスタート

```bash
# 1. クローンとセットアップ
git clone https://github.com/aws-samples/sample-aws-iot-device-management-learning-path-basics.git
cd sample-aws-iot-device-management-learning-path-basics
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. AWS設定
aws configure

# 3. 完全なワークフロー（推奨順序）
python scripts/provision_script.py        # タグ付きインフラストラクチャの作成
python scripts/manage_dynamic_groups.py   # デバイスグループの作成
python scripts/manage_packages.py         # ファームウェアパッケージの管理
python scripts/create_job.py              # ファームウェアアップデートのデプロイ
python scripts/simulate_job_execution.py  # デバイスアップデートのシミュレーション
python scripts/explore_jobs.py            # ジョブ進捗の監視
python scripts/manage_commands.py         # デバイスへのリアルタイムコマンド送信
python scripts/cleanup_script.py          # リソース識別による安全なクリーンアップ
```

## 📚 利用可能なスクリプト

| スクリプト | 目的 | 主要機能 | ドキュメント |
|--------|---------|-------------|---------------|
| **provision_script.py** | 完全なインフラストラクチャセットアップ | デバイス、グループ、パッケージ、Amazon S3ストレージの作成 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptsprovision_scriptpy) |
| **manage_dynamic_groups.py** | 動的デバイスグループの管理 | Fleet Indexing検証による作成、一覧表示、削除 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptsmanage_dynamic_groupspy) |
| **manage_packages.py** | 包括的なパッケージ管理 | パッケージ/バージョンの作成、Amazon S3統合、個別復元ステータス付きデバイス追跡 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptsmanage_packagespy) |
| **create_job.py** | OTAアップデートジョブの作成 | マルチグループターゲティング、事前署名URL | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptscreate_jobpy) |
| **simulate_job_execution.py** | デバイスアップデートのシミュレーション | 実際のAmazon S3ダウンロード、可視化されたプラン準備、デバイス別進捗追跡 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptssimulate_job_executionpy) |
| **explore_jobs.py** | ジョブの監視と管理 | インタラクティブなジョブ探索、キャンセル、削除、分析 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptsexplore_jobspy) |
| **manage_commands.py** | デバイスへのリアルタイムコマンド送信 | テンプレート管理、コマンド実行、ステータス監視、履歴追跡 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptsmanage_commandspy) |
| **cleanup_script.py** | AWSリソースの削除 | 選択的クリーンアップ、コスト管理 | [📖 詳細](docs/DETAILED_SCRIPTS.md#scriptscleanup_scriptpy) |

> 📖 **詳細ドキュメント**: 包括的なスクリプト情報については[docs/DETAILED_SCRIPTS.md](docs/DETAILED_SCRIPTS.md)を参照してください。

## ⚙️ 設定

**環境変数**（オプション）：
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_IOT_LANG=ja                    # デフォルト言語の設定（en、es、ja等）
```

**スクリプト機能**：
- **ネイティブAWS SDK**: より良いパフォーマンスと信頼性のためにboto3を使用
- **多言語サポート**: 英語へのフォールバック付きインタラクティブ言語選択
- **デバッグモード**: すべてのAWS API呼び出しとレスポンスを表示
- **並列処理**: デバッグモード以外での同時実行操作
- **レート制限**: 自動AWS APIスロットリング準拠
- **進捗追跡**: リアルタイム操作ステータス
- **リソースタグ付け**: 安全なクリーンアップのための自動ワークショップタグ
- **設定可能な命名**: カスタマイズ可能なデバイス命名パターン

### リソースタグ付け

すべてのワークショップスクリプトは、クリーンアップ時の安全な識別のために、作成されたリソースに自動的に`workshop=learning-aws-iot-dm-basics`タグを付けます。これにより、ワークショップで作成されたリソースのみが削除されることが保証されます。

**タグ付きリソース**：
- IoT Thingタイプ
- IoT Thingグループ（静的および動的）
- IoTソフトウェアパッケージ
- IoTジョブ
- Amazon S3バケット
- AWS Identity and Access Management (IAM)ロール

**タグなしリソース**（命名パターンで識別）：
- IoT Thing（命名規則を使用）
- 証明書（関連付けで識別）
- Thingシャドウ（関連付けで識別）

### デバイス命名設定

`--things-prefix`パラメータでデバイス命名パターンをカスタマイズ：

```bash
# デフォルト命名：Vehicle-VIN-001、Vehicle-VIN-002など
python scripts/provision_script.py

# カスタムプレフィックス：Fleet-Device-001、Fleet-Device-002など
python scripts/provision_script.py --things-prefix "Fleet-Device-"

# クリーンアップ用カスタムプレフィックス（プロビジョニングプレフィックスと一致する必要があります）
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"
```

**プレフィックス要件**：
- 英数字、ハイフン、アンダースコア、コロンのみ
- 最大20文字
- 連番は自動的にゼロパディング（001-999）

## 🌍 国際化サポート

すべてのスクリプトは自動言語検出とインタラクティブ選択による多言語サポートを提供します。

**言語選択**：
- **インタラクティブ**: スクリプトが初回実行時に言語選択を促す
- **環境変数**: `AWS_IOT_LANG=ja`を設定して言語選択をスキップ
- **フォールバック**: 翻訳が不足している場合は自動的に英語にフォールバック

**サポート言語**：
- **English（en）**: 完全な翻訳 ✅
- **Spanish（es）**: 翻訳準備完了
- **Japanese（ja）**: 翻訳準備完了
- **Chinese（zh-CN）**: 翻訳準備完了
- **Portuguese（pt-BR）**: 翻訳準備完了
- **Korean（ko）**: 翻訳準備完了

**使用例**：
```bash
# 環境変数による言語設定（自動化に推奨）
export AWS_IOT_LANG=ja
python scripts/provision_script.py

# サポートされる代替言語コード
export AWS_IOT_LANG=japanese   # または "ja"、"日本語"、"jp"
export AWS_IOT_LANG=spanish    # または "es"、"español"
export AWS_IOT_LANG=chinese    # または "zh-cn"、"中文"、"zh"
export AWS_IOT_LANG=portuguese # または "pt"、"pt-br"、"português"
export AWS_IOT_LANG=korean     # または "ko"、"한국어"、"kr"

# インタラクティブ言語選択（デフォルト動作）
python scripts/manage_packages.py
# 出力: 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
#         1. English
#         2. Español (Spanish)
#         3. 日本語 (Japanese)
#         4. 中文 (Chinese)
#         5. Português (Portuguese)
#         6. 한국어 (Korean)
#         Select language (1-6): 

# すべてのユーザー向けテキストが選択した言語で表示されます
```

**メッセージカテゴリ**：
- **UI要素**: タイトル、ヘッダー、区切り線
- **ユーザープロンプト**: 入力要求、確認
- **ステータスメッセージ**: 進捗更新、成功/失敗通知
- **エラーメッセージ**: 詳細なエラー説明とトラブルシューティング
- **デバッグ出力**: API呼び出し情報とレスポンス
- **学習コンテンツ**: 教育的な瞬間と説明

## 📖 使用例

**完全なワークフロー**（推奨順序）：
```bash
python scripts/provision_script.py        # 1. インフラストラクチャの作成
python scripts/manage_dynamic_groups.py   # 2. デバイスグループの作成
python scripts/manage_packages.py         # 3. ファームウェアパッケージの管理
python scripts/create_job.py              # 4. ファームウェアアップデートのデプロイ
python scripts/simulate_job_execution.py  # 5. デバイスアップデートのシミュレーション
python scripts/explore_jobs.py            # 6. ジョブ進捗の監視
python scripts/manage_commands.py         # 7. デバイスへのリアルタイムコマンド送信
python scripts/cleanup_script.py          # 8. リソースのクリーンアップ
```

**個別操作**：
```bash
python scripts/manage_packages.py         # パッケージとバージョン管理
python scripts/manage_dynamic_groups.py   # 動的グループ操作
```

> 📖 **その他の例**: 詳細な使用シナリオについては[docs/EXAMPLES.md](docs/EXAMPLES.md)を参照してください。

## 🛠️ トラブルシューティング

**よくある問題**：
- **認証情報**: `aws configure`、環境変数、またはAWS Identity and Access Management (IAM)ロール経由でAWS認証情報を設定
- **権限**: AWS Identity and Access Management (IAM)ユーザーがAWS IoT、Amazon S3、AWS Identity and Access Management (IAM)権限を持っていることを確認
- **レート制限**: スクリプトがインテリジェントスロットリングで自動処理
- **ネットワーク**: AWS APIへの接続を確認

**デバッグモード**: 詳細なトラブルシューティングのため任意のスクリプトで有効化
```bash
🔧 Enable debug mode (show all API calls and responses)? [y/N]: y
```

> 📖 **詳細なトラブルシューティング**: 包括的な解決策については[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)を参照してください。

## 🧹 重要：リソースクリーンアップ

**継続的な料金を避けるため、完了時には必ずクリーンアップを実行してください：**
```bash
python scripts/cleanup_script.py
# オプション1を選択：すべてのリソース
# 入力：DELETE
```

### 安全なクリーンアップ機能

クリーンアップスクリプトは、ワークショップリソースのみが削除されることを保証するために複数の識別方法を使用します：

1. **タグベース識別**（プライマリ）：`workshop=learning-aws-iot-dm-basics`タグを確認
2. **命名パターンマッチング**（セカンダリ）：既知のワークショップ命名規則と一致
3. **関連付けベース**（ターシャリ）：ワークショップリソースに添付されたリソースを識別

**クリーンアップオプション**：
```bash
# 標準クリーンアップ（インタラクティブ）
python scripts/cleanup_script.py

# ドライランモード（削除せずにプレビュー）
python scripts/cleanup_script.py --dry-run

# カスタムデバイスプレフィックス（プロビジョニングプレフィックスと一致する必要があります）
python scripts/cleanup_script.py --things-prefix "Fleet-Device-"

# カスタムプレフィックス付きドライラン
python scripts/cleanup_script.py --dry-run --things-prefix "Fleet-Device-"
```

**クリーンアップで削除されるもの**：
- すべてのAWS IoTデバイスとグループ（ワークショップタグまたは一致する命名パターン付き）
- Amazon S3バケットとファームウェアファイル（タグ付き）
- AWS IoTソフトウェアパッケージ（タグ付き）
- AWS IoTコマンドテンプレート（タグ付き）
- AWS Identity and Access Management (IAM)ロールとポリシー（タグ付き）
- Fleet Indexing設定
- 関連する証明書とシャドウ

**安全機能**：
- ワークショップ以外のリソースは自動的にスキップ
- 詳細なサマリーで削除およびスキップされたリソースを表示
- デバッグモードで各リソースの識別方法を表示
- ドライランモードで実際の削除前にプレビュー可能

## 🔧 開発者ガイド：新しい言語の追加

**メッセージファイル構造**：
```
i18n/
├── common.json                    # すべてのスクリプト間で共有されるメッセージ
├── loader.py                      # メッセージ読み込みユーティリティ
├── language_selector.py           # 言語選択インターフェース
└── {language_code}/               # 言語固有のディレクトリ
    ├── provision_script.json     # スクリプト固有のメッセージ
    ├── manage_dynamic_groups.json
    ├── manage_packages.json
    ├── create_job.json
    ├── simulate_job_execution.json
    ├── explore_jobs.json
    └── cleanup_script.json
```

**新しい言語の追加**：

1. **言語ディレクトリの作成**：
   ```bash
   mkdir i18n/{language_code}  # 例：スペイン語の場合はi18n/es
   ```

2. **英語テンプレートのコピー**：
   ```bash
   cp i18n/en/*.json i18n/{language_code}/
   ```

3. **メッセージファイルの翻訳**：
   各JSONファイルには分類されたメッセージが含まれています：
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

4. **言語セレクターの更新**（新しい言語を追加する場合）：
   `i18n/language_selector.py`に言語を追加：
   ```python
   LANGUAGE_SELECTION = {
       "options": [
           "1. English",
           "2. Español (Spanish)",
           "3. Your Language Name",  # 新しいオプションを追加
           # ... 既存の言語
       ],
   }
   
   LANGUAGE_CODES = {
       "1": "en", 
       "2": "es", 
       "3": "your_code",  # 新しい言語コードを追加
       # ... 既存のマッピング
   }
   ```

5. **翻訳のテスト**：
   ```bash
   export AWS_IOT_LANG={language_code}
   python scripts/provision_script.py
   ```

**翻訳ガイドライン**：
- **フォーマットの保持**: 絵文字、色、特殊文字を保持
- **プレースホルダーの維持**: 動的コンテンツ用の`{}`プレースホルダーを保持
- **技術用語**: AWSサービス名は英語のまま
- **文化的適応**: 例と参照を適切に適応
- **一貫性**: すべてのファイル間で一貫した用語を使用

**メッセージキーパターン**：
- `title`: スクリプトのメインタイトル
- `separator`: 視覚的な区切り線と仕切り
- `prompts.*`: ユーザー入力要求と確認
- `status.*`: 進捗更新と操作結果
- `errors.*`: エラーメッセージと警告
- `debug.*`: デバッグ出力とAPI情報
- `ui.*`: ユーザーインターフェース要素（メニュー、ラベル、ボタン）
- `results.*`: 操作結果とデータ表示
- `learning.*`: 教育コンテンツと説明
- `warnings.*`: 警告メッセージと重要な通知
- `explanations.*`: 追加のコンテキストとヘルプテキスト

**翻訳のテスト**：
```bash
# 特定のスクリプトを言語でテスト
export AWS_IOT_LANG=your_language_code
python scripts/manage_packages.py

# フォールバック動作のテスト（存在しない言語を使用）
export AWS_IOT_LANG=xx
python scripts/provision_script.py  # 英語にフォールバックするはず
```

## 📚 ドキュメント

- **[詳細スクリプト](docs/DETAILED_SCRIPTS.md)** - 包括的なスクリプトドキュメント
- **[使用例](docs/EXAMPLES.md)** - 実用的なシナリオとワークフロー
- **[トラブルシューティング](docs/TROUBLESHOOTING.md)** - よくある問題と解決策

## 📄 ライセンス

MIT No Attribution License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🏷️ タグ

`aws` `aws-iot` `device-management` `ota-updates` `fleet-management` `python` `demo` `iot`