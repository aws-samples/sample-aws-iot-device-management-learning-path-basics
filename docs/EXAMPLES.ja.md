# 使用例

このドキュメントは、AWS IoT Device Managementの一般的なシナリオの実用的な例を提供します。

## クイックスタート例

### 基本的なフリート設定
```bash
# 1. インフラストラクチャの作成
python scripts/provision_script.py
# 選択: SedanVehicle,SUVVehicle
# バージョン: 1.0.0,1.1.0
# 地域: North America
# 国: US,CA
# デバイス: 100

# 2. 動的グループの作成
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# 国: US
# モノタイプ: SedanVehicle
# バッテリーレベル: <30

# 3. ファームウェア更新ジョブの作成
python scripts/create_job.py
# 選択: USFleetグループ
# パッケージ: SedanVehicle v1.1.0

# 4. デバイス更新のシミュレート
python scripts/simulate_job_execution.py
# 成功率: 85%
# 処理: すべての実行
```

### バージョンロールバックシナリオ
```bash
# すべてのSedanVehicleデバイスをバージョン1.0.0にロールバック
python scripts/manage_packages.py
# 選択: 10. デバイスバージョンの復元
# モノタイプ: SedanVehicle
# ターゲットバージョン: 1.0.0
# 確認: REVERT
```

### ジョブ監視
```bash
# ジョブの進行状況を監視
python scripts/explore_jobs.py
# オプション1: すべてのジョブをリスト
# オプション4: 特定のジョブのジョブ実行をリスト
```

## 高度なシナリオ

### マルチリージョンデプロイメント
```bash
# 複数のリージョンでプロビジョニング
export AWS_DEFAULT_REGION=us-east-1
python scripts/provision_script.py
# 北米に500デバイスを作成

export AWS_DEFAULT_REGION=eu-west-1  
python scripts/provision_script.py
# ヨーロッパに300デバイスを作成
```

### 段階的ロールアウト
```bash
# 1. テストグループの作成
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# 国: US
# モノタイプ: SedanVehicle
# バージョン: 1.0.0
# カスタム名: TestFleet_SedanVehicle_US

# 2. まずテストグループにデプロイ
python scripts/create_job.py
# 選択: TestFleet_SedanVehicle_US
# パッケージ: SedanVehicle v1.1.0

# 3. テストデプロイメントの監視
python scripts/simulate_job_execution.py
# 成功率: 95%

# 4. 検証後に本番環境にデプロイ
python scripts/create_job.py
# 選択: USFleet
# パッケージ: SedanVehicle v1.1.0
```

### バッテリーベースのメンテナンス
```bash
# 低バッテリーグループの作成
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# 方法: 1 (ガイド付きウィザード)
# 国: (すべての場合は空白)
# モノタイプ: (すべての場合は空白)
# バッテリーレベル: <20
# カスタム名: LowBatteryDevices

# メンテナンスジョブの作成
python scripts/create_job.py
# 選択: LowBatteryDevices
# パッケージ: MaintenanceFirmware v2.0.0
```

### 高度なカスタムクエリ
```bash
# カスタムクエリで複雑なグループを作成
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# 方法: 2 (カスタムクエリ)
# クエリ: (thingTypeName:SedanVehicle OR thingTypeName:SUVVehicle) AND attributes.country:US AND shadow.reported.batteryStatus:[30 TO 80]
# グループ名: USVehicles_MidBattery
```

### パッケージ管理
```bash
# 新しいパッケージとバージョンの作成
python scripts/manage_packages.py
# 操作: 1 (パッケージの作成)
# パッケージ名: TestVehicle

# S3アップロードでバージョンを追加
# 操作: 2 (バージョンの作成)
# パッケージ名: TestVehicle
# バージョン: 2.0.0

# パッケージの詳細を確認
# 操作: 4 (パッケージの説明)
# パッケージ名: TestVehicle
```

## 開発ワークフロー

### 新しいファームウェアのテスト
```bash
# 1. テスト環境のプロビジョニング
python scripts/provision_script.py
# モノタイプ: TestSensor
# バージョン: 1.0.0,2.0.0-beta
# 国: US
# デバイス: 10

# 2. ベータテストグループの作成
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# モノタイプ: TestSensor
# バージョン: 1.0.0
# カスタム名: BetaTestGroup

# 3. ベータファームウェアのデプロイ
python scripts/create_job.py
# 選択: BetaTestGroup
# パッケージ: TestSensor v2.0.0-beta

# 4. テスト用に高い失敗率でシミュレート
python scripts/simulate_job_execution.py
# 成功率: 60%

# 5. 結果の分析
python scripts/explore_jobs.py
# オプション4: ジョブ実行をリスト
```

### テスト後のクリーンアップ
```bash
# テストリソースのクリーンアップ
python scripts/cleanup_script.py
# オプション1: すべてのリソース
# 確認: DELETE
```

## フリート管理パターン

### 地理的デプロイメント
```bash
# 大陸別にプロビジョニング
python scripts/provision_script.py
# 大陸: 1 (北米)
# 国: 3 (最初の3か国)
# デバイス: 1000

# 国別グループの作成（USFleet、CAFleet、MXFleetとして自動作成）
# 地域固有のファームウェアをデプロイ
python scripts/create_job.py
# 選択: USFleet,CAFleet
# パッケージ: RegionalFirmware v1.2.0
```

### デバイスタイプ管理
```bash
# 複数の車両タイプをプロビジョニング
python scripts/provision_script.py
# モノタイプ: SedanVehicle,SUVVehicle,TruckVehicle
# バージョン: 1.0.0,1.1.0,2.0.0
# デバイス: 500

# タイプ固有の動的グループを作成
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# モノタイプ: TruckVehicle
# 国: US,CA
# カスタム名: NorthAmericaTrucks

# トラック固有のファームウェアをデプロイ
python scripts/create_job.py
# 選択: NorthAmericaTrucks
# パッケージ: TruckVehicle v2.0.0
```

### メンテナンススケジューリング
```bash
# 更新が必要なデバイスを検索
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# モノタイプ: SedanVehicle
# バージョン: 1.0.0  # 古いバージョン
# カスタム名: SedanVehicle_NeedsUpdate

# メンテナンスウィンドウでのデプロイをスケジュール
python scripts/create_job.py
# 選択: SedanVehicle_NeedsUpdate
# パッケージ: SedanVehicle v1.1.0

# デプロイの進行状況を監視
python scripts/explore_jobs.py
# オプション1: すべてのジョブをリスト（ステータスを確認）
```

## トラブルシューティング例

### 失敗したジョブの回復
```bash
# 1. ジョブステータスの確認
python scripts/explore_jobs.py
# オプション2: 特定のジョブを探索
# 失敗があるジョブIDを入力

# 2. 個別デバイスの失敗を確認
python scripts/explore_jobs.py
# オプション3: ジョブ実行を探索
# ジョブIDと失敗したデバイス名を入力

# 3. 失敗したデバイスをロールバック
python scripts/manage_packages.py
# 選択: 10. デバイスバージョンの復元
# モノタイプ: SedanVehicle
# ターゲットバージョン: 1.0.0  # 以前の動作バージョン
```

### デバイス状態の検証
```bash
# 現在のファームウェアバージョンを確認
python scripts/manage_dynamic_groups.py
# 操作: 1 (作成)
# モノタイプ: SedanVehicle
# バージョン: 1.1.0
# カスタム名: SedanVehicle_v1_1_0_Check

# グループメンバーシップを検証（期待されるカウントと一致する必要があります）
python scripts/explore_jobs.py
# デバイスの状態を検証するために使用
```

### パフォーマンステスト
```bash
# 大量のデバイスでテスト
python scripts/provision_script.py
# デバイス: 5000

# ジョブ実行パフォーマンスをテスト
python scripts/simulate_job_execution.py
# 処理: すべて
# 成功率: 90%
# 実行時間とTPSを監視
```

## 環境固有の例

### 開発環境
```bash
# 開発用の小規模
python scripts/provision_script.py
# モノタイプ: DevSensor
# バージョン: 1.0.0-dev
# 国: US
# デバイス: 5
```

### ステージング環境
```bash
# ステージング用の中規模
python scripts/provision_script.py
# モノタイプ: SedanVehicle,SUVVehicle
# バージョン: 1.0.0,1.1.0-rc
# 国: US,CA
# デバイス: 100
```

### 本番環境
```bash
# 本番用の大規模
python scripts/provision_script.py
# モノタイプ: SedanVehicle,SUVVehicle,TruckVehicle
# バージョン: 1.0.0,1.1.0,1.2.0
# 大陸: 1 (北米)
# 国: すべて
# デバイス: 10000
```

## 統合例

### CI/CDパイプライン統合
```bash
# 構文チェック（自動化）
python scripts/check_syntax.py

# 自動テスト
python scripts/provision_script.py --automated
python scripts/create_job.py --test-mode
python scripts/simulate_job_execution.py --success-rate 95
python scripts/cleanup_script.py --force
```

### 監視統合
```bash
# ジョブメトリクスのエクスポート
python scripts/explore_jobs.py --export-json > job_status.json

# デプロイメントの健全性を確認
python scripts/explore_jobs.py --health-check
```

## ベストプラクティス例

### 段階的ロールアウト
1. フリートの5%から開始（テストグループ）
2. 24時間監視
3. 成功した場合は25%に拡大
4. 検証後に完全デプロイメント

### ロールバック戦略
1. 常にロールバック手順をテスト
2. 以前のファームウェアバージョンを利用可能に保つ
3. デプロイ後のデバイスの健全性を監視
4. 自動ロールバックトリガーを用意

### リソース管理
1. テスト後にクリーンアップスクリプトを使用
2. AWSコストを監視
3. 古いファームウェアバージョンをクリーンアップ
4. 未使用のモノグループを削除
